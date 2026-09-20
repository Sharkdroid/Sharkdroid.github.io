# Caching

The caching layer is a thin wrapper around an aiohttp-client-cache SQLite backend. It exists to avoid redundant GET requests in bulk scripts by skipping the network on repeated reads. The cache is scoped to a single driver instance and is not persistent across runs by default.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations such as `create`, `edit`, `delete`, and `publish` perform non-GET requests and thus are never cached.

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
        "cache_name": "./custom_path/cache.sqlite",
        "allowed_codes": (200,),
        "allowed_methods": ("GET",),
    }
)
```

---

## Cache Scope & Lifetime

* **Driver Instance Scope:** The cache is tied to the lifecycle of the `CascadeCMSRestDriver` instance, utilizing a dedicated event loop and SQLite backend constructed on demand.
* **Latency and API Reduction:** Cache hits short-circuit repeated GET requests, reducing API call volume and latency within a session.
* **Tear-Down:** Calling `driver.close()` tears down the aiohttp session, cache DB, and event loop.

---

## When to Disable Caching

Caching should be disabled or bypassed when scripts require the absolute freshest asset state from the CMS or when debugging stale data issues. If you need to ensure that every read request hits the server to reflect concurrent external edits, you can configure the backend or override the cache settings accordingly.

<!-- synthesized-for: 3.1.6 -->
