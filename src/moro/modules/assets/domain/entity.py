"""Assets domain entities."""

from typing import Any

from pydantic import BaseModel

from .value_objects import AssetId, HostName, Location, ModelName


class Asset(BaseModel):
    """Asset entity representing network equipment or server."""

    id: AssetId
    model_name: ModelName
    host_name: HostName
    location: Location

    def __eq__(self, other: Any) -> bool:
        """Two assets are equal if they have the same ID."""
        if not isinstance(other, Asset):
            return False
        return self.id.value == other.id.value

    def __hash__(self) -> int:
        """Hash based on asset ID."""
        return hash(self.id.value)
