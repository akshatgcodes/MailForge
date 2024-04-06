#!/usr/bin/env python3
"""
MailForge - Bulk personalized email sender with a dry-run HTML preview mode.

Usage:
    python mailforge.py --contacts contacts.csv --template template.html --dry-run

See README.md for full documentation.
"""

import argparse
import re
import sys
from pathlib import Path

import pandas as pd
from jinja2 import Environment

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

SUBJECT_RE = re.compile(r"<!--\s*SUBJECT:\s*(.*?)\s*-->", re.IGNORECASE | re.DOTALL)
DEFAULT_SUBJECT = "A message for you"

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def slugify(value: str) -> str:
    value = re.sub(r"[^\w\s-]", "", str(value)).strip().lower()
    value = re.sub(r"[-\s]+", "-", value)
    return value or "contact"


def load_contacts(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower() for c in df.columns]
    if "email" not in df.columns:
        raise ValueError(
            f"Contacts CSV '{csv_path}' must contain an 'email' column. Found columns: {list(df.columns)}"
        )
    df = df.fillna("")
    return df


def load_template(template_path: str) -> tuple[str, str]:
    """Return (subject_template_str, body_template_str) extracted from an HTML template file.

    The subject line is declared in the template via an HTML comment:
        <!-- SUBJECT: Hello {{name}}, quick question -->
    """
    raw = Path(template_path).read_text(encoding="utf-8")
    match = SUBJECT_RE.search(raw)
    if match:
        subject_tpl = match.group(1)
        body_tpl = SUBJECT_RE.sub("", raw, count=1).strip()
    else:
        subject_tpl = DEFAULT_SUBJECT
        body_tpl = raw
    return subject_tpl, body_tpl


def render_email(subject_tpl: str, body_tpl: str, contact: dict) -> tuple[str, str]:
    env = Environment()
    subject = env.from_string(subject_tpl).render(**contact)
    body = env.from_string(body_tpl).render(**contact)
    return subject, body


def html_to_plaintext(html: str) -> str:
    """Very small best-effort HTML->text fallback for the multipart/alternative plain part."""
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# --------------------------------------------------------------------------
# Dry-run mode
# --------------------------------------------------------------------------


def run_dry_run(contacts: pd.DataFrame, subject_tpl: str, body_tpl: str, preview_dir: str) -> None:
    out_dir = Path(preview_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Clear stale previews from a previous run so the count always reflects this run.
    for old_file in out_dir.glob("*.html"):
        old_file.unlink()

    count = 0
    for idx, row in enumerate(contacts.to_dict(orient="records"), start=1):
        subject, body = render_email(subject_tpl, body_tpl, row)
        identifier = row.get("email") or row.get("name") or str(idx)
        filename = f"{idx:03d}_{slugify(identifier)}.html"
        preview_html = (
            "<!DOCTYPE html>\n<html><head><meta charset='utf-8'>"
            f"<title>PREVIEW: {subject}</title></head><body>"
            f"<div style='background:#111;color:#0f0;padding:12px;font-family:monospace;'>"
            f"<strong>To:</strong> {row.get('email', '')}<br>"
            f"<strong>Subject:</strong> {subject}"
            f"</div><hr>{body}</body></html>"
        )
        (out_dir / filename).write_text(preview_html, encoding="utf-8")
        count += 1

    print(f"✅ Previews generated in /{preview_dir} ({count} files) — open in browser to review")


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="MailForge - bulk personalized email sender with a dry-run preview mode."
    )
    parser.add_argument("--contacts", required=True, help="Path to contacts CSV (must include an 'email' column)")
    parser.add_argument("--template", required=True, help="Path to Jinja2 HTML email template")
    parser.add_argument("--dry-run", action="store_true", help="Generate HTML previews instead of sending")
    parser.add_argument("--preview-dir", default="preview", help="Output directory for dry-run previews")
    return parser


def main(argv=None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    try:
        contacts = load_contacts(args.contacts)
    except Exception as exc:
        print(f"❌ Failed to load contacts: {exc}", file=sys.stderr)
        return 1

    try:
        subject_tpl, body_tpl = load_template(args.template)
    except Exception as exc:
        print(f"❌ Failed to load template: {exc}", file=sys.stderr)
        return 1

    if len(contacts) == 0:
        print("❌ No contacts found in CSV.", file=sys.stderr)
        return 1

    if args.dry_run:
        run_dry_run(contacts, subject_tpl, body_tpl, args.preview_dir)
        return 0

    print("Sending is not implemented yet - use --dry-run for now.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
