# Result Handling

`.submit_requests()` returns a `ChainResults[T]` — a list subclass that
wraps the results of all chains in the batch. It has two properties:
`.success` and `.failed`.

```python
from cascade_cms.wrapper import Cascade
from cascade_cms.cmstypes import Asset

with Cascade(env) as cascade:
    results = cascade.operations.read("abc123").submit_requests(Asset)

print(len(results.success))   # assets that completed
print(len(results.failed))    # assets that hit an error
```

---

## `.success` and `.failed`

Both return lists. `.success` is a list of the result type passed to
`.submit_requests()`. `.failed` is a list of `ChainFailure` objects.

```python
for asset in results.success:
    print(asset.path)          # typed as Asset

for failure in results.failed:
    print(failure.identifier)  # which asset failed
    print(failure.step_name)   # operation that failed ("read", "edit", …)
    print(failure.step)        # step index (int)
    print(failure.message)     # human-readable description
    print(failure.category)    # FailureCategory enum value
```

`ChainFailure` fields:

| Field | Type | Description |
|---|---|---|
| `chain_index` | `int` | Position in the batch |
| `identifier` | `str` | Asset identifier |
| `step` | `int` | Index of the operation that failed |
| `step_name` | `str` | Name of the operation (`"read"`, `"edit"`, …) |
| `category` | `FailureCategory` | Error category (already computed) |
| `error` | `Exception` | Underlying exception |
| `message` | `str` | Summary string |

---

## Failure categories

`ChainFailure.category` already holds the `FailureCategory` value — use it
directly. `FailureCategory` has four values:

```python
from cascade_cms.utils.failures import FailureCategory

for failure in results.failed:
    if failure.category == FailureCategory.NETWORK:
        # transient — retry is reasonable
        ...
    elif failure.category == FailureCategory.CASCADE:
        # Cascade returned an error (bad identifier, permission denied, …)
        ...
    elif failure.category == FailureCategory.CALLBACK:
        # your edit callback raised an exception
        ...
    elif failure.category == FailureCategory.LIBRARY:
        # internal library error — file a bug
        ...
```

| Category | Cause |
|---|---|
| `CASCADE` | Cascade CMS returned a failure response |
| `NETWORK` | Request did not reach the server or timed out |
| `CALLBACK` | An edit callback function raised an exception |
| `LIBRARY` | Internal library error |

---

## Exit behavior

By default (`exit_on_failure=True`), `Cascade` exits the script non-zero
when any chain fails. Code after the `with` block does not run:

```python
with Cascade(env) as cascade:
    results = cascade.operations.read("abc123").submit_requests(Asset)

# Only runs when zero chains failed
print("All done.")
```

Pass `exit_on_failure=False` to keep the process alive regardless of
failures — for example, inside an MCP server:

```python
with Cascade(env, exit_on_failure=False) as cascade:
    results = cascade.operations.read("abc123").submit_requests(Asset)

if results.failed:
    log_failures(results.failed)
```

---

## Upgrading from older versions

Prior to 3.8.0, result handling used `isinstance` checks against a
`CascadeError` class. That pattern no longer works:

```python
# Old pattern (pre-3.8.0) — do not use
result = wrapper.read(id)
if isinstance(result, CascadeError):
    print("failed")

# Current pattern (3.8.0+)
results = cascade.operations.read(id).submit_requests(Asset)
for failure in results.failed:
    print(f"[{failure.category}] {failure.message}")
```

See [Version History](./version-history.md) for the full list of breaking
changes between versions.
