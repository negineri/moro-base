"""資産管理ドメインの Entity のテスト"""

from uuid import uuid4

from moro.modules.assets.domain.entity import Asset
from moro.modules.assets.domain.value_objects import (
    AssetId,
    HostName,
    Location,
    ModelName,
)


class TestAsset:
    """Asset Entity のテスト"""

    def test_asset_正常作成_有効なパラメータ(self) -> None:
        """有効なパラメータでAssetが正常に作成されることを確認"""
        asset_id = AssetId(value=str(uuid4()))
        model_name = ModelName(value="Cisco Catalyst 9300")
        host_name = HostName(value="switch01.example.com")
        location = Location(value="Tokyo-DataCenter-Rack01")

        asset = Asset(
            id=asset_id,
            model_name=model_name,
            host_name=host_name,
            location=location,
        )

        assert asset.id == asset_id
        assert asset.model_name == model_name
        assert asset.host_name == host_name
        assert asset.location == location

    def test_asset_等価性_同じid(self) -> None:
        """同じIDを持つAssetは等価であることを確認"""
        asset_id = AssetId(value=str(uuid4()))
        model_name1 = ModelName(value="Cisco Catalyst 9300")
        model_name2 = ModelName(value="Juniper EX4300")
        host_name1 = HostName(value="switch01.example.com")
        host_name2 = HostName(value="switch02.example.com")
        location1 = Location(value="Tokyo-DataCenter-Rack01")
        location2 = Location(value="Osaka-DataCenter-Rack02")

        asset1 = Asset(
            id=asset_id,
            model_name=model_name1,
            host_name=host_name1,
            location=location1,
        )
        asset2 = Asset(
            id=asset_id,
            model_name=model_name2,
            host_name=host_name2,
            location=location2,
        )

        assert asset1 == asset2

    def test_asset_非等価性_異なるid(self) -> None:
        """異なるIDを持つAssetは非等価であることを確認"""
        asset_id1 = AssetId(value=str(uuid4()))
        asset_id2 = AssetId(value=str(uuid4()))
        model_name = ModelName(value="Cisco Catalyst 9300")
        host_name = HostName(value="switch01.example.com")
        location = Location(value="Tokyo-DataCenter-Rack01")

        asset1 = Asset(
            id=asset_id1,
            model_name=model_name,
            host_name=host_name,
            location=location,
        )
        asset2 = Asset(
            id=asset_id2,
            model_name=model_name,
            host_name=host_name,
            location=location,
        )

        assert asset1 != asset2

    def test_asset_ハッシュ値_idベース(self) -> None:
        """Assetのハッシュ値がIDベースであることを確認"""
        asset_id = AssetId(value=str(uuid4()))
        model_name = ModelName(value="Cisco Catalyst 9300")
        host_name = HostName(value="switch01.example.com")
        location = Location(value="Tokyo-DataCenter-Rack01")

        asset = Asset(
            id=asset_id,
            model_name=model_name,
            host_name=host_name,
            location=location,
        )

        assert hash(asset) == hash(asset_id.value)
