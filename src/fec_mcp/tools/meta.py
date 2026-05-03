
import json
import os
from typing import Optional
from ..server import mcp

_ALLOWED_DATA_FILES = {"help.json", "investigations.json", "glossary.json"}


def load_json_data(filename: str) -> dict:
    """Load JSON data from the data directory. Only allowlisted filenames are accepted."""
    if filename not in _ALLOWED_DATA_FILES:
        raise ValueError(
            f"Data file '{filename}' is not allowed. "
            f"Must be one of: {sorted(_ALLOWED_DATA_FILES)}"
        )
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), "data")
    file_path = os.path.join(data_dir, filename)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

@mcp.tool()
async def fec_help(topic: Optional[str] = None) -> str:
    """
    Get help on how to use this MCP server for campaign finance research.
    
    Args:
        topic: Specific topic (candidates, contributions, expenditures, pacs, filings, workflows, ids)
               Leave empty for general overview.
    
    Returns:
        Guidance and examples for using the FEC tools
    """
    data = load_json_data("help.json")
    
    if topic and topic.lower() in data:
        return data[topic.lower()]
    elif topic:
        topics = ", ".join([k for k in data.keys() if k != "general"])
        return f"Tópico '{topic}' não encontrado. Tópicos disponíveis: {topics}\n\n{data['general']}"
    else:
        return data["general"]

@mcp.tool()
async def suggest_investigation(focus: Optional[str] = None) -> str:
    """
    Get investigative journalism story ideas based on FEC data.
    
    Args:
        focus: Optional focus area (money_in_politics, dark_money, local, corporate, foreign)
    
    Returns:
        Story ideas and how to investigate them using this MCP
    """
    data = load_json_data("investigations.json")
    
    if focus and focus.lower() in data:
        return data[focus.lower()]
    
    return data["overview"]
