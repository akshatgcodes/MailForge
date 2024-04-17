#!/usr/bin/env python3
"""
MailForge - Bulk personalized email sender with dry-run preview and rate limiting.

Usage:
    python mailforge.py --contacts contacts.csv --template template.html --dry-run
    python mailforge.py --contacts contacts.csv --template template.html --rate 10/min

See README.md for full documentation.
"""

import argparse
import logging
import os
import re
import smtplib
import sys
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import pandas as pd
from jinja2 import Environment, Template
from dotenv import load_dotenv

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

SUBJECT_RE = re.compile(r"<!--\s*SUBJECT:\s*(.*?)\s*-->", re.IGNORECASE | re.DOTALL)
DEFAULT_SUBJECT = "A message for you"
MAX_SEND_ATTEMPTS = 2  # initial attempt + 1 retry
RETRY_BACKOFF_SECONDS = 2

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def parse_rate(rate_str: str) -> float:
    """Parse a rate string like '10/min', '5/sec', '120/hour' into seconds-between-sends."""
    match = re.match(r"^\s*(\d+(?:\.\d+)?)\s*/\s*(min|minute|sec|second|hour)s?\s*$", rate_str, re.IGNORECASE)
    if not match:
        raise ValueError(
            f"Invalid --rate format: {rate_str!r}. Expected e.g. '10/min', '5/sec', '120/hour'."
        )
    count = float(match.group(1))
    unit = match.group(2).lower()
    if count <= 0:
        raise ValueError("--rate count must be greater than 0")

    unit_seconds = {
        "sec": 1,
        "second": 1,
        "min": 60,
        "minute": 60,
        "hour": 3600,
    }[unit]

    return unit_seconds / count


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
# Send mode
# --------------------------------------------------------------------------


def build_message(from_addr: str, from_name: str, to_addr: str, subject: str, html_body: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{from_addr}>" if from_name else from_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(html_to_plaintext(html_body), "plain"))
    msg.attach(MIMEText(html_body, "html"))
    return msg


def send_via_smtp(smtp_config: dict, msg: MIMEMultipart, to_addr: str) -> None:
    with smtplib.SMTP(smtp_config["host"], smtp_config["port"], timeout=15) as server:
        if smtp_config.get("use_tls"):
            server.starttls()
        if smtp_config.get("user") and smtp_config.get("password"):
            server.login(smtp_config["user"], smtp_config["password"])
        server.sendmail(smtp_config["from_addr"], [to_addr], msg.as_string())


def run_send(
    contacts: pd.DataFrame,
    subject_tpl: str,
    body_tpl: str,
    smtp_config: dict,
    rate_str: str,
    logger: logging.Logger,
    log_filename: str,
) -> None:
    sleep_seconds = parse_rate(rate_str)
    sent = 0
    failed = 0
    total = len(contacts)

    records = contacts.to_dict(orient="records")
    for i, row in enumerate(records):
        to_addr = row.get("email", "").strip()
        subject, body = render_email(subject_tpl, body_tpl, row)

        if not to_addr:
            logger.error("SKIPPED contact #%d (name=%r): no email address", i + 1, row.get("name", ""))
            failed += 1
            continue

        msg = build_message(
            smtp_config["from_addr"], smtp_config.get("from_name", ""), to_addr, subject, body
        )

        success = False
        last_error = None
        for attempt in range(1, MAX_SEND_ATTEMPTS + 1):
            try:
                send_via_smtp(smtp_config, msg, to_addr)
                logger.info("SUCCESS to=%s subject=%r attempt=%d", to_addr, subject, attempt)
                success = True
                break
            except Exception as exc:  # noqa: BLE001 - we want to catch and log any SMTP failure
                last_error = exc
                logger.warning(
                    "FAILED attempt %d/%d to=%s error=%s", attempt, MAX_SEND_ATTEMPTS, to_addr, exc
                )
                if attempt < MAX_SEND_ATTEMPTS:
                    time.sleep(RETRY_BACKOFF_SECONDS)

        if success:
            sent += 1
        else:
            failed += 1
            logger.error("GIVE UP to=%s after %d attempts: %s", to_addr, MAX_SEND_ATTEMPTS, last_error)

        # Rate limiting: pause between sends (skip the wait after the very last contact).
        if i < total - 1:
            time.sleep(sleep_seconds)

    print(
        f"✅ {sent}/{total} sent | ❌ {failed} failed (logged) | \U0001F4CB {log_filename}"
    )


# --------------------------------------------------------------------------
# Logging setup
# --------------------------------------------------------------------------


def setup_logger() -> tuple[logging.Logger, str]:
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_filename = f"sent_log_{date_str}.txt"

    logger = logging.getLogger("mailforge")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(file_handler)

    return logger, log_filename


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="MailForge - bulk personalized email sender with dry-run preview and rate limiting."
    )
    parser.add_argument("--contacts", required=True, help="Path to contacts CSV (must include an 'email' column)")
    parser.add_argument("--template", required=True, help="Path to Jinja2 HTML email template")
    parser.add_argument("--dry-run", action="store_true", help="Generate HTML previews instead of sending")
    parser.add_argument("--rate", default="10/min", help="Send rate limit, e.g. '10/min', '5/sec' (default: 10/min)")
    parser.add_argument("--preview-dir", default="preview", help="Output directory for dry-run previews")
    parser.add_argument("--env-file", default=".env", help="Path to .env file with SMTP settings")
    return parser


def load_smtp_config(env_file: str) -> dict:
    load_dotenv(env_file)
    config = {
        "host": os.getenv("SMTP_HOST", "localhost"),
        "port": int(os.getenv("SMTP_PORT", "1025")),
        "user": os.getenv("SMTP_USER", ""),
        "password": os.getenv("SMTP_PASSWORD", ""),
        "use_tls": os.getenv("SMTP_USE_TLS", "false").strip().lower() in ("1", "true", "yes"),
        "from_addr": os.getenv("FROM_EMAIL", "noreply@example.com"),
        "from_name": os.getenv("FROM_NAME", ""),
    }
    return config


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

    try:
        parse_rate(args.rate)  # validate early
    except ValueError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1

    smtp_config = load_smtp_config(args.env_file)
    logger, log_filename = setup_logger()
    logger.info(
        "Starting send run: %d contacts, rate=%s, smtp=%s:%s",
        len(contacts),
        args.rate,
        smtp_config["host"],
        smtp_config["port"],
    )

    run_send(contacts, subject_tpl, body_tpl, smtp_config, args.rate, logger, log_filename)
    return 0


if __name__ == "__main__":
    sys.exit(main())

# Built incrementally - see git history for the development progression.
