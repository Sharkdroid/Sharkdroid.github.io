# Caching

The caching layer is a thin wrapper around an `aiohttp-client-cache` SQLite backend. It exists to avoid redundant GET requests in bulk scripts by short-circuiting repeated reads and skipping the network. The cache scope is tied to a single driver instance and its lifetime, rather than persisting globally.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations such as create, edit, delete, and publish are never cached.

---

## Default Configuration

```python
SQLiteBackend(
    cache_name="./cache/cache.sqlite",  # Path to the SQLite database file
    allowed_codes=(200,),              # Only cache successful 200 responses
    allowed_methods=("GET",),          # Only cache GET read requests
)
```

---

## Custom Configuration

To override the default cache config, pass a `backendConfig` dictionary containing kwargs forwarded to `SQLiteBackend` when instantiating `CascadeCMSRestDriver`:

```python
driver = CascadeCMSRestDriver(
    apiKey="your-api-key",
    cascade_url="https://cascade.institution.edu",
    backendConfig={
        "cache_name": "./custom_path/cache.sqlite",
        "allowed_codes": (200,),
        "allowed_methods": ("GET",),
    }
)
```

---

## Cache Scope & Lifetime

* The cache is scoped to a single driver/session instance and is maintained via a `CacheHandler` wrapping the underlying SQLite backend.
* Cache hits reduce latency and API calls within a session by reading from the SQLite backend instead of hitting the network.
* You can tear down or close the cache DB along with the driver session by calling `driver.close()`.

---

## When to Disable Caching

You should disable or bypass caching when your script requires the absolute freshest asset state from the server, when running real-time polling loops, or when you are actively debugging stale results. Because caching is enabled by default for all GET requests, supplying custom configuration or overriding methods may be necessary in high-frequency update workflows.

<!-- synthesized-for: 3.1.3 -->
