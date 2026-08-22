from __future__ import annotations

import json
import os
import hashlib
import re
import requests
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Dict, List, TypedDict

from langgraph.graph import StateGraph, START, END

try:
    from langgraph.checkpoint.memory import InMemorySaver
    CHECKPOINTER = InMemorySaver
except ImportError:
    from langgraph.checkpoint.memory import MemorySaver
    CHECKPOINTER = MemorySaver

from intelligence_tools import (
    select_tools,
    search_arxiv,
    search_openalex,
    search_crossref,
    search_semantic_scholar,
    search_google_news,
    search_gdelt,
)

MEMORY_FILE = "memory_store.json"


class ResearchState(TypedDict, total=False):
    topic: str
    objective: str
    competitors: str
    plan: List[Dict[str, Any]]
    subtasks: List[Dict[str, Any]]
    selected_tools: List[str]
    findings: List[Dict[str, Any]]
    verified_findings: List[Dict[str, Any]]
    tool_results: Dict[str, Any]
    tool_status: Dict[str, str]
    tool_failures: List[str]
    conflicts: List[Dict[str, Any]]
    uncertainty_reasons: List[str]
    previous_context: List[Dict[str, Any]]
    confidence: float
    evaluation: Dict[str, Any]
    strategy: Dict[str, Any]
    final_answer: Dict[str, Any]
    execution_trace: List[Dict[str, Any]]
    iteration: int
    max_iterations: int
    tool_budget: int
    tool_calls_used: int
    needs_replanning: bool
    deadlock_detected: bool
    visited_states: List[str]
    checkpoint_count: int


def initial_state(topic: str, objective: str, competitors: str = "", max_iterations: int = 3, tool_budget: int = 6) -> ResearchState:
    return {
        "topic": topic.strip(),
        "objective": objective.strip(),
        "competitors": competitors.strip(),
        "plan": [],
        "subtasks": [],
        "selected_tools": [],
        "findings": [],
        "verified_findings": [],
        "tool_results": {},
        "tool_status": {},
        "tool_failures": [],
        "conflicts": [],
        "uncertainty_reasons": [],
        "previous_context": load_memory(topic),
        "confidence": 0.0,
        "evaluation": {},
        "strategy": {},
        "final_answer": {},
        "execution_trace": [],
        "iteration": 0,
        "max_iterations": max_iterations,
        "tool_budget": tool_budget,
        "tool_calls_used": 0,
        "needs_replanning": False,
        "deadlock_detected": False,
        "visited_states": [],
        "checkpoint_count": 0,
    }


def trace(state: ResearchState, agent: str, action: str, status: str = "info", details: str = "") -> None:
    state.setdefault("execution_trace", []).append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "agent": agent,
        "action": action,
        "status": status,
        "details": details,
    })


def load_memory(topic: str) -> List[Dict[str, Any]]:
    try:
        if not os.path.exists(MEMORY_FILE):
            return []
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = data.get("scans", data.get("memory", []))
        if not isinstance(data, list):
            return []
        key = topic.lower().strip()
        return [x for x in data if isinstance(x, dict) and key and key in str(x.get("topic", "")).lower()][-5:]
    except Exception:
        return []


def planner(state: ResearchState) -> ResearchState:
    state["iteration"] = state.get("iteration", 0) + 1
    topic = state["topic"]
    objective = state["objective"]
    competitors = state.get("competitors", "")

    subtasks = [
        {"id": "scholarly", "goal": f"Find scholarly evidence directly relevant to {topic} and the objective: {objective}", "priority": "high"},
        {"id": "signals", "goal": "Find recent external and industry signals relevant to the objective.", "priority": "high"},
    ]
    if competitors:
        subtasks.append({"id": "competitive", "goal": f"Check developments involving {competitors}.", "priority": "medium"})
    if state.get("needs_replanning"):
        subtasks.append({"id": "verification", "goal": "Verify weak or conflicting evidence before deciding.", "priority": "critical"})

    state["subtasks"] = subtasks
    state["plan"] = [{"step": i + 1, **task} for i, task in enumerate(subtasks)]
    trace(state, "Mission Planner", "Decomposed objective into adaptive subtasks", "success", f"Iteration {state['iteration']}: {len(subtasks)} subtasks")
    return state


