# 🔎 ResearchRadar

### AI-Powered Multi-Agent Research Intelligence Platform

## 👥 Team TriX

- **Bawake Bhakti — Team Leader**
- **Aditi Kadam**
- **Harshal Ingale**

---

## 🚀 About ResearchRadar

ResearchRadar transforms open-ended research questions into
evidence-grounded, decision-ready intelligence.

Instead of simply returning research-paper links, ResearchRadar
researches, evaluates, compares and synthesizes evidence using
multiple specialized agents.

---

# 🧠 What ResearchRadar Does

```text
Research Objective
       ↓
Dynamic Planning
       ↓
Tool Selection
       ↓
Parallel Research
       ↓
Evidence Evaluation
       ↓
Conflict Detection
       ↓
Self Evaluation
       ↓
Replanning / Recovery
       ↓
Gemini Strategic Synthesis
       ↓
Intelligence Brief
       ↓
Persistent Memory
```

---

# 1. 🤖 Agentic Reasoning

ResearchRadar follows an adaptive:

**Observe → Reason → Decide → Act → Evaluate → Replan**

loop.

The agent determines what information is required, selects
appropriate tools, observes their results and evaluates whether
additional research is required.

This allows the system to move beyond a fixed search workflow.

**Status: ✅ Implemented**

---

# 2. 🛠️ Tool Calling

ResearchRadar integrates multiple external research and intelligence
sources:

- arXiv API
- OpenAlex API
- Crossref API
- Semantic Scholar API
- Google News RSS
- GDELT API

Tools are selected according to the research objective rather than
blindly calling every available API.

The system also supports fallback behavior when an external tool
fails or becomes unavailable.

**Status: ✅ Implemented**

---

# 3. 🤝 Multi-Agent Architecture

ResearchRadar uses specialized agents with clearly defined
responsibilities.

| Agent | Responsibility |
|---|---|
| Orchestrator | Coordinates the research mission |
| Planner | Decomposes objectives and selects tools |
| Research Agent | Collects external evidence |
| Evidence Judge | Evaluates evidence and detects conflicts |
| Self-Evaluator | Evaluates mission quality |
| Strategy Agent | Converts evidence into strategic intelligence |
| Memory Agent | Stores and recalls previous research |

Agents collaborate through shared structured state.

**Status: ✅ Implemented**

---

# 4. 🧠 Context & Memory Management

ResearchRadar maintains both short-term task context and persistent
research memory.

### Short-Term Context

The shared research state can contain:

- Research topic
- Objective
- Competitors
- Selected tools
- Research findings
- Evidence scores
- Conflicting evidence
- Confidence
- Iteration count
- Resource budget
- Execution trace
- Strategy results

### Long-Term Memory

Previous research scans are persisted and can influence future
research missions.

Example:

```text
Previous Scan → HIGH signal

Current Scan → MEDIUM signal

        ↓

Strategy Agent receives previous context
and can reason about changes over time.
```

**Status: ✅ Implemented**

---

# 5. 🧩 Agent Framework — LangGraph

ResearchRadar uses **LangGraph** as its agentic framework.

LangGraph was selected because ResearchRadar requires stateful,
conditional and iterative execution rather than a simple fixed
pipeline.

The framework supports:

- ✅ Dynamic planning
- ✅ Multi-agent orchestration
- ✅ Conditional routing
- ✅ Parallel execution
- ✅ Shared state
- ✅ Checkpointed execution context
- ✅ Autonomous replanning
- ✅ Failure recovery
- ✅ Tool fallback
- ✅ Conflicting-evidence resolution
- ✅ Uncertainty-aware decisions
- ✅ Resource-aware execution
- ✅ Self-evaluation
- ✅ Hypothesis verification
- ✅ Memory-based reasoning
- ✅ Loop/deadlock protection
- ✅ Adaptive task decomposition

---
## 6. Evaluation

