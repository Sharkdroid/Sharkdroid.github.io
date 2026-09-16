# Caching

The caching layer is a thin wrapper around an `aiohttp-client-cache` SQLite backend. It exists to avoid redundant GET requests in bulk scripts, skipping the network for repeated reads. The cache is scoped to a single driver instance and is not persistent across runs by default.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations such as `create`, `edit`, `delete`, `publish`, and others are never cached.

---

## Default Configuration

```python
SQLiteBackend(
    cache_name="./cache/cache.sqlite",  # Path to the SQLite cache database
    allowed_codes=(200,),               # Only HTTP 200 responses are cached
    allowed_methods=("GET",),           # Only GET requests are cached
)
```

---

## Custom Configuration

To override the default cache config, you can pass a `backendConfig` dictionary (containing keyword arguments forwarded to `SQLiteBackend`) when initializing `CascadeCMSRestDriver`:

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

* **Driver-Scoped:** The cache is bound to a single `CascadeCMSRestDriver` instance and its associated event loop and session. It does not automatically clean up or persist across separate script executions unless configured with a persistent path.
* **Performance:** Cache hits dramatically reduce latency and API calls within a session by serving responses directly from the local SQLite database.
* **Teardown:** When the driver's `close()` method is called, the underlying cache DB and session are properly torn down.

---

## When to Disable Caching

Caching should be bypassed or disabled when running scripts that require the absolute freshest state of assets in Cascade CMS, such as polling loops or debugging stale results. In these scenarios, configuring the driver or bypassing the cached path ensures all requests hit the live server directly.

<!-- synthesized-for: 3.1.5 -->
