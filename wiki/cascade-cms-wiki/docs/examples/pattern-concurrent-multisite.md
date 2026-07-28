---
layout: default
title: Multi-Site Concurrent
parent: Examples & Patterns
nav_order: 11
---

# Concurrent operations across multiple sites

`Path` identifiers address assets by site name and path, making it natural to operate across sites with identical logic. Concurrency is automatic — queue everything, submit once, and the semaphore manages execution.

```python
import os
from dotenv import load_dotenv
from cascade_cms.cmstypes import Asset, Path
from cascade_cms.wrapper import CascadeWrapperBase

load_dotenv()

env = {
    "API_KEY": os.environ["CASCADE_API_KEY"],
    "CASCADE_URL": os.environ["CASCADE_URL"],
    "SERVER": os.environ["SERVER"],
}
config = {
    "cache_name": "./cache/cache.sqlite",
    "allowed_codes": (200,),
    "allowed_methods": ("GET",),
}

# The same path in three different sites
target_path = "/about/contact"
sites = ["www.example.edu", "staging.example.edu", "dev.example.edu"]

paths = [
    Path(asset_type="page", siteName=site, path=target_path)
    for site in sites
]

with CascadeWrapperBase(env, config) as cascade:
    cascade.operations.read(paths)
    results = cascade.submit_requests(Asset)

for asset in results:
    print(f"{asset.get('siteId')}: {asset.get('name')}")
```

## Grouping results by site with a callback

```python
from collections import defaultdict

site_groups: dict[str, list[Asset]] = defaultdict(list)

def group_by_site(asset: Asset):
    # siteId is available on all assets
    site = asset.get("siteName") or asset.get("siteId", "unknown")
    site_groups[site].append(asset)
    print(f"[{site}] {asset.get('name')}")

with CascadeWrapperBase(env, config) as cascade:
    cascade.operations.read(paths).then(group_by_site)
    cascade.submit_requests(Asset)

# site_groups now maps site name → list of assets
for site, assets in site_groups.items():
    print(f"{site}: {len(assets)} assets")
```

## Cross-site bulk edit

Read the same page from multiple sites, apply an identical change, and edit all at once:

```python
with CascadeWrapperBase(env, config) as cascade:
    cascade.operations.read(paths)
    results = cascade.submit_requests(Asset)

    for asset in results:
        asset["keywords"] = "contact, location, directions"

    cascade.operations.edit(results)
    cascade.submit_requests()
    print(f"Updated {len(results)} pages across {len(sites)} sites")
```

## Concurrency limit

The driver limits concurrent in-flight requests to `MAX_REQUESTS = 50` via an internal semaphore. If you queue more than 50 operations, the semaphore queues the remainder automatically — you don't need to batch manually.

For very large site sweeps (hundreds of paths), you can split into multiple `submit_requests()` calls to control memory usage:

```python
BATCH_SIZE = 100
all_paths = [...]  # e.g., 500 paths across 10 sites

with CascadeWrapperBase(env, config) as cascade:
    for i in range(0, len(all_paths), BATCH_SIZE):
        batch = all_paths[i : i + BATCH_SIZE]
        cascade.operations.read(batch)
        results = cascade.submit_requests(Asset)
        # process results before loading next batch
        for asset in results:
            print(asset.get("name"))
```

---

See also: [Core Concepts: Identifiers](../core-concepts/#3-identifiers-identifiertype-vs-path) · [Advanced: Concurrency](../advanced/concurrency-caching/)
