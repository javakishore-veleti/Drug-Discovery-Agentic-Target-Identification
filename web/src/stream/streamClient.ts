import { STALL_TIMEOUT_MS, type StackMode } from "../config";
import type { StreamEvent } from "./types";

function parseSse(body: string): StreamEvent[] {
  const events: StreamEvent[] = [];
  for (const block of body.split("\n\n")) {
    const trimmed = block.trim();
    if (!trimmed) continue;
    for (const line of trimmed.split("\n")) {
      if (!line.startsWith("data:")) continue;
      const raw = line.slice(5).trim();
      if (!raw) continue;
      try {
        events.push(JSON.parse(raw) as StreamEvent);
      } catch {
        // ignore malformed chunks
      }
    }
  }
  return events;
}

export type StreamTurnHandlers = {
  onEvent: (event: StreamEvent) => void;
};

async function postStream(
  mode: StackMode,
  url: string,
  region: string,
  payload: unknown,
  signal?: AbortSignal,
): Promise<Response> {
  if (mode === "local") {
    // Local stack: plain HTTP — do not import SigV4/AWS SDK (Node `process` in browser).
    return fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal,
    });
  }
  // Lazy-load only for aws mode so local UI never evaluates @aws-sdk/* at module init.
  const { sigv4Post } = await import("./sigv4Fetch");
  return sigv4Post(url, region, payload, signal);
}

/**
 * One buffered SSE turn.
 * - aws: Cognito Identity Pool → SigV4 → Stream Function URL
 * - local: plain POST → local/stream_app (no AWS auth stacks)
 */
export async function runStreamTurn(options: {
  mode: StackMode;
  streamUrl: string;
  region: string;
  message: string;
  sessionId?: string | null;
  /** Local specialists only — ignored by AWS Stream. */
  agentId?: string | null;
  handlers: StreamTurnHandlers;
}): Promise<{ sessionId: string | null }> {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), STALL_TIMEOUT_MS);

  const payload: Record<string, string> = { message: options.message };
  if (options.sessionId) {
    payload.sessionId = options.sessionId;
  }
  if (options.mode === "local" && options.agentId) {
    payload.agentId = options.agentId;
  }

  try {
    const resp = await postStream(
      options.mode,
      options.streamUrl,
      options.region,
      payload,
      controller.signal,
    );
    if (!resp.ok) {
      const text = await resp.text().catch(() => "");
      throw new Error(`Stream HTTP ${resp.status}${text ? `: ${text.slice(0, 200)}` : ""}`);
    }
    const body = await resp.text();
    const events = parseSse(body);
    let sessionId = options.sessionId ?? null;
    for (const ev of events) {
      if (ev.type === "session_started" && typeof ev.sessionId === "string") {
        sessionId = ev.sessionId;
      }
      options.handlers.onEvent(ev);
    }
    return { sessionId };
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      options.handlers.onEvent({
        type: "error",
        message: "Stream stalled — no terminal event within 5 minutes.",
        code: "stall_timeout",
      });
      options.handlers.onEvent({ type: "done" });
      return { sessionId: options.sessionId ?? null };
    }
    throw err;
  } finally {
    window.clearTimeout(timer);
  }
}