ResearchRadar was evaluated using an automated evaluation pipeline designed to measure reliability, robustness, evidence quality, groundedness, recovery, uncertainty awareness, adaptive behaviour, latency, and resource usage.

### Evaluation Configuration

- Repeats: 1
- Maximum iterations: 3
- Tool budget: 6
- Scenarios tested: 6
- Human evaluation rubric: 1–5 scale

### Evaluation Scenarios

The agent was tested under:

1. **Normal** — Standard research request with available tools.
2. **Ambiguous** — Research objective with incomplete or unclear intent.
3. **Contradictory** — Evidence containing conflicting signals.
4. **Incomplete** — Research performed with incomplete information.
5. **Adversarial** — Challenging research conditions designed to test uncertainty handling.
6. **Tool Failure** — External research tools intentionally unavailable or failing.

### Automated Results

| Scenario | Task Completion | Evidence Quality | Groundedness | Hallucination Risk | Recovery | Uncertainty Awareness | Adaptive Behaviour | Latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Normal | 100% | 83% | 100% | 0% | 50% | 100% | 25% | 14.37s |
| Ambiguous | 100% | 67% | 100% | 0% | 100% | 100% | 75% | 16.22s |
| Contradictory | 100% | 77% | 100% | 0% | 100% | 100% | 75% | 26.06s |
| Incomplete | 100% | 78% | 100% | 0% | 100% | 100% | 75% | 16.36s |
| Adversarial | 100% | 74% | 100% | 0% | 100% | 100% | 75% | 21.71s |
| Tool Failure | 100% | 77% | 100% | 0% | 100% | 100% | 75% | 15.34s |

### Additional Measurements

The evaluator also recorded:

- Number of research findings
- Number of verified findings
- Tool failures
- Conflicting evidence
- Number of tool calls
- Number of reasoning iterations
- Execution latency
- Resource efficiency
- Errors encountered during execution

The evaluation demonstrated that the system maintained **100% task completion and 100% groundedness across all tested scenarios**, while maintaining **0% measured hallucination risk**. The agent also demonstrated recovery behaviour when tools failed or evidence conflicted.

### Human Evaluation

A human evaluation rubric was defined using a 1–5 scale for:

- Accuracy
- Groundedness
- Task Completion
- Uncertainty Handling
- Recovery
- Clarity

The automated metrics provide reproducible system-level measurements, while the human rubric allows evaluators to independently assess the quality and usefulness of the final intelligence output.

### Evaluation Artifact

The complete machine-generated evaluation output is stored in:

`evaluation_results.json`

This artifact contains the configuration, scenario-level results, measured metrics, and human evaluation rubric.

## 🔄 Dynamic Planning & Conditional Routing

ResearchRadar does not assume that every research objective requires
the same workflow.

The planner determines which research dimensions are required and
selects appropriate tools.

Example:

```text
Research Objective
        ↓
Identify required evidence
        ↓
Select relevant tools
        ↓
Execute research
        ↓
Evaluate evidence
        ↓
Is evidence sufficient?
       /       \
     YES        NO
      ↓         ↓
  Strategy    Replan
      ↓
Final Intelligence
```

This allows the system to adapt its execution according to the
mission state.

---

## ⚡ Parallel Execution

Independent research sources can be queried as parallel research
branches.

```text
                 Research Mission
                       ↓
          ┌────────────┼────────────┐
          ↓            ↓            ↓
        arXiv       OpenAlex     Crossref
          ↓            ↓            ↓
      Semantic      News RSS      GDELT
      Scholar
          └────────────┼────────────┘
                       ↓
                Evidence Judge
```

The collected evidence is then combined into the shared research
state.

---

## 🗃️ Shared State

Agents communicate using a shared research state.

Important state information includes:

```text
topic
objective
competitors
selected_tools
research_findings
evidence_count
confidence
conflicts
strategy
memory_context
execution_trace
iteration
resource_budget
```

