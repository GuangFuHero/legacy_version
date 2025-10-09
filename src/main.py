import logging
from logging.handlers import RotatingFileHandler
import schedule
import time
import os
import dotenv

from message_queue import MessageQueueProcessor
from lib import OllamaClient, GfApiClient, GoogleSheetHandler

logger = logging.getLogger(__name__)

dotenv.load_dotenv()

rotating_file_handler = RotatingFileHandler(
    "logs/main.log", maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[rotating_file_handler, logging.StreamHandler()],
)


def run_message_queue_processor(
    processor: MessageQueueProcessor, interval_minutes: int = 1, offset: int = 0, fetch_limit: int = 50
):
    """執行 Redis message queue 處理器"""

    schedule.every(interval_minutes).minutes.do(processor.scheduled_fetch, limit=fetch_limit, offset=offset)

    logger.info(
        f"Redis Message Queue 排程器已設定：每 {interval_minutes} 分鐘抓取 {fetch_limit} 筆資料"
    )

    processor.scheduled_fetch(limit=fetch_limit)

    processor.start()

    try:
        import threading

        process_thread = threading.Thread(target=processor.process_queue, daemon=True)
        process_thread.start()

        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到中斷信號")
    finally:
        processor.stop()


if __name__ == "__main__":
    """主程式 - 使用 Message Queue"""

    validator = OllamaClient()
    gf_api_client = GfApiClient()
    google_sheet_handler = GoogleSheetHandler()

    logger.info("使用 Redis Message Queue 處理器")
    processor = MessageQueueProcessor(
        validator=validator,
        gf_api_client=gf_api_client,
        google_sheet_handler=google_sheet_handler,
    )

    fetch_limit = int(os.getenv("FETCH_LIMIT", 50))
    offset = int(os.getenv("OFFSET", 0))

    try:
        run_message_queue_processor(processor, interval_minutes=1, offset=offset, fetch_limit=fetch_limit)
    except KeyboardInterrupt:
        logger.info("收到中斷信號")
    finally:
        processor.stop()