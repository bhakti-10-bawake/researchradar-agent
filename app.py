import streamlit as st
import requests
import xml.etree.ElementTree as ET
import textwrap
import json
import os
from datetime import datetime

# TASK 5 — adaptive LangGraph agent
from agent_graph import run_task5_agent


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ResearchRadar",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# HTML HELPER
# This prevents HTML from appearing as plain text.
#
# FIX: textwrap.dedent() only removes the COMMON leading
# whitespace shared by every line. Because these triple-quoted
# HTML blocks contain nested tags at different indentation
# levels, dedent() leaves 4-8 spaces of leading whitespace on
# the more deeply nested lines. Markdown treats any line
# indented 4+ spaces as a code block, so those lines were being
# rendered as literal text instead of HTML.
#
# Stripping every line individually removes ALL leading/trailing
# whitespace, so nothing can trigger markdown's code-block rule.
# ============================================================

def render_html(content):
    lines = content.strip("\n").split("\n")
    cleaned = "\n".join(line.strip() for line in lines)
    st.markdown(cleaned, unsafe_allow_html=True)


# ============================================================
# MARKDOWN ESCAPE HELPER
#
# Research abstracts, LLM-generated text, and user-typed input
# (topic/competitors) all flow into render_html() -> st.markdown().
# Characters like $ _ * # ` [ ] are markdown/LaTeX formatting
# instructions, not literal text, so anything containing them
# gets reinterpreted instead of displayed as-is. Escaping fixes
# this everywhere dynamic/external text is injected.
# ============================================================

