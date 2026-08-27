#!/usr/bin/env python3
"""
Create PR in wiki repo with synthesized documentation.

Reads filled markdown files and failure log from the staging directory
(written by synthesize_docs.py), creates a branch, writes files to their
wiki paths, prepends [OUTDATED] banners to failed files, and opens a PR
for manual review.
"""

import json
import os
from datetime import datetime, timezone

from github import Github, GithubException

STAGING_DIR = "/tmp/filled-docs"

TEMPLATE_TO_WIKI_PATH = {
    "core-concepts-index.md":    "wiki/cascade-cms-wiki/docs/core-concepts/index.md",
    "advanced-index.md":         "wiki/cascade-cms-wiki/docs/advanced/index.md",
    "advanced-caching.md":       "wiki/cascade-cms-wiki/docs/advanced/caching.md",
    "advanced-logging.md":       "wiki/cascade-cms-wiki/docs/advanced/logging.md",
    "advanced-cpu-intensive.md": "wiki/cascade-cms-wiki/docs/advanced/cpu-intensive.md",
    "examples-main-patterns.md": "wiki/cascade-cms-wiki/docs/examples/main-patterns.md",
    "examples-administrative.md":"wiki/cascade-cms-wiki/docs/examples/administrative.md",
}

OUTDATED_BANNER = """\
!!! warning "Documentation may be out of date"
    This page was not successfully updated in the latest synthesis run. \
If you notice inaccuracies, please open an issue.

"""


def write_file(repo, wiki_path: str, content: str, message: str, branch: str):
    """Create or update a file in the wiki repo."""
    try:
        existing = repo.get_contents(wiki_path, ref=branch)
        repo.update_file(wiki_path, message, content, existing.sha, branch=branch)
    except GithubException as e:
        if e.status != 404:
            raise
        repo.create_file(wiki_path, message, content, branch=branch)


def create_branch(repo, branch_name: str, base_sha: str) -> str:
    """Create the synthesis branch, falling back to a time-suffixed name if
    a branch with the same date already exists (e.g. a same-day forced rerun)."""
    try:
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_sha)
        return branch_name
    except GithubException as e:
        if e.status != 422:
            raise
        suffixed = f"{branch_name}-{datetime.now(timezone.utc).strftime('%H%M%S')}"
        print(f"[create_pr] Branch {branch_name} already exists, using {suffixed}")
        repo.create_git_ref(ref=f"refs/heads/{suffixed}", sha=base_sha)
        return suffixed


def main():
    token = os.environ["GITHUB_TOKEN"]
    repo_name = os.environ["GITHUB_REPOSITORY"]

    # Load manifest written by synthesize_docs.py
    manifest = json.load(open(os.path.join(STAGING_DIR, "manifest.json")))
    version      = manifest["version"]
    model        = manifest["model"]
    filled_names = manifest["filled"]
    failed_files = manifest["failed"]

    print(f"[create_pr] cascade_cms {version}")
    print(f"[create_pr] Filled: {len(filled_names)}  Failed: {len(failed_files)}")

    g    = Github(token)
    repo = g.get_repo(repo_name)
    base = repo.get_branch("main")

    # Branch name includes version and date for traceability
    datestamp   = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    branch_name = create_branch(repo, f"docs-synthesis/{version}-{datestamp}", base.commit.sha)

    # Write successfully filled files
    for template_name in filled_names:
        wiki_path    = TEMPLATE_TO_WIKI_PATH[template_name]
        staging_path = os.path.join(STAGING_DIR, template_name)
        content      = open(staging_path).read()
        print(f"[create_pr] Writing {wiki_path}")
        write_file(
            repo, wiki_path, content,
            f"docs({version}): synthesize {template_name}",
            branch_name,
        )

    # Prepend OUTDATED banner to failed files
    for template_name, errors in failed_files.items():
        wiki_path  = TEMPLATE_TO_WIKI_PATH.get(template_name)
        if not wiki_path:
            continue
        error_note = "\n".join(f"- {e}" for e in errors)
        banner     = OUTDATED_BANNER + f"<!-- synthesis-failed\n{error_note}\n-->\n\n"
        print(f"[create_pr] Marking {template_name} as outdated")
        try:
            existing = repo.get_contents(wiki_path, ref=branch_name)
            current  = existing.decoded_content.decode()
            if "synthesis-failed" not in current:
                repo.update_file(
                    wiki_path,
                    f"docs({version}): mark {template_name} outdated",
                    banner + current,
                    existing.sha,
                    branch=branch_name,
                )
        except GithubException as e:
            if e.status != 404:
                raise

    # Build PR body
    success_list = "\n".join(f"- ✅ {n}" for n in sorted(filled_names))
    failed_list  = "\n".join(
        f"- ❌ {n}\n  - " + "\n  - ".join(errs)
        for n, errs in sorted(failed_files.items())
    ) if failed_files else ""

    body = f"""\
## AI Documentation Synthesis — `cascade_cms {version}`

Auto-generated documentation update. Phase 1 reference docs were rebuilt \
before synthesis ran.

### Generated successfully
{success_list or "_None_"}

{"### Generation failed (pages marked [OUTDATED])" + chr(10) + failed_list if failed_list else ""}

### Model used
`{model}`

### To approve
Merge this PR to publish updated documentation. The wiki deploys automatically on merge.

### To reject
Close without merging. Any `[OUTDATED]` banners remain until the next synthesis run or manual fix.
"""

    pr = repo.create_pull(
        title=f"docs({version}): AI synthesis update",
        body=body,
        head=branch_name,
        base="main",
    )

    print(f"[create_pr] ✓ PR created: {pr.html_url}")


if __name__ == "__main__":
    main()
