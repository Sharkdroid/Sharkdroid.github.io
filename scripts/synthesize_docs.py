#!/usr/bin/env python3
"""
Synthesize AI-generated narrative documentation.

For each template skeleton in wiki-templates/, builds grounding for the
model, calls Gemini Flash-Lite to fill [PLACEHOLDER: ...] blocks, validates
the output, appends a version footer, and writes filled files to a staging
directory for PR creation.

Grounding (DOCS_GROUNDING_MODE):
  facts (default)  A compact digest of source-code facts extracted from the
                   installed library (see code_facts.py): import paths,
                   aliases, signatures, overloads, pydantic fields + aliases,
                   constants, call graph, raises, and the library's own
                   current usage examples — prioritised by what the template
                   mentions and trimmed to DOCS_FACTS_TOKEN_BUDGET.
  html             The previous behaviour: text of the Phase 1 built
                   mkdocstrings HTML pages (properdocs build output).
  both             Facts digest followed by the HTML text.
If facts extraction fails for any reason, the run falls back to html.

Validation checks:
  1. No unfilled placeholders remain
  2. Markdown structure (headings) preserved
  3. No invented field names in code blocks
  4. (facts mode) Code blocks only import names from modules that export
     them, only call real `operations.<op>()` methods, and only pass keyword
     arguments the target callable accepts

A page that fails validation gets DOCS_SYNTHESIS_REPAIR_ATTEMPTS (default 1)
follow-up call(s) quoting the validation errors before it is marked failed.
"""

import os
import re
import sys
import json
import time
import litellm
from bs4 import BeautifulSoup

# Newer Gemini models reject some OpenAI-style params (gemini-3.5-flash-lite
# raises UnsupportedParamsError on `temperature`). Drop whatever the target
# model doesn't support instead of failing every call — the SDK equivalent
# of the proxy's `litellm_settings: drop_params: true`.
litellm.drop_params = True

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import code_facts
except Exception as e:  # griffe missing/broken → html grounding only
    code_facts = None
    _CODE_FACTS_IMPORT_ERROR = e

# ============================================================================
# Configuration
# ============================================================================

TEMPLATES_DIR = "wiki-templates"
REF_DOCS_DIR  = "wiki/cascade-cms-wiki/site/operations"  # built HTML, not the docs/operations stubs
REF_STUBS_DIR = "wiki/cascade-cms-wiki/docs/operations"  # `::: module` stubs → which modules to digest
STAGING_DIR   = "/tmp/filled-docs"

GROUNDING_MODES = ("facts", "html", "both")
DEFAULT_MAX_TOKENS = 6000  # templates are mostly placeholders now, so pages are fully generated

# Template metadata comments (stripped before the template reaches the model
# or the validator, so they never land in the published page):
#   <!-- purpose: what the page is for, who reads it -->  → sent as PAGE PURPOSE
#   <!-- focus: Name, Name, ... -->                         → code-facts relevance hints
_META_RE = re.compile(r"^<!--\s*(purpose|focus)\s*:\s*(.*?)\s*-->\s*\n?", re.S | re.M)


def parse_template(raw: str) -> tuple[str, str, set[str]]:
    """Split a template into (body, purpose, focus names)."""
    purpose, focus = "", set()
    for kind, value in _META_RE.findall(raw):
        if kind == "purpose":
            purpose = " ".join(value.split())
        else:
            focus |= {n.strip() for n in value.split(",") if n.strip()}
    return _META_RE.sub("", raw).lstrip("\n"), purpose, focus

# Maps template filename → which built reference pages to use as grounding.
# Kept here in the wiki repo — not in the library.
TEMPLATE_TO_REF_DOCS = {
    "core-concepts-index.md":    ["operations.md", "cmstypes.md", "wrapper.md"],
    "advanced-index.md":         [],    # pure TOC — no grounding needed
    "advanced-logging.md":       ["operation_logger.md", "wrapper.md"],
    "advanced-cpu-intensive.md": ["wrapper.md", "operations.md"],
    "examples-main-patterns.md": ["operations.md", "cmstypes.md"],
    "examples-administrative.md":["operations.md", "cmstypes.md"],
}

# Maps template filename → target wiki path
TEMPLATE_TO_WIKI_PATH = {
    "core-concepts-index.md":    "wiki/cascade-cms-wiki/docs/core-concepts/index.md",
    "advanced-index.md":         "wiki/cascade-cms-wiki/docs/advanced/index.md",
    "advanced-logging.md":       "wiki/cascade-cms-wiki/docs/advanced/logging.md",
    "advanced-cpu-intensive.md": "wiki/cascade-cms-wiki/docs/advanced/cpu-intensive.md",
    "examples-main-patterns.md": "wiki/cascade-cms-wiki/docs/examples/main-patterns.md",
    "examples-administrative.md":"wiki/cascade-cms-wiki/docs/examples/administrative-ops.md",
}