This allows each agent to build upon the work of other agents.

---

## 🛡️ Failure Recovery & Tool Fallback

External APIs can fail due to rate limits, timeouts or temporary
unavailability.

During testing, ResearchRadar encountered failures including:

```text
Semantic Scholar → HTTP 429 Too Many Requests

GDELT → HTTP 429 Too Many Requests

GDELT → Connection Timeout
```

Instead of terminating the complete research mission, the system
records the failure and continues using available evidence and
fallback sources.

```text
Tool Failure
     ↓
Failure Detection
     ↓
Fallback / Replanning
     ↓
Continue Research
     ↓
Evidence Evaluation
     ↓
Strategic Synthesis
```

---

## ⚖️ Conflicting-Evidence Resolution

ResearchRadar explicitly detects conflicting evidence.

The Evidence Judge evaluates supporting and limiting signals rather
than assuming every source agrees.

Example:

```text
Supporting signals: 1
Limiting signals:   4

        ↓

Mixed evidence detected
        ↓
Confidence reduced
        ↓
Binary conclusion avoided
```

This allows the final result to communicate uncertainty instead of
hiding it.

---

## 📊 Uncertainty-Aware Decisions

ResearchRadar considers:

- Evidence strength
- Evidence count
- Conflicting signals
- Confidence
- Risks
- Limitations

The final system can produce signals such as:

```text
HIGH
MEDIUM
LOW
WATCH CLOSELY
```

instead of presenting uncertain research as absolute fact.

---

## 💰 Resource-Aware Execution

Agentic systems can potentially consume unlimited tools and
iterations.

ResearchRadar therefore uses execution constraints such as:

- Maximum iterations
- Tool budget
- Evidence limits
- Completion checks

These constraints help prevent:

- Infinite loops
- Excessive API usage
- Unnecessary tool calls
- Uncontrolled agent execution

---

## 🧪 Self-Evaluation

The Self-Evaluator reviews the mission after evidence collection.

It considers factors such as:

- Evidence quality
- Tool failures
- Conflicting evidence
- Mission completeness
- Confidence
- Available resources

Example execution:

```text
Evidence Judge
→ Scored evidence quality

Evidence Judge
→ Resolved conflicting evidence

Self-Evaluator
→ Evaluated mission quality

Strategy Agent
→ Generated final intelligence brief
```

---

## 🔬 Hypothesis Verification

ResearchRadar separates:

```text
Evidence Discovery
        ↓
Evidence Evaluation
        ↓
Strategic Interpretation
```

This prevents the Strategy Agent from treating every retrieved
document as automatically valid evidence.

The Evidence Judge evaluates relevance and conflicting signals before
strategic synthesis.

---

## 🔁 Loop & Deadlock Protection

ResearchRadar uses:

- Maximum iteration limits
- Tool budgets
- Execution state
- Completion checks

to prevent uncontrolled agent loops.

Example:

```text
Iteration 1
    ↓
Iteration 2
    ↓
Iteration 3
    ↓
STOP / FINALIZE
```

---

## 🧩 Adaptive Task Decomposition

Broad research objectives can be divided into multiple research
dimensions.

Example:

```text
EV Solid-State Batteries
        ↓
Academic Research
        +
Technical Breakthroughs
        +
Manufacturing Challenges
        +
Competitor Activity
        +
Commercial Opportunities
        ↓
Unified Intelligence Assessment
```

The final result combines these dimensions rather than presenting
them as unrelated search results.

---

# 🧠 Gemini Strategic Synthesis

Google Gemini is used by the Strategy Agent to transform evaluated
evidence into a higher-level intelligence brief.

The final result can contain:

- Verdict
- Summary
- Emerging Trends
- Risks
- Recommendations
- Competitor Context
- Confidence
- Evidence Count
- Supporting Sources

The raw evidence remains available for verification.

---

