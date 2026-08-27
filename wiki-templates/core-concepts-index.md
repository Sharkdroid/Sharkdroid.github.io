# Core Concepts

[PLACEHOLDER: 1–2 sentence intro that bridges from Getting Started — what this page adds on top of the quick-start guide. Should reference the library's "mental model": wrapper → operations → chains → submit.]

---

## Basic Operation Calls

[PLACEHOLDER: Short paragraph explaining how every script follows the same skeleton — open the wrapper as a context manager, queue operations on `cascade.operations`, chain callbacks with `.then()`, then call `submit_requests()` once to execute all chains concurrently. Keep it to 3–4 sentences.]

### Example

[PLACEHOLDER: Code block showing a minimal `read` call — `CascadeWrapperBase` context manager, `cascade.operations.read(identifier)`, `cascade.submit_requests()`, and a `isinstance(result, CascadeError)` guard. Source from the `read` docstring example in operations.md. Include inline `# comments` explaining each line.]

### Expected Output

[PLACEHOLDER: Code block or annotated console output showing what the `read` result looks like — the `Asset` wrapper with `.displayName`, `.metadata`, etc. referenced. Use the example output from the `read` docstring if present, otherwise describe the shape concisely.]

---

## Payload Models

[PLACEHOLDER: 2–3 sentence explanation of what payload models are and why they exist — typed objects (e.g. `SearchInformation`) that pair with specific operations to ensure the API endpoint receives the expected fields. Explain the type-safety/clarity benefit without being verbose.]

### Example: `SearchInformation` paired with `search`

[PLACEHOLDER: Code block showing `SearchInformation` constructed with its fields (`siteName`, `searchTerms`, `searchFields`, `searchTypes`) and passed to `cascade.operations.search(payload)`. Source from the `SearchInformation` and `search` docstrings in cmstypes.md and operations.md. Include a brief comment on what each field does.]

[PLACEHOLDER: 1–2 sentence explanation below the code block — what the model enforces, why passing a raw dict would not work, and that other operations follow the same pattern (`deleteParameters`, `auditParameters`, etc.).]

---

## CPU-Intensive Operations

For operations involving heavy computation in `.then()` callbacks — image processing, data transformation, bulk string manipulation — offload work to a `ProcessPoolExecutor` rather than running it on the async event loop.

[PLACEHOLDER: 4–6 line code snippet showing the `ProcessPoolExecutor` context manager wrapping a `CascadeWrapperBase` block, with a module-level callback function passed to `.then()`. Source from the `CascadeWrapperBase` or `then` docstring examples if present.]

!!! note "Module-level functions only"
    Callbacks passed to `ProcessPoolExecutor` must be defined at module level — lambdas and nested functions are not picklable and will raise at runtime.

See [Advanced: CPU-Intensive Tasks](../advanced/cpu-intensive.md) for full configuration details, performance trade-offs, and `ThreadPoolExecutor` comparison.

---

## Next Steps

Ready to go deeper? The [Advanced](../advanced/index.md) section covers configuration topics for power users: caching strategies, debug logging, and CPU-intensive workload patterns.
