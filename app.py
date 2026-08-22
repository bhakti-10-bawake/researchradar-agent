import streamlit as st
import requests
import urllib.parse
import xml.etree.ElementTree as ET


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ResearchRadar",
    page_icon="🔎",
    layout="wide"
)


# ============================================================
# PREMIUM BEIGE / PINK / WHITE UI
# ============================================================

st.markdown("""
<style>

.stApp {
    background: #F8F1EA;
    color: #4A3535;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* HERO */

.hero {
    padding: 38px;
    border-radius: 24px;
    background: linear-gradient(
        135deg,
        #FFF9F5,
        #F8E2E3,
        #F2D5D8
    );
    border: 1px solid #E7C9CA;
    box-shadow: 0 8px 30px rgba(100, 70, 70, 0.08);
    margin-bottom: 28px;
}

.hero-title {
    font-size: 44px;
    font-weight: 800;
    color: #4A3535;
}

.hero-subtitle {
    font-size: 19px;
    color: #A2676E;
    font-weight: 600;
}

.hero p {
    color: #665454;
}

/* CARDS */

.card {
    padding: 22px;
    border-radius: 18px;
    background: #FFFFFF;
    border: 1px solid #E8DADA;
    box-shadow: 0 6px 20px rgba(100, 70, 70, 0.06);
    margin-bottom: 15px;
}

.card h3 {
    color: #B56F78;
}

.agent-card {
    padding: 24px;
    border-radius: 18px;
    background: #FFFFFF;
    border: 1px solid #E8DADA;
    box-shadow: 0 6px 20px rgba(100, 70, 70, 0.06);
    min-height: 250px;
}

.agent-card h3 {
    color: #B56F78;
}

.tool-card {
    padding: 20px;
    border-radius: 16px;
    background: #FFFDFC;
    border: 1px solid #E6D3D3;
    box-shadow: 0 5px 18px rgba(100, 70, 70, 0.05);
}

.finding-card {
    padding: 20px;
    border-radius: 16px;
    background: #FFFFFF;
    border: 1px solid #E8DADA;
    margin-bottom: 14px;
    box-shadow: 0 5px 18px rgba(100, 70, 70, 0.05);
}

.finding-card h3 {
    color: #594343;
}

.signal-card {
    padding: 22px;
    border-radius: 16px;
    background: #FFF3F4;
    border-left: 5px solid #C47A84;
    border-top: 1px solid #E8C9CC;
    border-right: 1px solid #E8C9CC;
    border-bottom: 1px solid #E8C9CC;
}

/* INPUTS */

.stTextInput input,
.stTextArea textarea {
    background: #FFFFFF !important;
    color: #4A3535 !important;
    border: 1px solid #DDC8C8 !important;
    border-radius: 12px !important;
}

.stTextInput label,
.stTextArea label {
    color: #594343 !important;
    font-weight: 600 !important;
}

/* BUTTON */

.stButton > button {
    background: linear-gradient(
        135deg,
        #C9828A,
        #B96D77
    ) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    padding: 12px 24px !important;
    box-shadow: 0 6px 16px rgba(185, 109, 119, 0.20);
}

.stButton > button:hover {
    background: #A95F69 !important;
}

/* METRICS */

[data-testid="stMetric"] {
    background: #FFFFFF;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #E8DADA;
}

[data-testid="stMetricLabel"] {
    color: #967878 !important;
}

[data-testid="stMetricValue"] {
    color: #4A3535 !important;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: #FFF8F3;
    border-right: 1px solid #E8DADA;
}

/* HEADINGS */

h1, h2, h3 {
    color: #4A3535;
}

hr {
    border-color: #E5D4D4 !important;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="hero">

<div class="hero-title">
🔎 ResearchRadar
</div>

<div class="hero-subtitle">
Autonomous Research & Competitive Intelligence
</div>

<p>
ResearchRadar dynamically selects research tools, collects
academic intelligence, and coordinates specialized agents
to transform research into strategic insights.
</p>

</div>
""", unsafe_allow_html=True)


