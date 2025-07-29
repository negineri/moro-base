"""Assets CLI commands."""

import asyncio
import json
from typing import Literal, Optional

import click

from moro.config.settings import ConfigRepository
from moro.dependencies.container import create_injector
from moro.modules.assets.domain.entity import Asset
from moro.modules.assets.usecase import AssetSearchUseCase


@click.group()
def assets() -> None:
    """Assets management commands."""
    pass


@assets.command()
@click.option("--id", "asset_id", help="Asset ID (UUID)")
@click.option("--model", "model_name", help="Model name")
@click.option("--location", help="Location")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
def search(
    asset_id: Optional[str],
    model_name: Optional[str],
    location: Optional[str],
    output_format: Literal["table", "json"],
) -> None:
    """Search assets by criteria."""
    try:
        # Validate input - exactly one search criterion required
        search_criteria = [asset_id, model_name, location]
        provided_criteria = [c for c in search_criteria if c is not None]

        if len(provided_criteria) == 0:
            click.echo(
                "Error: Please specify exactly one search criterion (--id, --model, or --location)"
            )
            raise click.Abort()

        if len(provided_criteria) > 1:
            click.echo("Error: Please specify only one search criterion at a time")
            raise click.Abort()

        # Setup dependency injection
        config_repo = ConfigRepository.create()
        injector = create_injector(config_repo)

        # Create use case
        usecase = injector.get(AssetSearchUseCase)

        # Execute search
        if asset_id:
            results = asyncio.run(usecase.search_by_id(asset_id))
        elif model_name:
            results = asyncio.run(usecase.search_by_model_name(model_name))
        elif location:
            results = asyncio.run(usecase.search_by_location(location))
        else:
            click.echo("Error: No valid search criteria provided")
            raise click.Abort()

        # Handle results
        if results is None:
            click.echo("Error: Failed to search assets (connection or server error)")
            raise click.Abort()

        if len(results) == 0:
            click.echo("No assets found matching the criteria")
            return

        # Output results
        if output_format == "json":
            _output_json(results)
        else:
            _output_table(results)

    except click.Abort:
        raise
    except Exception as e:
        click.echo(f"Error: Unexpected error occurred: {e}")
        raise click.Abort() from e


def _output_json(results: list[Asset]) -> None:
    """Output results in JSON format."""
    json_data = []
    for asset in results:
        json_data.append(
            {
                "id": asset.id.value,
                "model_name": asset.model_name.value,
                "host_name": asset.host_name.value,
                "location": asset.location.value,
            }
        )

    click.echo(json.dumps(json_data, indent=2, ensure_ascii=False))


def _output_table(results: list[Asset]) -> None:
    """Output results in table format."""
    # Header
    header = f"{'ID':<36} | {'Model Name':<20} | {'Host Name':<25} | {'Location':<30}"
    separator = "-" * len(header)

    click.echo(separator)
    click.echo(header)
    click.echo(separator)

    # Rows
    for asset in results:
        row = (
            f"{asset.id.value:<36} | "
            f"{asset.model_name.value:<20} | "
            f"{asset.host_name.value:<25} | "
            f"{asset.location.value:<30}"
        )
        click.echo(row)

    click.echo(separator)
    click.echo(f"Total: {len(results)} asset(s) found")
