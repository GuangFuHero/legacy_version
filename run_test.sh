#!/bin/bash
# 執行單一 API 測試文件
# 使用方法: ./run_test.sh test_shelters

set -e

cd "$(dirname "$0")"

if [ -z "$1" ]; then
    echo "Usage: $0 <test_name>"
    echo ""
    echo "Available tests:"
    ls tests/test_*.hurl | xargs -n 1 basename | sed 's/\.hurl$//'
    exit 1
fi

TEST_FILE="tests/$1.hurl"
if [ ! -f "$TEST_FILE" ]; then
    TEST_FILE="tests/test_$1.hurl"
    if [ ! -f "$TEST_FILE" ]; then
        echo "❌ Error: Test file not found: $1"
        echo ""
        echo "Available tests:"
        ls tests/test_*.hurl | xargs -n 1 basename | sed 's/\.hurl$//'
        exit 1
    fi
fi

# 檢查 .env.hurl 是否存在
if [ ! -f .env.hurl ]; then
    echo "❌ Error: .env.hurl not found"
    echo "Please create .env.hurl with:"
    echo "base_url=http://localhost:8080"
    exit 1
fi

echo "🧪 Running test: $(basename $TEST_FILE)"
echo ""

hurl --test --variables-file .env.hurl "$TEST_FILE"

echo ""
echo "✅ Test passed!"
