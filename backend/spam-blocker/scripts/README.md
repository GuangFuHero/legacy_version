# Redis 管理腳本

這些腳本用於管理和監控 spam-blocker 系統的 Redis 數據。

## 腳本列表

### 1. `redis_quick_check.sh` - 快速狀態檢查

**用途：** 快速查看 Redis 的當前狀態，包括已處理記錄數、隊列大小等。

**使用方法：**
```bash
./scripts/redis_quick_check.sh
```

**輸出內容：**
- 已處理記錄總數
- 最後處理的 ID
- 有效/無效記錄數
- 隊列狀態
- 記憶體使用情況

---

### 2. `check_redis_processed.sh` - 互動式檢查工具

**用途：** 提供互動式菜單，用於詳細檢查和管理已處理記錄。

**使用方法：**

互動模式：
```bash
./scripts/check_redis_processed.sh
```

直接執行特定功能：
```bash
./scripts/check_redis_processed.sh stats        # 顯示基本統計
./scripts/check_redis_processed.sh queue        # 顯示隊列大小
./scripts/check_redis_processed.sh list         # 列出所有已處理記錄
./scripts/check_redis_processed.sh export       # 導出已處理記錄
./scripts/check_redis_processed.sh duplicates   # 檢查重複記錄
./scripts/check_redis_processed.sh content      # 顯示隊列內容
```

**功能列表：**
1. 查看基本統計
2. 查看隊列大小
3. 列出所有已處理記錄 ID
4. 檢查特定記錄是否已處理
5. 導出已處理記錄到文件
6. 檢查重複記錄
7. 刪除特定記錄（謹慎使用）
8. 查看隊列內容（前 10 筆）
9. 清空所有已處理記錄（危險！）

---

## 環境變數

所有腳本都支持自定義 Redis 容器名稱：

```bash
export REDIS_CONTAINER=your-redis-container-name
./scripts/redis_quick_check.sh
```

默認容器名稱：`spam-blocker-redis`

---

## Redis 數據結構

系統使用以下 Redis 鍵：

- `processed_records` (Set) - 所有已處理記錄的 ID
- `last_processed_id` (String) - 最後處理的記錄 ID
- `valid_records` (Set) - 有效記錄的 ID
- `invalid_records` (Set) - 無效記錄的 ID
- `human_resource_validation_queue` (List) - 人力資源驗證隊列
- `supplies_validation_queue` (List) - 物資驗證隊列

---

## 維護建議

1. **定期檢查：** 每天執行一次 `redis_quick_check.sh` 查看系統狀態
2. **監控隊列：** 如果隊列持續增長，檢查處理器是否正常運行
3. **清理策略：** 定期檢查是否有已處理但仍在隊列中的記錄
4. **備份：** 在執行清理操作前，考慮導出當前數據作為備份