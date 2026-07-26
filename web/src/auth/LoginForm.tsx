import { useState, type FormEvent } from "react";
import { signIn } from "aws-amplify/auth";

type Props = {
  onSignedIn: () => void;
};

export function LoginForm({ onSignedIn }: Props) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const result = await signIn({ username: email.trim(), password });
      if (result.isSignedIn) {
        onSignedIn();
        return;
      }
      setError(
        `Sign-in incomplete (${result.nextStep?.signInStep ?? "unknown step"}). Use an admin-provisioned user.`,
      );
    } catch (err) {
      const name = err instanceof Error ? err.name : "";
      const msg = err instanceof Error ? err.message : String(err);
      if (name === "NotAuthorizedException" || name === "UserNotFoundException") {
        setError("Invalid email or password.");
      } else {
        setError(msg || "Sign-in failed.");
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="card login" onSubmit={onSubmit}>
      <h1>Agentic Target ID</h1>
      <p className="muted">Sign in with your admin-provisioned Cognito account.</p>
      <label>
        Email
        <input
          type="email"
          autoComplete="username"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </label>
      <label>
        Password
        <input
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </label>
      {error ? <p className="error" role="alert">{error}</p> : null}
      <button type="submit" disabled={busy}>
        {busy ? "Signing in…" : "Sign in"}
      </button>
      <p className="hint">
        No self-registration. See <code>docs/web.md</code> /{" "}
        <code>docs/auth.md</code> for admin create-user.
      </p>
    </form>
  );
}
