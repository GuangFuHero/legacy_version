import logging

from lib import (
    GfApiClient,
    GoogleSheetHandler,
    HumanResource,
    OllamaClient,
    Supplies,
    ValidationResult,
)
from message_queue import ProcessedRecordTracker

logger = logging.getLogger(__name__)


class RecordProcessor:
    """記錄處理器 - 負責驗證記錄和上傳結果"""

    def __init__(
        self,
        validator: OllamaClient,
        gf_api_client: GfApiClient,
        google_sheet_handler: GoogleSheetHandler,
        tracker: ProcessedRecordTracker,
        resource_type: str,
    ):
        """
        Args:
            validator: Ollama 驗證客戶端
            gf_api_client: GF API 客戶端
            google_sheet_handler: Google Sheet 處理器
            tracker: 已處理記錄追蹤器
            resource_type: 資源類型 (human_resource 或 supplies)
        """
        self.validator = validator
        self.gf_api_client = gf_api_client
        self.google_sheet_handler = google_sheet_handler
        self.tracker = tracker
        self.resource_type = resource_type

    def process_record(self, record: HumanResource | Supplies) -> bool:
        """
        處理一筆記錄：驗證 -> 上傳 -> 標記為已處理

        Returns:
            bool: 處理是否成功
        """
        record_id = record.id

        try:
            logger.info(f"開始處理記錄: {record_id}")

            validation_result = self.validator.get_validation_result(record, self.resource_type)

            if not validation_result:
                logger.error(f"記錄 {record_id} 驗證失敗")
                return False

            if validation_result.valid:
                sheet_name = f"valid_{self.resource_type}"
            elif not validation_result.valid:
                sheet_name = f"invalid_{self.resource_type}"
                self.submit_spam_judgment(record, validation_result)

            logger.info(f"validation_result: {validation_result}")

            self.upload_result(record, validation_result, sheet_name)

            return True

        except Exception as e:
            logger.error(f"處理記錄 {record_id} 時發生錯誤: {e}", exc_info=True)
            return False

    def submit_spam_judgment(self, record: HumanResource | Supplies, validation_result: ValidationResult) -> None:
        """透過 GF API 提交 SPAM 判定"""
        self.gf_api_client.submit_spam_judgment(
            record.id,
            self.resource_type,
            record.model_dump(),
            validation_result.valid,
            validation_result.reason,
        )

    def upload_result(self, record: HumanResource | Supplies, validation_result, sheet_name: str) -> None:
        """上傳記錄到 Google Sheet 並標記為已處理"""
        record_id = record.id

        try:
            self.google_sheet_handler.append_record(record, validation_result, sheet_name)
            logger.info(f"{sheet_name} {record_id} 上傳完成")

            self.tracker.mark_as_processed(record_id)
            logger.info(f"記錄 {record_id} 已標記為已處理")
        except Exception as e:
            logger.error(f"上傳記錄 {record_id} 時發生錯誤: {e}", exc_info=True)
            raise