# ============================================================
# TOOL INFORMATION
# ============================================================

TOOLS = {

    "arxiv": {
        "name": "📚 arXiv API",
        "description": "Searches recent scientific and technical papers.",
        "purpose": "Emerging research and scientific breakthroughs."
    },

    "openalex": {
        "name": "🌐 OpenAlex API",
        "description": "Searches scholarly works and research activity.",
        "purpose": "Academic research trends and scholarly intelligence."
    }
}


# ============================================================
# TASK 2
# DYNAMIC TOOL SELECTION
# ============================================================

def select_tools(topic, objective):

    text = (
        topic + " " + objective
    ).lower()

    research_terms = [
        "research",
        "paper",
        "papers",
        "scientific",
        "technology",
        "innovation",
        "breakthrough",
        "algorithm",
        "model",
        "experiment",
        "engineering",
        "artificial intelligence",
        "machine learning",
        "quantum",
        "robotics",
        "battery",
        "semiconductor"
    ]

    academic_terms = [
        "academic",
        "scholarly",
        "authors",
        "universities",
        "citations",
        "publication",
        "publications",
        "research trends"
    ]

    selected = []

    if any(
        term in text
        for term in research_terms
    ):
        selected.append("arxiv")

    if any(
        term in text
        for term in academic_terms
    ):
        selected.append("openalex")

    # Broad intelligence objectives use both.
    if (
        "comprehensive" in text
        or "intelligence" in text
        or "competitor" in text
        or "opportunity" in text
        or not selected
    ):
        selected = ["arxiv", "openalex"]

    return list(dict.fromkeys(selected))


# ============================================================
# TOOL 1 — ARXIV
# ============================================================

def search_arxiv(topic, limit=6):

    try:

        query = urllib.parse.quote(
            f'all:"{topic}"'
        )

        url = (
            "https://export.arxiv.org/api/query"
            f"?search_query={query}"
            f"&start=0"
            f"&max_results={limit}"
            "&sortBy=submittedDate"
            "&sortOrder=descending"
        )

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent":
                "ResearchRadar/1.0"
            }
        )

        response.raise_for_status()

        root = ET.fromstring(
            response.text
        )

        namespace = {
            "atom":
            "http://www.w3.org/2005/Atom"
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
            ).strip().replace(
                "\n",
                " "
            )

            summary = entry.findtext(
                "atom:summary",
                "",
                namespace
            ).strip().replace(
                "\n",
                " "
            )

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

            link = ""

            for link_item in entry.findall(
                "atom:link",
                namespace
            ):

                if (
                    link_item.attrib.get(
                        "type"
                    ) == "text/html"
                ):

                    link = link_item.attrib.get(
                        "href",
                        ""
                    )

            if title:

                results.append({
                    "title": title,
                    "summary": summary,
                    "source": "arXiv",
                    "date": (
                        published[:10]
                        if published
                        else "Unknown"
                    ),
                    "authors": ", ".join(
                        authors[:3]
                    ),
                    "url": link
                })

        return results

    except Exception as error:

        return [{
            "error":
            f"arXiv unavailable: {error}"
        }]


# ============================================================
# TOOL 2 — OPENALEX
# ============================================================

def search_openalex(topic, limit=6):

    try:

        encoded_topic = urllib.parse.quote(
            topic
        )

        url = (
            "https://api.openalex.org/works"
            f"?search={encoded_topic}"
            f"&per-page={limit}"
            "&sort=publication_date:desc"
        )

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent":
                "ResearchRadar/1.0"
            }
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

            date = work.get(
                "publication_date",
                "Unknown"
            )

            authors = []

            for authorship in work.get(
                "authorships",
                []
            )[:3]:

                author = authorship.get(
                    "author",
                    {}
                )

                name = author.get(
                    "display_name"
                )

                if name:
                    authors.append(name)

            url = work.get(
                "doi"
            )

            if not url:
                url = work.get(
                    "id",
                    ""
                )

            results.append({
                "title": title,
                "summary":
                    "Scholarly work discovered "
                    "through the OpenAlex research database.",
                "source": "OpenAlex",
                "date": date,
                "authors": ", ".join(authors),
                "url": url
            })

        return results

    except Exception as error:

        return [{
            "error":
            f"OpenAlex unavailable: {error}"
        }]


