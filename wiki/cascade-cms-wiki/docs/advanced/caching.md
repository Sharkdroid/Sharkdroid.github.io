# Caching

The caching layer is a thin wrapper around an aiohttp-client-cache SQLite backend. It exists to avoid redundant GET requests in bulk scripts by skipping the network on repeated reads. The cache is scoped to the driver instance and is managed by `CacheHandler`.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations such as `create`, `edit`, `delete`, and `publish` bypass the cache completely.

---

## Default Configuration

```python
SQLiteBackend(
    cache_name="./cache/cache.sqlite",
    allowed_codes=(200,),
    allowed_methods=("GET",),
)
```

The default cache backend uses SQLite, caches GET requests only, and caches only 200 responses.

---

## Custom Configuration

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

You can pass a custom `backendConfig` dictionary to `CascadeCMSRestDriver` to forward kwargs to `SQLiteBackend` and override the default cache config.

---

## Cache Scope & Lifetime

* The cache is scoped to a single driver instance and is tied to its event loop, session, and SQLite backend.
* Cache hits reduce latency and API calls within a session by short-circuiting repeated GETs through `CacheHandler.get_response`.
* You can tear down the cache DB and its session by calling `driver.close()`.

---

## When to Disable Caching

You should disable or bypass caching in scripts that require real-time, freshest-state asset retrieval where stale data from a previous run or earlier in the script is unacceptable. Polling loops or debugging sessions investigating intermittent server responses also benefit from running without cache assistance.

<!-- synthesized-for: 3.1.1 -->
