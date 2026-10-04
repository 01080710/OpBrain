"""讀取專案根目錄的 .env（不入庫）。只回傳需要的單一值，不印出內容。"""
import os

from dotenv import load_dotenv

from . import paths

load_dotenv(paths.PROJECT_ROOT / ".env")


def get(name: str, default=None):
    return os.getenv(name, default)
