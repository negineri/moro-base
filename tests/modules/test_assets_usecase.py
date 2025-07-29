"""資産管理ユースケースのテスト"""

from typing import Optional
from uuid import uuid4

from moro.modules.assets.domain.entity import Asset
from moro.modules.assets.domain.repository import AssetRepository, SearchCriteria
from moro.modules.assets.domain.value_objects import (
    AssetId,
    HostName,
    Location,
    ModelName,
)
from moro.modules.assets.usecase import AssetSearchUseCase


class MockAssetRepository(AssetRepository):
    """テスト用のAssetRepositoryモック実装"""

    def __init__(self) -> None:
        """モックリポジトリの初期化"""
        self._assets: list[Asset] = []
        self._should_fail = False

    def add_asset(self, asset: Asset) -> None:
        """テスト用にアセットを追加"""
        self._assets.append(asset)

    def set_failure_mode(self, should_fail: bool) -> None:
        """テスト用に失敗モードを設定"""
        self._should_fail = should_fail

    async def search(self, criteria: SearchCriteria) -> Optional[list[Asset]]:
        """検索条件に基づいてアセットを検索"""
        if self._should_fail:
            return None

        try:
            results = []
            for asset in self._assets:
                if self._matches_criteria(asset, criteria):
                    results.append(asset)
            return results
        except Exception:
            return None

    def _matches_criteria(self, asset: Asset, criteria: SearchCriteria) -> bool:
        """アセットが検索条件にマッチするかチェック"""
        if criteria.asset_id is not None:
            if asset.id.value != criteria.asset_id:
                return False

        if criteria.model_name is not None:
            if asset.model_name.value != criteria.model_name:
                return False

        if criteria.location is not None:
            if asset.location.value != criteria.location:
                return False

        return True


class TestAssetSearchUseCase:
    """AssetSearchUseCase のテスト"""

    def test_usecase_id検索_正常実行(self) -> None:
        """ID検索ユースケースが正常に実行されることを確認"""
        # テストデータ準備
        asset_id = AssetId(value=str(uuid4()))
        asset = Asset(
            id=asset_id,
            model_name=ModelName(value="Cisco Catalyst 9300"),
            host_name=HostName(value="switch01.example.com"),
            location=Location(value="Tokyo-DataCenter-Rack01"),
        )

        repository = MockAssetRepository()
        repository.add_asset(asset)
        usecase = AssetSearchUseCase(repository)

        # 検索実行
        import asyncio
        results = asyncio.run(usecase.search_by_id(asset_id.value))

        # 結果確認
        assert results is not None
        assert len(results) == 1
        assert results[0] == asset

    def test_usecase_機種名検索_正常実行(self) -> None:
        """機種名検索ユースケースが正常に実行されることを確認"""
        # テストデータ準備
        model_name = "Cisco Catalyst 9300"
        asset1 = Asset(
            id=AssetId(value=str(uuid4())),
            model_name=ModelName(value=model_name),
            host_name=HostName(value="switch01.example.com"),
            location=Location(value="Tokyo-DataCenter-Rack01"),
        )
        asset2 = Asset(
            id=AssetId(value=str(uuid4())),
            model_name=ModelName(value=model_name),
            host_name=HostName(value="switch02.example.com"),
            location=Location(value="Tokyo-DataCenter-Rack02"),
        )

        repository = MockAssetRepository()
        repository.add_asset(asset1)
        repository.add_asset(asset2)
        usecase = AssetSearchUseCase(repository)

        # 検索実行
        import asyncio
        results = asyncio.run(usecase.search_by_model_name(model_name))

        # 結果確認
        assert results is not None
        assert len(results) == 2
        assert asset1 in results
        assert asset2 in results

    def test_usecase_ロケーション検索_正常実行(self) -> None:
        """ロケーション検索ユースケースが正常に実行されることを確認"""
        # テストデータ準備
        location = "Tokyo-DataCenter-Rack01"
        asset = Asset(
            id=AssetId(value=str(uuid4())),
            model_name=ModelName(value="Cisco Catalyst 9300"),
            host_name=HostName(value="switch01.example.com"),
            location=Location(value=location),
        )

        repository = MockAssetRepository()
        repository.add_asset(asset)
        usecase = AssetSearchUseCase(repository)

        # 検索実行
        import asyncio
        results = asyncio.run(usecase.search_by_location(location))

        # 結果確認
        assert results is not None
        assert len(results) == 1
        assert results[0] == asset

    def test_usecase_検索結果0件(self) -> None:
        """検索結果が0件の場合の確認"""
        repository = MockAssetRepository()
        usecase = AssetSearchUseCase(repository)

        # 検索実行
        import asyncio
        results = asyncio.run(usecase.search_by_id(str(uuid4())))

        # 結果確認
        assert results is not None
        assert len(results) == 0

    def test_usecase_リポジトリ失敗時None返却(self) -> None:
        """リポジトリが失敗した場合にNoneが返却されることを確認"""
        repository = MockAssetRepository()
        repository.set_failure_mode(True)
        usecase = AssetSearchUseCase(repository)

        # 検索実行
        import asyncio
        results = asyncio.run(usecase.search_by_id(str(uuid4())))

        # 結果確認
        assert results is None

    def test_usecase_複合検索条件_正常実行(self) -> None:
        """複合検索条件ユースケースが正常に実行されることを確認"""
        # テストデータ準備
        asset = Asset(
            id=AssetId(value=str(uuid4())),
            model_name=ModelName(value="Cisco Catalyst 9300"),
            host_name=HostName(value="switch01.example.com"),
            location=Location(value="Tokyo-DataCenter-Rack01"),
        )

        repository = MockAssetRepository()
        repository.add_asset(asset)
        usecase = AssetSearchUseCase(repository)

        # 複合検索条件作成
        criteria = SearchCriteria(
            model_name="Cisco Catalyst 9300",
            location="Tokyo-DataCenter-Rack01",
        )

        # 検索実行
        import asyncio
        results = asyncio.run(usecase.search(criteria))

        # 結果確認
        assert results is not None
        assert len(results) == 1
        assert results[0] == asset
