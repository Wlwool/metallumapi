import pytest

from metallum.models.results import AlbumResult, BandResult, SongResult


class FakeBand:
    def __init__(self, url):
        self.url = url


class FakeAlbum:
    def __init__(self, url):
        self.url = url


def test_band_result_parses_details_and_gets_band(monkeypatch):
    monkeypatch.setattr("metallum.models.results.Band", FakeBand)
    result = BandResult(
        [
            '<a href="https://www.metal-archives.com/bands/_/125">Metallica</a>',
            "Thrash Metal (early), Heavy Metal (later)",
            "United States",
            "Active",
        ]
    )

    assert result.id == "125"
    assert result.url == "bands/_/125"
    assert result.name == "Metallica"
    assert result.genres == ["Thrash Metal (early)", "Heavy Metal (later)"]
    assert result.country == "United States"
    assert result.other == ["Active"]
    assert isinstance(result.get(), FakeBand)
    assert result.get().url == "bands/_/125"


def test_album_result_parses_details_and_gets_album(monkeypatch):
    monkeypatch.setattr("metallum.models.results.AlbumWrapper", FakeAlbum)
    result = AlbumResult(
        [
            '<a href="https://www.metal-archives.com/bands/_/125">Metallica</a>',
            '<a href="https://www.metal-archives.com/albums/_/_/547">Master of Puppets</a>',
            "Full-length",
            "1986",
        ]
    )

    assert result.id == "547"
    assert result.url == "albums/_/_/547"
    assert result.band_name == "Metallica"
    assert result.title == "Master of Puppets"
    assert result.type == "Full-length"
    assert isinstance(result.get(), FakeAlbum)
    assert result.get().url == "albums/_/_/547"


def test_song_result_parses_details_and_returns_self():
    result = SongResult(
        [
            '<a href="https://www.metal-archives.com/bands/_/33">Iron Maiden</a>',
            '<a href="https://www.metal-archives.com/albums/_/_/501">Fear of the Dark</a>',
            "Full-length",
            "Fear of the Dark",
            "Heavy Metal | NWOBHM",
            '<a id="lyricsLink_5018" href="#">Show lyrics</a>',
        ]
    )

    assert result.id == "5018"
    assert result.band_name == "Iron Maiden"
    assert result.album_name == "Fear of the Dark"
    assert result.title == "Fear of the Dark"
    assert result.type == "Full-length"
    assert result.genres == ["Heavy Metal", "NWOBHM"]
    assert result.get() is result


def test_song_result_rejects_missing_numeric_id():
    result = SongResult(["band", "album", "type", "song", "genre", "missing"])

    with pytest.raises(ValueError):
        _ = result.id
