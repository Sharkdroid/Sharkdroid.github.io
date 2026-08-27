# Caching

The caching layer is a thin wrapper around an aiohttp-client-cache SQLite backend. It exists to avoid redundant GET requests in bulk scripts, allowing repeated reads to skip the network while ensuring mutations always hit the server. The cache is scoped to a single driver instance and operates on a per-driver-instance basis.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. `create`, `edit`, `delete`, `publish`, and other mutating operations are never cached.

---

## Default Configuration

```python
SQLiteBackend(
    cache_name="./cache/cache.sqlite",
    allowed_codes=(200,),
    allowed_methods=("GET",),
)
```

---

## Custom Configuration

The cache is configurable via `backendConfig` at construction time, where kwargs are forwarded to `SQLiteBackend` to override the default cache config, or None to use the default.

---

## Cache Scope & Lifetime

- The cache is scoped to a single driver/session instance and does not persist across separate script runs unless explicitly configured via a persistent file path in `backendConfig`.
- Cache hits reduce latency and API calls within a session.
- You can tear down the cache DB and its underlying connections by calling the driver's `.close()` method.

---

## When to Disable Caching

Caching should be turned off when running scripts that need the absolute freshest asset state from the CMS, or when executing polling loops where stale results would cause issues. Disabling or bypassing the cache ensures every read operation queries the live server directly.

<!-- synthesized-for: 3.1.1 -->
