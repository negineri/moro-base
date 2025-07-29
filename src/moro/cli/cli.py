"""Entry point for the CLI."""

from logging import getLogger
from logging.config import dictConfig

import click

from moro.cli._utils import AliasedGroup
from moro.cli.assets import assets
from moro.cli.config import config
from moro.cli.example import example
from moro.config.settings import ConfigRepository

logger = getLogger(__name__)


@click.group(cls=AliasedGroup)
@click.version_option()
def cli() -> None:
    """Entry point for the CLI."""
    repo = ConfigRepository.create()

    # Configure logging
    dictConfig(repo.common.logging_config)


cli.add_command(config)
cli.add_command(example)
cli.add_command(assets)
