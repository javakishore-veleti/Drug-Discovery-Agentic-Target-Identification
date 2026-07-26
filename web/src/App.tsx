import { useEffect, useState } from "react";
import { getCurrentUser } from "aws-amplify/auth";
import { configureAmplify } from "./auth/configureAmplify";
import { LoginForm } from "./auth/LoginForm";
import { ChatPage } from "./chat/ChatPage";
import { resolveAppConfig, type AppConfig } from "./config";

type AuthState =
  | { status: "loading" }
  | { status: "config_error"; message: string }
  | { status: "signed_out"; config: AppConfig }
  | { status: "signed_in"; config: AppConfig; email: string };

export default function App() {
  const [auth, setAuth] = useState<AuthState>({ status: "loading" });

  useEffect(() => {
    void resolveAppConfig()
      .then((config) => {
        configureAmplify(config);
        return getCurrentUser()
          .then((user) => {
            setAuth({
              status: "signed_in",
              config,
              email: user.signInDetails?.loginId || user.username,
            });
          })
          .catch(() => setAuth({ status: "signed_out", config }));
      })
      .catch((err: unknown) => {
        setAuth({
          status: "config_error",
          message: err instanceof Error ? err.message : String(err),
        });
      });
  }, []);

  if (auth.status === "loading") {
    return <main className="center muted">Loading…</main>;
  }
  if (auth.status === "config_error") {
    return (
      <main className="center">
        <p className="error">{auth.message}</p>
      </main>
    );
  }
  if (auth.status === "signed_out") {
    return (
      <main className="center">
        <LoginForm
          onSignedIn={() => {
            void getCurrentUser().then((user) =>
              setAuth({
                status: "signed_in",
                config: auth.config,
                email: user.signInDetails?.loginId || user.username,
              }),
            );
          }}
        />
      </main>
    );
  }

  return (
    <main>
      <ChatPage
        config={auth.config}
        email={auth.email}
        onSignedOut={() => setAuth({ status: "signed_out", config: auth.config })}
      />
    </main>
  );
}
