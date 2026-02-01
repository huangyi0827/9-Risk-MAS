from __future__ import annotations

import hashlib
import json
import csv
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

import numpy as np
from openai import OpenAI
from langchain.agents import create_agent

from .agent_utils import extract_tool_calls, last_ai_content, wrap_tool
from ..state import RiskState, Finding
from ..tools.csv_data import etf_industry_map, etf_codes_by_industry
from ..tools.rules import get_blocklist
from ..config import RuntimeConfig, DEFAULT_CONFIG
from ..skills_runtime import load_skill, build_system_prompt, filter_tools, validate_output


def _provenance(source: str, params: Dict[str, Any]) -> Dict[str, Any]:
    payload = json.dumps(params, sort_keys=True, separators=(",", ":"))
    return {
        "source": source,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "params_hash": hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16],
    }


def _blocklist_payload(profile: str, runtime: RuntimeConfig) -> Dict[str, Any]:
    # TODO: 改为基于合规语料的 RAG 方式生成禁投清单。
    blocklist, ruleset_version = get_blocklist(profile, runtime)
    return {
        "items": list(blocklist),
        "source": ruleset_version,
        "note": "rag_placeholder",
    }


# ============ Embedding 客户端 ============

_embedding_client: OpenAI | None = None
_embedding_client_key: Tuple[str, str] | None = None


def _get_embedding_client(runtime: RuntimeConfig) -> OpenAI:
    """获取或创建 embedding 客户端（复用 DashScope 配置）"""
    global _embedding_client, _embedding_client_key
    key = (runtime.openai_api_key or "", runtime.openai_base_url or "")
    if _embedding_client is None or _embedding_client_key != key:
        _embedding_client = OpenAI(
            api_key=runtime.openai_api_key or None,
            base_url=runtime.openai_base_url or None,
        )
        _embedding_client_key = key
    return _embedding_client


def _get_embeddings(texts: List[str], runtime: RuntimeConfig, model: str = "text-embedding-v4") -> np.ndarray:
    """批量获取文本的 embedding 向量"""
    if not texts:
        return np.array([])
    client = _get_embedding_client(runtime)
    response = client.embeddings.create(input=texts, model=model)
    embeddings = [item.embedding for item in response.data]
    return np.array(embeddings)


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """计算余弦相似度"""
    a_norm = a / (np.linalg.norm(a, axis=-1, keepdims=True) + 1e-9)
    b_norm = b / (np.linalg.norm(b, axis=-1, keepdims=True) + 1e-9)
    if a_norm.ndim == 1:
        a_norm = a_norm.reshape(1, -1)
    return np.dot(a_norm, b_norm.T).flatten()


# ============ 文档缓存 ============

_docs_cache: Dict[str, List[Dict[str, Any]]] = {}
_embeddings_cache: Dict[Tuple[str, str, str], np.ndarray] = {}
_industry_embeddings_cache: Tuple[List[str], np.ndarray, Tuple[str, str]] | None = None


def _get_cached_docs(path: Path) -> List[Dict[str, Any]]:
    """获取缓存的文档，避免重复加载"""
    key = str(path)
    if key not in _docs_cache:
        _docs_cache[key] = _load_rag_docs(path)
    return _docs_cache[key]


def _get_cached_embeddings(path: Path, docs: List[Dict[str, Any]], runtime: RuntimeConfig) -> np.ndarray:
    """获取缓存的文档 embeddings"""
    key = (str(path), runtime.openai_api_key or "", runtime.openai_base_url or "")
    if key not in _embeddings_cache:
        texts = [doc.get("text", "") for doc in docs]
        _embeddings_cache[key] = _get_embeddings(texts, runtime)
    return _embeddings_cache[key]


def _get_industry_embeddings(industries: List[str], runtime: RuntimeConfig) -> Tuple[List[str], np.ndarray]:
    """获取缓存的行业名 embeddings"""
    global _industry_embeddings_cache
    key = (runtime.openai_api_key or "", runtime.openai_base_url or "")
    if (
        _industry_embeddings_cache is None
        or _industry_embeddings_cache[0] != industries
        or _industry_embeddings_cache[2] != key
    ):
        embeddings = _get_embeddings(industries, runtime)
        _industry_embeddings_cache = (industries, embeddings, key)
    return _industry_embeddings_cache[0], _industry_embeddings_cache[1]


