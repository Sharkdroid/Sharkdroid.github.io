#!/usr/bin/env python3
"""
Create PR in wiki repo with synthesized documentation.

Reads filled markdown files and failure log from the staging directory
(written by synthesize_docs.py).

  * Failed pages: the [OUTDATED] banner is committed directly to main and
    the Pages deploy is dispatched — no review needed to warn readers. (If
    main refuses direct pushes, the banners go into the PR instead.)
  * Filled pages: written to a new branch and opened as a PR for review.
    If nothing was filled, no PR is created.
"""

import json
import os
from datetime import datetime, timezone

from github import Github, GithubException

STAGING_DIR     = "/tmp/filled-docs"
BASE_BRANCH     = "main"
DEPLOY_WORKFLOW = "deploy.yml"

TEMPLATE_TO_WIKI_PATH = {
    "core-concepts-index.md":    "wiki/cascade-cms-wiki/docs/core-concepts/index.md",
    "advanced-index.md":         "wiki/cascade-cms-wiki/docs/advanced/index.md",
    "advanced-logging.md":       "wiki/cascade-cms-wiki/docs/advanced/logging.md",
    "advanced-cpu-intensive.md": "wiki/cascade-cms-wiki/docs/advanced/cpu-intensive.md",
    "examples-main-patterns.md": "wiki/cascade-cms-wiki/docs/examples/main-patterns.md",
    "examples-administrative.md":"wiki/cascade-cms-wiki/docs/examples/administrative-ops.md",
}

# `danger` renders as a red admonition (needs the `admonition` extension in
# properdocs.yml, otherwise the banner shows as literal "!!! ..." text).
BANNER_HEAD     = '!!! danger "Documentation may be out of date"'
OLD_BANNER_HEAD = '!!! warning "Documentation may be out of date"'

