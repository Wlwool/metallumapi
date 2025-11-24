"""Модуль операций для API Metallum."""

from urllib.parse import urlencode

from metallum.models import AlbumWrapper, Band
from metallum.models.lyrics import Lyrics
from metallum.models.results import AlbumResult, BandResult, SongResult
from metallum.models.search import Search
from metallum.utils import map_params


def band_for_id(band_id: str) -> "Band":
    """
    Получить группу по её ID.

    Args:
        band_id: ID группы.

    Returns:
        Band: Группа с указанным ID.
    """
    return Band(f"bands/_/{band_id}")


def band_search(
    name,
    strict=True,
    genre=None,
    countries=None,
    year_created_from=None,
    year_created_to=None,
    status=None,
    themes=None,
    location=None,
    label=None,
    additional_notes=None,
    page_start=0,
) -> "Search":
    """
    Выполнить расширенный поиск группы.

    Args:
        name: Название группы.
        strict: Должен ли поиск быть строгим.
        genre: Жанр группы.
        countries: Страны группы.
        year_created_from: Год основания группы (от).
        year_created_to: Год основания группы (до).
        status: Статус группы.
        themes: Тематика группы.
        location: Местоположение группы.
        label: Лейбл группы.
        additional_notes: Дополнительные заметки о группе.
        page_start: Страница, с которой начать поиск.

    Returns:
        Search: Результаты поиска.
    """
    # Создать словарь из аргументов метода
    params = locals()

    # Преобразовать булево значение в целое число
    params["strict"] = str(int(params["strict"]))

    # Сопоставить аргументы метода с их эквивалентами в строке запроса URL
    params = map_params(
        params,
        {
            "name": "bandName",
            "strict": "exactBandMatch",
            "countries": "country[]",
            "year_created_from": "yearCreationFrom",
            "year_created_to": "yearCreationTo",
            "status": "status[]",
            "label": "bandLabelName",
            "additional_notes": "bandNotes",
            "page_start": "iDisplayStart",
        },
    )

    # Сформировать URL поиска
    url = "search/ajax-advanced/searching/bands/?" + urlencode(params, True)

    return Search(url, BandResult)


def album_for_id(album_id: str) -> "AlbumWrapper":
    """
    Получить альбом по его ID.

    Args:
        album_id: ID альбома.

    Returns:
        AlbumWrapper: Альбом с указанным ID.
    """
    return AlbumWrapper(url=f"albums/_/_/{album_id}")


def album_search(
    title,
    strict=True,
    band=None,
    band_strict=True,
    year_from=None,
    year_to=None,
    month_from=None,
    month_to=None,
    countries=None,
    location=None,
    label=None,
    indie_label=False,
    genre=None,
    catalog_number=None,
    identifiers=None,
    recording_info=None,
    version_description=None,
    additional_notes=None,
    types=None,
    page_start=0,
    formats=None,
) -> "Search":
    """
    Выполнить расширенный поиск альбома

    Args:
        title: Название альбома.
        strict: Должен ли поиск быть строгим.
        band: Группа альбома.
        band_strict: Должен ли поиск группы быть строгим.
        year_from: Год выпуска альбома (от).
        year_to: Год выпуска альбома (до).
        month_from: Месяц выпуска альбома (от).
        month_to: Месяц выпуска альбома (до).
        countries: Страны альбома.
        location: Местоположение альбома.
        label: Лейбл альбома.
        indie_label: Является ли лейбл независимым.
        genre: Жанр альбома.
        catalog_number: Каталожный номер альбома.
        identifiers: Идентификаторы альбома.
        recording_info: Информация о записи альбома.
        version_description: Описание версии альбома.
        additional_notes: Дополнительные заметки об альбоме.
        types: Типы альбома.
        page_start: Страница, с которой начать поиск.
        formats: Форматы альбома.

    Returns:
        Search: Результаты поиска.
    """
    # Создать словарь из аргументов метода
    params = locals()

    # Преобразовать булево значение в целое число
    params["strict"] = str(int(params["strict"]))
    params["band_strict"] = str(int(params["band_strict"]))
    params["indie_label"] = str(int(params["indie_label"]))

    # Значения месяцев должны быть указаны, если указан год
    if year_from and not month_from:
        params["month_from"] = "1"
    if year_to and not month_to:
        params["month_to"] = "12"

    # Сопоставить аргументы метода с их эквивалентами в строке запроса URL
    params = map_params(
        params,
        {
            "title": "releaseTitle",
            "strict": "exactReleaseMatch",
            "band": "bandName",
            "band_strict": "exactBandMatch",
            "year_from": "releaseYearFrom",
            "year_to": "releaseYearTo",
            "month_from": "releaseMonthFrom",
            "month_to": "releaseMonthTo",
            "countries": "country[]",
            "label": "releaseLabelName",
            "indie_label": "indieLabel",
            "catalog_number": "releaseCatalogNumber",
            "identifiers": "releaseIdentifiers",
            "recording_info": "releaseRecordingInfo",
            "version_description": "releaseDescription",
            "additional_notes": "releaseNotes",
            "types": "releaseType[]",
            "formats": "releaseFormat[]",
            "page_start": "iDisplayStart",
        },
    )

    # Сформировать URL поиска
    url = "search/ajax-advanced/searching/albums/?" + urlencode(params, True)

    return Search(url, AlbumResult)


def song_search(
    title,
    strict=True,
    band=None,
    band_strict=True,
    release=None,
    release_strict=True,
    lyrics=None,
    genre=None,
    types=None,
    page_start=0,
) -> "Search":
    """
    Выполнить расширенный поиск песни

    Args:
        title: Название песни.
        strict: Должен ли поиск быть строгим.
        band: Группа песни.
        band_strict: Должен ли поиск группы быть строгим.
        release: Релиз песни.
        release_strict: Должен ли поиск релиза быть строгим.
        lyrics: Текст песни.
        genre: Жанр песни.
        types: Типы песни.
        page_start: Страница, с которой начать поиск.

    Returns:
        Search: Результаты поиска.
    """
    # Создать словарь из аргументов метода
    params = locals()

    # Преобразовать булево значение в целое число
    params["strict"] = str(int(params["strict"]))
    params["band_strict"] = str(int(params["band_strict"]))
    params["release_strict"] = str(int(params["release_strict"]))

    # Установить жанр как '*', если он не указан, чтобы убедиться,
    # что будет возвращено правильное количество параметров
    if params["genre"] is None or len(params["genre"].strip()) == 0:
        params["genre"] = "*"

    # Сопоставить аргументы метода с их эквивалентами в строке запроса URL
    params = map_params(
        params,
        {
            "title": "songTitle",
            "strict": "exactSongMatch",
            "band": "bandName",
            "band_strict": "exactBandMatch",
            "release": "releaseTitle",
            "release_strict": "exactReleaseMatch",
            "types": "releaseType[]",
            "page_start": "iDisplayStart",
        },
    )

    # Сформировать URL поиска
    url = "search/ajax-advanced/searching/songs/?" + urlencode(params, True)

    return Search(url, SongResult)


def lyrics_for_id(lyrics_id: int) -> "Lyrics":
    """
    Получить текст песни по его ID.

    Args:
        id: ID текста песни.

    Returns:
        Lyrics: Текст песни с указанным ID.
    """
    return Lyrics(lyrics_id)