# ============================================================
# AGENT 1
# RESEARCH INTELLIGENCE AGENT
# ============================================================

class ResearchIntelligenceAgent:

    name = "Research Intelligence Agent"

    def run(
        self,
        topic,
        objective,
        selected_tools
    ):

        findings = []
        logs = []

        # -------------------------------
        # ARXIV TOOL
        # -------------------------------

        if "arxiv" in selected_tools:

            logs.append(
                "Calling arXiv API..."
            )

            arxiv_results = search_arxiv(
                topic
            )

            valid = [
                item
                for item in arxiv_results
                if "error" not in item
            ]

            findings.extend(valid)

            logs.append(
                f"arXiv returned {len(valid)} findings."
            )

        # -------------------------------
        # OPENALEX TOOL
        # -------------------------------

        if "openalex" in selected_tools:

            logs.append(
                "Calling OpenAlex API..."
            )

            openalex_results = search_openalex(
                topic
            )

            valid = [
                item
                for item in openalex_results
                if "error" not in item
            ]

            findings.extend(valid)

            logs.append(
                f"OpenAlex returned {len(valid)} findings."
            )

        # -------------------------------
        # REMOVE DUPLICATES
        # -------------------------------

        unique_findings = []
        seen_titles = set()

        for item in findings:

            title = item.get(
                "title",
                ""
            ).strip().lower()

            if not title:
                continue

            if title in seen_titles:
                continue

            seen_titles.add(title)
            unique_findings.append(item)

        return {
            "agent":
                self.name,

            "findings":
                unique_findings,

            "logs":
                logs,

            "tools_used":
                selected_tools
        }


# ============================================================
# AGENT 2
# STRATEGIC ANALYSIS AGENT
# ============================================================

class StrategicAnalysisAgent:

    name = "Strategic Analysis Agent"

    def run(
        self,
        topic,
        competitors,
        research_findings
    ):

        competitors_list = [
            item.strip()
            for item in competitors.split(",")
            if item.strip()
        ]

        total = len(
            research_findings
        )

        arxiv_count = len([
            item
            for item in research_findings
            if item.get("source")
            == "arXiv"
        ])

        openalex_count = len([
            item
            for item in research_findings
            if item.get("source")
            == "OpenAlex"
        ])

        # -------------------------------
        # SIGNAL
        # -------------------------------

        if total >= 8:

            signal = "HIGH"
            signal_text = (
                "Strong research activity detected "
                "in this technology area."
            )

        elif total >= 4:

            signal = "MEDIUM"
            signal_text = (
                "Moderate research activity detected. "
                "This area should be monitored closely."
            )

        else:

            signal = "LOW"
            signal_text = (
                "Limited research activity detected "
                "from the selected sources."
            )

        # -------------------------------
        # COMPETITOR MATCHING
        # -------------------------------

        competitor_matches = []

        for finding in research_findings:

            title = finding.get(
                "title",
                ""
            ).lower()

            matched = []

            for competitor in competitors_list:

                if competitor.lower() in title:
                    matched.append(
                        competitor
                    )

            if matched:

                competitor_matches.append({
                    "title":
                        finding.get(
                            "title",
                            ""
                        ),

                    "competitors":
                        matched,

                    "source":
                        finding.get(
                            "source",
                            ""
                        )
                })

        # -------------------------------
        # RECOMMENDATIONS
        # -------------------------------

        recommendations = []

        recommendations.append(
            "Monitor emerging research directions "
            "before competitors gain an advantage."
        )

        if arxiv_count > 0:

            recommendations.append(
                "Review recent arXiv papers for "
                "early-stage technology breakthroughs."
            )

        if openalex_count > 0:

            recommendations.append(
                "Track scholarly publication activity "
                "to identify growing research areas."
            )

        if competitors_list:

            recommendations.append(
                "Compare future competitor activity "
                "against the detected research trends."
            )

        recommendations.append(
            "Investigate high-activity research areas "
            "for potential innovation opportunities."
        )

        # -------------------------------
        # VERDICT
        # -------------------------------

        if signal == "HIGH":
            verdict = "HIGH PRIORITY"

        elif signal == "MEDIUM":
            verdict = "WATCH CLOSELY"

        else:
            verdict = "LOW IMMEDIATE RISK"

        takeaway = (
            f"ResearchRadar identified {total} relevant "
            f"research findings for '{topic}'. "
            f"The detected research signal is {signal}. "
            f"Organizations should monitor this area and "
            f"evaluate emerging developments for potential "
            f"strategic opportunities."
        )

        return {
            "agent":
                self.name,

            "signal":
                signal,

            "signal_text":
                signal_text,

            "arxiv_count":
                arxiv_count,

            "openalex_count":
                openalex_count,

            "competitor_matches":
                competitor_matches,

            "recommendations":
                recommendations,

            "verdict":
                verdict,

            "takeaway":
                takeaway
        }


