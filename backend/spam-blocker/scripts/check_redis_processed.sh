#!/bin/bash

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REDIS_CONTAINER=${REDIS_CONTAINER:-"spam-blocker-redis"}

check_redis_container() {
    if ! docker ps --format '{{.Names}}' | grep -q "^${REDIS_CONTAINER}$"; then
        echo -e "${RED}錯誤: Redis 容器 '${REDIS_CONTAINER}' 未運行${NC}"
        echo "請使用以下命令查看運行中的容器："
        echo "  docker ps | grep redis"
        echo ""
        echo "或設置環境變數指定容器名稱："
        echo "  export REDIS_CONTAINER=<your_redis_container_name>"
        exit 1
    fi
}

redis_cmd() {
    if [ -t 0 ]; then
        docker exec -it ${REDIS_CONTAINER} redis-cli "$@"
    else
        docker exec ${REDIS_CONTAINER} redis-cli "$@"
    fi
}

show_menu() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}   Redis 已處理記錄檢查工具${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    echo "1) 查看基本統計"
    echo "2) 查看隊列大小"
    echo "3) 列出所有已處理記錄 ID"
    echo "4) 檢查特定記錄是否已處理"
    echo "5) 導出已處理記錄到文件"
    echo "6) 檢查重複記錄"
    echo "7) 刪除特定記錄（謹慎使用）"
    echo "8) 查看隊列內容（前 10 筆）"
    echo "9) 清空所有已處理記錄（危險！）"
    echo "0) 退出"
    echo ""
}

show_basic_stats() {
    echo -e "${GREEN}=== 基本統計 ===${NC}"
    
    PROCESSED_COUNT=$(redis_cmd SCARD processed_records | tr -d '\r')
    LAST_ID=$(redis_cmd GET last_processed_id | tr -d '\r')
    VALID_COUNT=$(redis_cmd SCARD valid_records | tr -d '\r')
    INVALID_COUNT=$(redis_cmd SCARD invalid_records | tr -d '\r')
    
    echo -e "已處理記錄總數: ${YELLOW}${PROCESSED_COUNT}${NC}"
    echo -e "最後處理的 ID: ${YELLOW}${LAST_ID}${NC}"
    echo -e "有效記錄數: ${GREEN}${VALID_COUNT}${NC}"
    echo -e "無效記錄數: ${RED}${INVALID_COUNT}${NC}"
    echo ""
}

show_queue_size() {
    echo -e "${GREEN}=== 隊列大小 ===${NC}"
    
    HR_QUEUE_SIZE=$(redis_cmd LLEN human_resource_validation_queue | tr -d '\r')
    SUPPLIES_QUEUE_SIZE=$(redis_cmd LLEN supplies_validation_queue | tr -d '\r')
    
    echo -e "人力資源隊列: ${YELLOW}${HR_QUEUE_SIZE}${NC} 筆"
    echo -e "物資隊列: ${YELLOW}${SUPPLIES_QUEUE_SIZE}${NC} 筆"
    echo ""
    
    echo -e "${GREEN}=== 初始載入狀態 ===${NC}"
    
    HR_ALL_LOADED=$(redis_cmd GET spam_blocker:all_records_loaded:human_resource | tr -d '\r')
    SUPPLIES_ALL_LOADED=$(redis_cmd GET spam_blocker:all_records_loaded:supplies | tr -d '\r')
    
    if [ -z "$HR_ALL_LOADED" ]; then
        echo -e "人力資源: ${YELLOW}未完成初始載入${NC}"
    else
        echo -e "人力資源: ${GREEN}已完成初始載入${NC}"
    fi
    
    if [ -z "$SUPPLIES_ALL_LOADED" ]; then
        echo -e "物資: ${YELLOW}未完成初始載入${NC}"
    else
        echo -e "物資: ${GREEN}已完成初始載入${NC}"
    fi
    echo ""
}

list_all_processed() {
    echo -e "${GREEN}=== 所有已處理記錄 ===${NC}"
    echo -e "${YELLOW}警告: 如果記錄很多，這可能需要一些時間...${NC}"
    
    redis_cmd SMEMBERS processed_records
    echo ""
}

check_specific_record() {
    echo -e "${GREEN}=== 檢查特定記錄 ===${NC}"
    read -p "請輸入記錄 ID: " RECORD_ID
    
    RESULT=$(redis_cmd SISMEMBER processed_records "$RECORD_ID" | tr -d '\r')
    
    if [ "$RESULT" == "1" ]; then
        echo -e "${GREEN}✓ 記錄 ${RECORD_ID} 已處理${NC}"
    else
        echo -e "${RED}✗ 記錄 ${RECORD_ID} 未處理${NC}"
    fi
    echo ""
}

