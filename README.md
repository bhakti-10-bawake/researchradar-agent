# 🔎 ResearchRadar

## 👥 Team Members

| Name | Role / Details |
|------|----------------|
| **Bhakti Bawake** | Team Leader |
| **Aditi Kadam** | Team Member |
| **Harshal Ingale** | Team Member |

**Team:** TriX  
**Project:** ResearchRadar

### Autonomous Research & Competitive Intelligence Agent

ResearchRadar is an AI-powered research intelligence platform that transforms a user's research objective into actionable strategic insights.

Instead of simply searching and summarizing information, ResearchRadar dynamically selects relevant external research and intelligence tools, retrieves current information, and coordinates specialized agents to analyze the findings.

---

## 🚀 Key Features

### 🛠️ 1. Dynamic External Tool Calling

ResearchRadar dynamically determines which external tools are relevant to the user's research topic, objective, and competitive context.

Currently integrated tools:

- 📚 **arXiv API** — Retrieves recent scientific and technical research papers.
- 🌐 **OpenAlex API** — Retrieves scholarly works and academic research activity.
- 📖 **Crossref API** — Retrieves scholarly publication metadata.
- 🧠 **Semantic Scholar API** — Retrieves relevant academic research.
- 📰 **Google News RSS** — Retrieves recent news and industry signals.
- 🌍 **GDELT** — Retrieves global news and event intelligence.

The system can dynamically select relevant tools depending on the research topic and objective instead of blindly using the same source for every request.

The research query uses both the **Research / Technology Area** and the **Intelligence Objective**, allowing the system to focus on the user's actual research goal.

---

### 🤖 2. Multi-Agent Architecture

ResearchRadar uses specialized agents with clearly defined responsibilities.

#### 🔬 Agent 1 — Research Intelligence Agent

Responsibilities:

- Understand the research objective.
- Collect relevant scholarly and intelligence information.
- Call selected external APIs.
- Retrieve research papers and relevant intelligence findings.
- Calculate relevance of retrieved findings.
- Remove duplicate results.
- Rank relevant findings.
- Prepare structured research findings for the Strategy Agent.

#### 🎯 Agent 2 — Strategic Analysis Agent

Responsibilities:

- Receive findings produced by Agent 1.
- Analyze the research activity.
- Identify strategic signals.
- Analyze competitor-related findings.
- Identify high-priority findings.
- Generate recommendations.
- Produce a final strategic verdict.

#### 🧠 Agent 3 — Memory Agent

Responsibilities:

- Maintain short-term conversation and scan context.
- Recall relevant previous intelligence scans.
- Provide previous context to the Strategy Agent.
- Store completed intelligence scans.
- Maintain persistent long-term memory across sessions.

---

### 🔄 Agent Orchestration

The agents collaborate through an orchestrator:

```text
                    USER OBJECTIVE
                          │
                          ▼
                 ┌─────────────────┐
                 │   ORCHESTRATOR  │
                 └────────┬────────┘
                          │
                  Dynamic Tool Selection
                          │
          ┌───────────────┼────────────────┐
          ▼               ▼                ▼
      ┌────────┐     ┌──────────┐     ┌───────────┐
      │ arXiv  │     │ OpenAlex │     │ News /    │
      │  API   │     │   API    │     │ Research  │
      └────┬───┘     └────┬─────┘     │   APIs    │
           │              │            └─────┬─────┘
           └──────────────┼──────────────────┘
                          ▼
             🔬 RESEARCH INTELLIGENCE AGENT
                          │
                          │ Research Findings
                          ▼
                  🧠 MEMORY AGENT
                          │
                  Previous Context
                          │
                          ▼
             🎯 STRATEGIC ANALYSIS AGENT
                          │
                ┌─────────┼──────────┐
                ▼         ▼          ▼
             Signals  Competitor  Recommendations
                       Analysis
                          │
                          ▼
                    FINAL VERDICT
##Live demo
https://researchradar-agent-j5rjyhiou6d3uotxxyvhzj.streamlit.app/
