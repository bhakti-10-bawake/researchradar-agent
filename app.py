import streamlit as st
import requests
import xml.etree.ElementTree as ET
import textwrap


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ResearchRadar",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)



def render_html(content):
    lines = content.strip("\n").split("\n")
    cleaned = "\n".join(line.strip() for line in lines)
    st.markdown(cleaned, unsafe_allow_html=True)


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
# TOOL ORCHESTRATOR
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

    # OpenAlex is always useful for scholarly research.
    selected.append("OpenAlex")

    return list(dict.fromkeys(selected))


# ============================================================
# AGENT 1 — RESEARCH AGENT
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
# AGENT 2 — STRATEGY AGENT
# ============================================================

class StrategyAgent:

    def run(
        self,
        topic,
        findings,
        competitors
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
            "total": total,
            "arxiv": arxiv_count,
            "openalex": openalex_count
        }


# ============================================================
# ORCHESTRATOR — TASK 3
# ============================================================

class ResearchRadarOrchestrator:

    def run(
        self,
        topic,
        objective,
        competitors
    ):

        # STEP 1
        tools = select_tools(topic)

        # STEP 2
        research_agent = ResearchAgent(tools)

        findings = research_agent.run(
            topic
        )

        # STEP 3
        strategy_agent = StrategyAgent()

        strategy = strategy_agent.run(
            topic,
            findings,
            competitors
        )

        return {
            "tools": tools,
            "findings": findings,
            "strategy": strategy,
            "objective": objective
        }


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
        Receives Agent 1 findings and
        converts them into strategic insights.
    </div>

    <div class="sidebar-agent">
        Orchestrator
    </div>

    <div class="sidebar-text">
        Coordinates tool selection and
        agent-to-agent handoff.
    </div>
    """)

    st.success("System Online")


# ============================================================
# HERO
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
        Discover research. Detect signals.
        Make smarter decisions.
    </div>

    <div class="hero-description">
        An autonomous multi-agent intelligence
        system that searches scholarly research,
        synthesizes evidence, and transforms
        emerging developments into strategic insights.
    </div>

</div>
""")


# ============================================================
# DASHBOARD
# ============================================================

render_html("""
<div class="section-label">
    INTELLIGENCE WORKSPACE
</div>
""")

d1, d2, d3, d4 = st.columns(4)

with d1:

    render_html("""
    <div class="dashboard-card">

        <div class="card-title">
            🔬 Research Agent
        </div>

        <div class="card-value">
            Ready
        </div>

        <div class="card-caption">
            Research discovery & evidence
        </div>

    </div>
    """)

with d2:

    render_html("""
    <div class="dashboard-card">

        <div class="card-title">
            🎯 Strategy Agent
        </div>

        <div class="card-value">
            Ready
        </div>

        <div class="card-caption">
            Strategic analysis
        </div>

    </div>
    """)

with d3:

    render_html("""
    <div class="dashboard-card">

        <div class="card-title">
            🛠️ Intelligence Tools
        </div>

        <div class="card-value">
            02
        </div>

        <div class="card-caption">
            arXiv + OpenAlex
        </div>

    </div>
    """)

with d4:

    render_html("""
    <div class="dashboard-card">

        <div class="card-title">
            ⚡ System Status
        </div>

        <div class="card-value">
            LIVE
        </div>

        <div class="card-caption">
            Intelligence system online
        </div>

    </div>
    """)


st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# WORKFLOW
# ============================================================

render_html("""
<div class="section-label">
    AUTONOMOUS AGENT WORKFLOW
</div>
""")

w1, w2, w3, w4 = st.columns(4)

workflow_data = [
    ("01", "Define", "Research objective"),
    ("02", "Discover", "arXiv + OpenAlex"),
    ("03", "Analyze", "Strategic signals"),
    ("04", "Decide", "Actionable insights")
]

for column, item in zip(
    [w1, w2, w3, w4],
    workflow_data
):

    number, title, description = item

    with column:

        render_html(f"""
        <div class="workflow">

            <div class="workflow-number">
                {number}
            </div>

            <div class="workflow-title">
                {title}
            </div>

            <div class="workflow-text">
                {description}
            </div>

        </div>
        """)


st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# INPUT
# ============================================================

render_html("""
<div class="section-label">
    INTELLIGENCE SCAN
</div>
""")

