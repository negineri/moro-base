# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is "moro" - a Python-based collection of miscellaneous scripts aggregated in a subcommand format. It's a personal toolbox project using Click for CLI, dependency injection with Injector, and Pydantic for configuration management.

## Development Commands

### Setup and Installation

```bash
# Install in development mode
uv run moro

# Install pre-commit hooks
pre-commit install
```

### Testing

```bash
# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Run tests across multiple Python versions
tox

# Clean coverage data
tox -e clean

# Generate coverage report
tox -e report
```

### Code Quality

```bash
# Run linter and formatter (auto-fix enabled)
ruff check

# Type checking
mypy

# All quality checks via tox
tox -e py39,py310,py311
```

### Documentation

```bash
# Build documentation
mkdocs build

# Serve documentation locally
mkdocs serve

# Build docs via tox
tox -e docs
```

### Running the CLI

```bash
# Run the main CLI
uv run moro --help

# Run specific commands
uv run moro config --help
uv run moro example --help
```

## Architecture

このプロジェクトは**レイヤードアーキテクチャ**と**依存性注入パターン**を組み合わせたモジュラー設計を採用しています。

### アーキテクチャの基本原則

1. **関心の分離**: CLI、設定、ビジネスロジックが明確に分離
2. **依存性の逆転**: 高レベルモジュールが低レベルモジュールに依存しない
3. **設定の中央集権化**: 全ての設定が`ConfigRepository`で統一管理
4. **拡張性**: 新しいコマンドやモジュールの追加が容易

### プロジェクト構造

```
src/moro/
├── cli/                    # CLIレイヤー
│   ├── _utils.py          # AliasedGroup（コマンドエイリアス機能）
│   ├── cli.py             # メインCLIエントリーポイント
│   ├── config.py          # 設定管理コマンド群
│   └── example.py         # サンプルコマンド群
├── config/                 # 設定管理レイヤー
│   ├── settings.py        # ConfigRepository、設定ローダー
│   └── settings.toml      # デフォルト設定ファイル
├── dependencies/           # 依存性注入レイヤー
│   └── container.py       # Injectorコンテナ設定
├── modules/               # 共通モジュールレイヤー
│   └── common.py          # CommonConfig（共通設定）
└── scenarios/             # ドメインレイヤー（将来のビジネスロジック）
```

### 主要コンポーネント詳細

#### 1. CLI Framework（CLI フレームワーク）

- **Click + AliasedGroup**: コマンドの部分一致実行を可能にする
- **階層型コマンド構造**: `moro config show`のようなサブコマンド形式
- **自動ヘルプ生成**: 各コマンドの使用方法が自動生成される

```python
# 例: "conf s" → "config show" として解釈される
@click.group(cls=AliasedGroup)
def config():
    pass
```

#### 2. Configuration System（設定システム）

**3 層の設定読み込み**（優先度順）:

1. **デフォルト設定**: `settings.toml`
2. **環境変数**: `MORO_*`プレフィックス
3. **実行時オプション**: プログラム引数

**設定の特徴**:

- **型安全性**: Pydantic Models による型チェック
- **ネストした環境変数**: `MORO_COMMON__JOBS=8` → `common.jobs`
- **複数パス検索**: `/etc/moro/`, `~/.config/moro/`, ローカル
- **バリデーション**: 設定値の妥当性チェック

#### 3. Dependency Injection（依存性注入）

**Injector ライブラリ**を使用した依存性管理:

```python
# ConfigRepositoryが自動的にInjectorを設定
def create_injector_builder(self) -> Callable[[Binder], None]:
    def configure(binder: Binder) -> None:
        binder.bind(ConfigRepository, to=self)
        binder.bind(CommonConfig, to=self.common)
    return configure
```

**メリット**:

- テスタビリティの向上
- 設定の一元化
- コンポーネント間の疎結合

#### 4. Modular Design（モジュラー設計）

各モジュールは独立して開発・テスト可能:

- **`modules/`**: ドメインモデルに着目してモジュールを分離、モジュール同士が参照してはならない
  - **`modules/common.py`**: common.py は全体で使用される共通設定であり、例外として他モジュールからの参照が認められる
- **`scenarios/`**: 複数のモジュールを横断するユースケースの置き場
- **拡張パターン**: 新しい CLI コマンドは`cli/`に追加し、メイン CLI に登録

### 新機能追加パターン

1. **新しい CLI コマンド**:

   ```python
   # 1. cli/new_command.py を作成
   # 2. cli/cli.py でインポート・登録
   from moro.cli.new_command import new_command
   cli.add_command(new_command)
   ```

2. **新しい設定項目**:

   ```python
   # 1. modules/に新しいConfigクラス作成
   # 2. ConfigRepositoryに追加
   # 3. settings.tomlにデフォルト値追加
   ```

3. **新しいドメイン機能**:
   ```python
   # scenarios/に新しいモジュール作成
   # 依存性注入でConfigRepositoryを取得
   ```

### テストアーキテクチャ

- **pytest**: テストフレームワーク
- **pytest-cov**: カバレッジ測定
- **polyfactory**: テストデータ生成
- **pytest-mock**: モック機能
- **tox**: 複数 Python 版でのテスト実行

## Code Style

- Line length: 100 characters
- Uses Ruff for linting and formatting with strict rules
- MyPy for type checking with strict mode
- Google-style docstrings
- Japanese comments are allowed (RUF002/003 ignored)
