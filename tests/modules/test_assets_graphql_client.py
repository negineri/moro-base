"""GraphQL API クライアントのテスト"""

import asyncio
import json
from typing import Any
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

from moro.modules.assets.config import AssetsConfig
from moro.modules.assets.domain.repository import SearchCriteria
from moro.modules.assets.infrastructure.graphql_client import GraphQLAssetRepository


class TestGraphQLAssetRepository:
    """GraphQLAssetRepository のテスト"""

    def test_graphql_client_正常初期化(self) -> None:
        """GraphQL APIクライアントが正常に初期化されることを確認"""
        config = AssetsConfig(
            api_base_url="https://api.example.com",
            bearer_token="test-token",  # noqa: S106
            timeout=30,
            retry_count=3,
        )

        client = GraphQLAssetRepository(config)
        assert client._config == config

    def test_graphql_client_id検索_正常レスポンス(self) -> None:
        """ID検索で正常なレスポンスを受信することを確認"""
        config = AssetsConfig(
            api_base_url="https://api.example.com",
            bearer_token="test-token",  # noqa: S106
        )

        # モックレスポンス作成
        asset_id = str(uuid4())
        mock_response_data = {
            "data": {
                "assets": [
                    {
                        "id": asset_id,
                        "modelName": "Cisco Catalyst 9300",
                        "hostName": "switch01.example.com",
                        "location": "Tokyo-DataCenter-Rack01",
                    }
                ]
            }
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client_class.return_value = mock_client

            client = GraphQLAssetRepository(config)
            criteria = SearchCriteria.by_id(asset_id)
            results = asyncio.run(client.search(criteria))

            # 結果確認
            assert results is not None
            assert len(results) == 1
            assert results[0].id.value == asset_id
            assert results[0].model_name.value == "Cisco Catalyst 9300"
            assert results[0].host_name.value == "switch01.example.com"
            assert results[0].location.value == "Tokyo-DataCenter-Rack01"

    def test_graphql_client_機種名検索_複数件レスポンス(self) -> None:
        """機種名検索で複数件のレスポンスを受信することを確認"""
        config = AssetsConfig(
            api_base_url="https://api.example.com",
            bearer_token="test-token",  # noqa: S106
        )

        # モックレスポンス作成
        mock_response_data = {
            "data": {
                "assets": [
                    {
                        "id": str(uuid4()),
                        "modelName": "Cisco Catalyst 9300",
                        "hostName": "switch01.example.com",
                        "location": "Tokyo-DataCenter-Rack01",
                    },
                    {
                        "id": str(uuid4()),
                        "modelName": "Cisco Catalyst 9300",
                        "hostName": "switch02.example.com",
                        "location": "Tokyo-DataCenter-Rack02",
                    },
                ]
            }
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client_class.return_value = mock_client

            client = GraphQLAssetRepository(config)
            criteria = SearchCriteria.by_model_name("Cisco Catalyst 9300")
            results = asyncio.run(client.search(criteria))

            # 結果確認
            assert results is not None
            assert len(results) == 2
            assert all(asset.model_name.value == "Cisco Catalyst 9300" for asset in results)

    def test_graphql_client_検索結果0件(self) -> None:
        """検索結果が0件の場合の確認"""
        config = AssetsConfig()

        mock_response_data: dict[str, Any] = {"data": {"assets": []}}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client_class.return_value = mock_client

            client = GraphQLAssetRepository(config)
            criteria = SearchCriteria.by_id(str(uuid4()))
            results = asyncio.run(client.search(criteria))

            # 結果確認
            assert results is not None
            assert len(results) == 0

    def test_graphql_client_接続エラー_None返却(self) -> None:
        """接続エラー時にNoneが返却されることを確認"""
        config = AssetsConfig()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post.side_effect = Exception("Connection error")
            mock_client.__aenter__.return_value = mock_client
            mock_client_class.return_value = mock_client

            client = GraphQLAssetRepository(config)
            criteria = SearchCriteria.by_id(str(uuid4()))
            results = asyncio.run(client.search(criteria))

            # 結果確認
            assert results is None

    def test_graphql_client_graphqlエラー_None返却(self) -> None:
        """GraphQLエラー時にNoneが返却されることを確認"""
        config = AssetsConfig()

        mock_response_data = {
            "errors": [
                {
                    "message": "Field 'invalid' doesn't exist on type 'Asset'",
                    "locations": [{"line": 2, "column": 3}],
                }
            ]
        }

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client_class.return_value = mock_client

            client = GraphQLAssetRepository(config)
            criteria = SearchCriteria.by_id(str(uuid4()))
            results = asyncio.run(client.search(criteria))

            # 結果確認
            assert results is None

    def test_graphql_client_500エラー_リトライ後None返却(self) -> None:
        """500エラー時にリトライ後Noneが返却されることを確認"""
        config = AssetsConfig(retry_count=2)

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 500
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client_class.return_value = mock_client

            client = GraphQLAssetRepository(config)
            criteria = SearchCriteria.by_id(str(uuid4()))
            results = asyncio.run(client.search(criteria))

            # 結果確認
            assert results is None
            # リトライ回数確認（初回 + リトライ2回 = 3回）
            assert mock_client.post.call_count == 3

    def test_graphql_client_無効なjsonレスポンス_None返却(self) -> None:
        """無効なJSONレスポンス時にNoneが返却されることを確認"""
        config = AssetsConfig()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client_class.return_value = mock_client

            client = GraphQLAssetRepository(config)
            criteria = SearchCriteria.by_id(str(uuid4()))
            results = asyncio.run(client.search(criteria))

            # 結果確認
            assert results is None

    def test_graphql_client_Bearer認証ヘッダー設定(self) -> None:
        """Bearer認証ヘッダーが正しく設定されることを確認"""
        config = AssetsConfig(
            api_base_url="https://api.example.com",
            bearer_token="test-token-12345",  # noqa: S106
        )

        mock_response_data: dict[str, Any] = {"data": {"assets": []}}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client_class.return_value = mock_client

            client = GraphQLAssetRepository(config)
            criteria = SearchCriteria.by_id(str(uuid4()))
            asyncio.run(client.search(criteria))

            # ヘッダー確認
            call_args = mock_client.post.call_args
            headers = call_args.kwargs.get("headers", {})
            assert headers.get("Authorization") == "Bearer test-token-12345"

    def test_graphql_client_複合検索条件_クエリ変数設定(self) -> None:
        """複合検索条件が正しくGraphQLクエリ変数に設定されることを確認"""
        config = AssetsConfig()

        mock_response_data: dict[str, Any] = {"data": {"assets": []}}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client_class.return_value = mock_client

            client = GraphQLAssetRepository(config)
            criteria = SearchCriteria(
                model_name="Cisco Catalyst 9300",
                location="Tokyo-DataCenter-Rack01",
            )
            asyncio.run(client.search(criteria))

            # GraphQLクエリ変数確認
            call_args = mock_client.post.call_args
            json_data = call_args.kwargs.get("json", {})
            variables = json_data.get("variables", {})
            assert variables.get("modelName") == "Cisco Catalyst 9300"
            assert variables.get("location") == "Tokyo-DataCenter-Rack01"
            assert "assetId" not in variables
