---
layout: default
title: Quick Start
parent: Getting Started
nav_order: 2
---

# Quick Start

## Set up your environment variables

The library requires three values at runtime:

| Variable | Description |
|----------|-------------|
| `CASCADE_API_KEY` | Your Cascade CMS API bearer token |
| `CASCADE_URL` | Base URL of your Cascade instance (no trailing slash) |
| `SERVER` | A short label for this server, used in log filenames (e.g. `prod`, `dev`) |

Create a `.env` file in your project directory:

```bash
CASCADE_API_KEY=your-api-key-here
CASCADE_URL=https://cascade.yourschool.edu
SERVER=prod
```

Then load it at the top of your script:

```python
from dotenv import load_dotenv
load_dotenv()
```

Or read directly from `os.environ` without `python-dotenv` if you set variables another way.

## Your first script

This reads a single Cascade asset and prints its name.

```python
import os
from uuid import UUID
from dotenv import load_dotenv
from cascade_cms.cmstypes import Asset, IdentifierType
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

identifier = IdentifierType(
    identifier=UUID("your-asset-uuid-here"),
    asset_type="page",
)

with CascadeWrapperBase(env, config) as cascade:
    cascade.operations.read(identifier)
    results = cascade.submit_requests(Asset)

asset = results[0]
print(asset.get("name"))
```

## What you should see in the console

```
[INIT]: Connecting to prod
[RUNNING]: your_script.py
Processed: 1/1
[DONE]: 1 assets processed in 0.3s
[EXIT]: Disconnecting from prod
```

A log file is also written to `./logs/prod_{timestamp}.log`.

## Finding your asset UUID

In the Cascade CMS web interface, open any asset and look at the URL:
```
https://cascade.yourschool.edu/entity/open.act?id=e868f539ac1001062cfa029c4c5df4d0&type=page
```

The `id` value is your UUID. The `type` value is your `asset_type`.

---

Next: [The Fluent Pattern](./fluent-pattern/)
