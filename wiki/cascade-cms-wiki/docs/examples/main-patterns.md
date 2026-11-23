# Main Patterns

These are common recipes for this version of the library using the `cascade-cms-rest` package:

```python
from cascade_cms.cmstypes import Asset, IdentifierType, Path, SearchInformation
from cascade_cms.wrapper import Cascade

environment_variables = {
    "API_KEY": "your-api-key",
    "CASCADE_URL": "https://cascade.example.com/api/v1",
    "SERVER": "prod",
}

identifier = IdentifierType(identifier="e868f539ac1001062cfa029c4c5df4d0", asset_type="folder")
page_identifier = IdentifierType(identifier="12345678ac1001062cfa029c4c5df4d0", asset_type="page")
path_target = Path(path="/_folder/index", asset_type="page")
```

---

## Read a single asset

```python
with Cascade(environment_variables) as cascade:
    cascade.operations.read(identifier)
    results = cascade.submit_requests(Asset)

for asset in results.success:
    print(asset.internal_type)
```

A read operation retrieves a dynamic asset wrapper containing the inner asset data. Submitting with an expected `Asset` result type parses the returned JSON into an `Asset` instance.

---

## Edit and save

```python
def rewrite(asset):
    return asset

with Cascade(environment_variables) as cascade:
    cascade.operations.read(page_identifier).then(rewrite).edit(rewrite)
    results = cascade.submit_requests()

for failure in results.failed:
    print(f"Failed at step {failure.step}: {failure.message}")
```

The edit operation saves modified assets, using each asset's own id, path, and site fields to build its per-request identifier. If any chain fails, inspect the `.failed` collection on the `ChainResults` object.

---

## Publish

```python
with Cascade(environment_variables) as cascade:
    cascade.operations.read(page_identifier).edit(rewrite).publish(page_identifier)
    cascade.operations.publish(path_target)
    results = cascade.submit_requests()
```

Pass a `publishInformation` payload to the publish step when configuring unpublish options, or call publish directly on an identifier when no payload modifications are required.

---

## Search

```python
with Cascade(environment_variables) as cascade:
    payload = SearchInformation(site_name="default", search_terms="welcome")
    cascade.operations.search(payload)
    results = cascade.submit_requests()

for res in results.success:
    for element in res.elements:
        print(element)
```

The `SearchInformation` payload accepts parameters like `site_name`, `search_terms`, `search_fields`, and `search_types`, and operations return `ListElements` containing the matching elements.

---

## Bulk operations

```python
identifiers = [
    IdentifierType(identifier="11111111ac1001062cfa029c4c5df4d0", asset_type="page"),
    IdentifierType(identifier="22222222ac1001062cfa029c4c5df4d0", asset_type="page"),
]

with Cascade(environment_variables) as cascade:
    cascade.operations.read(identifiers).then(rewrite).edit(rewrite).publish(identifiers)
    results = cascade.submit_requests()

print(f"Success: {len(results.success)}, Failed: {len(results.failed)}")
for failure in results.failed:
    print(f"Chain {failure.chain_index} failed with {failure.category}: {failure.message}")
```

Passing a sequence of identifiers to an operation fans the call out into independent chains processed concurrently.

---

## Handling failures by category

```python
with Cascade(environment_variables, exit_on_failure=False) as cascade:
    cascade.operations.read(identifier)
    results = cascade.submit_requests(Asset)

for failure in results.failed:
    if failure.category == FailureCategory.CASCADE:
        print(f"CMS rejected request: {failure.message}")
    elif failure.category == FailureCategory.NETWORK:
        print(f"Network error: {failure.message}")
    elif failure.category == FailureCategory.LIBRARY:
        print(f"Library error: {failure.message}")
    elif failure.category == FailureCategory.CALLBACK:
        print(f"Callback exception: {failure.message}")
```

Passing `exit_on_failure=False` keeps long-lived processes like MCP servers alive, allowing you to inspect `FailureCategory` values (`CASCADE`, `NETWORK`, `LIBRARY`, `CALLBACK`) directly from the returned results.

---

## Script logging

```python
from cascade_cms.utils.extension import script_log

with Cascade(environment_variables) as cascade:
    script_log.log_note("Starting batch synchronization")
    cascade.operations.read(identifier)
    results = cascade.submit_requests(Asset)
    script_log.log_note("Batch synchronization complete")
```

The `script_log` helper instance can be called directly within script execution blocks to log custom notes and activities to the active log file.

<!-- synthesized-for: 3.10.1 -->
