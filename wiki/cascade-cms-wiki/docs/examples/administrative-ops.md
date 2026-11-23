# Administrative Operations: Messages & Preferences

These administrative operations manage the signed-in user's inbox and personal preferences rather than CMS assets. They follow the exact same session, operations, and submission flow as demonstrated in [Main Patterns](main-patterns.md).

---

## Messages: list, mark, delete

```python
from cascade_cms.wrapper import Cascade

environment_variables = {
    "API_KEY": "...",
    "CASCADE_URL": "...",
    "SERVER": "prod",
}

with Cascade(environment_variables) as cascade:
    cascade.operations.listMessages()
    list_results = cascade.submit_requests()
    
    inbox_messages = list_results.success[0].elements

with Cascade(environment_variables) as cascade:
    cascade.operations.markMessage(inbox_messages[0])
    cascade.operations.deleteMessage(inbox_messages[1])
    cascade.submit_requests()
```

The `markMessage` and `deleteMessage` steps take a `Message` instance as input and return `CascadeSuccess` responses indicating the operation succeeded.

---

## Preferences: read, edit

```python
from cascade_cms.cmstypes import preference
from cascade_cms.wrapper import Cascade

environment_variables = {
    "API_KEY": "...",
    "CASCADE_URL": "...",
    "SERVER": "prod",
}

with Cascade(environment_variables) as cascade:
    cascade.operations.readPreferences()
    results = cascade.submit_requests()

with Cascade(environment_variables) as cascade:
    pref = preference(name="some-preference", value="new-value")
    cascade.operations.editPreference(pref)
    cascade.submit_requests()
```

The read preferences operation returns a container payload holding the user preferences. Preferences are updated individually through the `editPreference` operation using the `preference` payload type.

---

See [Main Patterns](main-patterns.md) for reading, editing, publishing and searching assets.

<!-- synthesized-for: 3.10.1 -->
