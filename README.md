# MailForge

A bulk personalized email sender for cold outreach and campaigns. Load a CSV
of contacts, write one Jinja2 HTML template with `{{ name }}` / `{{ company }}`
style placeholders, and MailForge renders and sends a unique email to every
contact — with a full audit log of every send attempt.

**Month:** April 2024 &nbsp;|&nbsp; **Language:** Python &nbsp;|&nbsp; **Type:** CLI Tool

## The X Factor

Most cold-email tools let you fire off a merge job and hope for the best.
MailForge doesn't let you send anything until you've actually looked at it:

- **Dry-run preview mode** (`--dry-run`) — instead of sending, MailForge
  renders every single personalized email as its own HTML file in
  `/preview`. Open them in a browser and proofread every version — the
  actual subject line, the actual "Hi Jane," the actual company name — for
  every contact, before a single email goes out.
- **Send rate limiter** (`--rate 10/min`) — when you do send, MailForge
  paces the sends (`time.sleep` between each one) so you don't blast your
  SMTP provider and get flagged as spam.

## Key concepts demonstrated

- `smtplib` — real SMTP connections, MIME message construction
  (`multipart/alternative` with plaintext + HTML parts), STARTTLS/auth support
- `jinja2` — per-contact template rendering, including a templated subject
  line pulled from an `<!-- SUBJECT: ... --> ` comment in the template file
- `pandas` — loading and iterating the contacts CSV
- Dry-run mode with HTML preview generation to `/preview`
- `logging` — a dated, append-only audit trail (`sent_log_YYYY-MM-DD.txt`) of
  every send attempt: success, failure, and retries, with timestamps
- Rate limiting via `time.sleep` between sends
- Retry-on-failure (one retry per contact, with a short backoff) so a
  transient SMTP hiccup doesn't silently drop a contact

## Project layout

```
mailforge.py       # the CLI
contacts.csv        # sample contact list (name, email, company, role)
template.html        # sample Jinja2 HTML email template
.env.example          # SMTP config template (copy to .env)
requirements.txt
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your SMTP details
```

Your contacts CSV must have at least an `email` column; any other columns
(`name`, `company`, `role`, ...) become placeholders you can use in the
template with `{{ column_name }}`.

The template file is plain HTML rendered with Jinja2. The subject line is
declared via a special comment at the top of the file:

```html
<!-- SUBJECT: Quick question for {{ company }}, {{ name }} -->
<html>
  <body>
    <p>Hi {{ name }},</p>
    ...
  </body>
</html>
```

## Run it

Always preview first:

```bash
python mailforge.py --contacts contacts.csv --template template.html --dry-run
```

```
✅ Previews generated in /preview (5 files) — open in browser to review
```

Open the files in `/preview` in a browser and check every personalized
version. When you're happy, send for real (rate-limited):

```bash
python mailforge.py --contacts contacts.csv --template template.html --rate 10/min
```

```
✅ 45/47 sent | ❌ 2 failed (logged) | 📋 sent_log_2024-04-22.txt
```

Every attempt (success, failure, and each retry) is appended to the dated
`sent_log_YYYY-MM-DD.txt` file with a timestamp.

### CLI flags

| Flag | Description |
|---|---|
| `--contacts` | Path to contacts CSV (must include an `email` column) |
| `--template` | Path to the Jinja2 HTML email template |
| `--dry-run` | Generate HTML previews in `/preview` instead of sending |
| `--rate` | Send rate limit, e.g. `10/min`, `5/sec`, `120/hour` (default `10/min`) |
| `--preview-dir` | Output directory for dry-run previews (default `preview`) |
| `--env-file` | Path to the `.env` file with SMTP settings (default `.env`) |

### SMTP configuration (`.env`)

| Variable | Meaning |
|---|---|
| `SMTP_HOST` / `SMTP_PORT` | Your SMTP server |
| `SMTP_USER` / `SMTP_PASSWORD` | Auth credentials (leave blank if not required) |
| `SMTP_USE_TLS` | `true` to call `starttls()` before sending |
| `FROM_EMAIL` / `FROM_NAME` | The sender identity used in the `From:` header |

## How the send path was tested safely (no real emails, no real SMTP creds)

The spec requires a *real* `smtplib` send path — not a stub — but this must
never contact a live mail server or a real inbox. To satisfy both:

1. A **local, throwaway debug SMTP server** was run on the same machine with
   [`aiosmtpd`](https://pypi.org/project/aiosmtpd/) (the modern replacement
   for the deprecated stdlib `python -m smtpd`, which was removed in recent
   Python versions):

   ```bash
   python3 -m aiosmtpd -n -l localhost:1025
   ```

   This server accepts real SMTP connections on `localhost:1025` and prints
   every received message to stdout — it never relays or delivers anything
   anywhere.

2. `.env` was pointed at `SMTP_HOST=localhost`, `SMTP_PORT=1025` (see
   `.env.example`), and `mailforge.py --rate 60/min` was run against a small
   sample contacts file. This exercises the **real** code path: a real
   `smtplib.SMTP` connection, a real MIME message, and a real SMTP `DATA`
   transaction — captured and printed locally by the debug server, confirming
   the subject and body were rendered correctly per contact.

3. **Retry-on-failure** was verified by pointing `SMTP_HOST`/`SMTP_PORT` at a
   closed port so the connection is refused. MailForge logged the first
   failed attempt, retried once after a short backoff, logged the second
   failure, and then logged a final "give up" line and counted the contact
   as failed in the run summary — confirming the retry and failure-logging
   logic both work.

4. **Rate limiting** was verified by timing a run against multiple contacts
   at a known rate (e.g. `--rate 60/min` → 1 second between sends) and
   confirming the wall-clock time matched the expected number of
   `time.sleep` pauses.

No real SMTP credentials were configured anywhere in this project, and no
email address outside the bundled sample `contacts.csv` (all `@example.com`,
a reserved non-routable domain) was ever used.

## Notes / deviations from spec

- The subject line is templated via an `<!-- SUBJECT: ... -->` comment at
  the top of the HTML template rather than a separate `--subject` CLI flag,
  so the whole personalized email (subject + body) lives in one template
  file per the "write a Jinja2 template" framing in the spec.
- `python -m smtpd -c DebuggingServer` (mentioned in the original task as an
  option) is deprecated and removed as of Python 3.12+; `aiosmtpd` was used
  instead as it's the documented modern replacement and behaves the same
  way (a local, non-relaying debug SMTP sink).

## Notes

Built as a focused, single-purpose tool - a bulk personalized email sender, nothing more, nothing less.

## Troubleshooting

If something doesn't run as expected, double-check you're using the dependency versions noted above and running the exact commands from the "Run it" section.
