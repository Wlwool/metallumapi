"""Модели Metal Archives"""

import datetime
import re
from typing import List, Optional

from dateutil import parser as date_parser
from pyquery import PyQuery

from metallum.models.album_types import AlbumTypes
from metallum.models.lyrics import Lyrics
from metallum.models.metallum import Metallum
from metallum.models.metallum_collection import MetallumCollection
from metallum.models.metallum_entity import MetallumEntity
from metallum.models.similar_artists import SimilarArtists
from metallum.utils import offset_time, parse_duration, split_genres


def _get_bands_list(page) -> List["Band"]:
    """
    Получить список групп из страницы

    Args:
        page: PyQuery object

    Returns:
        List[Band]
    """
    bands = []
    for a in page.find("a"):
        url = PyQuery(a).attr("href")
        band_id = re.search(r"\d+$", url).group(0)
        bands.append(Band(f"bands/_/{band_id}"))
    return bands


class TrackCollection(MetallumCollection):
    """Представляет коллекцию треков на Metal Archives"""

    def __init__(self, url, album):
        super().__init__(url)

        disc = 1
        overall_number = 1
        rows = (
            self._page("table.table_lyrics")
            .find("tr.odd, tr.even")
            .not_(".displayNone")
        )
        for index, track in enumerate(rows):
            track = Track(rows.eq(index), album, disc, overall_number)
            if index != 0 and track.number == 1:
                disc += 1
                track._disc_number = disc
            overall_number += 1
            self.append(track)


