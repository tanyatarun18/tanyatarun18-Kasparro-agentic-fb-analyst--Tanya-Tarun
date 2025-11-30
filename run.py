import argparse
import json
import os
import datetime
from dotenv import load_dotenv

# Agent Imports
from src.agents.planner import PlannerAgent
from src.agents.data_agent import DataAgent
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator import EvaluatorAgent
from src.agents.creative_agent import CreativeAgent

# Infrastructure Imports
from src.logger import logger
from src.governance import InputSanitizer
from src.exceptions import SecurityError

load_dotenv()

def save_json_artifact(data, filename, folder="reports"):
    """Saves structured data to the reports directory with UTF-8 encoding."""
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def generate_markdown(query, data_summary, insights, creatives):
    """Generates a formatted human-readable report."""
    date_str = datetime.date.today().strftime("%B %d, %Y")
    
    md = f"# 🚀 Marketing Performance Analysis\n"
    md += f"**Date:** {date_str}\n\n"
    md += f"**Query:** *\"{query}\"*\n\n"
    
    md += "## 1. Executive Summary 📊\n"
    # Pretty print data summary, truncating if too long
    summary_str = json.dumps(data_summary, indent=2)
    if len(summary_str) > 3000:
        summary_str = summary_str[:3000] + "\n... (data truncated for brevity)"
    md += f"```json\n{summary_str}\n```\n\n"
    
    md += "## 2. Strategic Insights & Validation 🔍\n"
    for item in insights:
        status_icon = "✅" if item['validation']['valid'] else "❌"
        md += f"### {status_icon} Hypothesis: {item['hypothesis']}\n"
        md += f"- **Confidence:** {item.get('confidence', 'N/A')}\n"
        md += f"- **Evidence:** {item.get('evidence', 'N/A')}\n"
        md += f"- **Validation Result:** {item['validation']['reason']}\n\n"
    
    md += "## 3. Creative Optimization 🎨\n"
    if creatives:
        for c in creatives:
            md += f"**Context:** Based on *{c['related_hypothesis']}*\n\n"
            for var in c['recommendations'].get('variations', []):
                md += f"**Option: {var.get('headline', 'Headline')}**\n"
                md += f"> {var.get('primary_text', 'Body copy...')}\n\n"
                md += f"*Reasoning: {var.get('reasoning', '')}*\n\n"
            md += "---\n"
    else:
        md += "_No creative rework required based on current validation results._\n"
        
    return md

def main():
    # CLI Argument Setup
    parser = argparse.ArgumentParser(description="Kasparro Agentic Analyst CLI")
    parser.add_argument("query", type=str, nargs="?", default="Why did ROAS drop last week?", help="The analytical question to resolve.")
    args = parser.parse_args()

    # --- SECURITY: Input Sanitization ---
    try:
        clean_query = InputSanitizer.clean_query(args.query)
    except SecurityError as e:
        print(f"⛔ Security Alert: {e}")
        logger.log("Orchestrator", "security_block", {"error": str(e), "input": args.query})
        return

    print(f"\n🤖 Agentic Analyst | Processing: '{clean_query}'")
    print("="*60)
    
    # Start Global Log
    logger.log("Orchestrator", "start", {"query": clean_query})

    # --- Phase 1: Planning ---
    planner = PlannerAgent()
    plan = planner.create_plan(clean_query)
    if not plan:
        print("❌ Analysis aborted: Planner failed.")
        return
    print(f"📝 Plan Established: {len(plan.get('analysis_plan', []))} steps.")

    # --- Phase 2: Data Retrieval ---
    data_agent = DataAgent()
    data_summary = data_agent.analyze(clean_query)
    
    if isinstance(data_summary, str) and "Error" in data_summary:
        print(f"❌ Analysis aborted: {data_summary}")
        return
    print(f"📊 Data Retrieved Successfully.")

    # --- Phase 3: Insight Generation ---
    insight_agent = InsightAgent()
    insights_raw = insight_agent.generate_insights(clean_query, data_summary)
    
    if not insights_raw or 'insights' not in insights_raw:
        print("⚠️ No actionable insights found.")
        return

    # --- Phase 4: Validation & Creative Loop ---
    evaluator = EvaluatorAgent()
    creative_agent = CreativeAgent()
    
    validated_insights = []
    final_creatives = []
    
    # Buffer to store valid insights for long-term memory
    memory_buffer = []

    print("\n⚖️  Validating Hypotheses...")
    for item in insights_raw['insights']:
        # Validate
        validation = evaluator.validate_hypothesis(item['hypothesis'], data_summary)
        
        # Merge validation result
        record = {**item, "validation": validation}
        validated_insights.append(record)
        
        status = "Valid" if validation['valid'] else "Invalid"
        print(f"   -> [{status}] {item['hypothesis'][:50]}...")

        # LOGIC: If Valid (True), add to memory & generate creatives
        if validation['valid']:
            # 1. Add to Memory Buffer
            memory_buffer.append({
                "hypothesis": item['hypothesis'],
                "query": clean_query,
                "date": str(datetime.date.today()),
                "validation_reason": validation['reason']
            })

            # 2. Trigger Creative Agent
            print("      🎨 Generating creative variations...")
            new_copy = creative_agent.generate_copy(item['hypothesis'])
            if new_copy:
                final_creatives.append({
                    "related_hypothesis": item['hypothesis'],
                    "recommendations": new_copy
                })

    # --- Phase 5: Memory Storage ---
    if memory_buffer:
        insight_agent.save_to_memory(memory_buffer)
        print(f"\n🧠 [Memory] Saved {len(memory_buffer)} new valid insights to memory/short_term_memory.json")
        logger.log("Orchestrator", "memory_save", {"count": len(memory_buffer)})

    # --- Phase 6: Deliverables ---
    print("\n💾 Saving Artifacts...")
    
    # 1. Save JSONs
    save_json_artifact(validated_insights, "insights.json")
    save_json_artifact(final_creatives, "creatives.json")
    
    # 2. Save Report
    report_content = generate_markdown(clean_query, data_summary, validated_insights, final_creatives)
    with open("reports/report.md", "w", encoding="utf-8") as f:
        f.write(report_content)

    # 3. Save Logs (Trace)
    logger.save_logs()

    print(f"✅ Workflow Complete. Check 'reports/' and 'logs/' folders.")

if __name__ == "__main__":
    main()