# Logging & Debugging

[PLACEHOLDER: 2–3 sentence intro — two output modes exist (normal mode for everyday use, debug mode for diagnosing failures). Mention that both produce logfiles; debug mode adds a verbose nested call-chain log alongside a quieter console output.]

---

## Normal Mode Output

[PLACEHOLDER: Short paragraph explaining what normal mode logs — lifecycle markers (`[INIT]`, `[RUNNING]`, `[DONE]`, `[EXIT]`), per-operation progress lines (`Processed: N/total (X failed)`), and a normal logfile named `{SERVER}_{timestamp}.log` with one line per operation. Source from `OperationLogger` docstring in operation_logger.md.]

### Normal Logfile Format

[PLACEHOLDER: Code block showing a sample normal logfile — a few representative lines like `[READ]: mySite/blog/post-1`, one `CascadeError` line, and one Python error line. Source from operation_logger.md docstring examples if present.]

---

## Enabling Debug Mode

[PLACEHOLDER: Code block showing how to pass the `debug` dict to `CascadeWrapperBase` to activate debug mode. Show the minimal required keys. Source from `CascadeWrapperBase` docstring in wrapper.md.]

---

## Debug Configuration Options

[PLACEHOLDER: Table or bullet list of all keys in the debug config dict — what each controls (response body truncation via `response_line_limit`, granular toggles, etc.) and their defaults. Source from `CascadeWrapperBase` or `OperationLogger` docstring in wrapper.md / operation_logger.md.]

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| [PLACEHOLDER: key] | [PLACEHOLDER: type] | [PLACEHOLDER: default] | [PLACEHOLDER: description] |

---

## Debug Logfile Format

[PLACEHOLDER: Paragraph explaining the debug logfile naming convention (`{SERVER}_debug_{timestamp}.log`) and the nested pipe-delimited call-chain format. Source from `OperationLogger` docstring.]

### Sample Debug Log

[PLACEHOLDER: Code block showing a representative debug log excerpt — a few lines of the nested call-chain format, showing a read operation and a callback with `>>` separators. Source from operation_logger.md docstring examples if present.]

---

## Interpreting Errors in Debug Mode

[PLACEHOLDER: Short explanation of how error blocks appear in debug mode — parsing the traceback's local frame to show only relevant variables, the distinction between `CascadeError` (includes asset path) and Python errors (type and message only). Source from operation_logger.md.]
