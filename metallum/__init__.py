#!/usr/bin/env python
# encoding: utf-8
"""Python-интерфейс для metal-archives.com"""

from metallum.models.album_types import AlbumTypes
from metallum.operations import album_for_id, band_search, song_search

if __name__ == "__main__":
    import doctest

    # Тестовые объекты
    search_results = band_search("metallica")
    band = search_results[0].get()
    album = band.albums.search(type=AlbumTypes.FULL_LENGTH)[2]
    track = album.tracks[0]

    # Объекты для тестирования split-альбомов
    split_album = album_for_id("42682")
    split_album_track = split_album.tracks[2]

    # Объекты для тестирования многодисковых альбомов
    multi_disc_album = album_for_id("338756")

    # Объекты для тестирования поиска песен
    song = song_search(
        "Fear of the Dark", band="Iron Maiden", release="Fear of the Dark"
    )[0]

    doctest.testmod(globs=locals())