# 📋 Intelligence Brief

The key output of ResearchRadar is an **AI Intelligence Brief**.

Instead of:

```text
Research Paper 1
Research Paper 2
Research Paper 3
...
Research Paper 20
```

ResearchRadar produces:

```text
Strategic Verdict
       ↓
Summary
       ↓
Emerging Trends
       ↓
Risks
       ↓
Recommendation
       ↓
Confidence
       ↓
Supporting Evidence
```

This turns research retrieval into research intelligence.

---

# 🧨 Adversarial Testing

Task 5 was tested under adversarial conditions involving:

- External API failures
- API rate limiting
- Timeouts
- Conflicting evidence
- Limited resource budgets
- LLM/model availability issues

The system was able to continue the mission using fallback evidence,
evaluate uncertainty and generate a final intelligence assessment.

Example:

```text
Research Agent
      ↓
Tool Failure
      ↓
Fallback Research
      ↓
Evidence Judge
      ↓
Conflict Resolution
      ↓
Self-Evaluator
      ↓
Strategy Agent
      ↓
Gemini Synthesis
      ↓
Final Intelligence Brief
```

---

# 🖥️ User Interface

ResearchRadar provides a Streamlit-based research intelligence
dashboard.

The interface displays:

- Research objective
- Agent execution progress
- Tool selection
- Agent collaboration
- Intelligence Brief
- Confidence
- Evidence count
- Supporting sources
- Memory context
- Previous research scans

The UI makes the multi-agent execution visible rather than hiding
the agent architecture behind a single response.

---

# 🛠️ Technology Stack

- **Python** — Core implementation
- **LangGraph** — Agent orchestration
- **Google Gemini** — Strategic synthesis
- **Streamlit** — Web interface
- **arXiv API** — Academic research
- **OpenAlex API** — Scholarly discovery
- **Crossref API** — Publication metadata
- **Semantic Scholar API** — Research discovery
- **Google News RSS** — Recent news intelligence
- **GDELT API** — Global news/event intelligence
- **JSON** — Persistent memory and data storage
- **Git/GitHub** — Version control

---

# 📁 Project Structure

```text
researchradar-agent/
│
├── app.py
├── agent_graph.py
├── intelligence_tools.py
├── test_tools.py
├── memory_store.json
├── data.json
├── requirements.txt
├── README.md
├── app_backup.py
└── .gitignore
```

---

# ▶️ Running the Project

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configure Gemini

Set the Gemini API key as an environment variable:

```powershell
$env:GEMINI_API_KEY="YOUR_API_KEY"
```

## Test Agent Graph

```bash
python agent_graph.py
```

## Run Streamlit Application

```bash
streamlit run app.py
```

---

# 🧪 Example Input

```text
Analyze recent breakthroughs, manufacturing challenges,
competitor activity and commercial opportunities in
solid-state batteries for electric vehicles.
```

Example competitors:

```text
Toyota, QuantumScape, Samsung SDI
```

ResearchRadar then dynamically researches the topic, evaluates the
evidence and generates an intelligence brief.

---

# 🏆 Why ResearchRadar?

Traditional research systems:

```text
Query
  ↓
Search
  ↓
Research Papers
  ↓
Links
```

ResearchRadar:

```text
Research Objective
        ↓
Reason
        ↓
Plan
        ↓
Select Tools
        ↓
Research
        ↓
Verify Evidence
        ↓
Resolve Conflicts
        ↓
Replan When Necessary
        ↓
Synthesize
        ↓
Remember
        ↓
Research Intelligence
```

ResearchRadar doesn't just find research.

**It reasons over research, validates evidence, adapts to failures,
remembers previous work and turns information into intelligence.**

---

# 👥 Team TriX

### Bawake Bhakti — Team Leader
### Aditi Kadam
### Harshal Ingale

**ResearchRadar — AI-Powered Multi-Agent Research Intelligence Platform**
