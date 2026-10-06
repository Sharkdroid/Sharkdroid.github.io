# Core Concepts

## The `Cascade` class

`Cascade` is the single entry point for all library interactions. Open a
session with it as a [context manager](https://docs.python.org/3/reference/datamodel.html#context-managers):

```python
from cascade_cms.wrapper import Cascade, EnvironmentVars

env: EnvironmentVars = {
    "SERVER": "my-site",
    "API_KEY": "your-api-key",
    "CASCADE_URL": "https://your-cascade-instance.com",
}

with Cascade(env) as cascade:
    # queue operations here
    ...
```

Previously known as `CascadeWrapperBase`; the alias still works but `Cascade`
is the current name.

### Constructor

```python
Cascade(
    environmentVariables: EnvironmentVars,
    debug: dict[str, Any] | None = None,
    *,
    exit_on_failure: bool = True,
    log_dir: str | os.PathLike | None = None,
)
```

`EnvironmentVars` is a `TypedDict` with three required keys:

| Key | Description |
|---|---|
| `SERVER` | Label used in log output (not a network address) |
| `API_KEY` | Cascade REST API bearer token |
| `CASCADE_URL` | Base URL of your Cascade CMS instance |

`exit_on_failure=True` (default) ends the script non-zero on any failure.
Pass `False` for long-lived processes like the MCP server.

---

## Operations

`cascade.operations` is the entry point for all CMS operations. It returns
an `Operations` builder that accepts the first call in a chain:

```python
with Cascade(env) as cascade:
    chain = cascade.operations.read("abc123")
```

Available operations mirror the Cascade REST API:

| Operation | Description |
|---|---|
| `.read(id)` | Read one asset |
| `.edit(payload)` | Edit an asset via callback or direct payload |
| `.publish(id)` | Publish an asset |
| `.delete(id)` | Delete an asset |
| `.copy(id, dest)` | Copy an asset |
| `.move(id, dest)` | Move an asset |
| `.checkIn(id)` | Check in an asset |
| `.checkOut(id)` | Check out an asset |
| `.search(query)` | Search assets |
| `.create(asset)` | Create a new asset |

See the [API Reference](../operations/operations.md) for full signatures.

---

## Operation chains

Each operation call returns an `OperationChain`, not a result. Nothing
executes until you call `.submit_requests()`. This design lets you compose
multi-step workflows before any network requests are made:

```python
from cascade_cms.cmstypes import Asset

def set_searchable(asset: Asset) -> Asset:
    asset.searchable = True
    return asset

with Cascade(env) as cascade:
    results = (
        cascade.operations
        .read("abc123")
        .edit(set_searchable)
        .publish("abc123")
        .submit_requests(Asset)
    )
```

The type argument to `.submit_requests()` is for the type checker. `Asset`
covers most cases; use a more specific type when the operation returns one.

---

## `edit()` and callbacks

`edit()` accepts a callable, a single asset, or a list of assets. The
callable form is the most common in practice:

```python
def update_keywords(asset: Asset) -> Asset:
    asset.keywords = "updated"
    return asset

cascade.operations.edit(update_keywords)
```

The callback receives the current asset and must return the modified asset.
The identifier is derived from the asset's own `id`/`path`/`siteName` fields
— there is no separate identifier argument on `edit()` in 3.9.1.

---

## Batch execution and `ChainGroup`

Passing a list to operations that accept identifiers — `read`, `delete`,
`publish`, etc. — creates one independent `OperationChain` per identifier,
returned as a `ChainGroup`:

```python
with Cascade(env) as cascade:
    results = (
        cascade.operations
        .read(["id1", "id2", "id3"])
        .submit_requests(Asset)
    )
```

Failures in one chain do not cancel others. The returned `ChainResults`
covers all chains in the group.

---

## Result handling

`.submit_requests()` returns `ChainResults[T]` — a list subclass with
`.success` and `.failed` properties. See [Result Handling](../getting-started/result-handling.md)
for full details.

```python
results = cascade.operations.read("abc123").submit_requests(Asset)

for asset in results.success:
    print(asset.path)

for failure in results.failed:
    print(f"[{failure.category}] {failure.message}")
```

---

## Script logging

`script_log.note()` writes annotated log lines from within a script:

```python
from cascade_cms.utils import script_log

with Cascade(env) as cascade:
    script_log.note("Starting run")
    results = cascade.operations.read("abc123").submit_requests(Asset)
    script_log.note(f"Done — {len(results.success)} succeeded")
```

Calls outside the `with` block drop silently with a `RuntimeWarning`.
API keys are automatically redacted from log output.

---

## Identifiers

The `utils.identifiers` module (added in 3.8.3) coerces raw Cascade
identifier dicts to `IdentifierType`:

```python
from cascade_cms.utils.identifiers import to_identifier, to_identifiers

identifier = to_identifier({"id": "abc123", "type": "page", "path": None})
identifiers = to_identifiers([{"id": "a"}, {"id": "b"}])
```

Use these when processing raw API responses before passing identifiers to
operations.

<!-- synthesized-for: 3.9.1 -->
