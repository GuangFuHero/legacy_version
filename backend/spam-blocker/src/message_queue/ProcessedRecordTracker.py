import logging
from typing import Optional

import redis

logger = logging.getLogger(__name__)


class ProcessedRecordTracker:
    """使用 Redis 追蹤已處理記錄"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.processed_set_key = "processed_records"
        self.last_processed_key = "last_processed_id"
        self.valid_records_key = "valid_records"
        self.invalid_records_key = "invalid_records"
        self.retry_count_key_prefix = "retry_count:"  # 記錄重試次數

    def is_processed(self, record_id: str) -> bool:
        """檢查是否已處理"""
        return self.redis.sismember(self.processed_set_key, record_id)

    def mark_as_processed(self, record_id: str):
        """標記為已處理"""
        self.redis.sadd(self.processed_set_key, record_id)
        self.redis.set(self.last_processed_key, record_id)
        logger.info(f"記錄 {record_id} 已標記為已處理")

    def mark_as_valid(self, record_id: str):
        """標記為有效記錄"""
        self.redis.sadd(self.valid_records_key, record_id)

    def mark_as_invalid(self, record_id: str):
        """標記為無效記錄"""
        self.redis.sadd(self.invalid_records_key, record_id)

    def get_last_processed_id(self) -> Optional[str]:
        """取得最後處理的記錄 ID"""
        result = self.redis.get(self.last_processed_key)
        return result.decode("utf-8") if result else None

    def get_processed_count(self) -> int:
        """取得已處理記錄數量"""
        return self.redis.scard(self.processed_set_key)

    def get_valid_count(self) -> int:
        """取得有效記錄數量"""
        return self.redis.scard(self.valid_records_key)

    def get_invalid_count(self) -> int:
        """取得無效記錄數量"""
        return self.redis.scard(self.invalid_records_key)

    def get_retry_count(self, record_id: str) -> int:
        """取得記錄的重試次數"""
        key = f"{self.retry_count_key_prefix}{record_id}"
        count = self.redis.get(key)
        return int(count) if count else 0

    def increment_retry_count(self, record_id: str) -> int:
        """增加記錄的重試次數，回傳新的次數"""
        key = f"{self.retry_count_key_prefix}{record_id}"
        new_count = self.redis.incr(key)
        # 設定過期時間 7 天，避免永久佔用記憶體
        self.redis.expire(key, 7 * 24 * 60 * 60)
        return new_count

    def clear_retry_count(self, record_id: str):
        """清除記錄的重試次數"""
        key = f"{self.retry_count_key_prefix}{record_id}"
        self.redis.delete(key)
