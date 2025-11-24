"""Константы, используемые во всем пакете."""

import os
import tempfile


CACHE_FILE = os.path.join(tempfile.gettempdir(), "metallum_cache")

# Детали сайта
BASE_URL = "https://www.metal-archives.com"

# HTML-сущности
BR = "<br/>"
CR = "&#13;"

# Тайм-аут между запросами к страницам, в секундах
REQUEST_TIMEOUT = 1.0

# Смещение UTC
UTC_OFFSET = 3
