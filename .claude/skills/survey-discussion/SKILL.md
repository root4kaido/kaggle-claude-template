---
name: survey-discussion
description: Kaggleのディスカッションを調査する。playwright-cliでブラウザを操作し、注目トピックの内容を分析する。
allowed-tools: Bash(playwright-cli:*)
---

# ディスカッション調査スキル

## 手順

1. **コンペURLの確認**: `CLAUDE.md` からコンペURLを取得

2. **ブラウザでDiscussion一覧を開く**:
   ```bash
   playwright-cli open "https://www.kaggle.com/competitions/{comp-slug}/discussion"
   ```

3. **一覧の探索**:
   - `playwright-cli snapshot` でDOM状態を確認
   - スクロールして一覧を読み込む
   - 各トピックのタイトル、投票数、コメント数を把握
   - ソート切り替え（Most Votes / Hotness / Recent）で異なる切り口も確認

4. **個別トピックの深掘り**:
   - 気になるトピックをクリックして内容を確認
   - `playwright-cli snapshot` や `playwright-cli eval` でテキストを抽出
   - コメント欄の有用な情報もチェック
   - 関連リンク・参照先があれば辿る

5. **結果の整理**:
   - `docs/survey/discussion/activity_summary.md` に分析レポートを更新
   - 重要な発見があれば `eda/eda_summary.md` の知見セクションにも追記

6. **レポート**: 注目ディスカッションのサマリーを報告
   - 公式アナウンスメント
   - 有用なテクニック・知見の共有
   - データに関する議論・注意点

7. **後片付け**:
   ```bash
   playwright-cli close
   ```
