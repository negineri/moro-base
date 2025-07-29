"""Assets use cases."""

from typing import Optional

from .domain.entity import Asset
from .domain.repository import AssetRepository, SearchCriteria


class AssetSearchUseCase:
    """Asset search use case."""

    def __init__(self, repository: AssetRepository) -> None:
        """Initialize the use case with a repository."""
        self._repository = repository

    async def search_by_id(self, asset_id: str) -> Optional[list[Asset]]:
        """Search assets by ID."""
        criteria = SearchCriteria.by_id(asset_id)
        return await self._repository.search(criteria)

    async def search_by_model_name(self, model_name: str) -> Optional[list[Asset]]:
        """Search assets by model name."""
        criteria = SearchCriteria.by_model_name(model_name)
        return await self._repository.search(criteria)

    async def search_by_location(self, location: str) -> Optional[list[Asset]]:
        """Search assets by location."""
        criteria = SearchCriteria.by_location(location)
        return await self._repository.search(criteria)

    async def search(self, criteria: SearchCriteria) -> Optional[list[Asset]]:
        """Search assets by custom criteria."""
        return await self._repository.search(criteria)
