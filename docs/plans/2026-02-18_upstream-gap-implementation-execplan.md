# upstream 差分を現行拡張と両立して実装する

This ExecPlan is a living document. The sections `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` must be kept up to date as work proceeds.

本ドキュメントは `execplan` スキルの PLANS methodology に準拠して保守する。実装者はこのファイルだけを読めば、`$PWD` の現行コードベースで作業を再開できる状態を維持すること。

## Purpose / Big Picture

この変更後、`site2skill` は upstream で追加された機能差分を取り込みつつ、fork 独自の拡張（`skill_description`、`--skip-package`、`--full-sync`、`--replace-skill-md`、Query Building 記述）を壊さずに利用できる。利用者は target agent を指定して適切な出力先にスキルを生成でき、生成コンテンツは `references/` を正規ディレクトリとして扱いながら legacy `docs/` も互換サポートする。さらに、ローカルで再現可能なテストと CI が追加され、変更の正しさを継続的に検証できる。

目で見える完了条件は、`site2skill --target codex` などの実行が成功し、生成スキルが `references/` ベースで検索・検証でき、`uv run pytest` が成功し、CI 定義が同等の検証を自動実行することである。

## Progress

- [x] (2026-02-18 16:33Z) レポート差分と現行コードの不整合を整理し、統合方針を確定した。
- [x] (2026-02-18 16:39Z) Milestone 1 完了。`--target`、target 別出力先、`utils.py` 導入、package 条件分岐を実装した。
- [x] (2026-02-18 16:40Z) Milestone 2 完了。`references/` 正規化と `docs/` fallback を生成・検索・検証へ実装した。
- [x] (2026-02-18 16:41Z) Milestone 3 完了。`tests/`、fixtures、optional `skills_ref` テスト、`pyproject.toml` の dev group、CI workflow を追加した。
- [x] (2026-02-18 16:42Z) Milestone 4 完了。README とテンプレート文面を更新し、自動テストと手動シナリオを実施した。
- [x] (2026-02-18 16:42Z) 受け入れ検証完了。`uv run pytest` 12 passed、codex/claude-desktop の package 条件分岐を実機確認した。

## Surprises & Discoveries

- Observation: リポジトリ root には実行可能なテスト群がなく、テストファイルは `docs/examples/upstream-site2skill` サブモジュール側にのみ存在する。
  Evidence: `rg --files -g 'test*.py' -g '*test*.py'` の結果が `docs/examples/upstream-site2skill/...` のみだった。

- Observation: `scripts/README.md` は `--category` オプションを記載しているが、`site2skill/templates/search_docs.py` は `--category` を受け付けない。
  Evidence: `site2skill/templates/scripts_README.md` と `site2skill/templates/search_docs.py` の引数定義差分。

- Observation: 手動検証コマンドとして `python` は使えず `python3` または venv の Python が必要だった。
  Evidence: `zsh:1: command not found: python` が発生。

- Observation: `uv run python ...` は sandbox で `~/.cache/uv` 参照が拒否されるケースがあり、今回の環境では `./.venv/bin/python` が安定した。
  Evidence: `failed to open file ... $HOME/.cache/uv/... Operation not permitted` が発生。

## Decision Log

- Decision: upstream 差分を取り込む際、fork 独自拡張は削除せず共存させる。
  Rationale: 利用者の既存フロー互換を保ちつつ、upstream の機能改善を得ることが目的だから。
  Date/Author: 2026-02-18 / Codex

- Decision: 生成コンテンツは `references/` を正とし、`docs/` は読み取り互換のみ維持する。
  Rationale: upstream 方針に合わせつつ、既存利用者の skill 資産が壊れない移行パスが必要だから。
  Date/Author: 2026-02-18 / Codex

- Decision: パッケージングは `target == claude-desktop` かつ `--skip-package` 未指定のときのみ実行する。
  Rationale: upstream の target 依存挙動を導入しつつ、fork の明示的 skip フラグを優先するため。
  Date/Author: 2026-02-18 / Codex

