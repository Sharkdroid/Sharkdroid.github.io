# Caching

The caching layer is a thin wrapper around an aiohttp-client-cache SQLite backend. It exists to avoid redundant GET requests in bulk scripts by skipping the network on repeated reads while ensuring POST/PUT requests always hit the server. The cache operates at the per-driver-instance scope and uses a dedicated SQLite database.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations like create, edit, delete, and publish are never cached.

---

## Default Configuration

```python
SQLiteBackend(
    cache_name="./cache/cache.sqlite",
    allowed_codes=(200,),
    allowed_methods=("GET",),
)
```

The default cache backend is built to handle SQLite, GET-only requests, and 200 status codes only. It is constructed on demand rather than at module scope so that merely importing `cascade_cms` does not create a `./cache/` directory in the caller's working directory.

---

## Custom Configuration

```python
driver = CascadeCMSRestDriver(
    apiKey="your-api-key",
    cascade_url="https://cascade.example.com",
    backendConfig={
        "cache_name": "./custom_path/cache.sqlite",
        "allowed_codes": (200, 203),
        "allowed_methods": ("GET",),
    }
)
```

You can pass a custom `backendConfig` dictionary to `CascadeCMSRestDriver` containing kwargs forwarded to `SQLiteBackend` to override the default cache config, or pass `None` to use the default.

---

## Cache Scope & Lifetime

* The cache is scoped to a single driver instance and is tied to the lifecycle of that session and its SQLite database.
* Cache hits reduce latency and API calls within a session by short-circuiting repeated GET requests.
* You can tear down the cache DB and session by calling `close()` on the driver instance.

---

## When to Disable Caching

You should disable or bypass caching in scripts that require the absolute freshest state of assets from the server, such as polling loops or debugging scenarios where stale cached results might mask recent changes made outside the current session. Since caching applies exclusively to GET requests, you can also ensure fresh fetches by performing mutating operations or avoiding repeated identical reads.

<!-- synthesized-for: 3.1.3 -->
