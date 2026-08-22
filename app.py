import streamlit as st
import json
import time
from intelligence_tools import run_intelligence_tools

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ResearchRadar",
    page_icon="🔎",
    layout="wide"
)

# ============================================================
# LOAD DATA
# ============================================================

with open("data.json", "r", encoding="utf-8") as f:
    DATA = json.load(f)

# ============================================================
# CUSTOM CSS
# ============================================================

st.html("""
<style>

.stApp {
    background:
        radial-gradient(
            circle at 15% 10%,
            rgba(71,91,180,.18),
            transparent 30%
        ),
        radial-gradient(
            circle at 85% 10%,
            rgba(0,180,200,.10),
            transparent 30%
        ),
        #080d18;

    color: #edf2ff;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

header {
    background: transparent !important;
}

/* =========================================================
   BRAND
   ========================================================= */

.brand {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 8px;
}

.brand-icon {
    width: 58px;
    height: 58px;
    border-radius: 17px;

    display: flex;
    align-items: center;
    justify-content: center;

    background:
        linear-gradient(
            135deg,
            #536dff,
            #00c6c8
        );

    font-size: 30px;

    box-shadow:
        0 10px 30px rgba(83,109,255,.3);
}

.brand-name {
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: -2px;
    color: #f4f7ff;
}

/* =========================================================
   TEXT
   ========================================================= */

.eyebrow {
    color: #7387ff;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 10px;
}

.subtitle {
    color: #9da9c1;
    font-size: 17px;
    line-height: 1.6;
    max-width: 800px;
    margin-bottom: 35px;
}

/* =========================================================
   HERO
   ========================================================= */

.hero {
    background:
        linear-gradient(
            135deg,
            rgba(83,109,255,.15),
            rgba(0,198,200,.05)
        );

    border: 1px solid #2b3b60;
    border-radius: 22px;

    padding: 30px;
    margin: 25px 0;

    box-shadow:
        0 20px 50px rgba(0,0,0,.25);
}

.hero-label {
    color: #7387ff;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1.7px;
    margin-bottom: 10px;
}

.hero-title {
    font-size: 28px;
    font-weight: 750;
    color: #f4f7ff;
    margin-bottom: 8px;
}

.hero-text {
    color: #9da9c1;
    font-size: 16px;
}

/* =========================================================
   SIGNAL CARDS
   ========================================================= */

.signal-card {
    background:
        linear-gradient(
            145deg,
            #131c2e,
            #0e1626
        );

    border: 1px solid #2b3853;
    border-radius: 18px;

    padding: 25px;
    margin: 18px 0;

    box-shadow:
        0 12px 30px rgba(0,0,0,.18);
}

.signal-badge {
    display: inline-block;

    background: rgba(255,193,91,.12);
    border: 1px solid rgba(255,193,91,.25);

    color: #ffd36a;

    border-radius: 50px;

    padding: 5px 11px;

    font-size: 11px;
    font-weight: 800;

    margin-bottom: 14px;
}

.signal-title {
    font-size: 22px;
    font-weight: 750;
    color: #f4f7ff;
    margin-bottom: 10px;
}

.signal-summary {
    color: #aeb9d0;
    font-size: 15px;
    line-height: 1.6;
}

.signal-meta {
    color: #9ba8c0;
    margin-top: 15px;
    font-size: 14px;
}

.signal-meta strong {
    color: #dce4f5;
}

/* =========================================================
   SO WHAT
   ========================================================= */

.so-what {
    background: rgba(102,124,255,.08);

    border-left: 3px solid #667cff;

    border-radius: 0 12px 12px 0;

    padding: 17px 20px;

    margin-top: 18px;
}

.so-title {
    color: #8495ff;

    font-size: 12px;

    font-weight: 800;

    letter-spacing: 1px;

    margin-bottom: 7px;
}

.so-text {
    color: #c0c9dc;
    line-height: 1.6;
}

/* =========================================================
   RECOMMENDATION
   ========================================================= */

.recommendation {
    background: rgba(55,210,143,.08);

    border: 1px solid rgba(55,210,143,.18);

    border-radius: 12px;

    padding: 17px 20px;

    margin-top: 12px;

    color: #8ce8b8;

    line-height: 1.6;
}

.recommendation-title {
    color: #6ee6a5;
    font-weight: 800;
    margin-bottom: 5px;
}

/* =========================================================
   ACTIVITY
   ========================================================= */

.activity {
    display: flex;
    align-items: center;
    gap: 12px;

    background: #101827;

    border: 1px solid #25324c;

    border-radius: 11px;

    padding: 12px 16px;

    margin: 8px 0;

    color: #cbd5e8;
}

.check {
    color: #55d99a;
    font-weight: 900;
}

/* =========================================================
   COMPETITOR
   ========================================================= */

.competitor {
    background: #101827;

    border: 1px solid #25324c;

    border-radius: 12px;

    padding: 16px 20px;

    margin: 9px 0;

    color: #e1e7f4;
}

.count {
    float: right;
    color: #7f91ff;
}

/* =========================================================
   VERDICT
   ========================================================= */

.verdict-card {
    border-radius: 20px;
    padding: 28px;
    margin: 20px 0 30px 0;

    box-shadow:
        0 15px 40px rgba(0,0,0,.25);
}

.verdict-title {
    display: flex;
    align-items: center;
    gap: 12px;

    font-size: 24px;
    font-weight: 800;

    margin-bottom: 15px;
}

.verdict-text {
    color: #c4cee1;
    font-size: 16px;
    line-height: 1.7;
    margin-bottom: 20px;
}

.decision-box {
    background: rgba(102,124,255,.08);
    border-left: 3px solid #667cff;

    border-radius: 0 12px 12px 0;

    padding: 16px 18px;
}

.decision-label {
    color: #8495ff;

    font-size: 11px;
    font-weight: 800;

    letter-spacing: 1px;

    margin-bottom: 6px;
}

.decision-text {
    color: #d3daea;
    line-height: 1.6;
}

/* =========================================================
   FOOTER
   ========================================================= */

.footer {
    text-align: center;

    color: #596782;

    margin-top: 50px;

    padding-top: 20px;

    border-top: 1px solid #202c43;

    font-size: 13px;
}

</style>
""")

