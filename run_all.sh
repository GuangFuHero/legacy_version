#!/bin/bash
# 執行所有 API 測試

set -e  # 遇到錯誤時停止

cd "$(dirname "$0")"

echo "🧪 Running all API tests..."
echo ""

# 檢查 .env.hurl 是否存在
if [ ! -f .env.hurl ]; then
    echo "❌ Error: .env.hurl not found"
    echo "Please create .env.hurl with:"
    echo "base_url=http://localhost:8080"
    exit 1
fi

# 執行所有測試
hurl --test --variables-file .env.hurl tests/*.hurl

echo ""
echo "✅ All tests passed!"
