# Caching

The caching layer is a thin wrapper around an aiohttp-client-cache SQLite backend. It exists to avoid redundant GET requests in bulk scripts, skipping the network for repeated reads. The cache is scoped to a single driver instance and is not persistent across runs by default.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations like `create`, `edit`, `delete`, and `publish` are never cached.

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

```python
driver = CascadeCMSRestDriver(
    apiKey="your-api-key",
    cascade_url="https://cascade.example.edu",
    backendConfig={
        "cache_name": "./custom_cache/cache.sqlite",
        "allowed_codes": (200,),
        "allowed_methods": ("GET",),
    }
)
```

---

## Cache Scope & Lifetime

* **Driver-Scoped:** The cache is bound to a single driver and session instance, constructed via `SQLiteBackend` or the default backend on demand.
* **Reduction of API Calls:** Cache hits short-circuit repeated GETs, returning cached responses directly and skipping network I/O.
* **Tear Down:** Calling `close()` on the driver tears down the cache DB along with the aiohttp session and event loop.

---

## When to Disable Caching

Caching should be turned off or bypassed when scripts need to retrieve the freshest asset state from the server after recent modifications. It should also be avoided in polling loops or when debugging stale results where fresh network data is required for every request.

<!-- synthesized-for: 3.1.1 -->
