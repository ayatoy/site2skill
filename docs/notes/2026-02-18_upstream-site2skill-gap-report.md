# upstream-site2skill 差分調査レポート

- 作成日: 2026-02-18
- 対象リポジトリ: `$PWD`
- 比較元: `$PWD/docs/examples/upstream-site2skill` (submodule, upstream `laiso/site2skill`)

## 1. 調査範囲

- 現行リポジトリ `main`: `c384560`
- upstream 側 head: `f89fd77`
- 共通祖先: `2f108dc`
- 比較対象: `2f108dc..f89fd77` の upstream 追加コミット

## 2. 結論サマリ

`2f108dc` 以降に upstream で導入された機能のうち、現行実装に未導入と判断できる主な項目は以下。

1. ターゲットエージェント対応 (`--target`) と target ごとの出力先制御
2. `references/` 優先 + `docs/` フォールバックの互換モード
3. HTML->MD パス変換の共通ユーティリティ化とパスサニタイズ強化
4. `search_docs.py` の実行権限自動付与 (`chmod 755`)
5. `skills_ref` を使ったオフライン検証・CI・追加テスト群

## 3. 未導入機能一覧（コミット紐付け）

### 3.1 Target agent 対応

- upstream commit: `be26aa6` (`Enhance skill generation with target agent support`)
- 追加機能:
  - CLI `--target` (`claude|claude-desktop|cursor|gemini|codex`)
  - `--output` 未指定時に target ごとの既定出力先へ切替
  - 生成 `SKILL.md` frontmatter に `metadata.target_agent` を付与
  - `claude-desktop` のときのみ `.skill` パッケージ作成
- upstream 実装位置:
  - `docs/examples/upstream-site2skill/site2skill/main.py:33`
  - `docs/examples/upstream-site2skill/site2skill/main.py:54`
  - `docs/examples/upstream-site2skill/site2skill/main.py:157`
  - `docs/examples/upstream-site2skill/site2skill/generate_skill_structure.py:55`
- 現行状況:
  - 現行は `--target` 未対応、`--skip-package` フラグで制御する方式
  - `site2skill/main.py:41`
  - `site2skill/main.py:150`
  - `site2skill/generate_skill_structure.py:53`

### 3.2 references/ 優先 + legacy docs/ フォールバック

- upstream commit: `3988d35` (`Add offline skills validation and legacy docs fallback`)
- 追加機能:
  - 生成先ディレクトリを `docs/` から `references/` に移行
  - 既存スキル互換として `docs/` をフォールバック
  - 検索スクリプトとバリデータも `references/` 優先で動作
- upstream 実装位置:
  - `docs/examples/upstream-site2skill/site2skill/generate_skill_structure.py:35`
  - `docs/examples/upstream-site2skill/site2skill/templates/search_docs.py:129`
  - `docs/examples/upstream-site2skill/site2skill/validate_skill.py:13`
  - `docs/examples/upstream-site2skill/site2skill/validate_skill.py:108`
- 現行状況:
  - `docs/` 固定実装のまま
  - `site2skill/generate_skill_structure.py:37`
  - `site2skill/templates/search_docs.py:129`
  - `site2skill/validate_skill.py:98`

### 3.3 パス変換ユーティリティ化 + サニタイズ強化

- upstream commits:
  - `04bfb5c` (`Preserve directory structure when converting HTML to MD`)
  - `7ffd300` (`Extract utility functions and improve code quality`)
  - `566798e` (`improve edge case handling`)
- 追加機能:
  - `utils.py` を追加し `html_to_md_path` / `sanitize_path` を共通化
  - HTML 変換出力時にパス要素をサニタイズ（不正文字対策）
  - 空パスなどのエッジケースの安全処理
- upstream 実装位置:
  - `docs/examples/upstream-site2skill/site2skill/main.py:22`
  - `docs/examples/upstream-site2skill/site2skill/main.py:123`
  - `docs/examples/upstream-site2skill/site2skill/utils.py:8`
- 現行状況:
  - ディレクトリ構造保持自体は導入済み（`e7c5a05`）
  - ただし upstream の `utils.py` ベース共通化・サニタイズ強化は未導入
  - `site2skill/main.py:117`

### 3.4 search script 実行権限付与

- upstream commit: `c6ab9ea` (`ensure python command portability`)
- 追加機能:
  - 生成時に `scripts/search_docs.py` へ `0o755` を付与
- upstream 実装位置:
  - `docs/examples/upstream-site2skill/site2skill/generate_skill_structure.py:111`
- 現行状況:
  - 権限付与処理なし
  - `site2skill/generate_skill_structure.py:108`

### 3.5 品質保証（オフライン検証・CI・追加テスト）

- upstream commits:
  - `e9e9a57`, `ea8fbd4`, `1b89e7d`, `3988d35`
- 追加機能:
  - `skills_ref` を使った生成スキル検証テスト (`test_agentskills_integration.py`)
  - 追加統合テスト (`test_integration.py`, `test_filename_conversion.py`, `test_site2skill.py`)
  - GitHub Actions CI (`.github/workflows/test.yml`)
  - 開発依存グループ (`pytest`, `skills-ref`)
- upstream 実装位置:
  - `docs/examples/upstream-site2skill/test_agentskills_integration.py:12`
  - `docs/examples/upstream-site2skill/.github/workflows/test.yml`
  - `docs/examples/upstream-site2skill/pyproject.toml:30`
- 現行状況:
  - 本体リポジトリ側に同等のテスト/CI/依存設定は未導入

## 4. 既に取り込み済みの主な項目（参考）

- `e7c5a05` により、ファイル名フラット化をやめてディレクトリ構造保持は現行に導入済み
  - `site2skill/main.py:115`
  - `site2skill/generate_skill_structure.py:120`

## 5. 参考（upstream の追加コミット列）

`2f108dc..f89fd77`:

- `faca52b`
- `04bfb5c`
- `99258e3`
- `e9e9a57`
- `7ffd300`
- `566798e`
- `ea8fbd4`
- `1b89e7d`
- `877dec7` (merge)
- `c6ab9ea`
- `3988d35`
- `2331207` (merge)
- `be26aa6`
- `f89fd77` (merge)
