# Caching

The caching layer is built as a thin wrapper around an `aiohttp-client-cache` SQLite backend. It exists to avoid redundant GET requests in bulk scripts by skipping the network on repeated reads while ensuring POST/PUT requests always hit the server. The cache is scoped to a single driver instance and does not persist across separate runs unless a specific persistent cache path is configured.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations such as creates, edits, deletes, and publishes are never cached.

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

To override the default cache settings, you can pass a custom `backendConfig` dictionary to `CascadeCMSRestDriver` (which forwards these kwargs to `SQLiteBackend`):

```python
driver = CascadeCMSRestDriver(
    apiKey="your-api-key",
    cascade_url="https://cascade.example.com",
    backendConfig={
        "cache_name": "./custom_path/my_cache.sqlite",
        "allowed_codes": (200, 201),
        "allowed_methods": ("GET",),
    }
)
```

---

## Cache Scope & Lifetime

- The cache is scoped to a single driver/session instance and uses a dedicated event loop created for the driver's lifetime.
- Cache hits reduce latency and API calls within a session by storing and returning previously fetched responses.
- You can tear down the underlying SQLite cache database and close the session by calling `driver.close()`.

---

## When to Disable Caching

You should disable or bypass caching in scenarios where scripts require the freshest possible asset state from the server, such as in active development, polling loops, or when debugging stale results. Because caching is enabled by default for GET requests, scripts that perform rapid iterations on content modification and verification may benefit from a fresh cache-free session or a custom non-persistent or memory-backed configuration.

<!-- synthesized-for: 3.1.3 -->