def router(state: ResearchState) -> ResearchState:
    selected = select_tools(state["topic"], state["objective"], state.get("competitors", ""))
    state["selected_tools"] = selected
    trace(state, "Dynamic Router", "Selected tools from user context", "success", ", ".join(selected))
    return state


def resource_manager(state: ResearchState) -> ResearchState:
    remaining = max(0, state["tool_budget"] - state.get("tool_calls_used", 0))
    selected = state.get("selected_tools", [])[:remaining]
    state["selected_tools"] = selected
    status = "success" if selected else "warning"
    trace(state, "Resource Manager", "Allocated research budget", status, f"{len(selected)} tool calls available")
    return state


def call_tool(name: str, topic: str, objective: str, competitors: str) -> List[Dict[str, Any]]:
    if name == "arXiv API":
        return search_arxiv(topic, objective, max_results=5)
    if name == "OpenAlex API":
        return search_openalex(topic, objective, max_results=5)
    if name == "Crossref API":
        return search_crossref(topic, objective, max_results=5)
    if name == "Semantic Scholar API":
        return search_semantic_scholar(topic, objective, max_results=5)
    if name == "Google News RSS":
        return search_google_news(topic, objective, competitors, max_results=6)
    if name == "GDELT API":
        return search_gdelt(topic, objective, max_results=6)
    raise ValueError(f"Unknown tool: {name}")


