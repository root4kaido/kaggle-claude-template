---
name: survey-notebooks
description: Kaggleのノートブック（Code）を調査する。kaggle CLI (kernels) で人気ノートを一覧・取得し、内容・手法を分析する。解法リサーチやアイデア探索に使う。
allowed-tools: Bash(kaggle:*)
---

# ノートブック調査スキル

kaggle CLI の `kernels` を使い、ブラウザを使わずにノートブックを一覧・取得・分析する。

> **実行ルール**: `kaggle` はPython由来のCLIなので、`CLAUDE.md` のtmuxルールに従い **tmux send-keys（dev0 / dev1）で実行**し、`capture-pane` で結果を取得すること。直接bashで実行しない。

## 手順

1. **コンペslugの確認**: `CLAUDE.md` のコンペURLから slug を取得（例: `birdclef-2026`）

2. **ノートブック一覧の取得（vote順）**:
   ```bash
   # vote数上位を取得
   kaggle kernels list --competition <comp-slug> --sort-by voteCount --page-size 50
   # Pythonのみ / 検索語で絞り込み
   kaggle kernels list --competition <comp-slug> --language python -s "<keyword>"
   ```
   - `--sort-by`: `voteCount` / `scoreDescending` / `viewCount` / `commentCount` / `dateCreated` / `hotness` など
   - 出力の `ref`（`user/kernel-slug`）・タイトル・投票数を把握

3. **個別ノートブックの取得・深掘り**:
   ```bash
   # コード本体（.ipynb/.py + metadata）をローカルに取得
   kaggle kernels pull <user/kernel-slug> -p docs/survey/notebooks/downloaded/<slug>
   # 出力ファイルの一覧 / 取得
   kaggle kernels files <user/kernel-slug>
   kaggle kernels output <user/kernel-slug> -p docs/survey/notebooks/downloaded/<slug>
   ```
   - 注目ポイント:
     - 使用ライブラリ・モデル
     - 前処理・特徴量エンジニアリングの手法
     - 独自のアイデア・テクニック

4. **結果の整理**:
   - `docs/survey/notebooks/notebook_summary.md` に分析レポートを更新
     - 上位ノートブックの手法一覧
     - 使用されている特徴量・モデルの傾向
     - 独自のアイデア・テクニック
   - 重要な発見があれば `eda/eda_summary.md` の知見セクションにも追記

5. **レポート**: 注目ノートブックのサマリーを報告
   - 手法別の分類（特徴量系、モデル系、アンサンブル系等）
   - 我々の実験に取り入れるべきアイデアの提案（堅実案＋爆発案）
