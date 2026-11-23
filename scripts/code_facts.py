#!/usr/bin/env python3
"""
Extract a compact, token-budgeted digest of source-code facts for the
narrative docs synthesis (see synthesize_docs.py).

Before this module existed, the only grounding the model got was the text of
the built mkdocstrings HTML pages. That text is dominated by `show_source`
code listings (~40-60k tokens per template) while still leaving out the
things a narrative page most often gets wrong: where a name is importable
from, which names are aliases, what a pydantic field's wire name is, which
helpers a public method calls, and what the library's own current usage
examples look like.

This module reads those facts straight from the *installed* package, so they
always match the version PyPI published:

  * griffe (already installed — it's the engine behind mkdocstrings[python])
    supplies the API surface: modules, classes and their bases, signatures
    with annotations and defaults, overloads, pydantic/dataclass fields and
    their aliases, type aliases, constants, re-exports and parsed Google-style
    docstrings.
  * stdlib `ast` supplies what griffe does not model: a depth-limited call
    graph, the exceptions each function raises, and calls whose arguments are
    all literals (e.g. `asyncio.Semaphore(50)`), which pin down the concrete
    numbers a narrative page tends to quote.
  * The package's own README (shipped in its wheel metadata) and docstring
    code blocks supply current, author-written usage examples.

The digest is rendered as Python-stub-like text — the format a model reads
most cheaply and most accurately — and symbols the template actually mentions
get full detail while everything else is reduced to one-line signatures, then
trimmed further until the whole digest fits a token budget.

Run directly to preview what a template would receive:

    python scripts/code_facts.py wiki-templates/advanced-cpu-intensive.md
"""

from __future__ import annotations

import ast
import importlib.metadata
import os
import re
import sys
from dataclasses import dataclass, field

import logging

import griffe

# griffe logs every missing annotation it meets; mkdocs already reports those.
logging.getLogger("griffe").setLevel(logging.ERROR)

PACKAGE = "cascade_cms"
DISTRIBUTION = "cascade-cms-rest"

# Rough chars-per-token for Gemini/English+code. Only used for budgeting and
# logging, so an estimate is enough — no tokenizer dependency.
CHARS_PER_TOKEN = 4
DEFAULT_TOKEN_BUDGET = 9000

# Callees in these modules are bookkeeping (console/logfile output), not
# behaviour a narrative page describes; they're left out of `# calls:`.
CALL_GRAPH_IGNORE_MODULES = ("utils.operation_logger",)
MAX_CALLEES_SHOWN = 8

# Parameter names too common in prose to signal relevance on their own.
GENERIC_PARAM_WORDS = {
    "asset", "assets", "callback", "debug", "identifier", "identifiers", "logger",
    "message", "operation", "parser", "payload", "request", "requests", "result",
    "results", "session", "value", "values",
}

# Detail levels, highest first.
FULL, BRIEF, NAME = 2, 1, 0


def estimate_tokens(text: str) -> int:
    return (len(text) + CHARS_PER_TOKEN - 1) // CHARS_PER_TOKEN


# ============================================================================
# Data model
# ============================================================================


@dataclass
class CallInfo:
    calls: set[str] = field(default_factory=set)      # in-package qualnames
    raises: set[str] = field(default_factory=set)     # exception names
    literals: set[str] = field(default_factory=set)   # e.g. "asyncio.Semaphore(50)"


@dataclass
class Facts:
    """Everything extracted from one package, independent of any template."""

    package: griffe.Module
    version: str
    # qualname ("wrapper.Cascade.submit_requests") -> griffe object
    objects: dict[str, griffe.Object] = field(default_factory=dict)
    # short name ("submit_requests") -> qualnames
    by_name: dict[str, set[str]] = field(default_factory=dict)
    # qualname -> CallInfo (functions only)
    calls: dict[str, CallInfo] = field(default_factory=dict)
    # "Cascade" -> {"cascade_cms", "cascade_cms.wrapper", ...}: every module
    # a name can legally be imported from (incl. incidental re-imports)
    import_paths: dict[str, set[str]] = field(default_factory=dict)
    # "Cascade" -> "cascade_cms.wrapper": where it is defined
    canonical: dict[str, str] = field(default_factory=dict)
    # parameter name -> qualnames of public functions taking it
    params: dict[str, set[str]] = field(default_factory=dict)
    # dotted module paths that exist, e.g. "cascade_cms.utils.operation_logger"
    modules: set[str] = field(default_factory=set)
    # "CascadeWrapperBase" -> "Cascade"
    aliases: dict[str, str] = field(default_factory=dict)
    # Every identifier a correct example could use as an attribute / kwarg.
    known_names: set[str] = field(default_factory=set)
    # (title, code) pairs from README + docstrings
    examples: list[tuple[str, str]] = field(default_factory=list)

    # ---- lookups used by the validator ---------------------------------

    def params_of(self, name: str) -> set[str] | None:
        """Union of keyword names accepted by every callable called `name`
        (a method name is ambiguous across classes). None = unknown or it
        accepts **kwargs, i.e. don't check."""
        accepted: set[str] = set()
        found = False
        for qn in self.by_name.get(name, ()):
            obj = self.objects[qn]
            if obj.is_class:
                # Pydantic models / dataclasses take their fields (by name or
                # alias); plain classes take __init__'s parameters.
                init = obj.members.get("__init__")
                if init is not None and init.is_function:
                    obj = init
                else:
                    for fld in _fields(obj):
                        accepted.add(fld.name)
                        accepted.update(_field_aliases(fld))
                    found = True
                    # inherited fields — be permissive rather than wrong
                    if obj.bases:
                        return None
                    continue
            if not obj.is_function:
                continue
            found = True
            for p in obj.parameters:
                if p.kind is griffe.ParameterKind.var_keyword:
                    return None
                accepted.add(p.name)
        return accepted if found else None