# Maps a "docs/operations/*.md" name to the built HTML page(s) that render it.
# mkdocs' default use_directory_urls emits "<page>/index.html"; fall back to a
# flat "<page>.html" in case that setting or theme convention changes.
REF_DOC_HTML_CANDIDATES = {
    "operations.md":       ["operations/index.html", "operations.html"],
    "cmstypes.md":          ["cmstypes/index.html", "cmstypes.html"],
    "wrapper.md":           ["wrapper/index.html", "wrapper.html"],
    "driver.md":            ["driver/index.html", "driver.html"],
    "operation_logger.md":  ["operation_logger/index.html", "operation_logger.html"],
}

# Known-safe field and method names — extend when new payload models are added.
KNOWN_FIELDS = {
    "displayName", "metadata", "id", "path", "siteName", "asset_type",
    "searchTerms", "searchFields", "searchTypes", "doWorkflow",
    "destinations", "unpublish", "name", "value", "flat", "children",
    "type", "read", "delete", "create", "edit", "search",
    "operations", "submit_requests", "message", "elements", "marked",
}

SYSTEM_PROMPT = """\
You are a technical documentation writer filling placeholder sections in a \
pre-structured markdown template for a Python library wiki.

Rules — follow all of them exactly:
1. Fill every [PLACEHOLDER: ...] block with accurate, concise prose or code.
2. Do NOT modify any text outside a [PLACEHOLDER: ...] block — copy all \
   headings, admonition blocks (!!!), tables, cross-page links, and fixed \
   code blocks character-for-character, including exact heading wording.
3. Source ALL code examples, imports and field names ONLY from the reference \
   material provided below. Do NOT invent field names, method signatures, or \
   parameters that do not appear in it.
4. Code examples must use the actual signatures and field names from the \
   reference material. Do not paraphrase or rename them.
5. Do NOT leave any [PLACEHOLDER: ...] markers in the output.
6. Return ONLY the completed markdown — no preamble, no commentary, no \
   markdown fences wrapping the output.
7. Placeholders describe WHAT to cover, not which API to use: take every \
   class, function, parameter, field and import path from the reference \
   material. A PAGE PURPOSE line, when given, sets the page's audience and \
   goal — keep every section consistent with it.
8. When CODE FACTS are provided they describe the exact library version \
   being documented and override anything you remember about older \
   versions. Import every name from a module the facts list for it, prefer \
   canonical names over aliases, and model examples on the facts' usage \
   examples. If a placeholder's instructions assume an API the facts \
   contradict (a renamed class, a moved module, a changed return type), \
   write what the facts say.
"""

# ============================================================================
# Utility Functions
# ============================================================================


def _resolve_html_path(doc: str) -> str:
    """Find the built HTML file for a docs/operations/*.md reference name."""
    for candidate in REF_DOC_HTML_CANDIDATES[doc]:
        path = os.path.join(REF_DOCS_DIR, candidate)
        if os.path.exists(path):
            return path
    raise FileNotFoundError(
        f"No built HTML found for {doc} under {REF_DOCS_DIR}. "
        f"Checked: {REF_DOC_HTML_CANDIDATES[doc]}. "
        f"Did 'properdocs build' run before this script?"
    )