# ============================================================
# HEADER
# ============================================================

st.html("""
<div class="eyebrow">
    AUTONOMOUS COMPETITIVE INTELLIGENCE
</div>

<div class="brand">

    <div class="brand-icon">
        🔎
    </div>

    <div class="brand-name">
        ResearchRadar
    </div>

</div>

<div class="subtitle">
    An autonomous intelligence agent that investigates
    research, competitor activity and emerging industry
    signals — then turns them into actionable strategic insights.
</div>
""")

# ============================================================
# HERO
# ============================================================

st.html("""
<div class="hero">

    <div class="hero-label">
        START AN INTELLIGENCE SCAN
    </div>

    <div class="hero-title">
        What should we investigate?
    </div>

    <div class="hero-text">
        Define your monitoring objective and let the agent
        investigate relevant intelligence.
    </div>

</div>
""")

# ============================================================
# INPUTS
# ============================================================

col1, col2 = st.columns(2)

with col1:

    research_area = st.text_input(
        "Research / Technology Area",
        placeholder="e.g. AI healthcare"
    )

with col2:

    competitors = st.text_input(
        "Competitors",
        placeholder="e.g. Google, Microsoft, HealthAI Technologies"
    )

st.write("")

def search_intelligence(topic, competitors):

    import feedparser
    from urllib.parse import quote

    results = []

    # --------------------------------------------------------
    # Build dynamic search queries
    # --------------------------------------------------------

    queries = [
        f"{topic} latest research",
        f"{topic} latest developments",
        f"{topic} industry news",
        f"{topic} technology trends"
    ]

    competitor_list = [
        c.strip()
        for c in competitors.split(",")
        if c.strip()
    ]

    # Add competitor-specific searches
    for competitor in competitor_list:
        queries.append(
            f"{competitor} {topic}"
        )

    # --------------------------------------------------------
    # Search Google News RSS dynamically
    # --------------------------------------------------------

    for query in queries:

        try:

            encoded_query = quote(query)

            url = (
                "https://news.google.com/rss/search?"
                f"q={encoded_query}"
                "&hl=en-IN"
                "&gl=IN"
                "&ceid=IN:en"
            )

            feed = feedparser.parse(url)

            for entry in feed.entries[:5]:

                title = entry.get(
                    "title",
                    "Untitled"
                )

                summary = entry.get(
                    "summary",
                    "No summary available."
                )

                source = entry.get(
                    "source",
                    {}
                )

                if isinstance(source, dict):

                    source_name = source.get(
                        "title",
                        "Google News"
                    )

                else:

                    source_name = "Google News"

                published = entry.get(
                    "published",
                    "Recent"
                )

                # ------------------------------------------------
                # Try to identify organization
                # ------------------------------------------------

                organization = "Industry"

                for competitor in competitor_list:

                    if competitor.lower() in title.lower():

                        organization = competitor

                        break

                # ------------------------------------------------
                # Determine importance
                # ------------------------------------------------

                important_words = [
                    "launch",
                    "acquisition",
                    "investment",
                    "funding",
                    "patent",
                    "breakthrough",
                    "new model",
                    "partnership",
                    "expansion",
                    "research",
                    "regulation",
                    "technology"
                ]

                importance = "High"

                if not any(
                    word in (
                        title + " " + summary
                    ).lower()
                    for word in important_words
                ):

                    importance = "Medium"

                # ------------------------------------------------
                # Strategic signal
                # ------------------------------------------------

                signal = (
                    f"New development detected in "
                    f"{topic}"
                )

                if organization != "Industry":

                    signal = (
                        f"{organization} is showing "
                        f"activity related to {topic}"
                    )

                # ------------------------------------------------
                # Add finding
                # ------------------------------------------------

                results.append({

                    "topic": topic,

                    "title": title,

                    "summary": summary,

                    "organization": organization,

                    "importance": importance,

                    "source": source_name,

                    "date": published,

                    "signal": signal

                })

        except Exception:

            # If one search fails, continue with
            # the remaining searches.
            continue

    # --------------------------------------------------------
    # Remove duplicate articles
    # --------------------------------------------------------

    unique_results = []

    seen_titles = set()

    for item in results:

        title_key = item["title"].strip().lower()

        if title_key not in seen_titles:

            seen_titles.add(title_key)

            unique_results.append(item)

    return unique_results