# ============================================================================
# Extraction
# ============================================================================


def _is_public(name: str) -> bool:
    return not name.startswith("_") or name in ("__init__", "__enter__", "__exit__", "__call__")


def _fields(cls: griffe.Class) -> list[griffe.Attribute]:
    return [
        m for m in cls.members.values()
        if not m.is_alias and m.is_attribute and "class-attribute" in m.labels
        and m.annotation is not None and _is_public(m.name)
        and not m.name.startswith("model_")
    ]


_ALIAS_RE = re.compile(r"(?:validation_alias|serialization_alias|alias)\s*=\s*['\"](\w+)['\"]")


def _field_aliases(attr: griffe.Attribute) -> set[str]:
    return set(_ALIAS_RE.findall(str(attr.value or "")))


def _walk(obj: griffe.Object, prefix: str, out: dict[str, griffe.Object]) -> None:
    for name, member in obj.members.items():
        qn = f"{prefix}.{name}" if prefix else name
        if member.is_alias:
            # Imports of external names (json, pydantic.BaseModel, ...) show
            # up as aliases too; only in-package re-exports are facts.
            if member.target_path.split(".")[0] == PACKAGE:
                out[qn] = member
            continue
        out[qn] = member
        if member.is_module or member.is_class:
            _walk(member, qn, out)


def _docstring_code_blocks(text: str) -> list[str]:
    """Fenced blocks, plus indented blocks introduced by 'Use as:' /
    'Example:' / '>>>' lines, which is how this library writes examples."""
    blocks = [b.strip("\n") for b in re.findall(r"```(?:python|py)?\n(.*?)```", text, re.S)]
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if _EXAMPLE_HEAD_RE.match(lines[i]):
            base = len(lines[i]) - len(lines[i].lstrip())
            j, chunk = i + 1, []
            while j < len(lines) and (not lines[j].strip() or
                                      len(lines[j]) - len(lines[j].lstrip()) > base):
                chunk.append(lines[j])
                j += 1
            code = _dedent("\n".join(chunk)).strip("\n")
            if code and "```" not in code:
                blocks.append(code)
            i = j
        else:
            i += 1
    return [b for b in blocks if b.strip()]


# "Use as:", "Example:", "Example (CPU-bound callbacks):", ...
_EXAMPLE_HEAD_RE = re.compile(r"\s*(Use as|Usage|Examples?)(\s*\([^)]*\))?\s*:\s*$")


def _dedent(text: str) -> str:
    import textwrap
    return textwrap.dedent(text)


def _readme_examples() -> list[tuple[str, str]]:
    """Python code blocks from the README shipped in the wheel's metadata,
    titled by the nearest preceding markdown heading."""
    try:
        meta = importlib.metadata.metadata(DISTRIBUTION)
    except importlib.metadata.PackageNotFoundError:
        return []
    readme = meta.get_payload() or meta.get("Description") or ""
    out, heading = [], "README"
    for part in re.split(r"(```(?:python|py)\n.*?```)", readme, flags=re.S):
        if part.startswith("```"):
            out.append((f"README — {heading}", part.split("\n", 1)[1].rsplit("```", 1)[0].strip("\n")))
        else:
            hs = re.findall(r"^#{1,6}\s+(.+)$", part, re.M)
            if hs:
                heading = hs[-1].strip()
    return out


class _CallVisitor(ast.NodeVisitor):
    """Collects call targets / raises / literal-arg calls inside one function,
    without descending into nested function definitions' own entries (their
    calls are attributed to the enclosing function, which is what a reader
    of the enclosing function's behaviour cares about)."""

    def __init__(self) -> None:
        self.info = CallInfo()
        self.raw_calls: set[tuple[str | None, str]] = set()  # (receiver, name)

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        if isinstance(func, ast.Name):
            self.raw_calls.add((None, func.id))
        elif isinstance(func, ast.Attribute):
            recv = func.value.id if isinstance(func.value, ast.Name) else None
            self.raw_calls.add((recv, func.attr))
        if node.args and all(isinstance(a, ast.Constant) for a in node.args) and not node.keywords:
            try:
                text = ast.unparse(node)
                if len(text) <= 60 and not text.startswith(("print(", "str(", "len(", "isinstance(")):
                    self.info.literals.add(text)
            except Exception:
                pass
        self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> None:
        exc = node.exc
        if isinstance(exc, ast.Call):
            exc = exc.func
        if isinstance(exc, ast.Name):
            self.info.raises.add(exc.id)
        elif isinstance(exc, ast.Attribute):
            self.info.raises.add(exc.attr)
        self.generic_visit(node)


