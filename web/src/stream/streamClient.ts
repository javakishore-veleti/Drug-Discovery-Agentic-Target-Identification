import { STALL_TIMEOUT_MS } from "../config";
import { sigv4Post } from "./sigv4Fetch";
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

/**
 * One buffered SSE turn (Stream Lambda completes Runtime then returns events).
 * Soft stall: AbortController fires terminal error within 5 minutes (NFR-9).
 */
export async function runStreamTurn(options: {
  streamUrl: string;
  region: string;
  message: string;
  sessionId?: string | null;
  handlers: StreamTurnHandlers;
}): Promise<{ sessionId: string | null }> {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), STALL_TIMEOUT_MS);

  const payload: Record<string, string> = { message: options.message };
  if (options.sessionId) {
    payload.sessionId = options.sessionId;
  }

  try {
    const resp = await sigv4Post(
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
