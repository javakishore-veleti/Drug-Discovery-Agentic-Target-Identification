import type { TranscriptItem } from "../stream/types";

function formatIds(ids?: { pmid?: string[]; nct?: string[]; chembl?: string[] }) {
  if (!ids) return "";
  const parts: string[] = [];
  if (ids.pmid?.length) parts.push(`PMID ${ids.pmid.join(", ")}`);
  if (ids.nct?.length) parts.push(ids.nct.join(", "));
  if (ids.chembl?.length) parts.push(ids.chembl.join(", "));
  return parts.join(" · ");
}

type Props = {
  items: TranscriptItem[];
};

export function Transcript({ items }: Props) {
  return (
    <div className="transcript" aria-live="polite">
      {items.length === 0 ? (
        <p className="muted">Ask a research question to start a Chat Session.</p>
      ) : null}
      {items.map((item) => {
        if (item.kind === "user") {
          return (
            <div key={item.id} className="bubble user">
              <div className="label">You</div>
              <div>{item.text}</div>
            </div>
          );
        }
        return (
          <div key={item.id} className="bubble assistant">
            <div className="label">Research agent</div>
            {item.reasoning.map((r, i) => (
              <div key={`r-${i}`} className="reasoning">
                {r}
              </div>
            ))}
            {item.tools.map((t, i) => (
              <div
                key={`t-${i}`}
                className={`tool ${t.phase}${t.status === "error" ? " err" : ""}`}
              >
                {t.phase === "use" ? (
                  <>
                    tool_use: <strong>{t.tool}</strong>
                  </>
                ) : (
                  <>
                    tool_result: <strong>{t.tool}</strong> ({t.status || "ok"})
                    {formatIds(t.ids) ? ` — ${formatIds(t.ids)}` : ""}
                    {t.message ? ` — ${t.message}` : ""}
                  </>
                )}
              </div>
            ))}
            {item.errors.map((err, i) => (
              <div key={`e-${i}`} className="error-line" role="alert">
                {err}
              </div>
            ))}
            {item.answer ? <div className="answer">{item.answer}</div> : null}
            {item.stalled ? (
              <div className="error-line">Stream stalled (soft 5-minute timeout).</div>
            ) : null}
            {!item.done && !item.stalled ? (
              <div className="muted small">Streaming…</div>
            ) : null}
          </div>
        );
      })}
    </div>
  );
}
