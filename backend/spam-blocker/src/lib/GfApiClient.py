import logging
import os

import dotenv
import requests
from pydantic import BaseModel

logger = logging.getLogger(__name__)

dotenv.load_dotenv()


class HumanResource(BaseModel):
    id: str
    org: str
    address: str
    role_name: str
    assignment_notes: str


class Supplies(BaseModel):
    """物資資料"""

    class SupplyItem(BaseModel):
        """物資項目"""

        name: str
        unit: str

    id: str
    name: str
    address: str
    supplies: list[SupplyItem]


class GfApiClient:
    """負責與 GF API 進行互動"""

    def __init__(self):
        self.gf_api_baseurl = os.getenv("GF_API_BASE_URL")
        self.gf_api_key = os.getenv("GF_API_KEY") or ""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.session.request = lambda *args, **kwargs: requests.Session.request(
            self.session, *args, timeout=kwargs.get("timeout", 30), **kwargs
        )

    def base_request(
        self,
        method: str,
        url: str,
        headers: dict = None,
        params: dict = None,
        body: dict = None,
        use_auth: bool = True,
    ):
        """基礎請求"""
        if use_auth:
            headers = headers or {}
            headers.setdefault("x-api-key", self.gf_api_key)
        response = self.session.request(method, url, headers=headers, params=params, json=body)
        return response.json()

    def get_resources(
        self,
        endpoint: str,
        model_class: type[BaseModel],
        limit: int,
        offset: int,
        **kwargs,
    ) -> list[BaseModel]:
        """通用的資源取得方法

        Args:
            endpoint: API 端點路徑（例如 "human_resources", "supplies"）
            model_class: Pydantic model 類別（例如 HumanResource, Supplies）
            limit: 限制筆數
            offset: 偏移量
            use_auth: 是否使用認證
            **kwargs: 額外的查詢參數

        Returns:
            解析後的 model 列表
        """
        all_records: list[BaseModel] = []

        params = {"limit": limit, "offset": offset, **kwargs}

        response = self.base_request(
            "GET",
            f"{self.gf_api_baseurl}/{endpoint}",
            params=params,
        )

        if response.get("totalItems", 0) == 0:
            return []

        for item in response.get("member", []):
            filtered_item = model_class(**item)
            all_records.append(filtered_item)

        logger.info(f"Total items fetched from {endpoint}: {len(all_records)}/{response['totalItems']}")

        return all_records

    def get_all_resources(
        self,
        endpoint: str,
        model_class: type[BaseModel],
        batch_size: int = 100,
        **kwargs,
    ) -> list[BaseModel]:
        """取得所有資源（分頁處理）

        Args:
            endpoint: API 端點路徑（例如 "human_resources", "supplies"）
            model_class: Pydantic model 類別（例如 HumanResource, Supplies）
            batch_size: 每次請求的筆數
            use_auth: 是否使用認證
            **kwargs: 額外的查詢參數

        Returns:
            解析後的 model 列表
        """
        all_resources: list[BaseModel] = []
        offset = 0

        while True:
            params = {"limit": batch_size, "offset": offset, **kwargs}

            response = self.base_request(
                "GET",
                f"{self.gf_api_baseurl}/{endpoint}",
                params=params,
            )

            total_items = response.get("totalItems", 0)
            if total_items == 0:
                break

            members = response.get("member", [])
            if not members:
                break

            logger.info(f"第一筆原始資料: {members[0]}")
            logger.info(model_class(**members[0]))

            for item in members:
                all_resources.append(model_class(**item))

            offset += len(members)

            if offset >= total_items:
                break

        logger.info(f"Total {endpoint} fetched: {len(all_resources)}")
        return all_resources

    def get_all_human_resources(self, **kwargs) -> list[HumanResource]:
        """取得所有人力資源"""
        return self.get_all_resources("human_resources", HumanResource, **kwargs)

    def get_all_supplies(self, **kwargs) -> list[Supplies]:
        """取得所有物資"""
        return self.get_all_resources("supplies", Supplies, **kwargs)

    def get_human_resource(self, limit: int, offset: int, **kwargs) -> list[HumanResource]:
        """取得最新幾筆人力資源"""
        return self.get_resources("human_resources", HumanResource, limit, offset, **kwargs)

    def get_supplies(self, limit: int, offset: int, **kwargs) -> list[Supplies]:
        """取得物資資料"""
        return self.get_resources("supplies", Supplies, limit, offset, **kwargs)

    def submit_spam_judgment(
        self, target_id: str, target_type: str, target_data: dict, is_spam: bool, judgment: str
    ) -> None:
        """提交 spam 判斷結果"""
        self.base_request(
            "POST",
            f"{self.gf_api_baseurl}/spam_results",
            body={
                "target_id": target_id,
                "target_type": target_type,
                "target_data": target_data,
                "is_spam": is_spam,
                "judgment": judgment,
            },
            use_auth=True,
        )
        logger.info(f"Submitted spam judgment for {target_id} of type {target_type}")


if __name__ == "__main__":
    gf_api_client = GfApiClient()
    human_resources = gf_api_client.get_human_resource(limit=100, offset=0, status="active")
    supplies = gf_api_client.get_supplies(limit=10, offset=0, embed="all")
    print(len(human_resources))
    print(len(supplies))
