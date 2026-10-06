<!-- handwritten — not tracked by docs automation. Update manually when
     breaking changes ship. Remove this file if it becomes stale and is
     no longer useful as an upgrade guide. -->

# Version History

A summary of breaking API changes across major versions, for users upgrading
from older installations.

For a complete changelog including non-breaking changes and bug fixes, see
[CHANGELOG.md](https://github.com/Sharkdroid/py-cascade-cms/blob/master/CHANGELOG.md)
in the library repository.

---

## 3.9.1 (current)

No breaking changes from 3.9.0.

---

## 3.8.2

**Breaking: `get_data_structure` path format changed.**

Dotted string paths are no longer accepted. Use tuple paths instead:

```python
# Old (pre-3.8.2) — broken
asset.get_data_structure("group.field")

# Current (3.8.2+)
asset.get_data_structure(("group", "field"))
```

---

## 3.8.0

**Breaking: result handling redesigned.**

`CascadeError` and `isinstance` result checks are gone. Use `.success` and
`.failed` on the returned `ChainResults`:

```python
# Old — broken
result = wrapper.read(id)
if isinstance(result, CascadeError):
    handle_error(result)

# Current
results = cascade.operations.read(id).submit_requests(Asset)
for failure in results.failed:
    handle_failure(failure)
```

**Breaking: `submit_requests()` now takes an explicit result type.**

```python
# Old — broken
results = cascade.submit_requests()

# Current
results = cascade.submit_requests(Asset)
```

---

## 3.7.0

**Breaking: `get_page_configuration` is now read-only.**

Attempting to write to a `PageConfiguration` object raises
`ReadOnlyPageConfigError`. Use asset-level operations for modifications
instead.

---

## 3.4.0

`utils.script_notes` module added. `script_log.note()` is now the
recommended way to write log lines from scripts:

```python
from cascade_cms.utils import script_log
script_log.note("Processing started")
```

---

## 3.3.0

**Breaking: response caching removed.**

The caching layer and its configuration keys no longer exist. Remove any
cache-related configuration from your scripts.

---

## 3.2.0

`failures` module added (`ChainResults`, `ChainFailure`, `FailureCategory`,
`classify_failure`). This is the version that introduced `.success` and
`.failed` as the result API.

---

## 3.0.0

**Breaking: class renamed.**

`CascadeWrapperBase` is still importable as an alias but the canonical name
is now `Cascade`:

```python
# Old — still works via alias
from cascade_cms.wrapper import CascadeWrapperBase

# Current — preferred
from cascade_cms.wrapper import Cascade
```

Update `__init__.py` exports narrowed: `cmstypes` symbols must be imported
from `cascade_cms.cmstypes` directly, not from the package root.
