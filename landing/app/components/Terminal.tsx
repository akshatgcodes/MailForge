type Line =
  | { type: "comment"; text: string }
  | { type: "command"; text: string }
  | { type: "output"; text: string; tone?: "default" | "success" | "error" };

const toneColor: Record<string, string> = {
  default: "text-[#c7cbd1]",
  success: "text-[#7fe28a]",
  error: "text-[#f28b82]",
};

export function TerminalWindow({
  title = "zsh",
  lines,
}: {
  title?: string;
  lines: Line[];
}) {
  return (
    <div className="w-full rounded-xl border border-white/10 bg-[#0d0f13] shadow-[0_20px_60px_-25px_rgba(0,0,0,0.8)] overflow-hidden">
      <div className="flex items-center gap-2 border-b border-white/10 bg-[#12151b] px-4 py-2.5">
        <span className="h-3 w-3 rounded-full bg-[#f2545b]/80" />
        <span className="h-3 w-3 rounded-full bg-[#f2b705]/80" />
        <span className="h-3 w-3 rounded-full bg-[#3fb950]/80" />
        <span className="ml-2 text-xs text-white/40 font-mono">{title}</span>
      </div>
      <div className="px-4 py-4 sm:px-5 sm:py-5 font-mono text-[13px] sm:text-sm leading-relaxed overflow-x-auto">
        {lines.map((line, i) => {
          if (line.type === "comment") {
            return (
              <div key={i} className="text-white/35">
                {line.text}
              </div>
            );
          }
          if (line.type === "command") {
            return (
              <div key={i} className="flex gap-2 text-white/90">
                <span className="text-[#7fe28a] select-none">$</span>
                <span className="whitespace-pre">{line.text}</span>
              </div>
            );
          }
          return (
            <div
              key={i}
              className={`whitespace-pre-wrap ${toneColor[line.tone ?? "default"]}`}
            >
              {line.text}
            </div>
          );
        })}
      </div>
    </div>
  );
}
