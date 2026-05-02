
import sys
import os

# Only add to path if fec_mcp is not importable
try:
    import fec_mcp
except ImportError:
    # Add src to python path so we can import the package
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(current_dir, "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

from fec_mcp.main import main

if __name__ == "__main__":
    import sys
    print(f"Starting FEC MCP Server from {src_dir}...", file=sys.stderr)
    main()
