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
            <strong>Host</strong> means <strong>your Mac</strong> — the machine
            running local Stream (<code>local/stream_app.py</code> on{" "}
            <code>:8787</code>). It is <em>not</em> Bedrock, Cognito, or a remote
            server. PubMed/ChEMBL adapters run here; Bedrock only plans and writes
            the answer in AWS.
          </p>

          <ol className="arch-steps">
            <li>
              <strong>Your browser</strong> POSTed the prompt to the host Stream
              at <code>:8787</code>
              {debug?.agentId ? (
                <>
                  {" "}
                  with <code>agentId={debug.agentId}</code>
                </>
              ) : null}
              .
            </li>
            <li>
              <strong>Host (your Mac)</strong> ran the selected Strands agent and
              called <strong>Bedrock</strong> (billable) using your Mac AWS
              credentials (<code>~/.aws</code> / <code>AWS_*</code>).
            </li>
            <li>
              <strong>Bedrock (AWS cloud)</strong>{" "}
              {requested
                ? "requested tool calls — it does not call PubMed/ChEMBL itself."
                : "did not request tools this turn (answer may be model-only)."}
            </li>
            <li>
              <strong>Host tools (your Mac)</strong>{" "}
              {executed
                ? "ran local adapters (HTTP to PubMed/ChEMBL/…) and sent IDs/summaries back to Bedrock."
                : "did not execute on your Mac this turn."}
            </li>
            <li>
              <strong>UI</strong> painted <code>tool_use</code> /{" "}
              <code>tool_result</code> / answer tokens from the SSE response.
            </li>
          </ol>

          <div className="turn-debug-badges">
            <span className={requested ? "badge ok" : "badge no"}>
              Bedrock requested tools: {requested ? "yes" : "no"}
            </span>
            <span className={executed ? "badge ok" : "badge no"}>
              Host (your Mac) executed tools: {executed ? "yes" : "no"}
            </span>
          </div>

          <div className="turn-debug-grid">
            <div>
              <h4>Tools Bedrock asked for</h4>
              {toolUses.length === 0 && bedrockRequests.length === 0 ? (
                <p className="muted small">None.</p>
              ) : (
                <ul>
                  {toolUses.map((t, i) => (
                    <li key={`u-${i}`}>
                      <strong>{t.tool}</strong>
                    </li>
                  ))}
                  {bedrockRequests.map((r, i) => (
                    <li key={`br-${i}`}>
                      <strong>{String(r.tool || "tool")}</strong>
                      {r.input ? (
                        <pre className="mini-pre">
                          {JSON.stringify(r.input, null, 2)}
                        </pre>
                      ) : null}
                    </li>
                  ))}
                </ul>
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
