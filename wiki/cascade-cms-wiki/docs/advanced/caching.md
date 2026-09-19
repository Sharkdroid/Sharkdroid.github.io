# Caching

The caching layer is a thin wrapper around an aiohttp-client-cache SQLite backend (`CacheHandler`). It exists to skip the network on repeated GET requests and avoid redundant calls in bulk scripts. The cache is scoped to a single driver instance and runs on its dedicated event loop.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations such as creates, edits, deletes, and publishes are never cached.

---

## Default Configuration

```python
SQLiteBackend(
    cache_name="./cache/cache.sqlite",  # Path to the SQLite cache database file
    allowed_codes=(200,),               # Only cache successful 200 responses
    allowed_methods=("GET",),           # Only cache GET read requests
)
```

---

## Custom Configuration

To override the default cache config, pass a `backendConfig` dictionary containing kwargs forwarded to `SQLiteBackend` when instantiating `CascadeCMSRestDriver`:

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

* The cache is scoped to a single driver session instance and shares the driver's lifetime and dedicated event loop.
* Cache hits reduce latency and API calls within a session by serving responses straight from the local SQLite database.
* The cache can be cleaned up or closed alongside the driver instance via `driver.close()`, which tears down the aiohttp session, cache DB, and event loop.

---

## When to Disable Caching

Caching should be disabled or bypassed when scripts require the absolute freshest state of assets from the server, such as during polling loops or when debugging stale results. Since POST and PUT requests always hit the server, mutating requests never serve stale data, but custom `backendConfig` settings or separate driver lifecycles can be used if read operations require real-time validation.

<!-- synthesized-for: 3.1.6 -->