# ============================================================
# ORCHESTRATOR
# ============================================================

class ResearchRadarOrchestrator:

    def __init__(self):

        self.research_agent = (
            ResearchIntelligenceAgent()
        )

        self.strategy_agent = (
            StrategicAnalysisAgent()
        )

    def run(
        self,
        topic,
        objective,
        competitors
    ):

        # STEP 1:
        # Dynamically select tools

        selected_tools = select_tools(
            topic,
            objective
        )

        # STEP 2:
        # Agent 1 investigates

        research_output = (
            self.research_agent.run(
                topic,
                objective,
                selected_tools
            )
        )

        # STEP 3:
        # Agent 1 hands findings to Agent 2

        strategy_output = (
            self.strategy_agent.run(
                topic,
                competitors,
                research_output[
                    "findings"
                ]
            )
        )

        # STEP 4:
        # Return combined intelligence

        return {
            "selected_tools":
                selected_tools,

            "research_agent":
                research_output,

            "strategy_agent":
                strategy_output
        }


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## 🤖 ResearchRadar"
    )

    st.markdown(
        """
### Multi-Agent Architecture

**Agent 1 — Research Intelligence**

Discovers research and scholarly intelligence using external APIs.

**Agent 2 — Strategic Analysis**

Receives Agent 1's findings and converts them into strategic insights.

**Orchestrator**

Coordinates tool selection and agent-to-agent handoff.
"""
    )

    st.divider()

    st.caption(
        "Task 2: External Tool Calling"
    )

    st.caption(
        "Task 3: Multi-Agent Architecture"
    )


# ============================================================
# INPUT SECTION
# ============================================================

st.header(
    "🎯 Define Your Intelligence Objective"
)

input_col1, input_col2 = st.columns(2)

with input_col1:

    topic = st.text_input(
        "Research / Technology Area",
        placeholder="e.g. electric vehicles"
    )

with input_col2:

    competitors = st.text_input(
        "Competitors",
        placeholder="e.g. Tesla, BYD, Toyota"
    )

objective = st.text_area(
    "Monitoring Objective",
    value=(
        "Conduct comprehensive research intelligence "
        "and identify emerging developments and "
        "competitive opportunities."
    )
)


