#!/bin/bash

echo "🔧 開始自動修正程式碼..."

echo "📦 移除未使用的 imports 和變數..."
uv run autoflake --in-place --remove-all-unused-imports --remove-unused-variables --recursive src/

echo "🧹 移除尾隨空白..."
find src -name "*.py" -type f -exec sed -i 's/[[:space:]]*$//' {} +

echo "📋 排序 imports..."
uv run isort src/

echo "✨ 使用 Black 格式化..."
uv run black src/

echo "🔍 檢查剩餘問題..."
uv run flake8 src/

echo "✅ 完成！"

