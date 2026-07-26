/** AD-4 Stream Event shapes the UI understands (unknown types are ignored). */

export type SourceIds = {
  pmid?: string[];
  nct?: string[];
  chembl?: string[];
};

export type StreamEvent = {
  type: string;
  sessionId?: string;
  requestId?: string;
  text?: string;
  tool?: string;
  input?: unknown;
  status?: string;
  ids?: SourceIds;
  summary?: string;
  message?: string;
  code?: string;
};

export type TranscriptItem =
  | { kind: "user"; id: string; text: string }
  | {
      kind: "assistant_turn";
      id: string;
      sessionId?: string;
      reasoning: string[];
      tools: Array<{
        tool: string;
        phase: "use" | "result";
        status?: string;
        ids?: SourceIds;
        message?: string;
      }>;
      answer: string;
      errors: string[];
      stalled?: boolean;
      done: boolean;
    };
