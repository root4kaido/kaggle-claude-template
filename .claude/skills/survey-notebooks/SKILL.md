---
name: survey-notebooks
description: Kaggleのノートブック（Code）を調査する。playwright-cliでブラウザを操作し、人気ノートブックの内容・手法を分析する。解法リサーチやアイデア探索に使う。
allowed-tools: Bash(playwright-cli:*)
---

# ノートブック調査スキル

## 手順

1. **コンペURLの確認**: `CLAUDE.md` からコンペURLを取得し、Code（Notebook）ページのURLを構成
   - 例: `https://www.kaggle.com/competitions/{comp-slug}/code`

2. **ブラウザでNotebook一覧を開く**:
   ```bash
   playwright-cli open "https://www.kaggle.com/competitions/{comp-slug}/code?sortBy=voteCount"
   ```

3. **一覧の探索**:
   - `playwright-cli snapshot` でDOM状態を確認
   - スクロールして一覧を読み込む: `playwright-cli eval "window.scrollTo(0, document.body.scrollHeight)"`
   - 各ノートブックのタイトル、投票数、著者を把握
   - 気になるノートブックがあればクリックして詳細を確認
   - ソート切り替え（Most Votes / Hotness / Recently Created）で異なる切り口も確認

4. **個別ノートブックの深掘り**:
   - ノートブックページを開いてコード・手法を確認
   - `playwright-cli snapshot` や `playwright-cli eval` でセル内容を抽出
   - ノートブックをダウンロードしたい場合は、ページ上のダウンロードボタンを押す（Kaggle APIは使わない）
     - ダウンロード先: `docs/survey/notebooks/downloaded/`
   - 注目ポイント:
     - 使用ライブラリ・モデル
     - 前処理・特徴量エンジニアリングの手法
     - 独自のアイデア・テクニック

5. **結果の整理**:
   - `docs/survey/notebooks/notebook_summary.md` に分析レポートを更新
     - 上位ノートブックの手法一覧
     - 使用されている特徴量・モデルの傾向
     - 独自のアイデア・テクニック
   - 重要な発見があれば `eda/eda_summary.md` の知見セクションにも追記

6. **レポート**: 注目ノートブックのサマリーを報告
   - 手法別の分類（特徴量系、モデル系、アンサンブル系等）
   - 我々の実験に取り入れるべきアイデアの提案（堅実案＋爆発案）

7. **後片付け**:
   ```bash
   playwright-cli close
   ```
