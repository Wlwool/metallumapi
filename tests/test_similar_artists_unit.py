from pathlib import Path

from metallum.models import SimilarArtistsResult
from metallum.models.similar_artists import SimilarArtists

FIXTURES = Path(__file__).parent / "fixtures"
SIMILAR_URL = "band/ajax-recommendations/id/3540539551/showMoreSimilar/1"


def make_similar_artists(monkeypatch, fixture_name: str) -> SimilarArtists:
    content = (FIXTURES / fixture_name).read_text(encoding="utf-8")
    monkeypatch.setattr(
        "metallum.models.metallum.Metallum._fetch_page_content",
        lambda self, url: content,
    )
    return SimilarArtists(SIMILAR_URL, SimilarArtistsResult)


def test_no_artists_partial_returns_empty_list(monkeypatch):
    similar = make_similar_artists(monkeypatch, "similar_no_artists.html")

    assert similar == []


def test_no_artists_partial_does_not_crash_on_id(monkeypatch):
    similar = make_similar_artists(monkeypatch, "similar_no_artists.html")

    for artist in similar:
        assert artist.id.isdigit()


def test_mixed_partial_skips_service_links(monkeypatch):
    similar = make_similar_artists(monkeypatch, "similar_mixed.html")

    assert [a.id for a in similar] == ["138", "70"]
    assert [a.name.strip() for a in similar] == ["Megadeth", "Testament"]
    assert [a.country.strip() for a in similar] == ["United States", "United States"]
    assert [a.score for a in similar] == [618, 512]
    assert similar[0].url == "bands/_/138"


def test_mixed_partial_results_are_band_like(monkeypatch):
    similar = make_similar_artists(monkeypatch, "similar_mixed.html")

    for artist in similar:
        assert "/bands/" in artist[0]
        assert artist.id.isdigit()
