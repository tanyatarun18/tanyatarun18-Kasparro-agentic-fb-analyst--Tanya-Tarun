import os
import time
import pandas as pd
import yaml
import google.generativeai as genai
from dotenv import load_dotenv
from src.governance import SchemaValidator
from src.exceptions import ConfigurationError, DataValidationError

load_dotenv()

if not os.getenv("GEMINI_API_KEY"):
    raise ConfigurationError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def load_config():
    try:
        with open("config/config.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}

def load_data(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(filepath)
        
        df.columns = [c.strip().lower().replace(' ', '_').replace('-', '_') for c in df.columns]
        
        column_map = {
            'ad_name': 'creative_name',
            'creative': 'creative_name',
            'creative_message': 'creative_name',
            'ad_set_name': 'adset_name',
            'campaign': 'campaign_name'
        }
        df.rename(columns=column_map, inplace=True)

        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')

        numeric_cols = ['spend', 'impressions', 'clicks', 'purchases', 'revenue', 'roas']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        text_cols = ['campaign_name', 'adset_name', 'creative_name', 'creative_type']
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).apply(lambda x: x.encode('ascii', 'ignore').decode('ascii'))

        SchemaValidator.validate(df)

        return df

    except DataValidationError as e:
        print(f"Data Validation Failed: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

def call_llm(system_prompt, user_message, model=None, json_mode=False):
    config = load_config()
    target_model = model or config.get('system', {}).get('model', 'gemini-2.0-flash')
    
    generation_config = {"temperature": 0.2}
    if json_mode:
        generation_config["response_mime_type"] = "application/json"

    model_instance = genai.GenerativeModel(
        model_name=target_model,
        system_instruction=system_prompt,
        generation_config=generation_config
    )

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model_instance.generate_content(user_message)
            return response.text

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "Resource exhausted" in error_str:
                time.sleep(20)
            else:
                print(f"LLM API Error: {e}")
                return None
    
    return None