class Band(MetallumEntity):
    """Представляет группу на Metal Archives"""

    def __repr__(self):
        return f"<Band: {self.name}>"

    @property
    def id(self) -> str:
        """
        >>> band.id
        '125'
        """
        url = self._page(".band_name a").attr("href")
        return re.search(r"\d+$", url).group(0)

    @property
    def url(self) -> str:
        """
        >>> band.url
        'bands/_/125'
        """
        return f"bands/_/{self.id}"

    @property
    def added(self) -> Optional[datetime.datetime]:
        """
        >>> type(band.added)
        <class 'datetime.datetime'>
        """
        s = self._page("#auditTrail").find("tr").eq(1).find("td").eq(0).text()[10:]
        try:
            return offset_time(datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S"))
        except ValueError:
            return None

    @property
    def modified(self) -> Optional[datetime.datetime]:
        """
        >>> type(band.modified)
        <class 'datetime.datetime'>
        """
        s = self._page("#auditTrail").find("tr").eq(1).find("td").eq(1).text()[18:]
        try:
            return offset_time(datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S"))
        except ValueError:
            return None

    @property
    def name(self) -> str:
        """
        >>> band.name
        'Metallica'
        """
        return self._page("h1.band_name").text().strip()

    @property
    def country(self) -> str:
        """
        >>> band.country
        'United States'
        """
        return self._dd_text_for_label("Country of origin:")

    @property
    def location(self) -> str:
        """
        >>> band.location
        'Los Angeles/San Francisco, California'
        """
        return self._dd_text_for_label("Location:")

    @property
    def status(self) -> str:
        """
        >>> band.status
        'Active'
        """
        return self._dd_text_for_label("Status:")

    @property
    def formed_in(self) -> str:
        """
        >>> band.formed_in
        '1981'
        """
        return self._dd_text_for_label("Formed in:")

    @property
    def genres(self) -> List[str]:
        """
        >>> band.genres
        ['Thrash Metal (early)', 'Hard Rock (mid)', 'Heavy/Thrash Metal (later)']
        """
        return split_genres(self._dd_text_for_label("Genre:"))

    @property
    def themes(self) -> List[str]:
        """
        >>> band.themes
        ['Introspection', 'Anger', 'Corruption', 'Deceit', 'Death', 'Life',
        'Metal', 'Literature', 'Films']
        """
        return self._dd_text_for_label("Themes:").split(", ")

    @property
    def label(self) -> str:
        """
        >>> band.label
        'Blackened Recordings'
        """
        return self._dd_text_for_label("Current label:")

    @property
    def logo(self) -> Optional[str]:
        """
        >>> band.logo
        'https://www.metal-archives.com/images/1/2/5/125_logo.png'
        """
        url = self._page("#logo").attr("href")
        if not url:
            return None
        return url.split("?")[0]

    @property
    def photo(self) -> Optional[str]:
        """
        >>> band.photo
        'https://www.metal-archives.com/images/1/2/5/125_photo.jpg'
        """
        url = self._page("#photo").attr("href")
        if not url:
            return None
        return url.split("?")[0]

    @property
    def albums(self) -> List["AlbumCollection"]:
        """
        >>> len(band.albums) > 0
        True

        >>> type(band.albums[0])
        <class '__main__.AlbumWrapper'>
        """
        url = f"band/discography/id/{self.id}/tab/all"
        return AlbumCollection(url)

    @property
    def similar_artists(self) -> "SimilarArtists":
        """
        Получить список похожих групп к текущей группе.

        Examples:
            >>> band.similar_artists
            <SimilarArtists: Megadeth (488) | Testament (420) | Exodus (212) |
            Evile (206) | Anthrax (182) | Death Angel (148) | Diamond Head
            (119) | Xentrix (115) | Annihilator (111) | Newsted (108) | Metal
            Church (105) | Heathen (105) | Flotsam and Jetsam (104) | Slayer
            ...
        """

        url = "band/ajax-recommendations/id/" + self.id + "/showMoreSimilar/1"
        return SimilarArtists(url, SimilarArtistsResult)


class Track:
    """Представляет трек на Metal Archives"""

    def __init__(self, elem, album, disc_number, overall_number):
        self._elem = elem
        self.album = album
        self._disc_number = disc_number
        self._overall_number = overall_number

    def __repr__(self):
        return f"<Track: {self.title} ({self.duration})>"

    @property
    def id(self) -> str:
        """
        >>> track.id
        '5018A'
        """
        return self._elem("td").eq(0)("a").attr("name")

    @property
    def number(self) -> int:
        """
        >>> track.number
        1

        >>> multi_disc_album.tracks[0].number
        1

        >>> multi_disc_album.tracks[-1].number
        4
        """
        return int(self._elem("td").eq(0).text()[:-1])

    @property
    def overall_number(self) -> int:
        """
        >>> track.overall_number
        1

        >>> multi_disc_album.tracks[0].overall_number
        1

        >>> multi_disc_album.tracks[-1].overall_number
        8
        """
        return self._overall_number

    @property
    def disc_number(self) -> int:
        """
        >>> track.disc_number
        1

        >>> multi_disc_album.tracks[0].disc_number
        1

        >>> multi_disc_album.tracks[-1].disc_number
        2
        """
        return self._disc_number

    @property
    def full_title(self) -> str:
        """
        >>> track.full_title
        'Battery'

        >>> split_album_track.full_title
        'Lunar Aurora - A haudiga Fluag'
        """
        return self._elem("td").eq(1).text().replace("\n", "").replace("\t", "")

    @property
    def title(self) -> str:
        """
        >>> track.title
        'Battery'

        >>> split_album_track.title
        'A haudiga Fluag'
        """
        title = self.full_title
        # Remove band name from split album track titles
        if self.album.type == AlbumTypes.SPLIT:
            title = title[len(self.band.name) + 3 :]
        return title

    @property
    def duration(self) -> int:
        """
        >>> track.duration
        313
        """
        s = self._elem("td").eq(2).text()
        if s:
            seconds = parse_duration(s)
        else:
            seconds = 0
        return seconds

    @property
    def band(self) -> Band:
        """
        >>> track.band
        <Band: Metallica>

        >>> split_album_track.band
        <Band: Lunar Aurora>
        """
        if self.album.type == AlbumTypes.SPLIT:
            for band in self.album.bands:
                if self.full_title.startswith(band.name):
                    break
        else:
            band = self.album.bands[0]
        return band

    @property
    def lyrics(self) -> "Lyrics":
        """
        >>> str(track.lyrics).split('\\n')[0]
        'Lashing out the action, returning the reaction'
        """
        return Lyrics(self.id)


class Album(MetallumEntity):
    """Представляет альбом на Metal Archives"""

    def __repr__(self):
        return f"<Album: {self.title}>"

    @property
    def id(self) -> str:
        """
        >>> album.id
        '547'
        """
        url = self._page(".album_name a").attr("href")
        return re.search(r"\d+$", url).group(0)

    @property
    def url(self) -> str:
        """
        >>> album.url
        'albums/_/_/547'
        """
        return f"albums/_/_/{self.id}"

    @property
    def bands(self) -> List[Band]:
        """Возвращает список объектов группы. Список будет содержать
        несколько групп только в том случае, если альбом имеет тип 'Split'.

        >>> album.bands
        [<Band: Metallica>]

        >>> split_album.bands
        [<Band: Lunar Aurora>, <Band: Paysage d'Hiver>]
        """
        page = self._page(".band_name")
        return _get_bands_list(page)

    @property
    def added(self) -> Optional[datetime.datetime]:
        """
        >>> type(album.added)
        <class 'NoneType'>
        """
        s = self._page("#auditTrail").find("tr").eq(1).find("td").eq(0).text()[10:]
        try:
            return offset_time(datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S"))
        except ValueError:
            return None

    @property
    def modified(self) -> Optional[datetime.datetime]:
        """
        >>> type(album.modified)
        <class 'datetime.datetime'>
        """
        s = self._page("#auditTrail").find("tr").eq(1).find("td").eq(1).text()[18:]
        try:
            return offset_time(datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S"))
        except ValueError:
            return None

    @property
    def title(self) -> str:
        """
        >>> album.title
        'Master of Puppets'
        """
        return self._page("h1.album_name a").text()

    @property
    def type(self) -> str:
        """
        >>> album.type
        'Full-length'
        """
        element = self._dd_element_for_label("Type:")
        return element.text() if element else ""

    @property
    def duration(self) -> int:
        """
        >>> album.duration
        3290
        """
        s = self._page("table.table_lyrics td strong").text()
        if s:
            return parse_duration(s)
        return 0

    @property
    def date(self) -> Optional[datetime.datetime]:
        """
        >>> album.date
        datetime.datetime(1986, 3, 3, 0, 0)
        """
        s = self._dd_text_for_label("Release date:")

        # Date has no day portion
        if len(s) > 4 and "," not in s:
            date = datetime.datetime.strptime(s, "%B %Y")
        else:
            date = date_parser.parse(s)
        return date

    @property
    def year(self) -> int:
        """
        >>> album.year
        1986
        """
        return int(self.date.year)

    @property
    def label(self) -> str:
        """
        >>> album.label
        'Elektra Records'

        >>> multi_disc_album.label
        'Osmose Productions'
        """
        element = self._dd_element_for_label("Label:")
        return element("a").text() if element else ""

    def _review_element(self) -> Optional[PyQuery]:
        return self._dd_element_for_label("Reviews:")

    @property
    def score(self) -> Optional[int]:
        """
        >>> album.score
        79

        >>> split_album.score
        94

        >>> multi_disc_album.score
        97
        """
        element = self._review_element()
        if not element:
            return None

        score = re.search(r"(\d{1,3})%", element.text())
        if not score:
            return None

        return int(score.group(1))

    @property
    def review_count(self) -> Optional[int]:
        """
        >>> album.review_count
        39

        >>> split_album.review_count
        1

        >>> multi_disc_album.review_count
        4
        """
        element = self._review_element()
        if not element:
            return None

        count = re.search(r"(\d+)", element.text())
        if not count:
            return None

        return int(count.group(1))

    @property
    def cover(self) -> Optional[str]:
        """
        >>> album.cover
        'https://www.metal-archives.com/images/5/4/7/547.jpg'
        """
        url = self._page("#cover").attr("href")
        if not url:
            return None
        return url.split("?")[0]


class AlbumCollection(MetallumCollection):
    """Представляет коллекцию альбомов Metal Archives"""

    def __init__(self, url):
        super().__init__(url)

        rows = self._page("tr:gt(0)")
        for index in range(len(rows)):
            self.append(AlbumWrapper(elem=rows.eq(index)))


class AlbumWrapper(Metallum):
    """Обёртка class для Album / LazyAlbum

    Экземпляры альбомов создаются автоматически при обращении к атрибуту, который
    не предоставляется LazyAlbum:

    >>> a = band.albums[1]
    >>> a.label
    'Megaforce Records'

    В результате вышеописанного создается экземпляр альбома
    (требуется запрос дополнительной страницы!):

    >>> type(a._album)
    <class '__main__.Album'>
    """

    def __init__(self, url=None, elem=None):
        if url:
            super().__init__(url)
            self._album = Album(url)
        elif elem:
            self._album = LazyAlbum(elem)

    def __repr__(self):
        return f"<Album: {self.title} ({self.type})>"

    def __getattr__(self, name):
        if not hasattr(self._album, name) and hasattr(Album, name):
            self._album = Album(self._album.url)
        return getattr(self._album, name)

    @property
    def tracks(self):
        """
        >>> len(album.tracks)
        8
        """
        return TrackCollection(self._album.url, self)

    @property
    def disc_count(self):
        """
        >>> album.disc_count
        1

        >>> multi_disc_album.disc_count
        2
        """
        discs = 0
        for track in self.tracks:
            if track.disc_number > discs:
                discs = track.disc_number
        return discs


class LazyAlbum:
    """LazyAlbum - это заполнитель для экземпляров альбомов, которые еще не созданы"""

    def __init__(self, elem):
        self._elem = elem

    @property
    def id(self) -> str:
        """
        >>> album.id
        '547'
        """
        url = self._elem("td").eq(0)("a").attr("href")
        return re.search(r"\d+$", url).group(0)

    @property
    def url(self) -> str:
        """
        >>> album.url
        'albums/_/_/547'
        """
        return f"albums/_/_/{self.id}"

    @property
    def title(self) -> str:
        """
        >>> album.title
        'Master of Puppets'
        """
        return self._elem("td").eq(0)("a").text()

    @property
    def type(self) -> str:
        """
        >>> album.type
        'Full-length'
        """
        return self._elem("td").eq(1).text()

    @property
    def year(self) -> int:
        """
        >>> album.year
        1986
        """
        return int(self._elem("td").eq(2).text())


class SimilarArtistsResult(list):
    """Представляет собой запись на вкладке похожие исполнители"""

    _resultType = Band

    def __init__(self, details):
        super().__init__()
        self._details = details
        for d in details:
            self.append(d)

    def __repr__(self):
        s = " | ".join(self[1:])
        return f"<SimilarArtist: {s}>"

    @property
    def id(self) -> str:
        """
        >>> search_results[0].id
        '125'
        """
        # url = PyQuery(self._details[0])('a').attr('href')
        return re.search(r"\d+$", self[0]).group(0)

    @property
    def url(self) -> str:
        """
        >>> search_results[0].url
        'bands/_/125'
        """
        return f"bands/_/{self.id}"

    @property
    def name(self) -> str:
        """
        >>> search_results[0].name
        'Metallica'
        """
        return self[1]

    @property
    def country(self) -> str:
        """
        >>> search_results[0].country
        'United States'
        """
        return self[2]

    @property
    def genres(self) -> List[str]:
        """
        >>> search_results[0].genres
        ['Thrash Metal (early)', 'Hard Rock (mid)', 'Heavy/Thrash Metal (later)']
        """
        return split_genres(self[3])

    @property
    def score(self) -> int:
        """
        >>> search_results[0].score
        100
        """
        return int(self[4])

    def get(self) -> "Metallum":
        """
        Получает объект группы

        Returns:
            Band
        """
        return self._resultType(self.url)