def extract_reference_text(html_path: str) -> str:
    """Strip mkdocs-material theme chrome, keep the rendered mkdocstrings
    API content (headings, docstrings, signatures, param tables) as text."""
    with open(html_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # Page body content lives inside <article class="md-content__inner ...">
    # — this excludes header, nav sidebar, TOC sidebar, search dialog, footer.
    article = soup.select_one("article.md-content__inner") or soup.select_one("article")
    if article is None:
        raise ValueError(f"Could not locate main content <article> in {html_path}")

    # Remove chrome nested *inside* the article: '¶' permalink icons on every
    # heading, page-feedback/edit buttons, and any inline script/style tags.
    for junk in article.select(".headerlink, .md-content__button, script, style"):
        junk.decompose()

    text = article.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    if len(text) < 40:
        print(
            f"  ! WARNING: extracted grounding text from {html_path} is "
            f"suspiciously short ({len(text)} chars) — theme markup may have "
            f"changed; check REF_DOC_HTML_CANDIDATES / selectors above.",
            file=sys.stderr,
        )

    return text


def load_html_grounding(template_name: str) -> str:
    """Load grounding text for a template from the built reference HTML."""
    docs = TEMPLATE_TO_REF_DOCS.get(template_name, [])
    if not docs:
        return ""
    sections = []
    for doc in docs:
        html_path = _resolve_html_path(doc)
        sections.append(f"--- {doc} ---\n{extract_reference_text(html_path)}")
    return "\n\n".join(sections)


def load_facts_grounding(template_name: str, template_text: str, facts, budget: int,
                         focus: set[str] | None = None) -> str:
    """Token-budgeted code-facts digest for a template (see code_facts.py).
    Templates with no reference docs (pure TOC pages) get none, as before."""
    docs = TEMPLATE_TO_REF_DOCS.get(template_name, [])
    if not docs:
        return ""
    modules = code_facts.modules_for_ref_docs(docs, REF_STUBS_DIR)
    return code_facts.build_digest(facts, modules, template_text, budget, focus=focus)


def load_grounding(template_name: str, template_text: str = "", facts=None,
                   mode: str = "html", budget: int = 0, focus: set[str] | None = None) -> str:
    """Grounding for one template in the requested mode."""
    if mode == "html" or facts is None:
        return load_html_grounding(template_name)
    digest = load_facts_grounding(template_name, template_text, facts, budget, focus)
    if mode == "both" and digest:
        return digest + "\n\n--- RENDERED REFERENCE PAGES ---\n\n" + load_html_grounding(template_name)
    return digest


def _completion(messages: list[dict], model: str) -> str:
    max_tokens = int(os.getenv("DOCS_SYNTHESIS_MAX_TOKENS") or DEFAULT_MAX_TOKENS)
    """One model call. Retries once on a rate limit — a single run makes
    several sequential calls, which free-tier keys can plausibly exceed."""
    for attempt in range(2):
        try:
            response = litellm.completion(
                model=model,
                messages=messages,
                temperature=0,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except litellm.RateLimitError:
            if attempt == 1:
                raise
            print("  ! Rate limited, waiting 30s before one retry...")
            time.sleep(30)


def build_messages(template_text: str, grounding_text: str, purpose: str = "") -> list[dict]:
    if grounding_text.startswith("# CODE FACTS"):
        reference_section = (
            "REFERENCE — CODE FACTS (source all imports, field names and "
            "examples from here only):\n\n"
            f"{grounding_text}"
        )
    elif grounding_text:
        reference_section = (
            "REFERENCE DOCS (source all field names and examples from here only):\n\n"
            f"{grounding_text}"
        )
    else:
        # A template with no grounding docs (e.g. a pure TOC page) still
        # has placeholders that need filling — they just don't need any
        # field names or code sourced from a reference doc. Without this,
        # the model has repeatedly left such placeholders untouched,
        # apparently reading rule 3 ("source ONLY from reference docs") as
        # forbidding it from writing anything when that section is empty.
        reference_section = (
            "REFERENCE DOCS: none needed for this template — it has no code "
            "examples or field names to source. Fill its placeholder(s) using "
            "only the descriptive context already given in the template below."
        )
    purpose_section = f"PAGE PURPOSE: {purpose}\n\n---\n\n" if purpose else ""
    user_prompt = (
        f"{reference_section}\n\n"
        "---\n\n"
        f"{purpose_section}"
        "TEMPLATE (fill every [PLACEHOLDER: ...] block, touch nothing else):\n\n"
        f"{template_text}"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_prompt},
    ]


def fill_template(template_text: str, grounding_text: str, model: str, purpose: str = "") -> str:
    """Call Gemini to fill template placeholders."""
    return _completion(build_messages(template_text, grounding_text, purpose), model)


def repair_template(template_text: str, grounding_text: str, model: str,
                    previous: str, errors: list[str], purpose: str = "") -> str:
    """Follow-up call: show the model its own output and the validation
    errors, ask for a corrected full page. Only paid for on failure."""
    messages = build_messages(template_text, grounding_text, purpose) + [
        {"role": "assistant", "content": previous},
        {"role": "user", "content": (
            "Your output failed automated validation:\n"
            + "\n".join(f"- {e}" for e in errors)
            + "\n\nReturn the complete corrected markdown for the whole template, "
            "following every rule above. Change only what is needed to fix these "
            "errors."
        )},
    ]
    return _completion(messages, model)


def append_version_footer(content: str, version: str) -> str:
    """Stamp filled file with synthesized-for version footer."""
    return content.rstrip() + f"\n\n<!-- synthesized-for: {version} -->\n"


def validate_output(filled: str, template: str, facts=None) -> tuple[bool, list[str]]:
    """Validate a filled template (checks 1-3, plus 4 when facts are given)."""
    errors = []
    known_fields = KNOWN_FIELDS | (facts.known_names if facts is not None else set())

    # Check 1: No unfilled placeholders remain
    if "[PLACEHOLDER:" in filled:
        # Preview via string slicing, not a [^\]]+ regex — a placeholder's
        # own instruction text can contain literal ']' characters (e.g.
        # "lifecycle markers [INIT], [RUNNING]"), which truncated matches
        # mid-placeholder and made the diagnostic unreadable.
        count = filled.count("[PLACEHOLDER:")
        previews = []
        idx = 0
        for _ in range(count):
            idx = filled.index("[PLACEHOLDER:", idx)
            previews.append(filled[idx:idx + 80].replace("\n", " ") + "...")
            idx += 1
        errors.append(f"{count} unfilled placeholder(s) remain: {previews}")

    # Check 2: Markdown heading structure preserved (level + order, not
    # exact wording — the model has repeatedly reworded one specific H1
    # despite explicit instructions to copy headings verbatim, while H2/H3
    # headings have stayed exact across every run observed so far).
    def extract_headings(md: str) -> list[str]:
        # Strip fenced code blocks first — templates explicitly ask for
        # inline `# comments` in generated code, and a Python comment like
        # "# Open the wrapper session..." otherwise matches the same regex
        # as a markdown heading.
        without_code = re.sub(r'```.*?```', '', md, flags=re.S)
        return re.findall(r'^(#{1,3} .+)$', without_code, re.M)

    def heading_levels(headings: list[str]) -> list[str]:
        return [h.split(" ", 1)[0] for h in headings]

    template_headings = extract_headings(template)
    filled_headings = extract_headings(filled)
    if heading_levels(template_headings) != heading_levels(filled_headings):
        errors.append(
            f"Heading structure changed.\n"
            f"  Expected: {template_headings}\n"
            f"  Got:      {filled_headings}"
        )

    # Check 3: No invented field names in code blocks
    def strip_strings_and_comments(code: str) -> str:
        # Real reference values (e.g. a default like "./cache/cache.sqlite",
        # or an illustrative example URL) legitimately appear inside string
        # literals and comments. Strip those before scanning for attribute
        # access so quoted text isn't mistaken for `cascade.<attr>` usage.
        code = re.sub(r'""".*?"""|\'\'\'.*?\'\'\'', '', code, flags=re.S)
        code = re.sub(r'"[^"\n]*"|\'[^\'\n]*\'', '', code)
        code = re.sub(r'#.*$', '', code, flags=re.M)
        return code

    if code_facts is not None:
        code_blocks = code_facts.python_code_blocks(filled)
    else:
        code_blocks = re.findall(r'```(?:python)?(.*?)```', filled, re.S)
    invented = {}
    for block in code_blocks:
        cleaned = strip_strings_and_comments(block)
        for m in re.finditer(
            r'(?:result|asset|cascade|response|msg|pref)\.(\w+)', cleaned
        ):
            attr = m.group(1)
            if attr not in known_fields and not attr.startswith("_") and attr not in invented:
                start = max(0, m.start() - 30)
                invented[attr] = cleaned[start:m.end() + 15].strip()
    if invented:
        details = [f"{attr!r} (near: ...{ctx}...)" for attr, ctx in sorted(invented.items())]
        errors.append(f"Potentially invented field names: {details}")

    # Check 4: imports / operations / keyword arguments exist in the real API
    if facts is not None:
        errors.extend(code_facts.check_code_against_facts(filled, facts))

    return len(errors) == 0, errors


# ============================================================================
# Main
# ============================================================================


def main():
    version = os.environ["LIBRARY_VERSION"]
    # os.getenv's default only applies when the var is absent — but an unset
    # GitHub Actions repo variable still defines the env var, just as "".
    model   = os.getenv("DOCS_SYNTHESIS_MODEL") or "gemini/gemini-3.5-flash-lite"

    mode    = (os.getenv("DOCS_GROUNDING_MODE") or "facts").lower()
    budget  = int(os.getenv("DOCS_FACTS_TOKEN_BUDGET") or 0) or (
        code_facts.DEFAULT_TOKEN_BUDGET if code_facts else 0)
    repairs = int(os.getenv("DOCS_SYNTHESIS_REPAIR_ATTEMPTS") or 1)
    if mode not in GROUNDING_MODES:
        print(f"[synthesize_docs] Unknown DOCS_GROUNDING_MODE={mode!r}, using 'facts'")
        mode = "facts"

    print(f"[synthesize_docs] cascade_cms {version}")
    print(f"[synthesize_docs] Model: {model}")

    # Extract source-code facts once for the whole run.
    facts = None
    facts_version = None
    if mode != "html":
        if code_facts is None:
            print(f"[synthesize_docs] ! code_facts unavailable ({_CODE_FACTS_IMPORT_ERROR}); "
                  f"falling back to html grounding")
            mode = "html"
        else:
            try:
                facts = code_facts.extract()
                facts_version = facts.version
                print(f"[synthesize_docs] Code facts: {len(facts.objects)} objects, "
                      f"{len(facts.examples)} usage examples, from installed "
                      f"{code_facts.DISTRIBUTION} {facts.version}")
                if facts.version != version:
                    print(f"[synthesize_docs] ! WARNING: installed {code_facts.DISTRIBUTION} is "
                          f"{facts.version} but LIBRARY_VERSION is {version} — facts may not "
                          f"match the version being stamped", file=sys.stderr)
            except Exception as e:
                print(f"[synthesize_docs] ! Code facts extraction failed ({e!r}); "
                      f"falling back to html grounding", file=sys.stderr)
                mode = "html"
    print(f"[synthesize_docs] Grounding: {mode}"
          + (f" (budget ~{budget} tokens/template)" if mode != "html" else ""))
    print(f"[synthesize_docs] Processing {len(TEMPLATE_TO_REF_DOCS)} templates\n")

    os.makedirs(STAGING_DIR, exist_ok=True)

    filled_files = {}
    failed_files = {}
    grounding_tokens = {}
    repaired = []

    for template_name in sorted(TEMPLATE_TO_REF_DOCS.keys()):
        print(f"[synthesize_docs] {template_name} ...")

        # Load template skeleton
        tmpl_path = os.path.join(TEMPLATES_DIR, template_name)
        try:
            template, purpose, focus = parse_template(open(tmpl_path).read())
        except FileNotFoundError:
            failed_files[template_name] = [f"Template not found: {tmpl_path}"]
            print(f"  ✗ Template not found")
            continue

        # Load grounding (code facts digest and/or Phase 1 built reference docs)
        try:
            grounding = load_grounding(template_name, template, facts, mode, budget, focus)
        except (FileNotFoundError, ValueError) as e:
            failed_files[template_name] = [str(e)]
            print(f"  ✗ {e}")
            continue
        if facts is not None and focus:
            stale = code_facts.unresolved_names(facts, focus)
            if stale:
                print(f"  ! focus names not found in {code_facts.DISTRIBUTION} {facts.version} "
                      f"(update the template's focus comment): {', '.join(stale)}")
        grounding_tokens[template_name] = (len(grounding) + 3) // 4
        print(f"  · grounding ~{grounding_tokens[template_name]} tokens")

        # Call Gemini
        try:
            filled = fill_template(template, grounding, model, purpose)
        except Exception as e:
            failed_files[template_name] = [f"Model call failed: {e}"]
            print(f"  ✗ Model error: {e}")
            continue

        # Validate, with up to `repairs` corrective follow-up calls
        filled = _META_RE.sub("", filled)
        ok, errors = validate_output(filled, template, facts)
        for attempt in range(repairs):
            if ok:
                break
            print(f"  ! Validation failed, repair attempt {attempt + 1}:")
            for err in errors:
                print(f"    - {err}")
            try:
                candidate = repair_template(template, grounding, model, filled, errors, purpose)
            except Exception as e:
                print(f"  ! Repair call failed: {e}")
                break
            filled = _META_RE.sub("", candidate)
            ok, errors = validate_output(filled, template, facts)
            if ok:
                repaired.append(template_name)
        if ok:
            filled = append_version_footer(filled, version)
            filled_files[template_name] = filled
            staging_path = os.path.join(STAGING_DIR, template_name)
            open(staging_path, "w").write(filled)
            print(f"  ✓ OK")
        else:
            failed_files[template_name] = errors
            print(f"  ✗ Validation failed:")
            for err in errors:
                print(f"    - {err}")

    # Write manifest for create_pr.py
    manifest = {
        "version": version,
        "model": model,
        "filled": list(filled_files.keys()),
        "failed": failed_files,
        "grounding": {
            "mode": mode,
            "facts_version": facts_version,
            "approx_tokens": grounding_tokens,
        },
        "repaired": repaired,
    }
    open(os.path.join(STAGING_DIR, "manifest.json"), "w").write(
        json.dumps(manifest, indent=2)
    )

    print(f"\n[synthesize_docs] Filled: {len(filled_files)}  Failed: {len(failed_files)}")
    sys.exit(0)


if __name__ == "__main__":
    main()
