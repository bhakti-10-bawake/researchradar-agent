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
1. 🤖 Agentic Reasoning

ResearchRadar follows an adaptive:

Observe → Reason → Decide → Act → Evaluate → Replan

loop.

The agent determines what information is required, selects
appropriate tools, observes their results and evaluates whether
additional research is required.

This allows the system to move beyond a fixed search workflow.

Status: ✅ Implemented

2. 🛠️ Tool Calling

ResearchRadar integrates multiple external research and intelligence
sources:

arXiv API
OpenAlex API
Crossref API
Semantic Scholar API
Google News RSS
GDELT API

Tools are selected according to the research objective rather than
blindly calling every available API.

The system also supports fallback behavior when an external tool
fails or becomes unavailable.

Status: ✅ Implemented

3. 🤝 Multi-Agent Architecture

ResearchRadar uses specialized agents with clearly defined
responsibilities.

Agent	Responsibility
Orchestrator	Coordinates the research mission
Planner	Decomposes objectives and selects tools
Research Agent	Collects external evidence
Evidence Judge	Evaluates evidence and detects conflicts
Self-Evaluator	Evaluates mission quality
Strategy Agent	Converts evidence into strategic intelligence
Memory Agent	Stores and recalls previous research

Agents collaborate through shared structured state.

Status: ✅ Implemented

4. 🧠 Context & Memory Management

ResearchRadar maintains both short-term task context and persistent
research memory.

Short-Term Context

The shared research state can contain:

Research topic
Objective
Competitors
Selected tools
Research findings
Evidence scores
Conflicting evidence
Confidence
Iteration count
Resource budget
Execution trace
Strategy results
Long-Term Memory

Previous research scans are persisted and can influence future
research missions.

Example:

Previous Scan → HIGH signal

Current Scan → MEDIUM signal

              ↓

Strategy Agent receives previous context
and can reason about changes over time.

Status: ✅ Implemented

5. 🧩 Agent Framework — LangGraph

ResearchRadar uses LangGraph as its agentic framework.

LangGraph was selected because ResearchRadar requires stateful,
conditional and iterative execution rather than a simple fixed
pipeline.

The framework supports the following capabilities:

✅ Dynamic planning
✅ Multi-agent orchestration
✅ Conditional routing
✅ Parallel execution
✅ Shared state
✅ Checkpointed execution context
✅ Autonomous replanning
✅ Failure recovery
✅ Tool fallback
✅ Conflicting-evidence resolution
✅ Uncertainty-aware decisions
✅ Resource-aware execution
✅ Self-evaluation
✅ Hypothesis verification
✅ Memory-based reasoning
✅ Loop/deadlock protection
✅ Adaptive task decomposition
🔄 Dynamic Planning & Conditional Routing

ResearchRadar does not assume that every research objective requires
the same workflow.

The planner determines which research dimensions are required and
selects appropriate tools.

Example:

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

This allows the system to adapt its execution according to the
mission state.

⚡ Parallel Execution

Independent research sources can be queried as parallel research
branches.

                 Research Mission
                       ↓
          ┌────────────┼────────────┐
          ↓            ↓            ↓
        arXiv       OpenAlex     Crossref
          ↓            ↓            ↓
       Semantic     News RSS      GDELT
       Scholar
          └────────────┼────────────┘
                       ↓
                Evidence Judge

The collected evidence is then combined into the shared research
state.

🗃️ Shared State

Agents communicate using a shared research state.

Important state information includes:

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

This allows each agent to build upon the work of other agents.

🛡️ Failure Recovery & Tool Fallback

External APIs can fail due to rate limits, timeouts or temporary
unavailability.

During testing, ResearchRadar encountered failures including:

Semantic Scholar → HTTP 429 Too Many Requests

GDELT → HTTP 429 Too Many Requests

GDELT → Connection Timeout

Instead of terminating the complete research mission, the system
records the failure and continues using available evidence and
fallback sources.

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
⚖️ Conflicting-Evidence Resolution

ResearchRadar explicitly detects conflicting evidence.

The Evidence Judge evaluates supporting and limiting signals rather
than assuming every source agrees.

Example:

Supporting signals: 1
Limiting signals:   4

        ↓

Mixed evidence detected
        ↓
Confidence reduced
        ↓
Binary conclusion avoided

This allows the final result to communicate uncertainty instead of
hiding it.

📊 Uncertainty-Aware Decisions

ResearchRadar considers:

Evidence strength
Evidence count
Conflicting signals
Confidence
Risks
Limitations

