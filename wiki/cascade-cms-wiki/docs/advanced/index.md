!!! warning "Documentation may be out of date"
    This page was not successfully updated in the latest synthesis run. If you notice inaccuracies, please open an issue.

<!-- synthesis-failed
- Heading structure changed.
  Expected: ['# Advanced', '## In This Section']
  Got:      ['# Advanced']
-->

# Advanced

Welcome to the advanced power user guide for tuning and scaling your application. This section covers configuration and performance topics that go beyond the defaults, including caching behavior, debug logging, and CPU-intensive callback patterns.

---

## In This Section

| Page | What it covers |
|------|----------------|
| [Caching](caching.md) | How `aiohttp-client-cache` works per driver instance, what is and isn't cached, and how to configure the SQLite backend |
| [Logging & Debugging](logging.md) | Enabling debug mode, configuring the debug dict, reading log output, and walking through a sample logfile |
| [CPU-Intensive Tasks](cpu-intensive.md) | When to use `ProcessPoolExecutor`, pickling constraints, and performance trade-offs vs `ThreadPoolExecutor` |

<!-- synthesized-for: 3.1.1 -->
