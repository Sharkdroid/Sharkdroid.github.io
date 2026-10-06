# Getting Started

`cascade-cms-rest` is a typed async Python REST client for
[Hannon Hill Cascade CMS](https://www.hannonhill.com/products/cascade-cms/).
It wraps the Cascade REST API in a context-manager entry point with
chainable operations, batch execution, and structured failure handling.

Install from PyPI:

```bash
pip install cascade-cms-rest
```

---

## Your first script

Import the `Cascade` context manager and a CMS type, then supply your
instance credentials:

```python
from cascade_cms.wrapper import Cascade, EnvironmentVars
from cascade_cms.cmstypes import Asset

env: EnvironmentVars = {
    "SERVER": "my-site",
    "API_KEY": "your-api-key",
    "CASCADE_URL": "https://your-cascade-instance.com",
}
```

`EnvironmentVars` is a `TypedDict` — all three keys are required. `SERVER`
is a label used in log output, not a network address.

Open a session with the context manager:

```python
with Cascade(env) as cascade:
    results = cascade.operations.read("abc123").submit_requests(Asset)

for asset in results.success:
    print(asset.path)
```

The `with` block manages the session lifecycle. Operations queued inside the
block are submitted as a batch when you call `.submit_requests()`. See
[Python context managers](https://docs.python.org/3/reference/datamodel.html#context-managers)
for background.

---

## Operation chains

The library's primary pattern chains multiple operations on the same asset:

```python
from cascade_cms.wrapper import Cascade
from cascade_cms.cmstypes import Asset

def update_keywords(asset: Asset) -> Asset:
    asset.keywords = "cms, cascade, updated"
    return asset

with Cascade(env) as cascade:
    results = (
        cascade.operations
        .read("abc123")
        .edit(update_keywords)
        .publish("abc123")
        .submit_requests(Asset)
    )
```

Each call to `.read()`, `.edit()`, `.publish()`, etc. returns an
`OperationChain` — nothing executes until `.submit_requests()`. This lets you
describe the full workflow before any network requests are made.

---

## What happens on failure

If any operation in the chain fails, the failure is recorded on the returned
`ChainResults` and the remaining steps in that chain are skipped. Other
chains in the batch are unaffected.

```python
with Cascade(env) as cascade:
    results = cascade.operations.read("abc123").submit_requests(Asset)

if results.failed:
    for failure in results.failed:
        print(f"[{failure.category}] {failure.message}")
```

See [Result Handling](./result-handling.md) for full details on `.success`,
`.failed`, and failure classification.

---

## Bulk operations

Pass a list of identifiers to run the same chain across multiple assets:

```python
asset_ids = ["id1", "id2", "id3"]

with Cascade(env) as cascade:
    results = (
        cascade.operations
        .read(asset_ids)
        .submit_requests(Asset)
    )

print(f"{len(results.success)} succeeded, {len(results.failed)} failed")
```

The library creates one independent chain per identifier. Failures in one
chain do not cancel others.

---

## Further reading

- [Result Handling](./result-handling.md) — `.success`, `.failed`, `classify_failure`
- [Version History](./version-history.md) — changes from older versions
- [Core Concepts](../core-concepts/index.md) — `Cascade` class, `EnvironmentVars`, operations
- [Examples](../examples/main-patterns.md) — read, edit, publish, search, bulk patterns
