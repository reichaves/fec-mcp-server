"""
Security-focused test suite for fec-mcp-server.

Tests cover: path traversal prevention, null/empty input safety,
API key scrubbing from logs.
"""

import json
import logging
import os
import sys

import pytest
import respx
import httpx

# Add src to path, consistent with test_server.py
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

os.environ.setdefault("FEC_API_KEY", "TEST_KEY_SECURITY")


# ============================================================
# PATH TRAVERSAL PREVENTION
# ============================================================

class TestPathTraversal:
    """load_json_data() must reject any filename not on the allowlist."""

    def test_rejects_relative_path_traversal(self):
        from fec_mcp.tools.meta import load_json_data
        with pytest.raises(ValueError, match="not allowed"):
            load_json_data("../../../etc/passwd")

    def test_rejects_absolute_unix_path(self):
        from fec_mcp.tools.meta import load_json_data
        with pytest.raises(ValueError, match="not allowed"):
            load_json_data("/etc/passwd")

    def test_rejects_windows_path(self):
        from fec_mcp.tools.meta import load_json_data
        with pytest.raises(ValueError, match="not allowed"):
            load_json_data(r"C:\Windows\System32\drivers\etc\hosts")

    def test_rejects_unknown_json_file(self):
        from fec_mcp.tools.meta import load_json_data
        with pytest.raises(ValueError, match="not allowed"):
            load_json_data("secrets.json")

    def test_allows_help_json(self):
        from fec_mcp.tools.meta import load_json_data
        result = load_json_data("help.json")
        assert isinstance(result, dict)

    def test_allows_investigations_json(self):
        from fec_mcp.tools.meta import load_json_data
        result = load_json_data("investigations.json")
        assert isinstance(result, dict)

    def test_allows_glossary_json(self):
        from fec_mcp.tools.meta import load_json_data
        result = load_json_data("glossary.json")
        assert isinstance(result, dict)


# ============================================================
# NULL / EMPTY INPUT SAFETY
# ============================================================

@pytest.fixture
def client():
    os.environ["FEC_API_KEY"] = "TEST_KEY_SECURITY"
    from fec_mcp.client import FECClient
    return FECClient(default_timeout=1.0, max_retries=0)


@pytest.fixture
def fec_mock():
    with respx.mock(base_url="https://api.open.fec.gov/v1") as mock:
        yield mock


_EMPTY_RESPONSE = {"results": [], "pagination": {"count": 0}}


class TestNullInputSafety:
    """Passing None for optional string params must not raise AttributeError."""

    @pytest.mark.asyncio
    async def test_search_candidates_all_none(self, client, fec_mock):
        fec_mock.get("/candidates/search/").mock(
            return_value=httpx.Response(200, json=_EMPTY_RESPONSE)
        )
        result = await client.search_candidates(
            name=None, state=None, office=None, party=None
        )
        assert "results" in result

    @pytest.mark.asyncio
    async def test_search_committees_all_none(self, client, fec_mock):
        fec_mock.get("/committees/").mock(
            return_value=httpx.Response(200, json=_EMPTY_RESPONSE)
        )
        result = await client.search_committees(
            name=None, state=None, party=None, committee_type=None
        )
        assert "results" in result

    @pytest.mark.asyncio
    async def test_get_contributions_null_state(self, client, fec_mock):
        fec_mock.get("/schedules/schedule_a/").mock(
            return_value=httpx.Response(200, json=_EMPTY_RESPONSE)
        )
        result = await client.get_contributions(contributor_state=None)
        assert "results" in result

    @pytest.mark.asyncio
    async def test_get_filings_null_form_type(self, client, fec_mock):
        fec_mock.get("/filings/").mock(
            return_value=httpx.Response(200, json=_EMPTY_RESPONSE)
        )
        result = await client.get_filings(form_type=None)
        assert "results" in result

    @pytest.mark.asyncio
    async def test_get_independent_expenditures_null_support_oppose(self, client, fec_mock):
        fec_mock.get("/schedules/schedule_e/").mock(
            return_value=httpx.Response(200, json=_EMPTY_RESPONSE)
        )
        result = await client.get_independent_expenditures(support_oppose=None)
        assert "results" in result


# ============================================================
# LOG SCRUBBING
# ============================================================

class TestLogScrubbing:
    """SecretFilter must prevent API key from appearing in log output."""

    def test_secret_filter_masks_api_key_in_message(self):
        os.environ["FEC_API_KEY"] = "SENSITIVE_KEY_ABCDE12345"
        from fec_mcp.logging_config import SecretFilter

        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="",
            lineno=0,
            msg="Requesting /candidates/ params={'api_key': 'SENSITIVE_KEY_ABCDE12345'}",
            args=(),
            exc_info=None,
        )
        f = SecretFilter()
        f.filter(record)
        assert "SENSITIVE_KEY_ABCDE12345" not in record.getMessage()
        assert "***REDACTED***" in record.getMessage()

    def test_secret_filter_passes_unrelated_message(self):
        os.environ["FEC_API_KEY"] = "SENSITIVE_KEY_ABCDE12345"
        from fec_mcp.logging_config import SecretFilter

        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="",
            lineno=0,
            msg="Search completed for candidate Trump",
            args=(),
            exc_info=None,
        )
        f = SecretFilter()
        f.filter(record)
        assert record.getMessage() == "Search completed for candidate Trump"

    def test_secret_filter_handles_missing_env_key(self):
        """Filter must not crash when FEC_API_KEY is not set."""
        old_key = os.environ.pop("FEC_API_KEY", None)
        try:
            from fec_mcp.logging_config import SecretFilter
            record = logging.LogRecord(
                name="test",
                level=logging.DEBUG,
                pathname="",
                lineno=0,
                msg="some message",
                args=(),
                exc_info=None,
            )
            f = SecretFilter()
            result = f.filter(record)
            assert result is True
        finally:
            if old_key:
                os.environ["FEC_API_KEY"] = old_key
