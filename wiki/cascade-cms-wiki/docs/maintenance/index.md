---
layout: default
title: Maintenance
nav_order: 8
---

# Maintenance

This section documents `docs-drift.yml`, the automated GitHub Actions workflow that keeps [All Operations](../operations/all-operations.md) in sync with method signature changes in `py-cascade-cms`, plus the update steps that still fall outside its scope.

**Status: Implemented.**

---

## `docs-drift.yml`

`docs-drift.yml` lives in the `py-cascade-cms` repository and runs after CI passes on `master` (a `workflow_run` trigger — not a schedule, not `workflow_dispatch`, and not tied to any Cascade CMS API version check). For each run, it:

1. Checks out `py-cascade-cms` at the commit CI just verified, and this wiki repository, side by side.
2. Diffs `src/cascade_cms/operations.py` and `src/cascade_cms/cmstypes.py` between `HEAD~1` and `HEAD` using Python's `ast` module — comparing argument names, defaults, and type annotations for functions, and field types/defaults for payload and response model classes.
3. Uses `doc_mapping.yml` (in the `py-cascade-cms` repo root) to map each `Operations` method to its heading in `all-operations.md` and, where relevant, the `cmstypes.py` payload model it consumes.
4. For any mapped method whose signature or payload model changed, asks Gemini (`gemini-3.5-flash-lite`) to rewrite just that section of `all-operations.md` — matching the existing style — and draft one `CHANGELOG.md` line.
5. Opens a PR against this repository (labeled `docs-drift, automated`) with the drafted changes, for human review before merge. No PR opens if nothing drifted.

**What it does *not* do:**

- **No docstring or logic diffing.** Only the AST-visible signature (args, defaults, annotations) and payload model fields are compared — a docstring edit or a behavior change that doesn't touch the signature produces no drift and no PR.
- **No retroactive checking.** It only diffs `HEAD~1` against `HEAD`, so it catches drift introduced by the *latest* commit — not gaps that already existed before `docs-drift.yml` was added, and not older commits it never ran against.
- **No Cascade REST API version detection**, and no `.skill/` regeneration — neither is implemented. See [SKILL File](#skill-file) below.

> Pre-existing staleness (gaps that predate `docs-drift.yml`) must still be fixed manually — the workflow only prevents *new* signature drift from going undocumented.

---

## Manual steps

`docs-drift.yml` narrows the manual-update surface but doesn't eliminate it:

1. Review the [Cascade CMS REST API changelog](https://www.hannonhill.com/cascadecms/latest/developing-in-cascade/rest-api/index.html) for new or changed endpoints
2. Update operation signatures in `operations.py` and/or payload/response models in `cmstypes.py` — once this lands on `master` and CI passes, `docs-drift.yml` drafts the matching `all-operations.md` section and a `CHANGELOG.md` line automatically
3. For a brand-new operation, add an entry to `doc_mapping.yml` (methods not listed there are invisible to drift detection) and write its initial doc section and examples by hand
4. Update the SKILL file snapshot in `.skill/` — not automated, see below
5. Increment the version in `pyproject.toml`
6. Review and merge the `docs-drift` PR, if one was opened, alongside your own changes
7. Run tests and publish

---

## SKILL File

The SKILL file at `.skill/` in the [source repository](https://github.com/<your-org>/<your-repo>) enables AI-assisted script generation for this library. It is a snapshot of the library's source files bundled with a generation spec and prompt.

`docs-drift.yml` does not touch `.skill/` — there is no workflow that regenerates it. When the library changes, update the SKILL file by hand alongside the change.

See the repository README for instructions on using the SKILL file with supported AI coding assistants.