def parallel_research(state: ResearchState) -> ResearchState:
    tools = state.get("selected_tools", [])
    results: Dict[str, Any] = {}
    statuses: Dict[str, str] = {}
    failures: List[str] = []

    if not tools:
        failures.append("No tools available within resource budget")
        state["tool_failures"] = failures
        trace(state, "Research Agent", "No tool available", "error", failures[0])
        return state

    with ThreadPoolExecutor(max_workers=min(6, len(tools))) as pool:
        futures = {
            pool.submit(call_tool, name, state["topic"], state["objective"], state.get("competitors", "")): name
            for name in tools
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                results[name] = future.result() or []
                statuses[name] = "Success" if results[name] else "No results"
            except Exception as exc:
                results[name] = []
                statuses[name] = "Failed"
                failures.append(f"{name}: {exc}")

    findings = []
    for items in results.values():
        if isinstance(items, list):
            findings.extend(items)

    # Deduplicate by title/URL without changing the existing tool schema.
    unique = {}
    for item in findings:
        if not isinstance(item, dict):
            continue
        key = str(item.get("url") or item.get("title") or "").strip().lower()
        if key:
            unique[key] = item

    state["tool_results"] = results
    state["tool_status"] = statuses
    state["tool_failures"] = failures
    state["findings"] = list(unique.values())
    state["tool_calls_used"] = state.get("tool_calls_used", 0) + len(tools)
    trace(state, "Research Agent", "Executed selected tools in parallel", "success" if not failures else "warning", f"{len(tools)} tools; {len(state['findings'])} raw findings")
    return state


def evidence_judge(state: ResearchState) -> ResearchState:
    findings = state.get("findings", [])
    verified = []
    for item in findings:
        score = item.get("relevance_score", 0)
        try:
            score = float(score)
        except (TypeError, ValueError):
            score = 0
        if score >= 10:
            verified.append(item)

    state["verified_findings"] = verified
    confidence = min(1.0, len(verified) / 10.0)
    if state.get("tool_failures"):
        confidence *= 0.75
    state["confidence"] = round(confidence, 2)
    trace(state, "Evidence Judge", "Scored evidence quality", "success", f"{len(verified)} relevant; confidence {state['confidence']:.2f}")
    return state


def conflict_resolver(state: ResearchState) -> ResearchState:
    findings = state.get("verified_findings", [])
    positive = []
    limiting = []
    pos = ("improved", "increase", "effective", "promising", "advantage", "benefit", "successful")
    neg = ("risk", "challenge", "limitation", "limited", "barrier", "uncertain", "failure", "difficult")

    for item in findings:
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        if any(x in text for x in pos):
            positive.append(item)
        if any(x in text for x in neg):
            limiting.append(item)

    conflicts = []
    if positive and limiting:
        conflicts.append({
            "type": "mixed_evidence",
            "supporting_signals": len(positive),
            "limiting_signals": len(limiting),
            "resolution": "Do not force a binary conclusion; report both signals and lower confidence.",
        })
        state["confidence"] = round(state.get("confidence", 0) * 0.75, 2)
        state.setdefault("uncertainty_reasons", []).append("Evidence contains both supporting and limiting signals.")
        trace(state, "Evidence Judge", "Resolved conflicting evidence", "warning", "Mixed evidence retained; confidence reduced")
    else:
        trace(state, "Evidence Judge", "Checked for conflicting evidence", "success", "No major mixed-signal conflict detected")
    state["conflicts"] = conflicts
    return state


def evaluate(state: ResearchState) -> ResearchState:
    issues = []
    count = len(state.get("verified_findings", []))
    confidence = state.get("confidence", 0)
    if count < 3:
        issues.append("insufficient_evidence")
    if confidence < 0.40:
        issues.append("low_confidence")
    if state.get("tool_failures"):
        issues.append("tool_failure")
    if state.get("conflicts"):
        issues.append("conflicting_evidence")

    can_replan = bool(issues) and state.get("iteration", 1) < state.get("max_iterations", 3)
    state["needs_replanning"] = can_replan
    state["evaluation"] = {"passed": not can_replan, "issues": issues, "confidence": confidence, "evidence_count": count}
    trace(state, "Self-Evaluator", "Evaluated mission quality", "warning" if can_replan else "success", ", ".join(issues) if issues else "Mission meets quality threshold")
    return state


def deadlock_guard(state: ResearchState) -> ResearchState:
    raw = f"{state.get('iteration')}|{len(state.get('findings', []))}|{state.get('confidence', 0):.2f}|{state.get('needs_replanning')}"
    signature = hashlib.sha1(raw.encode()).hexdigest()
    visited = state.setdefault("visited_states", [])
    if signature in visited:
        state["deadlock_detected"] = True
        state["needs_replanning"] = False
        trace(state, "Safety Guard", "Detected repeated state", "error", "Deadlock prevented")
    else:
        visited.append(signature)
    return state


def _clean_sentence(text: str, limit: int = 360) -> str:
    """Turn API abstracts into compact, readable evidence sentences."""
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    if not text:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", text)
    selected = []
    length = 0
    for part in parts:
        if not part:
            continue
        if length + len(part) > limit and selected:
            break
        selected.append(part)
        length += len(part) + 1
        if len(selected) >= 2:
            break
    result = " ".join(selected).strip()
    return result[:limit].rstrip() + ("…" if len(result) > limit else "")


def _themes(findings: List[Dict[str, Any]], topic: str) -> List[str]:
    """Extract recurring technical concepts from titles/summaries."""
    stop = {
        "the", "and", "for", "with", "from", "using", "based", "study",
        "research", "analysis", "system", "systems", "model", "models",
        "approach", "method", "methods", "results", "paper", "toward",
        "towards", "new", "novel", "design", "development", "application",
        "applications", "data", "learning", "technology", "technologies",
        "intelligence", "research", "show", "shows", "can", "may", "using",
    }
    counter = Counter()
    for item in findings:
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        words = re.findall(r"[a-z][a-z0-9-]{3,}", text)
        for word in words:
            if word not in stop and not word.isdigit():
                counter[word] += 1
    topic_words = {w.lower() for w in re.findall(r"[a-z][a-z0-9-]{3,}", topic)}
    ranked = [w for w, _ in counter.most_common(20) if w not in topic_words]
    return ranked[:4]


def _synthesis_from_evidence(state: ResearchState) -> Dict[str, Any]:
    """Create the user-facing intelligence brief from verified evidence.

    This deliberately stays evidence-grounded: it synthesizes retrieved
    material rather than inventing facts that are not present in the sources.
    """
    topic = state.get("topic", "the topic")
    objective = state.get("objective", "")
    findings = state.get("verified_findings", [])
    conflicts = state.get("conflicts", [])
    confidence = float(state.get("confidence", 0) or 0)

    if not findings:
        return {
            "summary": (
                f"I could not build a reliable intelligence brief for {topic} "
                "because the research run did not produce enough verified evidence. "
                "The system should broaden the search or try again before drawing a conclusion."
            ),
            "key_findings": [],
            "trends": "No defensible trend can be established from the available evidence.",
            "risks": ["Evidence coverage is currently insufficient for a confident decision."],
            "opportunities": [],
            "verdict": "INSUFFICIENT EVIDENCE",
        }

    themes = _themes(findings, topic)
    theme_text = ", ".join(themes[:3]) if themes else topic

    positive_terms = ("improved", "increase", "effective", "promising", "advantage", "benefit", "successful", "opportunity")
    limiting_terms = ("risk", "challenge", "limitation", "limited", "barrier", "uncertain", "failure", "difficult", "cost")

    positive_count = 0
    limiting_count = 0
    for item in findings:
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        positive_count += sum(1 for term in positive_terms if term in text)
        limiting_count += sum(1 for term in limiting_terms if term in text)

    key_findings = []
    for item in findings[:4]:
        title = str(item.get("title", "Untitled evidence")).strip()
        summary = _clean_sentence(item.get("summary", ""))
        source = str(item.get("source") or item.get("tool") or "source")
        key_findings.append({
            "title": title,
            "summary": summary or "Relevant evidence was identified in this source.",
            "source": source,
            "url": item.get("url", ""),
        })

    if positive_count > limiting_count:
        trend = (
            f"The strongest recurring signals point toward active development around {theme_text}. "
            "Several sources contain positive or opportunity-oriented evidence, although this should be read as a research signal rather than proof of commercial success."
        )
    elif limiting_count > positive_count:
        trend = (
            f"The evidence around {theme_text} is active but carries meaningful constraints. "
            "Challenges and limitations appear often enough that execution risk should remain part of the decision."
        )
    else:
        trend = (
            f"The evidence shows active work around {theme_text}, but the signals are mixed. "
            "The current literature supports continued investigation more than a one-sided conclusion."
        )

    risks = []
    if limiting_count:
        risks.append("Multiple sources mention constraints, risks, limitations, barriers, or uncertainty.")
    if conflicts:
        risks.append("The evidence contains mixed signals, so the agent has deliberately reduced confidence.")
    if confidence < 0.75:
        risks.append("Evidence confidence is below the high-confidence threshold; further validation is advisable.")
    if not risks:
        risks.append("No major risk pattern was detected in the verified evidence set.")

    opportunities = []
    if positive_count:
        opportunities.append("The evidence contains recurring positive or opportunity-oriented signals worth investigating further.")
    if themes:
        opportunities.append(f"The recurring themes around {', '.join(themes[:3])} provide useful directions for deeper research or product strategy.")

    if confidence >= 0.75:
        verdict = "HIGH SIGNAL"
    elif confidence >= 0.40:
        verdict = "WATCH CLOSELY"
    else:
        verdict = "EMERGING"

    summary = (
        f"For the objective of {objective or 'understanding the current landscape'}, "
        f"the agent reviewed {len(findings)} verified evidence items on {topic}. "
        f"Across those sources, the clearest recurring themes are {theme_text}. "
        f"Overall, the evidence indicates meaningful activity in this area, but the strength of the conclusion depends on how consistently the sources support the same direction. "
        f"The current assessment is {verdict.lower()} with {confidence:.0%} confidence."
    )

    if conflicts:
        summary += " Because the evidence contains both supporting and limiting signals, the agent is keeping that uncertainty visible instead of forcing a binary answer."

    return {
        "summary": summary,
        "key_findings": key_findings,
        "trends": trend,
        "risks": risks,
        "opportunities": opportunities,
        "verdict": verdict,
    }



def _gemini_api_key() -> str:
    """Read the Gemini key from common environment variable names."""
    return (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
        or os.getenv("GOOGLE_GEMINI_API_KEY")
        or ""
    ).strip()


def _extract_json_object(text: str) -> Dict[str, Any]:
    """Extract a JSON object even when Gemini wraps it in markdown fences."""
    text = str(text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if match:
            return json.loads(match.group(0))
        raise ValueError("Gemini did not return a JSON object")


def _gemini_synthesis(state: ResearchState) -> Dict[str, Any]:
    """Use Gemini to turn verified evidence into the actual intelligence brief."""
    api_key = _gemini_api_key()
    if not api_key:
        return {"status": "unavailable", "error": "GEMINI_API_KEY/GOOGLE_API_KEY is not set."}

    findings = state.get("verified_findings", [])[:12]
    topic = state.get("topic", "")
    objective = state.get("objective", "")
    competitors = state.get("competitors", "")
    previous = state.get("previous_context", [])[-3:]

    evidence = []
    for i, item in enumerate(findings, 1):
        evidence.append({
            "id": i,
            "title": str(item.get("title", ""))[:300],
            "summary": str(item.get("summary", ""))[:900],
            "source": str(item.get("source") or item.get("tool") or "Unknown"),
            "date": str(item.get("date", "Unknown")),
            "url": str(item.get("url", "")),
        })

    prompt = f"""
You are the Strategy Agent inside ResearchRadar, a university hackathon research-intelligence system.
Your job is NOT to merely summarize papers. Turn the VERIFIED evidence below into a concise decision-ready intelligence brief.

TOPIC: {topic}
OBJECTIVE: {objective}
COMPETITORS: {competitors or 'None specified'}
PREVIOUS MEMORY: {json.dumps(previous, ensure_ascii=False)}

VERIFIED EVIDENCE:
{json.dumps(evidence, ensure_ascii=False)}

Rules:
1. Use only claims supported by the supplied evidence.
2. Never invent competitor facts, numbers, dates, products, or market claims.
3. Clearly distinguish evidence from inference.
4. If evidence is insufficient for a claim, say so.
5. The output must be useful to a founder/researcher deciding what to investigate next.
6. Mention recurring themes across multiple sources rather than treating one paper as a trend.
7. Keep the answer readable and specific, not generic filler.

Return ONLY valid JSON with exactly these keys:
summary: string (120-220 words, decision-ready)
key_findings: array of 3-5 objects, each with title, insight, source
trends: string (80-150 words)
opportunities: array of 2-4 strings
risks: array of 2-4 strings
competitor_context: string (80-150 words; if competitors are not supported by evidence, explicitly say that)
recommendation: string (80-150 words)
verdict: one of HIGH SIGNAL, WATCH CLOSELY, EMERGING, INSUFFICIENT EVIDENCE
confidence: number from 0 to 1
"""

    model_candidates = [
        os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
        "gemini-3.6-flash",
        "gemini-2.5-flash",
    ]

    last_error = "Unknown Gemini error"
    for model in dict.fromkeys(model_candidates):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            response = requests.post(
                url,
                params={"key": api_key},
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.2,
                        "responseMimeType": "application/json",
                    },
                },
                timeout=45,
            )
            response.raise_for_status()
            data = response.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed = _extract_json_object(text)
            parsed["status"] = "success"
            parsed["model"] = model
            return parsed
        except Exception as exc:
            last_error = f"{model}: {exc}"

    return {"status": "error", "error": last_error}