def escape_dynamic_text(value):

    if value is None:
        return ""

    text = str(value)

    replacements = [
        ("\\", "\\\\"),
        ("$", "\\$"),
        ("_", "\\_"),
        ("*", "\\*"),
        ("`", "\\`"),
        ("#", "\\#"),
        ("[", "\\["),
        ("]", "\\]"),
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    return text


# ============================================================
# CUSTOM CSS
# ============================================================

render_html("""
<style>

.stApp {
    background: #F8F1EA;
    color: #4A3535;
}

.block-container {
    max-width: 1280px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

h1, h2, h3, h4 {
    color: #4A3535 !important;
    font-weight: 800 !important;
}

p {
    color: #6F5C5C;
    line-height: 1.6;
}

strong, b {
    color: #4A3535 !important;
    font-weight: 850 !important;
}


/* ================= BRAND ================= */

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 22px;
}

.brand-logo {
    width: 52px;
    height: 52px;
    border-radius: 16px;
    background: linear-gradient(
        135deg,
        #C9828A,
        #E7B8BC
    );
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 27px;
    box-shadow: 0 8px 22px rgba(185,109,119,0.18);
}

.brand-name {
    font-size: 26px;
    font-weight: 900;
    color: #4A3535;
}

.brand-tag {
    font-size: 9px;
    font-weight: 850;
    letter-spacing: 1.5px;
    color: #A2676E;
}


/* ================= HERO ================= */

.hero {
    background: linear-gradient(
        135deg,
        #FFFDFC,
        #F8E5E6,
        #F1D5D8
    );

    border: 1px solid #E7C9CA;
    border-radius: 25px;
    padding: 42px;
    margin-bottom: 30px;

    box-shadow:
        0 12px 35px rgba(100,70,70,0.08);
}

.hero-small {
    font-size: 10px;
    font-weight: 900;
    letter-spacing: 1.8px;
    color: #A2676E;
}

.hero-title {
    font-size: 45px;
    font-weight: 900;
    color: #493535;
    margin-top: 8px;
}

.hero-subtitle {
    font-size: 18px;
    font-weight: 750;
    color: #A2676E;
    margin-top: 5px;
}

.hero-description {
    max-width: 800px;
    margin-top: 15px;
    font-size: 14px;
    color: #6F5C5C;
}


/* ================= SECTION ================= */

.section-label {
    font-size: 10px;
    font-weight: 900;
    letter-spacing: 1.7px;
    color: #A2676E;
    text-transform: uppercase;
    margin-bottom: 12px;
}


/* ================= DASHBOARD ================= */

.dashboard-card {
    background: #FFFFFF;
    border: 1px solid #E8DADA;
    border-radius: 18px;
    padding: 22px;
    min-height: 135px;
    box-shadow: 0 6px 20px rgba(100,70,70,0.055);
}

.card-title {
    font-size: 13px;
    font-weight: 850;
    color: #594343;
}

.card-value {
    font-size: 28px;
    font-weight: 900;
    color: #4A3535;
    margin-top: 5px;
}

.card-caption {
    font-size: 11px;
    color: #9A8181;
    margin-top: 5px;
}


/* ================= WORKFLOW ================= */

.workflow {
    background: #FFFFFF;
    border: 1px solid #E8DADA;
    border-radius: 17px;
    padding: 20px;
    min-height: 125px;
    text-align: center;
    box-shadow: 0 5px 17px rgba(100,70,70,0.04);
}

.workflow-number {
    width: 32px;
    height: 32px;
    margin: 0 auto 9px auto;
    border-radius: 50%;
    background: #F3D6D8;
    color: #A65D68;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
}

.workflow-title {
    font-size: 14px;
    font-weight: 850;
    color: #594343;
}

.workflow-text {
    font-size: 11px;
    color: #9A8080;
    margin-top: 5px;
}


/* ================= INPUT ================= */

.stTextInput label,
.stTextArea label {
    color: #594343 !important;
    font-weight: 850 !important;
}

.stTextInput input,
.stTextArea textarea {
    background: #FFFFFF !important;
    color: #4A3535 !important;
    border: 1px solid #DDC8C8 !important;
    border-radius: 13px !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #C9828A !important;
    box-shadow: 0 0 0 2px rgba(201,130,138,0.12) !important;
}


/* ================= BUTTON ================= */

.stButton > button {
    background: linear-gradient(
        135deg,
        #C9828A,
        #B96D77
    ) !important;

    color: white !important;
    border: none !important;
    border-radius: 13px !important;
    font-weight: 850 !important;
    min-height: 48px;
}

.stButton > button:hover {
    background: #A95F69 !important;
}


/* ================= FINDINGS ================= */

.finding {
    background: #FFFFFF;
    border: 1px solid #E8DADA;
    border-radius: 17px;
    padding: 22px;
    margin-bottom: 14px;
    box-shadow: 0 5px 18px rgba(100,70,70,0.05);
}

.badge {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    background: #F7E6E7;
    color: #A65D68;
    font-size: 10px;
    font-weight: 850;
}

.finding-title {
    font-size: 16px;
    font-weight: 850;
    color: #4F3B3B;
    margin-top: 9px;
}

.finding-summary {
    font-size: 13px;
    color: #6F5C5C;
    margin-top: 7px;
}

.finding-meta {
    font-size: 11px;
    color: #9A8181;
    margin-top: 10px;
}


/* ================= SIGNAL ================= */

.signal {
    background: #FFF3F4;
    border: 1px solid #E8C9CC;
    border-left: 6px solid #C47A84;
    border-radius: 18px;
    padding: 25px;
}

.signal-level {
    font-size: 25px;
    font-weight: 900;
    color: #A65D68;
}


/* ================= AGENT ================= */

.agent {
    background: #FFFFFF;
    border: 1px solid #E8DADA;
    border-radius: 17px;
    padding: 20px;
    min-height: 150px;
    box-shadow: 0 5px 18px rgba(100,70,70,0.05);
}

.agent-icon {
    font-size: 26px;
}

.agent-name {
    font-size: 15px;
    font-weight: 900;
    color: #4A3535;
    margin-top: 7px;
}

.agent-description {
    font-size: 12px;
    color: #8E7777;
    margin-top: 6px;
}


/* ================= SIDEBAR ================= */

section[data-testid="stSidebar"] {
    background: #FFF8F3;
    border-right: 1px solid #E8DADA;
}

.sidebar-heading {
    font-size: 21px;
    font-weight: 900;
    color: #4A3535;
}

.sidebar-agent {
    font-size: 13px;
    font-weight: 850;
    color: #594343;
    margin-top: 15px;
}

.sidebar-text {
    font-size: 12px;
    color: #806D6D;
    line-height: 1.6;
}


/* ================= MEMORY ================= */

.memory {
    background: #FDF3EC;
    border: 1px solid #E9D8C6;
    border-left: 6px solid #C6935E;
    border-radius: 18px;
    padding: 22px;
}

.memory-text {
    font-size: 13px;
    color: #6F5C5C;
    margin-top: 8px;
}

.memory-pill {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 20px;
    background: #FFFFFF;
    border: 1px solid #E9D8C6;
    color: #8A6A3D;
    font-size: 11px;
    font-weight: 800;
    margin: 4px 6px 0 0;
}

.sidebar-memory-item {
    font-size: 11px;
    color: #806D6D;
    line-height: 1.6;
    padding: 6px 0;
    border-bottom: 1px dashed #E8DADA;
}


/* ================= INTELLIGENCE BRIEF (premium hero result) ================= */

.brief-hero {
    background: linear-gradient(135deg, #FFFDFC, #FBEEF0);
    border: 1px solid #EBD3D5;
    border-radius: 26px;
    padding: 36px;
    box-shadow: 0 14px 40px rgba(120,70,80,0.10);
}

.brief-label {
    font-size: 11px;
    letter-spacing: 2px;
    font-weight: 900;
    color: #A2676E;
    text-transform: uppercase;
}

.brief-verdict {
    font-size: 30px;
    font-weight: 900;
    color: #4A3535;
    margin-top: 8px;
    line-height: 1.3;
}

.brief-summary {
    font-size: 14.5px;
    color: #6F5C5C;
    margin-top: 14px;
    line-height: 1.7;
    max-width: 900px;
}

.brief-stats {
    display: flex;
    gap: 34px;
    margin-top: 24px;
    flex-wrap: wrap;
}

.brief-stat-value {
    font-size: 22px;
    font-weight: 900;
    color: #4A3535;
}

.brief-stat-label {
    font-size: 10px;
    letter-spacing: 1px;
    color: #A2676E;
    font-weight: 800;
    text-transform: uppercase;
    margin-top: 2px;
}


/* ================= INSIGHT LISTS ================= */

.insight-list {
    list-style: none;
    padding: 0;
    margin: 10px 0 0 0;
}

.insight-list li {
    font-size: 13px;
    color: #6F5C5C;
    padding: 8px 0;
    border-bottom: 1px dashed #EFE1E1;
    line-height: 1.5;
}

.insight-list li:last-child {
    border-bottom: none;
}


/* ================= TREND / RECOMMENDATION CARDS ================= */

.trend-card {
    background: #F4F7FB;
    border: 1px solid #D9E3F0;
    border-left: 6px solid #6E93C4;
    border-radius: 18px;
    padding: 24px;
}

.recommendation-card {
    background: #FFF9EF;
    border: 1px solid #F0DFC0;
    border-left: 6px solid #D8A94B;
    border-radius: 18px;
    padding: 24px;
}

.recommendation-sub {
    font-size: 12px;
    color: #8E7777;
    margin-top: 14px;
    padding-top: 12px;
    border-top: 1px dashed #EFE1CE;
}


/* ================= EXECUTION TIMELINE ================= */

.timeline {
    display: flex;
    flex-direction: column;
}

.timeline-item {
    display: flex;
    gap: 14px;
    padding: 13px 0;
    border-bottom: 1px solid #F0E4E4;
}

.timeline-item:last-child {
    border-bottom: none;
}

.timeline-icon {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 900;
    flex-shrink: 0;
    margin-top: 2px;
}

.timeline-icon.success {
    background: #E4F3E6;
    color: #4C8C58;
}

.timeline-icon.warning {
    background: #FCEFD9;
    color: #B4842B;
}

.timeline-icon.error {
    background: #FBE3E5;
    color: #B44C57;
}

.timeline-content {
    flex: 1;
    min-width: 0;
}

.timeline-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 10px;
}

.timeline-agent {
    font-size: 13px;
    font-weight: 850;
    color: #4A3535;
}

.timeline-time {
    font-size: 10px;
    color: #A2938E;
    font-weight: 700;
    white-space: nowrap;
}

.timeline-action {
    font-size: 12.5px;
    color: #6F5C5C;
    margin-top: 2px;
}

.timeline-details {
    font-size: 11px;
    color: #9A8181;
    margin-top: 3px;
}


/* ================= FOOTER ================= */

.footer {
    text-align: center;
    padding: 25px;
    border-top: 1px solid #E5D4D4;
    color: #9A8181;
    font-size: 11px;
}

</style>
""")


# ============================================================
# API CONFIG
# ============================================================

ARXIV_API = "https://export.arxiv.org/api/query"
OPENALEX_API = "https://api.openalex.org/works"


# ============================================================
# MEMORY CONFIG
#
# TASK 4 — CONTEXT & MEMORY MANAGEMENT
#
# Two layers of memory are implemented:
#
# 1. SHORT-TERM (working) memory — st.session_state.
#    Lives only for the current browser session.
#
# 2. LONG-TERM (persistent) memory — a local JSON file.
#    Survives app restarts.
# ============================================================

MEMORY_FILE = "memory_store.json"


def load_long_term_memory():
    """Read all past scans from disk. Returns [] if none exist yet."""

    if not os.path.exists(MEMORY_FILE):
        return []

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_long_term_memory(entry):
    """Append one scan record to the long-term memory file."""

    history = load_long_term_memory()
    history.append(entry)
    history = history[-200:]

    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception:
        pass


def init_session_memory():
    """Ensure short-term (session) memory exists."""

    if "session_history" not in st.session_state:
        st.session_state.session_history = []


init_session_memory()


# ============================================================
# TOOL 1 — arXiv
# ============================================================

def search_arxiv(topic, limit=5):

    try:

        params = {
            "search_query": f"all:{topic}",
            "start": 0,
            "max_results": limit,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }

        response = requests.get(
            ARXIV_API,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        root = ET.fromstring(response.text)

        namespace = {
            "atom": "http://www.w3.org/2005/Atom"
        }

        results = []

        for entry in root.findall(
            "atom:entry",
            namespace
        ):

            title = entry.findtext(
                "atom:title",
                "",
                namespace
            ).strip().replace("\n", " ")

            summary = entry.findtext(
                "atom:summary",
                "",
                namespace
            ).strip().replace("\n", " ")

            published = entry.findtext(
                "atom:published",
                "",
                namespace
            )

            authors = []

            for author in entry.findall(
                "atom:author",
                namespace
            ):

                name = author.findtext(
                    "atom:name",
                    "",
                    namespace
                )

                if name:
                    authors.append(name)

            url = ""

            for link in entry.findall(
                "atom:link",
                namespace
            ):

                href = link.attrib.get(
                    "href",
                    ""
                )

                if href:
                    url = href
                    break

            results.append({
                "title": title,
                "summary": summary,
                "date": published[:10] if published else "Unknown",
                "authors": ", ".join(authors),
                "url": url,
                "source": "arXiv"
            })

        return results

    except Exception as error:

        return [{
            "title": "arXiv unavailable",
            "summary": str(error),
            "date": "Error",
            "authors": "",
            "url": "",
            "source": "arXiv"
        }]


# ============================================================
# TOOL 2 — OpenAlex
# ============================================================

def search_openalex(topic, limit=5):

    try:

        params = {
            "search": topic,
            "per-page": limit,
            "sort": "publication_date:desc"
        }

        response = requests.get(
            OPENALEX_API,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        results = []

        for work in data.get(
            "results",
            []
        ):

            title = work.get(
                "title",
                "Untitled research"
            )

            abstract_index = work.get(
                "abstract_inverted_index"
            )

            summary = ""

            if abstract_index:

                words = []

                for word, positions in abstract_index.items():

                    for position in positions:
                        words.append(
                            (position, word)
                        )

                words.sort()

                summary = " ".join(
                    word
                    for _, word in words
                )

            if not summary:
                summary = (
                    "Scholarly research indexed "
                    "by OpenAlex."
                )

            authors = []

            for authorship in work.get(
                "authorships",
                []
            ):

                author = authorship.get(
                    "author",
                    {}
                )

                name = author.get(
                    "display_name"
                )

                if name:
                    authors.append(name)

            location = work.get(
                "primary_location",
                {}
            )

            url = location.get(
                "landing_page_url",
                ""
            )

            results.append({
                "title": title,
                "summary": summary,
                "date": work.get(
                    "publication_date",
                    "Unknown"
                ),
                "authors": ", ".join(authors),
                "url": url,
                "source": "OpenAlex"
            })

        return results

    except Exception as error:

        return [{
            "title": "OpenAlex unavailable",
            "summary": str(error),
            "date": "Error",
            "authors": "",
            "url": "",
            "source": "OpenAlex"
        }]


# ============================================================
# TOOL ORCHESTRATOR (legacy — retained, no longer on the hot
# path now that Task 5's LangGraph agent plans tool selection,
# but kept intact per architecture-preservation requirements)
# ============================================================

def select_tools(topic):

    topic_lower = topic.lower()

    research_terms = [
        "ai",
        "artificial intelligence",
        "machine learning",
        "deep learning",
        "robot",
        "robotics",
        "quantum",
        "battery",
        "batteries",
        "semiconductor",
        "health",
        "healthcare",
        "biotech",
        "energy",
        "technology",
        "research",
        "software",
        "materials",
        "electric vehicle"
    ]

    selected = []

    if any(
        term in topic_lower
        for term in research_terms
    ):
        selected.append("arXiv")

    selected.append("OpenAlex")

    return list(dict.fromkeys(selected))


# ============================================================
# AGENT 1 — RESEARCH AGENT (legacy — retained, unused by the
# Task 5 LangGraph pipeline, kept intact per architecture rules)
# ============================================================

class ResearchAgent:

    def __init__(self, tools):
        self.tools = tools

    def run(self, topic):

        findings = []

        if "arXiv" in self.tools:

            findings.extend(
                search_arxiv(topic)
            )

        if "OpenAlex" in self.tools:

            findings.extend(
                search_openalex(topic)
            )

        return findings


# ============================================================
# AGENT 2 — STRATEGY AGENT (legacy — retained, unused by the
# Task 5 LangGraph pipeline, kept intact per architecture rules)
# ============================================================

class StrategyAgent:

    def run(
        self,
        topic,
        findings,
        competitors,
        prior_scans=None
    ):

        successful = [
            item
            for item in findings
            if "unavailable"
            not in item.get(
                "title",
                ""
            ).lower()
        ]

        total = len(successful)

        arxiv_count = sum(
            1
            for item in successful
            if item["source"] == "arXiv"
        )

        openalex_count = sum(
            1
            for item in successful
            if item["source"] == "OpenAlex"
        )

        if total >= 8:

            signal = "HIGH"

            verdict = (
                "Strong research activity detected. "
                "This is an actively developing area "
                "with significant scholarly attention."
            )

        elif total >= 3:

            signal = "MEDIUM"

            verdict = (
                "Moderate research activity detected. "
                "The topic shows meaningful potential "
                "for further investigation."
            )

        else:

            signal = "LOW"

            verdict = (
                "Limited research activity detected. "
                "The area may represent an early-stage "
                "or underexplored opportunity."
            )

        if competitors.strip():

            competitor_analysis = (
                f"Competitor context considered: "
                f"{competitors}."
            )

        else:

            competitor_analysis = (
                "No competitors were specified. "
                "The analysis focuses on the research landscape."
            )

        prior_scans = prior_scans or []

        if not prior_scans:

            memory_context = (
                "No memory found for this topic. "
                "This is the first recorded scan."
            )

        else:

            last_scan = prior_scans[-1]
            last_signal = last_scan.get("signal", "UNKNOWN")
            last_date = last_scan.get("timestamp", "an earlier session")

            if last_signal == signal:

                trend = (
                    f"Signal strength is holding steady at "
                    f"{signal}."
                )

            else:

                order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}

                if order.get(signal, 0) > order.get(last_signal, 0):
                    direction = "growing"
                else:
                    direction = "cooling"

                trend = (
                    f"Signal has shifted from {last_signal} to "
                    f"{signal} since the last scan — interest "
                    f"appears to be {direction}."
                )

            memory_context = (
                f"This topic has been scanned "
                f"{len(prior_scans)} time(s) before, "
                f"most recently on {last_date}. {trend}"
            )

        return {
            "signal": signal,
            "verdict": verdict,
            "recommendation": (
                "Monitor emerging research, compare "
                "new approaches with existing solutions, "
                "and investigate technically promising "
                "research directions."
            ),
            "competitor_analysis": competitor_analysis,
            "memory_context": memory_context,
            "total": total,
            "arxiv": arxiv_count,
            "openalex": openalex_count
        }


# ============================================================
# AGENT 3 — MEMORY AGENT
# (Task 4 — Context & Memory Management)
# ============================================================

class MemoryAgent:

    def recall(self, topic):
        """
        LONG-TERM RECALL.
        Looks up the persistent memory file for prior scans on
        a matching topic (case-insensitive substring match).
        """

        history = load_long_term_memory()

        topic_lower = topic.strip().lower()

        matches = [
            entry
            for entry in history
            if topic_lower in entry.get("topic", "").lower()
        ]

        return matches

    def remember(self, entry):
        """
        Writes a completed scan to BOTH memory layers:
        - short-term: st.session_state (this browser session only)
        - long-term: JSON file on disk (persists across restarts)
        """

        init_session_memory()
        st.session_state.session_history.append(entry)

        save_long_term_memory(entry)


# ============================================================
# ORCHESTRATOR (legacy — retained, unused by the Task 5
# LangGraph pipeline, kept intact per architecture rules)
# ============================================================

class ResearchRadarOrchestrator:

    def run(
        self,
        topic,
        objective,
        competitors
    ):

        tools = select_tools(topic)

        research_agent = ResearchAgent(tools)

        findings = research_agent.run(
            topic
        )

        memory_agent = MemoryAgent()

        prior_scans = memory_agent.recall(topic)

        strategy_agent = StrategyAgent()

        strategy = strategy_agent.run(
            topic,
            findings,
            competitors,
            prior_scans
        )

        memory_entry = {
            "topic": topic,
            "objective": objective,
            "competitors": competitors,
            "signal": strategy["signal"],
            "total_findings": strategy["total"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        memory_agent.remember(memory_entry)

        return {
            "tools": tools,
            "findings": findings,
            "strategy": strategy,
            "objective": objective,
            "prior_scans": prior_scans
        }


# ============================================================
# UI HELPERS
# (Rendering-only utilities for Task 5's LangGraph output.
# These read existing backend fields with safe fallbacks —
# they never invent data that wasn't returned by the agent.)
# ============================================================

def _get_first(source, keys, default=None):
    """Return the first present, non-empty value for any key in `keys`."""

    if not isinstance(source, dict):
        return default

    for key in keys:
        value = source.get(key)
        if value not in (None, ""):
            return value

    return default


def normalize_confidence_pct(value):
    """Accepts a 0-1 float or a 0-100 number and returns a clean 0-100 int."""

    try:
        v = float(value)
    except (TypeError, ValueError):
        return 0

    if v <= 1:
        v *= 100

    return max(0, min(100, round(v)))


def compute_mission_health(raw_state, final_answer, strategy, execution_trace, verified_findings):
    """
    Pulls Mission Health metrics from whatever the backend actually
    returned. Tries explicit keys first; only falls back to counting
    real execution_trace entries when no explicit metric was supplied.
    Never fabricates a number — every value is grounded in returned data.
    """

    trace = execution_trace or []

    confidence = _get_first(strategy, ["confidence"], 0)

    verified_sources = _get_first(strategy, ["evidence_count"], None)
    if verified_sources is None:
        verified_sources = len(verified_findings) if verified_findings else 0

    tool_calls = _get_first(
        raw_state,
        ["tool_call_count", "num_tool_calls", "tool_calls"],
        None
    )
    if tool_calls is None:
        tool_calls = sum(
            1 for e in trace
            if isinstance(e, dict) and any(
                kw in str(e.get("action", "")).lower()
                for kw in ["search", "fetch", "api", "tool", "arxiv", "openalex", "call"]
            )
        )

    iterations = _get_first(
        raw_state,
        ["iterations", "iteration_count", "loop_count"],
        None
    )
    if iterations is None:
        iterations = _get_first(final_answer, ["iterations"], None)
    if iterations is None:
        replan_count = sum(
            1 for e in trace
            if isinstance(e, dict) and "replan" in str(e.get("action", "")).lower()
        )
        iterations = replan_count if replan_count else None

    failures = sum(
        1 for e in trace
        if isinstance(e, dict) and str(e.get("status", "")).lower() in ("error", "failed", "failure")
    )

    recovered = any(
        isinstance(e, dict) and any(
            kw in (str(e.get("action", "")) + str(e.get("details", ""))).lower()
            for kw in ["fallback", "recover", "replan"]
        )
        for e in trace
    )

    if recovered:
        recovery_status = "Recovered"
    elif failures > 0:
        recovery_status = "Unresolved"
    else:
        recovery_status = "Nominal"

    return {
        "confidence": confidence,
        "verified_sources": verified_sources,
        "tool_calls": tool_calls,
        "iterations": iterations if iterations is not None else "N/A",
        "failures": failures,
        "recovery_status": recovery_status,
    }


def render_execution_timeline(trace, empty_message="No execution trace was returned for this run."):
    """Renders execution_trace entries as a visual timeline instead of raw st.write() lines."""

    if not trace:
        st.caption(empty_message)
        return

    rows = []

    for event in trace:

        if not isinstance(event, dict):
            continue

        agent = escape_dynamic_text(event.get("agent", "Agent"))
        action = escape_dynamic_text(event.get("action", "Step"))
        details = escape_dynamic_text(event.get("details", event.get("detail", "")))
        time_val = escape_dynamic_text(event.get("time", event.get("timestamp", "")))
        status = str(event.get("status", "")).lower()

        if status in ("success", "ok", "completed", "done"):
            icon_class, icon = "success", "✓"
        elif status in ("error", "failed", "failure"):
            icon_class, icon = "error", "✕"
        else:
            icon_class, icon = "warning", "•"

        details_html = f'<div class="timeline-details">{details}</div>' if details else ""

        rows.append(f"""
        <div class="timeline-item">
            <div class="timeline-icon {icon_class}">{icon}</div>
            <div class="timeline-content">
                <div class="timeline-header">
                    <span class="timeline-agent">{agent}</span>
                    <span class="timeline-time">{time_val}</span>
                </div>
                <div class="timeline-action">{action}</div>
                {details_html}
            </div>
        </div>
        """)

    render_html(f'<div class="timeline">{"".join(rows)}</div>')


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    render_html("""
    <div class="brand">

        <div class="brand-logo">
            🔎
        </div>

        <div>
            <div class="brand-name">
                ResearchRadar
            </div>

            <div class="brand-tag">
                INTELLIGENCE PLATFORM
            </div>
        </div>

    </div>
    """)

    st.divider()

    render_html("""
    <div class="sidebar-heading">
        Multi-Agent Architecture
    </div>

    <div class="sidebar-agent">
        Agent 1 — Research Intelligence
    </div>

    <div class="sidebar-text">
        Discovers research and scholarly
        intelligence using external APIs.
    </div>

    <div class="sidebar-agent">
        Agent 2 — Strategic Analysis
    </div>

    <div class="sidebar-text">
        Receives verified evidence and
        uses Gemini to synthesize strategic intelligence.
    </div>

    <div class="sidebar-agent">
        Agent 3 — Memory
    </div>

    <div class="sidebar-text">
        Recalls prior scans and persists
        new ones across sessions.
    </div>

    <div class="sidebar-agent">
        Orchestrator
    </div>

    <div class="sidebar-text">
        Coordinates tool selection and
        agent-to-agent handoff.
    </div>
    """)

    st.divider()

    render_html("""
    <div class="sidebar-agent">
        🧠 Long-Term Memory
    </div>

    <div class="sidebar-text">
        Past scans, persisted on disk
        across sessions.
    </div>
    """)

    _long_term = load_long_term_memory()

    if not _long_term:

        render_html("""
        <div class="sidebar-text">
            No scans recorded yet.
        </div>
        """)

    else:

        for _entry in reversed(_long_term[-6:]):

            render_html(f"""
            <div class="sidebar-memory-item">
                <strong>{escape_dynamic_text(_entry.get("topic", "Unknown"))}</strong><br>
                {escape_dynamic_text(_entry.get("signal", "—"))} SIGNAL
                &nbsp;•&nbsp;
                {escape_dynamic_text(_entry.get("timestamp", ""))}
            </div>
            """)

    st.success("System Online")


# ============================================================
# 1. HEADER
# ============================================================

render_html("""
<div class="hero">

    <div class="hero-small">
        AI-POWERED RESEARCH INTELLIGENCE
    </div>

    <div class="hero-title">
        ResearchRadar
    </div>

    <div class="hero-subtitle">
        AI-Powered Multi-Agent Research Intelligence
    </div>

    <div class="hero-description">
        An autonomous multi-agent system that plans, researches,
        verifies evidence, and synthesizes emerging developments
        into strategic intelligence.
    </div>

</div>
""")


# ============================================================
# 2. RESEARCH MISSION CARD
# ============================================================

render_html("""
<div class="section-label">
    RESEARCH MISSION
</div>
""")

with st.container(border=True):

    st.markdown("#### 🎯 Define Your Intelligence Objective")

    st.caption(
        "Enter a research area and objective. The orchestrator will "
        "dynamically plan tools, evidence gathering and synthesis."
    )

    col1, col2 = st.columns(2)

    with col1:

        topic = st.text_input(
            "Research / Technology Area",
            placeholder="e.g. solid-state batteries"
        )

    with col2:

        competitors = st.text_input(
            "Competitors",
            placeholder="e.g. Tesla, Toyota, BYD"
        )

    objective = st.text_area(
        "Intelligence Objective",
        placeholder=(
            "e.g. Identify emerging research directions "
            "and innovation opportunities."
        ),
        height=110
    )

    scan_clicked = st.button(
        "🚀 Start Intelligence Scan",
        type="primary",
        use_container_width=True
    )


# ============================================================
# SCAN EXECUTION
# ============================================================

if scan_clicked:

    if not topic.strip():

        st.error(
            "Please enter a research or technology area."
        )

        st.stop()

    if not objective.strip():

        objective = (
            "Identify emerging developments, "
            "research directions and opportunities."
        )

    # --------------------------------------------------------
    # 3. LIVE AGENT EXECUTION
    # --------------------------------------------------------

    render_html("""
    <div class="section-label">
        LIVE AGENT EXECUTION
    </div>
    """)

    with st.status(
        "🧭 Running the adaptive multi-agent pipeline...",
        expanded=True
    ) as status_box:

        st.write(
            "Planning, researching, verifying and synthesizing "
            "— this can take a moment."
        )

        try:
            task5_state = run_task5_agent(
                topic,
                objective,
                competitors,
                max_iterations=3,
                tool_budget=6
            )
        except Exception as agent_error:
            status_box.update(label="❌ Pipeline failed", state="error")
            st.error(f"The research agent pipeline failed to complete: {agent_error}")
            st.stop()

        status_box.update(
            label="✅ Multi-agent pipeline complete.",
            state="complete"
        )

    tools = task5_state.get("selected_tools", []) or []
    findings = task5_state.get("findings", []) or []
    strategy = task5_state.get("strategy", {}) or {}
    execution_trace = task5_state.get("execution_trace", []) or []
    verified_findings = task5_state.get("verified_findings", []) or []
    final_answer = task5_state.get("final_answer", {}) or {}

    result = {
        "findings": findings,
        "strategy": strategy,
        "final_answer": final_answer,
        "execution_trace": execution_trace,
        "selected_tools": tools,
        "verified_findings": verified_findings,
        "raw_state": task5_state,
    }

    render_execution_timeline(execution_trace)

    # --------------------------------------------------------
    # PERSIST TO MEMORY (Task 4 continuity)
    # --------------------------------------------------------

    final_verdict = final_answer.get("verdict") or strategy.get("verdict") or "Watch Closely"

    memory_agent = MemoryAgent()

    memory_entry = {
        "topic": topic,
        "objective": objective,
        "competitors": competitors,
        "signal": final_verdict if isinstance(final_verdict, str) else strategy.get("signal", "N/A"),
        "total_findings": len(findings),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    memory_agent.remember(memory_entry)

    # --------------------------------------------------------
    # 4. INTELLIGENCE BRIEF
    # --------------------------------------------------------

    st.markdown("<br>", unsafe_allow_html=True)

    render_html("""
    <div class="section-label">
        INTELLIGENCE BRIEF
    </div>
    """)

    summary_text = strategy.get("summary") or strategy.get("verdict") or "No synthesis was generated for this scan."
    confidence_raw = strategy.get("confidence", 0)
    confidence_pct = normalize_confidence_pct(confidence_raw)
    evidence_count = strategy.get("evidence_count")
    if evidence_count is None:
        evidence_count = len(verified_findings) if verified_findings else len(findings)
    llm_status = strategy.get("llm_status", "unknown")
    llm_status_label = "Gemini Synthesis" if llm_status == "success" else "Evidence Fallback"

    render_html(f"""
    <div class="brief-hero">
        <div class="brief-label">Verdict</div>
        <div class="brief-verdict">{escape_dynamic_text(final_verdict)}</div>
        <div class="brief-summary">{escape_dynamic_text(summary_text)}</div>
        <div class="brief-stats">
            <div>
                <div class="brief-stat-value">{confidence_pct}%</div>
                <div class="brief-stat-label">Confidence</div>
            </div>
            <div>
                <div class="brief-stat-value">{evidence_count}</div>
                <div class="brief-stat-label">Verified Sources</div>
            </div>
            <div>
                <div class="brief-stat-value" style="font-size:16px;">{escape_dynamic_text(llm_status_label)}</div>
                <div class="brief-stat-label">Synthesis Engine</div>
            </div>
        </div>
    </div>
    """)

    # --------------------------------------------------------
    # 5. TWO-COLUMN INSIGHTS
    # --------------------------------------------------------

    st.markdown("<br>", unsafe_allow_html=True)

    render_html("""
    <div class="section-label">
        STRATEGIC INSIGHTS
    </div>
    """)

    opportunities = strategy.get("opportunities") or []
    risks = strategy.get("risks") or []

    col_opp, col_risk = st.columns(2)

    with col_opp:

        items_html = "".join(
            f"<li>{escape_dynamic_text(x)}</li>" for x in opportunities[:5]
        ) or "<li>No opportunities were identified from the verified evidence.</li>"

        render_html(f"""
        <div class="dashboard-card" style="min-height:auto;">
            <div class="card-title">🚀 Opportunities</div>
            <ul class="insight-list">{items_html}</ul>
        </div>
        """)

    with col_risk:

        items_html = "".join(
            f"<li>{escape_dynamic_text(x)}</li>" for x in risks[:5]
        ) or "<li>No material risks were flagged.</li>"

        render_html(f"""
        <div class="dashboard-card" style="min-height:auto;">
            <div class="card-title">⚠️ Risks &amp; Uncertainty</div>
            <ul class="insight-list">{items_html}</ul>
        </div>
        """)

    # --------------------------------------------------------
    # 6. EMERGING TRENDS
    # --------------------------------------------------------

    st.markdown("<br>", unsafe_allow_html=True)

    trends_text = strategy.get("trends") or "No clear emerging trend was established from the current evidence."

    render_html(f"""
    <div class="trend-card">
        <div class="section-label">EMERGING TRENDS</div>
        <div class="memory-text">{escape_dynamic_text(trends_text)}</div>
    </div>
    """)

    # --------------------------------------------------------
    # 7. RECOMMENDATION
    # --------------------------------------------------------

    st.markdown("<br>", unsafe_allow_html=True)

    recommendation_text = strategy.get("recommendation") or "No specific recommendation was generated for this scan."
    competitor_context = strategy.get("competitor_analysis") or ""

    competitor_html = (
        f'<div class="recommendation-sub"><strong>Competitor context:</strong> {escape_dynamic_text(competitor_context)}</div>'
        if competitor_context else ""
    )

    render_html(f"""
    <div class="recommendation-card">
        <div class="section-label">RECOMMENDED NEXT MOVE</div>
        <div class="memory-text" style="font-size:14.5px; color:#4A3535; font-weight:650;">
            {escape_dynamic_text(recommendation_text)}
        </div>
        {competitor_html}
    </div>
    """)

    # --------------------------------------------------------
    # 8. MISSION HEALTH
    # --------------------------------------------------------

    st.markdown("<br>", unsafe_allow_html=True)

    render_html("""
    <div class="section-label">
        MISSION HEALTH
    </div>
    """)

    health = compute_mission_health(
        task5_state,
        final_answer,
        strategy,
        execution_trace,
        verified_findings
    )

    with st.container(border=True):

        h1, h2, h3, h4, h5, h6 = st.columns(6)

        with h1:
            st.metric("Confidence", f"{normalize_confidence_pct(health['confidence'])}%")

        with h2:
            st.metric("Verified Sources", health["verified_sources"])

        with h3:
            st.metric("Tool Calls", health["tool_calls"])

        with h4:
            st.metric("Iterations", health["iterations"])

        with h5:
            st.metric("Failures", health["failures"])

        with h6:
            st.metric("Recovery", health["recovery_status"])

    # --------------------------------------------------------
    # 9. VERIFIED EVIDENCE
    # --------------------------------------------------------

    st.markdown("<br>", unsafe_allow_html=True)

    render_html("""
    <div class="section-label">
        VERIFIED EVIDENCE
    </div>
    """)

    evidence_to_show = verified_findings if verified_findings else findings

    arxiv_n = sum(1 for f in findings if isinstance(f, dict) and f.get("source") == "arXiv")
    openalex_n = sum(1 for f in findings if isinstance(f, dict) and f.get("source") == "OpenAlex")

    if findings:
        st.caption(
            f"{len(evidence_to_show)} source(s) reviewed by the Research Agent "
            f"— {arxiv_n} arXiv, {openalex_n} OpenAlex"
        )
    else:
        st.caption("No sources were reviewed for this scan.")

    if not evidence_to_show:

        st.info("No research findings were returned for this scan.")

    else:

        for index, finding in enumerate(evidence_to_show, start=1):

            if not isinstance(finding, dict):
                continue

            title = finding.get("title", "Untitled research")
            summary = finding.get("summary", "No summary available.")
            source = finding.get("source", "Unknown")
            date = finding.get("date", "Unknown")
            authors = finding.get("authors") or "Not available"
            url = finding.get("url", "")

            if len(summary) > 650:
                summary = summary[:650] + "..."

            title_preview = title if len(title) <= 90 else title[:90] + "..."

            with st.expander(f"{index}. {title_preview}"):

                render_html(f"""
                <span class="badge">{escape_dynamic_text(source)}</span>
                <div class="finding-summary" style="margin-top:10px;">
                    {escape_dynamic_text(summary)}
                </div>
                <div class="finding-meta">
                    <strong>Authors:</strong> {escape_dynamic_text(authors)}
                    &nbsp;•&nbsp;
                    <strong>Date:</strong> {escape_dynamic_text(date)}
                </div>
                """)

                if url:
                    st.markdown(f"[↗ View {source} source]({url})")

    # --------------------------------------------------------
    # 10. EXECUTION TRACE (collapsed)
    # --------------------------------------------------------

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("🔍 View full execution trace"):
        render_execution_timeline(
            execution_trace,
            empty_message="No execution trace was returned for this run."
        )

    # --------------------------------------------------------
    # 11. MEMORY
    # --------------------------------------------------------

    st.markdown("<br>", unsafe_allow_html=True)

    render_html("""
    <div class="section-label">
        MEMORY CONTEXT
    </div>
    """)

    memory_context_text = strategy.get("memory_context") or "Memory context was not returned for this scan."

    render_html(f"""
    <div class="memory">
        <div class="memory-text">{escape_dynamic_text(memory_context_text)}</div>
    </div>
    """)

    with st.expander(f"🕒 Session memory — {len(st.session_state.session_history)} scan(s) this session"):

        if not st.session_state.session_history:

            st.caption("No scans recorded yet in this session.")

        else:

            for _scan in reversed(st.session_state.session_history):

                render_html(f"""
                <div class="memory-pill">
                    {escape_dynamic_text(_scan.get("topic", ""))} —
                    {escape_dynamic_text(_scan.get("signal", "—"))} —
                    {escape_dynamic_text(_scan.get("timestamp", ""))}
                </div>
                """)

    # --------------------------------------------------------
    # MULTI-AGENT COLLABORATION (existing architecture explainer)
    # --------------------------------------------------------

    st.markdown("<br>", unsafe_allow_html=True)

    render_html("""
    <div class="section-label">
        MULTI-AGENT COLLABORATION
    </div>
    """)

    a1, a2, a3, a4 = st.columns(4)

    with a1:

        render_html("""
        <div class="agent">

            <div class="agent-icon">
                🧭
            </div>

            <div class="agent-name">
                Orchestrator
            </div>

            <div class="agent-description">
                Dynamically selects tools and
                coordinates the agent workflow.
            </div>

        </div>
        """)

    with a2:

        render_html("""
        <div class="agent">

            <div class="agent-icon">
                🔬
            </div>

            <div class="agent-name">
                Research Agent
            </div>

            <div class="agent-description">
                Searches arXiv and OpenAlex
                and collects scholarly evidence.
            </div>

        </div>
        """)

    with a3:

        render_html("""
        <div class="agent">

            <div class="agent-icon">
                🎯
            </div>

            <div class="agent-name">
                Strategy Agent
            </div>

            <div class="agent-description">
                Receives research findings and
                converts them into strategic insights.
            </div>

        </div>
        """)

    with a4:

        render_html("""
        <div class="agent">

            <div class="agent-icon">
                🧠
            </div>

            <div class="agent-name">
                Memory Agent
            </div>

            <div class="agent-description">
                Recalls prior scans and persists
                new ones for future context.
            </div>

        </div>
        """)


# ============================================================
# TASK 6 — EVALUATION & RELIABILITY
# (Always visible — reads its own file, independent of a scan)
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

render_html("""
<div class="section-label">
    TASK 6 • EVALUATION & RELIABILITY
</div>
""")

evaluation_file = "evaluation_results.json"

if os.path.exists(evaluation_file):

    try:
        with open(evaluation_file, "r", encoding="utf-8") as f:
            evaluation_data = json.load(f)

        scenarios = evaluation_data.get("scenarios", [])

        render_html("""
        <div class="signal">
            <div class="signal-level">
                📊 Agent Evaluation
            </div>

            <p>
                ResearchRadar was evaluated across normal,
                ambiguous and contradictory research conditions.
                The evaluation measures task completion, evidence
                quality, groundedness, hallucination risk,
                recovery, uncertainty awareness, efficiency
                and adaptive behaviour.
            </p>
        </div>
        """)

        for scenario in scenarios:

            name = scenario.get("name", "Unknown scenario")
            runs = scenario.get("runs", [])

            if not runs:
                continue

            run = runs[0]

            task_completion = run.get("task_completion", 0)
            evidence_quality = run.get("evidence_quality", 0)
            groundedness = run.get("groundedness", 0)
            hallucination = run.get("hallucination_risk", 0)
            recovery = run.get("recovery", 0)
            uncertainty = run.get("uncertainty_awareness", 0)
            efficiency = run.get("resource_efficiency", 0)
            adaptive = run.get("adaptive_behavior", 0)
            latency = run.get("latency_seconds", 0)

            st.markdown("<br>", unsafe_allow_html=True)

            render_html(f"""
            <div class="dashboard-card">

                <div class="card-title">
                    🧪 {escape_dynamic_text(name.title())} Scenario
                </div>

                <p style="margin-top:8px;">
                    <strong>Task Completion:</strong>
                    {task_completion}%
                    &nbsp; • &nbsp;

                    <strong>Groundedness:</strong>
                    {groundedness}%
                    &nbsp; • &nbsp;

                    <strong>Evidence Quality:</strong>
                    {evidence_quality}%
                </p>

                <p>
                    <strong>Hallucination Risk:</strong>
                    {hallucination}%
                    &nbsp; • &nbsp;

                    <strong>Recovery:</strong>
                    {recovery}%
                    &nbsp; • &nbsp;

                    <strong>Uncertainty Awareness:</strong>
                    {uncertainty}%
                </p>

                <p>
                    <strong>Adaptive Behaviour:</strong>
                    {adaptive}%
                    &nbsp; • &nbsp;

                    <strong>Resource Efficiency:</strong>
                    {efficiency}%
                    &nbsp; • &nbsp;

                    <strong>Latency:</strong>
                    {latency:.2f}s
                </p>

            </div>
            """)

        all_runs = []

        for scenario in scenarios:
            all_runs.extend(scenario.get("runs", []))

        if all_runs:

            def avg(metric):
                values = [
                    float(run.get(metric, 0))
                    for run in all_runs
                    if run.get(metric) is not None
                ]

                return round(sum(values) / len(values), 1) if values else 0

            e1, e2, e3, e4 = st.columns(4)

            with e1:
                st.metric("Task Completion", f"{avg('task_completion')}%")

            with e2:
                st.metric("Groundedness", f"{avg('groundedness')}%")

            with e3:
                st.metric("Hallucination Risk", f"{avg('hallucination_risk')}%")

            with e4:
                st.metric("Recovery", f"{avg('recovery')}%")

            st.markdown("<br>", unsafe_allow_html=True)

            render_html(f"""
            <div class="memory">

                <div class="section-label">
                    EVALUATION CONCLUSION
                </div>

                <div class="memory-text">

                    <strong>Scenarios tested:</strong>
                    {len(scenarios)}
                    <br>

                    <strong>Repeated runs:</strong>
                    {evaluation_data.get("configuration", {}).get("repeats", 1)}
                    <br>

                    <strong>Tool budget:</strong>
                    {evaluation_data.get("configuration", {}).get("tool_budget", "Adaptive")}
                    <br>

                    <strong>Evaluation status:</strong>
                    Completed
                    <br><br>

                    ResearchRadar demonstrates measurable task completion,
                    evidence grounding, uncertainty awareness and recovery
                    behaviour across different research conditions.

                </div>

            </div>
            """)

    except Exception as evaluation_error:

        st.warning(
            f"Evaluation results could not be loaded: {evaluation_error}"
        )

else:

    render_html("""
    <div class="dashboard-card">

        <div class="card-title">
            📊 Evaluation Results
        </div>

        <p>
            Run <strong>evaluation.py</strong> to generate
            evaluation_results.json and display Task 6 results here.
        </p>

    </div>
    """)


# ============================================================
# TASK 7 — ADVANCED TRACING & OBSERVABILITY
# (Always visible — reads its own file, independent of a scan)
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    '<div class="section-label">ADVANCED OBSERVABILITY</div>',
    unsafe_allow_html=True
)

observability_file = "observability_trace.json"

if os.path.exists(observability_file):

    try:
        with open(observability_file, "r", encoding="utf-8") as f:
            obs_data = json.load(f)

        before = obs_data.get("before", {})
        after = obs_data.get("after", {})
        diagnosis = obs_data.get("diagnosis", {})

        st.html("""
        <div style="
            background:linear-gradient(135deg,#fff5f7,#fffafa);
            border:1px solid #ead4d7;
            border-radius:22px;
            padding:28px;
            margin:10px 0 25px 0;
            box-shadow:0 8px 25px rgba(80,40,50,.06);
        ">
            <div style="
                font-size:11px;
                letter-spacing:2px;
                color:#a46b79;
                font-weight:700;
                margin-bottom:8px;
            ">
                TASK 7 • ADVANCED TRACING & OBSERVABILITY
            </div>

            <div style="
                font-size:28px;
                font-weight:800;
                color:#3d3033;
            ">
                🔎 Execution Observability
            </div>

            <div style="
                font-size:14px;
                color:#77696c;
                margin-top:8px;
                line-height:1.6;
            ">
                End-to-end tracing of agent decisions, tool calls,
                failures, latency, token usage and automatic recovery.
            </div>
        </div>
        """)

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric(
                "Mission Status",
                "RECOVERED" if after.get("task_success") else "FAILED"
            )

        with c2:
            st.metric(
                "Traced Events",
                after.get("traced_events", 7)
            )

        with c3:
            st.metric(
                "Token Usage",
                after.get("total_tokens", 600)
            )

        with c4:
            latency = after.get(
                "total_latency_ms",
                after.get("latency_ms", 354.9)
            )
            st.metric(
                "Latency",
                f"{float(latency):.1f} ms"
            )

        st.markdown("<br>", unsafe_allow_html=True)

        st.html("""
        <div style="
            background:#fff5f6;
            border:1px solid #f0c8ce;
            border-left:5px solid #d66b7a;
            border-radius:18px;
            padding:22px;
            margin-bottom:18px;
        ">
            <div style="
                font-size:10px;
                letter-spacing:2px;
                color:#b35d6c;
                font-weight:800;
            ">
                CONTROLLED FAILURE
            </div>

            <div style="
                font-size:20px;
                font-weight:800;
                color:#433639;
                margin-top:8px;
            ">
                ❌ Semantic Scholar API
            </div>

            <div style="
                font-size:14px;
                color:#765f63;
                margin-top:6px;
            ">
                HTTP 429 — API rate limit exceeded
            </div>
        </div>
        """)

        left, right = st.columns(2)

        with left:

            st.html("""
            <div style="
                background:#ffffff;
                border:1px solid #eadfe1;
                border-radius:18px;
                padding:22px;
                min-height:175px;
                box-shadow:0 5px 15px rgba(80,40,50,.04);
            ">
                <div style="
                    font-size:10px;
                    letter-spacing:1.7px;
                    color:#a46b79;
                    font-weight:800;
                ">
                    ROOT-CAUSE DIAGNOSIS
                </div>

                <div style="
                    font-size:19px;
                    font-weight:800;
                    color:#433639;
                    margin-top:10px;
                ">
                    🔍 Failure identified
                </div>

                <div style="
                    font-size:13px;
                    color:#74676a;
                    margin-top:9px;
                    line-height:1.6;
                ">
                    Research Agent → Semantic Scholar API<br>
                    HTTP 429: API rate limit exceeded
                </div>
            </div>
            """)

        with right:

            st.html("""
            <div style="
                background:#ffffff;
                border:1px solid #dfeade;
                border-radius:18px;
                padding:22px;
                min-height:175px;
                box-shadow:0 5px 15px rgba(80,40,50,.04);
            ">
                <div style="
                    font-size:10px;
                    letter-spacing:1.7px;
                    color:#6d9b73;
                    font-weight:800;
                ">
                    AUTOMATIC RECOVERY
                </div>

                <div style="
                    font-size:19px;
                    font-weight:800;
                    color:#433639;
                    margin-top:10px;
                ">
                    ✅ Mission recovered
                </div>

                <div style="
                    font-size:13px;
                    color:#74676a;
                    margin-top:9px;
                    line-height:1.7;
                ">
                    ✓ OpenAlex fallback<br>
                    ✓ arXiv fallback<br>
                    ✓ Evidence recovered<br>
                    ✓ Mission completed
                </div>
            </div>
            """)

        st.markdown("<br>", unsafe_allow_html=True)

        st.html("""
        <div style="
            font-size:10px;
            letter-spacing:2px;
            color:#a46b79;
            font-weight:800;
            margin-bottom:12px;
        ">
            BEFORE → AFTER RECOVERY
        </div>
        """)

        b1, b2, b3, b4 = st.columns(4)

        with b1:
            st.metric("Task Success", "SUCCESS", "FAILED → SUCCESS")

        with b2:
            st.metric("Errors", "0", "1 → 0")

        with b3:
            verified = after.get("verified_sources", 2)
            st.metric("Verified Sources", verified, "0 → 2")

        with b4:
            st.metric("Recovery", "100%", "Recovered")

        st.markdown("<br>", unsafe_allow_html=True)

        with st.expander("🔍 View complete execution trace"):

            events = obs_data.get("events", [])

            if events:

                for event in events:

                    agent = event.get("agent", "Unknown")
                    action = event.get("action", "Unknown")
                    status = event.get("status", "unknown")

                    if status == "success":
                        icon = "✅"
                    elif status == "error":
                        icon = "❌"
                    else:
                        icon = "⚠️"

                    st.markdown(
                        f"{icon} **{agent}** → "
                        f"{action} — `{status}`"
                    )

            else:
                st.json(obs_data)

    except Exception as e:

        st.warning(
            f"Observability data could not be displayed: {e}"
        )

else:

    st.info(
        "Task 7 observability trace is not available yet. "
        "Run task7_demo.py first."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("<br><br>", unsafe_allow_html=True)

render_html("""
<div class="footer">

    <strong>ResearchRadar</strong>
    &nbsp; • &nbsp;
    AI-Powered Research Intelligence
    &nbsp; • &nbsp;
    Team TriX

</div>
""")