# ============ 路径解析 ============

def _resolve_rag_source(source: str, runtime: RuntimeConfig) -> Path | None:
    if not source:
        return None
    path = Path(source)
    if path.exists():
        return path
    base = runtime.csv_data_dir.strip()
    data_dir = Path(base).expanduser() if base else Path(__file__).resolve().parents[2] / "cufel_practice_data"
    candidates = [
        data_dir / source,
        data_dir / f"{source}.csv",
        data_dir / f"{source}.json",
        data_dir / f"{source}.jsonl",
        data_dir / f"{source}.txt",
        data_dir / f"{source}.md",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _make_doc(item: Dict[str, Any], source: str) -> Dict[str, Any] | None:
    """从原始记录构建文档，返回 None 表示跳过。"""
    title = str(item.get("title") or item.get("name") or "")
    content = str(item.get("content") or item.get("text") or item.get("body") or "")
    text = f"{title}\n{content}".strip()
    if not text:
        return None
    return {
        "text": text,
        "meta": {
            "source": source,
            "title": title,
            "industry_name": item.get("industry_name") or item.get("industry") or "",
        },
    }


def _load_rag_docs(path: Path) -> List[Dict[str, Any]]:
    suffix = path.suffix.lower()
    source = str(path)

    if suffix in {".txt", ".md"}:
        text = path.read_text(encoding="utf-8", errors="ignore").strip()
        return [{"text": text, "meta": {"source": source}}] if text else []

    if suffix == ".csv":
        with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
            items: List[Dict[str, Any]] = list(csv.DictReader(f))
    elif suffix == ".jsonl":
        items = []
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.strip():
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    elif suffix == ".json":
        raw = json.loads(path.read_text(encoding="utf-8", errors="ignore") or "[]")
        items = raw if isinstance(raw, list) else raw.get("items", [])
    else:
        return []

    return [doc for item in items if isinstance(item, dict) and (doc := _make_doc(item, source))]


def _keyword_retrieve(docs: List[Dict[str, Any]], query: str, limit: int) -> List[Dict[str, Any]]:
    """关键词检索（fallback）"""
    if not query or not docs:
        return []
    tokens = [t for t in query.lower().split() if t] or [query.lower()]
    scored = []
    for doc in docs:
        text = str(doc.get("text") or "")
        hay = text.lower()
        score = sum(hay.count(tok) for tok in tokens)
        if score > 0:
            scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "score": score,
            "snippet": (doc.get("text") or "")[:200],
            "meta": doc.get("meta"),
        }
        for score, doc in scored[:limit]
    ]


def _vector_retrieve(
    path: Path,
    docs: List[Dict[str, Any]],
    query: str,
    limit: int,
    runtime: RuntimeConfig,
    min_score: float = 0.3,
) -> List[Dict[str, Any]]:
    """向量检索（使用 text-embedding-v4）"""
    if not query or not docs:
        return []
    try:
        doc_embeddings = _get_cached_embeddings(path, docs, runtime)
        query_embedding = _get_embeddings([query], runtime)[0]
        scores = _cosine_similarity(query_embedding, doc_embeddings)

        # 按相似度排序，过滤低分结果
        indices = np.argsort(scores)[::-1][:limit]
        hits = []
        for idx in indices:
            score = float(scores[idx])
            if score < min_score:
                continue
            doc = docs[idx]
            hits.append({
                "score": round(score, 4),
                "snippet": (doc.get("text") or "")[:200],
                "meta": doc.get("meta"),
            })
        return hits
    except Exception:
        # embedding 失败时降级到关键词检索
        return _keyword_retrieve(docs, query, limit)


