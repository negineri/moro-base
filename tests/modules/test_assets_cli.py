"""資産管理 CLI コマンドのテスト"""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

from click.testing import CliRunner

from moro.modules.assets.cli.assets import assets
from moro.modules.assets.domain.entity import Asset
from moro.modules.assets.domain.value_objects import (
    AssetId,
    HostName,
    Location,
    ModelName,
)


class TestAssetsCLI:
    """Assets CLI コマンドのテスト"""

    def test_cli_assets_search_id検索_正常実行(self) -> None:
        """`moro assets search --id=<uuid>` コマンドの正常実行を確認"""
        runner = CliRunner()

        # テストデータ準備
        asset_id = str(uuid4())
        mock_asset = Asset(
            id=AssetId(value=asset_id),
            model_name=ModelName(value="Cisco Catalyst 9300"),
            host_name=HostName(value="switch01.example.com"),
            location=Location(value="Tokyo-DataCenter-Rack01"),
        )

        with patch("moro.modules.assets.cli.assets.AssetSearchUseCase") as mock_usecase_class:
            mock_usecase = AsyncMock()
            mock_usecase.search_by_id.return_value = [mock_asset]
            mock_usecase_class.return_value = mock_usecase

            result = runner.invoke(assets, ["search", "--id", asset_id])

            # 結果確認
            assert result.exit_code == 0
            assert asset_id in result.output
            assert "Cisco Catalyst 9300" in result.output
            assert "switch01.example.com" in result.output
            assert "Tokyo-DataCenter-Rack01" in result.output

    def test_cli_assets_search_機種名検索_正常実行(self) -> None:
        """`moro assets search --model=<model>` コマンドの正常実行を確認"""
        runner = CliRunner()

        # テストデータ準備
        model_name = "Cisco Catalyst 9300"
        mock_assets = [
            Asset(
                id=AssetId(value=str(uuid4())),
                model_name=ModelName(value=model_name),
                host_name=HostName(value="switch01.example.com"),
                location=Location(value="Tokyo-DataCenter-Rack01"),
            ),
            Asset(
                id=AssetId(value=str(uuid4())),
                model_name=ModelName(value=model_name),
                host_name=HostName(value="switch02.example.com"),
                location=Location(value="Tokyo-DataCenter-Rack02"),
            ),
        ]

        with patch("moro.modules.assets.cli.assets.AssetSearchUseCase") as mock_usecase_class:
            mock_usecase = AsyncMock()
            mock_usecase.search_by_model_name.return_value = mock_assets
            mock_usecase_class.return_value = mock_usecase

            result = runner.invoke(assets, ["search", "--model", model_name])

            # 結果確認
            assert result.exit_code == 0
            assert "switch01.example.com" in result.output
            assert "switch02.example.com" in result.output
            assert model_name in result.output

    def test_cli_assets_search_ロケーション検索_正常実行(self) -> None:
        """`moro assets search --location=<location>` コマンドの正常実行を確認"""
        runner = CliRunner()

        # テストデータ準備
        location = "Tokyo-DataCenter-Rack01"
        mock_asset = Asset(
            id=AssetId(value=str(uuid4())),
            model_name=ModelName(value="Cisco Catalyst 9300"),
            host_name=HostName(value="switch01.example.com"),
            location=Location(value=location),
        )

        with patch("moro.modules.assets.cli.assets.AssetSearchUseCase") as mock_usecase_class:
            mock_usecase = AsyncMock()
            mock_usecase.search_by_location.return_value = [mock_asset]
            mock_usecase_class.return_value = mock_usecase

            result = runner.invoke(assets, ["search", "--location", location])

            # 結果確認
            assert result.exit_code == 0
            assert location in result.output
            assert "switch01.example.com" in result.output

    def test_cli_assets_search_検索結果0件(self) -> None:
        """検索結果が0件の場合の出力確認"""
        runner = CliRunner()

        with patch("moro.modules.assets.cli.assets.AssetSearchUseCase") as mock_usecase_class:
            mock_usecase = AsyncMock()
            mock_usecase.search_by_id.return_value = []
            mock_usecase_class.return_value = mock_usecase

            result = runner.invoke(assets, ["search", "--id", str(uuid4())])

            # 結果確認
            assert result.exit_code == 0
            assert (
                "No assets found" in result.output
                or "該当する資産が見つかりませんでした" in result.output
            )

    def test_cli_assets_search_検索エラー_None返却(self) -> None:
        """検索エラー時の処理確認"""
        runner = CliRunner()

        with patch("moro.modules.assets.cli.assets.AssetSearchUseCase") as mock_usecase_class:
            mock_usecase = AsyncMock()
            mock_usecase.search_by_id.return_value = None
            mock_usecase_class.return_value = mock_usecase

            result = runner.invoke(assets, ["search", "--id", str(uuid4())])

            # 結果確認
            assert result.exit_code == 1
            assert "Error" in result.output or "エラー" in result.output

    def test_cli_assets_search_json出力(self) -> None:
        """JSON形式での出力確認"""
        runner = CliRunner()

        # テストデータ準備
        asset_id = str(uuid4())
        mock_asset = Asset(
            id=AssetId(value=asset_id),
            model_name=ModelName(value="Cisco Catalyst 9300"),
            host_name=HostName(value="switch01.example.com"),
            location=Location(value="Tokyo-DataCenter-Rack01"),
        )

        with patch("moro.modules.assets.cli.assets.AssetSearchUseCase") as mock_usecase_class:
            mock_usecase = AsyncMock()
            mock_usecase.search_by_id.return_value = [mock_asset]
            mock_usecase_class.return_value = mock_usecase

            result = runner.invoke(assets, ["search", "--id", asset_id, "--format", "json"])

            # 結果確認
            assert result.exit_code == 0
            assert '{"id":' in result.output or '"id":' in result.output
            assert asset_id in result.output

    def test_cli_assets_search_テーブル出力(self) -> None:
        """テーブル形式での出力確認"""
        runner = CliRunner()

        # テストデータ準備
        asset_id = str(uuid4())
        mock_asset = Asset(
            id=AssetId(value=asset_id),
            model_name=ModelName(value="Cisco Catalyst 9300"),
            host_name=HostName(value="switch01.example.com"),
            location=Location(value="Tokyo-DataCenter-Rack01"),
        )

        with patch("moro.modules.assets.cli.assets.AssetSearchUseCase") as mock_usecase_class:
            mock_usecase = AsyncMock()
            mock_usecase.search_by_id.return_value = [mock_asset]
            mock_usecase_class.return_value = mock_usecase

            result = runner.invoke(assets, ["search", "--id", asset_id, "--format", "table"])

            # 結果確認
            assert result.exit_code == 0
            assert "|" in result.output or "+" in result.output  # テーブル罫線
            assert asset_id in result.output

    def test_cli_assets_search_引数不足_エラー(self) -> None:
        """検索条件が指定されていない場合のエラー"""
        runner = CliRunner()

        result = runner.invoke(assets, ["search"])

        # 結果確認
        assert result.exit_code != 0
        assert "Error" in result.output or "Usage" in result.output

    def test_cli_assets_search_複数条件指定_エラー(self) -> None:
        """複数の検索条件が指定された場合のエラー"""
        runner = CliRunner()

        result = runner.invoke(
            assets, ["search", "--id", str(uuid4()), "--model", "Cisco Catalyst 9300"]
        )

        # 結果確認
        assert result.exit_code != 0
        assert "Error" in result.output or "cannot" in result.output
