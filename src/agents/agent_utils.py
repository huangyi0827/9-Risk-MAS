from __future__ import annotations

import json
from typing import Any, Dict, List, Sequence

from langchain_core.messages import AIMessage, ToolMessage


def _parse_tool_output(content: Any) -> Any:
    if isinstance(content, str):
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return content
    return content


def extract_tool_calls(messages: Sequence[Any]) -> List[Dict[str, Any]]:
    pending: Dict[str, Dict[str, Any]] = {}
    tool_calls: List[Dict[str, Any]] = []

    for msg in messages:
        if isinstance(msg, AIMessage):
            for call in msg.tool_calls or []:
                call_id = call.get("id") or f"{call.get('name', 'tool')}-{len(pending)}"
                pending[call_id] = {
                    "tool": call.get("name", "unknown"),
                    "input": call.get("args", {}),
                }
        elif isinstance(msg, ToolMessage):
            info = pending.get(msg.tool_call_id, {})
            output = _parse_tool_output(msg.content)
            meta = output.get("tool_meta") if isinstance(output, dict) else None
            tool_calls.append(
                {
                    "tool": info.get("tool", "unknown"),
                    "input": info.get("input", {}),
                    "output": output,
                    "latency_ms": (meta or {}).get("latency_ms"),
                    "error": (meta or {}).get("error"),
                }
            )
    return tool_calls


def last_ai_content(messages: Sequence[Any]) -> str:
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            content = msg.content
            if isinstance(content, list):
                return json.dumps(content, separators=(",", ":"))
            return str(content)
    return ""
