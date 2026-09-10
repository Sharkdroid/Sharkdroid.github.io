# Caching

The caching layer is a thin wrapper around an `aiohttp-client-cache` SQLite backend. It exists to avoid redundant GET requests in bulk scripts, skipping the network for repeated reads while allowing POST/PUT requests to always hit the server. The cache has a per-driver-instance scope and is managed via the `CacheHandler` and `CascadeCMSRestDriver`.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server.

---

## Default Configuration

```python
def default_cache_backend() -> SQLiteBackend:
    """Build the default cache backend: SQLite, GET-only, 200s only.
    Constructed on demand rather than at module scope so that merely
    importing `cascade_cms` does not create a `./cache/` directory in the
    caller's working directory.
    """
    return SQLiteBackend(
        cache_name="./cache/cache.sqlite",
        allowed_codes=(200,),
        allowed_methods=("GET",),
    )
```

---

## Custom Configuration

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

- The cache is scoped to a single driver instance and tied to its dedicated event loop and SQLite backend configuration.
- Cache hits bypass network round-trips for GET requests, significantly reducing latency and API overhead within a single session.
- You can tear down or close the cache along with the driver session by calling `driver.close()`, which closes the underlying SQLite backend connection.

---

## When to Disable Caching

Caching should be bypassed or cleared when writing scripts that require the absolute freshest state of assets in Cascade CMS, such as rapid verification loops right after a write or publish operation. Relying on cached GET responses during active concurrent mutations can lead to reading stale data until the cache expires or is re-initialized.

<!-- synthesized-for: 3.1.3 -->
