
import pytest
import respx
import httpx
import json
import sys
import os

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from fec_mcp.client import FECClient
from fec_mcp.server import mcp

# Fixtures
@pytest.fixture
def client():
    # Usa chave falsa para testes
    os.environ["FEC_API_KEY"] = "TEST_KEY"
    return FECClient(default_timeout=1.0, max_retries=0)

@pytest.fixture
def mock_fec_api():
    with respx.mock(base_url="https://api.open.fec.gov/v1") as mock:
        yield mock

# ============================================================
# CLIENT TESTS
# ============================================================

@pytest.mark.asyncio
async def test_search_candidates(client, mock_fec_api):
    # Mocking response
    mock_fec_api.get("/candidates/search/").mock(return_value=httpx.Response(200, json={
        "results": [{"candidate_id": "P80001571", "name": "TRUMP, DONALD J."}],
        "pagination": {"count": 1}
    }))
    
    result = await client.search_candidates(name="Trump")
    assert result["results"][0]["candidate_id"] == "P80001571"

@pytest.mark.asyncio
async def test_get_candidate_totals(client, mock_fec_api):
    mock_fec_api.get("/candidate/P80000722/totals/").mock(return_value=httpx.Response(200, json={
        "results": [{"receipts": 1000000}],
        "pagination": {"count": 1}
    }))
    
    result = await client.get_candidate_totals("P80000722")
    assert result["results"][0]["receipts"] == 1000000

@pytest.mark.asyncio
async def test_api_error_retry(client, mock_fec_api):
    # Simula erro 503 depois sucesso
    route = mock_fec_api.get("/candidates/search/")
    route.side_effect = [
        httpx.Response(503),
        httpx.Response(200, json={"results": []})
    ]
    
    # Client configurado com retries
    client.max_retries = 1
    result = await client.search_candidates(name="Retry")
    assert "results" in result
    assert route.call_count == 2

# ============================================================
# MCP SERVER TESTS
# ============================================================

@pytest.mark.asyncio
async def test_server_registration():
    # Assegura que main importa tudo e registra
    from fec_mcp.main import main
    # Não executamos main(), apenas importamos modules via main
    # Na verdade, precisamos importar os submódulos para registrar
    import fec_mcp.tools.candidates
    import fec_mcp.tools.meta
    
    tools = [t.name for t in await mcp.list_tools()]
    
    assert "search_candidates" in tools
    assert "fec_help" in tools
    assert "suggest_investigation" in tools

@pytest.mark.asyncio
async def test_tool_execution(mock_fec_api):
    # Importa ferramentas para registro
    import fec_mcp.tools.candidates
    
    # Mock para search_candidates
    mock_fec_api.get("/candidates/search/").mock(return_value=httpx.Response(200, json={
        "results": [{"candidate_id": "P123", "name": "Test Candidate", "party_full": "PARTY", "state": "US", "office_full": "President"}],
        "pagination": {"count": 1}
    }))
    
    # Executa ferramenta via MCP (simulado)
    # Como FastMCP não expõe executor direto fácil sem rodar servidor, chamamos a função decorada
    # Mas as funções decoradas estão disponíveis no módulo
    from fec_mcp.tools.candidates import search_candidates
    
    result_json = await search_candidates(name="Test")
    result = json.loads(result_json)
    
    assert result["showing"] == 1
    assert result["candidates"][0]["name"] == "Test Candidate"
