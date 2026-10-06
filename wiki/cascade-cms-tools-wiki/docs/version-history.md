<!-- handwritten — not tracked by docs automation. Update manually when
     breaking changes ship to either the MCP server or the skill.
     Remove this file if it becomes stale. -->

# Version History

Notable changes to `cascade-cms-rest-mcp` and `cascade-script-writer`.
Both tools share a version tag.

For the complete changelog, see
[Releases](https://github.com/Sharkdroid/cascade-cms-tools/releases).

---

## 0.4.8 (current)

- Updated to track `cascade-cms-rest` 3.9.1 (`Cascade` class rename,
  3.8.2 tuple path breaking change, `ChainResults` result API).
- Templates updated for 3.9.1 API patterns.

## 0.4.7

- **Skill**: Step 0 mandatory session logging added. Every invocation
  must create a timestamped log at
  `reports/cascade-script-YYYYMMDD-HHMMSS.txt`.
- Updated to track `cascade-cms-rest` 3.8.3 (identifiers module,
  expanded error handling).

## 0.4.0

- Skill build 041 merged with MCP server into unified version tag.
- Metadata field fix in skill templates.
- MCP live-verify step added to field placement workflow.

## 0.2.6

- MCP server and skill migrated to `cascade-cms-rest` 3.4.0.
- Templates updated to use `script_log.note()` and `[RESULT]` lines.
- Error handling aligned with `ChainResults` design.

## 0.2.0

- Initial public release of MCP server and Claude Code skill.
