# MailForge — Product Requirements Document

**Status:** Final (v1 shipped)
**Owner:** Akshat Gupta
**One-liner:** A bulk personalised email sender that makes you preview every rendered email before anything goes out.

---

## 1. Problem

Cold outreach and small campaigns need one email per person, each with their name and company. Mail-merge tools make that easy, but they also make it easy to send fifty copies of "Hi {{ name }}," or the wrong company name before you notice. Sending too fast from a personal SMTP account also gets you flagged. What's missing is a forced look at every rendered email first, and a polite, logged send.

---

## 2. Goals (v1)

1. Load contacts from a CSV with at least an `email` column. Every column is available to the template.
2. Render a personalised subject and HTML body per contact from one Jinja2 template.
3. `--dry-run` writes every rendered email to its own HTML file and sends nothing.
4. Send through real SMTP (`smtplib`), with STARTTLS and login when configured.
5. Rate-limit sends (`10/min`, `5/sec`, `120/hour`).
6. Retry each failed send once, and log every attempt to a dated audit file.

---

## 3. Non-Goals (explicit scope cuts)

- **Open or click tracking** — no pixels, no link rewriting.
- **Unsubscribe handling** — no list management. You're responsible for consent.
- **Scheduling** — runs when you run it.
- **Attachments** — HTML and plain text only.
- **A web UI** — command line only.

---

## 4. Users

**Primary:** Someone sending a personalised batch (job outreach, event invites, a small campaign) from their own SMTP account.

**Secondary:** Engineers reviewing a careful `smtplib` send path with previews, retries and an audit log.

---

## 5. User Stories

1. *As a sender,* I run `--dry-run` so that I can open every rendered email in a browser and proofread it.
2. *As a sender,* I use `{{ company }}` in the subject so that each subject line is personalised too.
3. *As a sender,* I send with `--rate 10/min` so that my SMTP provider doesn't flag me.
4. *As a sender,* I check `sent_log_YYYY-MM-DD.txt` so that I know exactly who got an email and who failed.
5. *As a sender,* I see a contact with no email address skipped and logged, instead of crashing the run.

---

## 6. Functional Requirements

### 6.1 Inputs

- `--contacts` (CSV, required), `--template` (HTML, required), `--dry-run`, `--rate` (default `10/min`), `--preview-dir` (default `preview`), `--env-file` (default `.env`).

### 6.2 Template

- Jinja2 HTML. The subject comes from the first `<!-- SUBJECT: ... -->` comment, which is removed from the body. Without one, the subject is "A message for you".
- Every CSV column is a template variable.

### 6.3 Dry run

- Writes `NNN_<slug-of-email>.html` per contact into `--preview-dir`, with a header showing To and Subject, then the rendered body.

### 6.4 Sending

- Each email is `multipart/alternative`: a plain-text part (simple HTML-to-text) and the HTML part.
- `From` uses `FROM_NAME <FROM_EMAIL>`.
- The rate is turned into a fixed sleep between sends (`10/min` = 6 s).
- Up to 2 attempts per contact, 2 s apart. Then "GIVE UP" is logged and the contact counts as failed.
- Contacts with no email are skipped and logged as errors.

### 6.5 Logging

- Every SUCCESS, FAILED attempt, GIVE UP and SKIPPED line is appended with a timestamp to `sent_log_YYYY-MM-DD.txt`.
- The run ends with a summary: sent, failed, and the log file name.

---

## 7. Non-Functional Requirements

- **Safety:** nothing is sent without SMTP settings, and `--dry-run` never opens a connection.
- **Secrets:** SMTP credentials only come from `.env` (gitignored).
- **Politeness:** sends are rate-limited by default (10 per minute).
- **Auditability:** every attempt is in a plain-text log.

---

## 8. Success Metrics

| Metric | Target |
|---|---|
| Preview accuracy | Each preview's body is the exact HTML that would be sent, under a To / Subject header |
| Delivery | All sample contacts are received by a local debug SMTP server |
| Failure handling | A refused connection gives 2 FAILED lines and 1 GIVE UP per contact |

---

## 9. Risks & Open Questions

- **No autoescaping** — Jinja2 runs with autoescape off, so HTML inside a CSV value is inserted as-is into the email.
- **Consent** — the tool doesn't check consent or handle unsubscribes. That's the sender's responsibility.
- **Provider limits** — the default rate is conservative, but providers' daily caps still apply.

---

## 10. v2 Candidates

- Autoescaping, with an explicit `|safe` for intentional HTML.
- A `--limit N` flag to send a small test batch first.
- Resume from the log, skipping contacts already marked SUCCESS.

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
