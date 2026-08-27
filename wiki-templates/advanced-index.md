# Advanced

[PLACEHOLDER: 2–3 sentence intro for power users. This section covers configuration and performance topics that go beyond the defaults — caching behavior, debug logging, and CPU-intensive callback patterns. Tone: assumes reader has already worked through Core Concepts.]

---

## In This Section

| Page | What it covers |
|------|----------------|
| [Caching](caching.md) | How `aiohttp-client-cache` works per driver instance, what is and isn't cached, and how to configure the SQLite backend |
| [Logging & Debugging](logging.md) | Enabling debug mode, configuring the debug dict, reading log output, and walking through a sample logfile |
| [CPU-Intensive Tasks](cpu-intensive.md) | When to use `ProcessPoolExecutor`, pickling constraints, and performance trade-offs vs `ThreadPoolExecutor` |
