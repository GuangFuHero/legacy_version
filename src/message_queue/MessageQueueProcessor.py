import json
import logging
import os
import time
from typing import Union

import redis

from lib import HumanResource, Supplies
from wokers import RecordProcessor

logger = logging.getLogger(__name__)


class MessageQueueProcessor:
    """基於 Redis Message Queue 的處理器 - 純 Queue 管理"""

    def __init__(
        self,
        record_processor: RecordProcessor,
        redis_url: str = os.getenv("REDIS_URL"),
        queue_name: str = "",
    ):
        """
        Args:
            record_processor: 記錄處理器
            redis_url: Redis 連線 URL
            queue_name: Queue 名稱
        """
        self.record_processor = record_processor
        self.redis = redis.from_url(redis_url, decode_responses=False)
        self.queue_name = queue_name
        self.is_running = False

    def _is_record_in_queue(self, record_id: str) -> bool:
        """檢查記錄是否已在 Redis queue 中"""
        try:
            queue_items = self.redis.lrange(self.queue_name, 0, -1)

            for item in queue_items:
                try:
                    record = json.loads(item)
                    if record.get("id") == record_id:
                        return True
                except json.JSONDecodeError:
                    continue

            return False
        except Exception as e:
            logger.error(f"檢查 queue 中的記錄時發生錯誤: {e}")
            return False

    def add_to_queue(self, records: list[Union[HumanResource, Supplies]]):
        """將資料加入 Redis message queue，避免重複"""
        added_count = 0
        skipped_count = 0

        for record in records:
            try:
                record_id = record.id

                if self._is_record_in_queue(record_id):
                    skipped_count += 1
                    logger.debug(f"記錄 {record_id} 已在 queue 中，跳過加入")
                    continue

                record_dict = record.model_dump() if hasattr(record, "dict") else record
                record_json = json.dumps(record_dict, ensure_ascii=False)
                self.redis.lpush(self.queue_name, record_json)
                added_count += 1
                logger.info(f"資料 {record.id} 已加入 Redis queue")

            except Exception as e:
                logger.error(f"加入 Redis queue 失敗: {e}")

        logger.info(f"Queue 更新完成：新增 {added_count} 筆，跳過 {skipped_count} 筆")

    def process_queue(self):
        """處理 Redis message queue 中的資料"""
        logger.info("開始處理 Redis queue 中的資料...")

        while self.is_running:
            try:
                result = self.redis.brpop(self.queue_name, timeout=1)

                if result:
                    _, record_json = result
                    record_dict = json.loads(record_json)

                    if "human_resource" in self.queue_name:
                        record = HumanResource(**record_dict)
                    elif "supplies" in self.queue_name:
                        record = Supplies(**record_dict)
                    else:
                        logger.error(f"未知的 queue_name: {self.queue_name}")
                        continue

                    record_id = record.id

                    logger.info(f"從 queue 取出記錄: {record_id}")

                    success = self.record_processor.process_record(record)

                    if not success:
                        self.redis.rpush(self.queue_name, record_json)
                        logger.info(f"記錄 {record_id} 處理失敗，已放回 queue 等待重試")
                        time.sleep(1)

            except json.JSONDecodeError as e:
                logger.error(f"JSON 解析錯誤: {e}")
            except Exception as e:
                if "timeout" not in str(e).lower():
                    logger.error(f"處理錯誤: {e}")
                time.sleep(0.5)

    def clear_queue(self):
        """清空 Redis queue"""
        self.redis.delete(self.queue_name)
        logger.info(f"已清空 queue: {self.queue_name}")

    def start(self):
        """啟動處理器"""
        if self.is_running:
            logger.warning("處理器已在運行中")
            return

        self.is_running = True
        logger.info(f"Redis Message Queue 處理器已啟動: {self.queue_name}")

    def stop(self):
        """停止處理器"""
        logger.info(f"正在停止 Redis Message Queue 處理器: {self.queue_name}")
        self.is_running = False
        logger.info(f"Redis Message Queue 處理器已停止: {self.queue_name}")

    def get_queue_size(self) -> int:
        """取得 Redis queue 大小"""
        return self.redis.llen(self.queue_name)

    def get_stats(self) -> dict:
        """取得統計資訊"""
        return {
            "queue_name": self.queue_name,
            "queue_size": self.get_queue_size(),
            "processed_count": self.record_processor.tracker.get_processed_count(),
            "last_processed_id": self.record_processor.tracker.get_last_processed_id(),
        }
