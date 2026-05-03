# Security Policy — fec-mcp-server

## Overview

`fec-mcp-server` is an MCP (Model Context Protocol) server that exposes the [OpenFEC API](https://api.open.fec.gov/developers/) as tools for AI assistants. This document describes the security model, safe usage practices, and how to report vulnerabilities.

---

## Threat Model

### What this server IS

- A **local process** that runs on your own machine
- A **read-only** proxy to a **public government dataset** (FEC campaign finance records)
- Designed to be invoked by a trusted local AI assistant (e.g., Claude Desktop) under human supervision

### What this server is NOT

- A web server exposed to the internet
- A handler of user credentials, PII, or financial transactions
- A multi-tenant or shared service

### Trust boundary

```
[Your Machine]
  └── AI Assistant (Claude Desktop / Cursor / VSCode)
        └── MCP Client
              └── fec-mcp-server (this project)  ←── runs locally
                    └── OpenFEC API (public, read-only)
```

Input to the server comes **only from the local AI assistant**, which operates under your direct supervision. There is no network-exposed attack surface.

---

## Safe Usage Guidelines

### 1. API Key Handling

Your OpenFEC API key is a **personal read-only token** for a public dataset. It is not a financial credential, but it should still be protected:

| Do | Do Not |
|----|--------|
| Store in `.env` file (local only) | Commit `.env` to version control |
| Rotate via [api.data.gov](https://api.data.gov/) if exposed | Share your key publicly |
| Keep `.env` in `.gitignore` (already configured) | Hardcode the key in source files |

Verify your key is protected before committing:
```bash
git status   # .env should NOT appear in tracked files
cat .gitignore | grep .env  # should output: .env
```

### 2. Log Files

Logs are written to `logs/fec_mcp.log`. The server includes a `SecretFilter` that automatically masks the API key in all log records. However:

- Do **not** share log files publicly (they contain request details)
- The `logs/` directory is in `.gitignore`
- Logs rotate automatically at 5 MB (3 backups kept)

### 3. Running the Server

The server uses `stdio` transport — it communicates via stdin/stdout with the MCP client. It does **not** open TCP/UDP ports and does **not** accept connections from the network.

### 4. Data Scope

All data returned is sourced directly from the OpenFEC API (public federal election finance records). No private data is accessed or stored by this server.

---

## Skill Vetter / Skills.sh Compatibility

If you are evaluating this project via a **Skill Vetter** tool or the **Skills.sh Manager** extension, here is what to expect:

### Permissions requested

| Permission | Requested? | Reason |
|-----------|------------|--------|
| Network (outbound) | Yes — `api.open.fec.gov` only | Fetches public FEC data |
| File system (read) | Yes — `src/fec_mcp/data/*.json` | Loads static reference data |
| File system (write) | Yes — `logs/` only | Rotating log files |
| Environment variables | Yes — `FEC_API_KEY`, `FEC_MCP_LANG` | API auth and language config |
| Stdin/stdout | Yes | MCP stdio transport |
| System commands | No | Not used |
| Credentials / passwords | No | Not handled |
| Camera / microphone / clipboard | No | Not applicable |

### Signals of safe behavior

- No `subprocess.run()` / `os.system()` calls with dynamic input
- No `pickle` deserialization
- No `eval()` / `exec()` on user input
- No dynamic imports based on user input
- All tool functions return JSON strings (no code execution)
- Input filename allowlisting in `tools/meta.py`

---

## Dependency Audit

Run a dependency vulnerability scan at any time:

```bash
# Install audit tool (included in dev dependencies)
pip install -e ".[dev]"

# Scan for known CVEs in dependencies
pip-audit

# Static security analysis of source code
bandit -r src/
```

Current production dependencies (minimal surface area):

| Package | Purpose | Known CVEs |
|---------|---------|-----------|
| `fastmcp` | MCP framework | Check via `pip-audit` |
| `httpx` | Async HTTP client | Check via `pip-audit` |
| `pydantic` | Data validation | Check via `pip-audit` |
| `python-dotenv` | Env file loading | Check via `pip-audit` |

---

## Verifying with Socket / Snyk / Gen Agent Trust Hub

If using the **VS Code / Cursor extension** that integrates Socket, Snyk, or Gen Agent Trust Hub:

1. Open the project in VS Code/Cursor with the Skills.sh Manager extension
2. The panel will show dependency audit results automatically
3. All flagged issues can also be reproduced locally with `pip-audit` (see above)

For a manual Socket scan of the published package (if/when published to PyPI):
- Visit [socket.dev](https://socket.dev/) and search for `fec-mcp-server`

---

## Reporting Vulnerabilities

This is an open-source research tool used for journalistic investigation of public data. To report a security issue:

1. **Do not** open a public GitHub issue for security vulnerabilities
2. Email: **reichaves@gmail.com** with subject `[SECURITY] fec-mcp-server`
3. Include: description of the issue, steps to reproduce, potential impact

Response time: best effort (this is a personal/research project).

---

## Security Checklist (for contributors)

Before submitting a PR:

- [ ] No secrets, API keys, or credentials in source files
- [ ] No new `subprocess`/`os.system()` calls with dynamic input
- [ ] No `pickle`, `eval()`, or `exec()` on external data
- [ ] New tool functions wrap all exceptions and return `{"error": ...}` JSON
- [ ] New filenames loaded from disk use the `_ALLOWED_DATA_FILES` allowlist
- [ ] `python -m py_compile` passes on all modified files
- [ ] `pytest tests/` passes (including `test_security.py`)
- [ ] `bandit -r src/` produces no HIGH severity findings
- [ ] `pip-audit` produces no CRITICAL findings in new dependencies

---

## Compliance Notes

- **FEC API Terms of Service**: This server respects the OpenFEC rate limit (1,000 req/hour). It does not cache or republish data beyond what is needed for individual queries.
- **Data attribution**: All data is attributed to the FEC as required.
- **GDPR / CCPA**: This server does not collect, store, or transmit personal data. FEC campaign finance data is public record.
