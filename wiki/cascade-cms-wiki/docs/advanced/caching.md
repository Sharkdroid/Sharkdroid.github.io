# Caching

The caching layer is a thin wrapper around an aiohttp-client-cache SQLite backend. It exists to avoid redundant GET requests during bulk operations and repeat script reads. The cache is scoped to the driver instance and uses an SQLite backing store.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations and non-GET requests are never cached.

---

## Default Configuration

```python
SQLiteBackend(
    cache_name="./cache/cache.sqlite", # Path to the SQLite cache file
    allowed_codes=(200,),              # Only cache successful 200 responses
    allowed_methods=("GET",),          # Only cache GET requests
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
    cascade_url="https://cascade.example.com",
    backendConfig=backendConfig
)
```

---

## Cache Scope & Lifetime

* The cache is scoped to a single `CascadeCMSRestDriver` instance and lives for the duration of that driver's session.
* Cache hits bypass the network, reducing latency and API overhead for repeat reads within the same execution run.
* Tearing down the driver via `driver.close()` closes the underlying SQLite connection, and cache lifetime is bounded by the cache file location (`./cache/cache.sqlite` by default).

---

## When to Disable Caching

You may want to avoid or bypass caching when your script relies on retrieving the absolute freshest state of rapidly changing assets. Caching should also be avoided during active debugging sessions where stale responses might mask recent modifications made directly inside the CMS.

<!-- synthesized-for: 3.1.5 -->
