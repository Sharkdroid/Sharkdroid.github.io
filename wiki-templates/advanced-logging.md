<!-- purpose: Help a user understand what the library writes to the console and log files, turn on debug mode, and read a failing run's log. Describe only output formats, file names, markers and config keys that appear in the code facts (docstrings, literals, constants); if a detail isn't there, leave it out rather than guessing. -->
<!-- focus: Cascade, OperationLogger, ChainLineBuilder, FailureCategory, debug, debug_config, log_dir, exit_on_failure, script_log -->
# Logging & Debugging

[PLACEHOLDER: 2–3 sentence intro: the two output modes (normal and debug), what decides which one is active, and that both write a logfile.]

---

## Normal Mode Output

[PLACEHOLDER: Paragraph on what normal mode prints and logs: lifecycle markers, the per-chain line, the batch tally, and the logfile's location and name pattern.]

### Normal Logfile Format

[PLACEHOLDER: `text` code block with a short, representative normal logfile: start, one successful chain, one failed chain, the tally, and exit. Build each line from formats documented in the code facts.]

---

## Enabling Debug Mode

[PLACEHOLDER: Code block showing how to turn debug mode on when opening a session, using the constructor parameter names exactly as the code facts give them, and where the log directory is set. 1–2 sentences on what changes when it is on.]

---

## Debug Configuration Options

[PLACEHOLDER: Table with the columns Key, Type, Default and Description, with one row per debug configuration key documented in the code facts. If a key can also be set as a constructor parameter, say which one wins.]

---

## Debug Logfile Format

[PLACEHOLDER: Paragraph on the debug logfile's name pattern, the extra request/response detail it records, and any per-request files written next to it.]

### Sample Debug Log

[PLACEHOLDER: `text` code block with a short, representative debug log excerpt for one chain, built only from formats documented in the code facts.]

---

## Interpreting Errors in Debug Mode

[PLACEHOLDER: Explain how a failed chain shows up in the log (which step failed, and its failure category), how API errors differ from Python exceptions and callback errors, and where to look first. Use the failure categories from the code facts.]
