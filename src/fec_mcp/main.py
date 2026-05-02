
from .server import mcp
from .logging_config import setup_logging

# Import all tools, resources, and prompts to register them with FastMCP
import fec_mcp.tools.candidates
import fec_mcp.tools.contributions
import fec_mcp.tools.expenses
import fec_mcp.tools.filings
import fec_mcp.tools.meta
import fec_mcp.tools.search

import fec_mcp.resources.reference

import fec_mcp.prompts.investigation

def main():
    """Main entry point for the MCP server"""
    setup_logging()
    mcp.run()

if __name__ == "__main__":
    main()
