# Caching

The caching layer is a thin wrapper around an `aiohttp-client-cache` SQLite backend. It helps avoid redundant GET requests in bulk scripts by caching responses locally. The cache is scoped to a single driver instance and runs on the driver's dedicated event loop.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations such as `create`, `edit`, `delete`, and `publish` bypass the cache entirely.

---

## Default Configuration

```python
SQLiteBackend(
    cache_name="./cache/cache.sqlite",  # Path to the SQLite cache database file
    allowed_codes=(200,),               # Only cache successful HTTP 200 OK responses
    allowed_methods=("GET",),           # Enforce GET-only caching
)
```

---

## Custom Configuration

To override the default cache config, pass a `backendConfig` dictionary containing kwargs forwarded to `SQLiteBackend` when instantiating `CascadeCMSRestDriver`:

```python
driver = CascadeCMSRestDriver(
    apiKey="your-api-key",
    cascade_url="https://cascade.example.edu",
    backendConfig={
        "cache_name": "./custom_path/cache.sqlite",
        "allowed_codes": (200,),
        "allowed_methods": ("GET",),
    }
)
```

---

## Cache Scope & Lifetime

- The cache is scoped to a single driver/session instance and tied to its dedicated event loop, residing locally at `./cache/cache.sqlite` by default.
- Cache hits reduce latency and API calls within a session by short-circuiting repeated GET requests.
- To tear down the cache and close the underlying SQLite database connection, call `driver.close()`.

---

## When to Disable Caching

Caching should be bypassed or cleared when running scripts that require the absolute freshest asset state from Cascade CMS. It should also be avoided during active debugging sessions where stale cached responses might mask recent server-side updates, or when running high-frequency polling loops that need to verify real-time status changes.

<!-- synthesized-for: 3.1.6 -->
