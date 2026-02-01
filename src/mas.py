from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from typing import Any, Dict, Optional

from .app import _build_minimal_view, _build_payload, _load_llm, _print_tables
from .graph import build_graph
from .config import RuntimeConfig, DEFAULT_CONFIG
from .state import new_state


class RiskMAS:
    def __init__(
        self,
        *,
        llm=None,
        output: str = "table",
        pretty: bool = False,
        use_env_llm: bool = True,
        config: RuntimeConfig | None = None,
    ) -> None:
        self._config = config or DEFAULT_CONFIG
        if llm is None and use_env_llm:
            llm = _load_llm(self._config)
        self._llm = llm
        self._graph = build_graph(llm=llm, config=self._config)
        self._output = output
        self._pretty = pretty

    def run_raw(self, intent: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        state = new_state(intent, context or {})
        return self._graph.invoke(state)

    def run(
        self,
        intent: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        *,
        output: Optional[str] = None,
        pretty: Optional[bool] = None,
    ) -> str | Dict[str, Any]:
        result = self.run_raw(intent, context)
        minimal_view = _build_minimal_view(result)
        payload = _build_payload(result, minimal_view)

        out = (output or self._output).lower()
        if out == "table":
            return self._render_table(result, minimal_view)
        if out == "json":
            return self._render_json(payload, pretty if pretty is not None else self._pretty)
        raise ValueError("output must be 'table' or 'json'")

    def _render_table(self, result: Dict[str, Any], minimal_view: Dict[str, Any]) -> str:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            _print_tables(result, minimal_view)
        return buffer.getvalue().strip()

    def _render_json(self, payload: Dict[str, Any], pretty: bool) -> str:
        if pretty:
            return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
