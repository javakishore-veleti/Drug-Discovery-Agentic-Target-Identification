"""BedrockModel wrapper that records every model.stream() invocation."""

from __future__ import annotations

from typing import Any, AsyncGenerator

from strands.models import BedrockModel
from strands.types.content import Messages, SystemContentBlock
from strands.types.streaming import StreamEvent
from strands.types.tools import ToolChoice, ToolSpec

from local.bedrock_trace import TRACE


class TracedBedrockModel(BedrockModel):
    """Same as BedrockModel, but each stream() = one traced Bedrock call."""

    async def stream(
        self,
        messages: Messages,
        tool_specs: list[ToolSpec] | None = None,
        system_prompt: str | None = None,
        *,
        tool_choice: ToolChoice | None = None,
        system_prompt_content: list[SystemContentBlock] | None = None,
        **kwargs: Any,
    ) -> AsyncGenerator[StreamEvent, None]:
        cfg = self.get_config() or {}
        model_id = str(cfg.get("model_id") or "")
        call = TRACE.start_call(
            messages=messages,
            tool_specs=tool_specs,
            model_id=model_id,
        )
        err: str | None = None
        try:
            async for event in super().stream(
                messages,
                tool_specs,
                system_prompt,
                tool_choice=tool_choice,
                system_prompt_content=system_prompt_content,
                **kwargs,
            ):
                TRACE.note_event(call, event)
                yield event
        except Exception as exc:  # noqa: BLE001
            err = f"{exc.__class__.__name__}: {exc}"
            raise
        finally:
            TRACE.finish_call(call, error=err)


def wrap_agent_model(agent: Any, *, region_name: str) -> Any:
    """Replace agent.model with a traced Bedrock model (local Stream only)."""
    old = getattr(agent, "model", None)
    if old is None:
        return agent
    cfg = {}
    try:
        cfg = dict(old.get_config() or {})
    except Exception:  # noqa: BLE001
        pass
    model_id = str(cfg.get("model_id") or "")
    if not model_id:
        return agent
    agent.model = TracedBedrockModel(model_id=model_id, region_name=region_name)
    return agent
