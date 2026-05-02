import os
import json
from pathlib import Path

# Cache for locales
_locales = {}

def load_locales():
    """Load locales from JSON files"""
    global _locales
    if _locales:
        return
    
    locales_dir = Path(__file__).parent / "locales"
    
    if not locales_dir.exists():
        return
        
    for file_path in locales_dir.glob("*.json"):
        lang = file_path.stem
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                _locales[lang] = json.load(f)
        except Exception:
            pass

def get_text(key: str, **kwargs) -> str:
    """
    Get a translated string based on the FEC_MCP_LANG environment variable.
    Defaults to 'en'.
    """
    if not _locales:
        load_locales()
        
    lang = os.getenv("FEC_MCP_LANG", "en").lower()
    
    # Fallback to English if language not found
    if lang not in _locales:
        lang = "en"
        
    # Get text from selected language or fallback to English
    text = _locales.get(lang, {}).get(key)
    if not text and lang != "en":
        text = _locales.get("en", {}).get(key)
        
    # If key is still missing, return the key itself
    if not text:
        return key
        
    # Format the string with kwargs if provided
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
            
    return text
