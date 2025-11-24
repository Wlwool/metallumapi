"""Вспомогательные функции для пакета Metallum."""

import datetime
import re
from functools import lru_cache
from typing import List

from fake_useragent import UserAgent

from metallum.consts import BASE_URL, UTC_OFFSET


def map_params(params, m):
    """
    Сопоставить параметры с соответствующими ключами.

    Args:
        params: Параметры для сопоставления.
        m: Сопоставление.

    Returns:
        dict: Сопоставленные параметры.
    """
    res = {}
    for k, v in params.items():
        if v is not None:
            res[m.get(k, k)] = v
    return res


def split_genres(s: str) -> List[str]:
    """
    Разделить строку жанров на список жанров.

    Args:
        s: Строка с жанрами.

    Returns:
        list: Список жанров.

    Examples:
        Разделить по запятой:
        >>> split_genres('Thrash Metal (early), Hard Rock/Heavy/Thrash Metal (later)')
        ['Thrash Metal (early)', 'Hard Rock/Heavy/Thrash Metal (later)']

        Разделить по точке с запятой:
        >>> split_genres('Deathcore (early); Melodic Death/Groove Metal')
        ['Deathcore (early)', 'Melodic Death/Groove Metal']

        Без запятых:
        >>> split_genres('Heavy Metal')
        ['Heavy Metal']

        Запятые внутри скобок:
        >>> split_genres('Heavy Metal/Hard Rock (early, later), Thrash Metal (mid)')
        ['Heavy Metal/Hard Rock (early, later)', 'Thrash Metal (mid)']
    """
    return re.split(r"(?:,|;)\s*(?![^()]*\))", s)


def make_absolute(endpoint: str) -> str:
    """
    Преобразовать относительные URL-адреса в абсолютные

    Args:
        endpoint: Относительный URL-адрес.

    Returns:
        str: Абсолютный URL-адрес.
    """
    return f"{BASE_URL}/{endpoint}"


def offset_time(t: datetime.datetime) -> datetime.datetime:
    """
    Преобразовать серверное время в UTC

    Args:
        t: Серверное время.

    Returns:
        datetime.datetime: Время в UTC.
    """
    td = datetime.timedelta(hours=UTC_OFFSET)
    return t + td


def parse_duration(s: str) -> int:
    """
    Разобрать строку длительности в секунды.

    Аргументы:
        s: Строка с длительностью.

    Возвращает:
        int: Длительность в секундах.

    Примеры:
        >>> parse_duration('00:01')
        1
        >>> parse_duration('03:33')
        213
        >>> parse_duration('01:14:00')
        4440
    """
    parts = s.split(":")
    seconds = int(parts[-1])
    if len(parts) > 1:
        seconds += int(parts[-2]) * 60
    if len(parts) == 3:
        seconds += int(parts[0]) * 3600
    return seconds


@lru_cache
def get_user_agent():
    """Получить случайного юзер агента."""
    return UserAgent().getSafari["useragent"]
