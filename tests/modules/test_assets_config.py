"""資産管理機能の設定モデルのテスト"""

import pytest
from pydantic import ValidationError

from moro.modules.assets.config import AssetsConfig


class TestAssetsConfig:
    """AssetsConfig のテスト"""

    def test_assets_config_デフォルト設定(self) -> None:
        """デフォルト設定で正常に作成されることを確認"""
        config = AssetsConfig()

        assert config.api_base_url == "http://localhost:8000"
        assert config.bearer_token == ""
        assert config.protocol == "rest"
        assert config.timeout == 30
        assert config.retry_count == 3

    def test_assets_config_カスタム設定(self) -> None:
        """カスタム設定で正常に作成されることを確認"""
        config = AssetsConfig(
            api_base_url="https://api.example.com",
            bearer_token="test-token-12345",  # noqa: S106
            protocol="graphql",
            timeout=60,
            retry_count=5,
        )

        assert config.api_base_url == "https://api.example.com"
        assert config.bearer_token == "test-token-12345"  # noqa: S105
        assert config.protocol == "graphql"
        assert config.timeout == 60
        assert config.retry_count == 5

    def test_assets_config_無効なプロトコル(self) -> None:
        """無効なプロトコルで作成が失敗することを確認"""
        with pytest.raises(ValidationError):
            AssetsConfig(protocol="invalid-protocol")  # type: ignore[arg-type]

    def test_assets_config_無効なタイムアウト_負の値(self) -> None:
        """負のタイムアウト値で作成が失敗することを確認"""
        with pytest.raises(ValidationError):
            AssetsConfig(timeout=-1)

    def test_assets_config_無効なリトライ回数_負の値(self) -> None:
        """負のリトライ回数で作成が失敗することを確認"""
        with pytest.raises(ValidationError):
            AssetsConfig(retry_count=-1)

    def test_assets_config_無効なurl形式(self) -> None:
        """無効なURL形式で作成が失敗することを確認"""
        with pytest.raises(ValidationError):
            AssetsConfig(api_base_url="invalid-url")

    def test_assets_config_境界値_タイムアウト最小値(self) -> None:
        """タイムアウト最小値で正常に作成されることを確認"""
        config = AssetsConfig(timeout=1)
        assert config.timeout == 1

    def test_assets_config_境界値_リトライ回数最小値(self) -> None:
        """リトライ回数最小値で正常に作成されることを確認"""
        config = AssetsConfig(retry_count=0)
        assert config.retry_count == 0

    def test_assets_config_境界値_タイムアウト最大値(self) -> None:
        """タイムアウト最大値で正常に作成されることを確認"""
        config = AssetsConfig(timeout=300)
        assert config.timeout == 300

    def test_assets_config_境界値_リトライ回数最大値(self) -> None:
        """リトライ回数最大値で正常に作成されることを確認"""
        config = AssetsConfig(retry_count=10)
        assert config.retry_count == 10
