# Caching

The caching layer is built as a thin wrapper around an aiohttp-client-cache SQLite backend (`CacheHandler`). It exists to skip the network for repeated reads and avoid redundant GET requests in bulk scripts. The cache is scoped to a single driver instance and is not persistent across runs by default.

---

## What Gets Cached

Only GET responses are ever cached (enforced by the backend's `allowed_methods` config) so repeated reads skip the network, while POST/PUT requests always hit the server. Mutating operations like create, edit, delete, and publish are never cached.

---

## Default Configuration

```python
def default_cache_backend() -> SQLiteBackend:
    """Build the default cache backend: SQLite, GET-only, 200s only.

    Constructed on demand rather than at module scope so that merely

    importing `cascade_cms` does not create a `./cache/` directory in the

    caller's working directory.

    """

    return SQLiteBackend(

        cache_name="./cache/cache.sqlite",

        allowed_codes=(200,),

        allowed_methods=("GET",),

    )
```

---

## Custom Configuration

```python
# Pass backendConfig to CascadeCMSRestDriver to override the default cache config
driver = CascadeCMSRestDriver(
    apiKey="your-api-key",
    cascade_url="https://cascade.example.edu",
    backendConfig={"cache_name": "./custom_cache/cache.sqlite"}
)
```

---

## Cache Scope & Lifetime

- **Driver Scope:** The cache is bound to a single `CascadeCMSRestDriver` instance and its underlying SQLite backend database file (`./cache/cache.sqlite` by default).
- **Session Performance:** Cache hits reduce latency and skip network requests entirely for repeated GETs within the session.
- **Tear Down:** Calling `driver.close()` tears down the session, cache DB, and event loop.

---

## When to Disable Caching

Caching should be bypassed or disabled when running scripts that require the absolute freshest asset state from the server, when running polling loops, or when debugging to avoid stale results. You can override or reconfigure the SQLite backend configuration at driver initialization time if different caching behaviors are needed for specific workflows.

<!-- synthesized-for: 3.1.5 -->
