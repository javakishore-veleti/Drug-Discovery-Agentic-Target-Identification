import { getLocalAgent, LOCAL_AGENTS } from "./localAgents";

type Props = {
  value: string;
  disabled?: boolean;
  onChange: (agentId: string) => void;
};

export function AgentPicker({ value, disabled, onChange }: Props) {
  const selected = getLocalAgent(value) ?? LOCAL_AGENTS[0];

  return (
    <div className="prompt-picker agent-picker">
      <label>
        <span>Research agent (local specialists)</span>
        <select
          disabled={disabled}
          value={value}
          aria-label="Choose which local research agent handles the prompt"
          onChange={(e) => onChange(e.target.value)}
        >
          {LOCAL_AGENTS.map((agent) => (
            <option key={agent.id} value={agent.id}>
              {agent.label}
            </option>
          ))}
        </select>
      </label>

      <div className="agent-brief" aria-live="polite">
        <p>
          <strong>Unique focus:</strong> {selected.objective}
        </p>
        <p>
          <strong>Tries to generate:</strong> {selected.output}
        </p>
        <p>
          <strong>How this helps Target ID:</strong> {selected.targetIdHelp}
        </p>
        <p className="muted small">
          Same V1 tools (PubMed / ClinicalTrials / ChEMBL / Open Targets); the
          system prompt changes the lens. Switching agents starts a new Chat
          Session. AWS mode ignores this picker (unified only).
        </p>
      </div>
    </div>
  );
}
