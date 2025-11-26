import json
from src.utils import call_llm
from src.logger import logger  

class PlannerAgent:
    def __init__(self):
        self.prompt_path = "prompts/planner.md"

    def load_prompt(self):
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def create_plan(self, user_query):
        print(f"🧠 Planner is thinking about: '{user_query}'...")
        
        logger.log("Planner", "start", {"query": user_query})
        
        system_prompt = self.load_prompt()
        
        response_text = call_llm(
            system_prompt=system_prompt,
            user_message=f"User Query: {user_query}",
            json_mode=True
        )

        if response_text:
            try:
                clean_text = response_text.replace("```json", "").replace("```", "").strip()
                plan = json.loads(clean_text)
                
                logger.log("Planner", "success", {"plan_steps": len(plan.get('analysis_plan', []))})
                return plan
            except json.JSONDecodeError as e:
                print("❌ Error: Planner returned invalid JSON.")
                logger.log("Planner", "error", {"raw_response": response_text, "error": str(e)})
                return None
        
        logger.log("Planner", "fail", {"reason": "No response from LLM"})
        return None