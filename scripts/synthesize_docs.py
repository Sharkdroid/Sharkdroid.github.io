#!/usr/bin/env python3
"""
Synthesize AI-generated narrative documentation.

For each template skeleton in wiki-templates/, loads grounding data extracted
from the Phase 1 built docs site (properdocs build output, run earlier in the
same job), calls Gemini Flash-Lite to fill [PLACEHOLDER: ...] blocks,
validates the output, appends a version footer, and writes filled files
to a staging directory for PR creation.

Validation checks:
  1. No unfilled placeholders remain
  2. Markdown structure (headings) preserved
  3. No invented field names in code blocks
"""

import os
import re
import sys
import json
import litellm
from bs4 import BeautifulSoup

# ============================================================================
# Configuration
# ============================================================================

TEMPLATES_DIR = "wiki-templates"
REF_DOCS_DIR  = "wiki/cascade-cms-wiki/site/operations"  # built HTML, not the docs/operations stubs
STAGING_DIR   = "/tmp/filled-docs"

# Maps template filename → which built reference pages to use as grounding.
# Kept here in the wiki repo — not in the library.
TEMPLATE_TO_REF_DOCS = {
    "core-concepts-index.md":    ["operations.md", "cmstypes.md", "wrapper.md"],
    "advanced-index.md":         [],    # pure TOC — no grounding needed
    "advanced-caching.md":       ["driver.md"],
    "advanced-logging.md":       ["operation_logger.md"],
    "advanced-cpu-intensive.md": ["wrapper.md", "operations.md"],
    "examples-main-patterns.md": ["operations.md", "cmstypes.md"],
    "examples-administrative.md":["operations.md", "cmstypes.md"],
}

# Maps template filename → target wiki path
TEMPLATE_TO_WIKI_PATH = {
    "core-concepts-index.md":    "wiki/cascade-cms-wiki/docs/core-concepts/index.md",
    "advanced-index.md":         "wiki/cascade-cms-wiki/docs/advanced/index.md",
    "advanced-caching.md":       "wiki/cascade-cms-wiki/docs/advanced/caching.md",
    "advanced-logging.md":       "wiki/cascade-cms-wiki/docs/advanced/logging.md",
    "advanced-cpu-intensive.md": "wiki/cascade-cms-wiki/docs/advanced/cpu-intensive.md",
    "examples-main-patterns.md": "wiki/cascade-cms-wiki/docs/examples/main-patterns.md",
    "examples-administrative.md":"wiki/cascade-cms-wiki/docs/examples/administrative.md",
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
}

