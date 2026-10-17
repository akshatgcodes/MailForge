# Local Setup — MailForge

> **Project page:** [mailforge.akshatgcodes.in](https://mailforge.akshatgcodes.in)
> MailForge is a command-line tool, so it runs on your machine. This guide covers installing, configuring and testing it safely.

---

## Prerequisites

- Python 3.8+
- An SMTP account for real sends (or `aiosmtpd` for local testing)

---

## 1. Clone and install

```bash
git clone https://github.com/akshatgcodes/MailForge
cd MailForge
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## 2. Environment variables

```bash
cp .env.example .env
```

| Variable | Where to get it |
|---|---|
| `SMTP_HOST` / `SMTP_PORT` | Your provider's SMTP server, e.g. `smtp.gmail.com` / `587`. Defaults to `localhost` / `1025` |
| `SMTP_USER` / `SMTP_PASSWORD` | Your SMTP login. For Gmail, an App Password from myaccount.google.com/apppasswords. Leave blank for no auth |
| `SMTP_USE_TLS` | `true` to run STARTTLS before login |
| `FROM_EMAIL` / `FROM_NAME` | The sender shown in the `From:` header |

---

## 3. Prepare contacts and a template

`contacts.csv` needs an `email` column. Every other column becomes a template variable:

```csv
name,email,company,role
Jane Doe,jane.doe@example.com,Acme Corp,Head of Marketing
```

`template.html` is Jinja2 HTML. The subject goes in a comment at the top:

```html
<!-- SUBJECT: Quick question for {{ company }}, {{ name }} -->
<html><body><p>Hi {{ name }},</p></body></html>
```

---

## 4. Run

Always preview first:

```bash
python mailforge.py --contacts contacts.csv --template template.html --dry-run
```

Open the files in `preview/` and check every version. Then send:

```bash
python mailforge.py --contacts contacts.csv --template template.html --rate 10/min
```

| Flag | Default | What it does |
|---|---|---|
| `--contacts` | required | Contacts CSV |
| `--template` | required | Jinja2 HTML template |
| `--dry-run` | off | Write previews instead of sending |
| `--rate` | `10/min` | `N/sec`, `N/min` or `N/hour` |
| `--preview-dir` | `preview` | Where previews go |
| `--env-file` | `.env` | SMTP settings file |

Every attempt is logged to `sent_log_YYYY-MM-DD.txt`.

---

## 5. Test the real send path safely

Run a local SMTP server that prints messages and never delivers them:

```bash
pip install aiosmtpd
python3 -m aiosmtpd -n -l localhost:1025
```

Keep the `.env.example` defaults (`localhost:1025`, no auth, no TLS) and send with `--rate 60/min`. Each rendered email shows up in the `aiosmtpd` terminal. To test retries, point `SMTP_PORT` at a closed port: every contact should log two FAILED attempts and a GIVE UP.

---

## 6. Project page (optional)

```bash
cd landing && npm install && npm run dev   # http://localhost:3000
```

See [DEPLOY.md](DEPLOY.md) for how it's hosted.

---

## Testing

There's no automated test suite yet. CI checks that every Python file compiles and that the project page lints and builds. Use the `aiosmtpd` steps above to test sending by hand.

---

## Known limitations

- Jinja2 autoescape is off, so HTML in a CSV value is inserted as-is.
- There's no resume. Re-running sends to everyone again, so check the log first.

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
