import pandas as pd
from src.utils import call_llm, load_data, load_config
from src.logger import logger 

class EvaluatorAgent:
    def __init__(self):
        config = load_config()
        self.df = load_data(config['paths']['data'])
        self.prompt_path = "prompts/evaluator.md"

    def validate_hypothesis(self, hypothesis, data_summary):
        logger.log("Evaluator", "start_check", {"hypothesis": hypothesis})
        
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
                user_message="Write Python code. Define 'validation_result' and 'explanation'.",
                json_mode=False
            )

            if not generated_code:
                logger.log("Evaluator", "fail", {"reason": "No code generated"})
                return {"valid": False, "reason": "AI generation failed."}

            cleaned_code = generated_code.replace("```python", "").replace("```", "").strip()
            
            logger.log("Evaluator", "code_generated", {"code": cleaned_code})

            local_scope = {"df": self.df, "pd": pd}
            
            try:
                exec(cleaned_code, {}, local_scope)
                
                raw_result = local_scope.get("validation_result", False)
                explanation = local_scope.get("explanation", "No explanation defined.")
                
                result_bool = bool(raw_result)
                
                logger.log("Evaluator", "result", {"valid": result_bool, "reason": explanation})
                return {"valid": result_bool, "reason": str(explanation)}
                
            except Exception as e:
                logger.log("Evaluator", "code_crash", {"error": str(e)})
                return {"valid": False, "reason": f"Script Error: {str(e)}"}
            
        except Exception as e:
            return {"valid": False, "reason": f"System Error: {str(e)}"} 
