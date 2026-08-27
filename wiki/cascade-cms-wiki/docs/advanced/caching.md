# Caching

The caching layer is a thin wrapper around an aiohttp-client-cache SQLite backend. It exists to avoid redundant GET requests in bulk scripts, skipping the network for repeated reads. The scope of the cache is tied to the driver instance and is not persistent across runs by default.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations like `create`, `edit`, `delete`, and `publish` are never cached.

---

## Default Configuration

```python
SQLiteBackend(
    cache_name="./cache/cache.sqlite",  # Path to the SQLite cache file
    allowed_codes=(200,),               # Only cache HTTP 200 responses
    allowed_methods=("GET",),           # Only cache GET requests
)
```

---

## Custom Configuration

```python
backendConfig = {
    "cache_name": "./custom_path/cache.sqlite",
    "allowed_codes": (200,),
    "allowed_methods": ("GET",),
}
driver = CascadeCMSRestDriver(
    apiKey="your-api-key",
    cascade_url="https://your-cascade-instance.com",
    backendConfig=backendConfig,
)
```

---

## Cache Scope & Lifetime

* **Driver-Scoped:** The cache is bound to a single driver instance and its dedicated event loop. It does not persist between separate script runs unless a persistent path is specified via `backendConfig`.
* **Reduced Latency:** Repeated GET requests within a session hit the local SQLite backend rather than the network, lowering API call volume.
* **Tear Down:** Calling `driver.close()` closes the underlying aiohttp session and the cache database cleanly.

---

## When to Disable Caching

Caching should be avoided or bypassed when running scripts that require the absolute freshest state of assets from the server, such as status-checking tools or interactive polling loops. If stale results are suspected during debugging, changing the cache configuration or clearing the underlying SQLite file ensures fresh network responses are fetched.

<!-- synthesized-for: 3.1.1 -->
