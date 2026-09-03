# Caching

The caching layer is a thin wrapper around an aiohttp-client-cache SQLite backend. It exists to avoid redundant GET requests in bulk scripts, skipping the network for repeated reads. The scope is tied to a single driver instance and is managed by the driver's event loop and cache handler.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations and non-GET requests are never cached.

---

## Default Configuration

```python
SQLiteBackend(
    cache_name="./cache/cache.sqlite",  # Default cache file path
    allowed_codes=(200,),               # Only cache successful 200 responses
    allowed_methods=("GET",),           # Only cache GET requests
)
```

---

## Custom Configuration

You can pass a custom `backendConfig` dictionary containing kwargs forwarded to `SQLiteBackend` to override the default cache config when initializing the driver:

```python
driver = CascadeCMSRestDriver(
    apiKey="your-api-key",
    cascade_url="https://cascade.example.com",
    backendConfig={
        "cache_name": "./custom_cache/cascade.sqlite",
        "allowed_codes": (200,),
        "allowed_methods": ("GET",),
    }
)
```

---

## Cache Scope & Lifetime

- The cache is scoped to a single driver/session instance and runs on the driver's dedicated event loop.
- Cache hits reduce latency and API calls within a session by short-circuiting repeated GET requests.
- You can tear down and close the cache database along with the session by calling the driver's `close()` method.

---

## When to Disable Caching

Caching should be disabled or bypassed when running scripts that require the absolute freshest asset state from the CMS. It is also recommended to turn off or clear caching during debugging sessions where stale cached results might mask recent server-side updates or changes made outside the current script execution.

<!-- synthesized-for: 3.1.3 -->
