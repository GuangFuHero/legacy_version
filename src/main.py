import logging
import os
import time
from logging.handlers import RotatingFileHandler

import dotenv
import redis
import schedule

from lib import GfApiClient, GoogleSheetHandler, OllamaClient
from message_queue import (
    MessageQueueProcessor,
    ProcessedRecordTracker,
    Scheduler,
)
from wokers import RecordFetcher, RecordProcessor

logger = logging.getLogger(__name__)

dotenv.load_dotenv()

rotating_file_handler = RotatingFileHandler("logs/main.log", maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[rotating_file_handler, logging.StreamHandler()],
)


def create_processor_components(
    validator: OllamaClient,
    gf_api_client: GfApiClient,
    google_sheet_handler: GoogleSheetHandler,
    redis_url: str,
    queue_name: str,
    resource_type: str,
) -> tuple[MessageQueueProcessor, Scheduler]:
    """
    創建處理器組件

    Returns:
        (MessageQueueProcessor, Scheduler)
    """
    redis_client = redis.from_url(redis_url, decode_responses=False)
    tracker = ProcessedRecordTracker(redis_client)

    record_processor = RecordProcessor(
        validator=validator,
        gf_api_client=gf_api_client,
        google_sheet_handler=google_sheet_handler,
        tracker=tracker,
        resource_type=resource_type,
    )

    queue_processor = MessageQueueProcessor(
        record_processor=record_processor,
        redis_url=redis_url,
        queue_name=queue_name,
    )

    fetcher = RecordFetcher(
        tracker=tracker,
        queue_checker=queue_processor._is_record_in_queue,
    )

    scheduler = Scheduler(
        fetcher=fetcher,
        gf_api_client=gf_api_client,
        redis_client=redis_client,
        add_to_queue_func=queue_processor.add_to_queue,
        resource_type=resource_type,
    )

    return queue_processor, scheduler


if __name__ == "__main__":
    """主程式 - 使用 Message Queue"""

    validator = OllamaClient()
    gf_api_client = GfApiClient()
    google_sheet_handler = GoogleSheetHandler()

    redis_url = os.getenv("REDIS_URL")
    fetch_limit = int(os.getenv("FETCH_LIMIT", 50))
    offset = int(os.getenv("OFFSET", 0))

    hr_queue_processor, hr_scheduler = create_processor_components(
        validator=validator,
        gf_api_client=gf_api_client,
        google_sheet_handler=google_sheet_handler,
        redis_url=redis_url,
        queue_name="human_resource_validation_queue",
        resource_type="human_resource",
    )

    supplies_queue_processor, supplies_scheduler = create_processor_components(
        validator=validator,
        gf_api_client=gf_api_client,
        google_sheet_handler=google_sheet_handler,
        redis_url=redis_url,
        queue_name="supplies_validation_queue",
        resource_type="supplies",
    )

    try:
        import threading

        hr_queue_processor.start()
        supplies_queue_processor.start()

        schedule.every(1).minutes.do(hr_scheduler.scheduled_fetch, limit=fetch_limit, offset=offset)
        schedule.every(1).minutes.do(supplies_scheduler.scheduled_fetch, limit=fetch_limit, offset=offset)

        hr_scheduler.scheduled_fetch(limit=fetch_limit)
        supplies_scheduler.scheduled_fetch(limit=fetch_limit)

        hr_thread = threading.Thread(target=hr_queue_processor.process_queue, daemon=True)
        supplies_thread = threading.Thread(target=supplies_queue_processor.process_queue, daemon=True)

        hr_thread.start()
        supplies_thread.start()

        logger.info("所有處理器已啟動")

        while True:
            schedule.run_pending()
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("收到中斷信號")
    finally:
        hr_queue_processor.stop()
        supplies_queue_processor.stop()
