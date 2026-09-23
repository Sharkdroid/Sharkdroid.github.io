# Caching

The caching layer is a thin wrapper around an aiohttp-client-cache SQLite backend. It exists to avoid redundant GET requests in bulk scripts by skipping the network for repeated reads. The scope of the cache is tied to the driver instance and is not persistent across runs by default.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations like create, edit, delete, and publish never touch the cache.

---

## Default Configuration

```python
SQLiteBackend(
    cache_name="./cache/cache.sqlite",  # Location of the SQLite cache file
    allowed_codes=(200,),               # Only cache successful 200 OK responses
    allowed_methods=("GET",),           # Only cache GET read requests
)
```

---

## Custom Configuration

To override the default cache config, you can pass a `backendConfig` dictionary containing kwargs forwarded to `SQLiteBackend` when instantiating `CascadeCMSRestDriver`:

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

* **Driver-Instance Scoped:** The cache is bound to a single `CascadeCMSRestDriver` instance and does not persist between separate script runs unless configured with a persistent path.
* **Reduced Latency:** Cache hits skip the network entirely, reducing API round-trips and speeding up repeated read operations within a session.
* **Teardown:** Calling `driver.close()` ensures the underlying cache database connection is properly closed along with the session and event loop.

---

## When to Disable Caching

Caching should be bypassed or disabled when running scripts that require absolute real-time asset states or when debugging stale data returned from previous API calls. If you need fresh data without modifying your code's read operations, you can override or manage the cache configuration via `backendConfig` or ensure a clean execution context where cache hits are avoided.

<!-- synthesized-for: 3.1.6 -->
