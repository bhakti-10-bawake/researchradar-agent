import streamlit as st
import json
import os
import textwrap
from datetime import datetime

from intelligence_tools import run_intelligence_tools


MEMORY_FILE = "memory_store.json"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ResearchRadar",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# HELPERS
# ============================================================

def html(content):
    """Render HTML safely without accidental Markdown code blocks."""
    st.markdown(
        textwrap.dedent(str(content)).strip(),
        unsafe_allow_html=True,
    )


def clean(value, default=""):
    if value is None:
        return default
    return str(value)


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (OSError, json.JSONDecodeError):
        return []


def save_memory(entry):
    history = load_memory()
    history.append(entry)

    try:
        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                history[-100:],
                file,
                indent=2,
                ensure_ascii=False,
            )

    except OSError:
        pass


def recall_memory(topic):
    topic = clean(topic).strip().lower()

    if not topic:
        return []

    matches = []

    for item in load_memory():

        old_topic = clean(
            item.get("topic")
        ).strip().lower()

        if old_topic == topic:

            matches.append(item)

        elif (
            topic in old_topic
            or old_topic in topic
        ):

            matches.append(item)

    return matches


def normalize_results(result):
    """
    Accept the current intelligence_tools.py output without
    requiring app.py to know about its internal helper functions.
    """

    if not isinstance(result, dict):

        return {
            "findings": [],
            "tools": [],
            "tool_status": [],
            "query": "",
        }

    findings = result.get(
        "findings",
        []
    )

    if not isinstance(
        findings,
        list
    ):

        findings = []

    tools = result.get(
        "selected_tools",
        result.get(
            "tools",
            []
        )
    )

    if not isinstance(
        tools,
        list
    ):

        tools = []

    tool_status = result.get(
        "tool_status",
        []
    )

    if not isinstance(
        tool_status,
        list
    ):

        tool_status = []

    query = result.get(
        "research_query",
        result.get(
            "query",
            ""
        )
    )

    return {
        "findings": findings,
        "tools": tools,
        "tool_status": tool_status,
        "query": query,
    }


def relevance_score(finding):

    try:

        return float(
            finding.get(
                "relevance_score",
                finding.get(
                    "relevance",
                    0
                ),
            )
        )

    except (
        TypeError,
        ValueError
    ):

        return 0.0


# ============================================================
# STRATEGIC ANALYSIS
# ============================================================

def strategic_analysis(
    findings,
    topic,
    objective,
    competitors,
    previous
):

    relevant = sorted(
        findings,
        key=relevance_score,
        reverse=True,
    )

    high = [

        item

        for item in relevant

        if (
            relevance_score(item) >= 15
            or
            clean(
                item.get(
                    "importance"
                )
            ).lower() == "high"
        )

    ][:5]

    sources = {}

    for item in findings:

        source = clean(
            item.get(
                "source"
            ),
            "Unknown"
        )

        sources[source] = (
            sources.get(
                source,
                0
            ) + 1
        )

    if not findings:

        signal = "INSUFFICIENT"

        verdict = (
            "The selected intelligence sources "
            "did not return enough evidence to "
            "produce a reliable strategic conclusion."
        )

    elif len(high) >= 4:

        signal = "HIGH"

        verdict = (
            "Multiple relevant signals were detected. "
            "The topic shows strong research or market "
            "activity and deserves closer strategic attention."
        )

    elif (
        len(high) >= 2
        or
        len(findings) >= 5
    ):

        signal = "MEDIUM"

        verdict = (
            "Relevant activity was detected across "
            "the retrieved sources. Further monitoring "
            "can reveal stronger trends."
        )

    else:

        signal = "LOW"

        verdict = (
            "Some relevant activity was detected, "
            "but the current evidence base is limited."
        )

    if high:

        strongest = clean(
            high[0].get(
                "title"
            ),
            "the highest-relevance finding"
        )

        recommendation = (
            f"Prioritize investigation of "
            f"'{strongest}' and compare it with "
            "the user's stated objective before "
            "making a strategic decision."
        )

    else:

        recommendation = (
            "Continue monitoring the topic and "
            "broaden the objective if additional "
            "evidence is required."
        )

    if not previous:

        memory_text = (
            "No previous scan for this topic was found."
        )

    else:

        memory_text = (
            f"{len(previous)} previous scan(s) were "
            "recalled for this topic and made available "
            "to the current analysis."
        )

    return {

        "signal":
            signal,

        "verdict":
            verdict,

        "recommendation":
            recommendation,

        "high_priority":
            high,

        "source_counts":
            sources,

        "memory_context":
            memory_text,

        "total":
            len(findings),

    }


