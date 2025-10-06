import logging
import schedule
import time

from message_queue import MessageQueueProcessor
from lib import OllamaClient, GfApiClient, GoogleSheetHandler

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("../logs/main.log")],
)


def run_message_queue_processor(
    processor: MessageQueueProcessor, interval_minutes: int = 1, fetch_limit: int = 50
):
    """執行 Redis message queue 處理器"""

    schedule.every(interval_minutes).minutes.do(processor.scheduled_fetch, limit=fetch_limit)

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


def main():
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

    try:
        run_message_queue_processor(processor, interval_minutes=1, fetch_limit=10)
    except KeyboardInterrupt:
        logger.info("收到中斷信號")
    finally:
        processor.stop()


if __name__ == "__main__":
    main()
