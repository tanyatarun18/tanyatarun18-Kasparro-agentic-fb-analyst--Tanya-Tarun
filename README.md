# 🤖 Kasparro Agentic Facebook Analyst

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![AI Model](https://img.shields.io/badge/Model-Gemini%20Flash-orange)](https://deepmind.google/technologies/gemini/flash/)
[![Architecture](https://img.shields.io/badge/Architecture-Planner%20Evaluator%20Loop-green)](./agent_graph.md)

An autonomous multi-agent system that acts as a **Facebook Marketing Analyst**. It ingests raw ad performance data, diagnoses ROAS fluctuations, validates hypotheses using statistical tests, and generates creative ad copy solutions for underperforming campaigns.

---

## 🧠 Architecture

The system implements a **Planner-Evaluator-Creative Loop** to ensure high-quality, grounded insights. Unlike simple RAG pipelines, this system uses an **Evaluator Agent** to mathematically validate every hypothesis before making recommendations.

**[📄 Click here to view the detailed Agent Graph & Data Flow](./agent_graph.md)**

### Agent Roles

| Agent | Role | Mechanism |
| :--- | :--- | :--- |
| **Planner** | **Strategist** | Decomposes abstract user queries (e.g., "Why is ROAS down?") into specific analytical steps. |
| **Data Agent** | **Execution** | Generates and executes Python Pandas code safely to extract metrics from the raw CSV. |
| **Insight Agent** | **Analyst** | Identifies patterns and generates hypotheses (e.g., "Ad fatigue in Men's Boxers campaign"). Includes Short-Term Memory. |
| **Evaluator** | **Critic** | Writes statistical validation code to prove/disprove hypotheses. Rejects hallucinations. |
| **Creative** | **Copywriter** | Generates new headlines/body copy for validated underperforming ads using proven marketing frameworks. |

---

## 🚀 Key Features (Production V2)

### 🛡️ Security & Governance
* **Input Sanitization:** Middleware intercepts and sanitizes user queries to prevent injection attacks or malicious commands.
* **Schema Validation:** Enforces strict data contracts. The system validates the CSV structure (columns, data types) before processing to prevent runtime hallucinations.

### 🔍 Observability & Logging
* **Structured JSON Logs:** Every execution generates a trace file in `logs/` capturing agent inputs, outputs, code generation, and execution time (latency tracking).
* **Failure Mapping:** Specific error types (`DataValidationError`, `SecurityError`, `LLMGenerationError`) are logged for easier debugging.

### 🧠 Resilience & Memory
* **Self-Correction:** Agents detect JSON parsing failures and API rate limits (429), automatically retrying with corrected prompts or backoff strategies.
* **Short-Term Memory:** Validated insights are stored in `memory/short_term_memory.json`. The system consults this history to avoid re-discovering the same issues in subsequent runs.

---

## 📂 Project Structure

```text
kasparro-agentic-fb-analyst/
├── config/
│   └── config.yaml             # Thresholds, model settings, and paths
├── data/
│   └── synthetic_fb_ads...csv  # The raw marketing dataset
├── logs/
│   └── trace_TIMESTAMP.json    # Full execution traces with latency & errors
├── memory/
│   └── short_term_memory.json  # Stores valid insights for iterative learning
├── prompts/                    # Agent System Prompts (Markdown)
│   ├── creative_writer.md
│   ├── data_analyst.md
│   ├── evaluator.md
│   ├── insight_generator.md
│   └── planner.md
├── reports/                    # Final Deliverables (Timestamped Folders)
│   └── run_TIMESTAMP/
│       ├── creatives.json      # Generated ad copy variations
│       ├── insights.json       # Structured hypotheses & validation results
│       └── report.md           # Human-readable summary
├── src/
│   ├── agents/                 # Individual Agent Logic
│   ├── exceptions.py           # Custom error classes (Security, Data, etc.)
│   ├── governance.py           # Input Sanitizer & Schema Validator
│   ├── logger.py               # Singleton JSON logger
│   ├── utils.py                # Data loading & LLM API wrappers
└── run.py                      # Main entry point & Orchestrator
```

## 🛠 Setup & Installation
## Prerequisites -                                                                                                                                                                                                 
Python 3.9+                                                                                                                                                                                                        
A Google Gemini API Key (Free Tier is supported)

## Installation - 
1. Clone the repository:
git clone [https://github.com/tanyatarun18/tanyatarun18-Kasparro-agentic-fb-analyst--Tanya-Tarun.git](https://github.com/tanyatarun18/tanyatarun18-Kasparro-agentic-fb-analyst--Tanya-Tarun.git)                    
cd tanyatarun18-Kasparro-agentic-fb-analyst--Tanya-Tarun

2. Install dependencies:                                                                                                                                                                                           
make setup                                                                                                                                                                                                        
OR: pip install -r requirements.txt

3. Configure Environment:
Create a .env file in the root directory:                                                                                                                                                                         
GEMINI_API_KEY=your_actual_api_key_here


## 🏃‍♂ Usage
You can run the analyst using the Makefile shortcuts or direct Python commands.

1. Default Analysis                                                                                                                                                                                                
Runs the standard diagnosis: "Why did ROAS drop last week?"                                                                                                                                                        
make run                                                                                                                                                                                                          
OR: python run.py

2. Custom Query                                                                                                                                                                                                    
Ask specific questions about your data.                                                                                                                                                                            
make query q="Which creative type has the highest CTR?"                                                                                                                                                            
OR: python run.py "Which creative type has the highest CTR?"

3. Resilience Testing
   
    Run the test suite to verify security and schema guards.

    python test_resilience.py


## ⚙ Configuration
You can tweak thresholds and model settings in config/config.yaml:

system:                                                                                                                                                                                                            
  model: "gemini-2.0-flash"                                                                                                                                     
  temperature: 0.2                                  

thresholds:                                                                                                                                                                                                        
  roas_drop_alert: 0.2                                                                                                                                 
  min_confidence: 0.7 
