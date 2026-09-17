# Caching

The caching layer is a thin wrapper around an aiohttp-client-cache SQLite backend. It exists to avoid redundant GET requests in bulk scripts by skipping the network for repeated reads. The cache is scoped to a single driver instance and is stored in a SQLite database.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations such as creates, updates, and publishes are never cached.

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

To override the default cache config, pass a `backendConfig` dictionary (containing keyword arguments forwarded to `SQLiteBackend`) when initializing the `CascadeCMSRestDriver`:

```python
driver = CascadeCMSRestDriver(
    apiKey="your-api-key",
    cascade_url="https://cascade.example.edu",
    backendConfig={"cache_name": "/tmp/custom_cache.sqlite"}
)
```

---

## Cache Scope & Lifetime

* The cache is scoped to a single driver/session instance and tied to its dedicated event loop and `CacheHandler`.
* Cache hits reduce latency and API calls within a session by reading from the SQLite backend instead of hitting the network.
* You can tear down the cache DB and its underlying resources by calling `driver.close()`.

---

## When to Disable Caching

Caching should be turned off when running scripts that require the absolute freshest asset state or when debugging potentially stale results returned from previous runs. If a workflow involves rapid content updates and immediate verification within the same script execution, bypassing or clearing the cache prevents stale reads.

<!-- synthesized-for: 3.1.5 -->
