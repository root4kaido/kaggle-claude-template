#!/bin/bash

# Kaggle Models APIを使ったモデルアップロードスクリプト
# Usage: ./upload_model.sh <experiment_name> [options]
#
# Options:
#   --model-dir DIR        アップロード対象のディレクトリ（デフォルト: workspace/<exp>/results）
#   --model-name NAME      Kaggle上のモデル名（デフォルト: KAGGLE_MODEL_NAME変数）
#   --variation NAME       バリエーション名（デフォルト: experiment_name）
#   --framework NAME       フレームワーク（デフォルト: KAGGLE_MODEL_FRAMEWORK変数）
#   --description TEXT     モデルの説明
#
# Examples:
#   ./upload_model.sh exp001_baseline
#   ./upload_model.sh exp001_baseline --model-dir workspace/exp001_baseline/results/best_model
#   ./upload_model.sh exp001_baseline --variation exp001_fold0 --framework pyTorch

set -e

# ============================================================
# コンペごとにカスタマイズするセクション
# ============================================================
KAGGLE_MODEL_NAME="MyModels"           # Kaggle上のモデル名
KAGGLE_MODEL_FRAMEWORK="pyTorch"       # pyTorch / tensorFlow / jax / other
KAGGLE_MODEL_DESCRIPTION="Model"       # モデルの説明
# ============================================================

# === Parse arguments ===
EXP_NAME=""
MODEL_DIR=""
MODEL_NAME="${KAGGLE_MODEL_NAME}"
VARIATION_NAME=""
FRAMEWORK="${KAGGLE_MODEL_FRAMEWORK}"
DESCRIPTION="${KAGGLE_MODEL_DESCRIPTION}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --model-dir)
            MODEL_DIR="$2"
            shift 2
            ;;
        --model-name)
            MODEL_NAME="$2"
            shift 2
            ;;
        --variation)
            VARIATION_NAME="$2"
            shift 2
            ;;
        --framework)
            FRAMEWORK="$2"
            shift 2
            ;;
        --description)
            DESCRIPTION="$2"
            shift 2
            ;;
        -*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            if [ -z "$EXP_NAME" ]; then
                EXP_NAME="$1"
            fi
            shift
            ;;
    esac
done

if [ -z "$EXP_NAME" ]; then
    echo "Error: Experiment name required."
    echo "Usage: ./upload_model.sh <experiment_name> [options]"
    echo ""
    echo "Options:"
    echo "  --model-dir DIR        アップロード対象のディレクトリ"
    echo "  --model-name NAME      Kaggle上のモデル名"
    echo "  --variation NAME       バリエーション名"
    echo "  --framework NAME       フレームワーク (pyTorch/tensorFlow/jax/other)"
    echo "  --description TEXT     モデルの説明"
    exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EXP_DIR="${PROJECT_ROOT}/workspace/${EXP_NAME}"

# Default model directory
if [ -z "$MODEL_DIR" ]; then
    MODEL_DIR="${EXP_DIR}/results"
fi

# Default variation name = experiment name
if [ -z "$VARIATION_NAME" ]; then
    VARIATION_NAME="$EXP_NAME"
fi

# Validate model directory
if [ ! -d "$MODEL_DIR" ]; then
    echo "Error: Model directory not found: ${MODEL_DIR}"
    exit 1
fi

# Get Kaggle username
KAGGLE_USERNAME=""
if [ -f ~/.kaggle/kaggle.json ]; then
    KAGGLE_USERNAME=$(cat ~/.kaggle/kaggle.json | grep "username" | cut -d'"' -f4)
fi
if [ -z "$KAGGLE_USERNAME" ]; then
    echo "Enter your Kaggle username:"
    read KAGGLE_USERNAME
fi
echo "Kaggle username: ${KAGGLE_USERNAME}"

# Create temp directory (within project to comply with no-/tmp rule)
TEMP_DIR="${PROJECT_ROOT}/.tmp/kaggle-model-upload-${MODEL_NAME}-${VARIATION_NAME}"
rm -rf "${TEMP_DIR}"
MODEL_META_DIR="${TEMP_DIR}/model"
VARIATION_DIR="${TEMP_DIR}/variation"
UPLOAD_DIR="${VARIATION_DIR}/${VARIATION_NAME}"
mkdir -p "${MODEL_META_DIR}" "${UPLOAD_DIR}"

# Copy model files
echo "Copying files from ${MODEL_DIR}..."
cp -r "${MODEL_DIR}/." "${UPLOAD_DIR}/"

echo ""
echo "Files to upload:"
find "${UPLOAD_DIR}" -type f | sort
echo ""
TOTAL_SIZE=$(du -sh "${UPLOAD_DIR}" | cut -f1)
echo "Total size: ${TOTAL_SIZE}"

# Check if model already exists
MODEL_EXISTS=false
if kaggle models list --owner "${KAGGLE_USERNAME}" 2>/dev/null | grep -q "${KAGGLE_USERNAME}/${MODEL_NAME}"; then
    MODEL_EXISTS=true
    echo "Model ${KAGGLE_USERNAME}/${MODEL_NAME} already exists."
fi

# Create model if needed
if [ "$MODEL_EXISTS" = false ]; then
    echo "Creating new model: ${KAGGLE_USERNAME}/${MODEL_NAME}"
    cat > "${MODEL_META_DIR}/model-metadata.json" << EOL
{
  "title": "${MODEL_NAME}",
  "id": "${KAGGLE_USERNAME}/${MODEL_NAME}",
  "ownerSlug": "${KAGGLE_USERNAME}",
  "slug": "${MODEL_NAME}",
  "isPrivate": true,
  "licenses": [{"name": "Apache 2.0"}],
  "description": "${DESCRIPTION}",
  "collaborators": []
}
EOL
    kaggle models create -p "${MODEL_META_DIR}"
fi

# Create variation metadata
echo "Preparing variation metadata..."
cat > "${VARIATION_DIR}/model-instance-metadata.json" << EOL
{
  "id": "${KAGGLE_USERNAME}/${MODEL_NAME}/${FRAMEWORK}/${VARIATION_NAME}",
  "instanceSlug": "${VARIATION_NAME}",
  "modelId": "${KAGGLE_USERNAME}/${MODEL_NAME}",
  "ownerSlug": "${KAGGLE_USERNAME}",
  "modelSlug": "${MODEL_NAME}",
  "framework": "${FRAMEWORK}",
  "slug": "${VARIATION_NAME}",
  "title": "${VARIATION_NAME}",
  "modelVersionName": "1.0",
  "modelVersionDescription": "${DESCRIPTION} - ${VARIATION_NAME}",
  "isPrivate": true,
  "licenseName": "Apache 2.0"
}
EOL

# Upload
echo "Uploading variation ${VARIATION_NAME}..."
if kaggle models instances create -p "${VARIATION_DIR}" --dir-mode zip; then
    echo "Variation created successfully."
else
    echo "Variation exists, updating..."
    kaggle models instances versions create -p "${VARIATION_DIR}" \
        --version-notes "Updated ${VARIATION_NAME}" \
        --dir-mode zip \
        "${KAGGLE_USERNAME}/${MODEL_NAME}/${FRAMEWORK}/${VARIATION_NAME}"
fi

# Cleanup
rm -rf "${TEMP_DIR}"

echo ""
echo "==================================================="
echo "Upload complete!"
echo "  ${KAGGLE_USERNAME}/${MODEL_NAME}/${FRAMEWORK}/${VARIATION_NAME}"
echo "  https://www.kaggle.com/models/${KAGGLE_USERNAME}/${MODEL_NAME}"
echo "==================================================="
