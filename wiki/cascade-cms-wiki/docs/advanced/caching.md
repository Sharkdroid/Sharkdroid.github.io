# Caching

The caching layer is a thin wrapper around an `aiohttp-client-cache` SQLite backend. It exists to avoid redundant GET requests in bulk scripts, skipping the network for repeated reads while ensuring POST/PUT requests always hit the server. The cache operates within the scope of a single driver instance and is not persistent across runs by default.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations such as creates, edits, deletes, and publishes are never cached.

---

## Default Configuration

```python
SQLiteBackend(
    cache_name="./cache/cache.sqlite",  # Path to the SQLite cache file
    allowed_codes=(200,),               # Only cache successful HTTP 200 responses
    allowed_methods=("GET",),           # Only cache GET requests
)
```

---

## Custom Configuration

To customize the cache location, expiration, or other SQLite settings, pass a `backendConfig` dictionary to the driver:

```python
driver = CascadeCMSRestDriver(
    apiKey="your-api-key",
    cascade_url="https://your-cascade-instance",
    backendConfig={
        "cache_name": "./custom_path/cache.sqlite",
        "allowed_codes": (200,),
        "allowed_methods": ("GET",),
    }
)
```

---

## Cache Scope & Lifetime

* **Driver-Scoped Lifetime:** The cache is scoped to a single driver instance and tied to its dedicated event loop and session. It is cleaned up when `driver.close()` is called.
* **Reduced Latency:** Cache hits completely bypass the network, returning previously fetched assets, lists, or results instantly within the same session.
* **Clearing and Teardown:** The cache database and underlying session can be torn down by calling `driver.close()`.

---

## When to Disable Caching

Caching should be bypassed or disabled when running scripts that require the absolute freshest state of assets from the server, during active content polling loops, or when debugging stale results where cached response data might mask recent changes made in Cascade CMS.

<!-- synthesized-for: 3.1.3 -->