def _infer_industry_hits(
    hits: List[Dict[str, Any]],
    runtime: RuntimeConfig,
    min_similarity: float = 0.5,
) -> List[str]:
    """从检索结果中推断相关行业，使用 embedding 相似度匹配。

    Args:
        hits: 检索命中结果
        min_similarity: 最小相似度阈值（默认 0.5）
    """
    mapping = etf_industry_map(runtime)
    industries = sorted({v for v in mapping.values() if str(v).strip()})
    if not industries or not hits:
        return []

    # 1. 优先使用文档元数据中的显式行业标签
    explicit: set[str] = set()
    for hit in hits:
        meta = hit.get("meta") or {}
        raw = meta.get("industry_name") or meta.get("industry") or ""
        name = str(raw).strip()
        if name:
            explicit.add(name)
    if explicit:
        return sorted(explicit)

    # 2. 使用 embedding 相似度匹配行业名（优化：批量获取 embeddings）
    try:
        industry_names, industry_embeddings = _get_industry_embeddings(industries, runtime)
        
        # 收集所有需要计算 embedding 的文本
        texts_to_embed: List[str] = []
        text_indices: List[int] = []  # 记录有效文本对应的 hit 索引
        
        for i, hit in enumerate(hits):
            meta = hit.get("meta") or {}
            text = f"{hit.get('snippet', '')} {meta.get('title', '')}".strip()
            if text:
                texts_to_embed.append(text)
                text_indices.append(i)
        
        if not texts_to_embed:
            return []
        
        # 批量获取所有文本的 embeddings（一次 API 调用）
        text_embeddings = _get_embeddings(texts_to_embed)
        
        matched: set[str] = set()
        for text_embedding in text_embeddings:
            similarities = _cosine_similarity(text_embedding, industry_embeddings)
            # 找出超过阈值的行业
            for idx, sim in enumerate(similarities):
                if sim >= min_similarity:
                    matched.add(industry_names[idx])

        return sorted(matched)
    except Exception:
        # embedding 失败时降级到精确匹配
        matched = set()
        for hit in hits:
            meta = hit.get("meta") or {}
            text = f"{hit.get('snippet', '')} {meta.get('title', '')}"
            for industry in industries:
                if industry and industry in text:
                    matched.add(industry)
        return sorted(matched)


def rag_search(
    query: str,
    limit: int = 5,
    source: str | None = None,
    runtime: RuntimeConfig | None = None,
) -> Dict[str, Any]:
    """RAG 检索函数，支持向量检索和关键词检索。

    用法：
    - 设置 COMPLIANCE_RAG_SOURCE 为库名或文件路径；
    - 若为库名，将在 CSV_DATA_DIR 下尝试匹配同名文件。
    - 设置 RAG_ENGINE=vector 启用向量检索（默认），=keyword 使用关键词检索。
    - 向量检索使用阿里云 text-embedding-v4 模型。
    """
    runtime = runtime or DEFAULT_CONFIG
    source = (source or runtime.compliance_rag_source or "").strip()
    if not source:
        return {"hits": [], "source": "placeholder", "note": "rag_source_not_configured"}
    path = _resolve_rag_source(source, runtime)
    if path is None:
        return {"hits": [], "source": source, "note": "rag_source_not_found"}

    docs = _get_cached_docs(path)
    engine = (runtime.rag_engine or "vector").lower()

    if engine == "vector":
        hits = _vector_retrieve(path, docs, query, limit, runtime)
    else:
        hits = _keyword_retrieve(docs, query, limit)
    industry_hits = _infer_industry_hits(hits, runtime)
    industry_map = etf_codes_by_industry(industry_hits, runtime)
    etf_blocklist = sorted({code for codes in industry_map.values() for code in codes})

    # 构建用于 LLM 上下文的文档引用
    context_docs = []
    for i, hit in enumerate(hits, 1):
        meta = hit.get("meta") or {}
        title = meta.get("title") or f"文档{i}"
        industry = meta.get("industry_name") or ""
        text = hit.get("snippet") or ""
        doc_ref = f"[{i}] {title}"
        if industry:
            doc_ref += f" (行业: {industry})"
        doc_ref += f"\n{text}"
        context_docs.append(doc_ref)

    return {
        "hits": hits,
        "source": str(path),
        "industry_hits": industry_hits,
        "etf_blocklist": etf_blocklist,
        "context_for_llm": "\n\n".join(context_docs),
    }


