import os
import dotenv
from datetime import datetime
import logging
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .GfApiClient import HumanResource
from .OllamaClient import ValidationResult

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class GoogleSheetConfig(BaseModel):
    credentials_path: Optional[str] = None
    spreadsheet_id: str


google_config = GoogleSheetConfig(
    credentials_path=os.getenv("GOOGLE_CREDENTIALS_PATH"),
    spreadsheet_id=os.getenv("GOOGLE_SHEET_ID"),
)


class RecordTargetFields(HumanResource, ValidationResult):
    """記錄的 schema"""

    validated_at: datetime


class GoogleSheetHandler:
    """Google Sheets 處理器，支援讀取、寫入、更新和刪除操作"""

    _service = None
    _credentials = None

    def __init__(self, config: GoogleSheetConfig = google_config):
        self.config = config
        self._ensure_service()

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
                config = GoogleSheetConfig(
                    credentials_path=os.getenv("GOOGLE_CREDENTIALS_PATH"),
                    spreadsheet_id=os.getenv("GOOGLE_SHEET_ID"),
                )

                if config.credentials_path:
                    cls._credentials = ServiceAccountCredentials.from_service_account_file(
                        config.credentials_path, scopes=SCOPES
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

    def append_sheet(self, sheet_name: str, values: List[List[str]]) -> Dict[str, Any]:
        """
        在 Google Sheets 末尾追加資料

        Args:
            sheet_name: 目標分頁，例如 'Sheet1'
            values: 要追加的資料（二維陣列）

        Returns:
            API 回應
        """
        try:
            body = {"values": values}

            result = (
                self.service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=self.config.spreadsheet_id,
                    range=sheet_name,
                    valueInputOption="RAW",
                    insertDataOption="INSERT_ROWS",
                    body=body,
                )
                .execute()
            )

            logger.info(f"成功追加 {len(values)} 行資料")
            return result

        except HttpError as error:
            logger.error(f"追加 Google Sheets 資料時發生錯誤: {error}")
            raise

    def append_record(self, record: dict, validation_result, sheet_name: str) -> None:
        """寫入一筆資料"""
        try:
            record = RecordTargetFields(
                id=record.get("id", ""),
                org=record.get("org", ""),
                address=record.get("address", ""),
                role_name=record.get("role_name", ""),
                assignment_notes=record.get("assignment_notes", ""),
                valid=validation_result.valid,
                reason=validation_result.reason,
                validated_at=datetime.now(),
            )

            row_data = [
                (
                    getattr(record, field).isoformat()
                    if isinstance(getattr(record, field), datetime)
                    else getattr(record, field)
                )
                for field in RecordTargetFields.__fields__.keys()
            ]

            self.append_sheet(sheet_name, [row_data])
            logger.info(f"已寫入資料: {record.id}")

        except Exception as e:
            logger.error(f"寫入資料時發生錯誤: {e}")
            raise


if __name__ == "__main__":
    try:
        google_sheet_config = GoogleSheetConfig(
            credentials_path=os.getenv("GOOGLE_CREDENTIALS_PATH"),
            spreadsheet_id=os.getenv("GOOGLE_SHEET_ID"),
        )
        sheet_handler = GoogleSheetHandler(google_sheet_config)

        new_data = [["測試", "資料", "範例"]]
        sheet_handler.append_sheet("test!A1:C1", new_data)

    except Exception as e:
        logger.error(f"發生錯誤: {e}")
