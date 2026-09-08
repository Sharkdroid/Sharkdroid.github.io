# Caching

The caching layer is a thin wrapper around an aiohttp-client-cache SQLite backend. It exists to avoid redundant GET requests in bulk scripts, skipping the network for repeated reads. The cache is scoped to a single driver instance and is not persistent across separate script runs by default.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations such as `create`, `edit`, `delete`, and `publish` are never cached.

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

To override the default cache config, pass `backendConfig` as keyword arguments forwarded to `SQLiteBackend` when instantiating `CascadeCMSRestDriver`:

```python
driver = CascadeCMSRestDriver(
    apiKey="your-api-key",
    cascade_url="https://cascade.example.com",
    backendConfig={
        "cache_name": "./custom_cache/cache.sqlite",
        "allowed_codes": (200, 201),
        "allowed_methods": ("GET",),
    }
)
```

---

## Cache Scope & Lifetime

* **Driver Instance Scope:** The cache is tied to the lifecycle of the `CascadeCMSRestDriver` instance and its underlying event loop/session.
* **Latency & API Calls:** Cache hits read from the SQLite database (`./cache/cache.sqlite` by default), reducing latency and API calls within a single session.
* **Cleanup:** The cache database and session are torn down when `driver.close()` is called.

---

## When to Disable Caching

You should disable or bypass caching when working with scripts that require the absolute freshest asset state from the CMS, or when executing polling loops where data changes frequently between checks. Caching can also lead to stale results during debugging if you are actively modifying assets and expecting immediate reflection in subsequent GET requests without a cache expiration or custom backend config.

<!-- synthesized-for: 3.1.3 -->