def _memory_context(state: ResearchState) -> str:
    """Build a compact memory context for the Strategy Agent.

    Task 4 memory is optional, so this function is deliberately defensive: if
    the memory store is unavailable or empty, it returns a useful neutral
    statement instead of breaking the Task 5 graph.
    """
    memory = state.get("memory") or {}
    if isinstance(memory, str):
        return memory

    if not isinstance(memory, dict):
        return "No prior scan context is available for this topic."

    topic = str(state.get("topic", "")).strip()
    count = memory.get("scan_count", memory.get("count", 0))
    previous_signal = memory.get("last_signal", memory.get("signal", ""))
    previous_date = memory.get("last_scanned", memory.get("timestamp", ""))

    parts = []
    if count:
        parts.append(f"This topic has been scanned {count} time(s) before.")
    elif topic:
        parts.append(f"No prior scan count is available for {topic}.")

    if previous_signal:
        parts.append(f"The most recent recorded signal was {previous_signal}.")
    if previous_date:
        parts.append(f"Previous scan timestamp: {previous_date}.")

    prior_summary = memory.get("summary", memory.get("previous_summary", ""))
    if prior_summary:
        parts.append(f"Previous context: {str(prior_summary)[:800]}")

    return " ".join(parts) if parts else "No prior scan context is available for this topic."


