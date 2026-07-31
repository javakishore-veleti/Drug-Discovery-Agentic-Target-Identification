import { promptsForAgent } from "./researchPrompts";
import { getLocalAgent } from "./localAgents";

type Props = {
  agentId: string;
  disabled?: boolean;
  onPick: (prompt: string) => void;
};

export function PromptPicker({ agentId, disabled, onPick }: Props) {
  const prompts = promptsForAgent(agentId);
  const agentLabel = getLocalAgent(agentId)?.label ?? agentId;

  return (
    <label className="prompt-picker">
      <span>Example research questions for {agentLabel}</span>
      <select
        key={agentId}
        disabled={disabled}
        defaultValue=""
        aria-label={`Choose an example research question for ${agentLabel}`}
        onChange={(e) => {
          const value = e.target.value;
          if (!value) return;
          onPick(value);
          e.target.value = "";
        }}
      >
        <option value="" disabled>
          Choose one of {prompts.length} prompts for this agent…
        </option>
        {prompts.map((prompt) => (
          <option key={prompt} value={prompt}>
            {prompt}
          </option>
        ))}
      </select>
      <span className="muted small">
        Prompts change with the Research agent dropdown so examples match that
        agent’s Target ID lens.
      </span>
    </label>
  );
}
