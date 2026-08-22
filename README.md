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

Instead of simply searching and summarizing information, ResearchRadar dynamically selects relevant external research tools, retrieves current scholarly intelligence, and coordinates specialized agents to analyze the findings.

---

## 🚀 Key Features

### 🛠️ 1. Dynamic External Tool Calling

ResearchRadar dynamically determines which external tools are relevant to the user's research objective.

Currently integrated tools:

- 📚 **arXiv API** — Retrieves recent scientific and technical research papers.
- 🌐 **OpenAlex API** — Retrieves scholarly works and academic research activity.

The system can select one or both tools depending on the research topic and objective.

### 🤖 2. Multi-Agent Architecture

ResearchRadar uses specialized agents with clearly defined responsibilities.

#### 🔬 Agent 1 — Research Intelligence Agent

Responsibilities:

- Understand the research objective.
- Collect relevant scholarly intelligence.
- Call selected external APIs.
- Retrieve research papers and academic findings.
- Remove duplicate research results.
- Prepare structured research findings.

#### 🎯 Agent 2 — Strategic Analysis Agent

Responsibilities:

- Receive findings produced by Agent 1.
- Analyze the research activity.
- Identify strategic signals.
- Analyze competitor-related findings.
- Generate recommendations.
- Produce a final strategic verdict.

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
             ┌────────┴────────┐
             ▼                 ▼
        ┌──────────┐      ┌──────────┐
        │  arXiv   │      │ OpenAlex │
        │   API    │      │   API    │
        └────┬─────┘      └────┬─────┘
             │                 │
             └────────┬────────┘
                      ▼
        🔬 RESEARCH INTELLIGENCE AGENT
                      │
                      │ Research Findings
                      ▼
        🎯 STRATEGIC ANALYSIS AGENT
                      │
             ┌────────┼─────────┐
             ▼        ▼         ▼
          Signals  Competitor  Recommendations
                   Analysis
                      │
                      ▼
              FINAL VERDICT