"""Assets domain repository interfaces and search criteria."""

from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel

from .entity import Asset


class SearchCriteria(BaseModel):
    """Asset search criteria."""

    asset_id: Optional[str] = None
    model_name: Optional[str] = None
    location: Optional[str] = None

    @classmethod
    def by_id(cls, asset_id: str) -> "SearchCriteria":
        """Create search criteria by asset ID."""
        return cls(asset_id=asset_id)

    @classmethod
    def by_model_name(cls, model_name: str) -> "SearchCriteria":
        """Create search criteria by model name."""
        return cls(model_name=model_name)

    @classmethod
    def by_location(cls, location: str) -> "SearchCriteria":
        """Create search criteria by location."""
        return cls(location=location)


class AssetRepository(ABC):
    """Abstract repository for asset operations."""

    @abstractmethod
    async def search(self, criteria: SearchCriteria) -> Optional[list[Asset]]:
        """
        Search assets based on criteria.

        Returns:
            List of matching assets, or None if an error occurred.
        """
        pass
