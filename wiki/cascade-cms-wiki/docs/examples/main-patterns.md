# Main Patterns

Here are common recipes for everyday asset workflows using version 3.10.1 of the library, assuming the shared setup below:

```python
from cascade_cms.cmstypes import Asset, IdentifierType, Path, SearchInformation
from cascade_cms.wrapper import Cascade

environment_variables = {
    "API_KEY": "your-api-key",
    "CASCADE_URL": "https://cascade.example.com/api/v1",
    "SERVER": "prod",
}

identifier = IdentifierType(identifier="e868f539ac1001062cfa029c4c5df4d0", asset_type="folder")
page_identifier = IdentifierType(identifier="e868f539ac1001062cfa029c4c5df4d1", asset_type="page")
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

A read operation retrieves a dynamic wrapper around the raw asset payload, returning an `Asset` instance on success.

---

## Edit and save

```python
def update_asset(asset):
    return asset

with Cascade(environment_variables) as cascade:
    cascade.operations.read(page_identifier).edit(page_identifier, update_asset)
    results = cascade.submit_requests()

for failure in results.failed:
    print(failure.message)
```

The edit step automatically addresses the request using the asset's own identifier fields, writing back the transformed asset returned by the callback.

---

## Publish

```python
with Cascade(environment_variables) as cascade:
    cascade.operations.read(page_identifier).edit(page_identifier, update_asset).publish(page_identifier)
    cascade.operations.publish(page_identifier)
    results = cascade.submit_requests()
```

You pass a `publishInformation` payload only when specific options like unpublishing need customization; otherwise, calling `.publish()` without arguments defaults to standard publishing behavior.

---

## Search

```python
with Cascade(environment_variables) as cascade:
    search_payload = SearchInformation(
        siteName="default",
        searchTerms="news",
        searchFields=["title"],
        searchTypes=["page"]
    )
    cascade.operations.search(search_payload)
    results = cascade.submit_requests()

for match in results.success:
    for element in match.elements:
        print(element)
```

The `SearchInformation` payload is imported from `cascade_cms.cmstypes` and returns a `ListElements` container whose matches are stored in `elements`.

---

## Bulk operations

```python
identifiers = [
    IdentifierType(identifier="e868f539ac1001062cfa029c4c5df4d1", asset_type="page"),
    IdentifierType(identifier="e868f539ac1001062cfa029c4c5df4d2", asset_type="page"),
]

with Cascade(environment_variables) as cascade:
    cascade.operations.read(identifiers).edit(identifiers, update_asset).publish(identifiers)
    results = cascade.submit_requests()

print(f"Success: {len(results.success)}, Failed: {len(results.failed)}")
for failure in results.failed:
    print(f"Chain {failure.chain_index} failed at step {failure.step}: {failure.message}")
```

Passing a sequence of identifiers to an operation automatically fans out the work into independent chains that execute concurrently.

---

## Handling failures by category

```python
with Cascade(environment_variables, exit_on_failure=False) as cascade:
    cascade.operations.read(identifier)
    results = cascade.submit_requests(Asset)

for failure in results.failed:
    if failure.category == "CASCADE":
        print(f"API rejected request: {failure.message}")
    elif failure.category == "NETWORK":
        print(f"Network error: {failure.message}")
    elif failure.category == "LIBRARY":
        print(f"Library error: {failure.message}")
    elif failure.category == "CALLBACK":
        print(f"Callback exception: {failure.message}")
```

Setting `exit_on_failure=False` keeps longer-lived processes like MCP servers alive, allowing you to inspect specific `FailureCategory` values (`CASCADE`, `NETWORK`, `LIBRARY`, `CALLBACK`) on failed chains.

---

## Script logging

```python
from cascade_cms.utils.extension import script_log

script_log.log_note("Starting batch synchronization script")
with Cascade(environment_variables) as cascade:
    cascade.operations.read(identifier)
    results = cascade.submit_requests(Asset)
script_log.log_note("Finished batch synchronization script")
```

The `script_log` helper instance can be imported directly from `cascade_cms.utils.extension` and called anywhere in your script to write notes to the run's log.

<!-- synthesized-for: 3.10.1 -->
