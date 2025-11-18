import logging

from lib import HumanResource, Supplies
from message_queue import ProcessedRecordTracker

logger = logging.getLogger(__name__)


class RecordFetcher:
    """資料抓取器 - 負責從 API 抓取資料並過濾"""

    def __init__(self, tracker: ProcessedRecordTracker, queue_checker: callable):
        """
        Args:
            tracker: 已處理記錄追蹤器
            queue_checker: 檢查記錄是否在 queue 中的函數
        """
        self.tracker = tracker
        self.queue_checker = queue_checker

    def _filter_records(self, records: list) -> tuple[list, int]:
        """過濾已處理和已在 queue 中的記錄（使用 set 提升效率）"""
        if not records:
            return [], 0

        processed_ids = self._get_processed_ids()
        queue_ids = self._get_queue_ids()

        filtered_ids = processed_ids | queue_ids

        new_records = []
        skipped_count = 0

        for record in records:
            record_id = record.id

            if record_id in filtered_ids:
                skipped_count += 1
                if record_id in processed_ids:
                    logger.debug(f"記錄 {record_id} 已處理過，跳過")
                else:
                    logger.debug(f"記錄 {record_id} 已在 queue 中，跳過")
                continue

            new_records.append(record)

        return new_records, skipped_count

    def _get_processed_ids(self) -> set:
        """取得所有已處理記錄的 ID"""
        try:
            raw_ids = self.tracker.redis.smembers(self.tracker.processed_set_key)
            return {id.decode("utf-8") if isinstance(id, bytes) else id for id in raw_ids}
        except Exception as e:
            logger.error(f"取得已處理記錄 ID 時發生錯誤: {e}")
            return set()

    def _get_queue_ids(self) -> set:
        """取得所有在 queue 中的記錄 ID"""
        try:
            import json

            queue_ids = set()

            queue_processor = self.queue_checker.__self__
            queue_items = queue_processor.redis.lrange(queue_processor.queue_name, 0, -1)

            for item in queue_items:
                try:
                    if isinstance(item, bytes):
                        item = item.decode("utf-8")

                    record = json.loads(item)
                    record_id = record.get("id")
                    if record_id:
                        queue_ids.add(record_id)
                except (json.JSONDecodeError, KeyError):
                    continue

            return queue_ids
        except Exception as e:
            logger.error(f"取得 queue 記錄 ID 時發生錯誤: {e}")
            return set()

    def fetch_all_records(self, get_method: callable) -> list[HumanResource] | list[Supplies]:
        """抓取所有資料，過濾已處理和已在 queue 中的記錄"""
        try:
            logger.info("開始載入所有 記錄...")
            response = get_method()
            logger.info(f"response: {response}")

            new_records, skipped_count = self._filter_records(response)

            logger.info(
                f"載入所有記錄完成：抓取到 {len(new_records)} 筆新資料（共檢查 {len(response)} 筆，跳過 {skipped_count} 筆）"
            )
            return new_records
        except Exception as e:
            logger.error(f"抓取所有資料錯誤: {e}")
            return []

    def fetch_new_records(self, get_method: callable) -> list[HumanResource] | list[Supplies]:
        """抓取最新的幾筆資料，過濾已處理和已在 queue 中的記錄"""
        try:
            response = get_method()

            new_records, skipped_count = self._filter_records(response)

            logger.info(f"抓取到 {len(new_records)} 筆新資料（共檢查 {len(response)} 筆，跳過 {skipped_count} 筆）")
            return new_records
        except Exception as e:
            logger.error(f"抓取資料錯誤: {e}")
            return []
