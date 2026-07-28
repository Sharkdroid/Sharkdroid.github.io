---
layout: default
title: All Operations
parent: Operations Reference
nav_order: 1
---

# Operations Reference

All operations are methods on `cascade.operations`. Each one queues a request that executes when `cascade.submit_requests()` is called. Methods return `self` (unless noted), so they can be chained.

---

## Asset CRUD

### `read(identifiers, parser=parse_assets)`

Read one or more assets by identifier.

```python
cascade.operations.read(identifier)
cascade.operations.read([id1, id2, id3])  # bulk
results = cascade.submit_requests(Asset)
```

| | |
|--|--|
| **Method** | `GET` |
| **URL** | `/read/{type}/{id}` or `/read/{type}/{siteName}/{path}` |
| **Identifier** | `IdentifierType \| Path` \| `list[IdentifierType \| Path]` |
| **Response** | `Asset` |

→ [Example: ID vs. Path](../examples/pattern-read-identifiers/) · [Example: Bulk iteration](../examples/pattern-read-iterate/)

---

### `create(payload)`

Create one or more new assets.

```python
new_page = NewAsset(
    name="my-page",
    asset_type="page",
    site_name="www.example.edu",
    parent_folder_path="/blog",
)
cascade.operations.create(new_page)
cascade.operations.create([asset_a, asset_b])  # bulk
results = cascade.submit_requests(IdentifierType)
```

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `/create` |
| **Payload** | `NewAsset \| list[NewAsset]` |
| **Response** | `IdentifierType` (contains the new asset's ID, not the full asset) |

→ [Example: Bulk create](../examples/pattern-create-bulk/)

---

### `edit(payload)`

Save one or more modified assets.

```python
asset["displayName"] = "New Title"
cascade.operations.edit(asset)
cascade.operations.edit([asset_a, asset_b])  # bulk
cascade.submit_requests()
```

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `/edit` |
| **Payload** | `Asset \| list[Asset]` |
| **Response** | `CascadeError` (success or failure indicator) |

→ [Example: Edit in-place](../examples/pattern-edit-in-place/)

---

### `delete(identifier, payload=None)`

Delete an asset.

```python
from cascade_cms.cmstypes import deleteParameters

params = deleteParameters(doWorkflow=False, destinations=[], unpublish=True)
cascade.operations.delete(identifier, params)
cascade.submit_requests()
```

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `/delete/{type}/{id}` |
| **Identifier** | `IdentifierType \| Path` |
| **Payload** | `deleteParameters` (optional) |
| **Response** | `CascadeError` |

---

### `copy(identifier, payload)`

Copy an asset to a new location.

```python
from cascade_cms.cmstypes import copyParameters

params = copyParameters(
    doWorkflow=False,
    newName="copy-of-my-page",
    destinationContainerIdentifier=folder_id,
)
cascade.operations.copy(identifier, params)
cascade.submit_requests()
```

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `/copy/{type}/{id}` |
| **Identifier** | `IdentifierType \| Path \| list[...]` |
| **Payload** | `copyParameters` |
| **Response** | `CascadeError` |

---

### `move(identifier, payload)`

Move or rename an asset.

```python
from cascade_cms.cmstypes import moveParameters

params = moveParameters(
    destinations=[],
    doWorkflow=False,
    destinationContainerIdentifier=target_folder,
    newName="renamed-page",
    unpublish=True,
)
cascade.operations.move(identifier, params)
cascade.submit_requests()
```

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `/move/{type}/{id}` |
| **Identifier** | `IdentifierType \| Path \| list[...]` |
| **Payload** | `moveParameters` |
| **Response** | `CascadeError` |

---

## Search & Discovery

### `search(payload)`

Search for assets matching criteria.

```python
from cascade_cms.cmstypes import SearchInformation

payload = SearchInformation(
    siteName="www.example.edu",
    searchTerms="annual report",
    searchTypes=["page"],
    searchFields=["title", "description"],
)
cascade.operations.search(payload)
results = cascade.submit_requests(ListElements)
```

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `/search` |
| **Payload** | `SearchInformation` |
| **Response** | `ListElements` (`.elements` is a list of `IdentifierType`) |

---

### `listSites()`

List all sites the API key can access.

```python
cascade.operations.listSites()
results = cascade.submit_requests(ListElements)
```

| | |
|--|--|
| **Method** | `GET` |
| **URL** | `/listSites` |
| **Response** | `ListElements` |

---

### `listSubscribers(identifier)`

List all assets that subscribe to (reference) a given asset.

```python
cascade.operations.listSubscribers(identifier)
results = cascade.submit_requests(ListElements)
```

| | |
|--|--|
| **Method** | `GET` |
| **URL** | `/listSubscribers/{type}/{id}` |
| **Identifier** | `IdentifierType \| Path` |
| **Response** | `ListElements` |
| **Note** | Returns `None` rather than `Self` — does not support method chaining |

---

## Publishing & Version Control

### `publish(identifier, payload=None)`

Publish one or more assets.

```python
cascade.operations.publish(identifier)
cascade.operations.publish([id1, id2, id3])  # bulk
cascade.submit_requests()
```

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `/publish/{type}/{id}` |
| **Identifier** | `IdentifierType \| Path \| list[...]` |
| **Payload** | `publishInformation` (optional) |
| **Response** | `CascadeError` |

---

### `checkOut(identifier)`

Check out an asset for editing, creating a working copy. Also toggles the local checkout ledger.

```python
cascade.operations.checkOut(identifier)
results = cascade.submit_requests(CheckedOutAsset)
working_copy_id = results[0].workingCopyIdentifier
```

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `/checkOut/{type}/{id}` |
| **Identifier** | `IdentifierType \| Path \| list[...]` |
| **Response** | `CheckedOutAsset` (contains `workingCopyIdentifier`) |

---

### `checkIn(identifier, payload)`

Check in an asset after editing. Also toggles the local checkout ledger.

```python
from cascade_cms.cmstypes import Comment

comment = Comment(comment="Updated annual report section")
cascade.operations.checkIn(identifier, comment)
cascade.submit_requests()
```

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `/checkIn/{type}/{id}` |
| **Identifier** | `IdentifierType \| Path \| list[...]` |
| **Payload** | `Comment` |
| **Response** | `CascadeError` |

---

## Workflow Operations

### `readWorkflowInformation(identifier)`

Read the active workflow state for an asset, including current step and available actions.

```python
cascade.operations.readWorkflowInformation(identifier)
results = cascade.submit_requests(workflowInformation)
wf = results[0]
print(wf.current_step)
```

| | |
|--|--|
| **Method** | `GET` |
| **URL** | `/readWorkflowInformation/{type}/{id}` |
| **Identifier** | `IdentifierType \| Path` |
| **Response** | `workflowInformation` (frozen dataclass) |

→ [Example: Workflow orchestration](../examples/pattern-workflow-orchestration/)

---

### `performWorkflowTransition(identifier, payload)`

Advance an asset's workflow to the next step. Does not auto-publish or send notifications — those are determined by the workflow definition.

```python
from cascade_cms.cmstypes import workflowTransitionInformation

transition = workflowTransitionInformation(
    workflowId=wf.workflow_info_id,
    actionIdentifier="approve",      # must exist on the current step
    transitionComment="Approved",
)
cascade.operations.performWorkflowTransition(identifier, transition)
cascade.submit_requests()
```

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `/performWorkflowTransition/{type}/{id}` |
| **Identifier** | `IdentifierType \| Path` |
| **Payload** | `workflowTransitionInformation` |
| **Response** | `CascadeError` |
| **Important** | Always call `readWorkflowInformation` first to validate the `actionIdentifier` against the current step |

→ [Example: Workflow orchestration](../examples/pattern-workflow-orchestration/)

---

### `readWorkflowSettings(identifier)`

Read the workflow definitions associated with an asset.

```python
cascade.operations.readWorkflowSettings(identifier)
results = cascade.submit_requests(workflowSettingsPayload)
```

| | |
|--|--|
| **Method** | `GET` |
| **URL** | `/readWorkflowSettings/{type}/{id}` |
| **Identifier** | `IdentifierType \| Path` |
| **Response** | `workflowSettingsPayload` |

---

### `editWorkflowSettings(payload)`

Update the workflow settings for an asset. Identifier is extracted from the payload.

```python
cascade.operations.editWorkflowSettings(settings_payload)
cascade.submit_requests()
```

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `/editWorkflowSettings/{type}/{id}` |
| **Payload** | `workflowSettingsPayload` |
| **Response** | `CascadeError` |
| **Note** | Returns `None` rather than `Self` — does not support method chaining |

---

## Access Control

### `readAccessRights(identifier)`

Read the ACL entries for an asset.

```python
cascade.operations.readAccessRights(identifier)
results = cascade.submit_requests(accessRightsInformationPayload)
```

| | |
|--|--|
| **Method** | `GET` |
| **URL** | `/readAccessRights/{type}/{id}` |
| **Identifier** | `IdentifierType \| Path` |
| **Response** | `accessRightsInformationPayload` |

---

### `editAccessRights(payload)`

Update the ACL entries for an asset.

```python
cascade.operations.editAccessRights(access_rights_payload)
cascade.submit_requests()
```

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `/editAccessRights` |
| **Payload** | `accessRightsInformationPayload` |
| **Response** | `CascadeError` |

---

## Audit & Admin

### `readAudits(payload)`

Read the audit log for a user, group, or role.

```python
from cascade_cms.cmstypes import auditParameters

params = auditParameters(
    auditType="publish",
    identifier=user_identifier,  # must be user, group, or role
)
cascade.operations.readAudits(params)
results = cascade.submit_requests(ListElements)
```

| | |
|--|--|
| **Method** | `GET` |
| **URL** | `/readAudits` |
| **Payload** | `auditParameters` |
| **Response** | `ListElements` |
| **Constraint** | `identifier` must reference a `user`, `group`, or `role` — not a content asset |

---

### `siteCopy(payload)`

Copy an entire site.

```python
from cascade_cms.cmstypes import SiteCopyParameter

params = SiteCopyParameter(
    originalSiteName="www.example.edu",
    newSiteName="www-staging.example.edu",
)
cascade.operations.siteCopy(params)
cascade.submit_requests()
```

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `/siteCopy` |
| **Payload** | `SiteCopyParameter` |
| **Response** | `CascadeError` |

---

### `readPreferences()`

Read the current user's Cascade preferences.

```python
cascade.operations.readPreferences()
results = cascade.submit_requests(ListElements)
```

| | |
|--|--|
| **Method** | `GET` |
| **URL** | `/readPreferences` |
| **Response** | `ListElements` |

---

### `editPreference(payload)`

Update a single user preference.

```python
from cascade_cms.cmstypes import preference

pref = preference(name="defaultSiteId", value="site-uuid-here")
cascade.operations.editPreference(pref)
cascade.submit_requests()
```

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `/editPreference` |
| **Payload** | `preference` |
| **Response** | `CascadeError` |
| **Note** | Returns `None` rather than `Self` |

---

## Messaging

### `listMessages()`

List all messages in the current user's inbox.

```python
cascade.operations.listMessages()
results = cascade.submit_requests(ListElements)
messages = [e for e in results[0].elements if isinstance(e, Message)]
```

| | |
|--|--|
| **Method** | `GET` |
| **URL** | `/listMessages` |
| **Response** | `ListElements` (`.elements` contains `Message` objects) |

---

### `markMessage(message)`

Mark a message as read or unread.

```python
message.marked = "read"
cascade.operations.markMessage(message)
cascade.submit_requests()
```

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `/markMessage/{type}/{id}` |
| **Payload** | `Message` |
| **Response** | `CascadeError` |
| **Note** | Returns `None` rather than `Self` |

---

### `deleteMessage(message)`

Delete a message from the inbox.

```python
cascade.operations.deleteMessage(message)
cascade.submit_requests()
```

| | |
|--|--|
| **Method** | `POST` |
| **URL** | `/deleteMessage/{type}/{id}` |
| **Payload** | `Message` |
| **Response** | `CascadeError` |
| **Note** | Returns `None` rather than `Self` |
