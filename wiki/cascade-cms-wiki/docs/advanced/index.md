!!! warning "Documentation may be out of date"
    This page was not successfully updated in the latest synthesis run. If you notice inaccuracies, please open an issue.

<!-- synthesis-failed
- Model call failed: litellm.UnsupportedParamsError: gemini does not support parameters: ['temperature'], for model=gemini-3.5-flash-lite. To drop these, set `litellm.drop_params=True` or for proxy:

`litellm_settings:
 drop_params: true`
. 
 If you want to use these params dynamically send allowed_openai_params=['temperature'] in your request.
-->

# Advanced

Welcome to the advanced power user guide for tuning and scaling your application. This section covers configuration and performance topics that go beyond the defaults, including caching behavior, debug logging, and CPU-intensive callback patterns.

---

## In This Section

| Page | What it covers |
|------|----------------|
| [Logging & Debugging](logging.md) | Enabling debug mode, configuring the debug dict, reading log output, and walking through a sample logfile |
| [CPU-Intensive Tasks](cpu-intensive.md) | When to use `ProcessPoolExecutor`, pickling constraints, and performance trade-offs vs `ThreadPoolExecutor` |

<!-- synthesized-for: 3.1.1 -->
