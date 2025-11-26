import json
import os
from src.utils import call_llm
from src.logger import logger

class InsightAgent:
    def __init__(self):
        self.prompt_path = "prompts/insight_generator.md"
        self.memory_path = "memory/short_term_memory.json"
        
        os.makedirs("memory", exist_ok=True)

    def _load_memory(self):
        """
        Loads past insights to prevent the AI from 'rediscovering' the same things.
        """
        if os.path.exists(self.memory_path):
            try:
                with open(self.memory_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []

    def save_to_memory(self, new_insights):
        """
        Saves valid insights. Keeps a rolling window of the last 20 items.
        """
        current_memory = self._load_memory()
        
        current_memory.extend(new_insights)
        
        if len(current_memory) > 20:
            current_memory = current_memory[-20:]
            
        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(current_memory, f, indent=2)
        
        logger.log("InsightAgent", "memory_updated", {"new_items": len(new_insights)})

    def generate_insights(self, user_query, data_summary):
        print(f"   ...Consulting memory & analyzing patterns...")
        
        past_insights = self._load_memory()
        
        if past_insights:
            past_context = "\n".join([f"- {i['hypothesis']} (Validated: {i.get('date', 'Unknown')})" for i in past_insights])
        else:
            past_context = "No previous history available."

        logger.log("InsightAgent", "context_loaded", {"memory_count": len(past_insights)})

        with open(self.prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()
        
        system_prompt = prompt_template.replace("{data_summary}", str(data_summary))\
                                       .replace("{user_query}", user_query)\
                                       .replace("{past_insights}", past_context)
        
        response = call_llm(
            system_prompt=system_prompt,
            user_message="Generate new insights based on data and history.",
            json_mode=True
        )

        if response:
            try:
                clean_text = response.replace("```json", "").replace("```", "").strip()
                result = json.loads(clean_text)
                
                logger.log("InsightAgent", "generated", {"count": len(result.get('insights', []))})
                return result
            except json.JSONDecodeError:
                logger.log("InsightAgent", "parse_error", {"response": response})
                print("❌ Error Parsing Insight JSON")
                return None
        return None