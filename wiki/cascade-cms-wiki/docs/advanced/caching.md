# Caching

The caching layer is a thin wrapper around an aiohttp-client-cache SQLite backend. It exists to avoid redundant GET requests in bulk scripts by skipping the network on repeated reads. The cache is scoped per driver instance and is tied to the driver's lifetime.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations such as creates, edits, deletes, and publishes are never cached.

---

## Default Configuration

```python
SQLiteBackend(
    cache_name="./cache/cache.sqlite",  # Path to the SQLite cache file
    allowed_codes=(200,),               # Only cache successful 200 responses
    allowed_methods=("GET",),           # Only cache GET requests
)
```

---

## Custom Configuration

To override the default cache config, you can pass kwargs forwarded to `SQLiteBackend` via the `backendConfig` parameter when instantiating `CascadeCMSRestDriver`:

```python
driver = CascadeCMSRestDriver(
    apiKey="your-api-key",
    cascade_url="https://cascade.example.com",
    backendConfig={
        "cache_name": "./custom_path/cache.sqlite",
        "allowed_codes": (200,),
        "allowed_methods": ("GET",),
    }
)
```

---

## Cache Scope & Lifetime

- The cache is scoped to a single driver instance and operates on a dedicated event loop created for that session.
- Cache hits reduce latency and API calls within a session by short-circuiting repeated GET requests.
- The cache can be cleaned up or torn down alongside the driver via the `close()` method, which closes the underlying cache database.

---

## When to Disable Caching

Caching should be turned off when running scripts that require the absolute freshest asset state from the server. It should also be avoided in polling loops or when debugging stale results where you need to guarantee every read hits the live server.

<!-- synthesized-for: 3.1.3 -->
