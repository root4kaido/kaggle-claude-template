---
name: survey-discussion
description: Kaggleのディスカッションを調査する。kaggle CLI (competitions topics) でトピック一覧・本文を取得し、注目トピックの内容を分析する。定点観測・差分分析に使う。
allowed-tools: Bash(kaggle:*)
---

# ディスカッション調査スキル

kaggle CLI v2.2.0+ の `competitions topics` を使い、ブラウザを使わずにディスカッションを取得・分析する（公式APIなのでスクレイピングより堅牢。旧来の403問題も解消済み）。

> **実行ルール**: `kaggle` はPython由来のCLIなので、`CLAUDE.md` のtmuxルールに従い **tmux send-keys（dev0 / dev1）で実行**し、`capture-pane` で結果を取得すること。直接bashで実行しない。

## 手順

1. **コンペslugの確認**: `CLAUDE.md` のコンペURLから slug を取得（例: `birdclef-2026`）

2. **トピック一覧の取得**:
   ```bash
   # vote上位（top）/ 新着（new）/ アクティブ（active）で切り替え
   kaggle competitions topics list <comp-slug> --sort-by top
   kaggle competitions topics list <comp-slug> --sort-by new -p 2   # 2ページ目
   ```
   - `--sort-by`: `hot` / `top` / `new` / `recent` / `active` / `relevance`
   - 1ページ20件。`-p` でページ送り、`-v` でCSV出力
   - 各トピックの **ID・タイトル・投票数・コメント数** を把握

3. **個別トピックの深掘り**:
   ```bash
   kaggle competitions topics show <comp-slug> <topic-id> --page-size 200
   ```
   - トピック本文＋コメントツリーを一括取得（最大200件/ページ）
   - 有用な情報・関連リンク・参照先を辿る

4. **結果の整理**:
   - `docs/survey/discussion/activity_summary.md` に分析レポートを更新
   - 重要な発見があれば `eda/eda_summary.md` の知見セクションにも追記

5. **レポート**: 注目ディスカッションのサマリーを報告
   - 公式アナウンスメント
   - 有用なテクニック・知見の共有
   - データに関する議論・注意点
