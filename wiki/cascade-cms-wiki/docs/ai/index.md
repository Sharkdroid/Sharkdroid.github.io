# AI & Automation

Workflows for maintaining the library and using AI-assisted tooling with
Cascade CMS.

---

## Library maintenance

Development, testing, and release workflow for `cascade-cms-rest`.

**[Library Maintenance](./library-maintenance.md)** covers:

- Setting up the development environment
- Running lint, type checks, and tests
- Releasing a new version to PyPI
- Maintaining the CHANGELOG
- Workflow for code agents working on this repo

---

## Automation tools

The [cascade-cms-tools](https://github.com/Sharkdroid/cascade-cms-tools)
repository provides two tools built on top of this library:

- **MCP Server** (`cascade-cms-rest-mcp`) — read-only Cascade CMS access
  via Model Context Protocol, for use with Claude Desktop and Claude Code
- **Claude Code Skill** (`cascade-script-writer`) — script generation and
  validation for this library in Claude Code

Full documentation for both tools is in the
**[cascade-cms-tools wiki](https://sharkdroid.github.io/wiki/cascade-cms-tools-wiki/)**.
