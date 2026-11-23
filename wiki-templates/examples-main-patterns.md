<!-- purpose: Task-oriented recipes for the everyday asset workflow. Each section is a complete, copy-pasteable script fragment that reuses the setup block from the top of the page, followed by 1–3 sentences on what to notice. Keep prose short; the code is the point. -->
<!-- focus: Cascade, EnvironmentVars, Asset, IdentifierType, Path, SearchInformation, ListElements, ChainResults, ChainFailure, FailureCategory, submit_requests, read, edit, publish, search, script_log -->
# Main Patterns

[PLACEHOLDER: One sentence saying these are common recipes for this version of the library, then a code block with the shared setup every recipe below assumes: imports, the environment dict, and one or two example identifiers built with the identifier types from the code facts.]

---

## Read a single asset

[PLACEHOLDER: Read one asset, submit, and print a couple of its fields from the successful result. 1–2 sentences on what a read returns.]

---

## Edit and save

[PLACEHOLDER: Read an asset, change it in a module-level callback, and write it back in the same chain. Show how to report failures from the result. 1–2 sentences on how the edit step knows which asset to save.]

---

## Publish

[PLACEHOLDER: Two short code blocks: publishing after an edit in the same chain, and publishing on its own. One sentence on when to pass a publish payload, if the code facts show one.]

---

## Search

[PLACEHOLDER: Build the search payload with the fields the code facts list for it (use the keyword names exactly as listed, either the field name or its alias), run the search, and iterate the matches. 1–2 sentences naming the payload and result types and where they are imported from.]

---

## Bulk operations

[PLACEHOLDER: Apply the same read → edit → publish chain to a list of identifiers and print a success/failure count plus each failure. 1–2 sentences on how a list fans out into independent chains.]

---

## Handling failures by category

[PLACEHOLDER: Run a batch with exit-on-failure turned off, then sort the failures by their category, using the category values the code facts list. 1–2 sentences on why you would keep the process alive and what each category means.]

---

## Script logging

[PLACEHOLDER: Add notes to the run's log before and after a batch. One sentence on where the helper can be called from.]
