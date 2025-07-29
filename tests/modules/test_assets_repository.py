"""資産管理ドメインの Repository とSearchCriteria のテスト"""

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


class TestSearchCriteria:
    """SearchCriteria のテスト"""

    def test_search_criteria_id検索条件作成(self) -> None:
        """ID検索条件が正常に作成されることを確認"""
        asset_id = str(uuid4())
        criteria = SearchCriteria.by_id(asset_id)

        assert criteria.asset_id == asset_id
        assert criteria.model_name is None
        assert criteria.location is None

    def test_search_criteria_機種名検索条件作成(self) -> None:
        """機種名検索条件が正常に作成されることを確認"""
        model = "Cisco Catalyst 9300"
        criteria = SearchCriteria.by_model_name(model)

        assert criteria.asset_id is None
        assert criteria.model_name == model
        assert criteria.location is None

    def test_search_criteria_ロケーション検索条件作成(self) -> None:
        """ロケーション検索条件が正常に作成されることを確認"""
        location = "Tokyo-DataCenter-Rack01"
        criteria = SearchCriteria.by_location(location)

        assert criteria.asset_id is None
        assert criteria.model_name is None
        assert criteria.location == location

    def test_search_criteria_複合検索条件作成(self) -> None:
        """複合検索条件が正常に作成されることを確認"""
        asset_id = str(uuid4())
        model = "Cisco Catalyst 9300"
        location = "Tokyo-DataCenter-Rack01"

        criteria = SearchCriteria(
            asset_id=asset_id,
            model_name=model,
            location=location,
        )

        assert criteria.asset_id == asset_id
        assert criteria.model_name == model
        assert criteria.location == location

    def test_search_criteria_空の検索条件(self) -> None:
        """空の検索条件が正常に作成されることを確認"""
        criteria = SearchCriteria()

        assert criteria.asset_id is None
        assert criteria.model_name is None
        assert criteria.location is None


class MockAssetRepository(AssetRepository):
    """テスト用のAssetRepositoryモック実装"""

    def __init__(self) -> None:
        """モックリポジトリの初期化"""
        self._assets: list[Asset] = []

    def add_asset(self, asset: Asset) -> None:
        """テスト用にアセットを追加"""
        self._assets.append(asset)

    async def search(self, criteria: SearchCriteria) -> Optional[list[Asset]]:
        """検索条件に基づいてアセットを検索"""
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


class TestAssetRepository:
    """AssetRepository インターフェースのテスト"""

    def test_repository_id検索_1件ヒット(self) -> None:
        """ID検索で1件ヒットすることを確認"""
        # テストデータ準備
        asset_id = AssetId(value=str(uuid4()))
        asset = Asset(
            id=asset_id,
            model_name=ModelName(value="Cisco Catalyst 9300"),
            host_name=HostName(value="switch01.example.com"),
            location=Location(value="Tokyo-DataCenter-Rack01"),
        )

        repo = MockAssetRepository()
        repo.add_asset(asset)

        # 検索実行
        import asyncio
        criteria = SearchCriteria.by_id(asset_id.value)
        results = asyncio.run(repo.search(criteria))

        # 結果確認
        assert results is not None
        assert len(results) == 1
        assert results[0] == asset

    def test_repository_機種名検索_複数件ヒット(self) -> None:
        """機種名検索で複数件ヒットすることを確認"""
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

        repo = MockAssetRepository()
        repo.add_asset(asset1)
        repo.add_asset(asset2)

        # 検索実行
        import asyncio
        criteria = SearchCriteria.by_model_name(model_name)
        results = asyncio.run(repo.search(criteria))

        # 結果確認
        assert results is not None
        assert len(results) == 2
        assert asset1 in results
        assert asset2 in results

    def test_repository_検索結果0件(self) -> None:
        """検索結果が0件の場合の確認"""
        repo = MockAssetRepository()

        # 検索実行
        import asyncio
        criteria = SearchCriteria.by_id(str(uuid4()))
        results = asyncio.run(repo.search(criteria))

        # 結果確認
        assert results is not None
        assert len(results) == 0