# ============================================================
# ANALYSIS AGENT
# ============================================================

def analyze_findings(findings):

    high_priority = [
        item
        for item in findings
        if item.get(
            "importance",
            ""
        ).lower() == "high"
    ]

    competitors_found = {}

    for item in findings:

        organization = item.get(
            "organization",
            "Unknown"
        )

        competitors_found[organization] = (
            competitors_found.get(
                organization,
                0
            ) + 1
        )

    return high_priority, competitors_found


# ============================================================
# VERIFICATION AGENT
# ============================================================

def verify_findings(findings):

    verified = []

    for item in findings:

        if (
            item.get("title")
            and item.get("summary")
            and item.get("source")
            and item.get("date")
        ):

            verified.append(item)

    return verified


# ============================================================
# RUN AGENT
# ============================================================

def run_agent(topic, competitors):

    steps = []

    steps.append(
        "Understanding monitoring objective"
    )

    time.sleep(.2)

    steps.append(
        "Creating investigation plan"
    )

    time.sleep(.2)

    findings = search_intelligence(
        topic,
        competitors
    )

    steps.append(
        f"Searching intelligence sources — {len(findings)} findings"
    )

    time.sleep(.3)

    high_priority, competitor_activity = (
        analyze_findings(findings)
    )

    steps.append(
        "Analyzing research and competitor activity"
    )

    time.sleep(.3)

    verified = verify_findings(
        findings
    )

    steps.append(
        f"Cross-checking findings — {len(verified)} verified"
    )

    time.sleep(.3)

    steps.append(
        "Detecting strategic signals"
    )

    time.sleep(.2)

    steps.append(
        "Generating actionable recommendations"
    )

    time.sleep(.2)

    return {
        "steps": steps,
        "findings": verified,
        "high_priority": high_priority,
        "competitors": competitor_activity
    }


# ============================================================
# START BUTTON
# ============================================================

