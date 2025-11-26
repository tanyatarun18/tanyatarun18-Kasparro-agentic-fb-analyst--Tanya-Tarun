import os
import time
import pandas as pd
import yaml
import google.generativeai as genai
from dotenv import load_dotenv

# Init environment
load_dotenv()
if not os.getenv("GEMINI_API_KEY"):
    print("⚠️  WARNING: GEMINI_API_KEY not found in .env file.")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def load_config():
    """Simple config loader."""
    try:
        with open("config/config.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("❌ Config file not found.")
        return {}

def load_data(filepath):
    """
    Loads data and handles the messy column names.
    """
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(filepath)
        
        # Standardize columns: lowercase, no spaces
        df.columns = [c.strip().lower().replace(' ', '_').replace('-', '_') for c in df.columns]
        
        # Fallback mapping
        column_map = {
            'ad_name': 'creative_name',
            'creative': 'creative_name',
            'creative_message': 'creative_name',
            'ad_set_name': 'adset_name',
            'campaign': 'campaign_name'
        }
        df.rename(columns=column_map, inplace=True)

        # Type enforcement
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')

        numeric_cols = ['spend', 'impressions', 'clicks', 'purchases', 'revenue', 'roas']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Fix encoding issues
        text_cols = ['campaign_name', 'adset_name', 'creative_name', 'creative_type']
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).apply(lambda x: x.encode('ascii', 'ignore').decode('ascii'))

        return df

    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return pd.DataFrame()

def call_llm(system_prompt, user_message, model=None, json_mode=False):
    """
    Wrapper for GenAI calls with AUTOMATIC RETRY for 429 Errors.
    """
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

    # --- RETRY LOGIC (Senior Engineer Feature) ---
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model_instance.generate_content(user_message)
            return response.text

        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "Resource exhausted" in error_str:
                print(f"   ⏳ Hit Rate Limit (429). Sleeping for 20s before retry {attempt+1}/{max_retries}...")
                time.sleep(20)  # Wait for quota to reset
            else:
                print(f"❌ LLM API Error: {e}")
                return None
    
    print("❌ Failed after max retries.")
    return None 