def _tool_arg_value(args: Tuple[Any, ...], kwargs: Dict[str, Any], key: str) -> Any:
    if key in kwargs and kwargs[key] not in (None, ""):
        return kwargs[key]
    if "args" in kwargs and kwargs.get("args"):
        return (kwargs.get("args") or [None])[0]
    if args:
        first = args[0]
        if isinstance(first, dict):
            if key in first and first.get(key) not in (None, ""):
                return first.get(key)
            if first.get("args"):
                return (first.get("args") or [None])[0]
        return first
    return None


def _policy_search_impl(runtime: RuntimeConfig, *args, **kwargs) -> Dict[str, Any]:
    """Search compliance docs for a query string.

    返回检索结果，包含：
    - hits: 命中文档列表
    - context_for_llm: 格式化的文档内容，用于 LLM 理解和引用
    - etf_blocklist: 根据行业推断的 ETF 禁投列表
    """
    query = _tool_arg_value(args, kwargs, "query")
    query = str(query or "").strip()
    if not query:
        return {"query": "", "hits": [], "context_for_llm": "", "industry_hits": [], "industry_blocklist": {}, "etf_blocklist": []}
    payload = rag_search(query, limit=5, runtime=runtime)
    hits = payload.get("hits") or []
    # 简化 hits 返回给 LLM（移除 full_text 以节省 token）
    simplified_hits = [
        {"score": h.get("score"), "snippet": h.get("snippet"), "meta": h.get("meta")}
        for h in hits
    ]
    return {
        "query": query,
        "hits": simplified_hits,
        "context_for_llm": payload.get("context_for_llm") or "",
        "industry_hits": payload.get("industry_hits") or [],
        "etf_blocklist": payload.get("etf_blocklist") or [],
        "provenance": _provenance(
            "compliance_docs",
            {
                "query": query,
                "hits": len(hits),
                "industry_hits": len(payload.get("industry_hits") or []),
                "etf_blocklist": len(payload.get("etf_blocklist") or []),
            },
        ),
    }


def _allowlist_check_impl(runtime: RuntimeConfig, *args, **kwargs) -> Dict[str, Any]:
    """Check if a code is allowed by policy."""
    code = _tool_arg_value(args, kwargs, "code")
    profile = kwargs.get("profile") or (args[1] if len(args) > 1 else "default")
    code = str(code or "").strip()
    payload = _blocklist_payload(profile, runtime)
    blocked = payload.get("items") or []
    allowed = code not in blocked if code else False
    return {
        "code": code,
        "allowed": allowed,
        "blocklist_source": payload.get("source"),
        "provenance": _provenance("risk_rules", {"code": code, "allowed": allowed, "profile": profile}),
    }


def _policy_search_tool(runtime: RuntimeConfig):
    def _impl(*args, **kwargs):
        return _policy_search_impl(runtime, *args, **kwargs)
    return wrap_tool("policy_search", _impl)


def _allowlist_check_tool(runtime: RuntimeConfig):
    def _impl(*args, **kwargs):
        return _allowlist_check_impl(runtime, *args, **kwargs)
    return wrap_tool("allowlist_check", _impl)


def _llm_model_name(llm) -> str:
    return str(getattr(llm, "model_name", None) or getattr(llm, "model", None) or "")

def _build_policy_query(normalized: Dict[str, Any]) -> str:
    jurisdiction = str(normalized.get("jurisdiction") or "CN").strip()
    account_type = str(normalized.get("account_type") or "brokerage").strip()
    return f"ETF blocklist for {jurisdiction} {account_type} account"