The final system can produce signals such as:

HIGH
MEDIUM
LOW
WATCH CLOSELY

instead of presenting uncertain research as absolute fact.

💰 Resource-Aware Execution

Agentic systems can potentially consume unlimited tools and
iterations.

ResearchRadar therefore uses execution constraints such as:

Maximum iterations
Tool budget
Evidence limits
Completion checks

These constraints help prevent:

Infinite loops
Excessive API usage
Unnecessary tool calls
Uncontrolled agent execution
🧪 Self-Evaluation

The Self-Evaluator reviews the mission after evidence collection.

It considers factors such as:

Evidence quality
Tool failures
Conflicting evidence
Mission completeness
Confidence
Available resources

Example execution:

Evidence Judge
→ Scored evidence quality

Evidence Judge
→ Resolved conflicting evidence

Self-Evaluator
→ Evaluated mission quality

Strategy Agent
→ Generated final intelligence brief
🔬 Hypothesis Verification

ResearchRadar separates:

Evidence Discovery
        ↓
Evidence Evaluation
        ↓
Strategic Interpretation

This prevents the Strategy Agent from treating every retrieved
document as automatically valid evidence.

The Evidence Judge evaluates relevance and conflicting signals before
strategic synthesis.

🔁 Loop & Deadlock Protection

ResearchRadar uses:

Maximum iteration limits
Tool budgets
Execution state
Completion checks

to prevent uncontrolled agent loops.

Example:

Iteration 1
    ↓
Iteration 2
    ↓
Iteration 3
    ↓
STOP / FINALIZE
🧩 Adaptive Task Decomposition

Broad research objectives can be divided into multiple research
dimensions.

Example:

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

The final result combines these dimensions rather than presenting
them as unrelated search results.

🧠 Gemini Strategic Synthesis

Google Gemini is used by the Strategy Agent to transform evaluated
evidence into a higher-level intelligence brief.

The final result can contain:

Verdict
Summary
Emerging Trends
Risks
Recommendations
Competitor Context
Confidence
Evidence Count
Supporting Sources

The raw evidence remains available for verification.

📋 Intelligence Brief

The key output of ResearchRadar is an AI Intelligence Brief.

Instead of:

Research Paper 1
Research Paper 2
Research Paper 3
...
Research Paper 20

ResearchRadar produces:

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

This turns research retrieval into research intelligence.

🧨 Adversarial Testing

Task 5 was tested under adversarial conditions involving:

External API failures
API rate limiting
Timeouts
Conflicting evidence
Limited resource budgets
LLM/model availability issues

The system was able to continue the mission using fallback evidence,
evaluate uncertainty and generate a final intelligence assessment.

Example:

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
🖥️ User Interface

ResearchRadar provides a Streamlit-based research intelligence
dashboard.

The interface displays:

Research objective
Agent execution progress
Tool selection
Agent collaboration
Intelligence Brief
Confidence
Evidence count
Supporting sources
Memory context
Previous research scans

The UI makes the multi-agent execution visible rather than hiding
the agent architecture behind a single response.

🛠️ Technology Stack
Python — Core implementation
LangGraph — Agent orchestration
Google Gemini — Strategic synthesis
Streamlit — Web interface
arXiv API — Academic research
OpenAlex API — Scholarly discovery
Crossref API — Publication metadata
Semantic Scholar API — Research discovery
Google News RSS — Recent news intelligence
GDELT API — Global news/event intelligence
JSON — Persistent memory and data storage
Git/GitHub — Version control
📁 Project Structure
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
▶️ Running the Project
Install Dependencies
pip install -r requirements.txt
Configure Gemini

Set the Gemini API key as an environment variable:

$env:GEMINI_API_KEY="YOUR_API_KEY"
Test Agent Graph
python agent_graph.py
Run Streamlit Application
streamlit run app.py
🧪 Example Input
Analyze recent breakthroughs, manufacturing challenges,
competitor activity and commercial opportunities in
solid-state batteries for electric vehicles.

Example competitors:

Toyota, QuantumScape, Samsung SDI

ResearchRadar then dynamically researches the topic, evaluates the
evidence and generates an intelligence brief.

🏆 Why ResearchRadar?

Traditional research systems:

Query
  ↓
Search
  ↓
Research Papers
  ↓
Links

ResearchRadar:

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

ResearchRadar doesn't just find research.

It reasons over research, validates evidence, adapts to failures,
remembers previous work and turns information into intelligence.
Intelligence Brief
       ↓
Persistent Memory