def strategy(state: ResearchState) -> ResearchState:
    """Strategy Agent: Gemini first, deterministic evidence-grounded fallback second."""
    confidence = float(state.get("confidence", 0) or 0)
    findings = state.get("verified_findings", [])
    conflicts = state.get("conflicts", [])

    # Real LLM synthesis for Task 5.
    llm = _gemini_synthesis(state)

    if llm.get("status") == "success":
        signal = str(llm.get("verdict", "WATCH CLOSELY")).upper()
        llm_confidence = llm.get("confidence", confidence)
        try:
            confidence = max(0.0, min(1.0, float(llm_confidence)))
        except (TypeError, ValueError):
            pass

        recommendation = str(llm.get("recommendation", "Validate the strongest signals with further evidence."))
        competitor_context = str(llm.get("competitor_context", "Competitor context was not sufficiently supported by the retrieved evidence."))
        memory_context = _memory_context(state)
        state["strategy"] = {
            "signal": signal,
            "confidence": confidence,
            "llm_status": "success",
            "llm_model": llm.get("model", "Gemini"),
            "recommendation": recommendation,
            "competitor_analysis": competitor_context,
            "memory_context": memory_context,
            "evidence_count": len(findings),
            "conflicts": conflicts,
            "summary": str(llm.get("summary", "")),
            "key_findings": llm.get("key_findings", []),
            "trends": str(llm.get("trends", "")),
            "risks": llm.get("risks", []) or [],
            "opportunities": llm.get("opportunities", []) or [],
            "total": len(findings),
            "arxiv": sum(1 for x in findings if str(x.get("source", "")).lower() == "arxiv"),
            "openalex": sum(1 for x in findings if str(x.get("source", "")).lower() == "openalex"),
        }
        trace(state, "Strategy Agent", "Gemini synthesized verified evidence into a decision-ready intelligence brief", "success", f"{signal}; {confidence:.0%} confidence")
    else:
        # Keep the application usable if Gemini is temporarily unavailable.
        synthesis = _synthesis_from_evidence(state)
        signal = synthesis.get("verdict", "INSUFFICIENT EVIDENCE")
        recommendation = (
            "Continue monitoring the strongest signals, validate important claims, and collect more evidence before making a high-stakes strategic decision."
            if signal != "INSUFFICIENT EVIDENCE"
            else "Broaden the research objective or collect additional evidence before making a strategic decision."
        )
        state["strategy"] = {
            "signal": signal,
            "confidence": confidence,
            "llm_status": "error",
            "llm_error": llm.get("error", "Gemini unavailable"),
            "recommendation": recommendation,
            "competitor_analysis": "Competitor conclusions are limited because Gemini synthesis was unavailable; retrieved evidence is shown for verification.",
            "memory_context": _memory_context(state),
            "evidence_count": len(findings),
            "conflicts": conflicts,
            "summary": synthesis["summary"],
            "key_findings": synthesis["key_findings"],
            "trends": synthesis["trends"],
            "risks": synthesis["risks"],
            "opportunities": synthesis["opportunities"],
            "total": len(findings),
            "arxiv": sum(1 for x in findings if str(x.get("source", "")).lower() == "arxiv"),
            "openalex": sum(1 for x in findings if str(x.get("source", "")).lower() == "openalex"),
        }
        trace(state, "Strategy Agent", "Gemini synthesis unavailable; deterministic evidence-grounded fallback used", "warning", str(llm.get("error", "Unknown error")))

    state["confidence"] = confidence
    state["final_answer"] = {
        "topic": state["topic"],
        "objective": state["objective"],
        "summary": state["strategy"].get("summary", ""),
        "key_findings": state["strategy"].get("key_findings", []),
        "trends": state["strategy"].get("trends", ""),
        "risks": state["strategy"].get("risks", []),
        "opportunities": state["strategy"].get("opportunities", []),
        "verdict": state["strategy"].get("signal", "INSUFFICIENT EVIDENCE"),
        "recommendation": state["strategy"].get("recommendation", ""),
        "competitor_context": state["strategy"].get("competitor_analysis", ""),
        "tools": state.get("selected_tools", []),
        "evidence_count": len(findings),
        "previous_context_used": bool(state.get("previous_context")),
        "iterations": state.get("iteration", 1),
        "tool_calls_used": state.get("tool_calls_used", 0),
        "replanned": state.get("iteration", 1) > 1,
        "execution_trace": state.get("execution_trace", []),
    }
    return state

