from urllib.parse import parse_qs, urlsplit

from metallum.operations import album_search, band_search, song_search


class FakeSearch:
    def __init__(self, url, result_handler):
        self.url = url
        self.result_handler = result_handler


def search_params(monkeypatch, search, *args, **kwargs):
    monkeypatch.setattr("metallum.operations.Search", FakeSearch)
    result = search(*args, **kwargs)
    return parse_qs(urlsplit(result.url).query, keep_blank_values=True)


def test_band_search_builds_query(monkeypatch):
    params = search_params(
        monkeypatch,
        band_search,
        "Metallica",
        strict=False,
        countries=["United States", "Sweden"],
        year_created_from=1981,
        year_created_to=1990,
        page_start=20,
    )

    assert params["bandName"] == ["Metallica"]
    assert params["exactBandMatch"] == ["0"]
    assert params["country[]"] == ["United States", "Sweden"]
    assert params["yearCreationFrom"] == ["1981"]
    assert params["yearCreationTo"] == ["1990"]
    assert params["iDisplayStart"] == ["20"]
    assert "genre" not in params


def test_album_search_builds_query_and_default_months(monkeypatch):
    params = search_params(
        monkeypatch,
        album_search,
        "Master of Puppets",
        strict=False,
        band="Metallica",
        band_strict=False,
        year_from=1986,
        year_to=1987,
        indie_label=True,
    )

    assert params["releaseTitle"] == ["Master of Puppets"]
    assert params["exactReleaseMatch"] == ["0"]
    assert params["bandName"] == ["Metallica"]
    assert params["exactBandMatch"] == ["0"]
    assert params["releaseYearFrom"] == ["1986"]
    assert params["releaseYearTo"] == ["1987"]
    assert params["releaseMonthFrom"] == ["1"]
    assert params["releaseMonthTo"] == ["12"]
    assert params["indieLabel"] == ["1"]


def test_album_search_preserves_explicit_months(monkeypatch):
    params = search_params(
        monkeypatch,
        album_search,
        "Master of Puppets",
        year_from=1986,
        month_from=3,
        year_to=1986,
        month_to=4,
    )

    assert params["releaseMonthFrom"] == ["3"]
    assert params["releaseMonthTo"] == ["4"]


def test_song_search_builds_query_with_default_genre(monkeypatch):
    params = search_params(
        monkeypatch,
        song_search,
        "Fear of the Dark",
        strict=False,
        band="Iron Maiden",
        band_strict=False,
        release="Fear of the Dark",
        release_strict=False,
    )

    assert params["songTitle"] == ["Fear of the Dark"]
    assert params["exactSongMatch"] == ["0"]
    assert params["bandName"] == ["Iron Maiden"]
    assert params["exactBandMatch"] == ["0"]
    assert params["releaseTitle"] == ["Fear of the Dark"]
    assert params["exactReleaseMatch"] == ["0"]
    assert params["genre"] == ["*"]