def _build_call_graph(facts: Facts) -> None:
    """Parse every module once with ast and resolve call targets to
    in-package qualnames by short name (same class first, then module, then
    anywhere in the package)."""
    for qn, obj in list(facts.objects.items()):
        if obj.is_alias or not obj.is_module:
            continue
        path = obj.filepath
        if not isinstance(path, os.PathLike | str) or not os.path.exists(path):
            continue
        try:
            tree = ast.parse(open(path, encoding="utf-8").read())
        except SyntaxError:
            continue

        def visit(body, scope: str, cls: str | None, module_qn: str) -> None:
            for node in body:
                if isinstance(node, ast.ClassDef):
                    visit(node.body, f"{scope}.{node.name}", f"{scope}.{node.name}", module_qn)
                elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    fqn = f"{scope}.{node.name}"
                    v = _CallVisitor()
                    for stmt in node.body:
                        v.visit(stmt)
                    info = facts.calls.setdefault(fqn, CallInfo())
                    info.raises |= v.info.raises
                    info.literals |= v.info.literals
                    for recv, name in v.raw_calls:
                        target = _resolve_call(facts, recv, name, cls, scope_module=module_qn)
                        if target and target != fqn:
                            info.calls.add(target)

        visit(tree.body, qn, None, qn)


def _resolve_call(facts: Facts, recv: str | None, name: str, cls: str | None,
                  scope_module: str) -> str | None:
    candidates = facts.by_name.get(name)
    if not candidates:
        return None
    if recv in ("self", "cls") and cls and f"{cls}.{name}" in facts.objects:
        return f"{cls}.{name}"
    local = facts.objects.get(f"{scope_module}.{name}")
    if recv is None and local is not None:
        if local.is_alias:  # `from .utils.failures import ChainResults`
            return local.target_path.removeprefix(PACKAGE + ".")
        return f"{scope_module}.{name}"
    # Module-qualified (`cmstypes.resolve_identifier`) or unique elsewhere.
    real = [c for c in candidates if not facts.objects[c].is_alias]
    if len(real) == 1:
        return real[0]
    return None


def extract(package: str = PACKAGE) -> Facts:
    """Load the installed package and build its Facts. Raises on failure
    (callers fall back to HTML grounding)."""
    pkg = griffe.load(package, resolve_aliases=True, resolve_external=False,
                      docstring_parser=griffe.Parser.google)
    try:
        version = importlib.metadata.version(DISTRIBUTION)
    except importlib.metadata.PackageNotFoundError:
        version = "unknown"

    facts = Facts(package=pkg, version=version)
    _walk(pkg, "", facts.objects)

    for qn, obj in facts.objects.items():
        facts.by_name.setdefault(qn.rsplit(".", 1)[-1], set()).add(qn)
        if obj.is_alias:
            continue
        if obj.is_module:
            facts.modules.add(f"{package}.{qn}")
        if obj.is_attribute and not obj.is_alias:
            facts.known_names.update(_field_aliases(obj))
        if _is_public(obj.name):
            facts.known_names.add(obj.name)
            if obj.is_function:
                for prm in obj.parameters:
                    if prm.name not in ("self", "cls"):
                        facts.params.setdefault(prm.name, set()).add(qn)
                        facts.known_names.add(prm.name)
    facts.modules.add(package)

    # Import paths: where each public name is defined, plus every module that
    # re-exports it. Module-level `X = Y` aliases of a class are recorded too.
    def record_imports(mod: griffe.Module, dotted: str) -> None:
        for name, member in mod.members.items():
            if not _is_public(name) or name == "__all__":
                continue
            if member.is_alias and member.target_path.split(".")[0] != PACKAGE:
                continue
            if member.is_module:
                record_imports(member, f"{dotted}.{name}")
                continue
            facts.import_paths.setdefault(name, set()).add(dotted)
            if not member.is_alias:
                if str(getattr(member, "value", "") or "").startswith("TypeVar("):
                    continue
                facts.canonical.setdefault(name, dotted)
            if member.is_attribute and not member.is_alias:
                value = str(member.value or "")
                if re.fullmatch(r"[A-Z]\w*", value) and value in mod.members:
                    facts.aliases[name] = value

    record_imports(pkg, package)

    # Usage examples: README first (most curated), then docstrings.
    facts.examples.extend(_readme_examples())
    for qn, obj in facts.objects.items():
        if obj.is_alias or not obj.docstring or not _is_public(obj.name):
            continue
        for code in _docstring_code_blocks(obj.docstring.value):
            if re.search(r"\b(cascade|Cascade|operations|submit_requests)\b", code):
                facts.examples.append((f"docstring of {qn}", code))

    _build_call_graph(facts)
    return facts


# ============================================================================
# Relevance: which symbols does a template talk about?
# ============================================================================

