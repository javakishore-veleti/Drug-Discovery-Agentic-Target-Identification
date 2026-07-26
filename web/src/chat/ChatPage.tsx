import { useCallback, useRef, useState, type FormEvent } from "react";
import { signOut } from "aws-amplify/auth";
import type { AppConfig } from "../config";
import { runStreamTurn } from "../stream/streamClient";
import type { StreamEvent, TranscriptItem } from "../stream/types";
import { Disclaimer } from "./Disclaimer";
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
  const sessionIdRef = useRef<string | null>(null);

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
        streamUrl: config.streamUrl,
        region: config.region,
        message,
        sessionId: sessionIdRef.current,
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

  async function onSignOut() {
    await signOut();
    sessionIdRef.current = null;
    onSignedOut();
  }

  return (
    <div className="chat-shell">
      <header className="chat-header">
        <div>
          <strong>Agentic Target ID</strong>
          <span className="muted"> · {email}</span>
        </div>
        <button type="button" className="ghost" onClick={() => void onSignOut()}>
          Sign out
        </button>
      </header>

      <Disclaimer />

      <Transcript items={items} />

      {status ? (
        <p className="error" role="alert">
          {status}
        </p>
      ) : null}

      <form className="composer" onSubmit={onSubmit}>
        <textarea
          rows={3}
          placeholder="Ask a research question…"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          disabled={busy}
        />
        <div className="composer-actions">
          <button
            type="button"
            className="ghost"
            disabled={busy}
            onClick={() =>
              void sendMessage("What is the mechanism of action of Herceptin?")
            }
          >
            Demo: mechanism
          </button>
          <button
            type="button"
            className="ghost"
            disabled={busy}
            onClick={() =>
              void sendMessage(
                "Which patient populations are most vulnerable to its cardiotoxicity?",
              )
            }
          >
            Demo: cardiotoxicity
          </button>
          <button type="submit" disabled={busy || !draft.trim()}>
            {busy ? "Streaming…" : "Send"}
          </button>
        </div>
      </form>
    </div>
  );
}
