# Advanced

This section covers configuration and performance topics that go beyond the defaults — caching behavior, debug logging, and CPU-intensive callback patterns. It assumes you have already worked through the core concepts and are ready to optimize your application for production use.

---

## In This Section

| Page | What it covers |
|------|----------------|
| [Caching](caching.md) | How `aiohttp-client-cache` works per driver instance, what is and isn't cached, and how to configure the SQLite backend |
| [Logging & Debugging](logging.md) | Enabling debug mode, configuring the debug dict, reading log output, and walking through a sample logfile |
| [CPU-Intensive Tasks](cpu-intensive.md) | When to use `ProcessPoolExecutor`, pickling constraints, and performance trade-offs vs `ThreadPoolExecutor` |

<!-- synthesized-for: 3.1.5 -->
