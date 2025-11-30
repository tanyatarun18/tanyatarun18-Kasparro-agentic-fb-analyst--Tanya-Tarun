import re
import pandas as pd
from src.exceptions import DataValidationError, SecurityError

class SchemaValidator:
    REQUIRED_COLUMNS = {
        'campaign_name', 
        'adset_name', 
        'creative_name', 
        'spend', 
        'impressions', 
        'clicks', 
        'ctr', 
        'purchases', 
        'revenue', 
        'roas'
    }

    @classmethod
    def validate(cls, df: pd.DataFrame):
        if df.empty:
            raise DataValidationError("Dataset is empty")

        missing = cls.REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise DataValidationError(f"Missing required columns: {missing}")

        if df['spend'].dtype not in ['float64', 'int64']:
            raise DataValidationError("Column 'spend' must be numeric")
            
        if df['roas'].dtype not in ['float64', 'int64']:
            raise DataValidationError("Column 'roas' must be numeric")

        return True

class InputSanitizer:
    MAX_LENGTH = 200
    FORBIDDEN_PATTERNS = [
        r"<script>", 
        r"javascript:", 
        r"DROP TABLE", 
        r"DELETE FROM",
        r"system:",
        r"ignore previous instructions"
    ]

    @classmethod
    def clean_query(cls, query: str) -> str:
        if not query or not isinstance(query, str):
            raise SecurityError("Invalid query format")

        cleaned = query.strip()
        
        if len(cleaned) > cls.MAX_LENGTH:
            raise SecurityError(f"Query too long. Max {cls.MAX_LENGTH} characters")

        for pattern in cls.FORBIDDEN_PATTERNS:
            if re.search(pattern, cleaned, re.IGNORECASE):
                raise SecurityError(f"Potential malicious input detected: {pattern}")

        cleaned = re.sub(r'[^\w\s\?.,\-]', '', cleaned)
        
        return cleaned