---
layout: default
title: Installation
parent: Getting Started
nav_order: 1
---

# Installation

## Requirements

- Python 3.11 or higher (the library uses `Self`, `X | Y` unions, and `TypeAlias` from 3.11+)
- A Cascade CMS instance with REST API access
- A valid Cascade API key

## Install from PyPI

```bash
pip install cascade-cms
```

To include development dependencies (testing, linting, type checking):

```bash
pip install "cascade-cms[dev]"
```

## Verify the install

```python
from cascade_cms.wrapper import CascadeWrapperBase
from cascade_cms.cmstypes import IdentifierType, Asset
print("cascade_cms installed successfully")
```

## Dependencies

The library installs these automatically:

| Package | Purpose |
|---------|---------|
| `pydantic>=2` | Payload models, response parsing, serialization |
| `aiohttp-client-cache[sqlite]` | Async HTTP client with SQLite-backed GET cache |
| `python-dotenv` | Loading environment variables from `.env` files |

## Troubleshooting

**`ModuleNotFoundError: No module named 'cascade_cms'`**
Make sure you're running Python in the same environment where you installed the package. Check with `which python` and `pip list | grep cascade`.

**`aiohttp_client_cache` install fails**
The `[sqlite]` extra requires `aiosqlite`. If it doesn't install automatically:
```bash
pip install aiosqlite
```

**Python version mismatch**
Run `python --version`. If it shows 3.10 or lower, install 3.11+ and create a fresh virtual environment.

---

Next: [Quick Start](./quick-start/)
