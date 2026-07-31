import { useEffect, useId, useRef } from "react";
import type { StackMode } from "../config";

type Props = {
  open: boolean;
  mode: StackMode;
  onClose: () => void;
};

export function ArchitectureModal({ open, mode, onClose }: Props) {
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

  if (!open) return null;

  const isLocal = mode === "local";

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
          <h2 id={titleId}>What happens after you enter the prompt below</h2>
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
            {isLocal
              ? "You are on the local stack (no Cognito / Stream Lambda / AgentCore Runtime)."
              : "You are on the AWS demo path (Cognito → SigV4 → Stream Function URL → AgentCore)."}
          </p>

          <ol className="arch-steps">
            <li>
              <strong>Browser</strong> — Your question is POSTed as JSON to the
              Stream endpoint
              {isLocal ? " at http://127.0.0.1:8787/" : " (Stream Function URL)"}.
            </li>
            <li>
              <strong>Stream</strong> —{" "}
              {isLocal
                ? "Host FastAPI (local/stream_app.py) mints or reuses a Chat Session id, and loads the agent selected in the UI (agentId: unified or a local specialist)."
                : "AWS Lambda Stream authenticates the request (SigV4) and opens the session (unified agent only)."}
            </li>
            <li>
              <strong>Research agent (Bedrock)</strong> — Your Mac calls{" "}
              <strong>Bedrock (Claude)</strong> (billable). Bedrock may reply
              with a <em>tool instruction</em> (“please run pubmed with this
              query”) instead of a finished answer. That is{" "}
              <strong>not</strong> Bedrock calling PubMed — it is a message back
              to your Mac.
            </li>
            <li>
              <strong>Tools are not guaranteed every turn</strong> — The model
              chooses whether to ask for a lookup. Trust the transcript:{" "}
              <code>tool_result (ok)</code> means your Mac ran the tool; if
              there is none, the answer may be model-only knowledge.
            </li>
            <li>
              <strong>AWS credentials (Bedrock only)</strong> —{" "}
              {isLocal ? (
                <>
                  Host Stream uses the standard AWS credential chain:{" "}
                  <code>AWS_*</code> env / <code>AWS_PROFILE</code>, else{" "}
                  <code>~/.aws/credentials</code> + <code>~/.aws/config</code>,
                  or SSO. Used for Bedrock — not for PubMed/ChEMBL public HTTP.
                  No Cognito Identity Pool in local mode.
                </>
              ) : (
                <>
                  Browser → Cognito Identity Pool → SigV4 for Stream. Bedrock
                  runs under AWS roles, not your laptop <code>~/.aws</code>.
                </>
              )}
            </li>
            <li>
              <strong>Where tools actually run</strong> —{" "}
              {isLocal ? (
                <>
                  On your <strong>local host process</strong> (in-process
                  adapters in the Stream/agent). They HTTP-call NCBI, ChEMBL,
                  Open Targets, CT.gov. Gateway MCP is forced off. Not executed
                  “inside Bedrock.”
                </>
              ) : (
                <>
                  In the AWS agent/runtime path (often AgentCore Gateway MCP
                  Lambdas), still separate from the Bedrock model call itself.
                </>
              )}
            </li>
            <li>
              <strong>SSE events</strong> — The Stream returns{" "}
              <code>session_started</code>, <code>tool_use</code>,{" "}
              <code>tool_result</code>, <code>token</code>, then{" "}
              <code>done</code>. The UI paints each line in the transcript.
            </li>
          </ol>

          <pre className="arch-flow" aria-label="Architecture flow">
            {isLocal
              ? `You (Vite :5173)
  → POST local Stream :8787
  → Strands agent on host
      → Bedrock: plan / answer (billable; may emit tool_use)
      → if tool_use: host adapters → PubMed/ChEMBL/OT/CT.gov
      → tool_result back into agent → Bedrock may continue
  → SSE → transcript`
              : `You (CloudFront or Vite)
  → Cognito + Identity Pool → SigV4
  → Stream Function URL
  → AgentCore + Bedrock (plan/answer)
  → tools (Gateway/adapters) if model requests them
  → SSE → transcript`}
          </pre>

          <section className="host-definition" aria-label="Why many agents">
            <h3 className="arch-subhead">Why so many agents? Do they have separate brains?</h3>
            <p>
              <strong>No.</strong> Every local agent uses the{" "}
              <strong>same Bedrock model</strong> and the{" "}
              <strong>same tools</strong> (PubMed / ClinicalTrials / ChEMBL /
              Open Targets). The “brain” is always Bedrock. What changes per
              agent is mainly the <strong>system prompt</strong> (domain lens:
              drug profile vs pathways vs cardioprotection, etc.) — not a
              different model or a private tool engine.
            </p>
            <p>
              <strong>What the job is (not “just calling tools”):</strong> each
              turn Bedrock (1) plans, (2) may emit tool instructions for your
              Mac to look things up, then (3) synthesizes the research answer.
              Tools only fetch; writing and reasoning are Bedrock.
            </p>
            <p>
              <strong>Where tool calling stops:</strong> there is no hard
              per-agent tool budget today. The loop stops when Bedrock returns a
              normal answer <em>without</em> another tool instruction. Broad
              questions can mean many Bedrock calls (and more cost).
            </p>
            <p>
              <strong>Why keep specialist folders then?</strong> Local
              experiments and UI demos of Target ID angles (different default
              framing). Production / AWS path stays{" "}
              <strong>one Unified Research Agent</strong> — not five cloud
              brains.
            </p>
            {isLocal ? (
              <p className="muted small">
                The Research agent dropdown only swaps that prompt lens +
                example questions. If two agents feel identical, their prompts
                are too similar — not because each has a separate intelligence.
              </p>
            ) : (
              <p className="muted small">
                AWS mode ignores the specialist picker and always uses Unified.
              </p>
            )}
          </section>

          <p className="muted small">
            “Streaming…” = waiting for the turn. Live IDs only when{" "}
            <code>tool_result</code> is <code>ok</code>. Bedrock cost applies
            whenever the model runs, even if no tools are called.
          </p>
        </div>
      </div>
    </div>
  );
}