- Decision: 手動受け入れ検証は `./.venv/bin/python -m site2skill.main ...` を正とする。
  Rationale: 本環境で `python` 不在、`uv run python` が sandbox 制約で不安定だったため、最小依存で再現できる経路を採用した。
  Date/Author: 2026-02-18 / Codex

## Outcomes & Retrospective

計画で定義した機能差分は実装完了。`main.py` は target aware になり、`generate_skill_structure.py` は references 正規化と legacy docs 互換、`validate_skill.py` と `search_docs.py` は fallback 対応となった。`tests/` と CI も追加し、`uv run pytest` で 12 passed を確認した。

手動シナリオでは `--target codex` + `--skip-package` で package 未生成、`--target claude-desktop` で `.skill` 生成を確認し、期待された user-visible behavior を満たした。依存追加に伴う `uv.lock` の差分も作業中に反映済み。

## Context and Orientation

このリポジトリの実装中心は `site2skill` パッケージで、CLI エントリポイントは `site2skill/main.py`。HTML 収集後の変換・正規化・スキル構造生成・検証・パッケージ化を直列実行している。現在の生成先は `docs/` 固定で、検索と検証も `docs/` 固定前提で書かれている。

変更対象の主要ファイルは以下。

- `site2skill/main.py`: CLI 引数、出力先決定、HTML->MD パス算出、パッケージング条件分岐。
- `site2skill/generate_skill_structure.py`: `SKILL.md` 生成、コンテンツディレクトリ作成、スクリプト配置、Markdown コピー。
- `site2skill/validate_skill.py`: スキル構造検証とサイズ検査。
- `site2skill/templates/search_docs.py`: 生成スキル内検索ツール。
- `site2skill/templates/scripts_README.md`: 生成スクリプト説明。
- `README.md`: CLI と生成物の説明。
- `pyproject.toml` と `uv.lock`: 開発依存・テスト実行環境。
- `.github/workflows/test.yml`: CI。
- `tests/...`（新規作成）: 単体・統合テスト、fixtures。

ここでいう “target agent” は、生成されたスキルをどのエージェント実行環境向けに配置するかを決める CLI パラメータで、`--output` を明示しないときの既定出力先に影響する。ここでいう “legacy docs fallback” は、`references/` が無い既存スキルでも `docs/` を読み取って検索・検証が動作する互換仕様を意味する。

## Plan of Work

### Milestone 1: CLI・変換パス・パッケージ条件の統合

まず `site2skill/main.py` に `--target` を追加し、`--output` 未指定時は target ごとの既定ディレクトリを使う。既存 positional の `skill_description` と fork 独自フラグは残す。`--output` が指定された場合は target より優先する。

次に upstream 由来の utility を `site2skill/utils.py` として新設し、`html_to_md_path` と `sanitize_path` を `main.py` で利用する。これにより HTML 変換出力のパス生成を共通化し、記号を含むパス要素でのファイル名問題を抑止する。

最後にパッケージング条件を再設計する。`--skip-package` は最優先で package 処理を止める。そのうえで `target != claude-desktop` は package を自動スキップし、`target == claude-desktop` のみ package を実行する。

この時点の受け入れ基準は、CLI 引数パースが壊れず、`--target codex` で `site2skill` が `build/markdown` まで正常進行し、パッケージング分岐ログが仕様どおりになること。

### Milestone 2: references 正規化と互換フォールバック

`site2skill/generate_skill_structure.py` を拡張し、コンテンツ出力先を `references/` に切り替える。`SKILL.md` のドキュメント説明と Usage 文面は `references/` 優先 + `docs/` fallback に更新する。ただし fork 独自の Query Building セクションは維持する。`skill_description`, `full_sync`, `replace_skill_md` は既存互換で維持する。

`full_sync` の挙動は `references/` と `docs/` の両方を掃除対象に拡張し、再実行時の stale ファイル混入を防ぐ。コピー処理は `references/` に対して path traversal 防止を継続する。

