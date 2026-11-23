<!-- purpose: Recipes for the two feature areas that don't touch CMS assets: the current user's message inbox and their account preferences. Same shape as Main Patterns: setup → operation → submit → use the results. -->
<!-- focus: Cascade, Message, ListElements, preference, listMessages, markMessage, deleteMessage, readPreferences, editPreference, submit_requests -->
# Administrative Operations: Messages & Preferences

[PLACEHOLDER: 2–3 sentences: these operations manage the signed-in user's inbox and preferences rather than CMS assets, and follow the same session → operations → submit flow as [Main Patterns](main-patterns.md).]

---

## Messages: list, mark, delete

[PLACEHOLDER: Code block with two batches in one session: first list the inbox and pick messages from the result; then mark one and delete another and submit again. Use the message type and method signatures exactly as the code facts give them, including what the mark and delete steps take as input.]

[PLACEHOLDER: 1–2 sentences on what the mark/delete steps need as input and what they return.]

---

## Preferences: read, edit

[PLACEHOLDER: Code block: read the current preferences, then edit one preference using the preference payload type from the code facts, and submit again.]

[PLACEHOLDER: 1–2 sentences on what the read returns and whether preferences can be updated in bulk, based on the operations the code facts list.]

---

See [Main Patterns](main-patterns.md) for reading, editing, publishing and searching assets.
