import json
import re
import time
from src.utils import call_llm
from src.logger import logger 

class CreativeAgent:
    def __init__(self):
        self.prompt_path = "prompts/creative_writer.md"

    def _load_prompt(self):
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def _extract_json(self, text):
        try:
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        json_pattern = re.compile(r'(\{[\s\S]*\})')
        match = json_pattern.search(text)
        if match:
            return json.loads(match.group(1))
        raise ValueError("No JSON found")

    def generate_copy(self, insight, current_message="Generic Brand Ad", max_retries=3):
        print(f"      🎨 Creative Agent is writing new ads (Retry Mode Active)...")
        logger.log("CreativeAgent", "start", {"insight": insight})
        
        base_prompt = self._load_prompt()
        system_prompt = base_prompt.replace("{insight}", insight).replace("{current_message}", current_message)
        user_message = "Generate new ad variations. Output ONLY JSON."
        
        for attempt in range(1, max_retries + 1):
            try:
                response = call_llm(system_prompt, user_message, json_mode=True)
                if not response: raise ValueError("Empty LLM response")

                parsed_data = self._extract_json(response)
                
                logger.log("CreativeAgent", "success", {"variations": len(parsed_data.get("variations", []))})
                return parsed_data

            except Exception as e:
                logger.log("CreativeAgent", "retry", {"attempt": attempt, "error": str(e)})
                user_message = f"Previous output invalid JSON. Error: {str(e)}. Return ONLY JSON."
                time.sleep(1)

        logger.log("CreativeAgent", "failed_all_retries", {})
        return None