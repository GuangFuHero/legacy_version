import os
import dotenv
import requests
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

dotenv.load_dotenv()


class HumanResource(BaseModel):
    id: str
    org: str
    address: str
    role_name: str
    assignment_notes: str


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
            headers.setdefault("Authorization", f"Bearer {self.gf_api_key}")
        response = self.session.request(method, url, headers=headers, params=params, json=body)
        return response.json()

    def get_human_resource(self, limit: int, offset: int) -> list[HumanResource]:
        """取得最新幾筆人力資源"""
        all_records: list[HumanResource] = []

        response = self.base_request(
            "GET",
            f"{self.gf_api_baseurl}/human_resources",
            params={"limit": limit, "offset": offset},
            use_auth=False,
        )

        if response["totalItems"] == 0:
            return []

        for member in response["member"]:
            filtered_member = HumanResource(**member)
            all_records.append(filtered_member)

        logger.info(f"Total items fetched: {len(all_records)}/{response['totalItems']}")

        return all_records

    def post_human_resource(self, id: str, body: dict):
        """更新人力資源"""
        response = self.session.post(
            f"{self.gf_api_baseurl}/human_resources/{id}",
            json=body,
        )
        return response.json()


if __name__ == "__main__":
    gf_api_client = GfApiClient()
    records = gf_api_client.get_human_resource(limit=10, offset=0)
    print(records)
