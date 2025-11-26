import argparse
import json
import os
import datetime
from dotenv import load_dotenv

from src.agents.planner import PlannerAgent
from src.agents.data_agent import DataAgent
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator import EvaluatorAgent
from src.agents.creative_agent import CreativeAgent

from src.logger import logger

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
    
    md = f"#  Marketing Performance Analysis\n"
    md += f"**Date:** {date_str}\n\n"
    md += f"**Query:** *\"{query}\"*\n\n"
    
    md += "## 1. Executive Summary \n"
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
    parser = argparse.ArgumentParser(description="Kasparro Agentic Analyst CLI")
    parser.add_argument("query", type=str, nargs="?", default="Why did ROAS drop last week?", help="The analytical question to resolve.")
    args = parser.parse_args()

    print(f"\n🤖 Agentic Analyst | Processing: '{args.query}'")
    print("="*60)
    
    logger.log("Orchestrator", "start", {"query": args.query})

    planner = PlannerAgent()
    plan = planner.create_plan(args.query)
    if not plan:
        print("❌ Analysis aborted: Planner failed.")
        return
    print(f"📝 Plan Established: {len(plan.get('analysis_plan', []))} steps.")

    data_agent = DataAgent()
    data_summary = data_agent.analyze(args.query)
    
    if isinstance(data_summary, str) and "Error" in data_summary:
        print(f"❌ Analysis aborted: {data_summary}")
        return
    print(f"📊 Data Retrieved Successfully.")

    insight_agent = InsightAgent()
    insights_raw = insight_agent.generate_insights(args.query, data_summary)
    
    if not insights_raw or 'insights' not in insights_raw:
        print(" No actionable insights found.")
        return

    evaluator = EvaluatorAgent()
    creative_agent = CreativeAgent()
    
    validated_insights = []
    final_creatives = []
    
    memory_buffer = []

    print("\n  Validating Hypotheses...")
    for item in insights_raw['insights']:
        validation = evaluator.validate_hypothesis(item['hypothesis'], data_summary)
        
        record = {**item, "validation": validation}
        validated_insights.append(record)
        
        status = "Valid" if validation['valid'] else "Invalid"
        print(f"   -> [{status}] {item['hypothesis'][:50]}...")

        if validation['valid']:
            memory_buffer.append({
                "hypothesis": item['hypothesis'],
                "query": args.query,
                "date": str(datetime.date.today()),
                "validation_reason": validation['reason']
            })

            print("      🎨 Generating creative variations...")
            new_copy = creative_agent.generate_copy(item['hypothesis'])
            if new_copy:
                final_creatives.append({
                    "related_hypothesis": item['hypothesis'],
                    "recommendations": new_copy
                })

    if memory_buffer:
        insight_agent.save_to_memory(memory_buffer)
        print(f"\n🧠 [Memory] Saved {len(memory_buffer)} new valid insights to memory/short_term_memory.json")
        logger.log("Orchestrator", "memory_save", {"count": len(memory_buffer)})

    print("\n💾 Saving Artifacts...")
    
    save_json_artifact(validated_insights, "insights.json")
    save_json_artifact(final_creatives, "creatives.json")
    
    report_content = generate_markdown(args.query, data_summary, validated_insights, final_creatives)
    with open("reports/report.md", "w", encoding="utf-8") as f:
        f.write(report_content)

    logger.save_logs()

    print(f"✅ Workflow Complete. Check 'reports/' and 'logs/' folders.")

if __name__ == "__main__":
    main() 
