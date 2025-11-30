import pandas as pd
import re
from src.utils import call_llm, load_data, load_config
from src.logger import logger

class EvaluatorAgent:
    def __init__(self):
        config = load_config()
        self.df = load_data(config['paths']['data'])
        self.prompt_path = "prompts/evaluator.md"

    def validate_hypothesis(self, hypothesis, data_summary):
        try:
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                prompt_template = f.read()
            
            summary_str = str(data_summary)
            if len(summary_str) > 2000:
                summary_str = summary_str[:2000] + "...(truncated)"

            system_prompt = prompt_template.replace("{hypothesis}", hypothesis)\
                                           .replace("{data_summary}", summary_str)
            
            generated_code = call_llm(
                system_prompt=system_prompt,
                user_message="Write Python code. Use the pre-defined variables 'df' and 'hypothesis'. Define 'validation_result' and 'explanation'.",
                json_mode=False
            )

            if not generated_code:
                return {"valid": False, "reason": "AI generation failed."}

            cleaned_code = generated_code.replace("```python", "").replace("```", "").strip()

            # Pass variables safely into scope to avoid string escape issues
            local_scope = {
                "df": self.df, 
                "pd": pd, 
                "re": re,
                "hypothesis": hypothesis,
                "data_summary": data_summary
            }
            
            try:
                exec(cleaned_code, {}, local_scope)
                
                raw_result = local_scope.get("validation_result", False)
                explanation = local_scope.get("explanation", "AI executed code but failed to define 'explanation'.")
                
                return {
                    "valid": bool(raw_result), 
                    "reason": str(explanation)
                }
            except Exception as e:
                logger.log("Evaluator", "code_crash", {"code": cleaned_code, "error": str(e)}, level="ERROR")
                return {"valid": False, "reason": f"Script Error: {str(e)}"}
            
        except Exception as e:
            return {"valid": False, "reason": f"System Error: {str(e)}"}