# ============================================================
# CSS
# ============================================================

html("""
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

h1,
h2,
h3,
h4 {
    color: #4A3535 !important;
}

p {
    color: #6F5C5C;
    line-height: 1.6;
}

section[data-testid="stSidebar"] {
    background: #FFF8F3;
    border-right: 1px solid #E8DADA;
}


/* ==========================================================
   BRAND
   ========================================================== */

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


/* ==========================================================
   SIDEBAR
   ========================================================== */

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

.sidebar-memory {
    font-size: 11px;
    color: #806D6D;
    padding: 7px 0;
    border-bottom: 1px dashed #E8DADA;
}


/* ==========================================================
   HERO
   ========================================================== */

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
}

.hero-small {
    font-size: 10px;
    font-weight: 900;
    letter-spacing: 1.7px;
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
    max-width: 850px;
    margin-top: 15px;
    font-size: 14px;
    color: #6F5C5C;
}


/* ==========================================================
   CARDS
   ========================================================== */

.card,
.workflow,
.agent,
.finding,
.memory-box,
.signal-box,
.source-card {
    background: #FFFFFF;
    border: 1px solid #E8DADA;
    border-radius: 17px;
    padding: 20px;
    box-shadow:
        0 5px 18px rgba(
            100,
            70,
            70,
            0.05
        );
}

.card {
    min-height: 125px;
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

.card-caption,
.workflow-text,
.agent-description {
    font-size: 11px;
    color: #9A8181;
    margin-top: 5px;
}


/* ==========================================================
   WORKFLOW
   ========================================================== */

.workflow {
    min-height: 120px;
    text-align: center;
}

.workflow-number {
    width: 32px;
    height: 32px;
    margin: 0 auto 9px;
    border-radius: 50%;
    background: #F3D6D8;
    color: #A65D68;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
}

.workflow-title,
.agent-name {
    font-size: 14px;
    font-weight: 850;
    color: #594343;
}


/* ==========================================================
   INPUTS
   ========================================================== */

.stTextInput input,
.stTextArea textarea {
    background: #FFFFFF !important;
    color: #4A3535 !important;
    border: 1px solid #DDC8C8 !important;
    border-radius: 13px !important;
}


/* ==========================================================
   BUTTON
   ========================================================== */

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


/* ==========================================================
   FINDINGS
   ========================================================== */

.finding {
    margin-bottom: 14px;
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


/* ==========================================================
   SIGNAL
   ========================================================== */

.signal-box {
    background: #FFF3F4;
    border-left: 6px solid #C47A84;
}

.signal-level {
    font-size: 25px;
    font-weight: 900;
    color: #A65D68;
}


/* ==========================================================
   MEMORY
   ========================================================== */

.memory-box {
    background: #FDF3EC;
    border-left: 6px solid #C6935E;
}


/* ==========================================================
   TOOLS
   ========================================================== */

.tool-chip {
    display: inline-block;
    padding: 6px 11px;
    margin: 3px 5px 3px 0;
    background: #F7E6E7;
    border: 1px solid #E8C9CC;
    border-radius: 18px;
    color: #8F5962;
    font-size: 11px;
    font-weight: 800;
}


/* ==========================================================
   QUERY
   ========================================================== */

.query-box {
    background: #FFFFFF;
    border: 1px solid #E8DADA;
    border-radius: 15px;
    padding: 15px 18px;
    margin-top: 12px;
}

.query-label {
    font-size: 10px;
    font-weight: 900;
    letter-spacing: 1.3px;
    color: #A2676E;
}

.query-text {
    font-size: 13px;
    color: #594343;
    margin-top: 5px;
}


/* ==========================================================
   SOURCES
   ========================================================== */

.source-card {
    min-height: 90px;
}

.source-name {
    font-size: 12px;
    font-weight: 850;
    color: #594343;
}

.source-count {
    font-size: 25px;
    font-weight: 900;
    color: #A65D68;
}


/* ==========================================================
   FOOTER
   ========================================================== */

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
# SESSION MEMORY
# ============================================================

if "session_history" not in st.session_state:

    st.session_state.session_history = []


if "last_result" not in st.session_state:

    st.session_state.last_result = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    html("""
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

    html("""
    <div class="sidebar-heading">
        Multi-Agent Architecture
    </div>

    <div class="sidebar-agent">
        Agent 1 — Research Intelligence
    </div>

    <div class="sidebar-text">
        Discovers research and intelligence
        using external APIs.
    </div>

    <div class="sidebar-agent">
        Agent 2 — Strategic Analysis
    </div>

    <div class="sidebar-text">
        Converts Research Agent findings
        into strategic insights.
    </div>

    <div class="sidebar-agent">
        Agent 3 — Memory
    </div>

    <div class="sidebar-text">
        Recalls prior scans and persists
        new context.
    </div>

    <div class="sidebar-agent">
        Orchestrator
    </div>

    <div class="sidebar-text">
        Coordinates tool selection and
        agent handoffs.
    </div>
    """)

    st.divider()

    html("""
    <div class="sidebar-agent">
        🧠 Long-Term Memory
    </div>

    <div class="sidebar-text">
        Past scans, persisted on disk
        across sessions.
    </div>
    """)

    memory = load_memory()

    if memory:

        for item in reversed(
            memory[-6:]
        ):

            html(f"""
            <div class="sidebar-memory">

                <strong>
                    {clean(
                        item.get(
                            "topic"
                        ),
                        "Unknown"
                    )}
                </strong>

                <br>

                {clean(
                    item.get(
                        "signal"
                    ),
                    "UNKNOWN"
                )}

                SIGNAL

                • {clean(
                    item.get(
                        "timestamp"
                    ),
                    ""
                )}

            </div>
            """)

    else:

        st.caption(
            "No previous scans recorded."
        )

    st.success(
        "System Online"
    )


# ============================================================
# HERO
# ============================================================

html("""
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
        system that gathers relevant research
        and information, analyzes evidence,
        remembers previous scans, and produces
        actionable insights.
    </div>

</div>
""")


# ============================================================
# INTELLIGENCE WORKSPACE
# ============================================================

html("""
<div class="section-label">
    INTELLIGENCE WORKSPACE
</div>
""")

c1, c2, c3, c4 = st.columns(4)


with c1:

    html("""
    <div class="card">

        <div class="card-title">
            🔬 Research Agent
        </div>

        <div class="card-value">
            Ready
        </div>

        <div class="card-caption">
            Research discovery
        </div>

    </div>
    """)


with c2:

    html("""
    <div class="card">

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


with c3:

    html("""
    <div class="card">

        <div class="card-title">
            🛠️ Intelligence Tools
        </div>

        <div class="card-value">
            APIs
        </div>

        <div class="card-caption">
            External intelligence sources
        </div>

    </div>
    """)


with c4:

    html("""
    <div class="card">

        <div class="card-title">
            ⚡ System Status
        </div>

        <div class="card-value">
            LIVE
        </div>

        <div class="card-caption">
            Pipeline online
        </div>

    </div>
    """)


st.markdown(
    "<br>",
    unsafe_allow_html=True
)


# ============================================================
# WORKFLOW
# ============================================================

html("""
<div class="section-label">
    AUTONOMOUS AGENT WORKFLOW
</div>
""")

w1, w2, w3, w4 = st.columns(4)

steps = [

    (
        "01",
        "Define",
        "Research objective"
    ),

    (
        "02",
        "Discover",
        "External intelligence tools"
    ),

    (
        "03",
        "Analyze",
        "Evidence and strategic signals"
    ),

    (
        "04",
        "Decide",
        "Actionable insights"
    ),

]


for column, (
    number,
    title,
    description
) in zip(
    [w1, w2, w3, w4],
    steps
):

    with column:

        html(f"""
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


st.markdown(
    "<br>",
    unsafe_allow_html=True
)


# ============================================================
# INTELLIGENCE SCAN INPUT
# ============================================================

html("""
<div class="section-label">
    INTELLIGENCE SCAN
</div>
""")

st.header(
    "🎯 Define Your Intelligence Objective"
)

st.write(
    "Enter a research or technology area and "
    "explain what you want to discover. "
    "ResearchRadar passes the topic and objective "
    "to the intelligence tools so the search is "
    "focused on your actual goal."
)


left, right = st.columns(2)


with left:

    topic = st.text_input(
        "Research / Technology Area",
        placeholder=(
            "e.g. AI Smart Study"
        ),
    )


with right:

    competitors = st.text_input(
        "Competitors",
        placeholder=(
            "e.g. Google, Microsoft, OpenAI"
        ),
    )


objective = st.text_area(
    "Intelligence Objective",
    placeholder=(
        "e.g. Develop a personalized AI "
        "study assistant that recommends "
        "study plans based on student "
        "performance, learning needs, "
        "and study behavior."
    ),
    height=120,
)


scan = st.button(
    "🚀 Start Intelligence Scan",
    type="primary",
    use_container_width=True,
)


# ============================================================
# SCAN EXECUTION
# ============================================================

if scan:

    topic = topic.strip()

    objective = objective.strip()

    competitors = competitors.strip()


    if not topic:

        st.error(
            "Please enter a Research / "
            "Technology Area."
        )

        st.stop()


    if not objective:

        objective = (
            "Identify relevant research, "
            "emerging developments, competitor "
            "activity, opportunities, and risks."
        )


    previous = recall_memory(
        topic
    )


    with st.status(
        "🧠 ResearchRadar agents working...",
        expanded=True
    ):

        st.write(
            "🧭 **Orchestrator:** "
            "understanding objective..."
        )

        st.write(
            "🧠 **Memory Agent:** "
            f"recalled {len(previous)} "
            "previous scan(s)."
        )

        st.write(
            "🔬 **Research Agent:** "
            "calling selected external "
            "intelligence tools..."
        )


        try:

            raw_result = (
                run_intelligence_tools(
                    topic,
                    objective,
                    competitors,
                )
            )


        except TypeError:

            # Compatibility fallback if the
            # installed intelligence_tools.py
            # still uses the older signature.

            raw_result = (
                run_intelligence_tools(
                    topic,
                    competitors,
                )
            )


        except Exception as error:

            st.error(
                "Intelligence tools failed: "
                f"{error}"
            )

            st.stop()


        result = normalize_results(
            raw_result
        )


        findings = result[
            "findings"
        ]


        st.write(
            "📚 **Research Agent:** "
            f"{len(findings)} finding(s) "
            "collected."
        )


        st.write(
            "🎯 **Strategy Agent:** "
            "analyzing Research Agent evidence..."
        )


        strategy = strategic_analysis(
            findings,
            topic,
            objective,
            competitors,
            previous,
        )


        st.write(
            "🤝 **Agent handoff:** "
            "Research Agent → Memory Agent → "
            "Strategy Agent"
        )


        st.write(
            "✅ **Intelligence scan complete.**"
        )


    # ========================================================
    # MEMORY SAVE
    # ========================================================

    memory_entry = {

        "topic":
            topic,

        "objective":
            objective,

        "competitors":
            competitors,

        "signal":
            strategy[
                "signal"
            ],

        "total_findings":
            len(findings),

        "selected_tools":
            result[
                "tools"
            ],

        "timestamp":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            ),

    }


    save_memory(
        memory_entry
    )


    st.session_state.session_history.append(
        memory_entry
    )


    st.session_state.last_result = {

        "result":
            result,

        "strategy":
            strategy,

        "topic":
            topic,

        "objective":
            objective,

        "competitors":
            competitors,

        "previous":
            previous,

    }


# ============================================================
# DISPLAY RESULT
# ============================================================

if st.session_state.last_result:

    data = (
        st.session_state.last_result
    )


    result = data[
        "result"
    ]

    strategy = data[
        "strategy"
    ]

    topic = data[
        "topic"
    ]

    objective = data[
        "objective"
    ]

    competitors = data[
        "competitors"
    ]

    previous = data[
        "previous"
    ]

    findings = result[
        "findings"
    ]


    st.divider()


    # ========================================================
    # SUMMARY
    # ========================================================

    html("""
    <div class="section-label">
        INTELLIGENCE SUMMARY
    </div>
    """)


    m1, m2, m3, m4 = st.columns(4)


    with m1:

        st.metric(
            "Relevant Findings",
            len(findings)
        )


    with m2:

        st.metric(
            "External Tools",
            len(
                result[
                    "tools"
                ]
            )
        )


    with m3:

        st.metric(
            "Previous Scans",
            len(previous)
        )


    with m4:

        st.metric(
            "Signal",
            strategy[
                "signal"
            ]
        )


    # ========================================================
    # TOOLS
    # ========================================================

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )


    html("""
    <div class="section-label">
        TOOLS SELECTED
    </div>
    """)


    chips = "".join(

        f'<span class="tool-chip">'
        f'{clean(tool)}'
        f'</span>'

        for tool in result[
            "tools"
        ]

    )


    if chips:

        html(
            f"<div>{chips}</div>"
        )

    else:

        st.info(
            "No tool information was returned."
        )


    # ========================================================
    # QUERY
    # ========================================================

    if result[
        "query"
    ]:

        html(f"""
        <div class="query-box">

            <div class="query-label">
                RESEARCH QUERY
            </div>

            <div class="query-text">
                {clean(
                    result["query"]
                )}
            </div>

        </div>
        """)


    # ========================================================
    # STRATEGIC ANALYSIS
    # ========================================================

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )


    html("""
    <div class="section-label">
        STRATEGIC ANALYSIS
    </div>
    """)


    html(f"""
    <div class="signal-box">

        <div class="section-label">
            OVERALL SIGNAL
        </div>

        <div class="signal-level">
            {clean(
                strategy["signal"]
            )}
        </div>

        <p>
            {clean(
                strategy["verdict"]
            )}
        </p>

        <p>

            <strong>
                Recommended Action:
            </strong>

            {clean(
                strategy["recommendation"]
            )}

        </p>

    </div>
    """)


    # ========================================================
    # HIGH PRIORITY
    # ========================================================

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )


    html("""
    <div class="section-label">
        HIGH-PRIORITY SIGNALS
    </div>
    """)


    if strategy[
        "high_priority"
    ]:

        for index, finding in enumerate(

            strategy[
                "high_priority"
            ],

            start=1

        ):

            title = clean(

                finding.get(
                    "title"
                ),

                "Untitled research"

            )


            summary = clean(

                finding.get(
                    "summary"
                ),

                "No summary available."

            )


            if len(summary) > 500:

                summary = (
                    summary[:500]
                    + "..."
                )


            html(f"""
            <div class="finding">

                <span class="badge">

                    {clean(
                        finding.get(
                            "source"
                        ),
                        "Research"
                    )}

                </span>

                <div class="finding-title">

                    {index}.
                    {title}

                </div>

                <div class="finding-summary">

                    {summary}

                </div>

                <div class="finding-meta">

                    Relevance:
                    {clean(
                        finding.get(
                            "relevance_score",
                            finding.get(
                                "relevance",
                                0
                            )
                        ),
                        "0"
                    )}

                    &nbsp; • &nbsp;

                    Date:
                    {clean(
                        finding.get(
                            "date"
                        ),
                        "Unknown"
                    )}

                </div>

            </div>
            """)


            url = clean(
                finding.get(
                    "url"
                )
            )


            if url.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                st.markdown(
                    f"[↗ View source]({url})"
                )


    else:

        st.info(
            "No high-priority signals "
            "were identified."
        )


    # ========================================================
    # SOURCE BREAKDOWN
    # ========================================================

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )


    html("""
    <div class="section-label">
        SOURCE INTELLIGENCE
    </div>
    """)


    source_counts = strategy[
        "source_counts"
    ]


    if source_counts:

        source_columns = st.columns(
            min(
                len(source_counts),
                4
            )
        )


        for index, (
            source,
            count
        ) in enumerate(
            source_counts.items()
        ):

            with source_columns[
                index
                % len(source_columns)
            ]:

                html(f"""
                <div class="source-card">

                    <div class="source-name">
                        {clean(source)}
                    </div>

                    <div class="source-count">
                        {count}
                    </div>

                    <div class="card-caption">
                        finding(s)
                    </div>

                </div>
                """)


    else:

        st.info(
            "No source breakdown available."
        )


    # ========================================================
    # CONTEXT AND MEMORY
    # ========================================================

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )


    html("""
    <div class="section-label">
        CONTEXT & MEMORY MANAGEMENT
    </div>
    """)


    html(f"""
    <div class="memory-box">

        <p>

            <strong>
                Current Topic:
            </strong>

            {clean(topic)}

        </p>

        <p>

            <strong>
                Current Objective:
            </strong>

            {clean(objective)}

        </p>

        <p>

            <strong>
                Competitors:
            </strong>

            {clean(
                competitors,
                "None specified"
            )}

        </p>

        <p>

            <strong>
                Memory Agent:
            </strong>

            {clean(
                strategy[
                    "memory_context"
                ]
            )}

        </p>

        <p>

            <strong>
                Storage:
            </strong>

            Short-term session memory +
            persistent
            <code>
                memory_store.json
            </code>

        </p>

    </div>
    """)


    # ========================================================
    # RESEARCH FINDINGS
    # ========================================================

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )


    html("""
    <div class="section-label">
        SCHOLARLY & INTELLIGENCE FINDINGS
    </div>
    """)


    st.header(
        "📚 Research Findings"
    )


    if not findings:

        st.warning(
            "No findings were returned. "
            "Try a broader research area "
            "or objective."
        )


    else:

        for index, finding in enumerate(

            findings,

            start=1

        ):

            title = clean(

                finding.get(
                    "title"
                ),

                "Untitled"

            )


            summary = clean(

                finding.get(
                    "summary"
                ),

                "No summary available."

            )


            if len(summary) > 650:

                summary = (
                    summary[:650]
                    + "..."
                )


            source = clean(

                finding.get(
                    "source"
                ),

                "Unknown"

            )


            organization = clean(

                finding.get(
                    "organization"
                ),

                "Research Community"

            )


            date = clean(

                finding.get(
                    "date"
                ),

                "Unknown"

            )


            score = finding.get(

                "relevance_score",

                finding.get(
                    "relevance",
                    0
                )

            )


            html(f"""
            <div class="finding">

                <span class="badge">
                    {source}
                </span>

                <div class="finding-title">

                    {index}.
                    {title}

                </div>

                <div class="finding-summary">

                    {summary}

                </div>

                <div class="finding-meta">

                    <strong>
                        Relevance:
                    </strong>

                    {clean(
                        score,
                        "0"
                    )}

                    &nbsp; • &nbsp;

                    <strong>
                        Date:
                    </strong>

                    {date}

                    &nbsp; • &nbsp;

                    <strong>
                        Organization:
                    </strong>

                    {organization}

                </div>

            </div>
            """)


            url = clean(
                finding.get(
                    "url"
                )
            )


            if url.startswith(
                (
                    "http://",
                    "https://"
                )
            ):

                st.markdown(
                    f"[↗ View original source]({url})"
                )


    # ========================================================
    # MULTI-AGENT COLLABORATION
    # ========================================================

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )


    html("""
    <div class="section-label">
        MULTI-AGENT COLLABORATION
    </div>
    """)


    a1, a2, a3, a4 = st.columns(4)


    agents = [

        (
            a1,
            "🧭",
            "Orchestrator",
            "Coordinates the intelligence pipeline "
            "and tool usage.",
        ),

        (
            a2,
            "🔬",
            "Research Agent",
            "Finds and ranks evidence from "
            "external sources.",
        ),

        (
            a3,
            "🎯",
            "Strategy Agent",
            "Transforms evidence into "
            "strategic intelligence.",
        ),

        (
            a4,
            "🧠",
            "Memory Agent",
            "Recalls previous context and "
            "persists new scans.",
        ),

    ]


    for column, (
        icon,
        name,
        description
    ) in [

        (
            item[0],
            item[1:],
        )

        for item in agents

    ]:

        pass


    for item in agents:

        column = item[0]
        icon = item[1]
        name = item[2]
        description = item[3]

        with column:

            html(f"""
            <div class="agent">

                <div class="agent-icon">
                    {icon}
                </div>

                <div class="agent-name">
                    {name}
                </div>

                <div class="agent-description">
                    {description}
                </div>

            </div>
            """)


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    "<br><br>",
    unsafe_allow_html=True
)


html("""
<div class="footer">

    <strong>
        ResearchRadar
    </strong>

    &nbsp; • &nbsp;

    AI-Powered Research Intelligence

    &nbsp; • &nbsp;

    Team TriX

</div>
""")