SYSTEM_PROMPT = """\
You are a technical documentation writer filling placeholder sections in a \
pre-structured markdown template for a Python library wiki.

Rules — follow all of them exactly:
1. Fill every [PLACEHOLDER: ...] block with accurate, concise prose or code.
2. Do NOT modify any text outside a [PLACEHOLDER: ...] block — preserve all \
   headings, admonition blocks (!!!), tables, cross-page links, and fixed \
   code blocks exactly as given.
3. Source ALL code examples and field names ONLY from the reference docs \
   provided below. Do NOT invent field names, method signatures, or parameters \
   that do not appear in the reference docs.
4. Code examples must use the actual signatures and field names from the \
   reference docs. Do not paraphrase or rename them.
5. Do NOT leave any [PLACEHOLDER: ...] markers in the output.
6. Return ONLY the completed markdown — no preamble, no commentary, no \
   markdown fences wrapping the output.
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


def load_grounding(template_name: str) -> str:
    """Load grounding text for a template from the built reference HTML."""
    docs = TEMPLATE_TO_REF_DOCS.get(template_name, [])
    if not docs:
        return ""
    sections = []
    for doc in docs:
        html_path = _resolve_html_path(doc)
        sections.append(f"--- {doc} ---\n{extract_reference_text(html_path)}")
    return "\n\n".join(sections)


def fill_template(template_text: str, grounding_text: str, model: str) -> str:
    """Call Gemini to fill template placeholders."""
    user_prompt = (
        "REFERENCE DOCS (source all field names and examples from here only):\n\n"
        f"{grounding_text}\n\n"
        "---\n\n"
        "TEMPLATE (fill every [PLACEHOLDER: ...] block, touch nothing else):\n\n"
        f"{template_text}"
    )
    response = litellm.completion(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0,
        max_tokens=3000,
    )
    return response.choices[0].message.content.strip()


def append_version_footer(content: str, version: str) -> str:
    """Stamp filled file with synthesized-for version footer."""
    return content.rstrip() + f"\n\n<!-- synthesized-for: {version} -->\n"


def validate_output(filled: str, template: str) -> tuple[bool, list[str]]:
    """Validate filled template against three checks."""
    errors = []

    # Check 1: No unfilled placeholders remain
    if "[PLACEHOLDER:" in filled:
        remaining = re.findall(r'\[PLACEHOLDER:[^\]]+\]', filled)
        errors.append(f"Unfilled placeholders remain: {remaining}")

    # Check 2: Markdown heading structure preserved
    def extract_headings(md: str) -> list[str]:
        return re.findall(r'^(#{1,3} .+)$', md, re.M)

    if extract_headings(template) != extract_headings(filled):
        errors.append(
            f"Heading structure changed.\n"
            f"  Expected: {extract_headings(template)}\n"
            f"  Got:      {extract_headings(filled)}"
        )

    # Check 3: No invented field names in code blocks
    code_blocks = re.findall(r'```(?:python)?(.*?)```', filled, re.S)
    invented = set()
    for block in code_blocks:
        attrs = re.findall(
            r'(?:result|asset|cascade|response|msg|pref)\.(\w+)', block
        )
        for attr in attrs:
            if attr not in KNOWN_FIELDS and not attr.startswith("_"):
                invented.add(attr)
    if invented:
        errors.append(f"Potentially invented field names: {sorted(invented)}")

    return len(errors) == 0, errors


# ============================================================================
# Main
# ============================================================================


def main():
    version = os.environ["LIBRARY_VERSION"]
    model   = os.getenv("DOCS_SYNTHESIS_MODEL", "gemini/gemini-3.5-flash-lite")

    print(f"[synthesize_docs] cascade_cms {version}")
    print(f"[synthesize_docs] Model: {model}")
    print(f"[synthesize_docs] Processing {len(TEMPLATE_TO_REF_DOCS)} templates\n")

    os.makedirs(STAGING_DIR, exist_ok=True)

    filled_files = {}
    failed_files = {}

    for template_name in sorted(TEMPLATE_TO_REF_DOCS.keys()):
        print(f"[synthesize_docs] {template_name} ...")

        # Load template skeleton
        tmpl_path = os.path.join(TEMPLATES_DIR, template_name)
        try:
            template = open(tmpl_path).read()
        except FileNotFoundError:
            failed_files[template_name] = [f"Template not found: {tmpl_path}"]
            print(f"  ✗ Template not found")
            continue

        # Load grounding from Phase 1 built reference docs
        try:
            grounding = load_grounding(template_name)
        except (FileNotFoundError, ValueError) as e:
            failed_files[template_name] = [str(e)]
            print(f"  ✗ {e}")
            continue

        # Call Gemini
        try:
            filled = fill_template(template, grounding, model)
        except Exception as e:
            failed_files[template_name] = [f"Model call failed: {e}"]
            print(f"  ✗ Model error: {e}")
            continue

        # Validate
        ok, errors = validate_output(filled, template)
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
    }
    open(os.path.join(STAGING_DIR, "manifest.json"), "w").write(
        json.dumps(manifest, indent=2)
    )

    print(f"\n[synthesize_docs] Filled: {len(filled_files)}  Failed: {len(failed_files)}")
    sys.exit(0)


if __name__ == "__main__":
    main()