_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def template_mentions(template_text: str) -> set[str]:
    """Identifiers a template names in code spans / code blocks / prose
    (CamelCase or snake/camel with an underscore or an inner capital)."""
    mentions: set[str] = set()
    for span in re.findall(r"`([^`\n]+)`", template_text):
        mentions.update(_IDENT_RE.findall(span))
    for block in re.findall(r"```.*?```", template_text, re.S):
        mentions.update(_IDENT_RE.findall(block))
    mentions.update(re.findall(r"\b[A-Z][a-z]+[A-Z]\w*\b", template_text))   # CamelCase
    mentions.update(re.findall(r"\b[a-z]+[A-Z]\w*\b", template_text))         # camelCase
    mentions.update(re.findall(r"\b[a-z]+_[a-z_]+\b", template_text))         # snake_case
    return mentions


def select_detail(facts: Facts, modules: list[str], mentions: set[str],
                  template_text: str = "") -> dict[str, int]:
    """qualname -> detail level for everything that goes in the digest."""
    detail: dict[str, int] = {}

    def bump(qn: str, level: int) -> None:
        if qn in facts.objects and detail.get(qn, -1) < level:
            detail[qn] = level

    # 1. Everything public in the mapped reference modules, briefly.
    for mod in modules:
        prefix = mod.removeprefix(PACKAGE).lstrip(".")
        for qn, obj in facts.objects.items():
            if obj.is_alias or obj.is_module or not _is_public(obj.name):
                continue
            parent = qn.rsplit(".", 1)[0] if "." in qn else ""
            if parent == prefix or (parent.startswith(prefix + ".") and
                                    facts.objects.get(parent) is not None and
                                    facts.objects[parent].is_class):
                bump(qn, BRIEF)

    # 2. Anything the template mentions, anywhere in the package, in full —
    #    plus its owning class, so a mentioned method has context. Generic
    #    member names ("id", "name", "path") only count when their class is
    #    in scope; otherwise every model with an `id` field would be pulled in.
    mapped = {m.removeprefix(PACKAGE).lstrip(".") for m in modules}
    resolved_mentions = {facts.aliases.get(n, n) for n in mentions}

    def distinctive(name: str) -> bool:
        return len(name) >= 6 and (bool(re.search(r"[A-Z_]", name[1:])) or len(name) >= 9)

    for name in resolved_mentions:
        for qn in facts.by_name.get(name, ()):
            obj = facts.objects[qn]
            if obj.is_alias or obj.is_module or not _is_public(obj.name):
                continue
            owner = qn.rsplit(".", 1)[0] if "." in qn else ""
            owner_obj = facts.objects.get(owner)
            if owner_obj is not None and owner_obj.is_class:
                owner_module = owner.rsplit(".", 1)[0] if "." in owner else ""
                if not (distinctive(name) or owner_obj.name in resolved_mentions
                        or owner_module in mapped):
                    continue
            bump(qn, FULL)
            owner = qn.rsplit(".", 1)[0]
            if owner in facts.objects and facts.objects[owner].is_class:
                bump(owner, BRIEF)
            if obj.is_class:
                for mname, member in obj.members.items():
                    if _is_public(mname) and not member.is_alias:
                        bump(f"{qn}.{mname}", BRIEF)

    # 2b. Prose that names a parameter ("pass an executor") promotes the few
    #     public functions taking it — that's usually where the behaviour the
    #     template describes is actually configured.
    prose_words = {w.lower() for w in _IDENT_RE.findall(template_text)}
    for pname, qns in facts.params.items():
        if (pname.lower() in prose_words and len(pname) >= 6 and len(qns) <= 4
                and pname.lower() not in GENERIC_PARAM_WORDS):
            for qn in qns:
                bump(qn, FULL)
                owner = qn.rsplit(".", 1)[0]
                if owner in facts.objects and facts.objects[owner].is_class:
                    bump(owner, BRIEF)

    # 3. UPPER_CASE constants anywhere in the package (limits, defaults such
    #    as `MAX_REQUESTS = 50`): cheap, and exactly the numbers prose quotes.
    for qn, obj in facts.objects.items():
        if (not obj.is_alias and obj.is_attribute and re.fullmatch(r"[A-Z][A-Z0-9_]+", obj.name)
                and obj.value is not None and len(str(obj.value)) <= 80):
            bump(qn, BRIEF)
            owner = qn.rsplit(".", 1)[0]
            if owner in facts.objects and facts.objects[owner].is_class:
                bump(owner, NAME)
    return detail


def _public_callees(facts: Facts, qn: str, depth: int) -> list[str]:
    """Public in-package functions reached from `qn`, looking through private
    helpers (which aren't documented) up to `depth` hops."""
    seen, out, frontier = {qn}, [], [qn]
    for _ in range(depth):
        nxt = []
        for f in frontier:
            for c in sorted(facts.calls.get(f, CallInfo()).calls):
                if c in seen:
                    continue
                seen.add(c)
                if c.startswith(CALL_GRAPH_IGNORE_MODULES):
                    continue
                if _is_public(c.rsplit(".", 1)[-1]):
                    out.append(c)
                else:
                    nxt.append(c)
        frontier = nxt
    return out


