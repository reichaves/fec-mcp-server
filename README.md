# FEC Campaign Finance MCP Server
### Author: Reinaldo Chaves (reichaves@gmail.com)

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/reichaves/fec-mcp-server)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![FastMCP](https://img.shields.io/badge/MCP-FastMCP-orange)](https://github.com/jlowin/fastmcp)
[![OpenFEC](https://img.shields.io/badge/API-OpenFEC-red)](https://api.open.fec.gov/developers/)

*Leia isto em [Português](README.pt-br.md)*

An MCP server that connects the [OpenFEC API](https://api.open.fec.gov/developers/) to AI assistants, allowing you to investigate US federal campaign finance through natural conversations.

Designed for data journalists, researchers, and citizens who need to explore complex Federal Election Commission (FEC) data without directly knowing the API.

---

## Table of Contents

- [What is MCP?](#what-is-mcp)
- [What does this project do?](#what-does-this-project-do)
- [Architecture](#architecture)
- [Available Tools](#available-tools)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Development and Tests](#development-and-tests)

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

## External Resources

- [OpenFEC API — Documentation](https://api.open.fec.gov/developers/)
- [FEC — Official Website](https://www.fec.gov/)
- [OpenSecrets](https://www.opensecrets.org/)
- [FastMCP — Documentation](https://github.com/jlowin/fastmcp)
- [MCP — Protocol Specification](https://modelcontextprotocol.io/)
