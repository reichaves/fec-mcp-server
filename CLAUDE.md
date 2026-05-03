# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (dev includes pytest, ruff, respx)
pip install -r requirements.txt
pip install -e ".[dev]"

# Run all tests
pytest tests/

# Run a single test
pytest tests/test_server.py::test_search_candidates

# Run tests excluding slow ones
pytest tests/ -m "not slow"

# Lint
ruff check src/

# Start the MCP server directly
python start_server.py
```

## Environment

Requires a `.env` file with:
```
FEC_API_KEY=your_key_here
```

Optional override: `FEC_API_BASE_URL` (defaults to `https://api.open.fec.gov/v1`).

## Architecture

This is a **FastMCP server** that wraps the [OpenFEC API](https://api.open.fec.gov/developers/) and exposes it as MCP tools, resources, and prompts for AI assistants (e.g., Claude Desktop).

### Registration pattern

FastMCP uses a decorator-based registration system. The central `mcp` instance lives in [src/fec_mcp/server.py](src/fec_mcp/server.py). **All tool/resource/prompt modules must be explicitly imported in [src/fec_mcp/main.py](src/fec_mcp/main.py)** to register them — FastMCP only knows about decorated items that have been imported. Adding a new module without importing it in `main.py` means it won't be available to the MCP client.

### Two FECClient implementations

There are two client files — this is intentional (the newer one is `client.py`):

- [src/fec_mcp/client.py](src/fec_mcp/client.py) — active client used by `context.py`. Has per-endpoint timeout tuning (slow endpoints like schedule_a/b/e get 120s), retry/backoff logic for 429/503, and progressive sleep on timeout.
- [src/fec_mcp/fec_client.py](src/fec_mcp/fec_client.py) — older client, 30s fixed timeout, no retry. Not used by the server.

The singleton `fec` in [src/fec_mcp/context.py](src/fec_mcp/context.py) is what all tools import and call.

### Tools (`src/fec_mcp/tools/`)

Each file wraps `FECClient` methods and returns JSON strings. Tools always catch all exceptions and return `{"error": ...}` rather than raising.

| File | MCP tools exposed |
|------|-------------------|
| `candidates.py` | `search_candidates`, `get_candidate_finances` |
| `contributions.py` | `search_contributions`, `get_top_donors`, `get_contributions_by_state` |
| `expenses.py` | `get_campaign_expenditures`, `get_independent_expenditures`, `get_independent_expenditures_summary` |
| `filings.py` | `get_candidate_filings`, `get_committee_filings` |
| `search.py` | `search_pacs`, `search_committees_by_type` |
| `meta.py` | `fec_help`, `suggest_investigation` |

### Resources (`src/fec_mcp/resources/`)

Static reference data served via `@mcp.resource()`:
- `fec://reference/codes` — party codes, office codes, committee types, form types
- `fec://reference/notable_ids` — known candidate/committee IDs for 2024 presidential race and major PACs
- `fec://reference/api_info` — rate limits, data coverage, tips

### Prompts (`src/fec_mcp/prompts/`)

Workflow prompts generated via `@mcp.prompt()`:
- `investigate_candidate(candidate_name)` — step-by-step investigation workflow
- `follow_the_money(company_name)` — trace corporate political influence
- `compare_candidates(candidate1, candidate2)` — side-by-side financial comparison

### Testing

Tests use `respx` to mock `httpx` calls against the base URL. Set `FEC_API_KEY=TEST_KEY` via `os.environ` in fixtures. When testing tools directly (not through MCP), call `tool_function.fn(...)` since FastMCP wraps the function.
