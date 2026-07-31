import { useEffect, useId, useRef } from "react";
import type { SourceIds, TurnDebug } from "../stream/types";

export type WhatHappenedTurn = {
  tools: Array<{
    tool: string;
    phase: "use" | "result";
    status?: string;
    ids?: SourceIds;
    message?: string;
  }>;
  errors: string[];
  debug?: TurnDebug;
  sessionId?: string;
};

type Props = {
  open: boolean;
  turn: WhatHappenedTurn | null;
  onClose: () => void;
};

function formatIds(ids?: SourceIds) {
  if (!ids) return "";
  const parts: string[] = [];
  if (ids.pmid?.length) parts.push(`PMID ${ids.pmid.join(", ")}`);
  if (ids.nct?.length) parts.push(ids.nct.join(", "));
  if (ids.chembl?.length) parts.push(ids.chembl.join(", "));
  return parts.join(" · ");
}

function asRecords(value: unknown): Array<Record<string, unknown>> {
  if (!Array.isArray(value)) return [];
  return value.filter((x): x is Record<string, unknown> => !!x && typeof x === "object");
}

export function WhatHappenedModal({ open, turn, onClose }: Props) {
  const titleId = useId();
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;
    closeRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open || !turn) return null;

  const debug = turn.debug;
  const requested = debug?.toolsRequestedByBedrock === true;
  const executed = debug?.toolsExecutedOnHost === true;
  const activity = asRecords(debug?.toolActivity);
  const bedrockRequests = activity.filter((a) => a.phase === "requested_by_bedrock");
  const hostResults = activity.filter((a) => a.executedLocally === true);
  const toolUses = turn.tools.filter((t) => t.phase === "use");
  const toolResults = turn.tools.filter((t) => t.phase === "result");

  return (
    <div
      className="modal-backdrop"
      role="presentation"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        className="modal-panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
      >
        <header className="modal-header">
          <h2 id={titleId}>What happened now</h2>
          <button
            ref={closeRef}
            type="button"
            className="ghost"
            onClick={onClose}
            aria-label="Close"
          >
            Close
          </button>
        </header>

        <div className="modal-body">
          <p className="muted">
            This is the story of the answer you just got — not the generic
            architecture overview.
          </p>

          <p className="host-definition">
            <strong>Where does the lookup happen?</strong> On{" "}
            <strong>your Mac</strong>, not in Bedrock. Bedrock only sends a tool
            instruction (“please run pubmed…”). Your Mac calls PubMed / ChEMBL /
            ClinicalTrials / Open Targets over HTTP, then sends those results
            back to Bedrock for the final answer. Bedrock never opens those sites.
          </p>

          <ol className="arch-steps">
            <li>
              <strong>Your browser</strong> sent the prompt to Stream on your Mac
              (<code>:8787</code>)
              {debug?.agentId ? (
                <>
                  {" "}
                  with <code>agentId={debug.agentId}</code>
                </>
              ) : null}
              .
            </li>
            <li>
              <strong>Your Mac</strong> called <strong>Bedrock</strong> (billable)
              with the prompt and available tool names, using your AWS credentials.
            </li>
            <li>
              <strong>Bedrock</strong>{" "}
              {requested
                ? "did not look anything up. It only replied to your Mac with a tool instruction (e.g. “please run pubmed with this query”) instead of finishing the answer. No PubMed/ChEMBL traffic leaves AWS for that step."
                : "answered from the model alone this turn (no tool instruction to your Mac)."}
            </li>
            <li>
              <strong>Your Mac</strong>{" "}
              {executed
                ? "is where the lookup happens: it HTTP-calls PubMed / ChEMBL / ClinicalTrials / Open Targets, then calls Bedrock again with those results so Bedrock can write the final answer."
                : "did not run any tools this turn — so no evidence lookup happened anywhere."}
            </li>
            <li>
              <strong>UI</strong> showed tool lines and the final answer from the
              Stream response.
            </li>
          </ol>

          <div className="turn-debug-badges">
            <span className={requested ? "badge ok" : "badge no"}>
              Model said “use a tool”: {requested ? "yes" : "no"}
            </span>
            <span className={executed ? "badge ok" : "badge no"}>
              Your Mac ran the tool: {executed ? "yes" : "no"}
            </span>
          </div>

          <div className="turn-debug-grid">
            <div>
              <h4>Lookups the model asked your Mac to run</h4>
              <p className="muted small">
                Each line is a separate instruction. Seeing <strong>pubmed</strong>{" "}
                several times is normal: the model often runs{" "}
                <em>different search queries</em> (pathway, ADCC, resistance, …)
                in one turn — not a bug and not Bedrock hitting PubMed itself.
              </p>
              {bedrockRequests.length === 0 && toolUses.length === 0 ? (
                <p className="muted small">None.</p>
              ) : bedrockRequests.length > 0 ? (
                <ol>
                  {bedrockRequests.map((r, i) => (
                    <li key={`br-${i}`}>
                      <strong>
                        #{i + 1} {String(r.tool || "tool")}
                      </strong>
                      {r.input ? (
                        <pre className="mini-pre">
                          {JSON.stringify(r.input, null, 2)}
                        </pre>
                      ) : null}
                    </li>
                  ))}
                </ol>
              ) : (
                <ol>
                  {toolUses.map((t, i) => (
                    <li key={`u-${i}`}>
                      <strong>
                        #{i + 1} {t.tool}
                      </strong>
                    </li>
                  ))}
                </ol>
              )}
            </div>
            <div>
              <h4>What the host (your Mac) returned</h4>
              <p className="muted small">
                Results from adapters on this laptop — not from Bedrock.
              </p>
              {toolResults.length === 0 && hostResults.length === 0 ? (
                <p className="muted small">No tool_result — tools did not run on your Mac.</p>
              ) : (
                <ul>
                  {toolResults.map((t, i) => (
                    <li key={`tr-${i}`}>
                      <strong>
                        {t.tool} ({t.status || "ok"})
                      </strong>
                      {formatIds(t.ids) ? (
                        <div className="small">{formatIds(t.ids)}</div>
                      ) : null}
                      {t.message ? (
                        <div className="small">{t.message}</div>
                      ) : null}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {turn.errors.length > 0 ? (
            <div className="error-line">
              Errors this turn: {turn.errors.join(" · ")}
            </div>
          ) : null}

          {debug ? (
            <details className="turn-debug-raw">
              <summary>Raw turn debug JSON</summary>
              <pre className="arch-flow">{JSON.stringify(debug, null, 2)}</pre>
            </details>
          ) : (
            <p className="muted small">
              No debug payload on this turn. Restart Stream (
              <code>npm run local:up</code>) and send a new prompt.
            </p>
          )}

          {typeof debug?.bedrockCallCount === "number" ? (
            <p>
              <strong>Bedrock calls this turn:</strong> {debug.bedrockCallCount}
              {debug.bedrockModelId ? (
                <>
                  {" "}
                  · model <code>{debug.bedrockModelId}</code>
                </>
              ) : null}
              {debug.bedrockTraceUrl ? (
                <>
                  {" "}
                  ·{" "}
                  <a href={debug.bedrockTraceUrl} target="_blank" rel="noreferrer">
                    live HTML trace
                  </a>
                </>
              ) : null}
            </p>
          ) : null}

          {debug?.savedTo ? (
            <p className="muted small">
              Saved on disk: <code>{debug.savedTo}</code>
            </p>
          ) : null}
        </div>
      </div>
    </div>
  );
}
