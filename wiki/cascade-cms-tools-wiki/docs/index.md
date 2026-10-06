# cascade-cms-tools

Automation tools for
[`cascade-cms-rest`](https://github.com/Sharkdroid/py-cascade-cms) —
a typed async Python REST client for Hannon Hill Cascade CMS.

The repository holds two independent tools. Both build on the **published**
`cascade-cms-rest` package from PyPI rather than bundling a copy, and
neither needs the other at runtime.

---

## MCP Server

`cascade-cms-rest-mcp` is a local, read-only
[Model Context Protocol](https://modelcontextprotocol.io/) server. It lets
MCP clients such as Claude Desktop and Claude Code inspect a Cascade CMS
server.

Install:

```bash
pip install cascade-cms-rest-mcp
```

Set the environment variables the server needs:

```bash
export CASCADE_API_KEY="your-api-key"
export CASCADE_URL="https://your-cascade-instance.com"
```

Then point your MCP client at the server. The
[repository README](https://github.com/Sharkdroid/cascade-cms-tools#how-to-use)
has the client configuration details.

**Security**: the server is read-only. `user`, `group`, `role`, and `message`
assets are blocked regardless of the API key's permissions.

---

## Claude Code Skill

`cascade-script-writer` is a Claude Code skill that writes and validates
Python scripts built on `cascade-cms-rest`.

Download the latest `cascade-cms-tools-skill-<version>.zip` from
[Releases](https://github.com/Sharkdroid/cascade-cms-tools/releases), unpack
it, and copy the `cascade-script-writer/` folder into your Claude Code
skills folder.

The skill provides:

- Script templates for common Cascade CMS workflows
- A validator that checks generated scripts against the bundled library source
- A session log that records the agent's reasoning and MCP interactions

The [repository README](https://github.com/Sharkdroid/cascade-cms-tools#how-to-use)
covers install locations per client.

---

## When to use each tool

| Task | Tool |
|---|---|
| Explore asset schemas interactively | MCP server |
| Verify a field path exists before scripting | MCP server |
| Generate a bulk operation script | Claude Code skill |
| Automate a multi-step Cascade workflow | Claude Code skill |
| One-off read or inspection | Library directly |

---

## Further reading

- **Setup**: [repository README](https://github.com/Sharkdroid/cascade-cms-tools)
- **MCP tools**: [MCP Server Reference](./mcp-reference.md)
- **Skill workflow**: [Skill Overview](./skill-overview.md)
- **Development**: [Maintenance](./maintenance.md)
- **Library docs**: [py-cascade-cms wiki](https://sharkdroid.github.io/wiki/cascade-cms-wiki/)