OUTDATED_BANNER = """\
!!! danger "Documentation may be out of date"
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


def mark_outdated(repo, template_name: str, errors: list[str], version: str,
                  branch: str) -> bool:
    """Prepend the [OUTDATED] banner to a failed page on `branch`. If the page
    already exists, keep its previously-deployed content and just flag it
    stale. If it doesn't exist yet (e.g. the very first run), write a stub so
    the page — and the failure — is visible. Returns True if it wrote."""
    wiki_path = TEMPLATE_TO_WIKI_PATH.get(template_name)
    if not wiki_path:
        return False
    error_note = "\n".join(f"- {e}" for e in errors)
    # `-->` inside an error would end the HTML comment early.
    banner     = OUTDATED_BANNER + f"<!-- synthesis-failed\n{error_note.replace('-->', '- ->')}\n-->\n\n"
    try:
        existing = repo.get_contents(wiki_path, ref=branch)
        current  = existing.decoded_content.decode()
        if "synthesis-failed" in current:
            # Upgrade banners written before they were switched to red.
            if OLD_BANNER_HEAD in current:
                write_file(repo, wiki_path, current.replace(OLD_BANNER_HEAD, BANNER_HEAD, 1),
                           f"docs({version}): make {template_name} outdated banner red", branch)
                return True
            print(f"[create_pr] {template_name} already marked outdated on {branch}")
            return False
        content = banner + current
        message = f"docs({version}): mark {template_name} outdated (synthesis failed)"
    except GithubException as e:
        if e.status != 404:
            raise
        content = banner + f"# {template_name}\n\n_Content pending successful synthesis._\n"
        message = f"docs({version}): stub {template_name} (synthesis failed)"
    print(f"[create_pr] Marking {template_name} as outdated on {branch}")
    write_file(repo, wiki_path, content, message, branch)
    return True


def redeploy_pages(repo):
    """Commits made with the workflow's GITHUB_TOKEN don't trigger other
    workflows, so the push above won't start deploy.yml by itself.
    workflow_dispatch is exempt from that rule (needs `actions: write`)."""
    try:
        ok = repo.get_workflow(DEPLOY_WORKFLOW).create_dispatch(BASE_BRANCH)
        print(f"[create_pr] Pages redeploy {'dispatched' if ok else 'NOT dispatched'} "
              f"({DEPLOY_WORKFLOW} on {BASE_BRANCH})")
    except GithubException as e:
        print(f"[create_pr] ! Could not dispatch {DEPLOY_WORKFLOW} ({e.status}); "
              f"banners are on {BASE_BRANCH} but Pages will update on the next deploy")


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
    grounding    = manifest.get("grounding") or {}
    repaired     = manifest.get("repaired") or []

    print(f"[create_pr] cascade_cms {version}")
    print(f"[create_pr] Filled: {len(filled_names)}  Failed: {len(failed_files)}")

    g    = Github(token)
    repo = g.get_repo(repo_name)

    # Failed pages skip review: their [OUTDATED] banner is committed straight
    # to the base branch and Pages is redeployed, so readers are warned right
    # away instead of only once someone merges a banner-only PR. If the base
    # branch rejects direct pushes (branch protection), fall back to the old
    # behaviour of carrying the banners in the PR.
    failed_direct = []
    failed_in_pr  = {}
    if failed_files:
        try:
            for template_name, errors in failed_files.items():
                if mark_outdated(repo, template_name, errors, version, BASE_BRANCH):
                    failed_direct.append(template_name)
        except GithubException as e:
            if e.status not in (403, 409, 422):
                raise
            print(f"[create_pr] ! Direct push to {BASE_BRANCH} refused ({e.status}); "
                  f"carrying [OUTDATED] banners in the PR instead")
            failed_in_pr = {n: errs for n, errs in failed_files.items() if n not in failed_direct}
        if failed_direct:
            redeploy_pages(repo)

    if not filled_names and not failed_in_pr:
        print("[create_pr] Nothing to review — no PR created")
        return

    # Branch name includes version and date for traceability
    datestamp   = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    branch_name = create_branch(repo, f"docs-synthesis/{version}-{datestamp}",
                                repo.get_branch(BASE_BRANCH).commit.sha)

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

    # Fallback only: banners the base branch refused
    for template_name, errors in failed_in_pr.items():
        mark_outdated(repo, template_name, errors, version, branch_name)

    # Build PR body
    success_list = "\n".join(f"- ✅ {n}" for n in sorted(filled_names))
    failed_list  = "\n".join(
        f"- ❌ {n}" + (" (banner already on main)" if n not in failed_direct and n not in failed_in_pr
                       else "")
        + "\n  - " + "\n  - ".join(errs)
        for n, errs in sorted(failed_files.items())
    ) if failed_files else ""
    failed_heading = (
        "### Generation failed (pages marked [OUTDATED] in this PR)" if failed_in_pr else
        f"### Generation failed (pages marked [OUTDATED] directly on `{BASE_BRANCH}`, not part of this PR)"
    )

    grounding_note = ""
    if grounding:
        tokens = grounding.get("approx_tokens") or {}
        token_lines = "\n".join(f"- {n}: ~{t:,} tokens" for n, t in sorted(tokens.items()))
        grounding_note = (
            f"### Grounding\n"
            f"Mode: `{grounding.get('mode')}`"
            + (f" (code facts from installed `cascade-cms-rest {grounding['facts_version']}`)"
               if grounding.get("facts_version") else "")
            + "\n\n" + (token_lines or "_No grounding sizes recorded_")
            + ("\n\nFixed after a validation-repair call: "
               + ", ".join(f"`{n}`" for n in sorted(repaired)) if repaired else "")
            + "\n"
        )

    body = f"""\
## AI Documentation Synthesis — `cascade_cms {version}`

Auto-generated documentation update. Phase 1 reference docs were rebuilt \
before synthesis ran.

### Generated successfully
{success_list or "_None_"}

{failed_heading + chr(10) + failed_list if failed_list else ""}

### Model used
`{model}`

{grounding_note}
### To approve
Merge this PR to publish updated documentation. The wiki deploys automatically on merge.

### To reject
Close without merging. Any `[OUTDATED]` banners remain until the next synthesis run or manual fix.
"""

    pr = repo.create_pull(
        title=f"docs({version}): AI synthesis update",
        body=body,
        head=branch_name,
        base=BASE_BRANCH,
    )

    print(f"[create_pr] ✓ PR created: {pr.html_url}")


if __name__ == "__main__":
    main()
