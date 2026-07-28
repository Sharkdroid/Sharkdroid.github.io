---
layout: default
title: Workflow Orchestration
parent: Examples & Patterns
nav_order: 10
---

# Workflow orchestration

The recommended pattern for advancing a workflow: read current state, validate the action exists on the current step, perform the transition, then read state again to confirm. The library exposes each REST call — your script owns the orchestration logic.

```python
import os
from uuid import UUID
from dotenv import load_dotenv
from cascade_cms.cmstypes import (
    IdentifierType,
    workflowInformation,
    workflowTransitionInformation,
)
from cascade_cms.wrapper import CascadeWrapperBase

load_dotenv()

env = {
    "API_KEY": os.environ["CASCADE_API_KEY"],
    "CASCADE_URL": os.environ["CASCADE_URL"],
    "SERVER": os.environ["SERVER"],
}
config = {
    "cache_name": "./cache/cache.sqlite",
    "allowed_codes": (200,),
    "allowed_methods": ("GET",),
}

asset_id = IdentifierType(
    identifier=UUID("8b320f55ac1001062545a6d2562cee4b"),
    asset_type="page",
)
desired_action = "approve"

with CascadeWrapperBase(env, config) as cascade:

    # Step 1: Read current workflow state
    cascade.operations.readWorkflowInformation(asset_id)
    wf_results = cascade.submit_requests(workflowInformation)

    if not wf_results:
        print("No active workflow on this asset.")
        exit(0)

    wf = wf_results[0]
    print(f"Workflow: {wf.name}")
    print(f"Current step: {wf.current_step}")

    # Step 2: Find the current step and validate the action exists
    current_step = next(
        (s for s in wf.ordered_steps
         if s["step_identifier"] == wf.current_step),
        None,
    )

    if current_step is None:
        print(f"Step '{wf.current_step}' not found in ordered steps.")
        exit(1)

    available_actions = [
        a["action_identifier"] for a in current_step.get("actions", [])
    ]
    print(f"Available actions: {available_actions}")

    if desired_action not in available_actions:
        print(f"Action '{desired_action}' is not available in the current step.")
        exit(1)

    # Step 3: Perform the transition
    transition = workflowTransitionInformation(
        workflowId=wf.workflow_info_id,
        actionIdentifier=desired_action,
        transitionComment="Approved via automation script",
    )
    cascade.operations.performWorkflowTransition(asset_id, transition)
    cascade.submit_requests()
    print(f"Transition '{desired_action}' submitted.")

    # Step 4: Read updated workflow state to confirm
    cascade.operations.readWorkflowInformation(asset_id)
    updated = cascade.submit_requests(workflowInformation)

    if updated:
        print(f"New step: {updated[0].current_step}")
    else:
        print("Workflow completed (no active workflow returned).")
```

## What this does not do automatically

A successful transition does not:

- **Publish the asset** — Publishing depends on the workflow definition, not this call
- **Send notifications** — Emails and alerts are triggered by workflow configuration in Cascade, not by the library
- **Advance multiple steps** — Each `performWorkflowTransition` call advances exactly one step

If your workflow has side effects (auto-publish on approve, email on reject), they occur on the Cascade side. Your script does not need to trigger them separately — but it also cannot intercept them.

## Inspecting workflow structure before running

To see what steps and actions are available without committing a transition:

```python
with CascadeWrapperBase(env, config) as cascade:
    cascade.operations.readWorkflowInformation(asset_id)
    wf = cascade.submit_requests(workflowInformation)[0]

print(f"Workflow: {wf.name}")
print(f"Current step: {wf.current_step}")
for step in wf.ordered_steps:
    actions = [a["action_identifier"] for a in step.get("actions", [])]
    print(f"  Step '{step['step_identifier']}': actions = {actions}")
```

## Bulk workflow transitions

To advance the same step on many assets:

```python
asset_ids = [
    IdentifierType(identifier=UUID("aaa..."), asset_type="page"),
    IdentifierType(identifier=UUID("bbb..."), asset_type="page"),
]

with CascadeWrapperBase(env, config) as cascade:
    for asset_id in asset_ids:
        cascade.operations.readWorkflowInformation(asset_id)

    wf_states = cascade.submit_requests(workflowInformation)

    for asset_id, wf in zip(asset_ids, wf_states):
        available = [
            a["action_identifier"]
            for step in wf.ordered_steps
            for a in step.get("actions", [])
            if step["step_identifier"] == wf.current_step
        ]
        if desired_action in available:
            transition = workflowTransitionInformation(
                workflowId=wf.workflow_info_id,
                actionIdentifier=desired_action,
                transitionComment="Bulk approval",
            )
            cascade.operations.performWorkflowTransition(asset_id, transition)

    cascade.submit_requests()
```

---

See also: [Operations: readWorkflowInformation](../operations/all-operations/#readworkflowinformation) · [Core Concepts: Philosophy](../core-concepts/#1-design-philosophy)