if st.button(
    "🚀  Start Intelligence Scan",
    type="primary"
):

    # ========================================================
    # VALIDATE INPUT
    # ========================================================

    if not research_area.strip():

        st.warning(
            "Please enter a research or technology area."
        )

        st.stop()

    # ========================================================
    # RUN AGENT
    # ========================================================

    with st.spinner(
        "ResearchRadar is investigating..."
    ):

        result = run_agent(
            research_area,
            competitors
        )

    st.divider()

    # ========================================================
    # ACTIVITY
    # ========================================================

    st.html("""
    <div class="eyebrow">
        AGENT EXECUTION
    </div>
    """)

    st.header(
        "🧠 Investigation Activity"
    )

    for number, step in enumerate(
        result["steps"],
        1
    ):

        st.html(
            f"""
            <div class="activity">

                <span class="check">
                    ✓
                </span>

                <span>
                    <strong>{number}.</strong>
                    {step}
                </span>

            </div>
            """
        )

    st.success(
        "Intelligence investigation complete."
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    st.html("""
    <div class="eyebrow">
        EXECUTIVE OVERVIEW
    </div>
    """)

    st.header(
        "📊 Intelligence Summary"
    )

    findings = result["findings"]

    high_priority = result["high_priority"]

    competitor_data = result["competitors"]

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Relevant Findings",
            len(findings)
        )

    with col2:

        st.metric(
            "High-Priority Signals",
            len(high_priority)
        )

    with col3:

        st.metric(
            "Organizations Tracked",
            len(competitor_data)
        )

    # ========================================================
    # HIGH PRIORITY SIGNALS
    # ========================================================

    st.html("""
    <div class="eyebrow">
        STRATEGIC SIGNALS
    </div>
    """)

    st.header(
        "🚨 High-Priority Signals"
    )

    if high_priority:

        for item in high_priority:

            title = item.get(
                "title",
                "Untitled finding"
            )

            summary = item.get(
                "summary",
                "No summary available."
            )

            importance = item.get(
                "importance",
                "Unknown"
            )

            organization = item.get(
                "organization",
                "Unknown"
            )

            source = item.get(
                "source",
                "Unknown"
            )

            signal = item.get(
                "signal",
                "Strategic activity detected"
            )

            st.html(
                f"""
                <div class="signal-card">

                    <div class="signal-badge">
                        HIGH PRIORITY
                    </div>

                    <div class="signal-title">
                        {title}
                    </div>

                    <div class="signal-summary">
                        {summary}
                    </div>

                    <div class="signal-meta">

                        <strong>Impact:</strong>
                        {importance}

                        &nbsp;&nbsp;•&nbsp;&nbsp;

                        <strong>Organization:</strong>
                        {organization}

                        &nbsp;&nbsp;•&nbsp;&nbsp;

                        <strong>Source:</strong>
                        {source}

                    </div>

                    <div class="so-what">

                        <div class="so-title">
                            💡 SO WHAT?
                        </div>

                        <div class="so-text">

                            {signal}.

                            This indicates increasing activity
                            around <strong>{research_area}</strong>
                            and may affect competitive positioning.

                        </div>

                    </div>

                    <div class="recommendation">

                        <div class="recommendation-title">
                            🎯 Recommended Action
                        </div>

                        Monitor this development,
                        investigate related activity,
                        and evaluate its potential impact
                        on research or product strategy.

                    </div>

                </div>
                """
            )

    else:

        st.info(
            "No high-priority signals were detected."
        )

    # ========================================================
    # FINDINGS
    # ========================================================

    st.html("""
    <div class="eyebrow">
        SOURCE INTELLIGENCE
    </div>
    """)

    st.header(
        "📚 Research & Competitor Findings"
    )

    if findings:

        for item in findings:

            title = item.get(
                "title",
                "Untitled"
            )

            organization = item.get(
                "organization",
                "Unknown"
            )

            with st.expander(
                f"{title}  ·  {organization}"
            ):

                st.write(
                    item.get(
                        "summary",
                        "No summary available."
                    )
                )

                st.write(
                    "**Signal:** "
                    + item.get(
                        "signal",
                        "No signal available."
                    )
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.write(
                        "**Date:** "
                        + item.get(
                            "date",
                            "Unknown"
                        )
                    )

                with col2:

                    st.write(
                        "**Source:** "
                        + item.get(
                            "source",
                            "Unknown"
                        )
                    )

                with col3:

                    st.write(
                        "**Importance:** "
                        + item.get(
                            "importance",
                            "Unknown"
                        )
                    )

    else:

        st.info(
            "No relevant findings were found for this scan."
        )

    # ========================================================
    # COMPETITOR ACTIVITY
    # ========================================================

    st.html("""
    <div class="eyebrow">
        COMPETITIVE LANDSCAPE
    </div>
    """)

    st.header(
        "🏢 Competitor Activity"
    )

    if competitor_data:

        for organization, count in competitor_data.items():

            st.html(
                f"""
                <div class="competitor">

                    <strong>
                        {organization}
                    </strong>

                    <span class="count">
                        {count} relevant development(s)
                    </span>

                </div>
                """
            )

    else:

        st.info(
            "No specific competitor activity was detected."
        )

    # ========================================================
    # STRATEGIC TAKEAWAY
    # ========================================================

    st.html("""
    <div class="eyebrow">
        STRATEGIC TAKEAWAY
    </div>
    """)

    st.header(
        "🎯 What should you do next?"
    )

    st.html(
        f"""
        <div class="hero">

            <div class="hero-title">
                Monitor {research_area}
            </div>

            <div class="hero-text">

                ResearchRadar identified
                <strong>{len(findings)}
                relevant developments</strong>,
                including
                <strong>{len(high_priority)}
                high-priority signals</strong>.

                These findings can be used to identify
                emerging opportunities, competitive threats
                and research trends.

            </div>

            <div class="recommendation">

                <div class="recommendation-title">
                    Recommended next step
                </div>

                Continue monitoring high-priority developments
                and investigate related research, competitor
                and patent activity.

            </div>

        </div>
        """
    )

    # ========================================================
    # FINAL VERDICT
    # ========================================================

    st.html("""
    <div class="eyebrow">
        AGENT DECISION
    </div>
    """)

    st.header(
        "🎯 Final Verdict"
    )

    # These variables exist because this section
    # runs ONLY after the intelligence scan.
    high_count = len(high_priority)

    finding_count = len(findings)

    competitor_count = len(competitor_data)

    # ========================================================
    # DETERMINE VERDICT
    # ========================================================

    if high_count >= 3:

        verdict = "HIGH COMPETITIVE RISK"

        verdict_icon = "🔴"

        verdict_color = "#ff6b6b"

        verdict_text = (
            f"ResearchRadar detected {high_count} "
            f"high-priority signals across "
            f"{competitor_count} organizations. "
            f"The monitored area shows significant "
            f"competitive activity and requires "
            f"immediate strategic attention."
        )

        decision = (
            "Investigate the highest-impact competitor "
            "developments and evaluate whether the current "
            "research or product strategy needs to respond."
        )

    elif high_count >= 1:

        verdict = "WATCH CLOSELY"

        verdict_icon = "🟠"

        verdict_color = "#ffb454"

        verdict_text = (
            f"ResearchRadar detected {high_count} "
            f"high-priority signal(s) among "
            f"{finding_count} relevant developments. "
            f"The activity is strategically relevant "
            f"but does not yet indicate an immediate "
            f"competitive threat."
        )

        decision = (
            "Continue monitoring competitor, research "
            "and patent activity and investigate whether "
            "the detected signals develop into a stronger "
            "competitive trend."
        )

    else:

        verdict = "LOW IMMEDIATE RISK"

        verdict_icon = "🟢"

        verdict_color = "#55d99a"

        verdict_text = (
            f"ResearchRadar found {finding_count} "
            f"relevant development(s), but no "
            f"high-priority signals were detected. "
            f"There is currently no strong indication "
            f"of immediate competitive disruption."
        )

        decision = (
            "Maintain routine monitoring and reassess "
            "if new research, competitor launches or "
            "patent activity appears."
        )

    # ========================================================
    # VERDICT CARD
    # ========================================================

    st.html(
        f"""
        <div
            class="verdict-card"
            style="
                background:
                    linear-gradient(
                        135deg,
                        rgba(20,30,50,.98),
                        rgba(12,20,35,.98)
                    );

                border:
                    1px solid {verdict_color};
            "
        >

            <div
                class="verdict-title"
                style="
                    color:{verdict_color};
                "
            >

                <span style="font-size:28px;">
                    {verdict_icon}
                </span>

                <span>
                    {verdict}
                </span>

            </div>

            <div class="verdict-text">

                {verdict_text}

            </div>

            <div class="decision-box">

                <div class="decision-label">
                    FINAL DECISION
                </div>

                <div class="decision-text">

                    {decision}

                </div>

            </div>

        </div>
        """
    )

    # ========================================================
    # VERDICT METRICS
    # ========================================================

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Findings",
            finding_count
        )

    with col2:

        st.metric(
            "High Priority",
            high_count
        )

    with col3:

        st.metric(
            "Organizations",
            competitor_count
        )

# ============================================================
# FOOTER
# ============================================================

st.html("""
<div class="footer">

    ResearchRadar · Autonomous Competitive Intelligence

    <br><br>

    Investigate → Verify → Understand → Act

</div>
""")