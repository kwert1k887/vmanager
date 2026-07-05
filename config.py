"""Конфигурация — загрузка из .env или переменных окружения."""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Config:
    def __init__(self):
        self.base_url = os.getenv("VM_BASE_URL", "https://hosting.example.com")
        self.email = os.getenv("VM_EMAIL", "")
        self.password = os.getenv("VM_PASSWORD", "")
