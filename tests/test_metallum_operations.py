from datetime import datetime

import pytest

from metallum.models.album_types import AlbumTypes
from metallum.operations import album_for_id, band_search, song_search


@pytest.fixture
def band():
    search_results = band_search("metallica")
    return search_results[0].get()


@pytest.fixture
def album(band):
    return band.albums.search(type=AlbumTypes.FULL_LENGTH.value)[2]


@pytest.fixture
def track(album):
    return album.tracks[0]


@pytest.fixture
def split_album():
    return album_for_id("42682")


@pytest.fixture
def split_album_track(split_album):
    return split_album.tracks[2]


@pytest.fixture
def multi_disc_album():
    return album_for_id("338756")


@pytest.fixture
def song():
    return song_search(
        "Fear of the Dark", band="Iron Maiden", release="Fear of the Dark"
    )[0]


@pytest.fixture
def metallica_band():
    # Поиск группы Metallica
    bands = band_search("metallica")
    return bands[0].get()


def test_band_search(band):
    assert band.name == "Metallica"


def test_album_search(album):
    assert album.title == "Master of Puppets"


def test_split_album(split_album):
    assert split_album.title == "Paysage d'Hiver / Lunar Aurora"


def test_multi_disc_album(multi_disc_album):
    assert multi_disc_album.title == "Blood Geometry"


def test_song_search(song):
    assert song.title == "Fear of the Dark"
    assert song.bands[0].name == "Iron Maiden"
    assert song.album.title == "Fear of the Dark"


def test_band_name(metallica_band):
    # Проверка названия группы
    assert metallica_band.name == "Metallica"


def test_band_albums(metallica_band):
    # Проверка существования альбомов
    assert len(metallica_band.albums) > 0


def test_band_full_length_albums(metallica_band):
    # Проверка существования полноформатных альбомов
    full_length_albums = metallica_band.albums.search(type=AlbumTypes.FULL_LENGTH.value)
    assert len(full_length_albums) > 0


def test_album_title_and_date(metallica_band):
    # Получение третьего полноформатного альбома (Master of Puppets)
    full_length_albums = metallica_band.albums.search(type=AlbumTypes.FULL_LENGTH.value)
    album = full_length_albums[2]

    # Проверка названия альбома
    assert album.title == "Master of Puppets"

    # Проверка даты альбома
    assert album.date == datetime(1986, 3, 3, 0, 0)


def test_album_tracks(metallica_band):
    # Получение третьего полноформатного альбома (Master of Puppets)
    full_length_albums = metallica_band.albums.search(type=AlbumTypes.FULL_LENGTH.value)
    album = full_length_albums[2]

    # Проверка существования треков
    assert len(album.tracks) > 0