export_processed_records() {
    echo -e "${GREEN}=== 導出已處理記錄 ===${NC}"
    
    OUTPUT_FILE="processed_records_$(date +%Y%m%d_%H%M%S).txt"
    
    redis_cmd SMEMBERS processed_records > "$OUTPUT_FILE"
    
    COUNT=$(wc -l < "$OUTPUT_FILE")
    echo -e "${GREEN}✓ 已導出 ${COUNT} 筆記錄到: ${OUTPUT_FILE}${NC}"
    echo ""
}

check_duplicates() {
    echo -e "${GREEN}=== 檢查重複記錄 ===${NC}"
    echo "正在檢查..."
    
    TEMP_FILE="/tmp/processed_records_temp.txt"
    redis_cmd SMEMBERS processed_records > "$TEMP_FILE"
    
    DUPLICATES=$(sort "$TEMP_FILE" | uniq -d)
    
    if [ -z "$DUPLICATES" ]; then
        echo -e "${GREEN}✓ 沒有發現重複記錄${NC}"
    else
        echo -e "${RED}發現重複記錄:${NC}"
        echo "$DUPLICATES"
    fi
    
    rm -f "$TEMP_FILE"
    echo ""
}

delete_specific_record() {
    echo -e "${RED}=== 刪除特定記錄 ===${NC}"
    echo -e "${YELLOW}警告: 這將從已處理記錄中移除指定的 ID${NC}"
    
    read -p "請輸入要刪除的記錄 ID: " RECORD_ID
    read -p "確定要刪除 ${RECORD_ID} 嗎? (yes/no): " CONFIRM
    
    if [ "$CONFIRM" == "yes" ]; then
        redis_cmd SREM processed_records "$RECORD_ID"
        echo -e "${GREEN}✓ 記錄 ${RECORD_ID} 已刪除${NC}"
    else
        echo -e "${YELLOW}已取消${NC}"
    fi
    echo ""
}

show_queue_content() {
    echo -e "${GREEN}=== 隊列內容（前 10 筆）===${NC}"
    echo ""
    
    echo -e "${BLUE}人力資源隊列:${NC}"
    redis_cmd LRANGE human_resource_validation_queue 0 9
    echo ""
    
    echo -e "${BLUE}物資隊列:${NC}"
    redis_cmd LRANGE supplies_validation_queue 0 9
    echo ""
}

clear_all_processed() {
    echo -e "${RED}=== 清空所有已處理記錄 ===${NC}"
    echo -e "${RED}危險: 這將刪除所有已處理記錄的追蹤資訊！${NC}"
    
    read -p "請輸入 'DELETE ALL' 來確認: " CONFIRM
    
    if [ "$CONFIRM" == "DELETE ALL" ]; then
        redis_cmd DEL processed_records
        redis_cmd DEL last_processed_id
        redis_cmd DEL valid_records
        redis_cmd DEL invalid_records
        echo -e "${GREEN}✓ 所有已處理記錄已清空${NC}"
    else
        echo -e "${YELLOW}已取消${NC}"
    fi
    echo ""
}

main() {
    check_redis_container
    
    while true; do
        show_menu
        read -p "請選擇操作 (0-9): " CHOICE
        echo ""
        
        case $CHOICE in
            1) show_basic_stats ;;
            2) show_queue_size ;;
            3) list_all_processed ;;
            4) check_specific_record ;;
            5) export_processed_records ;;
            6) check_duplicates ;;
            7) delete_specific_record ;;
            8) show_queue_content ;;
            9) clear_all_processed ;;
            0) 
                echo -e "${GREEN}再見！${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}無效的選擇，請重試${NC}"
                echo ""
                ;;
        esac
        
        read -p "按 Enter 繼續..."
        clear
    done
}

if [ $# -gt 0 ]; then
    check_redis_container
    case $1 in
        stats) show_basic_stats ;;
        queue) show_queue_size ;;
        list) list_all_processed ;;
        export) export_processed_records ;;
        duplicates) check_duplicates ;;
        content) show_queue_content ;;
        *) 
            echo "用法: $0 [stats|queue|list|export|duplicates|content]"
            echo "或直接執行 $0 進入互動模式"
            exit 1
            ;;
    esac
else
    clear
    main
fi

