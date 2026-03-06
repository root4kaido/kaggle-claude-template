"""
Kaggle Notebook 詳細取得 (Kaggle API版)
上位ノートブックを kaggle kernels pull でダウンロードし、コード・マークダウンを解析する
"""

import json
import glob
import os
import re
import subprocess
from datetime import datetime

MAX_NOTEBOOKS = 15  # 詳細取得するノートブック数の上限
DOWNLOAD_DIR = "downloaded"


def get_latest_snapshot():
    """最新のスナップショットファイルを取得"""
    files = sorted(glob.glob("snapshot_*.json"))
    files = [f for f in files if "_details" not in f]
    if not files:
        raise FileNotFoundError("No snapshot files found. Run scrape_notebooks.py first.")
    return files[-1]


def url_to_kernel_ref(url):
    """KaggleノートブックURLからkernel参照 (user/slug) を抽出"""
    # https://www.kaggle.com/code/username/notebook-slug -> username/notebook-slug
    match = re.search(r"kaggle\.com/code/([^/]+/[^/]+)", url)
    if match:
        return match.group(1)
    return None


def download_notebook(kernel_ref, download_dir):
    """kaggle kernels pull でノートブックをダウンロード"""
    os.makedirs(download_dir, exist_ok=True)
    result = subprocess.run(
        ["kaggle", "kernels", "pull", kernel_ref, "-p", download_dir],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"kaggle kernels pull failed: {result.stderr}")

    # ダウンロードされたファイルを探す
    slug = kernel_ref.split("/")[-1]
    for ext in [".ipynb", ".py", ".r", ".rmd"]:
        path = os.path.join(download_dir, slug + ext)
        if os.path.exists(path):
            return path

    # ファイル名が見つからない場合、最新ファイルを返す
    files = sorted(glob.glob(os.path.join(download_dir, "*")), key=os.path.getmtime, reverse=True)
    return files[0] if files else None


def parse_ipynb(filepath):
    """ipynbファイルからコードセルとマークダウンセルを抽出"""
    with open(filepath, "r", encoding="utf-8") as f:
        nb = json.load(f)

    code_cells = []
    markdown_cells = []

    for cell in nb.get("cells", []):
        source = "".join(cell.get("source", []))
        if cell.get("cell_type") == "code":
            if source.strip():
                code_cells.append(source)
        elif cell.get("cell_type") == "markdown":
            if source.strip():
                markdown_cells.append(source)

    return code_cells, markdown_cells


def extract_libraries(code_cells):
    """コードセルからimportされているライブラリを抽出"""
    libraries = set()
    import_pattern = re.compile(r'(?:import|from)\s+(\w+)')
    for code in code_cells:
        for match in import_pattern.finditer(code):
            lib = match.group(1)
            # 標準的な非ライブラリを除外
            if lib not in {"os", "sys", "re", "json", "glob", "time", "datetime",
                           "math", "copy", "collections", "itertools", "functools",
                           "pathlib", "warnings", "typing", "abc", "io", "csv",
                           "pickle", "random", "string", "textwrap", "operator"}:
                libraries.add(lib)
    return sorted(libraries)


def extract_models(code_cells):
    """コードセルから使用されているモデル・手法を推定"""
    all_code = "\n".join(code_cells)
    models = []

    model_patterns = {
        "XGBoost": r"xgb\.|XGB|xgboost",
        "LightGBM": r"lgb\.|LGBM|lightgbm",
        "CatBoost": r"catboost|CatBoost|cb\.",
        "RandomForest": r"RandomForest",
        "LogisticRegression": r"LogisticRegression",
        "HistGradientBoosting": r"HistGradientBoosting",
        "GradientBoosting": r"GradientBoosting(?!Hist)",
        "Neural Network": r"keras|torch|nn\.|tensorflow",
        "ELO": r"[Ee]lo",
        "Isotonic Calibration": r"IsotonicRegression|isotonic",
        "Platt Calibration": r"CalibratedClassifier|platt",
        "Stacking": r"StackingClassifier|stacking",
    }

    for name, pattern in model_patterns.items():
        if re.search(pattern, all_code):
            models.append(name)

    return models