`site2skill/validate_skill.py` と `site2skill/templates/search_docs.py` は、`references/` があれば優先し、なければ `docs/` を使用する。両方なければエラーにする。サイズ検査も同じ優先順位に合わせる。これで新旧 skill 構造の両方が運用できる。

この時点の受け入れ基準は、新規生成 skill が `references/` を持ち、検索とバリデーションが `references/` と `docs/` のどちらでも通ること。

### Milestone 3: テスト・依存・CI の導入

root に `tests/` を新設し、upstream のテストを土台に現行仕様へ合わせて再配置する。具体的には、パス変換、生成構造、target 分岐、legacy fallback、packaging 条件の回帰を網羅する。`skills_ref` に依存する検証テストは `pytest.importorskip("skills_ref")` で optional とし、未導入環境でもテスト全体が破綻しないようにする。

`pyproject.toml` に `dependency-groups.dev` を追加し、`pytest` と `skills-ref`（Python バージョン条件付き）を導入する。必要なら `pytest` の探索対象を `tests/` に限定し、`docs/examples/upstream-site2skill` 配下を誤って収集しないようにする。

`.github/workflows/test.yml` を追加し、CI で依存同期とテスト実行を自動化する。ローカルと CI のコマンドは揃え、結果解釈を統一する。

この時点の受け入れ基準は、`uv run pytest` が green で、CI 設定ファイルが同じ検証ステップを実行すること。

### Milestone 4: 文書化と最終受け入れ

`README.md` を更新し、CLI usage に `--target` と output 優先順位、`references/` への移行方針、package 条件（claude-desktop のみ自動 package）を明記する。`site2skill/templates/scripts_README.md` も `references/` 優先挙動に合わせる。

最後に end-to-end の手動検証シナリオを実行し、target ごとの生成先、検索、検証、package 条件の実動作を確認する。結果は本計画の `Outcomes & Retrospective` と `Artifacts and Notes` に追記し、将来の再実行者が同じ確認を辿れる状態にする。

## Concrete Steps

作業ディレクトリはすべて `$PWD` を前提とする。以下は実装時に順番どおり実行する。

1. 現状確認。

    cd $PWD
    git status --short
    rg --files site2skill

2. Milestone 1 実装。`site2skill/main.py` と `site2skill/utils.py` を編集し、CLI と path utility と packaging 条件を反映する。

3. Milestone 2 実装。`site2skill/generate_skill_structure.py`、`site2skill/validate_skill.py`、`site2skill/templates/search_docs.py`、`site2skill/templates/scripts_README.md` を更新する。

4. Milestone 3 実装。`tests/` 一式と `pyproject.toml`、必要なら `pytest` 設定、`.github/workflows/test.yml` を追加する。依存ロック更新が必要なら `uv lock` を実行する。

5. Milestone 4 実装。`README.md` を更新し、受け入れテストを実行する。

6. テスト実行。

    cd $PWD
    uv run pytest

   期待結果:

    - 失敗 0。
    - `skills_ref` 未導入時は該当テストが skip 扱いで終了する。

7. 手動シナリオ検証（ネットワーク依存を避けるため `--skip-fetch` と fixture を利用）。

    cd $PWD
    ./.venv/bin/python -m site2skill.main https://example.com sample-skill --target codex --output build/manual/skills --skip-fetch --temp-dir build/manual --skip-package

   期待結果:

    - `build/manual/skills/sample-skill/references/` が生成される。
    - `build/manual/skills/sample-skill/scripts/search_docs.py` が存在し実行権限を持つ。
    - package は作成されない。

## Validation and Acceptance

受け入れは挙動で判定する。コンパイル可能性や lint だけでは完了としない。

まず自動テストとして `uv run pytest` を実行し、target 分岐、references fallback、path sanitize、SKILL frontmatter、validation/search compatibility が検証されること。特に、新規テストで「変更前に落ち、変更後に通る」シナリオを最低 1 件ずつ用意する。

