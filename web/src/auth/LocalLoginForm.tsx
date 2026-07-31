import { useState, type FormEvent } from "react";

const STORAGE_KEY = "ati_local_demo_user";

export function readLocalDemoUser(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

export function clearLocalDemoUser(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    /* ignore */
  }
}

type Props = {
  onSignedIn: (email: string) => void;
};

/** Cost-free local gate — any email; no Cognito. Not for production. */
export function LocalLoginForm({ onSignedIn }: Props) {
  const [email, setEmail] = useState("local.dev@example.com");
  const [error, setError] = useState<string | null>(null);

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = email.trim();
    if (!trimmed || !trimmed.includes("@")) {
      setError("Enter a demo email (local only — not Cognito).");
      return;
    }
    try {
      localStorage.setItem(STORAGE_KEY, trimmed);
    } catch {
      /* ignore */
    }
    onSignedIn(trimmed);
  }

  return (
    <form className="card login" onSubmit={onSubmit}>
      <h1>Agentic Target ID</h1>
      <p className="muted">
        <strong>Local stack</strong> — no Cognito / no AWS auth stacks. Bedrock
        still needs AWS creds on the local Stream process.
      </p>
      <label>
        Demo email
        <input
          type="email"
          autoComplete="username"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </label>
      {error ? <p className="error" role="alert">{error}</p> : null}
      <button type="submit">Continue locally</button>
      <p className="hint">
        Set <code>VITE_STACK_MODE=aws</code> + Cognito Outputs for the real path.
      </p>
    </form>
  );
}
