"""Tests for scripts/code_facts.py against the installed cascade-cms-rest.

Run from the repo root (needs the wiki requirements + litellm installed):

    pip install -r wiki/cascade-cms-wiki/requirements.txt litellm beautifulsoup4 pytest
    python -m pytest scripts/tests
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import code_facts as cf  # noqa: E402

REPO = os.path.join(os.path.dirname(__file__), "..", "..")
TEMPLATES = os.path.join(REPO, "wiki-templates")
STUBS = os.path.join(REPO, "wiki", "cascade-cms-wiki", "docs", "operations")


@pytest.fixture(scope="module")
def facts():
    return cf.extract()


def test_version_comes_from_installed_distribution(facts):
    import importlib.metadata
    assert facts.version == importlib.metadata.version(cf.DISTRIBUTION)


def test_aliases_and_import_paths(facts):
    assert facts.aliases.get("CascadeWrapperBase") == "Cascade"
    assert "cascade_cms" in facts.import_paths["Cascade"]
    assert facts.canonical["Cascade"] == "cascade_cms.wrapper"


def test_modules_for_ref_docs_reads_mkdocstrings_directives():
    mods = cf.modules_for_ref_docs(["wrapper.md", "operation_logger.md"], STUBS)
    assert mods == ["cascade_cms.wrapper", "cascade_cms.utils.operation_logger"]


def test_digest_fits_budget_and_names_the_real_api(facts):
    template = open(os.path.join(TEMPLATES, "advanced-cpu-intensive.md")).read()
    digest = cf.build_digest(facts, ["cascade_cms.wrapper", "cascade_cms.operations"],
                             template, token_budget=cf.DEFAULT_TOKEN_BUDGET)
    assert cf.estimate_tokens(digest) <= cf.DEFAULT_TOKEN_BUDGET
    assert digest.startswith("# CODE FACTS")
    # executor is configured on submit_requests — the fact the page needs
    assert "def submit_requests(" in digest and "executor: Executor | None" in digest
    assert "CascadeWrapperBase is an alias of Cascade" in digest
    assert "MAX_REQUESTS = 50" in digest


def test_tight_budget_degrades_instead_of_overflowing(facts):
    template = open(os.path.join(TEMPLATES, "core-concepts-index.md")).read()
    full = cf.build_digest(facts, ["cascade_cms.operations", "cascade_cms.cmstypes"], template, 50_000)
    small = cf.build_digest(facts, ["cascade_cms.operations", "cascade_cms.cmstypes"], template, 3000)
    assert len(small) < len(full)


def test_pydantic_field_aliases_are_rendered_compactly(facts):
    template = "Use `deleteParameters` with `delete`."
    digest = cf.build_digest(facts, ["cascade_cms.cmstypes"], template)
    assert "do_workflow: bool  # kwarg/JSON alias: doWorkflow" in digest
    assert "Field(" not in digest.split("class deleteParameters", 1)[1].split("class ", 1)[0]


def test_python_code_blocks_pairs_fences_correctly():
    md = "```python\na = 1\n```\n\nprose with `x.y` and — dashes\n\n```bash\nls\n```\n\n```\nb = 2\n```\n"
    assert cf.python_code_blocks(md) == ["a = 1", "b = 2"]


def test_check_flags_stale_imports_and_bad_calls(facts):
    md = (
        "```python\n"
        "from cascade_cms.utils.identifiers import to_identifiers\n"
        "from cascade_cms.wrapper import CascadeWrapperBase\n"
        "from cascade_cms.cmstypes import deleteParameters\n"
        "with Cascade(env, exit_on_failur=False) as cascade:\n"
        "    cascade.operations.fetch(x)\n"
        "    cascade.operations.delete(x, deleteParameters(doWorkflow=False, unpublish=True))\n"
        "```\n"
    )
    errors = cf.check_code_against_facts(md, facts)
    text = "\n".join(errors)
    assert "cascade_cms.utils.identifiers" in text
    assert "CascadeWrapperBase" in text           # alias only exported from the package root
    assert "exit_on_failur" in text
    assert "operations.fetch()" in text
    assert "doWorkflow" not in text               # alias kwarg is valid (populate_by_name)
    assert len(errors) == 4


def test_check_accepts_readme_examples(facts):
    md = "\n".join(f"```python\n{code}\n```" for title, code in facts.examples if title.startswith("README"))
    assert cf.check_code_against_facts(md, facts) == []


def test_check_flags_methods_chained_onto_operations_that_dont_exist(facts):
    md = (
        "```python\n"
        "cascade.operations.read(ident).then(cb).edit(cb).submit_requests(Asset)\n"
        "results = cascade.submit_requests(Asset)\n"
        "```\n"
    )
    errors = cf.check_code_against_facts(md, facts)
    assert len(errors) == 1 and "`.submit_requests()` cannot be chained" in errors[0]


def test_templates_have_purpose_and_resolvable_focus(facts):
    import glob
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    pytest.importorskip("litellm")
    import synthesize_docs as sd
    for path in sorted(glob.glob(os.path.join(TEMPLATES, "*.md"))):
        body, purpose, focus = sd.parse_template(open(path).read())
        assert purpose, f"{path} has no purpose comment"
        assert "<!--" not in body, f"{path} metadata not stripped"
        assert "[PLACEHOLDER:" in body
        assert cf.unresolved_names(facts, focus) == [], path
        # Fixed (non-placeholder) code in a template must be valid against the API.
        assert cf.check_code_against_facts(body, facts) == [], path
