# 🔎 ResearchRadar

## Autonomous Research & Competitor Intelligence Agent

ResearchRadar is an autonomous intelligence agent designed to help organizations, startups, and research institutions monitor research developments, competitor activities, industry news, and emerging technology signals.

Instead of simply displaying information, ResearchRadar investigates a user-defined topic, gathers intelligence from multiple external sources, analyzes important developments, explains why they matter, recommends actions, and produces a final strategic verdict.

---

## 👥 Team Members

- **Bhakti Bawake** — Team Leader — SY-CSE
- **Aditi Kadam** — Team Member — SY-CSE
- **Harshal Ingale** — Team Member — SY-CSE

---

## 🎯 Theme

**Research & Competitor Tracking**

---

# 📌 Problem Statement

Organizations, startups, and research institutions operate in rapidly changing and highly competitive environments.

Keeping track of:

- Scientific research
- Competitor activities
- Industry developments
- Emerging technologies
- Research trends

requires monitoring multiple information sources.

Traditional manual monitoring is:

- Time-consuming
- Difficult to scale
- Inefficient
- Prone to missing important developments

Missing important intelligence can result in:

- Lost opportunities
- Delayed innovation
- Poor strategic decisions
- Weakened competitive positioning

ResearchRadar addresses this problem through an autonomous research and competitive intelligence workflow.

---

# 💡 Our Solution

ResearchRadar allows users to enter a research or technology area and optionally provide competitors they want to monitor.

The agent dynamically investigates the selected topic using multiple external intelligence sources:

- 📰 Google News RSS
- 📚 arXiv API
- 🔬 OpenAlex API

The collected intelligence is then analyzed to identify:

- Relevant findings
- High-priority signals
- Competitor activity
- Research trends
- Strategic implications
- Recommended actions
- Final strategic verdict

### Core Workflow

**Investigate → Collect → Analyze → Verify → Detect Signals → Explain → Recommend → Decide**

---

# 🚀 Key Features

## 🔎 1. Dynamic Topic Investigation

ResearchRadar accepts user-defined research and technology topics instead of being restricted to one predefined domain.

Example topics include:

- Artificial Intelligence
- Electric Vehicles
- Cybersecurity
- Quantum Computing
- Robotics
- Renewable Energy
- FinTech
- Space Technology

The system dynamically searches for intelligence relevant to the selected topic.

---

## 📰 2. Google News Industry Intelligence

ResearchRadar uses Google News RSS to retrieve current industry and competitor-related developments.

It can help identify:

- Company announcements
- Product launches
- Partnerships
- Funding activity
- Investments
- Industry developments
- Technology trends
- Regulatory developments

This provides a view of **what is happening in the current industry landscape**.

---

## 📚 3. arXiv Research Intelligence

ResearchRadar integrates the arXiv API to retrieve recent academic research based on the user's selected research or technology topic.

It can help identify:

- Recent research papers
- Emerging research areas
- Scientific developments
- Research trends
- Potential technological breakthroughs

This provides insight into **what researchers are currently exploring**.

---

## 🔬 4. OpenAlex Scholarly Intelligence

ResearchRadar integrates the OpenAlex API to explore the broader scholarly research landscape.

OpenAlex can provide information related to:

- Research publications
- Authors and researchers
- Institutions
- Research concepts
- Scholarly trends
- Research activity across technology domains

OpenAlex complements arXiv by providing a broader scholarly perspective across research literature.

---

# 🧠 5. Multi-Source Intelligence

ResearchRadar combines information from multiple intelligence sources to provide a broader understanding of a technology domain.

```text
          📰 Google News
       Industry Intelligence
                │
                │
                ▼
          ┌───────────┐
          │           │
          │ Research  │
          │   Radar   │
          │   Agent   │
          │           │
          └───────────┘
                ▲
                │
       ┌────────┴────────┐
       │                 │
       ▼                 ▼
 📚 arXiv            🔬 OpenAlex
Academic Research   Scholarly Research
