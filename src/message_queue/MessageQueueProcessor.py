import json
import logging
import time
import os
import redis

from .ProcessedRecordTracker import ProcessedRecordTracker

from lib import GfApiClient, HumanResource, GoogleSheetHandler, OllamaClient

logger = logging.getLogger(__name__)


class MessageQueueProcessor:
    """基於 Redis Message Queue 的處理器"""

    def __init__(
        self,
        validator: OllamaClient,
        gf_api_client: GfApiClient,
        google_sheet_handler: GoogleSheetHandler,
        redis_url: str = os.getenv("REDIS_URL"),
        queue_name: str = "validation_queue",
    ):
        self.validator = validator
        self.gf_api_client = gf_api_client
        self.google_sheet_handler = google_sheet_handler
        self.redis = redis.from_url(redis_url, decode_responses=False)
        self.queue_name = queue_name
        self.tracker = ProcessedRecordTracker(self.redis)
        self.is_running = False

    def fetch_new_records(self, limit: int = 0, offset: int = 0) -> list[HumanResource]:
        """抓取最新的幾筆資料，過濾已處理和已在 queue 中的記錄"""
        try:
            response = self.gf_api_client.get_human_resource(limit=limit, offset=offset)

            new_records: list[HumanResource] = []
            skipped_count = 0

            for record in response:
                record_id = record.id

                if self.tracker.is_processed(record_id):
                    skipped_count += 1
                    logger.debug(f"記錄 {record_id} 已處理過，跳過")
                    continue

                if self._is_record_in_queue(record_id):
                    skipped_count += 1
                    logger.debug(f"記錄 {record_id} 已在 queue 中，跳過")
                    continue

                new_records.append(record)

            logger.info(
                f"抓取到 {len(new_records)} 筆新資料（共檢查 {len(response)} 筆，跳過 {skipped_count} 筆）"
            )
            return new_records

        except Exception as e:
            logger.error(f"抓取資料錯誤: {e}")
            return []

    def upload_record_to_google_sheet(
        self, record: dict, validation_result, sheet_name: str
    ) -> None:
        """上傳記錄到 Google Sheet"""
        try:
            record_id = record.get("id", "unknown")
            self.google_sheet_handler.append_record(record, validation_result, sheet_name)
            self.tracker.mark_as_processed(record_id)

            logger.info(f"{sheet_name} {record_id} 處理完成")

        except Exception as e:
            logger.error(f"處理有效記錄時發生錯誤: {e}", exc_info=True)

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

    def add_to_queue(self, records: list[HumanResource]):
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

                record_dict = record.dict() if hasattr(record, "dict") else record
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
                    record = json.loads(record_json)
                    record_id = record.get("id", "unknown")

                    logger.info(f"開始處理記錄: {record_id}")

                    try:
                        validation_result = self.validator.get_validation_result(record)

                        if validation_result:
                            sheet_name = "valid" if validation_result.valid else "invalid"
                            self.upload_record_to_google_sheet(
                                record, validation_result, sheet_name
                            )
                            if not validation_result.valid:
                                self.gf_api_client.submit_spam_judgment(
                                    record_id, "human_resource", record, 
                                    validation_result.valid, validation_result.reason
                                )
                        else:
                            logger.error(f"記錄 {record_id} 驗證失敗")

                    except Exception as process_error:
                        logger.error(
                            f"處理記錄 {record_id} 時發生錯誤: {process_error}", exc_info=True
                        )
                        self.redis.rpush(self.queue_name, record_json)
                        logger.info(f"記錄 {record_id} 已放回 queue 等待重試")
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

    def process_record(self, record: dict):
        """處理一筆記錄"""
        validation_result = self.validator.get_validation_result(record)
        if validation_result:
            sheet_name = "valid" if validation_result.valid else "invalid"
            self.upload_record_to_google_sheet(record, validation_result, sheet_name)

    def start(self):
        """啟動處理器"""
        if self.is_running:
            logger.warning("處理器已在運行中")
            return

        self.is_running = True
        logger.info("Redis Message Queue 處理器已啟動")

    def stop(self):
        """停止處理器"""
        logger.info("正在停止 Redis Message Queue 處理器...")
        self.is_running = False
        logger.info("Redis Message Queue 處理器已停止")

    def get_queue_size(self) -> int:
        """取得 Redis queue 大小"""
        return self.redis.llen(self.queue_name)

    def get_stats(self) -> dict:
        """取得統計資訊"""
        return {
            "queue_size": self.get_queue_size(),
            "processed_count": self.tracker.get_processed_count(),
            "last_processed_id": self.tracker.get_last_processed_id(),
        }

    def scheduled_fetch(self, limit: int = 10, offset: int = 0):
        """定時抓取任務"""
        logger.info(f"[定時任務] 開始抓取最新 {limit} 筆資料...")
        new_records = self.fetch_new_records(limit=limit, offset=offset)

        if new_records:
            self.add_to_queue(new_records)
            logger.info(f"[定時任務] 已將 {len(new_records)} 筆資料加入 Redis queue")
        else:
            logger.info("[定時任務] 沒有新資料")

        stats = self.get_stats()
        logger.info(
            f"[統計] Queue 大小: {stats['queue_size']}, 已處理: {stats['processed_count']}, "
        )
