import enum
import logging
import os
import socket
import time
from datetime import datetime
from typing import Any, Dict, List

import dotenv
from google.oauth2.service_account import (
    Credentials as ServiceAccountCredentials,
)
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .GfApiClient import HumanResource, Supplies
from .OllamaClient import ValidationResult

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class SheetName(enum.Enum):
    valid_human_resource = "valid_human_resource"
    invalid_human_resource = "invalid_human_resource"
    valid_supplies = "valid_supplies"
    invalid_supplies = "invalid_supplies"


class HumanResourceRecord(HumanResource, ValidationResult):
    """人力資源記錄的 schema"""

    validated_at: datetime


class SuppliesRecord(Supplies, ValidationResult):
    """物資記錄的 schema - 用於 Google Sheet"""

    supplies: str
    validated_at: datetime


class GoogleSheetHandler:
    """Google Sheets 處理器，支援讀取、寫入、更新和刪除操作"""

    _service = None
    _credentials = None
    credentials_path = "secret/cred.json"

    def __init__(self):
        self._ensure_service()
        self.spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")

    @classmethod
    def _ensure_service(cls):
        """確保 service 已經建立，如果沒有則建立一個"""
        if cls._service is None:
            cls._authenticate()

    @classmethod
    def _authenticate(cls) -> None:
        """使用 JSON 憑證檔案進行認證（只執行一次）"""
        try:
            if cls._credentials is None:
                if cls.credentials_path:
                    cls._credentials = ServiceAccountCredentials.from_service_account_file(
                        cls.credentials_path, scopes=SCOPES
                    )
                else:
                    raise ValueError("必須提供 credentials_path")

            cls._service = build("sheets", "v4", credentials=cls._credentials)
            logger.info("Google Sheets API 使用 JSON 憑證認證成功")

        except Exception as e:
            logger.error(f"Google Sheets API 認證失敗: {e}")
            raise

    @property
    def service(self):
        """取得共享的 service 實例"""
        return self._service

    def append_sheet(self, sheet_name: SheetName, values: List[List[str]], max_retries: int = 3) -> Dict[str, Any]:
        """
        在 Google Sheets 末尾追加資料（帶重試機制）

        Args:
            sheet_name: 目標分頁
            values: 要追加的資料（二維陣列）
            max_retries: 最大重試次數

        Returns:
            API 回應
        """
        for attempt in range(max_retries):
            try:
                body = {"values": values}

                result = (
                    self.service.spreadsheets()
                    .values()
                    .append(
                        spreadsheetId=self.spreadsheet_id,
                        range=f"{sheet_name.value}!A:A",
                        valueInputOption="RAW",
                        insertDataOption="INSERT_ROWS",
                        body=body,
                    )
                    .execute()
                )

                logger.info(f"成功追加 {len(values)} 行資料")
                return result

            except (TimeoutError, socket.timeout, OSError) as error:
                if attempt < max_retries - 1:
                    wait_time = 2**attempt
                    logger.warning(f"請求超時，{wait_time}秒後重試 (嘗試 {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    logger.error(f"追加資料失敗，已達最大重試次數: {error}")
                    raise

            except HttpError as error:
                logger.error(f"追加 Google Sheets 資料時發生錯誤: {error}")
                raise

    def append_record(self, record: HumanResource | Supplies, validation_result, sheet_name: str) -> None:
        """寫入一筆資料，根據 sheet_name 判斷資料類型"""
        try:
            if "human_resource" in sheet_name:
                record_obj = HumanResourceRecord(
                    id=record.id,
                    org=record.org,
                    address=record.address,
                    role_name=record.role_name,
                    assignment_notes=record.assignment_notes,
                    valid=validation_result.valid,
                    reason=validation_result.reason,
                    validated_at=datetime.now(),
                )
                fields = ["id", "org", "address", "role_name", "assignment_notes", "valid", "reason", "validated_at"]
            elif "supplies" in sheet_name:
                supplies_list = record.supplies

                supplies_items = []
                for item in supplies_list:
                    supply_info = f"{item.name} ({item.unit})"
                    supplies_items.append(supply_info)

                supplies_str = " / ".join(supplies_items)
                logger.info(f"轉換後的 supplies 字串: {supplies_str}")

                record_obj = SuppliesRecord(
                    id=record.id,
                    name=record.name,
                    address=record.address,
                    supplies=supplies_str,
                    valid=validation_result.valid,
                    reason=validation_result.reason,
                    validated_at=datetime.now(),
                )
                fields = ["id", "name", "address", "supplies", "valid", "reason", "validated_at"]
            else:
                raise ValueError(f"Unknown sheet_name: {sheet_name}")

            row_data = []
            for field in fields:
                value = getattr(record_obj, field)
                if isinstance(value, datetime):
                    formatted_value = value.isoformat()
                else:
                    formatted_value = str(value) if value is not None else ""
                row_data.append(formatted_value)

            self.append_sheet(SheetName[sheet_name], [row_data])
            logger.info(f"已寫入資料到 {sheet_name}: {record_obj.id}")

        except Exception as e:
            logger.error(f"寫入資料時發生錯誤: {e}")
            raise
