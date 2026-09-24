# Caching

The caching layer is a thin wrapper around an `aiohttp-client-cache` SQLite backend. It helps avoid redundant GET requests in bulk scripts by caching responses on a per-driver-instance scope.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations such as create, edit, delete, and publish are never cached.

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

```python
driver = CascadeCMSRestDriver(
    apiKey="your_api_key",
    cascade_url="https://your-cms-instance",
    backendConfig={
        "cache_name": "./custom_path/my_cache.sqlite",
        "allowed_codes": (200,),
        "allowed_methods": ("GET",),
    }
)
```

---

## Cache Scope & Lifetime

* The cache is scoped to a single driver instance and is managed through the `CacheHandler` and `SQLiteBackend`.
* Cache hits reduce latency and API calls within a session by short-circuiting repeated GETs.
* The cache DB and session can be torn down by calling `driver.close()`.

---

## When to Disable Caching

Caching should be disabled or bypassed when scripts require the absolute freshest state of assets from the server, during active polling loops, or when debugging potential stale results. Since only GET requests are cached, operations that perform POST or PUT requests will naturally always hit the live server without needing configuration changes.

<!-- synthesized-for: 3.2.1 -->
