# Library Maintenance

Development and release workflow for `cascade-cms-rest`. This page
summarizes [`AGENTS.md`](https://github.com/Sharkdroid/py-cascade-cms/blob/master/AGENTS.md)
and [`PUBLISHING.md`](https://github.com/Sharkdroid/py-cascade-cms/blob/master/PUBLISHING.md)
in the library repository.

---

## Environment setup

```bash
git clone https://github.com/Sharkdroid/py-cascade-cms
cd py-cascade-cms

conda create -y -p ./.conda python=3.13
./.conda/bin/pip install -e ".[dev]"
```

Or use `.venv` — either works. The conda environment at `./.conda` is the
convention the AGENTS.md assumes.

---

## Before committing

All three must pass before any commit or PR:

```bash
ruff check .      # lint
mypy src/         # type check
pytest            # tests
```

GitHub Actions runs the same checks on push. A tag push that fails CI
cancels the PyPI publish.

---

## Releasing

### 1. Bump version

Edit `pyproject.toml`:

```toml
[project]
version = "3.10.0"
```

### 2. Update CHANGELOG.md

Add a section at the top:

```markdown
## [3.10.0] - 2026-10-05

### Added
- ...

### Changed
- ...

### Fixed
- ...

### Files Changed
- src/cascade_cms/wrapper.py
- src/cascade_cms/operations.py
```

The `Files Changed` line at the bottom of each section is required — it is
used by the drift detection workflow.

### 3. Commit, tag, push

```bash
git commit -m "Bump version to 3.10.0"
git tag -a v3.10.0 -m "Release 3.10.0"
git push origin master
git push origin v3.10.0
```

The tag push triggers `.github/workflows/release.yml`, which runs CI and
publishes to [PyPI: cascade-cms-rest](https://pypi.org/project/cascade-cms-rest/).

**Do not run `twine upload` by hand.**

### 4. Verify

```bash
pip index versions cascade-cms-rest
```

Or check [pypi.org/project/cascade-cms-rest](https://pypi.org/project/cascade-cms-rest/).

---

## Dependency note

`cascade-cms-tools` depends on the **published** package, not a local copy.
Changes to this library are not picked up by the tools until a version is
tagged and PyPI shows the new release. After releasing, the tools maintainer
must update and rebuild the skill bundle.

---

## Backwards compatibility

Within a `MAJOR` version, prefer deprecation over removal:

```python
import warnings

def old_method(self, x):
    warnings.warn(
        "old_method is deprecated, use new_method instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return self.new_method(x)
```

When renaming a public symbol, keep the old name as an alias exported from
`__init__.py`. Example: `CascadeWrapperBase` remains as an alias for
`Cascade`.

---

## Workflow for code agents

When Claude Code or another agent is modifying this repository:

1. Run the full test suite before committing: `ruff check .`, `mypy src/`,
   `pytest`
2. Update `CHANGELOG.md` with your changes and a `Files Changed` section
3. Do not bump the version unless explicitly asked
4. Keep backwards compatibility — deprecate instead of removing
5. Write tests for new features in `tests/`

Refer to [`AGENTS.md`](https://github.com/Sharkdroid/py-cascade-cms/blob/master/AGENTS.md)
for the complete developer command reference.
