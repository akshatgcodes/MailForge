# MailForge — Architecture

---

## 1. Stack

| Layer | Tech |
|---|---|
| Language | Python 3.8+ |
| CLI | `argparse` |
| Contacts | pandas `read_csv` |
| Templating | Jinja2 `Environment().from_string` |
| Email | `email.mime` (`MIMEMultipart("alternative")`, `MIMEText`) · `smtplib.SMTP` |
| Config | `python-dotenv` |
| Logging | `logging` to a dated file |
| Project page | Next.js 16 static site in `landing/`, on Vercel |

---

## 2. Components

```
mailforge.py   the whole tool: arg parsing, contacts, template, dry run, send loop, logging
template.html  sample template with a <!-- SUBJECT: ... --> line
contacts.csv   sample contacts (all @example.com)
.env.example   SMTP settings, names only
landing/       Next.js project page
```

| Function | Role |
|---|---|
| `parse_rate("10/min")` | Returns seconds between sends (here 6.0) |
| `load_contacts(csv)` | pandas → list of row dicts |
| `load_template(path)` | Pulls out the `SUBJECT:` comment and returns `(subject_tpl, body_tpl)` |
| `render_email(...)` | Renders the subject and body with the row's columns |
| `run_dry_run(...)` | Writes one preview HTML file per contact |
| `build_message(...)` | Builds `multipart/alternative` with plain text + HTML |
| `send_via_smtp(...)` | Connects (15 s timeout), optional STARTTLS and login, then `sendmail` |
| `run_send(...)` | Loop: render → send with retry → log → sleep |
| `load_smtp_config(env)` | Reads `SMTP_*` and `FROM_*` from `.env` |

---

## 3. Data Flow

```
contacts.csv ──► load_contacts ──► rows
template.html ─► load_template ──► subject_tpl, body_tpl

--dry-run:
  for row: render ──► preview/NNN_<email-slug>.html

send:
  for row:
    no email? ──► log SKIPPED, continue
    render ──► build_message
    attempt 1 ──► send_via_smtp ──► SUCCESS? log, done
                       └─ fail ──► log FAILED 1/2, sleep 2 s
    attempt 2 ──► send_via_smtp ──► SUCCESS? log, done
                       └─ fail ──► log FAILED 2/2, log GIVE UP
    sleep(seconds from --rate)
  print "✅ N/M sent | ❌ K failed | 📋 sent_log_YYYY-MM-DD.txt"
```

---

## 4. Template Format

```html
<!-- SUBJECT: Quick question for {{ company }}, {{ name }} -->
<html>
  <body>
    <p>Hi {{ name }},</p>
    <p>I saw {{ company }} is hiring for {{ role }}…</p>
  </body>
</html>
```

The first `SUBJECT:` comment becomes the subject template and is removed from the body. Every CSV column (`name`, `email`, `company`, `role`, …) is a variable.

---

## 5. Security

- **Credentials:** `SMTP_USER` and `SMTP_PASSWORD` are only read from `.env`, which is gitignored and never logged.
- **Transport:** with `SMTP_USE_TLS=true`, `starttls()` runs before login.
- **Dry run:** never opens an SMTP connection.
- **Templating:** autoescape is off, so CSV values are inserted as raw HTML. Use contact data you trust.
- **Logs:** they contain recipient addresses and subjects, and are gitignored (`sent_log_*.txt`).

---

## 6. Error Handling & Reliability

| Failure | Behaviour |
|---|---|
| Bad `--rate` | `ValueError` with the expected format, and nothing is sent |
| Row without an email | Logged as SKIPPED; the run continues |
| SMTP connect or send error | Logged as FAILED; one retry after 2 s; then GIVE UP and counted as failed |
| Template without `SUBJECT:` | Subject "A message for you" |

---

## 7. Deployment

The CLI isn't hosted. It's installed and run locally. The project page in `landing/` is a Vercel project with root directory `landing`, deployed on every push to `master` (see [DEPLOY.md](DEPLOY.md)).

---

## 8. Explicit Scope Cuts

- **Tracking, unsubscribe and scheduling** — out of scope for a personal sender.
- **Attachments** — text and HTML only.
- **Concurrency** — sends happen one at a time by design, so the rate limit holds.

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