st.header("🎯 Define Your Intelligence Objective")

st.write(
    "Enter a research area and objective. "
    "The orchestrator will dynamically select "
    "the relevant external intelligence tools."
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


# ============================================================
# SCAN BUTTON
# ============================================================

if st.button(
    "🚀 Start Intelligence Scan",
    type="primary",
    use_container_width=True
):

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
    # ORCHESTRATOR
    # --------------------------------------------------------

    orchestrator = ResearchRadarOrchestrator()

    # --------------------------------------------------------
    # TOOL SELECTION
    # --------------------------------------------------------

    with st.status(
        "🧭 ResearchRadar agents working...",
        expanded=True
    ):

        st.write(
            "🧭 **Orchestrator:** Understanding objective..."
        )

        tools = select_tools(topic)

        st.write(
            f"🛠️ **Tools selected:** "
            f"{', '.join(tools)}"
        )

        st.write(
            "🔬 **Research Agent:** "
            "Collecting scholarly evidence..."
        )

        result = orchestrator.run(
            topic,
            objective,
            competitors
        )

        st.write(
            "🎯 **Strategy Agent:** "
            "Analyzing research findings..."
        )

        st.write(
            "🤝 **Agent handoff:** "
            "Research Agent → Strategy Agent"
        )

        st.write(
            "✅ **Multi-agent pipeline complete.**"
        )


    findings = result["findings"]
    strategy = result["strategy"]


    # ========================================================
    # SUMMARY
    # ========================================================

    st.divider()

    render_html("""
    <div class="section-label">
        INTELLIGENCE SUMMARY
    </div>
    """)

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric(
            "Total Findings",
            strategy["total"]
        )

    with m2:
        st.metric(
            "arXiv",
            strategy["arxiv"]
        )

    with m3:
        st.metric(
            "OpenAlex",
            strategy["openalex"]
        )

    with m4:
        st.metric(
            "Signal",
            strategy["signal"]
        )


    # ========================================================
    # STRATEGIC VERDICT
    # ========================================================

    st.markdown("<br>", unsafe_allow_html=True)

    render_html(f"""
    <div class="signal">

        <div class="section-label">
            STRATEGIC VERDICT
        </div>

        <div class="signal-level">
            {strategy["signal"]} SIGNAL
        </div>

        <p>
            {strategy["verdict"]}
        </p>

        <p>
            <strong>Recommendation:</strong>
            {strategy["recommendation"]}
        </p>

        <p>
            <strong>Competitor Context:</strong>
            {strategy["competitor_analysis"]}
        </p>

    </div>
    """)


    # ========================================================
    # FINDINGS
    # ========================================================

    st.markdown("<br>", unsafe_allow_html=True)

    render_html("""
    <div class="section-label">
        RESEARCH INTELLIGENCE
    </div>
    """)

    st.header("📚 Scholarly Findings")

    if not findings:

        st.warning(
            "No research findings were returned."
        )

    else:

        for index, finding in enumerate(
            findings,
            start=1
        ):

            title = finding.get(
                "title",
                "Untitled research"
            )

            summary = finding.get(
                "summary",
                "No summary available."
            )

            source = finding.get(
                "source",
                "Unknown"
            )

            date = finding.get(
                "date",
                "Unknown"
            )

            authors = finding.get(
                "authors",
                "Not available"
            )

            url = finding.get(
                "url",
                ""
            )

            if len(summary) > 650:
                summary = summary[:650] + "..."

            render_html(f"""
            <div class="finding">

                <span class="badge">
                    {source}
                </span>

                <div class="finding-title">
                    {index}. {title}
                </div>

                <div class="finding-summary">
                    {summary}
                </div>

                <div class="finding-meta">
                    <strong>Authors:</strong>
                    {authors if authors else "Not available"}

                    &nbsp; • &nbsp;

                    <strong>Date:</strong>
                    {date}
                </div>

            </div>
            """)

            if url:

                st.markdown(
                    f"[↗ View {source} source]({url})"
                )


    # ========================================================
    # MULTI-AGENT COLLABORATION
    # ========================================================

    st.markdown("<br>", unsafe_allow_html=True)

    render_html("""
    <div class="section-label">
        MULTI-AGENT COLLABORATION
    </div>
    """)

    a1, a2, a3 = st.columns(3)

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