def extract_features(code_cells, markdown_cells):
    """特徴量エンジニアリングの手法を推定"""
    all_text = "\n".join(code_cells + markdown_cells)
    features = []

    feature_patterns = {
        "Seed": r"[Ss]eed",
        "ELO Rating": r"[Ee]lo.*[Rr]at",
        "Win Rate": r"win.*rate|win_rate|win_pct|WinPct",
        "Massey Ordinals": r"[Mm]assey|[Oo]rdinal",
        "Four Factors": r"[Ff]our.*[Ff]actor|eFG|efg_pct|TOV%|ORB%|FTRate|ft_rate",
        "Point Spread": r"point.*spread|score.*diff|margin",
        "SOS (Strength of Schedule)": r"[Ss]trength.*[Ss]chedule|SOS|sos_",
        "RPI": r"\bRPI\b|rpi_",
        "Tempo": r"[Tt]empo|[Pp]ace|possessions",
        "Home/Away": r"[Hh]ome.*[Aa]way|location|venue|neutral",
        "Conference": r"[Cc]onference|conf_",
        "Betting Odds": r"[Bb]etting|[Oo]dds|spread|vegas|538|fivethirtyeight",
        "Rolling Stats": r"rolling|last_\d+|recent_",
    }

    for name, pattern in feature_patterns.items():
        if re.search(pattern, all_text):
            features.append(name)

    return features


def scrape_details(snapshot_file=None):
    if snapshot_file is None:
        snapshot_file = get_latest_snapshot()

    with open(snapshot_file, "r", encoding="utf-8") as f:
        snapshot = json.load(f)

    notebooks = snapshot["notebooks"][:MAX_NOTEBOOKS]
    print(f"Downloading details for top {len(notebooks)} notebooks from {snapshot_file}")

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    for i, nb in enumerate(notebooks):
        url = nb["url"]
        kernel_ref = url_to_kernel_ref(url)
        if not kernel_ref:
            print(f"[{i+1}/{len(notebooks)}] Skip (invalid URL): {url}")
            nb["detail_scraped"] = False
            nb["error"] = "Could not parse kernel ref from URL"
            continue

        print(f"[{i+1}/{len(notebooks)}] {nb['title'][:60]}...")
        print(f"  kernel: {kernel_ref}")

        try:
            filepath = download_notebook(kernel_ref, DOWNLOAD_DIR)
            if not filepath:
                raise FileNotFoundError("Downloaded file not found")

            nb["local_path"] = filepath
            print(f"  -> {filepath}")

            if filepath.endswith(".ipynb"):
                code_cells, markdown_cells = parse_ipynb(filepath)

                nb["code_cells_count"] = len(code_cells)
                nb["markdown_cells_count"] = len(markdown_cells)
                nb["libraries"] = extract_libraries(code_cells)
                nb["models"] = extract_models(code_cells)
                nb["features"] = extract_features(code_cells, markdown_cells)

                # コード全体のサマリー（最初の部分）
                all_code = "\n\n# ---CELL---\n\n".join(code_cells)
                nb["code_summary"] = all_code[:15000]  # 先頭15KBまで保存

                # マークダウン内容
                all_md = "\n\n".join(markdown_cells)
                nb["markdown_summary"] = all_md[:5000]

                print(f"  -> {len(code_cells)} code cells, {len(markdown_cells)} md cells")
                print(f"     libs: {nb['libraries'][:8]}")
                print(f"     models: {nb['models']}")
                print(f"     features: {nb['features'][:6]}")
            else:
                # .py ファイル等
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                nb["code_summary"] = content[:15000]
                nb["libraries"] = extract_libraries([content])
                nb["models"] = extract_models([content])
                nb["features"] = extract_features([content], [])
                print(f"  -> script file, libs: {nb['libraries'][:8]}")

            nb["detail_scraped"] = True

        except Exception as e:
            print(f"  Error: {e}")
            nb["detail_scraped"] = False
            nb["error"] = str(e)

    # Save details
    output_file = snapshot_file.replace(".json", "_details.json")
    result = {
        "competition": snapshot["competition"],
        "scraped_at": snapshot["scraped_at"],
        "details_scraped_at": datetime.now().isoformat(),
        "total_notebooks": len(notebooks),
        "notebooks": notebooks,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Print summary
    print(f"\n{'='*60}")
    print(f"Saved details to {output_file}")
    print(f"{'='*60}")
    print(f"\nSummary:")
    for nb in notebooks:
        if nb.get("detail_scraped"):
            models = ", ".join(nb.get("models", []))
            features = ", ".join(nb.get("features", [])[:4])
            print(f"  {nb['title'][:50]:50s} | models: {models}")
            print(f"  {'':50s} | features: {features}")

    return result


if __name__ == "__main__":
    scrape_details()
