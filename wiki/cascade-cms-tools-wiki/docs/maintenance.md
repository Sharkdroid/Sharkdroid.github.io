# Maintenance

Development and release workflow for `cascade-cms-tools`. This page
summarizes [`AGENTS.md`](https://github.com/Sharkdroid/cascade-cms-tools/blob/main/AGENTS.md)
in the tools repository.

---

## Environment setup

```bash
git clone https://github.com/Sharkdroid/cascade-cms-tools
cd cascade-cms-tools

conda create -y -p ./.conda python=3.13
./.conda/bin/pip install --upgrade cascade-cms-rest ruff
./.conda/bin/pip install -e "./mcp[dev]"
```

---

## Before committing

```bash
ruff check .
mypy mcp/src/
pytest
```

All three must pass. GitHub Actions runs the same checks on push.

---

## MCP server

### Local development

```bash
./.conda/bin/pip install -e "./mcp[dev]"
./.conda/bin/cascade-cms-rest-mcp
```

The server reads `CASCADE_API_KEY` and `CASCADE_URL` from environment
variables and listens on stdio.

### Publishing

The MCP server publishes to PyPI as `cascade-cms-rest-mcp`. Version lives
in `mcp/pyproject.toml`.

```bash
# Bump version in mcp/pyproject.toml, then:
git tag v<X.Y.Z>
git push origin v<X.Y.Z>
```

GitHub Actions publishes automatically on tag push. Do not run `twine upload`
by hand.

---

## Claude Code skill

### Building the skill bundle

```bash
./.conda/bin/python build_release.py
```

This syncs the bundled library source from the installed `cascade-cms-rest`
package and validates all templates. The output is
`dist/cascade-cms-tools-skill-<version>.zip`.

If any template fails validation, rewrite it by hand to match the current
library API before re-running.

### Validating a script

```bash
python skill/cascade-script-writer/scripts/validate_script.py my_script.py
```

A script is ready when the validator exits 0. Format first:

```bash
./.conda/bin/ruff format --line-length 60 --isolated my_script.py
```

The 60-character line limit is a hard requirement enforced by the validator.

### Publishing the skill

Tag and push using the same tag as the MCP server version. GitHub Actions
publishes the MCP server to PyPI and the skill zip to GitHub Releases.

---

## Keeping in sync with cascade-cms-rest

When the library releases a new version:

```bash
./.conda/bin/pip install --upgrade cascade-cms-rest
./.conda/bin/python build_release.py
```

If `build_release.py` reports template validation failures, the affected
templates must be rewritten by hand before releasing.

Update the "Currently built against" line in `README.md` after upgrading.

---

## Library integration note

Both tools depend on the **published** `cascade-cms-rest` package. They do
not pick up local library changes. The library must be tagged and published
to PyPI before the tools can be updated against it.

See [py-cascade-cms — Library Maintenance](https://sharkdroid.github.io/wiki/cascade-cms-wiki/ai/library-maintenance/)
for the library release workflow.

---

## Workflow for code agents

When Claude Code is working in this repository:

1. Run `ruff format --line-length 60 --isolated <file>` before validating
   any generated scripts
2. Run the full test suite before committing: `ruff check .`, `mypy mcp/src/`,
   `pytest`
3. Rebuild the skill bundle after any template changes: `python build_release.py`
4. Validate all templates before considering the work done
5. Update `AGENTS.md` if the workflow changes

Refer to [`AGENTS.md`](https://github.com/Sharkdroid/cascade-cms-tools/blob/main/AGENTS.md)
for the complete command reference.
