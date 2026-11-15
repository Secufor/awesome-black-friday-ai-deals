#!/usr/bin/env python3
"""Validate data/deals.json and build README.md from it.

usage:
  python3 scripts/build_readme.py          # validate, then rewrite README.md
  python3 scripts/build_readme.py --check  # validate, exit 1 if README.md is out of date (CI)
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "deals.json"
README = ROOT / "README.md"
HEADER = ROOT / "scripts" / "readme_header.md"
FOOTER = ROOT / "scripts" / "readme_footer.md"

# Display order of sections. A deal's "category" must be one of these.
CATEGORIES = [
    "AI tools",
    "Developer tools & APIs",
    "Creator, video & design",
    "Productivity, SEO & marketing",
]
REQUIRED = ["name", "url", "category", "description", "deal", "ends", "source_url"]
TRACKING_PARAMS = {"ref", "via", "aff", "affiliate", "fpr", "irclickid", "gclid", "fbclid"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def anchor(text: str) -> str:
    return re.sub(r"[^a-z0-9 -]", "", text.lower()).replace(" ", "-")


def cell(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def validate(deals: list) -> list[str]:
    errors = []
    seen_names, seen_urls = set(), set()
    for i, deal in enumerate(deals):
        where = f"deal #{i + 1} ({deal.get('name', '?')})"
        for field in REQUIRED:
            if not str(deal.get(field, "")).strip():
                errors.append(f"{where}: missing '{field}'")
        if deal.get("category") not in CATEGORIES:
            errors.append(f"{where}: category must be one of {CATEGORIES}")
        for field in ("url", "source_url"):
            url = str(deal.get(field, ""))
            if not url.startswith("https://"):
                errors.append(f"{where}: '{field}' must start with https://")
            query = parse_qs(urlparse(url).query)
            bad = [k for k in query if k.lower().startswith("utm_") or k.lower() in TRACKING_PARAMS]
            if bad:
                errors.append(f"{where}: '{field}' has tracking/affiliate parameters {bad}")
        ends = str(deal.get("ends", ""))
        if ends != "not stated" and not DATE.match(ends):
            errors.append(f"{where}: 'ends' must be YYYY-MM-DD or 'not stated'")
        if len(str(deal.get("description", ""))) > 120:
            errors.append(f"{where}: description is over 120 characters")
        key_name, key_url = str(deal.get("name", "")).lower(), str(deal.get("url", "")).rstrip("/").lower()
        if key_name in seen_names or key_url in seen_urls:
            errors.append(f"{where}: duplicate name or url")
        seen_names.add(key_name)
        seen_urls.add(key_url)
    return errors


def render(deals: list) -> str:
    lifetime = sum(1 for d in deals if d.get("lifetime"))
    parts = [HEADER.read_text(encoding="utf-8").rstrip("\n").replace("{{COUNT}}", str(len(deals))).replace("{{LIFETIME}}", str(lifetime)), ""]
    parts.append("## Contents\n")
    for category in CATEGORIES:
        count = sum(1 for d in deals if d["category"] == category)
        parts.append(f"- [{category}](#{anchor(category)}) ({count})")
    parts.append("")
    for category in CATEGORIES:
        rows = sorted((d for d in deals if d["category"] == category), key=lambda d: d["name"].lower())
        parts.append(f"## {category}\n")
        if not rows:
            parts.append("_No deals yet. [Add one](CONTRIBUTING.md)._\n")
            continue
        parts.append("| Tool | What it does | Deal | Code | Ends |")
        parts.append("|---|---|---|---|---|")
        for d in rows:
            name = f"[{cell(d['name'])}]({d['url']})"
            deal = cell(d["deal"]) + (" (lifetime)" if d.get("lifetime") and "lifetime" not in d["deal"].lower() else "")
            code = f"`{cell(d['code'])}`" if d.get("code") else "No code needed"
            parts.append(f"| {name} | {cell(d['description'])} | {deal} ([source]({d['source_url']})) | {code} | {cell(d['ends'])} |")
        parts.append("")
    parts.append(FOOTER.read_text(encoding="utf-8").rstrip("\n"))
    return "\n".join(parts) + "\n"


def main() -> int:
    deals = json.loads(DATA.read_text(encoding="utf-8"))
    errors = validate(deals)
    if errors:
        print("data/deals.json has problems:\n  " + "\n  ".join(errors))
        return 1
    readme = render(deals)
    if "--check" in sys.argv:
        if README.read_text(encoding="utf-8") != readme:
            print("README.md is out of date. Run: python3 scripts/build_readme.py")
            return 1
        print(f"OK: {len(deals)} deals, README.md up to date")
        return 0
    README.write_text(readme, encoding="utf-8")
    print(f"Wrote README.md with {len(deals)} deals")
    return 0


if __name__ == "__main__":
    sys.exit(main())
