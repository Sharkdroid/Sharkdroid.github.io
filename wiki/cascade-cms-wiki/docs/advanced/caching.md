# Caching

The caching layer is a thin wrapper around an `aiohttp-client-cache` SQLite backend. It exists to avoid redundant GET requests in bulk scripts, skipping the network on repeated reads while ensuring POST/PUT requests always hit the server. The cache scope is tied to a single driver instance and is not persistent across runs by default.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations such as `create`, `edit`, `delete`, and `publish` are never cached.

---

## Default Configuration

```python
SQLiteBackend(
    cache_name="./cache/cache.sqlite",  # Path to SQLite cache database file
    allowed_codes=(200,),               # Only cache successful 200 responses
    allowed_methods=("GET",),           # Only cache GET requests
)
```

---

## Custom Configuration

You can pass a custom `backendConfig` dictionary containing kwargs forwarded to `SQLiteBackend` to override the default cache config when initializing `CascadeCMSRestDriver`:

```python
driver = CascadeCMSRestDriver(
    apiKey="your-api-key",
    cascade_url="https://cascade.example.com",
    backendConfig={
        "cache_name": "./custom_path/my_cache.sqlite",
        "allowed_codes": (200,),
        "allowed_methods": ("GET",),
    }
)
```

---

## Cache Scope & Lifetime

- The cache is scoped to a single driver/session instance and is stored in a SQLite database (defaulting to `./cache/cache.sqlite`). It does not persist or clear automatically between separate script runs unless managed by the underlying file system.
- Cache hits reduce latency and API calls within a session by reading raw data directly from the SQLite backend.
- You can tear down or close the cache DB alongside the session and event loop by calling `driver.close()`.

---

## When to Disable Caching

Caching should be bypassed or disabled in scripts that require absolute real-time asset states, such as polling loops waiting for asynchronous publishing or workflow completions. Running scripts against rapidly changing environments where stale results would cause data conflicts or validation failures may also benefit from avoiding cached GET responses.

<!-- synthesized-for: 3.1.5 -->
