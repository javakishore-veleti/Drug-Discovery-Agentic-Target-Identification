import { useEffect, useState } from "react";

type Props = {
  streamUrl: string;
  /** Changes after each Send completes — remounts/refetches latest turn only. */
  refreshToken: string;
};

/** HTML viewer of Bedrock calls for the latest completed Send (no history). */
export function BedrockTraceViewer({ streamUrl, refreshToken }: Props) {
  const base = streamUrl.replace(/\/?$/, "/");
  const traceUrl = `${base}bedrock-trace`;
  const [callCount, setCallCount] = useState<number | null>(null);
  const [modelId, setModelId] = useState<string>("");

  useEffect(() => {
    let cancelled = false;
    void fetch(`${base}bedrock-trace.json?t=${encodeURIComponent(refreshToken)}`, {
      cache: "no-store",
    })
      .then((r) => (r.ok ? r.json() : null))
      .then((data: { bedrockCallCount?: number; modelId?: string } | null) => {
        if (cancelled || !data) return;
        setCallCount(
          typeof data.bedrockCallCount === "number" ? data.bedrockCallCount : 0,
        );
        setModelId(typeof data.modelId === "string" ? data.modelId : "");
      })
      .catch(() => {
        /* stream may be down */
      });
    return () => {
      cancelled = true;
    };
  }, [base, refreshToken]);

  return (
    <section className="bedrock-trace-viewer" aria-label="Bedrock call trace">
      <header className="bedrock-trace-header">
        <h3>Bedrock calls for this Send</h3>
        <p className="muted small">
          Shown once after this Send finishes (no continuous refresh). Latest
          turn only. Model: <code>{modelId || "…"}</code>
          {callCount !== null ? (
            <>
              {" "}
              · Bedrock calls: <strong>{callCount}</strong>
            </>
          ) : null}
          {" · "}
          <a href={traceUrl} target="_blank" rel="noreferrer">
            open full HTML
          </a>
        </p>
      </header>
      <iframe
        key={refreshToken}
        title="Bedrock call trace"
        className="bedrock-trace-frame"
        src={`${traceUrl}?t=${encodeURIComponent(refreshToken)}`}
      />
    </section>
  );
}
