# Core Concepts

Every cascade-cms-rest script is built around a single session object that provides an operations builder, chaining independent units of work, explicit batch submission, and structured value-based results.

---

## The session entry point

The primary entry point for any script is the `Cascade` class, which opens as a context manager and ties together the logger, REST driver, and operations builder. (`CascadeWrapperBase` is an alias for `Cascade`, but `Cascade` is preferred.) When the `with` block exits, `Cascade` automatically runs any submitted operations, handles failures according to its configuration, and shuts down cleanly. By default, `exit_on_failure=True` causes the script to exit with a non-zero exit code if any operation chain fails, meaning code written after the `with` block will not execute in that event; passing `exit_on_failure=False` ensures the session never raises on failure, keeping results accessible as values via `.success` and `.failed` for embedding in long-lived processes like MCP servers.

```python
from cascade_cms import Cascade

environment_variables = {
    "SERVER": "cascade.example.com",
    "API_KEY": "your-api-key",
    "CASCADE_URL": "http://cascade.example.com:8080/api/v1",
}

with Cascade(environment_variables) as cascade:
    pass
```

### Constructor

```python
__init__(environment_variables: EnvironmentVars, *, exit_on_failure: bool = True, debug: bool = False, logfile: str | Path | None = None)
```

| Key | Description |
| :--- | :--- |
| `SERVER` | The hostname or IP address of the Cascade CMS server. |
| `API_KEY` | The authentication API key provided by Cascade. |
| `CASCADE_URL` | The full base URL for the Cascade REST API endpoint. |

* `environment_variables`: A dictionary containing the required connection keys (`SERVER`, `API_KEY`, `CASCADE_URL`).
* `exit_on_failure`: A boolean flag defaulting to `True` which terminates the script with a non-zero exit code if any chain fails upon exiting the context manager.
* `debug`: A boolean flag enabling verbose debug-mode logging.
* `logfile`: An optional custom file path or `Path` object for writing session logs.

---

## Operations

The `cascade.operations` builder starts a new operation chain on every method call, returning the chain rather than executing immediately or returning a result.

| Method | Description |
| :--- | :--- |
| `read` | Read an asset's data from Cascade. |
| `create` | Create a new asset using a payload. |
| `edit` | Save one or more modified assets. |
| `delete` | Delete an asset or assets. |
| `copy` | Copy an asset to a new location. |
| `move` | Move an asset to a new location. |
| `publish` | Publish an asset. |
| `search` | Search for assets in a site. |
| `checkIn` | Check in a working copy with a comment. |
| `checkOut` | Check out an asset to create a working copy. |
| `listSites` | List available sites. |
| `readAudits` | Read audit logs. |
| `listSubscribers` | List asset subscribers. |
| `siteCopy` | Copy an entire site. |
| `readAccessRights` | Read access control entries for an asset. |
| `editAccessRights` | Update access control entries for an asset. |
| `readWorkflowSettings` | Read workflow configuration settings. |
| `editWorkflowSettings` | Update workflow configuration settings. |
| `listMessages` | List inbox messages. |
| `markMessage` | Mark an inbox message with a state. |
| `deleteMessage` | Delete an inbox message. |
| `readPreferences` | Read user preferences. |
| `editPreference` | Update a user preference. |
| `readWorkflowInformation` | Read active workflow information for an asset. |
| `performWorkflowTransition` | Advance or transition an active workflow. |

For full method signatures and parameter details, see [the API reference](../operations/operations.md).

---

## Operation chains

An operation chain represents an ordered list of steps consisting of operations and callbacks. Each step receives the output of the previous step as its input, and nothing executes until the batch is explicitly submitted via `submit_requests()`. If a callback returns `None`, it is treated as a side effect and the previous result passes through unchanged.

```python
from cascade_cms import Cascade
from cascade_cms.cmstypes import IdentifierType, AssetTypes

def report(asset):
    print(asset.internal_type)
    return asset

page_a = IdentifierType(id="12345678-1234-5678-1234-567812345678", asset_type="page")

with Cascade(environment_variables) as cascade:
    cascade.operations.read(page_a).then(report)
    results = cascade.submit_requests()
```

---

## Editing with callbacks

The `edit` operation accepts an `Asset`, a list of `Asset` objects, or a callable that accepts the previous node's result and produces an `Asset` or list of `Asset` objects. The callable form is the usual pattern for modifying and saving an asset retrieved earlier in the chain. Each asset's own id, path, and site fields determine its identity and target endpoint when saved.

```python
def rewrite(asset):
    return asset

with Cascade(environment_variables) as cascade:
    cascade.operations.read(page_a).then(rewrite).edit(rewrite)
    results = cascade.submit_requests()
```

---

## Batch execution

Passing a list of identifiers to an identifier-taking operation fans the call out into independent chains—one chain per identifier—with any subsequent `.then()` or operation calls applied to every generated chain. Chains execute concurrently while the steps within each individual chain stay strictly sequential. A failure in one chain is isolated and does not stop or affect any other chain in the batch.

```python
pages = [
    IdentifierType(id="12345678-1234-5678-1234-567812345678", asset_type="page"),
    IdentifierType(id="87654321-4321-6789-4321-876543210987", asset_type="page"),
]

with Cascade(environment_variables) as cascade:
    cascade.operations.read(pages).then(report)
    results = cascade.submit_requests()
```

---

## Result handling

Submitting requests returns a `ChainResults` container holding one result per chain in the exact order the chains were created. It provides `.success` (containing values from chains that completed successfully) and `.failed` (containing a `ChainFailure` record for every failed chain naming the exact failing step and failure category). Callers do not need `try/except` blocks or `isinstance` checks to catch flow-breaking exceptions because errors are returned as values directly inside the results list.

```python
with Cascade(environment_variables) as cascade:
    cascade.operations.read(page_a).then(report)
    results = cascade.submit_requests()

for success_val in results.success:
    print("Success:", success_val)

for failure in results.failed:
    print("Failed at step", failure.step, ":", failure.message)
```

For more details, see [Result Handling](../getting-started/result-handling.md).

---

## Script logging

The library provides a `script_log` helper to write custom notes directly into the session's run log. It can be called from anywhere inside or outside a session context, automatically redacting sensitive secrets, though notes written outside an active session are not bound to a running operation logfile.

```python
from cascade_cms.utils.extension import script_log

script_log.log_note("Starting batch synchronization pass.")
```

---

## Identifiers

Assets in Cascade can be addressed by their unique identifier (`id` and `asset_type`) or by their path and site info (`Path` or `PathBase`). Raw identifier dictionaries returned from API responses can be safely parsed and converted into typed identifier objects using the library's conversion helpers.

```python
from cascade_cms.utils.extension import to_identifier, to_identifiers

raw_data = {"id": "12345678-1234-5678-1234-567812345678", "type": "page"}
identifier = to_identifier(raw_data)

raw_children = [{"id": "87654321-4321-6789-4321-876543210987", "type": "folder"}]
identifiers = to_identifiers(raw_children)
```

---

## Next Steps

For practical code examples and copy-pasteable recipes, head over to [Examples](../examples/main-patterns.md). For details on custom log configuration, error categories, and CPU-heavy process pool callbacks, check out [Advanced](../advanced/index.md).

<!-- synthesized-for: 3.10.1 -->
