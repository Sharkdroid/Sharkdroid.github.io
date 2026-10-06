# Skill Overview

`cascade-script-writer` is a Claude Code skill for generating and validating
Python scripts that use `cascade-cms-rest`. It is designed for agentic
workflows in Claude Code, not chat-only use: the agent needs read and write
access to the directory where the script runs. It earns its keep on
multi-step business logic such as create-then-edit pipelines, batch
processing with callbacks, and workflow orchestration. For a simple one-off
script, writing directly against the library is often the better choice.

The core workflow runs in a fixed order. The agent breaks the request down
into operations, targets, and data sources, then picks the matching template
from `templates/INDEX.md` rather than writing from scratch. It then looks up
exact payload names and aliases in the bundled schema and in
`references/asset_api.md`. Before a script writes any field, the field's
path is confirmed on a real asset, using the MCP server when it is connected,
because Cascade silently ignores fields it does not recognise. Only then is
the script edited, validated, and presented. Scripts that write are delivered
and verified in stages.

Every invocation starts with Step 0, a session log. The agent creates a new
timestamped file, `reports/cascade-script-YYYYMMDD-HHMMSS.txt`, and fills in
the header with the task quoted verbatim. It then appends each section as the
matching step finishes, so an interrupted session still leaves a partial
record. The sections cover the task breakdown, references read, MCP tool
calls, template selected, design decisions, validation runs, staged writes,
and what was delivered. The log is the agent's own working record, separate
from the runtime log the library writes.

A script is complete only when `validate_script.py` exits 0. The validator
checks the script against the bundled library source and enforces four
rules: `Cascade` is the only entry point, `Asset` fields are set by
attribute, everything is type-hinted, and no line exceeds 60 characters.
The 60-character limit is a hard requirement. Format with
`ruff format --line-length 60 --isolated` before validating, and wrap by hand
only the lines the validator still reports.

For the full rules and workflow, see
[`AGENTS.md`](https://github.com/Sharkdroid/cascade-cms-tools/blob/master/AGENTS.md)
and the skill's
[`references/`](https://github.com/Sharkdroid/cascade-cms-tools/tree/master/skill/cascade-script-writer/references)
folder.
