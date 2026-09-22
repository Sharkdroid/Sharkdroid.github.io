# Caching

The caching layer is built as a thin wrapper around an `aiohttp-client-cache` SQLite backend. It exists to avoid redundant GET requests in bulk scripts, skipping the network on repeated reads while ensuring write operations always reach the server. Caching is scoped per driver instance and is managed through the driver's lifecycle.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations such as `create`, `edit`, `delete`, and `publish` bypass the cache completely.

---

## Default Configuration

```python
SQLiteBackend(
    cache_name="./cache/cache.sqlite",  # Path to the local SQLite cache database file
    allowed_codes=(200,),               # Only cache successful HTTP 200 responses
    allowed_methods=("GET",),           # Only cache GET read requests
)
```

---

## Custom Configuration

To change the cache location, expiration, or other SQLite settings, pass a custom `backendConfig` dictionary to `CascadeCMSRestDriver`:

```python
backendConfig = {
    "cache_name": "./custom_path/my_cache.sqlite",
    "allowed_codes": (200,),
    "allowed_methods": ("GET",),
}

driver = CascadeCMSRestDriver(
    apiKey="your-api-key",
    cascade_url="https://cascade.yourdomain.edu",
    backendConfig=backendConfig
)
```

---

## Cache Scope & Lifetime

* The cache is scoped to a single driver instance and does not persist across separate script runs unless explicitly configured to use a persistent path.
* Cache hits reduce latency and API calls within a session by serving responses directly from the local SQLite database.
* The cache database can be closed and torn down along with the driver instance by calling the driver's `close()` method.

---

## When to Disable Caching

Caching should be turned off or bypassed when running scripts that require the absolute freshest asset state from the CMS, during active content polling loops, or when debugging potential stale results. Since POST and PUT requests always hit the server, mutating operations do not need cache bypassing, but read-heavy scripts checking for real-time updates may benefit from a custom ephemeral or disabled configuration.

<!-- synthesized-for: 3.1.6 -->