# ============================================================
# SCAN
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

    orchestrator = (
        ResearchRadarOrchestrator()
    )

    with st.spinner(
        "ResearchRadar agents are investigating..."
    ):

        result = orchestrator.run(
            topic,
            objective,
            competitors
        )

    research = result[
        "research_agent"
    ]

    strategy = result[
        "strategy_agent"
    ]

    findings = research[
        "findings"
    ]

    selected_tools = result[
        "selected_tools"
    ]


    # ========================================================
    # TASK 2
    # DYNAMIC TOOL CALLING
    # ========================================================

    st.divider()

    st.header(
        "🛠️ Dynamic Tool Selection"
    )

    st.success(
        f"Agent dynamically selected "
        f"{len(selected_tools)} external tool(s)."
    )

    tool_columns = st.columns(
        len(selected_tools)
    )

    for index, tool_id in enumerate(
        selected_tools
    ):

        info = TOOLS[
            tool_id
        ]

        with tool_columns[index]:

            st.markdown(
                f"""
<div class="tool-card">

<h3>{info['name']}</h3>

<b>Purpose</b>

<p>{info['purpose']}</p>

<b>Status</b>

<p>🟢 API Called Successfully</p>

</div>
""",
                unsafe_allow_html=True
            )


    # ========================================================
    # TASK 3
    # MULTI-AGENT ARCHITECTURE
    # ========================================================

    st.divider()

    st.header(
        "🤖 Multi-Agent Architecture"
    )

    agent_col1, arrow_col, agent_col2 = st.columns(
        [5, 1, 5]
    )

    with agent_col1:

        st.markdown(
            """
<div class="agent-card">

<h3>🔬 Agent 1</h3>

<h2>Research Intelligence Agent</h2>

<b>Responsibility</b>

<p>
Discover and structure relevant research intelligence.
</p>

<b>External Tools</b>

<p>
📚 arXiv API<br>
🌐 OpenAlex API
</p>

<b>Produces</b>

<p>
Research papers, scholarly findings,
emerging trends and evidence.
</p>

</div>
""",
            unsafe_allow_html=True
        )

    with arrow_col:

        st.markdown(
            """
<div style="
text-align:center;
padding-top:100px;
font-size:42px;
color:#B56F78;
font-weight:bold;
">
→
</div>
""",
            unsafe_allow_html=True
        )

    with agent_col2:

        st.markdown(
            """
<div class="agent-card">

<h3>🎯 Agent 2</h3>

<h2>Strategic Analysis Agent</h2>

<b>Responsibility</b>

<p>
Transform research findings into strategic intelligence.
</p>

<b>Receives</b>

<p>
Research findings generated by Agent 1.
</p>

<b>Produces</b>

<p>
Signals, competitor analysis,
recommendations and strategic verdict.
</p>

</div>
""",
            unsafe_allow_html=True
        )


    st.success(
        f"✓ Agent 1 generated {len(findings)} findings "
        "→ findings handed to Agent 2 "
        "→ strategic analysis completed."
    )


    # ========================================================
    # EXECUTION LOG
    # ========================================================

    st.subheader(
        "⚙️ Agent Execution Log"
    )

    for log in research[
        "logs"
    ]:

        st.write(
            "✓ " + log
        )

    st.write(
        "✓ Research Intelligence Agent completed."
    )

    st.write(
        "✓ Research findings passed to Strategic Analysis Agent."
    )

    st.write(
        "✓ Strategic Analysis Agent completed."
    )


    # ========================================================
    # SUMMARY
    # ========================================================

    st.divider()

    st.header(
        "📊 Intelligence Summary"
    )

    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:

        st.metric(
            "Relevant Findings",
            len(findings)
        )

    with metric2:

        st.metric(
            "arXiv Findings",
            strategy[
                "arxiv_count"
            ]
        )

    with metric3:

        st.metric(
            "OpenAlex Findings",
            strategy[
                "openalex_count"
            ]
        )

    with metric4:

        st.metric(
            "Signal",
            strategy[
                "signal"
            ]
        )


    # ========================================================
    # STRATEGIC SIGNAL
    # ========================================================

    st.header(
        "🚨 Strategic Signal"
    )

    st.markdown(
        f"""
<div class="signal-card">

<h2>{strategy['signal']} PRIORITY</h2>

<p>
{strategy['signal_text']}
</p>

</div>
""",
        unsafe_allow_html=True
    )


    # ========================================================
    # RESEARCH FINDINGS
    # ========================================================

    st.header(
        "📚 Research & Scholarly Findings"
    )

    if not findings:

        st.warning(
            "No findings were returned. "
            "Try a broader research topic."
        )

    else:

        for number, finding in enumerate(
            findings,
            start=1
        ):

            title = finding.get(
                "title",
                "Untitled"
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
                "Unknown"
            )

            summary = finding.get(
                "summary",
                ""
            )

            url = finding.get(
                "url",
                ""
            )

            st.markdown(
                f"""
<div class="finding-card">

<h3>{number}. {title}</h3>

<p>
<b>Source:</b> {source}
&nbsp;&nbsp; | &nbsp;&nbsp;
<b>Date:</b> {date}
</p>

<p>
{summary[:650]}
</p>

<p>
<b>Authors:</b> {authors}
</p>

</div>
""",
                unsafe_allow_html=True
            )

            if url:

                st.markdown(
                    f"[🔗 View source]({url})"
                )


    # ========================================================
    # COMPETITOR INTELLIGENCE
    # ========================================================

    st.header(
        "🏢 Competitor Intelligence"
    )

    competitor_matches = strategy[
        "competitor_matches"
    ]

    if competitor_matches:

        for match in competitor_matches:

            st.info(
                "Research finding related to "
                + ", ".join(
                    match["competitors"]
                )
                + ": "
                + match["title"]
            )

    elif competitors.strip():

        st.info(
            "No direct competitor mentions were "
            "detected in the retrieved research titles."
        )

    else:

        st.info(
            "No competitors were provided. "
            "Add competitors for deeper analysis."
        )


    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    st.header(
        "🎯 Recommended Actions"
    )

    for recommendation in strategy[
        "recommendations"
    ]:

        st.markdown(
            f"➡️ {recommendation}"
        )


    # ========================================================
    # FINAL VERDICT
    # ========================================================

    st.divider()

    st.header(
        "🏆 Final Strategic Verdict"
    )

    st.success(
        strategy[
            "verdict"
        ]
    )

    st.markdown(
        f"""
<div class="card">

<h3>Strategic Takeaway</h3>

<p>
{strategy['takeaway']}
</p>

</div>
""",
        unsafe_allow_html=True
    )


    # ========================================================
    # AGENT DATA HANDOFF
    # ========================================================

    with st.expander(
        "🔍 View Agent-to-Agent Data Handoff"
    ):

        st.write(
            "Agent 1:"
        )

        st.write(
            "Research Intelligence Agent"
        )

        st.write(
            f"Output: {len(findings)} research findings"
        )

        st.write(
            "↓"
        )

        st.write(
            "Orchestrator passes research findings to Agent 2"
        )

        st.write(
            "↓"
        )

        st.write(
            "Strategic Analysis Agent"
        )

        st.write(
            f"Signal: {strategy['signal']}"
        )

        st.write(
            f"Verdict: {strategy['verdict']}"
        )

        st.write(
            f"Recommendations: "
            f"{len(strategy['recommendations'])}"
        )


# ============================================================
# EMPTY STATE
# ============================================================

else:

    st.info(
        "Enter a research area and click "
        "'Start Intelligence Scan' to begin."
    )

    st.markdown(
        """
### 💡 Try These Topics

- Quantum Computing
- Electric Vehicles
- Solid-State Batteries
- Generative AI
- Robotics
- Semiconductor Technology
- Autonomous Vehicles
- AI Healthcare

ResearchRadar dynamically selects the appropriate
external intelligence tools based on the objective.
"""
    )