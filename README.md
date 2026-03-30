# kaggle-claude-template

Claude Codeを使ったKaggleコンペ用テンプレートリポジトリ。

## 概要

- 実験管理、EDA、ノートブック/ディスカッション調査などのスキルを備えたKaggleコンペ作業環境
- 詳細は [CLAUDE.md](CLAUDE.md) を参照

## ディレクトリ構成

```
├── CLAUDE.md                  # 作業規約・プロジェクト設定
├── .claude/                   # Claude Code設定・スキル
├── datasets/                  # データセット（raw / processed）
├── docs/                      # ドキュメント・サーベイ
├── eda/                       # EDA分析結果
├── workspace/                 # 実験フォルダ群
├── src/                       # 共有ユーティリティ
└── tools/                     # ツールスクリプト
```

## 主なスキル

| コマンド | 内容 |
|---------|------|
| `/experiment` | 新規実験フォルダ作成 |
| `/eda` | 探索的データ分析 |
| `/evaluate` | 全実験の結果集約 |
| `/survey-notebooks` | Kaggleノートブック調査 |
| `/survey-discussion` | Kaggleディスカッション調査 |
| `/survey-papers` | 論文・類似コンペ解法調査 |
