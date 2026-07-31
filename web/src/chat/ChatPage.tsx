import { useCallback, useRef, useState, type FormEvent } from "react";
import type { AppConfig } from "../config";
import { runStreamTurn } from "../stream/streamClient";
import type { StreamEvent, TranscriptItem } from "../stream/types";
import { AgentPicker } from "./AgentPicker";
import { ArchitectureModal } from "./ArchitectureModal";
import { Disclaimer } from "./Disclaimer";
import { DEFAULT_LOCAL_AGENT_ID, getLocalAgent } from "./localAgents";
import { PromptPicker } from "./PromptPicker";
import { Transcript } from "./Transcript";

type Props = {
  config: AppConfig;
  email: string;
  onSignedOut: () => void;
};

function newId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export function ChatPage({ config, email, onSignedOut }: Props) {
  const [items, setItems] = useState<TranscriptItem[]>([]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [archOpen, setArchOpen] = useState(false);
  const [agentId, setAgentId] = useState(DEFAULT_LOCAL_AGENT_ID);
  const sessionIdRef = useRef<string | null>(null);

  const agentLabel = getLocalAgent(agentId)?.label ?? agentId;

  const applyEvent = useCallback((turnId: string, event: StreamEvent) => {
    setItems((prev) =>
      prev.map((item) => {
        if (item.kind !== "assistant_turn" || item.id !== turnId) return item;
        const next = { ...item };
        switch (event.type) {
          case "session_started":
            if (typeof event.sessionId === "string") {
              next.sessionId = event.sessionId;
            }
            break;
          case "reasoning":
            if (typeof event.text === "string" && event.text.trim()) {
              next.reasoning = [...next.reasoning, event.text];
            }
            break;
          case "tool_use":
            next.tools = [
              ...next.tools,
              {
                tool: String(event.tool || "unknown"),
                phase: "use",
              },
            ];
            break;
          case "tool_result":
            next.tools = [
              ...next.tools,
              {
                tool: String(event.tool || "unknown"),
                phase: "result" as const,
                status: typeof event.status === "string" ? event.status : "ok",
                ids: event.ids,
                message:
                  typeof event.message === "string" ? event.message : undefined,
              },
            ];
            break;
          case "token":
            if (typeof event.text === "string") {
              next.answer = next.answer + event.text;
            }
            break;
          case "error": {
            const msg =
              (typeof event.message === "string" && event.message) ||
              "Stream error";
            next.errors = [...next.errors, msg];
            if (event.code === "stall_timeout") {
              next.stalled = true;
            }
            break;
          }
          case "debug":
            if (event.debug && typeof event.debug === "object") {
              next.debug = event.debug;
            }
            break;
          case "done":
            next.done = true;
            break;
          default:
            // Ignore unknown Stream Event types (Story 5.2 AC).
            break;
        }
        return next;
      }),
    );
  }, []);

  async function sendMessage(text: string) {
    const message = text.trim();
    if (!message || busy) return;

    const userId = newId();
    const turnId = newId();
    setItems((prev) => [
      ...prev,
      { kind: "user", id: userId, text: message },
      {
        kind: "assistant_turn",
        id: turnId,
        reasoning: [],
        tools: [],
        answer: "",
        errors: [],
        done: false,
      },
    ]);
    setDraft("");
    setBusy(true);
    setStatus(null);

    try {
      const { sessionId } = await runStreamTurn({
        mode: config.mode,
        streamUrl: config.streamUrl,
        region: config.region,
        message,
        sessionId: sessionIdRef.current,
        agentId: config.mode === "local" ? agentId : undefined,
        handlers: {
          onEvent: (ev) => applyEvent(turnId, ev),
        },
      });
      if (sessionId) {
        sessionIdRef.current = sessionId;
      }
      setItems((prev) =>
        prev.map((item) =>
          item.kind === "assistant_turn" && item.id === turnId
            ? { ...item, done: true }
            : item,
        ),
      );
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      setStatus(msg);
      setItems((prev) =>
        prev.map((item) =>
          item.kind === "assistant_turn" && item.id === turnId
            ? {
                ...item,
                errors: [...item.errors, msg],
                done: true,
              }
            : item,
        ),
      );
    } finally {
      setBusy(false);
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    void sendMessage(draft);
  }

  function onSignOut() {
    sessionIdRef.current = null;
    onSignedOut();
  }

  return (
    <div className="chat-shell">
      <header className="chat-header">
        <div>
          <strong>Agentic Target ID</strong>
          <span className="muted">
            {" "}
            · {email}
            {config.mode === "local" ? ` · local · ${agentLabel}` : ""}
          </span>
        </div>
        <button type="button" className="ghost" onClick={onSignOut}>
          Sign out
        </button>
      </header>

      <Disclaimer />

      {config.mode === "local" ? (
        <AgentPicker
          value={agentId}
          disabled={busy}
          onChange={(next) => {
            if (next === agentId) return;
            setAgentId(next);
            sessionIdRef.current = null;
            setItems([]);
            setDraft("");
            setStatus(null);
          }}
        />
      ) : null}

      <PromptPicker
        agentId={config.mode === "local" ? agentId : DEFAULT_LOCAL_AGENT_ID}
        disabled={busy}
        onPick={(prompt) => {
          setDraft(prompt);
          setStatus(null);
        }}
      />

      <p className="arch-link-row">
        <button
          type="button"
          className="linkish"
          onClick={() => setArchOpen(true)}
        >
          What happens after you enter the prompt below
        </button>
      </p>

      <ArchitectureModal
        open={archOpen}
        mode={config.mode}
        onClose={() => setArchOpen(false)}
      />

      <Transcript items={items} />

      {status ? (
        <p className="error" role="alert">
          {status}
        </p>
      ) : null}

      <form className="composer" onSubmit={onSubmit}>
        <textarea
          rows={3}
          placeholder="Ask a research question… or choose an example above"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          disabled={busy}
        />
        <div className="composer-actions">
          <button type="submit" disabled={busy || !draft.trim()}>
            {busy ? "Streaming…" : "Send"}
          </button>
        </div>
      </form>
    </div>
  );
}