def _extract_rag_blocklist(
    tool_calls: List[Dict[str, Any]],
) -> Tuple[List[str], List[str], str]:
    """从工具调用结果中提取 blocklist 和文档上下文。

    Returns:
        (etf_codes, industry_hits, context_for_llm)
    """
    codes: set[str] = set()
    industries: set[str] = set()
    contexts: List[str] = []

    for call in tool_calls:
        if call.get("tool") != "policy_search":
            continue
        output = call.get("output") or {}
        for code in output.get("etf_blocklist") or []:
            code_str = str(code).strip()
            if code_str:
                codes.add(code_str)
        for industry in output.get("industry_hits") or []:
            ind = str(industry).strip()
            if ind:
                industries.add(ind)
        # 提取文档上下文
        ctx = output.get("context_for_llm") or ""
        if ctx:
            contexts.append(ctx)

    return sorted(codes), sorted(industries), "\n\n---\n\n".join(contexts)


def _fallback_finding(
    state: RiskState,
    hard_blocklist: List[str],
    soft_blocklist: List[str],
    industry_hits: List[str],
) -> Finding:
    normalized = state.get("normalized") or {}
    targets = normalized.get("target_weights") or {}
    blocked = [c for c in targets if c in hard_blocklist]
    evidence = [
        {"ref": "tool:compliance_blocklist", "value": blocked},
    ]
    if soft_blocklist:
        evidence.append({"ref": "tool:compliance_blocklist_soft", "value": soft_blocklist})
    if industry_hits:
        evidence.append({"ref": "tool:compliance_industry_hits", "value": industry_hits})

    if blocked:
        severity = 3
        summary = f"目标中包含禁投ETF: {', '.join(blocked)}"
        policy_ids = ["blocklist"]
    elif soft_blocklist:
        severity = 1
        summary = "合规提示：命中文本行业映射到部分ETF，建议复核"
        policy_ids = ["soft_blocklist"]
    else:
        severity = 0
        summary = "未发现合规问题"
        policy_ids = []

    return {
        "agent": "ComplianceToolCallingAgent",
        "risk_type": "compliance",
        "severity": severity,
        "summary": summary,
        "policy_ids": policy_ids,
        "evidence": evidence,
        "recommendations": ["请复核合规规则"],
    }


