"""Assets module configuration."""

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


class AssetsConfig(BaseModel):
    """Configuration for the assets module."""

    api_base_url: str = Field(
        default="http://localhost:8000", description="Base URL for the assets API server"
    )
    bearer_token: str = Field(default="", description="Bearer token for API authentication")
    protocol: Literal["rest", "graphql"] = Field(
        default="rest", description="API protocol to use (rest or graphql)"
    )
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")
    retry_count: int = Field(
        default=3, ge=0, le=10, description="Number of retry attempts on failure"
    )

    @field_validator("api_base_url")
    @classmethod
    def validate_url_format(cls, v: str) -> str:
        """Validate that the URL is in a valid format."""
        try:
            # Use HttpUrl for validation but return string
            HttpUrl(v)
        except Exception as e:
            raise ValueError(f"Invalid URL format: {v}") from e
        return v