def _all_raises(facts: Facts, qn: str) -> set[str]:
    """Exceptions raised by `qn` or by its private helpers (depth 2)."""
    raises = set(facts.calls.get(qn, CallInfo()).raises)
    seen, frontier = {qn}, [qn]
    for _ in range(2):
        nxt = []
        for f in frontier:
            for c in facts.calls.get(f, CallInfo()).calls:
                if c not in seen and not _is_public(c.rsplit(".", 1)[-1]):
                    seen.add(c)
                    raises |= facts.calls.get(c, CallInfo()).raises
                    nxt.append(c)
        frontier = nxt
    return raises


# ============================================================================
# Rendering
# ============================================================================


def _clip(text: str, n: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def _summary(obj: griffe.Object, n: int = 140) -> str:
    if not obj.docstring:
        return ""
    first = obj.docstring.value.strip().split("\n\n", 1)[0]
    return _clip(first, n)


def _signature(fn: griffe.Function) -> str:
    parts, saw_kwonly, last_posonly = [], False, False
    for p in fn.parameters:
        if p.name in ("self", "cls") and not parts:
            continue
        if p.kind is griffe.ParameterKind.positional_only:
            last_posonly = True
        elif last_posonly:
            parts.append("/")
            last_posonly = False
        if p.kind is griffe.ParameterKind.keyword_only and not saw_kwonly:
            parts.append("*")
            saw_kwonly = True
        if p.kind is griffe.ParameterKind.var_positional:
            saw_kwonly = True
            s = f"*{p.name}"
        elif p.kind is griffe.ParameterKind.var_keyword:
            s = f"**{p.name}"
        else:
            s = p.name
        if p.annotation is not None:
            s += f": {p.annotation}"
        if p.default is not None:
            s += f" = {_clip(str(p.default), 50)}" if p.annotation is not None else f"={_clip(str(p.default), 50)}"
        parts.append(s)
    if last_posonly:
        parts.append("/")
    ret = f" -> {fn.returns}" if fn.returns is not None else ""
    prefix = "async def" if "async" in fn.labels else "def"
    return f"{prefix} {fn.name}({', '.join(parts)}){ret}"


def _docstring_detail(obj: griffe.Object, indent: str, budget_chars: int) -> list[str]:
    """Full-detail docstring: summary + description (clipped) + compact
    Args/Returns/Raises lines. Code examples are left to the examples
    section so they aren't paid for twice."""
    if not obj.docstring:
        return []
    lines: list[str] = []
    try:
        sections = obj.docstring.parse(griffe.Parser.google)
    except Exception:
        sections = []
    text_parts = []
    for sec in sections:
        kind = sec.kind.value
        if kind == "text":
            body = re.sub(r"```.*?```", "", sec.value, flags=re.S)
            body = re.sub(r"\n\s*(Use as|Usage|Examples?)(\s*\([^)]*\))?\s*:.*", "", body, flags=re.S)
            text_parts.append(body)
        elif kind == "parameters":
            for p in sec.value:
                if p.description:
                    lines.append(f"{indent}#   {p.name}: {_clip(p.description, 160)}")
        elif kind == "returns":
            # Google "Returns:" prose containing a colon parses as several
            # named items; it's one description, so join it back up.
            desc = " ".join(f"{r.name}: {r.description}" if r.name and r.description else
                            (r.description or r.name or "") for r in sec.value)
            if desc.strip():
                lines.append(f"{indent}#   returns: {_clip(desc, 240)}")
        elif kind == "raises":
            for r in sec.value:
                lines.append(f"{indent}#   raises {r.annotation}: {_clip(r.description or '', 120)}")
    prose = _clip(" ".join(text_parts), budget_chars)
    head = [f'{indent}"""{prose}"""'] if prose else []
    return head + lines


def _render_function(facts: Facts, qn: str, fn: griffe.Function, level: int, indent: str) -> list[str]:
    out = []
    overloads = getattr(fn, "overloads", None) or []
    decorators = [str(d.value) for d in fn.decorators if "overload" not in str(d.value)]
    for deco in decorators:
        if deco in ("classmethod", "staticmethod", "property") or level == FULL:
            out.append(f"{indent}@{deco}")
    if overloads and level >= BRIEF:
        for ov in overloads:
            out.append(f"{indent}@overload {_signature(ov)}")
    out.append(f"{indent}{_signature(fn)}")
    if level == FULL:
        out.extend(_docstring_detail(fn, indent + "    ", 600))
        callees = _public_callees(facts, qn, 2)[:MAX_CALLEES_SHOWN]
        if callees:
            out.append(f"{indent}    # calls: {', '.join(callees)}")
        raises = sorted(_all_raises(facts, qn))
        if raises:
            out.append(f"{indent}    # raises: {', '.join(raises)}")
        lits = sorted(facts.calls.get(qn, CallInfo()).literals)[:5]
        if lits:
            out.append(f"{indent}    # literal calls: {'; '.join(lits)}")
    elif level == BRIEF:
        s = _summary(fn, 120)
        if s:
            out.append(f"{indent}    # {s}")
    return out


def _render_attribute(attr: griffe.Attribute, level: int, indent: str) -> list[str]:
    s = attr.name
    if attr.annotation is not None:
        s += f": {attr.annotation}"
    value = str(attr.value) if attr.value is not None else None
    if value and value.startswith("Field("):
        # Pydantic Field(...): only the default matters to a caller; the
        # aliases are reported separately below.
        m = re.search(r"\bdefault(?:_factory)?\s*=\s*([^,)]+(?:\([^)]*\))?)", value)
        value = m.group(1).strip() if m else None
    if value is not None:
        limit = 400 if level == FULL else 70
        s += f" = {_clip(value, limit)}"
    aliases = _field_aliases(attr) - {attr.name}
    if aliases:
        s += f"  # kwarg/JSON alias: {', '.join(sorted(aliases))}"
    lines = [f"{indent}{s}"]
    if level == FULL and attr.docstring:
        lines.append(f"{indent}    # {_summary(attr, 200)}")
    return lines


def _render_class(facts: Facts, qn: str, cls: griffe.Class, detail: dict[str, int]) -> list[str]:
    level = detail[qn]
    bases = ", ".join(str(b) for b in cls.bases)
    head = f"class {cls.name}({bases}):" if bases else f"class {cls.name}:"
    alias_of = [a for a, t in facts.aliases.items() if t == cls.name]
    if alias_of:
        head += f"  # also importable as: {', '.join(alias_of)} (alias)"
    out = [head]
    if level == FULL:
        out.extend(_docstring_detail(cls, "    ", 900))
    elif level == BRIEF:
        s = _summary(cls)
        if s:
            out.append(f"    # {s}")
    members_out = 0
    skipped = []
    for mname, member in cls.members.items():
        mqn = f"{qn}.{mname}"
        if member.is_alias or not _is_public(mname):
            continue
        mlevel = detail.get(mqn)
        if mlevel is None:
            if level >= BRIEF:
                skipped.append(mname)
            continue
        if member.is_function:
            out.extend(_render_function(facts, mqn, member, mlevel, "    "))
        elif member.is_attribute:
            out.extend(_render_attribute(member, mlevel, "    "))
        elif member.is_class:
            out.append(f"    class {mname}: ...")
        members_out += 1
    if skipped:
        out.append(f"    # other members: {', '.join(skipped)}")
    elif not members_out and level < FULL:
        out[-1] = out[-1] + (" ..." if out[-1].endswith(":") else "")
    return out


def _render_type_alias(obj: griffe.Object, level: int) -> list[str]:
    value = str(getattr(obj, "value", "") or "")
    m = re.fullmatch(r"Literal\[(.*)\]", value, re.S)
    if m and level < FULL:
        items = [x.strip() for x in m.group(1).split(",") if x.strip()]
        if len(items) > 12:
            value = f"Literal[{', '.join(items[:12])}, … (+{len(items) - 12} more)]"
    return [f"type {obj.name} = {_clip(value, 2000 if level == FULL else 300)}"]


def _render_module_section(facts: Facts, module_qn: str, detail: dict[str, int]) -> list[str]:
    mod = facts.objects.get(module_qn) if module_qn else facts.package
    if mod is None:
        return []
    out = [f"# ---- module {PACKAGE}{'.' + module_qn if module_qn else ''} ----"]
    for name, obj in mod.members.items():
        qn = f"{module_qn}.{name}" if module_qn else name
        if qn not in detail or obj.is_alias or obj.is_module:
            continue
        level = detail[qn]
        if obj.is_class:
            out.extend(_render_class(facts, qn, obj, detail))
        elif obj.is_function:
            out.extend(_render_function(facts, qn, obj, level, ""))
        elif obj.kind.value == "type alias":
            out.extend(_render_type_alias(obj, level))
        elif obj.is_attribute:
            if name in ("T",) or str(obj.value or "").startswith("TypeVar("):
                continue
            out.extend(_render_attribute(obj, level, ""))
    return out if len(out) > 1 else []


def _render_imports(facts: Facts, names: set[str]) -> list[str]:
    out = ["# ---- import paths (only these are valid) ----"]
    top = sorted(n for n, mods in facts.import_paths.items() if PACKAGE in mods)
    if top:
        out.append(f"from {PACKAGE} import {', '.join(top)}")
    for alias, target in sorted(facts.aliases.items()):
        out.append(f"# {alias} is an alias of {target} (same class); prefer {target}")
    per_module: dict[str, list[str]] = {}
    for name in sorted(names):
        mod = facts.canonical.get(name)
        if mod and mod != PACKAGE and not (PACKAGE in facts.import_paths.get(name, ())
                                           and name in top):
            per_module.setdefault(mod, []).append(name)
    for mod, ns in sorted(per_module.items()):
        out.append(f"from {mod} import {', '.join(sorted(set(ns)))}")
    return out


def _rank_examples(facts: Facts, mentions: set[str]) -> list[tuple[int, str, str]]:
    ranked = []
    for idx, (title, code) in enumerate(facts.examples):
        idents = set(_IDENT_RE.findall(code))
        score = len(idents & mentions)
        # README order is meaningful (quick start first), so it breaks ties.
        ranked.append((score, -idx, title, code))
    ranked.sort(reverse=True)
    return [(s, t, c) for s, _, t, c in ranked]


def unresolved_names(facts: Facts, names: set[str]) -> list[str]:
    """Names (e.g. a template's `<!-- focus: -->` list) that match nothing in
    the package — a sign the template's focus list has gone stale. Stdlib
    names a template legitimately focuses on (ProcessPoolExecutor) count as
    resolved when they appear in some signature or docstring."""
    out = []
    for name in sorted(names):
        target = facts.aliases.get(name, name)
        if target in facts.by_name or target in facts.params:
            continue
        if any(o.docstring and name in o.docstring.value
               for o in facts.objects.values() if not o.is_alias):
            continue
        out.append(name)
    return out


def build_digest(facts: Facts, modules: list[str], template_text: str,
                 token_budget: int = DEFAULT_TOKEN_BUDGET,
                 focus: set[str] | None = None) -> str:
    """Render the digest for one template, trimmed to `token_budget`.
    `focus` names (from the template's focus comment) count as mentions."""
    mentions = template_mentions(template_text) | set(focus or ())
    detail = select_detail(facts, modules, mentions, template_text)

    def render(detail: dict[str, int], max_examples: int) -> str:
        header = [
            f"# CODE FACTS for {DISTRIBUTION} {facts.version} (package `{PACKAGE}`).",
            "# Extracted mechanically from the installed source — authoritative over",
            "# anything you remember about older versions of this library.",
            "# Notation: Python stub syntax. `# calls:` = public functions it reaches;",
            "# `# kwarg/JSON alias:` = alternative keyword name for a pydantic field.",
            "",
        ]
        body = _render_imports(facts, {qn.rsplit(".", 1)[-1] for qn, lvl in detail.items()
                                       if lvl >= BRIEF and facts.objects[qn].parent is not None
                                       and facts.objects[qn].parent.is_module}) + [""]
        module_order: list[str] = []
        for qn in detail:
            mod = qn
            while mod and not (facts.objects.get(mod) is not None and facts.objects[mod].is_module):
                mod = mod.rsplit(".", 1)[0] if "." in mod else ""
            if mod not in module_order:
                module_order.append(mod)
        mapped = [x.removeprefix(PACKAGE).lstrip(".") for x in modules]
        for mod in sorted(module_order, key=lambda m: (m not in mapped, m)):
            section = _render_module_section(facts, mod, detail)
            if section:
                body.extend(section + [""])
        ex = []
        if max_examples:
            ex.append("# ---- usage examples, verbatim from the library's README/docstrings ----")
            for _, title, code in _rank_examples(facts, mentions)[:max_examples]:
                ex.append(f"# from {title}:")
                ex.append(code)
                ex.append("")
        return "\n".join(header + body + ex).rstrip() + "\n"

    # Degrade until it fits, cheapest losses first.
    def demote(pred, to):
        return {q: (to if pred(q, lvl) else lvl) for q, lvl in detail.items()}

    max_examples = 6
    text = render(detail, max_examples)
    steps = [
        ("fewer examples", lambda: (detail, 3)),
        ("unmentioned methods -> names", lambda: (demote(
            lambda q, lvl: lvl == BRIEF and facts.objects[q].is_function, NAME), max_examples)),
        ("one example", lambda: (detail, 1)),
        ("drop name-only functions", lambda: ({q: lvl for q, lvl in detail.items()
                                               if lvl > NAME or facts.objects[q].is_class},
                                              max_examples)),
        ("classes -> summaries", lambda: (demote(
            lambda q, lvl: lvl == FULL and facts.objects[q].is_class, BRIEF), max_examples)),
        ("no examples", lambda: (detail, 0)),
    ]
    for _label, step in steps:
        if estimate_tokens(text) <= token_budget:
            break
        detail, max_examples = step()
        text = render(detail, max_examples)
    return text


# ============================================================================
# Helpers for synthesize_docs.py
# ============================================================================


def modules_for_ref_docs(ref_docs: list[str], docs_dir: str) -> list[str]:
    """Map docs/operations/<page>.md names to the module(s) their
    `::: module.path` mkdocstrings directives render, so the mapping in
    synthesize_docs.py stays the single source of truth."""
    modules = []
    for doc in ref_docs:
        path = os.path.join(docs_dir, doc)
        try:
            text = open(path, encoding="utf-8").read()
        except FileNotFoundError:
            continue
        modules.extend(re.findall(r"^:::\s*([\w.]+)", text, re.M))
    return modules


_FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})\s*([\w+-]*)")


