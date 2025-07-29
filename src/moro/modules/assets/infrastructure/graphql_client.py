"""GraphQL API client for assets."""

import asyncio
from typing import Any, Optional

import httpx
from pydantic import ValidationError

from ..config import AssetsConfig
from ..domain.entity import Asset
from ..domain.repository import AssetRepository, SearchCriteria
from ..domain.value_objects import AssetId, HostName, Location, ModelName


class GraphQLAssetRepository(AssetRepository):
    """GraphQL API implementation of AssetRepository."""

    def __init__(self, config: AssetsConfig) -> None:
        """Initialize with configuration."""
        self._config = config

    async def search(self, criteria: SearchCriteria) -> Optional[list[Asset]]:
        """Search assets via GraphQL API."""
        try:
            # Build GraphQL query and variables
            query = self._build_query()
            variables = self._build_variables(criteria)

            # Build headers
            headers = {"Content-Type": "application/json"}
            if self._config.bearer_token:
                headers["Authorization"] = f"Bearer {self._config.bearer_token}"

            # Prepare GraphQL request payload
            payload = {
                "query": query,
                "variables": variables,
            }

            # Perform request with retry logic
            for attempt in range(self._config.retry_count + 1):
                try:
                    async with httpx.AsyncClient(timeout=self._config.timeout) as client:
                        response = await client.post(
                            f"{self._config.api_base_url}/graphql",
                            json=payload,
                            headers=headers,
                        )

                        if response.status_code == 200:
                            response_data = response.json()
                            return self._parse_response(response_data)
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

    def _build_query(self) -> str:
        """Build GraphQL query string."""
        return """
            query SearchAssets($assetId: String, $modelName: String, $location: String) {
                assets(assetId: $assetId, modelName: $modelName, location: $location) {
                    id
                    modelName
                    hostName
                    location
                }
            }
        """

    def _build_variables(self, criteria: SearchCriteria) -> dict[str, Any]:
        """Build GraphQL variables from search criteria."""
        variables: dict[str, Any] = {}

        if criteria.asset_id is not None:
            variables["assetId"] = criteria.asset_id
        if criteria.model_name is not None:
            variables["modelName"] = criteria.model_name
        if criteria.location is not None:
            variables["location"] = criteria.location

        return variables

    def _parse_response(self, response_data: Any) -> Optional[list[Asset]]:
        """Parse GraphQL response into Asset entities."""
        try:
            if not isinstance(response_data, dict):
                return None

            # Check for GraphQL errors
            if "errors" in response_data:
                return None

            # Extract data
            data = response_data.get("data")
            if not isinstance(data, dict):
                return None

            assets_data = data.get("assets")
            if not isinstance(assets_data, list):
                return None

            assets = []
            for item in assets_data:
                if not isinstance(item, dict):
                    continue

                # Extract required fields (GraphQL uses camelCase)
                asset_id_str = item.get("id")
                model_name_str = item.get("modelName")
                host_name_str = item.get("hostName")
                location_str = item.get("location")

                if not (
                    isinstance(asset_id_str, str) and
                    isinstance(model_name_str, str) and
                    isinstance(host_name_str, str) and
                    isinstance(location_str, str)
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
