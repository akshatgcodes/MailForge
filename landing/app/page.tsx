import { TerminalWindow } from "./components/Terminal";

const concepts = [
  "smtplib",
  "Jinja2 templating",
  "pandas",
  "CSV contact lists",
  "logging module",
  "retry on failure",
  "dry-run HTML preview",
  "send rate limiting",
  "argparse CLI",
];

function Badge({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center rounded-full border border-white/10 bg-white/[0.04] px-3.5 py-1.5 text-sm text-white/70 font-mono">
      {children}
    </span>
  );
}

function SectionKicker({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-[0.2em] text-[#7fe28a]/80">
      <span className="h-1.5 w-1.5 rounded-full bg-[#7fe28a]" />
      {children}
    </div>
  );
}

export default function Home() {
  return (
    <div className="relative flex flex-col">
      {/* ambient background glow */}
      <div
        aria-hidden
        className="pointer-events-none fixed inset-0 -z-10 overflow-hidden"
      >
        <div className="absolute left-1/2 top-[-10%] h-[560px] w-[560px] -translate-x-1/2 rounded-full bg-[#3fb950]/[0.08] blur-[120px]" />
        <div className="absolute right-[5%] top-[30%] h-[420px] w-[420px] rounded-full bg-[#4f8cf2]/[0.06] blur-[120px]" />
      </div>

      {/* NAV */}
      <header className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-6 sm:px-10">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-white/10 bg-white/[0.04] font-mono text-sm font-semibold text-[#7fe28a]">
            &gt;_
          </div>
          <span className="font-semibold tracking-tight">MailForge</span>
        </div>
        <Badge>GPLv3</Badge>
      </header>

      {/* HERO */}
      <section className="mx-auto w-full max-w-6xl px-6 pt-10 pb-20 sm:px-10 sm:pt-16 sm:pb-28">
        <div className="grid grid-cols-1 items-center gap-14 lg:grid-cols-[1.05fr_1fr]">
          <div>
            <SectionKicker>Python CLI · bulk personalized email</SectionKicker>
            <h1 className="mt-5 text-4xl font-semibold leading-[1.08] tracking-tight sm:text-5xl lg:text-[3.25rem]">
              Send hundreds of emails.
              <br />
              <span className="text-white/50">Know exactly what each one says.</span>
            </h1>
            <p className="mt-6 max-w-xl text-base leading-relaxed text-white/60 sm:text-lg">
              MailForge loads a CSV of contacts and a Jinja2 template with{" "}
              <code className="rounded bg-white/[0.06] px-1.5 py-0.5 font-mono text-[0.85em] text-white/80">
                {"{{name}}"}
              </code>{" "}
              /{" "}
              <code className="rounded bg-white/[0.06] px-1.5 py-0.5 font-mono text-[0.85em] text-white/80">
                {"{{company}}"}
              </code>{" "}
              placeholders, then sends each contact a uniquely personalized
              email — logging every send with automatic retry on failure.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-3">
              <div className="rounded-lg border border-[#7fe28a]/25 bg-[#7fe28a]/[0.08] px-4 py-2.5 font-mono text-sm text-[#7fe28a]">
                --dry-run before you send. Always.
              </div>
            </div>
          </div>

          <TerminalWindow
            title="mailforge.py"
            lines={[
              {
                type: "comment",
                text: "# Preview first, always",
              },
              {
                type: "command",
                text: "python mailforge.py --contacts leads.csv --template email.html --dry-run",
              },
              {
                type: "output",
                tone: "success",
                text: "✅ Previews generated in /preview (47 files) — open in browser to review",
              },
              { type: "output", text: "" },
              {
                type: "comment",
                text: "# Send when ready",
              },
              {
                type: "command",
                text: "python mailforge.py --contacts leads.csv --template email.html --rate 10/min",
              },
              {
                type: "output",
                tone: "success",
                text: "✅ 45/47 sent | ❌ 2 failed (logged) | 📋 sent_log_2024-04-22.txt",
              },
            ]}
          />
        </div>
      </section>

      {/* X FACTOR */}
      <section className="border-t border-white/[0.06] bg-white/[0.015]">
        <div className="mx-auto w-full max-w-6xl px-6 py-20 sm:px-10 sm:py-28">
          <SectionKicker>The X factor</SectionKicker>
          <h2 className="mt-4 max-w-2xl text-3xl font-semibold tracking-tight sm:text-4xl">
            Never send a mail merge blind.
          </h2>
          <p className="mt-4 max-w-2xl text-white/60">
            Most bulk-send scripts fire straight into your contacts&apos;
            inboxes. MailForge makes proofing and pacing first-class citizens
            of the workflow, not an afterthought.
          </p>

          <div className="mt-12 grid grid-cols-1 gap-6 md:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-[#0d0f13] p-7 sm:p-8">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#7fe28a]/10 text-lg">
                🔍
              </div>
              <h3 className="mt-5 text-lg font-semibold">
                Dry-run HTML preview
              </h3>
              <p className="mt-2.5 text-sm leading-relaxed text-white/60">
                Run with <code className="rounded bg-white/[0.06] px-1.5 py-0.5 font-mono text-white/80">--dry-run</code>{" "}
                and MailForge renders every single personalized email as its
                own HTML file in a local{" "}
                <code className="rounded bg-white/[0.06] px-1.5 py-0.5 font-mono text-white/80">/preview</code>{" "}
                folder — one file per contact, fully rendered with their real
                name and company. Open the folder in a browser and read
                through all 47 versions before a single message leaves your
                SMTP server. Typos, broken merge fields, and awkward phrasing
                get caught while they&apos;re still free to fix.
              </p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-[#0d0f13] p-7 sm:p-8">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#4f8cf2]/10 text-lg">
                ⏱
              </div>
              <h3 className="mt-5 text-lg font-semibold">
                Built-in send rate limiter
              </h3>
              <p className="mt-2.5 text-sm leading-relaxed text-white/60">
                Pass <code className="rounded bg-white/[0.06] px-1.5 py-0.5 font-mono text-white/80">--rate 10/min</code>{" "}
                and sends are throttled to a steady, human-plausible pace
                instead of blasting your entire list in one burst. Bursty
                sending is exactly what triggers spam filters and provider
                rate limits — pacing sends keeps your domain&apos;s
                reputation intact and your emails out of the junk folder.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* KEY CONCEPTS */}
      <section className="mx-auto w-full max-w-6xl px-6 py-20 sm:px-10 sm:py-28">
        <SectionKicker>Under the hood</SectionKicker>
        <h2 className="mt-4 text-3xl font-semibold tracking-tight sm:text-4xl">
          Small script, real engineering.
        </h2>
        <p className="mt-4 max-w-2xl text-white/60">
          No frameworks, no dashboard, no vendor lock-in — just a focused
          Python CLI built on the standard tools for the job.
        </p>
        <div className="mt-8 flex flex-wrap gap-2.5">
          {concepts.map((c) => (
            <Badge key={c}>{c}</Badge>
          ))}
        </div>
      </section>

      {/* RUN IT */}
      <section className="border-t border-white/[0.06] bg-white/[0.015]">
        <div className="mx-auto w-full max-w-6xl px-6 py-20 sm:px-10 sm:py-28">
          <SectionKicker>Run it</SectionKicker>
          <h2 className="mt-4 text-3xl font-semibold tracking-tight sm:text-4xl">
            Four commands, start to finish.
          </h2>

          <div className="mt-10 grid grid-cols-1 gap-10 lg:grid-cols-[1fr_1fr]">
            <ol className="space-y-6">
              <li className="flex gap-4">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-white/15 font-mono text-xs text-white/50">
                  1
                </span>
                <div>
                  <p className="font-medium text-white/85">
                    Install dependencies
                  </p>
                  <p className="mt-1 text-sm text-white/50">
                    pandas and Jinja2, pinned in requirements.txt.
                  </p>
                </div>
              </li>
              <li className="flex gap-4">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-white/15 font-mono text-xs text-white/50">
                  2
                </span>
                <div>
                  <p className="font-medium text-white/85">
                    Configure SMTP credentials
                  </p>
                  <p className="mt-1 text-sm text-white/50">
                    Copy .env.example to .env and fill in your mail server.
                  </p>
                </div>
              </li>
              <li className="flex gap-4">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-white/15 font-mono text-xs text-white/50">
                  3
                </span>
                <div>
                  <p className="font-medium text-white/85">
                    Preview every email
                  </p>
                  <p className="mt-1 text-sm text-white/50">
                    --dry-run renders the full batch to /preview — nothing
                    sends.
                  </p>
                </div>
              </li>
              <li className="flex gap-4">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-white/15 font-mono text-xs text-white/50">
                  4
                </span>
                <div>
                  <p className="font-medium text-white/85">Send, paced</p>
                  <p className="mt-1 text-sm text-white/50">
                    --rate 10/min throttles delivery and logs every result.
                  </p>
                </div>
              </li>
            </ol>

            <TerminalWindow
              title="setup"
              lines={[
                { type: "command", text: "pip install -r requirements.txt" },
                { type: "command", text: "cp .env.example .env" },
                { type: "output", text: "" },
                {
                  type: "command",
                  text: "python mailforge.py --contacts contacts.csv --template template.html --dry-run",
                },
                {
                  type: "output",
                  tone: "success",
                  text: "✅ Previews generated in /preview",
                },
                { type: "output", text: "" },
                {
                  type: "command",
                  text: "python mailforge.py --contacts contacts.csv --template template.html --rate 10/min",
                },
                {
                  type: "output",
                  tone: "success",
                  text: "✅ Sent — see sent_log_*.txt for the full run",
                },
              ]}
            />
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="mx-auto flex w-full max-w-6xl flex-col gap-4 border-t border-white/[0.06] px-6 py-10 text-sm text-white/40 sm:flex-row sm:items-center sm:justify-between sm:px-10">
        <div className="flex items-center gap-2 font-mono">
          <span className="text-[#7fe28a]">&gt;_</span> MailForge
        </div>
        <p>A personal portfolio project · licensed under GPLv3</p>
      </footer>
    </div>
  );
}
