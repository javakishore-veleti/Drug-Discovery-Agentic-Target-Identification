import { useState } from "react";
import type { TranscriptItem } from "../stream/types";
import { WhatHappenedModal, type WhatHappenedTurn } from "./WhatHappenedModal";

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
  const [happened, setHappened] = useState<WhatHappenedTurn | null>(null);

  return (
    <div className="transcript" aria-live="polite">
      {items.length === 0 ? (
        <p className="muted">
          Ask a research question to start a Chat Session — or pick an example
          from the dropdown above.
        </p>
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

            {item.done ? (
              <p className="what-happened-row">
                <button
                  type="button"
                  className="linkish"
                  onClick={() =>
                    setHappened({
                      tools: item.tools,
                      errors: item.errors,
                      debug: item.debug,
                      sessionId: item.sessionId,
                    })
                  }
                >
                  What happened now
                </button>
                <span className="muted small">
                  {" "}
                  — Bedrock request, host tools, and proof for this answer
                </span>
              </p>
            ) : null}

            {item.stalled ? (
              <div className="error-line">Stream stalled (soft 5-minute timeout).</div>
            ) : null}
            {!item.done && !item.stalled ? (
              <div className="muted small">Streaming…</div>
            ) : null}
          </div>
        );
      })}

      <WhatHappenedModal
        open={happened !== null}
        turn={happened}
        onClose={() => setHappened(null)}
      />
    </div>
  );
}
