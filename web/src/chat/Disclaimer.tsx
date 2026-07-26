import { DISCLAIMER } from "../config";

/** Approved PRD addendum §F copy — always visible on chat surface (FR6 / AD-14). */
export function Disclaimer() {
  return (
    <aside className="disclaimer" role="note" aria-label="Research disclaimer">
      {DISCLAIMER}
    </aside>
  );
}
