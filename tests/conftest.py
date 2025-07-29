"""共通のテスト設定とfixture."""

import pytest

from moro.config.settings import ConfigRepository


@pytest.fixture
def config_repository() -> ConfigRepository:
    """ConfigRepositoryのテスト用fixture."""
    return ConfigRepository()
