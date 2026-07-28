"""Render the repo-root index.md and wiki/index.md into combined-site/.

Runs alongside the properdocs build in the deploy workflow so the plain
hub pages get served next to the generated wiki subsites instead of being
overwritten by them.
"""

import html
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
OUTPUT = ROOT / "combined-site"

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 42rem; margin: 3rem auto; padding: 0 1.5rem; line-height: 1.6; color: #1a1a1a; }}
  a {{ color: #0969da; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #d0d7de; padding: 0.5rem 0.75rem; text-align: left; }}
  @media (prefers-color-scheme: dark) {{
    body {{ background: #0d1117; color: #e6edf3; }}
    a {{ color: #58a6ff; }}
    th, td {{ border-color: #30363d; }}
  }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def render(md_path: Path, out_path: Path, title: str) -> None:
    text = md_path.read_text(encoding="utf-8")
    body = markdown.markdown(text, extensions=["tables"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(TEMPLATE.format(title=html.escape(title), body=body), encoding="utf-8")


if __name__ == "__main__":
    render(ROOT / "index.md", OUTPUT / "index.html", "Keith Shark")
    render(ROOT / "wiki" / "index.md", OUTPUT / "wiki" / "index.html", "Wiki Registry")
