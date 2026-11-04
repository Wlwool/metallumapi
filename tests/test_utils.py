from datetime import datetime

import pytest

from metallum.consts import UTC_OFFSET
from metallum.utils import (
    extract_id,
    make_absolute,
    map_params,
    offset_time,
    parse_duration,
    split_genres,
)


def test_map_params_maps_names_and_omits_none():
    params = {"name": "Metallica", "year": 1981, "unused": None}

    assert map_params(params, {"name": "bandName"}) == {
        "bandName": "Metallica",
        "year": 1981,
    }


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Heavy Metal", ["Heavy Metal"]),
        (
            "Thrash Metal (early), Hard Rock/Heavy Metal (later)",
            ["Thrash Metal (early)", "Hard Rock/Heavy Metal (later)"],
        ),
        (
            "Heavy Metal/Hard Rock (early, later), Thrash Metal (mid)",
            ["Heavy Metal/Hard Rock (early, later)", "Thrash Metal (mid)"],
        ),
        (
            "Deathcore (early); Melodic Death/Groove Metal",
            ["Deathcore (early)", "Melodic Death/Groove Metal"],
        ),
    ],
)
def test_split_genres(value, expected):
    assert split_genres(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [("00:01", 1), ("03:33", 213), ("01:14:00", 4440)],
)
def test_parse_duration(value, expected):
    assert parse_duration(value) == expected


def test_extract_id():
    assert extract_id("https://www.metal-archives.com/bands/_/125") == "125"


def test_extract_id_rejects_url_without_trailing_id():
    with pytest.raises(ValueError):
        extract_id("https://www.metal-archives.com/bands/_/")


def test_make_absolute():
    assert make_absolute("bands/_/125") == (
        "https://www.metal-archives.com/bands/_/125"
    )


def test_offset_time():
    assert offset_time(datetime(2026, 1, 1, 12, 0)) == datetime(
        2026, 1, 1, 12 + UTC_OFFSET, 0
    )
