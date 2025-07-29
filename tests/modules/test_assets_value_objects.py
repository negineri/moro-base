"""資産管理ドメインの Value Objects のテスト"""

from uuid import uuid4

import pytest
from pydantic import ValidationError

from moro.modules.assets.domain.value_objects import (
    AssetId,
    HostName,
    Location,
    ModelName,
)


class TestAssetId:
    """AssetId Value Object のテスト"""

    def test_asset_id_正常作成_有効なuuid形式(self) -> None:
        """有効なUUID文字列でAssetIdが正常に作成されることを確認"""
        valid_uuid = str(uuid4())
        asset_id = AssetId(value=valid_uuid)
        assert asset_id.value == valid_uuid

    def test_asset_id_作成失敗_無効なuuid形式(self) -> None:
        """無効なUUID形式でAssetId作成が失敗することを確認"""
        with pytest.raises(ValidationError):
            AssetId(value="invalid-uuid")

    def test_asset_id_作成失敗_空文字(self) -> None:
        """空文字でAssetId作成が失敗することを確認"""
        with pytest.raises(ValidationError):
            AssetId(value="")


class TestModelName:
    """ModelName Value Object のテスト"""

    def test_model_name_正常作成_有効な機種名(self) -> None:
        """有効な機種名でModelNameが正常に作成されることを確認"""
        model = "Cisco Catalyst 9300"
        model_name = ModelName(value=model)
        assert model_name.value == model

    def test_model_name_作成失敗_空文字(self) -> None:
        """空文字でModelName作成が失敗することを確認"""
        with pytest.raises(ValidationError):
            ModelName(value="")

    def test_model_name_作成失敗_空白のみ(self) -> None:
        """空白文字のみでModelName作成が失敗することを確認"""
        with pytest.raises(ValidationError):
            ModelName(value="   ")


class TestHostName:
    """HostName Value Object のテスト"""

    def test_host_name_正常作成_有効なホスト名(self) -> None:
        """有効なホスト名でHostNameが正常に作成されることを確認"""
        hostname = "switch01.example.com"
        host_name = HostName(value=hostname)
        assert host_name.value == hostname

    def test_host_name_作成失敗_空文字(self) -> None:
        """空文字でHostName作成が失敗することを確認"""
        with pytest.raises(ValidationError):
            HostName(value="")

    def test_host_name_作成失敗_空白のみ(self) -> None:
        """空白文字のみでHostName作成が失敗することを確認"""
        with pytest.raises(ValidationError):
            HostName(value="   ")


class TestLocation:
    """Location Value Object のテスト"""

    def test_location_正常作成_有効なロケーション(self) -> None:
        """有効なロケーション情報でLocationが正常に作成されることを確認"""
        location = "Tokyo-DataCenter-Rack01"
        location_obj = Location(value=location)
        assert location_obj.value == location

    def test_location_作成失敗_空文字(self) -> None:
        """空文字でLocation作成が失敗することを確認"""
        with pytest.raises(ValidationError):
            Location(value="")

    def test_location_作成失敗_空白のみ(self) -> None:
        """空白文字のみでLocation作成が失敗することを確認"""
        with pytest.raises(ValidationError):
            Location(value="   ")

    def test_location_正常作成_日本語文字含む(self) -> None:
        """日本語文字含むロケーション名で正常に作成されることを確認"""
        location = "東京データセンター-ラック01"
        location_obj = Location(value=location)
        assert location_obj.value == location
