import logging
from functools import partial
from typing import Callable

import redis

from lib import GfApiClient
from wokers import RecordFetcher

logger = logging.getLogger(__name__)


class Scheduler:
    """排程器 - 協調資料抓取和 Queue 管理"""

    def __init__(
        self,
        fetcher: RecordFetcher,
        gf_api_client: GfApiClient,
        redis_client: redis.Redis,
        add_to_queue_func: Callable,
        resource_type: str,
    ):
        """
        Args:
            fetcher: 資料抓取器
            gf_api_client: GF API 客戶端
            redis_client: Redis 客戶端
            add_to_queue_func: 將記錄加入 queue 的函數
            resource_type: 資源類型 (human_resource 或 supplies)
        """
        self.fetcher = fetcher
        self.gf_api_client = gf_api_client
        self.redis = redis_client
        self.add_to_queue = add_to_queue_func
        self.resource_type = resource_type
        self.all_records_loaded_key = f"spam_blocker:all_records_loaded:{resource_type}"

    def is_all_records_loaded(self) -> bool:
        """檢查是否已載入所有記錄"""
        return self.redis.exists(self.all_records_loaded_key) > 0

    def mark_all_records_loaded(self):
        """標記已載入所有記錄"""
        self.redis.set(self.all_records_loaded_key, "1")
        logger.info(f"已標記 {self.resource_type} 所有記錄載入完成")

    def scheduled_fetch(self, limit: int = 10, offset: int = 0):
        """定時抓取任務"""
        if not self.is_all_records_loaded():
            logger.info(f"[定時任務 - {self.resource_type}] 首次執行，開始載入所有記錄...")

            if self.resource_type == "human_resource":
                get_method = partial(self.gf_api_client.get_all_human_resources, status="active")
            else:
                get_method = partial(self.gf_api_client.get_all_supplies, embed="all")

            new_records = self.fetcher.fetch_all_records(get_method)

            if new_records:
                self.add_to_queue(new_records)
                logger.info(f"[定時任務 - {self.resource_type}] 已將 {len(new_records)} 筆資料加入 Redis queue")
                self.mark_all_records_loaded()
            else:
                logger.warning(
                    f"[定時任務 - {self.resource_type}] 沒有載入到任何新資料（可能全被過濾或 API 異常），保持未完成狀態以便重試"
                )
        else:
            logger.info(f"[定時任務 - {self.resource_type}] 開始抓取最新 {limit} 筆資料...")

            if self.resource_type == "human_resource":
                get_method = partial(self.gf_api_client.get_human_resource, limit=limit, offset=offset, status="active")
            elif self.resource_type == "supplies":
                get_method = partial(self.gf_api_client.get_supplies, limit=limit, offset=offset, embed="all")

            new_records = self.fetcher.fetch_new_records(get_method)

            if new_records:
                self.add_to_queue(new_records)
                logger.info(f"[定時任務 - {self.resource_type}] 已將 {len(new_records)} 筆資料加入 Redis queue")
            else:
                logger.info(f"[定時任務 - {self.resource_type}] 沒有新資料")
