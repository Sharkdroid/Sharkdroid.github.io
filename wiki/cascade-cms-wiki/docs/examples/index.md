---
layout: default
title: Examples & Patterns
nav_order: 5
has_children: true
---

# Examples & Patterns

These 11 examples demonstrate the library's core mechanics. They are organized by pattern, not scenario — the goal is to show you what the library can do, not prescribe what your script should look like.

Each example is self-contained and runnable. Swap in real UUIDs and environment variables to use them directly.

## Getting data into memory

| Example | What you learn |
|---------|---------------|
| [ID vs. Path addressing](./pattern-read-identifiers.md) | Two ways to reference the same asset; `get_data_structure()` and `get_page_configuration()` |
| [Cache behavior](./pattern-read-cache.md) | Repeated reads skip the network; how to configure or disable caching |
| [Iterating results three ways](./pattern-read-iterate.md) | List comprehension, for-loop, and callback on the same result set |

## Modifying and creating

| Example | What you learn |
|---------|---------------|
| [Bulk create](./pattern-create-bulk.md) | Batch `NewAsset` objects; why responses are IDs, not full assets |
| [Edit in-place](./pattern-edit-in-place.md) | Mutate an asset in memory, then queue the edit |

## Processing results

| Example | What you learn |
|---------|---------------|
| [No callbacks (pure submit)](./pattern-callback-none.md) | Queue multiple operations, collect results, no callbacks involved |
| [Callback chain with in-place modification](./pattern-callback-chain.md) | Sequential callbacks; mutating results from within the chain |
| [Dependent callbacks](./pattern-callback-dependent.md) | Callbacks that queue new operations based on what they see |
| [CPU-bound callbacks](./pattern-callback-cpu-bound.md) | `ProcessPoolExecutor` for true parallelism; pickling constraints |

## Complex operations

| Example | What you learn |
|---------|---------------|
| [Workflow orchestration](./pattern-workflow-orchestration.md) | Full read → validate → transition → confirm cycle |
| [Multi-site concurrent](./pattern-concurrent-multisite.md) | Path identifiers across multiple sites; automatic concurrency |

---

Not sure where to start? Try [ID vs. Path](./pattern-read-identifiers.md) if you're new to the library, or [No callbacks](./pattern-callback-none.md) for the simplest baseline.
