"""Результаты поиска на Metal Archives"""

import re
from collections.abc import Callable

from pyquery import PyQuery

from metallum.models import Album, AlbumWrapper, Band, _get_bands_list
from metallum.models.lyrics import Lyrics
from metallum.utils import extract_id, split_genres


class SearchResult[T](list):
    """Представляет результат поиска в расширенном поиске."""

    _resultType: Callable[[str], T]

    @property
    def url(self) -> str:
        raise NotImplementedError

    def __init__(self, details):
        super().__init__()
        for detail in details:
            if re.match("^<a href.*", detail):
                lyrics_link = re.search(r'id="lyricsLink_(\d+)"', detail)
                if lyrics_link is not None:
                    self.append(lyrics_link[1])
                else:
                    d = PyQuery(detail)
                    self.append(d("a").text())
            else:
                self.append(detail)

    def __repr__(self):
        s = " | ".join(self)
        return f"<SearchResult: {s}>"

    def get(self) -> T:
        """Return the result as its represented object."""
        return self._resultType(self.url)


class BandResult(SearchResult[Band]):
    """Представляет результат поиска группы"""

    def __init__(self, details):
        super().__init__(details)
        self._details = details
        self._resultType = Band

    @property
    def id(self) -> str:
        """
        ID группы

        Примеры:
            >>> search_results[0].id
            '125'
        """
        url = PyQuery(self._details[0])("a").attr("href")
        return extract_id(url)

    @property
    def url(self) -> str:
        """
        URL группы

        Примеры:
            >>> search_results[0].url
            'bands/_/125'
        """
        return f"bands/_/{self.id}"

    @property
    def name(self) -> str:
        """
        Название группы

        Примеры:
            >>> search_results[0].name
            'Metallica'
        """
        return self[0]

    @property
    def genres(self) -> list[str]:
        """
        Жанры группы

        Примеры:
            >>> search_results[0].genres
            ['Thrash Metal (early)', 'Hard Rock (mid)', 'Heavy/Thrash Metal (later)']
        """
        return split_genres(self[1])

    @property
    def country(self) -> str:
        """
        Страна группы

        Примеры:
            >>> search_results[0].country
            'United States'
        """
        return self[2]

    @property
    def other(self) -> list[str]:
        """
        Другая информация о группе

        Примеры:
            >>> search_results[0].other
            ['Active since: 1981']
        """
        return self[3:]


class AlbumResult(SearchResult[AlbumWrapper]):
    """Представляет результат поиска альбома"""

    def __init__(self, details):
        super().__init__(details)
        self._details = details
        self._resultType = AlbumWrapper

    @property
    def id(self) -> str:
        """
        ID альбома

        Примеры:
            >>> album.id
            '1'
        """
        url = PyQuery(self._details[1])("a").attr("href")
        return extract_id(url)

    @property
    def url(self) -> str:
        """
        URL альбома

        Примеры:
            >>> album.url
            'albums/_/_/1'
        """
        return f"albums/_/_/{self.id}"

    @property
    def title(self) -> str:
        """
        Название альбома

        Примеры:
            >>> album.title
            'Tuonela'
        """
        return self[1]

    @property
    def type(self) -> str:
        """
        Тип альбома

        Примеры:
            >>> album.type
            'Full-length'
        """
        return self[2]

    @property
    def bands(self) -> list["Band"]:
        """
        Список групп, выпустивших альбом

        Примеры:
            >>> album.bands
            [Amorphis]
        """
        page = PyQuery(self._details[0]).wrap("<div></div>")
        return _get_bands_list(page)

    @property
    def band_name(self) -> str:
        """
        Название группы, выпустившей альбом

        Примеры:
            >>> album.band_name
            'Amorphis'
        """
        return self[0]


class SongResult(SearchResult["SongResult"]):
    """Представляет результат поиска песни"""

    def __init__(self, details):
        super().__init__(details)
        self._details = details

    def get(self) -> "SongResult":
        """Return the result as a SongResult object"""
        return self

    @property
    def id(self) -> str:
        """
        ID песни

        Примеры:
            >>> song.id
            '3449'
        """
        match = re.search(r"(\d+)", self[5])
        if match is None:
            raise ValueError(f"Song has no numeric identifier: {self[5]!r}")
        return match.group(0)

    @property
    def title(self) -> str:
        """
        Название песни

        Примеры:
            >>> song.title
            'Fear of the Dark'
        """
        return self[3]

    @property
    def type(self) -> str:
        """
        Тип песни

        Примеры:
            >>> song.type
            'Single'
        """
        return self[2]

    @property
    def bands(self) -> list["Band"]:
        """
        Список групп, выпустивших песню

        Примеры:
            >>> song.bands
            [Iron Maiden]
        """
        page = PyQuery(self._details[0]).wrap("<div></div>")
        return _get_bands_list(page)

    @property
    def band_name(self) -> str:
        """
        Название группы, выпустившей песню

        Примеры:
            >>> song.band_name
            'Iron Maiden'
        """
        return self[0]

    @property
    def album(self) -> "Album":
        """
        Альбом, из которого взята песня

        Примеры:
            >>> song.album
            <Album: albums/_/_/1>
        """
        url = PyQuery(self._details[1]).attr("href")
        album_id = extract_id(url)
        return Album(f"albums/_/_/{album_id}")

    @property
    def album_name(self) -> str:
        """
        Название альбома, из которого взята песня

        Примеры:
            >>> song.album_name
            'Fear of the Dark'
        """
        return self[1]

    @property
    def genres(self) -> list[str]:
        """
        Жанры песни

        Примеры:
            >>> song.genres
            ['Heavy Metal', 'NWOBHM']
        """
        genres = []
        for genre in self[4].split(" | "):
            genres.extend(split_genres(genre.strip()))
        return genres

    @property
    def lyrics(self) -> "Lyrics":
        """
        Текст песни

        Примеры:
            >>> str(song.lyrics).split('\\n')[0]
            'I am a man who walks alone'
        """
        return Lyrics(self.id)
