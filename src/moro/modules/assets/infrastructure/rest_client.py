"""REST API client for assets."""

import asyncio
from typing import Any, Optional

import httpx
from pydantic import ValidationError

from ..config import AssetsConfig
from ..domain.entity import Asset
from ..domain.repository import AssetRepository, SearchCriteria
from ..domain.value_objects import AssetId, HostName, Location, ModelName


class RestAssetRepository(AssetRepository):
    """REST API implementation of AssetRepository."""

    def __init__(self, config: AssetsConfig) -> None:
        """Initialize with configuration."""
        self._config = config

    async def search(self, criteria: SearchCriteria) -> Optional[list[Asset]]:
        """Search assets via REST API."""
        try:
            # Build query parameters
            params = {}
            if criteria.asset_id is not None:
                params["asset_id"] = criteria.asset_id
            if criteria.model_name is not None:
                params["model_name"] = criteria.model_name
            if criteria.location is not None:
                params["location"] = criteria.location

            # Build headers
            headers = {}
            if self._config.bearer_token:
                headers["Authorization"] = f"Bearer {self._config.bearer_token}"

            # Perform request with retry logic
            for attempt in range(self._config.retry_count + 1):
                try:
                    async with httpx.AsyncClient(timeout=self._config.timeout) as client:
                        response = await client.get(
                            f"{self._config.api_base_url}/assets",
                            params=params,
                            headers=headers,
                        )

                        if response.status_code == 200:
                            response_data = response.json()
                            return self._parse_response(response_data)
                        if response.status_code == 404:
                            return None
                        if response.status_code >= 500 and attempt < self._config.retry_count:
                            # Retry on server errors
                            await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                            continue
                        return None

                except (httpx.RequestError, httpx.TimeoutException):
                    if attempt < self._config.retry_count:
                        await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                        continue
                    return None

            return None

        except Exception:
            return None

    def _parse_response(self, response_data: Any) -> Optional[list[Asset]]:
        """Parse API response into Asset entities."""
        try:
            if not isinstance(response_data, list):
                return None

            assets = []
            for item in response_data:
                if not isinstance(item, dict):
                    continue

                # Extract required fields
                asset_id_str = item.get("id")
                model_name_str = item.get("model_name")
                host_name_str = item.get("host_name")
                location_str = item.get("location")

                if not (
                    isinstance(asset_id_str, str)
                    and isinstance(model_name_str, str)
                    and isinstance(host_name_str, str)
                    and isinstance(location_str, str)
                ):
                    continue

                # Create value objects with validation
                asset_id = AssetId(value=asset_id_str)
                model_name = ModelName(value=model_name_str)
                host_name = HostName(value=host_name_str)
                location = Location(value=location_str)

                # Create asset entity
                asset = Asset(
                    id=asset_id,
                    model_name=model_name,
                    host_name=host_name,
                    location=location,
                )
                assets.append(asset)

            return assets

        except (ValidationError, TypeError, ValueError):
            return None
