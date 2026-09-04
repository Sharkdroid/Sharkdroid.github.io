# Caching

The caching layer is a thin wrapper around an aiohttp-client-cache SQLite backend (`CacheHandler`). It exists to skip the network on repeated reads and avoid redundant GET requests in bulk scripts. Caching is scoped to a single driver instance and is not persistent across runs by default.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations such as `create`, `edit`, `delete`, and `publish` are never cached.

---

## Default Configuration

```python
SQLiteBackend(
    cache_name="./cache/cache.sqlite",  # Path to the SQLite cache database
    allowed_codes=(200,),               # Only successful 200 OK responses are cached
    allowed_methods=("GET",),           # Only GET requests are cached
)
```

---

## Custom Configuration

To override the default cache config, pass a `backendConfig` dictionary containing kwargs forwarded to `SQLiteBackend` when instantiating `CascadeCMSRestDriver`:

```python
driver = CascadeCMSRestDriver(
    apiKey="your-api-key",
    cascade_url="https://cascade.example.edu",
    backendConfig={
        "cache_name": "./custom_path/my_cache.sqlite",
        "allowed_codes": (200,),
        "allowed_methods": ("GET",),
    }
)
```

---

## Cache Scope & Lifetime

- **Driver-Scoped:** The cache is bound to a single `CascadeCMSRestDriver` instance and its underlying SQLite backend database.
- **Lifetime:** By default, it uses `./cache/cache.sqlite` on disk, but does not automatically clear itself between separate script runs unless deleted or explicitly managed.
- **Performance:** Cache hits skip the network entirely, reducing latency and API overhead within a session.
- **Teardown:** Calling `driver.close()` tears down the cache DB along with the aiohttp session and event loop.

---

## When to Disable Caching

Caching should be disabled or bypassed when running scripts that require the absolute freshest asset state from the CMS, or when executing polling loops where data changes frequently between checks. If you need to debug potential stale results or verify server-side changes, using a fresh driver instance or clearing the SQLite cache backend ensures all requests hit the server directly.

<!-- synthesized-for: 3.1.3 -->