次に手動で 2 系統を確認する。`--target claude-desktop` の場合は `--skip-package` 無しで `.skill` が作成されること、`--target codex` の場合は package が作成されないこと。どちらも `validate_skill` が成功し、`search_docs.py` が `references/` を読めることを確認する。

最後に legacy 互換を確認する。`references/` を持たず `docs/` のみを持つ fixture skill を用意し、`validate_skill` と `search_docs.py` がフォールバック動作することを確認する。

## Idempotence and Recovery

この計画は再実行可能である。主要編集は加法的で、同じ差分を再適用しても破壊的変更にならないようにする。`full_sync` の実装変更は runtime 挙動なので、実装途中で壊れた場合は対象関数単位でテストを先に通してから次に進む。

依存更新や lock 更新で競合した場合は、`pyproject.toml` と `uv.lock` を同時に扱い、片方だけを残さない。テスト失敗時は最小再現ケースを固定し、`main.py` の分岐か `generate_skill_structure.py` の出力先制御かを切り分けて戻す。

もし途中で仕様を変える必要が出た場合は、このファイルの `Decision Log` と `Progress` を更新してから実装を継続する。これにより、次の実装者が中断地点から安全に再開できる。

## Artifacts and Notes

実行ログ要約:

- `uv run pytest`:

    collected 12 items
    12 passed in 0.30s

- codex target (`--skip-package`):

    === Step 6: Skipping Packaging Skill ===
    Skill directory: build/manual_codex/skills/sample-codex

- claude-desktop target:

    === Step 6: Packaging Skill ===
    Skill package: ./sample-desktop.skill

生成物抜粋:

    build/manual_codex/skills/sample-codex/
      SKILL.md
      references/example.com/index.md
      scripts/search_docs.py

    build/manual_desktop/skills/sample-desktop/
      SKILL.md
      references/example.com/index.md
      scripts/search_docs.py

権限確認:

    -rwxr-xr-x ... build/manual_codex/skills/sample-codex/scripts/search_docs.py
    -rwxr-xr-x ... build/manual_desktop/skills/sample-desktop/scripts/search_docs.py

## Interfaces and Dependencies

最終状態で以下のインターフェイスを満たすこと。

- `site2skill/main.py`
  - CLI に `--target` を持つ。
  - `--output` 未指定時の既定値は target で決まる。
  - package 実行条件は `target == "claude-desktop"` かつ `not --skip-package`。

- `site2skill/utils.py`（新規）
  - `sanitize_path(path: str) -> str`
  - `html_to_md_path(html_path: str) -> str`

- `site2skill/generate_skill_structure.py`
  - 既存シグネチャに互換を保ちつつ `target_agent` を追加する。
  - `references/` を生成先にし、`SKILL.md` で `references/` 優先を説明する。
  - `replace_skill_md` と `skill_description` は既存どおり機能する。
  - `full_sync` は `references/` と legacy `docs/` の両方を整合的にクリアできる。
  - `scripts/search_docs.py` に実行権限 (`0o755`) を付与する。

- `site2skill/validate_skill.py`
  - `references/` 優先、`docs/` fallback のディレクトリ解決ヘルパーを持つ。
  - サイズ計測と markdown 件数カウントが fallback に対応する。

- `site2skill/templates/search_docs.py`
  - `references/` があれば優先して走査し、なければ `docs/` を走査する。

- テスト/依存/CI
  - `tests/` 配下で pytest ベースの回帰テストが動く。
  - `pyproject.toml` に dev dependency group が追加される。
  - `.github/workflows/test.yml` がテストを自動実行する。

## Plan Update Notes

- 2026-02-18 (initial draft): レポート `docs/notes/2026-02-18_upstream-site2skill-gap-report.md` の未導入差分を、fork 独自機能との互換を維持して実装するための実行計画を新規作成。
- 2026-02-18 (execution update): Milestone 1-4 を完了し、進捗・意思決定・検証結果・成果物ログを反映。
