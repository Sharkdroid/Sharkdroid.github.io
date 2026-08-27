# Caching

[PLACEHOLDER: 2–3 sentence intro — what the caching layer is (`aiohttp-client-cache` with SQLite), why it exists (avoid redundant GET requests in bulk scripts), and the key constraint (per-driver-instance scope, not persistent across runs by default).]

---

## What Gets Cached

[PLACEHOLDER: Short paragraph explaining that only GET (read) requests are cached; POST/PUT operations always hit the server. Note that `create`, `edit`, `delete`, `publish`, and other mutating operations are never cached. Source from `driver.py` or `CacheHandler` docstring in driver.md.]

---

## Default Configuration

[PLACEHOLDER: Code block showing the default `backendConfig` dict (or however `CachHandler` is configured at default). Explain each key briefly in inline comments. Source from `CacheHandler` or `CascadeCMSRestDriver` docstring in driver.md.]

---

## Custom Configuration

[PLACEHOLDER: Code block showing how to pass a custom `backendConfig` to `CascadeWrapperBase` or `CascadeCMSRestDriver` to change the cache location, expiration, or other SQLite settings. Source from driver.md docstrings. If no custom config is supported, document that the cache is only configurable via `backendConfig` at construction time.]

---

## Cache Scope & Lifetime

[PLACEHOLDER: Bullet list or short paragraph covering: (1) cache is scoped to a single driver/session instance and does not persist by default between separate script runs; (2) cache hits reduce latency and API calls within a session; (3) how to clear or disable the cache if needed. Source from driver.md.]

---

## When to Disable Caching

[PLACEHOLDER: Brief guidance on scenarios where caching should be turned off — e.g. scripts that need the freshest asset state, polling loops, or debugging stale results. 2–4 sentences.]
