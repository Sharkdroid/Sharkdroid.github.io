!!! warning "Documentation may be out of date"
    This page was not successfully updated in the latest synthesis run. If you notice inaccuracies, please open an issue.

<!-- synthesis-failed
- Unfilled placeholders remain: ['[PLACEHOLDER: The cascade_cms library provides two distinct logging and output modes: normal mode for everyday running with minimal console output and simple logfiles, and debug mode for deep diagnostics with quiet console output, verbose logfiles, and per-request JSON files. Both modes write to logfiles, but debug mode adds a verbose nested call-chain log alongside a quieter console output.]', '[PLACEHOLDER: Normal mode runs with `debug_config=None`, producing a minimal console, a simple logfile, and lifecycle events such as connection status, running task scripts, completion summaries, and error notices. The logfile records the pipeline line per chain (via `flush_chain`/`flush_chain_error`) plus the batch tally. The logfile is named following `{SERVER}_{timestamp}.log`.]', '[PLACEHOLDER: \n[INIT]', '[PLACEHOLDER: \ndebug_config = {\n    "log_dir": "./logs",\n    "show_network_headers": True,\n}\n]', '[PLACEHOLDER: Recognized debug_config keys control the logging behavior, log directories, and output headers when debug mode is activated.]', '[PLACEHOLDER: The debug logfile is named using the convention `{SERVER}_debug_{timestamp}.log` and captures verbose activity, including `[METHOD]', '[PLACEHOLDER: \n>>>> START REQUEST <<<<\n(uuid_or_path, asset_type) OP1 -> fn_name: Type -> ...\n[GET]', '[PLACEHOLDER: Errors in debug mode are flushed via `flush_chain_error`, `log_cascade_error`, or `log_python_error`, producing a `v` alignment marker and an `!ERROR:` block indicating the exact failure step index or exception traceback details (`@{file}:{line}`). CascadeErrors include api-level failure states, while Python exceptions capture the exact exception type and message outside of chain contexts.]']
- Heading structure changed.
  Expected: ['# Logging & Debugging', '## Normal Mode Output', '### Normal Logfile Format', '## Enabling Debug Mode', '## Debug Configuration Options', '## Debug Logfile Format', '### Sample Debug Log', '## Interpreting Errors in Debug Mode']
  Got:      ['# Logging & Drafting', '## Normal Mode Output', '### Normal Logfile Format', '## Enabling Debug Mode', '## Debug Configuration Options', '## Debug Logfile Format', '### Sample Debug Log', '## Interpreting Errors in Debug Mode']
-->

# advanced-logging.md

_Content pending successful synthesis._
