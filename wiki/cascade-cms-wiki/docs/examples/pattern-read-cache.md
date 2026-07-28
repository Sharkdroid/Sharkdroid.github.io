---
layout: default
title: Cache Behavior
parent: Examples & Patterns
nav_order: 2
---

# Cache behavior

GET responses are cached automatically in a local SQLite database. This example reads the same asset twice to demonstrate the cache hit, and shows how to configure or disable caching.

## Default: automatic GET caching

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

ref = IdentifierType(
    identifier=UUID("8b320f55ac1001062545a6d2562cee4b"),
    asset_type="page",
)

with CascadeWrapperBase(env, config) as cascade:
    # First read: hits the network
    cascade.operations.read(ref)
    first = cascade.submit_requests(Asset)

    # Second read: served from SQLite cache, no HTTP request
    cascade.operations.read(ref)
    second = cascade.submit_requests(Asset)

print(first[0].get("name") == second[0].get("name"))  # True
```

The cache is keyed on `(method, url)`. POST and PUT requests bypass it entirely — only GET is ever cached.

## Observing cache hits in debug mode

Enable debug logging to see exactly when the cache is used:

```python
debug_config = {
    "log_dir": "./logs",
    "log_operations": True,
    "log_callbacks": True,
    "log_responses": True,
    "show_payload_data": True,
    "show_network_headers": True,  # shows whether request was cached
    "show_error_variables": True,
    "response_line_limit": 8,
}

with CascadeWrapperBase(env, config, debug=debug_config) as cascade:
    cascade.operations.read(ref)
    cascade.submit_requests(Asset)
    # First run: [URL], [response] block appears in logfile

    cascade.operations.read(ref)
    cascade.submit_requests(Asset)
    # Second run: same [URL], no HTTP round-trip logged
```

## Configuring caching

The `config` dict is forwarded directly to `aiohttp-client-cache`'s `SQLiteBackend`. All its kwargs are available.

### Disable caching entirely

Set `allowed_methods` to an empty tuple. No responses will be stored or served from cache.

```python
config = {
    "cache_name": "./cache/cache.sqlite",
    "allowed_codes": (200,),
    "allowed_methods": (),  # nothing is cached
}
```

Use this when you always need fresh data — for example, a script that reads workflow state before taking action.

### Time-limited cache (TTL)

Set `expire_after` in seconds. Cached responses older than this are treated as misses.

```python
config = {
    "cache_name": "./cache/cache.sqlite",
    "allowed_codes": (200,),
    "allowed_methods": ("GET",),
    "expire_after": 300,  # cache valid for 5 minutes
}
```

Useful for long-running scripts that might re-read the same assets but want to see updates after a delay.

### Custom cache location

```python
config = {
    "cache_name": "/tmp/cascade_cache.sqlite",  # ephemeral, cleared on reboot
    "allowed_codes": (200,),
    "allowed_methods": ("GET",),
}
```

### Use the library default without specifying config

Pass `None` as `configuration_variables` to use the built-in default (`./cache/cache.sqlite`, GET only, all 200s cached indefinitely):

```python
with CascadeWrapperBase(env, None) as cascade:
    ...
```

---

See also: [Concurrency & Caching](../advanced/concurrency-caching.md) for internals · [Core Concepts: Caching](../core-concepts/index.md#8-caching)