def route_after_research(state: ResearchState) -> str:
    return "replan" if state.get("tool_failures") and state.get("iteration", 1) < state.get("max_iterations", 3) else "evidence"


def route_after_evaluation(state: ResearchState) -> str:
    if state.get("deadlock_detected"):
        return "strategy"
    return "replan" if state.get("needs_replanning") else "strategy"


def build_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("planner", planner)
    graph.add_node("router", router)
    graph.add_node("resources", resource_manager)
    graph.add_node("research", parallel_research)
    graph.add_node("evidence", evidence_judge)
    graph.add_node("conflicts", conflict_resolver)
    graph.add_node("evaluate", evaluate)
    graph.add_node("deadlock", deadlock_guard)
    graph.add_node("strategy", strategy)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "router")
    graph.add_edge("router", "resources")
    graph.add_edge("resources", "research")
    graph.add_conditional_edges("research", route_after_research, {"replan": "planner", "evidence": "evidence"})
    graph.add_edge("evidence", "conflicts")
    graph.add_edge("conflicts", "evaluate")
    graph.add_edge("evaluate", "deadlock")
    graph.add_conditional_edges("deadlock", route_after_evaluation, {"replan": "planner", "strategy": "strategy"})
    graph.add_edge("strategy", END)

    return graph.compile(checkpointer=CHECKPOINTER())


research_graph = build_graph()


def run_task5_agent(topic: str, objective: str, competitors: str = "", max_iterations: int = 3, tool_budget: int = 6) -> ResearchState:
    state = initial_state(topic, objective, competitors, max_iterations, tool_budget)
    config = {"configurable": {"thread_id": hashlib.sha1(f"{topic}|{objective}|{datetime.now().isoformat()}".encode()).hexdigest()}}
    return research_graph.invoke(state, config=config)


if __name__ == "__main__":
    demo = run_task5_agent(
        "Solid-state batteries",
        "Identify recent research, breakthroughs, manufacturing challenges and commercial opportunities for EV solid-state batteries.",
        "Toyota, QuantumScape, Samsung SDI",
    )
    print(json.dumps({
        "strategy": demo.get("strategy"),
        "tools": demo.get("selected_tools"),
        "confidence": demo.get("confidence"),
        "iterations": demo.get("iteration"),
        "trace": demo.get("execution_trace"),
    }, indent=2, default=str))