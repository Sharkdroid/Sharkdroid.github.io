# Core Concepts

Every cascade-cms-rest script is built around a cohesive session context that manages state, builds operation pipelines, and executes them concurrently while capturing structured results. This page breaks down the mental model behind session handling, operation chains, callbacks, and result processing.

---

## The session entry point

The `Cascade` class (also importable under its older alias `CascadeWrapperBase`) serves as the central context manager that ties together the logger, the REST driver, and the operations builder for a single script session. When the `with` block exits, the session automatically triggers batch execution and enforces failure handling. By default, `exit_on_failure=True` means any recorded failure ends the script immediately with a non-zero exit code so that subsequent code does not run; passing `exit_on_failure=False` prevents this behavior, making it ideal for embedding the wrapper inside longer-lived processes like an MCP server where results should be inspected programmatically via `.success` and `.failed`.

```python
from cascade_cms import Cascade
from cascade_cms.wrapper import EnvironmentVars

environment_variables: EnvironmentVars = {
    "SERVER": "cascade.example.com",
    "API_KEY": "12345678-abcd-ef01-2345-6789abcdef01",
    "CASCADE_URL": "http://cascade.example.com:8080/api/v1"
}

with Cascade(environment_variables) as cascade:
    pass
```

### Constructor

```python
class Cascade:
    def __init__(self, environment_variables: EnvironmentVars, *, exit_on_failure: bool = True, debug: bool = False, log_file: str | None = None) -> None
```

| Key | Description |
| :--- | :--- |
| `SERVER` | The Cascade CMS server hostname or IP address. |
| `API_KEY` | The authentication API key provided by Cascade. |
| `CASCADE_URL` | The fully qualified base URL for the Cascade REST API. |

- `environment_variables`: A dictionary satisfying the `EnvironmentVars` TypedDict containing connection properties (`SERVER`, `API_KEY`, `CASCADE_URL`).
- `exit_on_failure`: A boolean flag determining whether the context manager exits the script with a non-zero status code if any operation chain fails (defaults to `True`).
- `debug`: A boolean flag enabling verbose logging and request detail tracking (defaults to `False`).
- `log_file`: An optional file path string to redirect or write operation audit logs.

---

## Operations

The operations builder acts as a fluent entry point where every method call instantiates and returns a brand-new `OperationChain` rather than executing immediately. 

| Method | Description |
| :--- | :--- |
| `read` | Reads an asset or container by identifier or path. |
| `edit` | Saves one or more modified assets via a POST request. |
| `delete` | Deletes an asset, folder, or site. |
| `create` | Creates a new asset from payload configurations. |
| `copy` | Copies an asset to a destination container. |
| `move` | Moves an asset to a new container and/or renames it. |
| `publish` | Publishes or unpublishes an asset. |
| `search` | Queries Cascade using search terms and filters. |
| `checkIn` | Checks in an asset using a check-in comment payload. |
| `checkOut` | Checks out an asset, returning its working copy identifier. |
| `listSites` | Lists available sites on the server. |
| `readAudits` | Reads audit logs based on audit parameters. |
| `listSubscribers` | Lists subscribers associated with an asset. |
| `siteCopy` | Copies an entire site configuration. |
| `readAccessRights` | Reads user and group access control entries. |
| `editAccessRights` | Modifies access control configurations. |
| `readWorkflowSettings` | Reads workflow settings assigned to an asset. |
| `editWorkflowSettings` | Edits an asset's workflow settings. |
| `listMessages` | Lists user inbox messages. |
| `markMessage` | Marks a message with a specific status. |
| `deleteMessage` | Deletes an inbox message. |
| `readPreferences` | Reads user preferences. |
| `editPreference` | Modifies an individual user preference. |
| `readWorkflowInformation` | Reads active workflow step and action details. |
| `performWorkflowTransition` | Performs a transition action on a workflow instance. |

For full method signatures and parameter details, consult [the API reference](../operations/operations.md).

---

## Operation chains

An `OperationChain` is an ordered sequence of steps consisting of REST operations and local callbacks. Nodes run strictly in order where each step receives the preceding node's result. Execution is deferred entirely until `submit_requests()` is invoked. If a callback returns `None`, it is treated as a side effect and the previous result is passed through unchanged.

