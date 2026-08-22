import streamlit as st
import requests
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ResearchRadar",
    page_icon="🔎",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

/* ---------- MAIN BACKGROUND ---------- */

.stApp {
    background: #F8F1EA;
    color: #3D3030;
}

.main {
    background: #F8F1EA;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}


/* ---------- HERO ---------- */

.hero {
    padding: 38px;
    border-radius: 24px;
    background: linear-gradient(
        135deg,
        #FFF8F3 0%,
        #F8E3E3 55%,
        #F3D6D8 100%
    );
    border: 1px solid #E8CACA;
    margin-bottom: 28px;
    box-shadow: 0 8px 30px rgba(105, 75, 75, 0.08);
}

.hero-title {
    font-size: 44px;
    font-weight: 800;
    color: #4A3535;
    margin-bottom: 8px;
}

.hero-subtitle {
    font-size: 19px;
    font-weight: 600;
    color: #9A6666;
    margin-bottom: 12px;
}

.hero p {
    color: #665454;
    font-size: 16px;
}


/* ---------- AGENT CARDS ---------- */

.agent-card {
    padding: 22px;
    border-radius: 18px;
    background: #FFFFFF;
    border: 1px solid #EADADA;
    margin-bottom: 15px;
    box-shadow: 0 6px 20px rgba(105, 75, 75, 0.07);
}

.agent-card h3 {
    color: #B56F78;
}

.agent-card h2 {
    color: #4A3535;
}


/* ---------- SIGNAL CARD ---------- */

.signal-card {
    padding: 20px;
    border-radius: 16px;
    background: #FFF5F5;
    border: 1px solid #E9C5C9;
    border-left: 5px solid #C97B84;
    margin-bottom: 15px;
}

.signal-card h3 {
    color: #A65D68;
}


/* ---------- FINDING CARDS ---------- */

.finding-card {
    padding: 20px;
    border-radius: 16px;
    background: #FFFFFF;
    border: 1px solid #E9DCDC;
    margin-bottom: 14px;
    box-shadow: 0 5px 18px rgba(105, 75, 75, 0.06);
}

.finding-card h3 {
    color: #594343;
}


/* ---------- TOOL CARDS ---------- */

.tool-card {
    padding: 18px;
    border-radius: 16px;
    background: #FFFDFC;
    border: 1px solid #E8D5D5;
    box-shadow: 0 5px 18px rgba(105, 75, 75, 0.06);
}

.tool-card h3 {
    color: #B56F78;
}


/* ---------- TEXT ---------- */

.small {
    color: #947878;
    font-size: 14px;
}


/* ---------- INPUTS ---------- */

.stTextInput > div > div > input,
.stTextArea textarea {
    background-color: #FFFFFF !important;
    color: #4A3535 !important;
    border: 1px solid #DFCACA !important;
    border-radius: 12px !important;
}

.stTextInput label,
.stTextArea label {
    color: #594343 !important;
    font-weight: 600 !important;
}


/* ---------- BUTTON ---------- */

.stButton > button {
    background: linear-gradient(
        135deg,
        #C9828A,
        #B96D77
    ) !important;

    color: white !important;

    border: none !important;

    border-radius: 12px !important;

    padding: 12px 24px !important;

    font-weight: 700 !important;

    box-shadow: 0 6px 16px rgba(185, 109, 119, 0.22);

    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: #A95F69 !important;
    transform: translateY(-1px);
}


/* ---------- METRICS ---------- */

[data-testid="stMetric"] {
    background: #FFFFFF;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #E8DADA;
    box-shadow: 0 5px 18px rgba(105, 75, 75, 0.05);
}

[data-testid="stMetricLabel"] {
    color: #967878 !important;
}

[data-testid="stMetricValue"] {
    color: #4A3535 !important;
}


/* ---------- SIDEBAR ---------- */

section[data-testid="stSidebar"] {
    background: #FFF8F3;
    border-right: 1px solid #E9D9D9;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #594343;
}

section[data-testid="stSidebar"] p {
    color: #766060;
}


/* ---------- HEADINGS ---------- */

h1, h2, h3 {
    color: #4A3535;
}

h1 {
    font-weight: 800;
}

h2 {
    font-weight: 750;
}


/* ---------- DIVIDERS ---------- */

hr {
    border-color: #E7D5D5 !important;
}


/* ---------- SUCCESS / INFO BOXES ---------- */

div[data-testid="stAlert"] {
    border-radius: 14px;
}


/* ---------- LINKS ---------- */

a {
    color: #B56F78 !important;
    font-weight: 600;
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
Autonomous Research & Competitor Intelligence Agent
</div>

<p>
Define a technology or research area and let ResearchRadar
discover relevant intelligence, detect strategic signals,
and generate actionable recommendations.
</p>

</div>
""", unsafe_allow_html=True)


# ============================================================
# TOOL DEFINITIONS
# ============================================================

TOOLS = {

    "arxiv": {
        "name": "arXiv API",
        "description":
            "Searches recent scientific and technical research papers.",
        "purpose":
            "Emerging research and scientific breakthroughs"
    },

    "openalex": {
        "name": "OpenAlex API",
        "description":
            "Searches scholarly works, authors and research activity.",
        "purpose":
            "Academic research trends and scholarly intelligence"
    }
}


# ============================================================
# TASK 2
# DYNAMIC TOOL SELECTOR
# ============================================================

def select_tools(topic, objective):

    text = (
        f"{topic} {objective}"
    ).lower()

    research_keywords = [
        "paper",
        "papers",
        "research",
        "scientific",
        "breakthrough",
        "technology",
        "innovation",
        "experiment",
        "algorithm",
        "model",
        "method",
        "machine learning",
        "artificial intelligence",
        "quantum",
        "robotics",
        "battery",
        "semiconductor",
        "computer vision",
        "nlp"
    ]

    scholarly_keywords = [
        "scholarly",
        "authors",
        "universities",
        "institutions",
        "citations",
        "academic",
        "publication",
        "publications",
        "research trend",
        "research landscape"
    ]

    selected = []

    if any(
        keyword in text
        for keyword in research_keywords
    ):
        selected.append("arxiv")

    if any(
        keyword in text
        for keyword in scholarly_keywords
    ):
        selected.append("openalex")

    # If the objective is broad, use both.
    if (
        "comprehensive" in text
        or "intelligence" in text
        or "competitor" in text
        or "monitor" in text
        or len(selected) == 0
    ):
        selected = ["arxiv", "openalex"]

    # Remove duplicates
    return list(dict.fromkeys(selected))


# ============================================================
# ARXIV API
# ============================================================

def search_arxiv(topic, max_results=6):

    try:

        query = urllib.parse.quote(
            f"all:{topic}"
        )

        url = (
            "https://export.arxiv.org/api/query"
            f"?search_query={query}"
            f"&start=0"
            f"&max_results={max_results}"
            "&sortBy=submittedDate"
            "&sortOrder=descending"
        )

        response = requests.get(
            url,
            timeout=20,
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

            link = ""

            for item in entry.findall(
                "atom:link",
                namespace
            ):

                if item.attrib.get(
                    "type"
                ) == "text/html":

                    link = item.attrib.get(
                        "href",
                        ""
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

            results.append({

                "title": title,

                "summary": summary,

                "source": "arXiv",

                "date":
                    published[:10]
                    if published
                    else "Unknown",

                "authors":
                    ", ".join(
                        authors[:3]
                    ),

                "url": link

            })

        return results

    except Exception as error:

        return [{
            "error":
                f"arXiv API error: {error}"
        }]


# ============================================================
# OPENALEX API
# ============================================================

def search_openalex(topic, max_results=6):

    try:

        encoded = urllib.parse.quote(
            topic
        )

        url = (
            "https://api.openalex.org/works"
            f"?search={encoded}"
            f"&per-page={max_results}"
            "&sort=publication_date:desc"
        )

        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent":
                "ResearchRadar/1.0"
            }
        )

        response.raise_for_status()

        data = response.json()

        results = []

        for item in data.get(
            "results",
            []
        ):

            title = item.get(
                "title",
                "Untitled research"
            )

            publication_date = item.get(
                "publication_date",
                "Unknown"
            )

            authors = []

            for authorship in item.get(
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

            doi = item.get(
                "doi",
                ""
            )

            results.append({

                "title": title,

                "summary":
                    "Scholarly work identified "
                    "through OpenAlex.",

                "source": "OpenAlex",

                "date":
                    publication_date,

                "authors":
                    ", ".join(authors),

                "url":
                    doi
                    if doi
                    else
                    item.get(
                        "id",
                        ""
                    )

            })

        return results

    except Exception as error:

        return [{
            "error":
                f"OpenAlex API error: {error}"
        }]


# ============================================================
# RESEARCH INTELLIGENCE AGENT
# TASK 3 - AGENT 1
# ============================================================

class ResearchIntelligenceAgent:

    def __init__(self):

        self.name = (
            "Research Intelligence Agent"
        )

        self.role = (
            "Discover and structure "
            "research intelligence."
        )

    def investigate(
        self,
        topic,
        objective,
        selected_tools
    ):

        all_findings = []

        tool_log = []

        # ----------------------------------------------------
        # ARXIV
        # ----------------------------------------------------

        if "arxiv" in selected_tools:

            tool_log.append(
                "Calling arXiv API..."
            )

            arxiv_results = search_arxiv(
                topic
            )

            valid_results = [
                result
                for result in arxiv_results
                if "error" not in result
            ]

            all_findings.extend(
                valid_results
            )

            if valid_results:

                tool_log.append(
                    f"arXiv returned "
                    f"{len(valid_results)} findings."
                )

            else:

                tool_log.append(
                    "arXiv returned no findings."
                )

        # ----------------------------------------------------
        # OPENALEX
        # ----------------------------------------------------

        if "openalex" in selected_tools:

            tool_log.append(
                "Calling OpenAlex API..."
            )

            openalex_results = (
                search_openalex(topic)
            )

            valid_results = [
                result
                for result in openalex_results
                if "error" not in result
            ]

            all_findings.extend(
                valid_results
            )

            if valid_results:

                tool_log.append(
                    f"OpenAlex returned "
                    f"{len(valid_results)} findings."
                )

            else:

                tool_log.append(
                    "OpenAlex returned no findings."
                )

        # ----------------------------------------------------
        # REMOVE DUPLICATES
        # ----------------------------------------------------

        unique = []

        seen = set()

        for item in all_findings:

            title = item.get(
                "title",
                ""
            ).strip().lower()

            if not title:
                continue

            if title in seen:
                continue

            seen.add(title)

            unique.append(item)

        return {

            "agent":
                self.name,

            "findings":
                unique,

            "tool_log":
                tool_log,

            "tools_used":
                selected_tools

        }


# ============================================================
# STRATEGIC ANALYSIS AGENT
# TASK 3 - AGENT 2
# ============================================================

class StrategicAnalysisAgent:

    def __init__(self):

        self.name = (
            "Strategic Analysis Agent"
        )

        self.role = (
            "Transform research findings "
            "into competitive intelligence."
        )

    def analyze(
        self,
        topic,
        competitors,
        findings
    ):

        competitor_list = [
            item.strip()
            for item in competitors.split(",")
            if item.strip()
        ]

        total_findings = len(
            findings
        )

        arxiv_count = len([
            item
            for item in findings
            if item.get("source")
            == "arXiv"
        ])

        openalex_count = len([
            item
            for item in findings
            if item.get("source")
            == "OpenAlex"
        ])

        # ----------------------------------------------------
        # SIGNAL LEVEL
        # ----------------------------------------------------

        if total_findings >= 8:

            signal_level = (
                "HIGH"
            )

            signal_text = (
                "Strong research activity "
                "was detected in this domain."
            )

        elif total_findings >= 4:

            signal_level = (
                "MEDIUM"
            )

            signal_text = (
                "Moderate research activity "
                "was detected."
            )

        else:

            signal_level = (
                "LOW"
            )

            signal_text = (
                "Limited research activity "
                "was detected."
            )

        # ----------------------------------------------------
        # COMPETITOR ANALYSIS
        # ----------------------------------------------------

        competitor_findings = []

        for finding in findings:

            title = finding.get(
                "title",
                ""
            ).lower()

            matched = []

            for competitor in competitor_list:

                if competitor.lower() in title:

                    matched.append(
                        competitor
                    )

            if matched:

                competitor_findings.append({

                    "title":
                        finding.get(
                            "title"
                        ),

                    "competitors":
                        matched,

                    "source":
                        finding.get(
                            "source"
                        )

                })

        # ----------------------------------------------------
        # RECOMMENDATIONS
        # ----------------------------------------------------

        recommendations = []

        if total_findings > 0:

            recommendations.append(
                "Monitor the latest research "
                "developments in this technology area."
            )

            recommendations.append(
                "Evaluate whether emerging research "
                "can create a competitive advantage."
            )

        if arxiv_count > 0:

            recommendations.append(
                "Review recent arXiv research for "
                "early-stage technology signals."
            )

        if openalex_count > 0:

            recommendations.append(
                "Track scholarly activity and research "
                "institutions through OpenAlex."
            )

        if competitor_list:

            recommendations.append(
                "Compare future competitor activity "
                "against the identified research trends."
            )

        # ----------------------------------------------------
        # STRATEGIC TAKEAWAY
        # ----------------------------------------------------

        takeaway = (
            f"ResearchRadar detected "
            f"{total_findings} relevant research findings "
            f"for '{topic}'. "
            f"The current intelligence signal is "
            f"{signal_level}. "
            f"Organizations should monitor this domain "
            f"and evaluate emerging developments "
            f"before competitors gain an advantage."
        )

        return {

            "agent":
                self.name,

            "signal_level":
                signal_level,

            "signal_text":
                signal_text,

            "arxiv_count":
                arxiv_count,

            "openalex_count":
                openalex_count,

            "competitor_findings":
                competitor_findings,

            "recommendations":
                recommendations,

            "takeaway":
                takeaway,

            "verdict":
                (
                    "HIGH PRIORITY"
                    if signal_level == "HIGH"
                    else
                    "WATCH CLOSELY"
                    if signal_level == "MEDIUM"
                    else
                    "LOW IMMEDIATE RISK"
                )

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

        # ----------------------------------------------------
        # STEP 1
        # DYNAMIC TOOL SELECTION
        # ----------------------------------------------------

        selected_tools = select_tools(
            topic,
            objective
        )

        # ----------------------------------------------------
        # STEP 2
        # RESEARCH AGENT
        # ----------------------------------------------------

        research_output = (
            self.research_agent.investigate(
                topic,
                objective,
                selected_tools
            )
        )

        findings = research_output[
            "findings"
        ]

        # ----------------------------------------------------
        # STEP 3
        # STRATEGY AGENT
        # Receives Agent 1's output
        # ----------------------------------------------------

        strategy_output = (
            self.strategy_agent.analyze(
                topic,
                competitors,
                findings
            )
        )

        # ----------------------------------------------------
        # STEP 4
        # COMBINED OUTPUT
        # ----------------------------------------------------

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

    st.header(
        "🤖 Agent Architecture"
    )

    st.markdown(
        """
### Agent 1
**Research Intelligence Agent**

Discovers and structures research intelligence using dynamically selected external tools.

### Agent 2
**Strategic Analysis Agent**

Analyzes the findings produced by Agent 1 and generates competitive signals and recommendations.

### Orchestrator

Coordinates the two agents and passes research findings from Agent 1 to Agent 2.
"""
    )

    st.divider()

    st.caption(
        "ResearchRadar • Team TriX • SY-CSE"
    )


# ============================================================
# USER INPUT
# ============================================================

st.subheader(
    "🎯 Define Your Intelligence Objective"
)

col1, col2 = st.columns(2)

with col1:

    topic = st.text_input(
        "Research / Technology Area",
        placeholder=
        "e.g. solid state batteries"
    )

with col2:

    competitors = st.text_input(
        "Competitors",
        placeholder=
        "e.g. Tesla, Toyota, BYD"
    )

objective = st.text_area(
    "Monitoring Objective",
    placeholder=
    "What do you want ResearchRadar to investigate?",
    value=
    "Conduct comprehensive research intelligence "
    "and identify important emerging developments."
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

    # --------------------------------------------------------
    # ORCHESTRATOR
    # --------------------------------------------------------

    orchestrator = (
        ResearchRadarOrchestrator()
    )

    with st.spinner(
        "ResearchRadar agents are investigating..."
    ):

        output = orchestrator.run(
            topic,
            objective,
            competitors
        )

    # ========================================================
    # TOOL CALLING DISPLAY
    # TASK 2
    # ========================================================

    st.divider()

    st.header(
        "🛠️ Dynamic Tool Selection"
    )

    selected_tools = output[
        "selected_tools"
    ]

    st.success(
        f"Agent selected "
        f"{len(selected_tools)} relevant tool(s) "
        f"for this objective."
    )

    tool_cols = st.columns(
        len(selected_tools)
    )

    for index, tool in enumerate(
        selected_tools
    ):

        with tool_cols[index]:

            tool_info = TOOLS[
                tool
            ]

            st.markdown(
                f"""
<div class="tool-card">

### {tool_info['name']}

**Purpose:**  
{tool_info['purpose']}

**Status:** 🟢 Called

</div>
""",
                unsafe_allow_html=True
            )

    # ========================================================
    # AGENT COLLABORATION
    # TASK 3
    # ========================================================

    st.divider()

    st.header(
        "🤖 Multi-Agent Collaboration"
    )

    agent1, agent2 = st.columns(2)

    with agent1:

        st.markdown(
            """
<div class="agent-card">

### 🔬 Agent 1
## Research Intelligence Agent

**Responsibility**

Discover and structure relevant research intelligence.

**Tools**

- arXiv API
- OpenAlex API

**Output**

Research findings passed to Agent 2.

</div>
""",
            unsafe_allow_html=True
        )

    with agent2:

        st.markdown(
            """
<div class="agent-card">

### 🎯 Agent 2
## Strategic Analysis Agent

**Responsibility**

Transform Agent 1's research findings into strategic intelligence.

**Input**

Research findings from Agent 1.

**Output**

Signals, recommendations and strategic verdict.

</div>
""",
            unsafe_allow_html=True
        )

    # ========================================================
    # EXECUTION LOG
    # ========================================================

    st.subheader(
        "⚙️ Agent Execution Log"
    )

    research_log = output[
        "research_agent"
    ][
        "tool_log"
    ]

    for log in research_log:

        st.write(
            "✓ " + log
        )

    st.success(
        "✓ Agent 1 completed → "
        "Findings passed to Agent 2 → "
        "Strategic analysis completed"
    )

    # ========================================================
    # SUMMARY METRICS
    # ========================================================

    strategy = output[
        "strategy_agent"
    ]

    findings = output[
        "research_agent"
    ][
        "findings"
    ]

    st.divider()

    st.header(
        "📊 Intelligence Summary"
    )

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "Relevant Findings",
        len(findings)
    )

    m2.metric(
        "arXiv Findings",
        strategy[
            "arxiv_count"
        ]
    )

    m3.metric(
        "OpenAlex Findings",
        strategy[
            "openalex_count"
        ]
    )

    m4.metric(
        "Signal Level",
        strategy[
            "signal_level"
        ]
    )

    # ========================================================
    # HIGH PRIORITY SIGNAL
    # ========================================================

    st.header(
        "🚨 Strategic Signal"
    )

    st.markdown(
        f"""
<div class="signal-card">

<h3>{strategy['signal_level']} PRIORITY</h3>

<p>{strategy['signal_text']}</p>

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
            "No research findings were returned. "
            "Try a broader technology area."
        )

    else:

        for index, finding in enumerate(
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

<h3>{index}. {title}</h3>

<p class="small">
Source: <b>{source}</b>
&nbsp;&nbsp; | &nbsp;&nbsp;
Date: <b>{date}</b>
</p>

<p>
{summary[:700]}
</p>

<p class="small">
Authors: {authors}
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
    # COMPETITOR ANALYSIS
    # ========================================================

    st.header(
        "🏢 Competitor Intelligence"
    )

    competitor_findings = strategy[
        "competitor_findings"
    ]

    if competitor_findings:

        for item in competitor_findings:

            st.info(
                f"Research finding related to "
                f"{', '.join(item['competitors'])}: "
                f"{item['title']}"
            )

    elif competitors.strip():

        st.info(
            "No direct competitor mentions "
            "were detected in the retrieved "
            "research titles."
        )

    else:

        st.info(
            "No competitors were provided. "
            "Add competitors for deeper "
            "competitive analysis."
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
        "🎯 Final Strategic Verdict"
    )

    st.success(
        strategy[
            "verdict"
        ]
    )

    st.markdown(
        f"""
### Strategic Takeaway

{strategy['takeaway']}
"""
    )

    # ========================================================
    # DEMONSTRATION OF COLLABORATION
    # ========================================================

    with st.expander(
        "🔍 View Agent-to-Agent Data Flow"
    ):

        st.json({

            "Agent_1":
                "Research Intelligence Agent",

            "Agent_1_Output":
                f"{len(findings)} research findings",

            "Handoff":
                "Research findings passed to Agent 2",

            "Agent_2":
                "Strategic Analysis Agent",

            "Agent_2_Output": {

                "signal":
                    strategy[
                        "signal_level"
                    ],

                "verdict":
                    strategy[
                        "verdict"
                    ],

                "recommendations":
                    strategy[
                        "recommendations"
                    ]

            }

        })

else:

    # ========================================================
    # EMPTY STATE
    # ========================================================

    st.info(
        "Enter a research area and click "
        "'Start Intelligence Scan' to begin."
    )

    st.markdown(
        """
### 💡 Example Objectives

Try:

- **Quantum Computing**
- **Solid-State Batteries**
- **Generative AI**
- **Autonomous Vehicles**
- **Robotics**
- **Semiconductor Technology**
- **AI Healthcare**

ResearchRadar will dynamically determine which intelligence tools are relevant to the objective.
"""
    )