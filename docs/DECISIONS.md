# Engineering Decisions — MailForge

---

## Decision 1 — Previews are a first-class mode

**Context:** Merge mistakes (a missing column, the wrong company) only show up once the email is in someone's inbox.

**Decision:** `--dry-run` renders every contact's email, subject included, to its own HTML file in `preview/`, with a header showing To and Subject. Nothing is sent.

**Reason:** You proofread the real output, not the template. The same `render_email()` is used for previews and sends, so what you see is what goes out.

**Tradeoff:** One file per contact. For thousands of contacts you'd spot-check rather than read them all.

---

## Decision 2 — The subject line lives in the template

**Context:** The subject needs the same personalisation as the body.

**Decision:** The first `<!-- SUBJECT: ... -->` comment in the template is the subject template, and it's removed from the body before rendering.

**Reason:** One file holds the whole email. There's no `--subject` flag to keep in sync, and HTML comments don't render even if left in.

**Tradeoff:** It's a convention you have to know. Without it, the subject falls back to "A message for you".

---

## Decision 3 — A fixed sleep between sends

**Context:** Sending a batch too fast from a personal SMTP account looks like spam.

**Decision:** `--rate N/unit` is converted to seconds between sends (`10/min` → 6 s), with `time.sleep` after each contact.

**Reason:** It's simple and predictable, and easy to verify by timing a run. Sends are one at a time, so there's no concurrency to manage.

**Tradeoff:** A slow SMTP response adds to the gap, so the real rate is slightly below the target.

---

## Decision 4 — One retry, then give up, all logged

**Context:** A transient SMTP hiccup shouldn't silently drop a contact, and a dead server shouldn't stall the run forever.

**Decision:** Up to 2 attempts per contact, 2 s apart. Every attempt is logged as SUCCESS or FAILED, and a final GIVE UP marks the contact as failed in the summary.

**Reason:** It covers one-off blips without hammering a server that's down, and the log shows exactly what happened to each address.

**Tradeoff:** A longer outage fails everyone after it, with no resume yet.

---

## Decision 5 — Real SMTP, tested against a local debug server

**Context:** The send path should be real `smtplib`, but testing must never reach a real inbox.

**Decision:** Test with `aiosmtpd` on `localhost:1025`, which accepts SMTP and prints messages without relaying them. `.env.example` points at it by default.

**Reason:** It exercises the real connection, MIME build and `DATA` transaction. Retries were checked by pointing at a closed port, and rate limiting by timing a run.

**Tradeoff:** It doesn't test provider-specific behaviour like Gmail's limits or app passwords.

---

## What I'd do differently in v2

- **Autoescape on** in Jinja2, with `|safe` for intentional HTML.
- **Resume from the log**, skipping addresses already marked SUCCESS.
- **`--limit N`** to send a small test batch first.

---

## Explicit non-decisions (deferred to v2)

| Feature | Why deferred |
|---|---|
| Open / click tracking | Privacy-invasive and needs a hosted endpoint |
| Unsubscribe management | Needs a list store and a hosted link |
| Attachments | Most outreach doesn't need them, and they raise spam scores |

---

<div align="center">

<h3>Akshat Gupta</h3>

<a href="https://akshatgcodes.in"><img src="https://img.shields.io/badge/Website-akshatgcodes.in-111111?style=flat-square&logo=googlechrome&logoColor=white" alt="Website"></a>
<a href="https://linkedin.com/in/akshatgcodes"><img src="https://img.shields.io/badge/LinkedIn-akshatgcodes-0A66C2?style=flat-square" alt="LinkedIn"></a>
<a href="https://github.com/akshatgcodes"><img src="https://img.shields.io/badge/GitHub-akshatgcodes-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"></a>
<a href="mailto:akshatgcodes@gmail.com"><img src="https://img.shields.io/badge/Email-akshatgcodes%40gmail.com-EA4335?style=flat-square&logo=gmail&logoColor=white" alt="Email"></a>

</div>
