<p align="center">
  <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24"
       fill="none" stroke="#7fe28a" stroke-width="1.5"
       stroke-linecap="round" stroke-linejoin="round">
    <rect width="20" height="16" x="2" y="4" rx="2"/>
    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
  </svg>
</p>

<h1 align="center">MailForge</h1>

<p align="center">
  <strong>A bulk personalised email sender that makes you preview every rendered email before anything goes out.</strong>
</p>

<p align="center">
  <a href="https://mailforge.akshatgcodes.in">
    <img src="https://img.shields.io/badge/project_page-7fe28a-7fe28a?style=flat-square" alt="Project page">
  </a>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Jinja2-B41717?style=flat-square&logo=jinja&logoColor=white" alt="Jinja2">
  <img src="https://img.shields.io/badge/pandas-150458?style=flat-square&logo=pandas&logoColor=white" alt="pandas">
  <img src="https://img.shields.io/badge/license-GPL--3.0-7fe28a?style=flat-square" alt="License">
</p>

---

## What is MailForge?

MailForge sends one personalised email per row of a contacts CSV, rendered from a single Jinja2 HTML template. Most merge tools let you fire and hope. MailForge's `--dry-run` renders every single email as its own HTML file first, with the real subject, the real "Hi Jane" and the real company name, so you can proofread them all before one is sent. Then it sends at a rate you set and logs every attempt.

> **Project page →** [mailforge.akshatgcodes.in](https://mailforge.akshatgcodes.in)
> It's a CLI: `pip install -r requirements.txt && python mailforge.py --contacts contacts.csv --template template.html --dry-run`

```
✅ Previews generated in /preview (5 files) — open in browser to review
✅ 45/47 sent | ❌ 2 failed (logged) | 📋 sent_log_2024-04-22.txt
```

---

## What you get

- **Dry-run previews** — one HTML file per contact in `preview/`, exactly as it would be sent.
- **One template, any columns** — every CSV column becomes a `{{ placeholder }}`, and the subject comes from a `<!-- SUBJECT: ... -->` comment.
- **Rate limiting** — `--rate 10/min`, `5/sec` or `120/hour`, so you don't get flagged as spam.
- **Retry + audit log** — one retry per contact, and every attempt goes to `sent_log_YYYY-MM-DD.txt`.
- **Real email format** — `multipart/alternative` with a plain-text part and an HTML part, with STARTTLS and auth supported.

---

## Stack

| Layer | Tech |
|---|---|
| Language | Python 3.8+ |
| Templating | Jinja2 |
| Contacts | pandas (CSV) |
| Sending | `smtplib` · `email.mime` |
| Config | `python-dotenv` |
| Project page | Next.js 16 on Vercel · GoDaddy DNS |

---

## Engineering Decisions

**Why make previews a first-class mode?**
A merge bug ("Hi {{ name }},", the wrong company) is invisible until it's in someone's inbox. Rendering every email to a file first turns that into a five-second check.

**Why put the subject in the template?**
`<!-- SUBJECT: ... -->` keeps the subject and body in one file, so both are personalised the same way and previewed together.

**Why a fixed sleep instead of a token bucket?**
The rate is turned into seconds between sends. It's simple, predictable, and easy to verify by timing a run.

**What would you do differently in v2?**
Turn on Jinja2 autoescaping, so a stray `<` in a CSV value can't change the email's HTML.

---

## Docs

| Document | Description |
|---|---|
| [PRD](docs/PRD.md) | Product requirements — goals, user stories, non-goals |
| [Architecture](docs/ARCHITECTURE.md) | Send pipeline, template format, logging |
| [Decisions](docs/DECISIONS.md) | Every major technical decision and why |
| [Setup](docs/SETUP.md) | Install, SMTP config, safe local testing |
| [Deploy](docs/DEPLOY.md) | How the project page is deployed |
| [Contributing](CONTRIBUTING.md) | How to propose changes |
| [Changelog](CHANGELOG.md) | What changed in each release |
| [Security](SECURITY.md) | How to report a vulnerability |

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
