---
layout: default
title: Cascade CMS REST Client
nav_order: 1
---

# Cascade CMS REST Client

A typed, async REST client for Hannon Hill Cascade CMS. Write standalone Python scripts to read, create, edit, publish, and orchestrate assets — without hiding the REST API behind high-level abstractions.

[← Back to Documentation Hub](/)

## What this library is

A thin, explicit wrapper around the Cascade CMS REST API. It handles:

- HTTP transport (async, with connection reuse)
- Request serialization (Pydantic models → JSON)
- Response parsing (JSON → typed Python objects)
- Concurrency (semaphore-bounded, parallel execution)
- Caching (SQLite-backed GET cache)
- Logging (two modes: minimal console and verbose debug)

## What it is not

It is not an orchestration layer. It does not auto-publish after edits, auto-advance workflows, or make decisions about what to do with results. That logic belongs in your script, where it is visible and maintainable.

## Quick example

```python
import os
from uuid import UUID
from cascade_cms.cmstypes import Asset, IdentifierType
from cascade_cms.wrapper import CascadeWrapperBase

env = {
    "API_KEY": os.environ["CASCADE_API_KEY"],
    "CASCADE_URL": os.environ["CASCADE_URL"],
    "SERVER": "prod",
}
config = {
    "cache_name": "./cache/cache.sqlite",
    "allowed_codes": (200,),
    "allowed_methods": ("GET",),
}

with CascadeWrapperBase(env, config) as cascade:
    identifier = IdentifierType(
        identifier=UUID("e868f539ac1001062cfa029c4c5df4d0"),
        asset_type="page",
    )
    cascade.operations.read(identifier)
    results = cascade.submit_requests(Asset)
    print(results[0].get("name"))
```

## Navigate the docs

| Section | What you'll find |
|---------|-----------------|
| [Getting Started](./getting-started/) | Installation, auth setup, your first script |
| [Core Concepts](./core-concepts/) | Philosophy, identifiers, callbacks, caching, logging |
| [Operations Reference](./operations/all-operations/) | Every operation: signature, payload, response type |
| [Examples & Patterns](./examples/) | 11 runnable patterns showing library mechanics |
| [Logging & Debugging](./logging/) | Reading normal and debug mode output |
| [Advanced Topics](./advanced/concurrency-caching/) | Executors, caching internals, concurrency model |
| [Maintenance](./maintenance/) | Auto-update roadmap (planned) |

## Using AI to write scripts?

The [SKILL file](https://github.com/<your-org>/<your-repo>/tree/main/.skill) in the source repository powers AI-assisted script generation for this library. Load it into your preferred LLM to generate, validate, and iterate on scripts without writing from scratch.
