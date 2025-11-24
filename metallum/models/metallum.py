"""Базовый класс для всех классов Metallum"""

import hashlib
import json
import time
from pathlib import Path
from typing import Optional

from curl_cffi import requests as curl_requests
from pyquery import PyQuery

from metallum.consts import CACHE_FILE, REQUEST_TIMEOUT
from metallum.utils import make_absolute, get_user_agent


class Metallum:
    """Базовый класс Metallum - представляет страницу Metallum"""

    _CACHE_TTL = 300

    def __init__(self, url):
        self._cache_dir = Path(CACHE_FILE)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._session = curl_requests.Session()
        self._session.headers = {
            "User-Agent": get_user_agent(),
            "Accept-Encoding": "gzip, deflate",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.metal-archives.com/",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
        }

        self._content = self._fetch_page_content(url)
        self._page = PyQuery(self._content)

    def _cache_path(self, url: str) -> Path:
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return self._cache_dir / f"{digest}.cache"

    def _load_from_cache(self, url: str) -> Optional[str]:
        cache_file = self._cache_path(url)
        if not cache_file.exists():
            return None
        try:
            with cache_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            cache_file.unlink(missing_ok=True)
            return None

        if time.time() - data.get("timestamp", 0) > self._CACHE_TTL:
            cache_file.unlink(missing_ok=True)
            return None

        return data.get("content")

    def _save_to_cache(self, url: str, content: str) -> None:
        cache_file = self._cache_path(url)
        payload = {"timestamp": time.time(), "content": content}
        with cache_file.open("w", encoding="utf-8") as file:
            json.dump(payload, file)

    def _fetch_page_content(self, url) -> str:
        """
        Получить содержимое страницы

        Args:
            url: URL-адрес страницы для получения

        Returns:
            str: Содержимое страницы
        """
        absolute_url = make_absolute(url)
        cached_content = self._load_from_cache(absolute_url)
        if cached_content:
            return cached_content

        response = self._session.get(absolute_url)
        response.raise_for_status()
        self._save_to_cache(absolute_url, response.text)
        time.sleep(REQUEST_TIMEOUT)
        return response.text
