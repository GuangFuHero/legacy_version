#!/bin/bash

# Redis 快速檢查腳本 - 一次顯示所有重要資訊

set -e

REDIS_CONTAINER=${REDIS_CONTAINER:-"spam-blocker-redis"}

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}   Redis 快速狀態檢查${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 檢查容器
if ! docker ps --format '{{.Names}}' | grep -q "^${REDIS_CONTAINER}$"; then
    echo -e "${RED}錯誤: Redis 容器 '${REDIS_CONTAINER}' 未運行${NC}"
    exit 1
fi

redis_cmd() {
    docker exec ${REDIS_CONTAINER} redis-cli "$@" 2>/dev/null | tr -d '\r'
}

# 基本統計
echo -e "${GREEN}【基本統計】${NC}"
PROCESSED_COUNT=$(redis_cmd SCARD processed_records)
LAST_ID=$(redis_cmd GET last_processed_id)
VALID_COUNT=$(redis_cmd SCARD valid_records)
INVALID_COUNT=$(redis_cmd SCARD invalid_records)

echo "  已處理記錄總數: $PROCESSED_COUNT"
echo "  最後處理的 ID: $LAST_ID"
echo "  有效記錄數: $VALID_COUNT"
echo "  無效記錄數: $INVALID_COUNT"
echo ""

# 隊列狀態
echo -e "${GREEN}【隊列狀態】${NC}"
HR_QUEUE_SIZE=$(redis_cmd LLEN human_resource_validation_queue)
SUPPLIES_QUEUE_SIZE=$(redis_cmd LLEN supplies_validation_queue)

echo "  人力資源隊列: $HR_QUEUE_SIZE 筆"
echo "  物資隊列: $SUPPLIES_QUEUE_SIZE 筆"
echo ""

# 初始載入狀態
echo -e "${GREEN}【初始載入狀態】${NC}"
HR_ALL_LOADED=$(redis_cmd GET spam_blocker:all_records_loaded:human_resource)
SUPPLIES_ALL_LOADED=$(redis_cmd GET spam_blocker:all_records_loaded:supplies)

if [ -z "$HR_ALL_LOADED" ]; then
    echo -e "  人力資源: ${YELLOW}未完成初始載入${NC}"
else
    echo -e "  人力資源: ${GREEN}已完成初始載入${NC}"
fi

if [ -z "$SUPPLIES_ALL_LOADED" ]; then
    echo -e "  物資: ${YELLOW}未完成初始載入${NC}"
else
    echo -e "  物資: ${GREEN}已完成初始載入${NC}"
fi
echo ""

# 記憶體使用
echo -e "${GREEN}【記憶體使用】${NC}"
MEMORY_INFO=$(redis_cmd INFO memory | grep "used_memory_human:" | cut -d: -f2 | tr -d '\r')
echo "  使用記憶體: $MEMORY_INFO"
echo ""

# 檢查最近 5 筆處理記錄
echo -e "${GREEN}【最近記錄 ID（隨機取樣 5 筆）】${NC}"
redis_cmd SRANDMEMBER processed_records 5 | head -5
echo ""

echo -e "${BLUE}================================${NC}"
echo "提示: 執行 ./scripts/check_redis_processed.sh 進入完整互動模式"

