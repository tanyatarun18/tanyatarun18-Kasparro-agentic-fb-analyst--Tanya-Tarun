import pandas as pd
from src.utils import call_llm, load_data, load_config
from src.logger import logger 

class DataAgent:
    def __init__(self):
        config = load_config()
        self.df = load_data(config['paths']['data'])
        self.prompt_path = "prompts/data_analyst.md"

    def _load_prompt(self):
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def analyze(self, query):
        print(f"   ...Querying dataset...")
        logger.log("DataAgent", "received_query", {"query": query})
        
        system_prompt = self._load_prompt()
        
        generated_code = call_llm(
            system_prompt=system_prompt,
            user_message=f"Request: {query}",
            json_mode=False 
        )

        if not generated_code:
            logger.log("DataAgent", "error", {"reason": "LLM generation failed"})
            return "❌ Error: Code generation failed."

        cleaned_code = generated_code.replace("```python", "").replace("```", "").strip()
        
        logger.log("DataAgent", "code_generated", {"code": cleaned_code})
        
        local_scope = {"df": self.df, "pd": pd}
        
        try:
            exec(cleaned_code, {}, local_scope)
            
            if "result" in local_scope:
                result = local_scope["result"]
                logger.log("DataAgent", "execution_success", {"result_preview": str(result)[:200]})
                return result
            else:
                logger.log("DataAgent", "runtime_error", {"reason": "No 'result' variable found"})
                return "❌ Runtime Error: No 'result' variable defined."
                
        except Exception as e:
            logger.log("DataAgent", "execution_crash", {"error": str(e), "code": cleaned_code})
            return f"❌ Execution Error: {str(e)}"