def python_code_blocks(markdown: str) -> list[str]:
    """Contents of fenced code blocks tagged python/py (or untagged), found
    by pairing each opening fence with its *own* closing fence. A single
    non-greedy ```...``` regex pairs one block's closing fence with the next
    block's opening fence and so scans the prose in between as code."""
    blocks, lines = [], markdown.splitlines()
    i = 0
    while i < len(lines):
        m = _FENCE_RE.match(lines[i])
        if not m:
            i += 1
            continue
        indent, fence, lang = m.group(1), m.group(2), m.group(3).lower()
        body, i = [], i + 1
        while i < len(lines):
            close = _FENCE_RE.match(lines[i])
            if close and close.group(2).startswith(fence[0] * len(fence)) and not close.group(3):
                break
            body.append(lines[i][len(indent):] if lines[i].startswith(indent) else lines[i])
            i += 1
        i += 1
        if lang in ("", "python", "py", "python3"):
            blocks.append("\n".join(body))
    return blocks


def check_code_against_facts(markdown: str, facts: Facts) -> list[str]:
    """Static checks on generated Python code blocks:
      * every `from cascade_cms... import X` / `import cascade_cms...` resolves
      * every `<x>.operations.<op>(` is a real Operations method, and every
        method chained after it (`.then()`, `.edit()`, ...) is a real chain
        method
      * keyword arguments passed to a known library callable exist on it
    Returns human-readable error strings (empty = OK)."""
    errors: list[str] = []
    operations_cls = next((facts.objects[q] for q in facts.by_name.get("Operations", ())
                           if facts.objects[q].is_class), None)
    op_methods = set(operations_cls.members) if operations_cls else set()
    # Methods callable on what an operation returns (OperationChain, or a
    # ChainGroup that forwards to it).
    chain_methods: set[str] = set()
    for cls_name in ("OperationChain", "ChainGroup"):
        for q in facts.by_name.get(cls_name, ()):
            if facts.objects[q].is_class:
                chain_methods |= {m for m, o in facts.objects[q].members.items()
                                  if not m.startswith("_") and not o.is_alias and o.is_function}

    def rooted_at_operations(expr: ast.AST) -> bool:
        """True for `<x>.operations.<op>(...)` and any chain built on it."""
        while isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute):
            if isinstance(expr.func.value, ast.Attribute) and expr.func.value.attr == "operations":
                return True
            expr = expr.func.value
        return False

    lib_callables = {n for n, qns in facts.by_name.items()
                     if any(facts.objects[q].is_function or facts.objects[q].is_class for q in qns)}

    for block in python_code_blocks(markdown):
        try:
            tree = ast.parse(block)
        except SyntaxError:
            # Signature listings, `...` elisions and REPL transcripts are
            # legitimate in docs; they just can't be checked statically.
            continue
        local_defs = {n.name for n in ast.walk(tree)
                      if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and \
                    node.module.split(".")[0] == PACKAGE:
                if node.module not in facts.modules:
                    errors.append(f"Import from non-existent module `{node.module}`")
                    continue
                for alias in node.names:
                    if alias.name == "*":
                        continue
                    valid = facts.import_paths.get(alias.name, set())
                    is_submodule = f"{node.module}.{alias.name}" in facts.modules
                    if node.module not in valid and not is_submodule:
                        where = ", ".join(sorted(valid)) or "nowhere in the package"
                        errors.append(f"`from {node.module} import {alias.name}` is invalid "
                                      f"({alias.name} is importable from: {where})")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] == PACKAGE and alias.name not in facts.modules:
                        errors.append(f"`import {alias.name}` — no such module")
            elif isinstance(node, ast.Call):
                func = node.func
                # <anything>.operations.<op>(...)
                if (isinstance(func, ast.Attribute) and isinstance(func.value, ast.Attribute)
                        and func.value.attr == "operations" and op_methods
                        and func.attr not in op_methods):
                    errors.append(f"`operations.{func.attr}()` does not exist "
                                  f"(Operations has no method {func.attr!r})")
                # <anything>.operations.<op>(...).<method>(...)
                elif (isinstance(func, ast.Attribute) and chain_methods
                        and rooted_at_operations(func.value)
                        and func.attr not in chain_methods):
                    errors.append(f"`.{func.attr}()` cannot be chained onto an operation "
                                  f"(operation chains have: {', '.join(sorted(chain_methods))})")
                name = func.id if isinstance(func, ast.Name) else (
                    func.attr if isinstance(func, ast.Attribute) else None)
                if not name or name in local_defs or name not in lib_callables:
                    continue
                accepted = facts.params_of(name)
                if accepted is None:
                    continue
                for kw in node.keywords:
                    if kw.arg and kw.arg not in accepted:
                        errors.append(f"`{name}(..., {kw.arg}=...)` — {name} has no "
                                      f"parameter/field {kw.arg!r} "
                                      f"(accepts: {', '.join(sorted(accepted)) or 'none'})")
    # de-duplicate, keep order
    return list(dict.fromkeys(errors))


# ============================================================================
# CLI preview
# ============================================================================


def main(argv: list[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("template", help="template markdown file to build a digest for")
    ap.add_argument("--module", action="append", default=[],
                    help="extra reference module(s), e.g. cascade_cms.wrapper")
    ap.add_argument("--budget", type=int, default=DEFAULT_TOKEN_BUDGET)
    args = ap.parse_args(argv)
    facts = extract()
    text = build_digest(facts, args.module, open(args.template, encoding="utf-8").read(), args.budget)
    print(text)
    print(f"# ~{estimate_tokens(text)} tokens", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
