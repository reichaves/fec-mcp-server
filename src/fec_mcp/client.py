import os
import asyncio
from typing import Optional, Dict, Any, List
import httpx
from dotenv import load_dotenv

from .logging_config import get_logger
from .models import FECResponse

logger = get_logger(__name__)

# Load environment variables (can be called again safely)
load_dotenv()

class FECClient:
    """Async client for the OpenFEC API"""
    
    # Endpoints known to be slow or heavy
    SLOW_ENDPOINTS = [
        "/schedules/schedule_a/",  # Contributions
        "/schedules/schedule_b/",  # Disbursements
        "/schedules/schedule_e/",  # Independent Expenditures
    ]
    
    def __init__(self, default_timeout: float = 60.0, slow_timeout: float = 120.0, max_retries: int = 2):
        self.api_key = os.getenv("FEC_API_KEY")
        self.base_url = os.getenv("FEC_API_BASE_URL", "https://api.open.fec.gov/v1")
        self.default_timeout = default_timeout
        self.slow_timeout = slow_timeout
        self.max_retries = max_retries
        
        if not self.api_key:
            logger.warning("FEC_API_KEY not found in environment variables.")
    
    def _get_timeout(self, endpoint: str) -> float:
        """Return appropriate timeout based on endpoint"""
        for slow_ep in self.SLOW_ENDPOINTS:
            if slow_ep in endpoint:
                return self.slow_timeout
        return self.default_timeout
    
    async def _request(self, endpoint: str, params: Optional[dict] = None) -> dict:
        params = params or {}
        params["api_key"] = self.api_key
        
        timeout = self._get_timeout(endpoint)
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient() as client:
                    logger.debug(f"Requesting {endpoint} (attempt {attempt+1})", extra={"params": params})
                    response = await client.get(
                        f"{self.base_url}{endpoint}",
                        params=params,
                        timeout=timeout
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    try:
                        validated_data = FECResponse.model_validate(data)
                        return validated_data.model_dump()
                    except Exception as e:
                        logger.warning(f"Data validation warning for {endpoint}: {e}. Returning unvalidated data as fallback.")
                        return data
            except httpx.ReadTimeout as e:
                last_exception = e
                logger.warning(f"Timeout accessing {endpoint} (attempt {attempt+1}): {e}")
                if attempt < self.max_retries:
                    # Progressive wait: 2s, 4s, etc.
                    await asyncio.sleep(2 ** (attempt + 1))
                    continue
                raise
            except httpx.HTTPStatusError as e:
                # Error 429 (rate limit) or 503 (service unavailable) - retry
                if e.response.status_code in (429, 503) and attempt < self.max_retries:
                    logger.warning(f"HTTP {e.response.status_code} for {endpoint} (attempt {attempt+1}): {e}")
                    await asyncio.sleep(2 ** (attempt + 1))
                    continue
                logger.error(f"HTTP error for {endpoint}: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error for {endpoint}: {e}")
                raise
        
        raise last_exception
    
    # ========== CANDIDATOS ==========
    
    async def search_candidates(
        self,
        name: Optional[str] = None,
        state: Optional[str] = None,
        office: Optional[str] = None,
        party: Optional[str] = None,
        cycle: Optional[int] = None,
        is_active: bool = True,
        per_page: int = 20
    ) -> dict:
        params = {"per_page": min(per_page, 100)}
        if name:
            params["q"] = name
        if state:
            params["state"] = state.upper()
        if office:
            params["office"] = office.upper()
        if party:
            params["party"] = party.upper()
        if cycle:
            params["cycle"] = cycle
        if is_active:
            params["is_active_candidate"] = "true"
        return await self._request("/candidates/search/", params)
    
    async def get_candidate(self, candidate_id: str) -> dict:
        return await self._request(f"/candidate/{candidate_id}/")
    
    async def get_candidate_totals(self, candidate_id: str, cycle: Optional[int] = None) -> dict:
        params = {}
        if cycle:
            params["cycle"] = cycle
        return await self._request(f"/candidate/{candidate_id}/totals/", params)
    
    # ========== COMITÊS ==========
    
    async def search_committees(
        self,
        name: Optional[str] = None,
        committee_type: Optional[str] = None,
        state: Optional[str] = None,
        party: Optional[str] = None,
        cycle: Optional[int] = None,
        per_page: int = 20
    ) -> dict:
        params = {"per_page": min(per_page, 100)}
        if name:
            params["q"] = name
        if committee_type:
            params["committee_type"] = committee_type.upper()
        if state:
            params["state"] = state.upper()
        if party:
            params["party"] = party.upper()
        if cycle:
            params["cycle"] = cycle
        return await self._request("/committees/", params)
    
    async def get_committee(self, committee_id: str) -> dict:
        return await self._request(f"/committee/{committee_id}/")
    
    # ========== CONTRIBUIÇÕES (Schedule A) ==========
    
    async def get_contributions(
        self,
        committee_id: Optional[str] = None,
        contributor_name: Optional[str] = None,
        contributor_employer: Optional[str] = None,
        contributor_state: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        two_year_transaction_period: Optional[int] = None,
        per_page: int = 20
    ) -> dict:
        params = {"per_page": min(per_page, 100)}
        if committee_id:
            params["committee_id"] = committee_id
        if contributor_name:
            params["contributor_name"] = contributor_name
        if contributor_employer:
            params["contributor_employer"] = contributor_employer
        if contributor_state:
            params["contributor_state"] = contributor_state.upper()
        if min_amount:
            params["min_amount"] = min_amount
        if max_amount:
            params["max_amount"] = max_amount
        if two_year_transaction_period:
            params["two_year_transaction_period"] = two_year_transaction_period
        return await self._request("/schedules/schedule_a/", params)
    
    async def get_contributions_by_state(self, committee_id: str, cycle: Optional[int] = None) -> dict:
        params = {"committee_id": committee_id}
        if cycle:
            params["cycle"] = cycle
        return await self._request("/schedules/schedule_a/by_state/", params)
    
    # ========== DESPESAS (Schedule B) ==========
    
    async def get_disbursements(
        self,
        committee_id: Optional[str] = None,
        recipient_name: Optional[str] = None,
        disbursement_purpose: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        two_year_transaction_period: Optional[int] = None,
        per_page: int = 20
    ) -> dict:
        params = {"per_page": min(per_page, 100)}
        if committee_id:
            params["committee_id"] = committee_id
        if recipient_name:
            params["recipient_name"] = recipient_name
        if disbursement_purpose:
            params["disbursement_purpose_category"] = disbursement_purpose
        if min_amount:
            params["min_amount"] = min_amount
        if max_amount:
            params["max_amount"] = max_amount
        if two_year_transaction_period:
            params["two_year_transaction_period"] = two_year_transaction_period
        return await self._request("/schedules/schedule_b/", params)
    
    # ========== FILINGS ==========
    
    async def get_filings(
        self,
        committee_id: Optional[str] = None,
        candidate_id: Optional[str] = None,
        form_type: Optional[str] = None,
        min_receipt_date: Optional[str] = None,
        per_page: int = 20
    ) -> dict:
        params = {"per_page": min(per_page, 100)}
        if committee_id:
            params["committee_id"] = committee_id
        if candidate_id:
            params["candidate_id"] = candidate_id
        if form_type:
            params["form_type"] = form_type.upper()
        if min_receipt_date:
            params["min_receipt_date"] = min_receipt_date
        return await self._request("/filings/", params)
    
    # ========== INDEPENDENT EXPENDITURES (Schedule E) ==========
    
    async def get_independent_expenditures(
        self,
        candidate_id: Optional[str] = None,
        committee_id: Optional[str] = None,
        support_oppose: Optional[str] = None,
        min_amount: Optional[float] = None,
        cycle: Optional[int] = None,
        per_page: int = 20
    ) -> dict:
        params = {"per_page": min(per_page, 100)}
        if candidate_id:
            params["candidate_id"] = candidate_id
        if committee_id:
            params["committee_id"] = committee_id
        if support_oppose:
            params["support_oppose_indicator"] = support_oppose.upper()
        if min_amount:
            params["min_amount"] = min_amount
        if cycle:
            params["cycle"] = cycle
        return await self._request("/schedules/schedule_e/", params)