def run_compliance_agent(state: RiskState, llm, config: RuntimeConfig | None = None) -> Dict[str, Any]:
    """运行合规 Agent：基于检索上下文输出结构化结论。"""
    runtime = config or DEFAULT_CONFIG
    normalized = state.get("normalized") or {}
    profile = normalized.get("policy_profile", "default")
    blocklist_payload = _blocklist_payload(profile, runtime)
    hard_blocklist = blocklist_payload.get("items") or []
    soft_blocklist: List[str] = []
    industry_hits: List[str] = []
    targets = normalized.get("target_weights") or {}
    blocked_targets = [c for c in targets if c in hard_blocklist]

    if blocked_targets:
        return {
            "finding_compliance": _fallback_finding(state, hard_blocklist, soft_blocklist, industry_hits),
            "compliance_blocklist": hard_blocklist,
            "compliance_blocklist_soft": soft_blocklist,
            "compliance_blocklist_meta": blocklist_payload,
            "tool_calls_compliance": [],
            "llm_used_compliance": False,
            "llm_model_compliance": "",
        }

    if llm is None:
        return {
            "finding_compliance": _fallback_finding(state, hard_blocklist, soft_blocklist, industry_hits),
            "compliance_blocklist": hard_blocklist,
            "compliance_blocklist_soft": soft_blocklist,
            "compliance_blocklist_meta": blocklist_payload,
            "tool_calls_compliance": [],
            "llm_used_compliance": False,
            "llm_model_compliance": "",
        }

    skill = load_skill("compliance-evidence")
    query = _build_policy_query(normalized)
    policy_search = _policy_search_tool(runtime)
    allowlist_check = _allowlist_check_tool(runtime)
    tools = filter_tools([policy_search, allowlist_check], skill.allowlist)
    if not tools:
        return {
            "finding_compliance": _fallback_finding(state, hard_blocklist, soft_blocklist, industry_hits),
            "compliance_blocklist": hard_blocklist,
            "compliance_blocklist_soft": soft_blocklist,
            "compliance_blocklist_meta": blocklist_payload,
            "tool_calls_compliance": [],
            "llm_used_compliance": False,
            "llm_model_compliance": "",
        }

    system_prompt = build_system_prompt("", skill)
    agent = create_agent(llm, tools, system_prompt=system_prompt)

    payload = {
        "normalized": normalized,
        "snapshot_metrics": state.get("snapshot_metrics") or {},
        "policy_profile": profile,
        "policy_query": query,
    }
    user_payload = json.dumps(payload, separators=(",", ":"))
    result = agent.invoke({"messages": [{"role": "user", "content": f"Input state: {user_payload}"}]})
    llm_model = _llm_model_name(llm)

    messages = result.get("messages", []) if isinstance(result, dict) else []
    tool_calls = extract_tool_calls(messages)
    if not any(call.get("tool") == "policy_search" for call in tool_calls):
        tool_calls.append({"tool": "policy_search_required", "error": "missing_policy_search"})
        return {
            "finding_compliance": _fallback_finding(state, hard_blocklist, soft_blocklist, industry_hits),
            "compliance_blocklist": hard_blocklist,
            "compliance_blocklist_soft": soft_blocklist,
            "compliance_blocklist_meta": blocklist_payload,
            "tool_calls_compliance": tool_calls,
            "llm_used_compliance": True,
            "llm_model_compliance": llm_model,
        }

    extra_blocklist, industry_hits, rag_context = _extract_rag_blocklist(tool_calls)
    if not rag_context:
        tool_calls.append({"tool": "policy_search_required", "error": "missing_rag_context"})
        return {
            "finding_compliance": _fallback_finding(state, hard_blocklist, soft_blocklist, industry_hits),
            "compliance_blocklist": hard_blocklist,
            "compliance_blocklist_soft": soft_blocklist,
            "compliance_blocklist_meta": blocklist_payload,
            "tool_calls_compliance": tool_calls,
            "llm_used_compliance": True,
            "llm_model_compliance": llm_model,
        }

    output = last_ai_content(messages)
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError:
        parsed = {}

    errors = validate_output(skill, parsed)
    if errors:
        tool_calls.append({"tool": "schema_validation", "errors": errors, "skill": skill.name})
        return {
            "finding_compliance": _fallback_finding(state, hard_blocklist, soft_blocklist, industry_hits),
            "compliance_blocklist": hard_blocklist,
            "compliance_blocklist_soft": soft_blocklist,
            "compliance_blocklist_meta": blocklist_payload,
            "tool_calls_compliance": tool_calls,
            "llm_used_compliance": True,
            "llm_model_compliance": llm_model,
        }

    finding: Finding = {
        "agent": "ComplianceToolCallingAgent",
        "risk_type": "compliance",
        "severity": int(parsed.get("severity", 0)),
        "summary": parsed.get("summary", ""),
        "evidence": parsed.get("evidence", []),
        "recommendations": parsed.get("recommendations", []),
        "policy_ids": parsed.get("policy_ids", []),
    }
    if extra_blocklist and int(finding.get("severity", 0)) >= 1:
        soft_blocklist = extra_blocklist
        blocklist_payload = {
            **blocklist_payload,
            "soft_items": soft_blocklist,
            "industry_hits": industry_hits,
            "industry_source": "indx_csname",
        }
    if soft_blocklist:
        finding["severity"] = max(int(finding.get("severity", 0)), 1)
        extra_evidence = [
            {"ref": "tool:compliance_blocklist_soft", "value": soft_blocklist},
            {"ref": "tool:compliance_industry_hits", "value": industry_hits},
        ]
        finding["evidence"] = list(finding.get("evidence") or []) + extra_evidence
        if "soft_blocklist" not in (finding.get("policy_ids") or []):
            finding["policy_ids"] = list(finding.get("policy_ids") or []) + ["soft_blocklist"]

    return {
        "finding_compliance": finding,
        "compliance_blocklist": hard_blocklist,
        "compliance_blocklist_soft": soft_blocklist,
        "compliance_blocklist_meta": blocklist_payload,
        "tool_calls_compliance": tool_calls,
        "llm_used_compliance": True,
        "llm_model_compliance": llm_model,
    }
