#  Kasparro Agentic Facebook Analyst

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![AI Model](https://img.shields.io/badge/Model-Gemini%20Flash-orange)](https://deepmind.google/technologies/gemini/flash/)
[![Architecture](https://img.shields.io/badge/Architecture-Planner%20Evaluator%20Loop-green)](./agent_graph.md)

An autonomous multi-agent system that acts as a *Facebook Marketing Analyst*. It ingests raw ad performance data, diagnoses ROAS fluctuations, validates hypotheses using statistical tests, and generates creative ad copy solutions for underperforming campaigns.

---

## 🧠 Architecture

The system implements a *Planner-Evaluator-Creative Loop* to ensure high-quality, grounded insights. Unlike simple RAG pipelines, this system uses an *Evaluator Agent* to mathematically validate every hypothesis before making recommendations.

*[📄 Click here to view the detailed Agent Graph & Data Flow](./agent_graph.md)*

### Agent Roles

| Agent | Role | Mechanism |
| :--- | :--- | :--- |
| *Planner* | *Strategist* | Decomposes abstract user queries (e.g., "Why is ROAS down?") into specific analytical steps. |
| *Data Agent* | *Execution* | Generates and executes Python Pandas code safely to extract metrics from the raw CSV. |
| *Insight Agent* | *Analyst* | Identifies patterns and generates hypotheses (e.g., "Ad fatigue in Men's Boxers campaign"). Includes Short-Term Memory. |
| *Evaluator* | *Critic* | Writes statistical validation code to prove/disprove hypotheses. Rejects hallucinations. |
| *Creative* | *Copywriter* | Generates new headlines/body copy for validated underperforming ads using proven marketing frameworks. |

---

## 📂 Project Structure

text
kasparro-agentic-fb-analyst/
├── config/
│   └── config.yaml             # Thresholds, model settings, and paths
├── data/
│   └── synthetic_fb_ads...csv  # The raw marketing dataset
├── logs/
│   └── trace_TIMESTAMP.json    # Full execution traces for debugging
├── memory/
│   └── short_term_memory.json  # Stores valid insights for iterative learning
├── prompts/                    # Agent System Prompts (Markdown)
│   ├── creative_writer.md
│   ├── data_analyst.md
│   ├── evaluator.md
│   ├── insight_generator.md
│   └── planner.md
├── reports/                    # Final Deliverables
│   ├── creatives.json          # Generated ad copy variations
│   ├── insights.json           # Structured hypotheses & validation results
│   └── report.md               # Human-readable summary
├── src/
│   ├── agents/                 # Logic for individual agents (Planner, Data, etc.)
│   ├── logger.py               # Centralized JSON logging system
│   ├── orchestrator.py         # (Legacy) Logic flow components
│   └── utils.py                # Data loading & LLM API wrappers
├── agent_graph.md              # Mermaid.js architecture diagram
├── check_models.py             # Utility to verify API model access
├── Makefile                    # Shortcut commands (setup, run, clean)
├── requirements.txt            # Python dependencies
└── run.py                      # Main entry point for the application


## Key Features
Self-Correcting Logic: The system detects API rate limits (429 Errors) and JSON parsing failures, automatically retrying with corrected prompts.

Short-Term Memory: Stores validated insights in memory/short_term_memory.json to prevent re-discovering the same issues in subsequent runs.

Math-Backed Validation: Does not trust the LLM's intuition. It forces the LLM to write Python code to calculate correlation or thresholds (e.g., ROAS < 4.0) before accepting an insight.

Structured Observability: Every step of the reasoning chain is logged to logs/trace_TIMESTAMP.json for debugging and audit trails.

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

3. Custom Query                                                                                                                                                                                                    
Ask specific questions about your data.                                                                                                                                                                            
make query q="Which creative type has the highest CTR?"                                                                                                                                                            
OR: python run.py "Which creative type has the highest CTR?"


## ⚙ Configuration
You can tweak thresholds and model settings in config/config.yaml:

system:                                                                                                                                                                                                            
  model: "gemini-2.0-flash"                                                                                                                                     
  temperature: 0.2                                  

thresholds:                                                                                                                                                                                                        
  roas_drop_alert: 0.2                                                                                                                                 
  min_confidence: 0.7
