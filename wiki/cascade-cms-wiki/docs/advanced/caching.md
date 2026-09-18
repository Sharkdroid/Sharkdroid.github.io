# Caching

The caching layer is built as a thin wrapper around an aiohttp-client-cache SQLite backend (`CacheHandler`). It exists to skip the network on repeated reads and avoid redundant GET requests in bulk scripts. The cache is scoped per driver instance and is tied to the driver's session and event loop.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations like create, edit, delete, and publish never touch the cache.

---

## Default Configuration

```python
SQLiteBackend(
    cache_name="./cache/cache.sqlite",  # Path to the SQLite cache file
    allowed_codes=(200,),               # Only cache successful 200 OK responses
    allowed_methods=("GET",),           # Enforce GET-only caching
)
```

---

## Custom Configuration

To override the default cache settings, you can pass a custom `backendConfig` dictionary (containing keyword arguments forwarded to `SQLiteBackend`) when instantiating the driver:

```python
driver = CascadeCMSRestDriver(
    apiKey="your-api-key",
    cascade_url="https://cascade.example.edu",
    backendConfig={
        "cache_name": "./custom_path/cache.sqlite",
        "allowed_methods": ("GET",),
    }
)
```

---

## Cache Scope & Lifetime

* **Instance Scoped:** The cache is bound to a single driver instance and its dedicated event loop. It does not automatically share state across separate script runs unless pointing to a persistent SQLite path.
* **Reduced Latency:** Cache hits short-circuit the network entirely, reducing latency and API usage within a session.
* **Tear Down:** Closing the driver via `driver.close()` also cleanly closes the underlying cache database connection.

---

## When to Disable Caching

Caching should be bypassed or disabled in scripts that require real-time accuracy where asset modifications made outside the script must be visible immediately. Similarly, scripts running continuous polling loops or those troubleshooting stale state issues should ensure they do not rely on cached GET responses.

<!-- synthesized-for: 3.1.6 -->
