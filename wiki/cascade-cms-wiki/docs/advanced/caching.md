# Caching

The caching layer is a thin wrapper around an aiohttp-client-cache SQLite backend (`CacheHandler`). It exists to avoid redundant GET requests in bulk scripts, skipping the network for repeated reads while ensuring write operations always hit the server. The cache is scoped to a single driver instance and is not persistent across separate runs by default.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations like `create`, `edit`, `delete`, and `publish` never use cached responses.

---

## Default Configuration

```python
SQLiteBackend(
    cache_name="./cache/cache.sqlite",  # Path to SQLite cache file
    allowed_codes=(200,),               # Only cache successful 200 OK responses
    allowed_methods=("GET",),           # Only cache GET requests
)
```

---

## Custom Configuration

You can pass a custom `backendConfig` dictionary to `CascadeCMSRestDriver` (which forwards kwargs to `SQLiteBackend`) to override the default cache config, or None to use the default.

```python
driver = CascadeCMSRestDriver(
    apiKey="your-api-key",
    cascade_url="https://cascade.example.com",
    backendConfig={"cache_name": "./custom_cache/my_cache.sqlite", "allowed_codes": (200,)}
)
```

---

## Cache Scope & Lifetime

* The cache is scoped to a single driver/client instance, utilizing a dedicated event loop and SQLite backend that are torn down when `.close()` is called.
* Cache hits reduce latency and API calls within a session by reading raw data straight from the SQLite backend and parsing it.
* You can tear down or close the underlying cache database alongside the driver session using the `close()` method.

---

## When to Disable Caching

Caching should be avoided or cleared when writing scripts that require the absolute freshest asset state from the server. It should also be skipped in polling loops where entity changes must be detected immediately without serving outdated cached responses.

<!-- synthesized-for: 3.1.5 -->
