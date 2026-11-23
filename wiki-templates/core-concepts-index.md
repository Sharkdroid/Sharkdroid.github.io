<!-- purpose: Explain the library's mental model to someone who has finished Getting Started: one session object, an operations builder, operation chains that run only when submitted, and results returned as values. Conceptual page; each section gets a short explanation plus one small, runnable example. -->
<!-- focus: Cascade, EnvironmentVars, Operations, OperationChain, ChainGroup, ChainResults, ChainFailure, submit_requests, then, edit, script_log, to_identifier, to_identifiers -->
# Core Concepts

[PLACEHOLDER: 1–2 sentence intro bridging from Getting Started: this page explains the pieces every script is built from and how they fit together (session → operations → chains → submit → results).]

---

## The session entry point

[PLACEHOLDER: Explain the class every script opens as a context manager, what it sets up (logger, REST driver, operations builder), and what happens when the `with` block exits, including the exit-on-failure behaviour and how to turn it off for long-lived processes. If the code facts list an older alias for this class, mention it in one sentence and use the current name everywhere else. Follow with a minimal code block that builds the environment dict and opens a session.]

### Constructor

[PLACEHOLDER: The constructor signature exactly as the code facts give it, in a code block, followed by a table of the required environment keys (key and description) and one sentence per optional parameter.]

---

## Operations

[PLACEHOLDER: Explain the operations builder: every call on it starts a new chain and returns it instead of a result. Follow with a table of the available operations (method and a one-line description) taken from the builder class in the code facts. List them all, grouped as asset operations, workflow and access operations, and messages/preferences, and do not guess signatures in the table. End with a link to [the API reference](../operations/operations.md) for full signatures.]

---

## Operation chains

[PLACEHOLDER: Explain that a chain is an ordered list of steps (operations and callbacks), that each step receives the previous step's result, that nothing runs until the batch is submitted, and that a callback returning None passes the previous result through. Show one code block with a read, a transforming callback and a write-back, submitted once. Build identifiers with the identifier types from the code facts, not bare strings.]

---

## Editing with callbacks

[PLACEHOLDER: Explain the forms the edit step accepts (from its signature in the code facts), why the callable form is the usual one, and how the edited asset's identity is determined. Show a short code block with a module-level callback that changes one field and returns the asset.]

---

## Batch execution

[PLACEHOLDER: Explain what happens when an identifier-taking operation receives a list: one independent chain per identifier, with any further steps applied to every chain. Explain that chains run concurrently while steps inside a chain stay sequential, and that one chain's failure does not stop the others. Short code block.]

---

## Result handling

[PLACEHOLDER: Explain what submitting returns: one result per chain in creation order, plus the success and failed views, and what a failure record tells you. State, as the code facts' docstrings do, whether callers need isinstance checks or try/except. Short code block iterating successes and failures, then link to [Result Handling](../getting-started/result-handling.md).]

---

## Script logging

[PLACEHOLDER: Explain the helper for writing your own notes into the run's log: where it can be called from, what happens outside a session, and that secrets are redacted. Show a short code block, importing it from the module the code facts list.]

---

## Identifiers

[PLACEHOLDER: Explain the two ways to address an asset (by id and type, or by site and path) and the helpers that turn raw identifier dicts from API responses into identifier objects. Short code block, importing every name from the module the code facts list for it.]

---

## Next Steps

[PLACEHOLDER: 1–2 sentences pointing to [Examples](../examples/main-patterns.md) for task-oriented recipes and [Advanced](../advanced/index.md) for logging and CPU-heavy callbacks.]
