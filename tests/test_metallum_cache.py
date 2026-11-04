import json

import pytest

from metallum.models.metallum import Metallum
from metallum.utils import make_absolute


class FakeResponse:
    def __init__(self, text="", error=None):
        self.text = text
        self.error = error

    def raise_for_status(self):
        if self.error:
            raise self.error


class FakeSession:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get(self, url):
        self.calls.append(url)
        return self.response


def configure_metallum(monkeypatch, tmp_path, response):
    session = FakeSession(response)
    monkeypatch.setattr("metallum.models.metallum.CACHE_FILE", tmp_path)
    monkeypatch.setattr("metallum.models.metallum.time.sleep", lambda _: None)
    monkeypatch.setattr(Metallum, "_session", session)
    return session


def test_fresh_cache_avoids_repeated_http_request(monkeypatch, tmp_path):
    session = configure_metallum(monkeypatch, tmp_path, FakeResponse("cached"))

    first = Metallum("bands/_/125")
    second = Metallum("bands/_/125")

    assert first._content == "cached"
    assert second._content == "cached"
    assert session.calls == ["https://www.metal-archives.com/bands/_/125"]


def test_expired_cache_is_refetched(monkeypatch, tmp_path):
    session = configure_metallum(monkeypatch, tmp_path, FakeResponse("fresh"))
    instance = Metallum.__new__(Metallum)
    instance._cache_dir = tmp_path
    cache_file = instance._cache_path(make_absolute("bands/_/125"))
    cache_file.write_text(
        json.dumps({"timestamp": 0, "content": "stale"}), encoding="utf-8"
    )

    result = Metallum("bands/_/125")

    assert result._content == "fresh"
    assert len(session.calls) == 1


def test_corrupt_cache_is_refetched(monkeypatch, tmp_path):
    session = configure_metallum(monkeypatch, tmp_path, FakeResponse("fresh"))
    instance = Metallum.__new__(Metallum)
    instance._cache_dir = tmp_path
    cache_file = instance._cache_path(make_absolute("bands/_/125"))
    cache_file.write_text("not json", encoding="utf-8")

    result = Metallum("bands/_/125")

    assert result._content == "fresh"
    assert len(session.calls) == 1


def test_http_error_is_not_cached(monkeypatch, tmp_path):
    configure_metallum(
        monkeypatch, tmp_path, FakeResponse(error=RuntimeError("HTTP 503"))
    )

    with pytest.raises(RuntimeError, match="HTTP 503"):
        Metallum("bands/_/125")

    assert list(tmp_path.iterdir()) == []
