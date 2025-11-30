# 🧠 Agent Architecture & Data Flow

This document details the multi-agent orchestration logic used in the Kasparro Agentic Analyst. The system follows a **Planner-Evaluator-Creative** loop to ensure insights are not just generated, but mathematically validated before action is taken.

## 🔗 Visual Workflow

```mermaid
graph TD
    User[User Query] -->|Raw Text| Guard{Governance Layer}
    Guard -->|Sanitized Query| Planner(Planner Agent)
    Guard --x|Malicious Input| Block[Reject Request]
    
    Planner -->|Step-by-Step Plan| Data{Data Agent}
    
    subgraph "Analysis Loop"
    Data <-->|Pandas Execution| CSV[(Ad Dataset)]
    Data -->|Statistical Summary| Insight(Insight Agent)
    Insight <-->|Read/Write| Memory[(Short-Term Memory)]
    Insight -->|Hypothesis| Eval{Evaluator Agent}
    end
    
    Eval -->|Invalid / No Correlation| Insight
    Eval -->|Valid + Low Performance| Creative(Creative Agent)
    
    Creative -->|Ad Variations| Report[Final Report]
```

## 🤖 Agent Responsibilities
##🛡️ Governance Layer (New in V2)
##Role##: Security & Validation.

Function: Intercepts the user query before it reaches any agent. It sanitizes input to prevent injections and validates the CSV schema to ensure data integrity.

1. Planner Agent
Role: Strategic decomposition.

Function: It accepts high-level ambiguous queries (e.g., "Why is ROAS down?") and breaks them into logical sub-tasks.

Output: JSON-structured plan.

2. Data Agent (The Execution Layer)
Role: Safe code execution.

Function: It acts as the interface between the LLM and the raw CSV. It generates Python Pandas code dynamically to answer specific questions from the plan.

Safety: Uses a restricted local scope exec() environment.

3. Insight Agent (The Analyst)
Role: Pattern recognition & Hypothesis generation.

Function: Analyzes the statistical summary provided by the Data Agent. It looks for anomalies (e.g., High Spend + Low ROAS).

Memory: It checks memory/short_term_memory.json before running to ensure it doesn't "rediscover" insights found in previous runs.

4. Evaluator Agent (The Critic)
Role: Mathematical Validation.

Function: This is the logic gate. It takes a hypothesis from the Insight Agent and writes new Python code to test it against the data.

Logic:

If Actual Metric meets the threshold (e.g., ROAS < 4.0), it returns Valid: True.

If the data contradicts the hypothesis, it returns Valid: False.

5. Creative Agent (The Copywriter)
Role: Actionable Solutions.

Function: Triggered only when the Evaluator validates a negative performance issue. It uses the insight context to generate 3 distinct ad variations (Headlines + Body Copy).
