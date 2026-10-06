# Main Patterns

Common usage patterns for `cascade-cms-rest` 3.9.1.

```python
from cascade_cms.wrapper import Cascade, EnvironmentVars
from cascade_cms.cmstypes import Asset

env: EnvironmentVars = {
    "SERVER": "my-site",
    "API_KEY": "your-api-key",
    "CASCADE_URL": "https://your-cascade-instance.com",
}
```

---

## Read a single asset

```python
with Cascade(env) as cascade:
    results = cascade.operations.read("abc123").submit_requests(Asset)

if results.success:
    asset = results.success[0]
    print(asset.path)
    print(asset.siteName)
```

---

## Edit and save

Use a callback that receives the current asset and returns the modified one:

```python
def update_metadata(asset: Asset) -> Asset:
    asset.keywords = "cascade, cms, updated"
    asset.metaDescription = "Updated via py-cascade-cms"
    return asset

with Cascade(env) as cascade:
    results = (
        cascade.operations
        .read("abc123")
        .edit(update_metadata)
        .submit_requests(Asset)
    )

if results.failed:
    for failure in results.failed:
        print(f"[{failure.category}] {failure.step_name}: {failure.message}")
```

The callback receives the asset after `.read()` completes. The identifier
is derived from the asset's own `id`/`path`/`siteName` fields — no separate
argument on `edit()`.

---

## Publish

Chain `.publish()` after editing to write and publish in one batch:

```python
with Cascade(env) as cascade:
    results = (
        cascade.operations
        .read("abc123")
        .edit(update_metadata)
        .publish("abc123")
        .submit_requests(Asset)
    )
```

Or publish without editing:

```python
with Cascade(env) as cascade:
    results = cascade.operations.publish("abc123").submit_requests(Asset)
```

---

## Search

```python
from cascade_cms.cmstypes import SearchInformation, ListElements

payload = SearchInformation(
    searchTerms="annual report",
    siteName="site123",
)

with Cascade(env) as cascade:
    results = (
        cascade.operations
        .search(payload)
        .submit_requests(ListElements)
    )

if results.success:
    for item in results.success:
        print(item)
```

`SearchInformation` is the typed payload; `ListElements` is the return type
from `.search()`. Both are in `cascade_cms.cmstypes`.

---

## Bulk operations

Pass a list of identifiers. Each gets its own independent chain — failures
in one do not cancel others:

```python
asset_ids = ["id1", "id2", "id3"]

def tag_asset(asset: Asset) -> Asset:
    asset.tags = [{"name": "bulk-update"}]
    return asset

with Cascade(env) as cascade:
    results = (
        cascade.operations
        .read(asset_ids)
        .edit(tag_asset)
        .publish(asset_ids)
        .submit_requests(Asset)
    )

print(f"{len(results.success)} updated, {len(results.failed)} failed")

for failure in results.failed:
    print(f"  {failure.identifier}: [{failure.category}] {failure.message}")
```

---

## Handling failures by category

`ChainFailure.category` holds the `FailureCategory` value — use it directly:

```python
from cascade_cms.utils.failures import FailureCategory

with Cascade(env, exit_on_failure=False) as cascade:
    results = cascade.operations.read(asset_ids).submit_requests(Asset)

network_errors = []
cascade_errors = []

for failure in results.failed:
    if failure.category == FailureCategory.NETWORK:
        network_errors.append(failure.identifier)
    elif failure.category == FailureCategory.CASCADE:
        cascade_errors.append(failure.identifier)

if network_errors:
    print(f"Network failures (retry candidates): {network_errors}")
if cascade_errors:
    print(f"Cascade errors (check identifiers): {cascade_errors}")
```

`exit_on_failure=False` keeps the process alive to inspect failures
programmatically.

---

## Script logging

```python
from cascade_cms.utils import script_log

with Cascade(env) as cascade:
    script_log.note("Starting bulk keyword update")

    results = (
        cascade.operations
        .read(asset_ids)
        .edit(tag_asset)
        .submit_requests(Asset)
    )

    script_log.note(f"Complete: {len(results.success)} updated")
```

`script_log.note()` only works inside the `with` block.

<!-- synthesized-for: 3.9.1 -->
