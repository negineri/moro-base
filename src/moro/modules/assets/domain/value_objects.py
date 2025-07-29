"""Assets domain value objects."""

from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class AssetId(BaseModel):
    """Asset ID value object."""

    value: str = Field(..., description="Asset ID as UUID string")

    @field_validator("value")
    @classmethod
    def validate_uuid_format(cls, v: str) -> str:
        """Validate that the value is a valid UUID format."""
        if not v:
            raise ValueError("Asset ID cannot be empty")
        try:
            UUID(v)
        except ValueError as e:
            raise ValueError(f"Invalid UUID format: {v}") from e
        return v


class ModelName(BaseModel):
    """Model name value object."""

    value: str = Field(..., description="Device model name")

    @field_validator("value")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that the value is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("Model name cannot be empty or whitespace")
        return v


class HostName(BaseModel):
    """Host name value object."""

    value: str = Field(..., description="Device hostname")

    @field_validator("value")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that the value is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("Hostname cannot be empty or whitespace")
        return v


class Location(BaseModel):
    """Location value object."""

    value: str = Field(..., description="Device location")

    @field_validator("value")
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate that the value is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("Location cannot be empty or whitespace")
        return v
