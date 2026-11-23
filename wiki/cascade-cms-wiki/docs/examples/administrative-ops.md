# Administrative Operations: Messages & Preferences

These administrative operations manage the signed-in user's inbox and personal preferences rather than CMS assets. They follow the exact same session, operations builder, and submit flow covered in [Main Patterns](main-patterns.md).

---

## Messages: list, mark, delete

```python
from cascade_cms.wrapper import Cascade
from cascade_cms.cmstypes import Message

environment_variables = {
    "API_KEY": "...",
    "CASCADE_URL": "...",
    "SERVER": "prod",
}

with Cascade(environment_variables) as cascade:
    cascade.operations.listMessages()
    results = cascade.submit_requests()
    
    # Pick a message from the results to mark and delete
    messages = results.success[0].elements
    target_msg = messages[0]

with Cascade(environment_variables) as cascade:
    cascade.operations.markMessage(target_msg)
    cascade.operations.deleteMessage(target_msg)
    results = cascade.submit_requests()
```

The `markMessage` and `deleteMessage` operations take a `Message` instance as input and return an `OperationChain` that evaluates to a `CascadeSuccess` response upon execution.

---

## Preferences: read, edit

```python
from cascade_cms.wrapper import Cascade
from cascade_cms.cmstypes import preference

environment_variables = {
    "API_KEY": "...",
    "CASCADE_URL": "...",
    "SERVER": "prod",
}

with Cascade(environment_variables) as cascade:
    cascade.operations.readPreferences()
    cascade.operations.editPreference(preference(name="somePreference", value="someValue"))
    results = cascade.submit_requests()
```

Reading preferences returns a container payload of user preferences, while editing preferences operates on a single user preference name and value at a time via the `preference` payload type.

---

See [Main Patterns](main-patterns.md) for reading, editing, publishing and searching assets.

<!-- synthesized-for: 3.10.1 -->
