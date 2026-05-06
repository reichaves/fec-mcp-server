# FEC Campaign Finance MCP Server
# Author: Reinaldo Chaves (reichaves@gmail.com)

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/reichaves/fec-mcp-server)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![FastMCP](https://img.shields.io/badge/MCP-FastMCP-orange)](https://github.com/jlowin/fastmcp)
[![OpenFEC](https://img.shields.io/badge/API-OpenFEC-red)](https://api.open.fec.gov/developers/)

*Leia isto em[Português](README.pt-br.md)*

An MCP server that connects the [OpenFEC API](https://api.open.fec.gov/developers/) to AI assistants, allowing you to investigate US federal campaign finance through natural conversations.

Designed for data journalists, researchers, and citizens who need to explore complex Federal Election Commission (FEC) data without directly knowing the API.

---

## Table of Contents

- [What is MCP?](#what-is-mcp)
- [What does this project do?](#what-does-this-project-do)
- [Architecture](#architecture)
- [Available Tools](#available-tools)
- [Installation](#installation)
- [Configuration in Claude Desktop](#configuration-in-claude-desktop)
-[Configuration in Claude Code and CLI Platforms](#configuration-in-claude-code-and-cli-platforms)
-[Usage Examples](#usage-examples)
- [Development and Tests](#development-and-tests)
- [Security](#security)

---

## What is MCP?

**MCP (Model Context Protocol)** is an open standard that enables AI assistants to communicate with external systems — databases, APIs, files, services — securely and uniformly.

### The three types of MCP capabilities

| Type | What it is | Example in this project |
|------|---------|----------------------|
| **Tools** | Functions the AI can call to fetch or manipulate data | `search_candidates()`, `get_top_donors()` |
| **Resources** | Static or contextual data that is always available | FEC codes tables, notable IDs, Glossary |
| **Prompts** | Workflow templates guiding complex investigations | `investigate_candidate()`, `follow_the_money()` |

---

## What does this project do?

This project exposes the [OpenFEC API](https://api.open.fec.gov/developers/) as an MCP server. The result: you can investigate political financing just by conversing with an LLM.

### Key Capabilities

- **Candidate Search**: Find any federal candidate by name, state, party, or office.
- **Financial Analysis**: Totals raised, spent, debts, and Cash on Hand.
- **Donor Tracking**: Identify the top financiers of a campaign and their employers.
- **Geo-analysis**: See from which states a candidate's money comes.
- **Super PACs and Independent Expenditures**: Monitor outside groups spending to support or attack candidates.
- **Official Reports**: Access filings submitted to the FEC by campaigns and committees.
- **Guided Investigation**: Ready-to-use workflows for journalistic investigations.

### 🔍 Methodological Note (OSINT and Data Architecture)

The FEC API separates "Candidate Totals" (the primary endpoint of the official committee) from the money housed in Political Action Committees (PACs). The `fec_mcp` was designed strictly for the **"Zero Hallucination"** principle. It exposes data exactly as the government bureaucracy classifies it. 
In OSINT investigations, it is up to the AI agent or journalist to use `search_candidates` to list all **Principal Authorized Committees and PACs** attached to a politician and query their finances individually.

### Multi-language Support (i18n)

The server supports internationalization. The default language for responses and tips is English. You can change this by setting the `FEC_MCP_LANG` environment variable (e.g., `FEC_MCP_LANG=pt-br`).

---

## Architecture

```text
fec-mcp-server/
├── README.md                    # Main documentation in English
├── README.pt-br.md              # Main documentation in Portuguese
├── .env.example                 # Example environment variables (API keys, language)
├── pyproject.toml               # Project configuration and modern Python dependencies
├── requirements.txt             # List of dependencies for simple installation via pip
├── start_server.py              # Entry point: adds src/ to path and starts the MCP server
├── src/fec_mcp/
│   ├── main.py                  # Imports all modules to register them in FastMCP
│   ├── server.py                # Creates the central `mcp = FastMCP(...)` instance
│   ├── context.py               # Singleton `fec`: shared instance of FECClient
│   ├── client.py                # Active FECClient: HTTP requests, retry/backoff, timeouts
│   ├── i18n.py                  # Internationalization system (loads text from /locales)
│   ├── logging_config.py        # Logging configuration and verbosity levels
│   ├── models.py                # Pydantic data models for validating API responses
│   ├── tools/                   # MCP Tools (@mcp.tool)
│   │   ├── candidates.py        # search_candidates, get_candidate_finances
│   │   ├── contributions.py     # search_contributions, get_top_donors, get_contributions_by_state
│   │   ├── expenses.py          # get_campaign_expenditures, get_independent_expenditures
│   │   ├── filings.py           # get_campaign_filings for financial reports
│   │   ├── search.py            # search_pacs for finding political action committees
│   │   └── meta.py              # fec_help, suggest_investigation
│   ├── resources/               # MCP Resources (@mcp.resource)
│   │   └── reference.py         # FEC codes, notable IDs, glossary, API info
│   ├── prompts/                 # MCP Prompts (@mcp.prompt)
│   │   └── investigation.py     # investigate_candidate, follow_the_money, compare_candidates
│   ├── data/                    # Static JSON files used by tools
│   │   ├── glossary.json        # FEC glossary terms
│   │   ├── help.json            # Documentation and examples by topic for fec_help
│   │   └── investigations.json  # Journalism investigation pitches
│   └── locales/                 # Translation files
│       ├── en.json              # English translations
│       └── pt.json              # Portuguese translations
└── tests/
    └── test_server.py           # Automated tests for the client and endpoints using pytest and respx
```

---

## Available Tools

### Tools

- `search_candidates`: Search for federal candidates.
- `get_candidate_finances`: Get financial totals for a candidate.
- `search_contributions`: Search for individual donations (Schedule A).
- `get_top_donors`: List the top donors to a committee.
- `get_contributions_by_state`: Aggregate donations by state.
- `get_campaign_expenditures`: List a campaign's expenditures (Schedule B).
- `get_independent_expenditures`: Search for independent expenditures by Super PACs.
- `get_candidate_filings` / `get_committee_filings`: List financial reports submitted to the FEC.
- `search_pacs`: Search for PACs and Super PACs by name.
- `fec_help`: Internal documentation for the tools.
- `suggest_investigation`: Journalistic pitch suggestions based on FEC data.

### Resources

| URI | Content |
|-----|----------|
| `fec://reference/codes` | Party codes, offices, committee types, filing types, donation limits |
| `fec://reference/notable_ids` | IDs of presidential candidates, national committees, relevant Super PACs |
| `fec://reference/api_info` | Data coverage, rate limits, usage tips |
| `fec://reference/glossary` | Glossary of FEC terminology (e.g., PAC, Schedule A, Cash on Hand) |

### Prompts

- `investigate_candidate(candidate_name)`: Step-by-step workflow for a complete financial investigation of a candidate.
- `follow_the_money(company_name)`: Tracks the political influence of a company.
- `compare_candidates(candidate1, candidate2)`: Side-by-side comparison of two candidates.

---

## Installation

### Prerequisites

- **Python 3.10+**
- **FEC API Key**: Free at [api.data.gov/signup](https://api.data.gov/signup/)

### Steps

```bash
git clone https://github.com/your-username/fec-mcp-server.git
cd fec-mcp-server
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
echo "FEC_API_KEY=your_key_here" > .env
```

---

## Configuration in Claude Desktop

1. Locate your Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the server to the configuration:
```json
{
  "mcpServers": {
    "fec-finance": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args":["/absolute/path/to/fec-mcp-server/start_server.py"],
      "env": {
        "FEC_API_KEY": "YOUR_FEC_API_KEY"
      }
    }
  }
}
```
3. Restart Claude Desktop.

---

## Configuration in Claude Code and CLI Platforms

The MCP protocol is highly compatible with CLI-based AI agents. Here is how to set it up for terminal environments.

### 1. Claude Code (Anthropic CLI)

[Claude Code](https://claude.ai/code) is Anthropic's official CLI tool. You can configure the FEC MCP server globally or per project.

**Method A: Using the CLI command**
Run the following command in your terminal (make sure to replace the paths with your actual absolute paths):
```bash
claude mcp add fec-finance -- /absolute/path/to/.venv/bin/python /absolute/path/to/fec-mcp-server/start_server.py
```
*Note: You will need to ensure your `FEC_API_KEY` is exported in your terminal environment (`export FEC_API_KEY="your_key"`) before running Claude Code.*

**Method B: Editing the settings file (Recommended for API Keys)**
To ensure the API key is always loaded, edit the global config file at `~/.claude/settings.json` (or `.claude/settings.json` in your project root):

```json
{
  "mcpServers": {
    "fec-finance": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args":["/absolute/path/to/fec-mcp-server/start_server.py"],
      "env": {
        "FEC_API_KEY": "YOUR_FEC_API_KEY"
      }
    }
  }
}
```
After saving, restart your `claude` session. You can verify it's working by typing `/mcp list` inside Claude Code.

### 2. Google Antigravity / Gemini CLI

Google's Antigravity (Gemini CLI Agent) supports MCP instances via stdio. 
Map the server in your global user configuration directory (e.g., `%APPDATA%\.gemini\antigravity\mcp.json` on Windows or `~/.config/gemini/mcp.json` on Linux/macOS):

```json
{
  "mcpServers": {
    "fec-mcp": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args":["/absolute/path/to/fec-mcp-server/start_server.py"],
      "env": {
        "FEC_API_KEY": "YOUR_FEC_API_KEY"
      }
    }
  }
}
```

### 3. IDEs (Cursor, Windsurf, Continue.dev)

- **Cursor IDE**: Edit `~/.cursor/mcp.json`. The JSON structure is identical to Claude Desktop.
- **Continue.dev**: Edit `.continue/config.json` in your workspace or global settings.
- **Windsurf**: Check the official Codeium documentation for the MCP config path, using the same JSON structure.

---

## Usage Examples

### Investigate a candidate

> *"Investigate the campaign finances of Kamala Harris in 2024"*

The LLM will automatically execute:
1. `search_candidates(name="Kamala Harris", election_year=2024)`
2. `get_candidate_finances(candidate_id="P00009423")`
3. `get_top_donors(committee_id="C00703975")`

### Compare candidates

> *"Compare the finances of Trump and Biden for 2024"*

The prompt `compare_candidates` generates a complete table with all metrics side by side.

---

## Known Limitations

- **Federal data only**: State and local elections are not in the FEC.
- **Dark money**: Donations to 501(c)(4) are not disclosed to the FEC.
- **Latency**: Individual donation endpoints (`schedule_a`) can be slow.
- **Rate limit**: 1,000 requests/hour with the free API key.

## Security

This server runs **locally** on your machine and makes **read-only** requests to the public OpenFEC API. It handles no user credentials or PII.

Key practices:
- Store your API key in `.env` only — never commit it (`.env` is in `.gitignore`)
- API key is automatically masked in all log output (`SecretFilter`)
- Logs rotate at 5 MB and are excluded from version control
- Input filenames loaded from disk are restricted to an explicit allowlist

For the full threat model, Skill Vetter compatibility declaration, dependency audit instructions, and how to report vulnerabilities, see [SECURITY.md](SECURITY.md).

```bash
# Audit dependencies for known CVEs
pip-audit

# Static security analysis
bandit -r src/

# Run security-focused tests
pytest tests/test_security.py -v
```

---

## External Resources

-[OpenFEC API — Documentation](https://api.open.fec.gov/developers/)
- [FEC — Official Website](https://www.fec.gov/)
- [OpenSecrets](https://www.opensecrets.org/)
- [FastMCP — Documentation](https://github.com/jlowin/fastmcp)
- [MCP — Protocol Specification](https://modelcontextprotocol.io/)