```python
from cascade_cms import Cascade
from cascade_cms.cmstypes import Asset, IdentifierType

def report(asset: Asset) -> None:
    print(f"Inspected asset name: {asset.internal_type}")

with Cascade(environment_variables) as cascade:
    target_id = IdentifierType(identifier="12345678-1234-1234-1234-1234567890ab", asset_type="page")
    cascade.operations.read(target_id).then(report)
    results = cascade.submit_requests()
```

---

## Editing with callbacks

The `edit` step accepts an `Asset`, a list of `Asset` objects, or a callable producing an asset from the previous node's output. The callable form is most common in a `read → then(transform) → edit` pipeline because it receives the fetched asset, modifies it in memory, and returns it for saving. The identity of the edited asset is derived automatically from its internal identifiers.

```python
from cascade_cms import Cascade
from cascade_cms.cmstypes import Asset, IdentifierType

def rewrite(asset: Asset) -> Asset:
    return asset

with Cascade(environment_variables) as cascade:
    page_id = IdentifierType(identifier="12345678-1234-1234-1234-1234567890ab", asset_type="page")
    cascade.operations.read(page_id).edit(rewrite)
    results = cascade.submit_requests()
```

---

## Batch execution

When an operation that accepts identifiers receives a list, the library automatically fans out the request into one independent chain per identifier (Approach A). Subsequent chaining methods like `.then()` or `.edit()` apply to all generated chains. Chains execute concurrently while steps within individual chains remain sequential, ensuring that a failure in one asset's chain does not halt execution for the others.

```python
from cascade_cms import Cascade
from cascade_cms.cmstypes import IdentifierType

with Cascade(environment_variables) as cascade:
    id_one = IdentifierType(identifier="11111111-1111-1111-1111-111111111111", asset_type="page")
    id_two = IdentifierType(identifier="22222222-2222-2222-2222-222222222222", asset_type="page")
    
    cascade.operations.read([id_one, id_two]).then(lambda asset: print(asset.internal_type))
    results = cascade.submit_requests()
```

---

## Result handling

Submitting requests returns a `ChainResults` container holding one result per chain in creation order, along with computed `.success` and `.failed` lists. A failure record contains comprehensive diagnostic details including the failing step index, node type, failure category, and error message. Because errors are captured as values in the results collection rather than raising unhandled exceptions during batch evaluation, callers can inspect failures directly without complex `try/except` blocks.

```python
with Cascade(environment_variables) as cascade:
    cascade.operations.read(page_a).then(rewrite).edit(rewrite)
    results = cascade.submit_requests()

    for success_item in results.success:
        print("Succeeded:", success_item)

    for failure_record in results.failed:
        print(f"Failed at step {failure_record.step} ({failure_record.step_name}): {failure_record.message}")
```

For more details, see [Result Handling](../getting-started/result-handling.md).

---

## Script logging

The library provides a built-in `script_log` helper to write custom notes directly into the session's operation log. This utility can be called from anywhere inside or outside an active session, automatically redacting sensitive properties or keys when appropriate.

```python
from cascade_cms.utils.extension import script_log

script_log.log_note("Starting batch migration of configuration blocks.")
```

---

## Identifiers

Assets can be addressed in Cascade either by their unique UUID identifier combined with an asset type, or by specifying a site name and path location. Raw identifier dictionaries returned from API responses can be safely converted into robust `IdentifierType` objects using extension helpers.

```python
from cascade_cms.cmstypes import IdentifierType, Path
from cascade_cms.utils.extension import to_identifier, to_identifiers

raw_dict = {"id": "12345678-1234-1234-1234-1234567890ab", "type": "page"}
parsed_id = to_identifier(raw_dict)

batch_list = to_identifiers([{"id": "11111111-1111-1111-1111-111111111111", "type": "folder"}])
```

---

## Next Steps

Explore task-oriented recipes in [Examples](../examples/main-patterns.md) or look into logging configurations and CPU-heavy callbacks under [Advanced](../advanced/index.md).

<!-- synthesized-for: 3.10.1 -->
