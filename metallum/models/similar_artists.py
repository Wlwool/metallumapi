"""Вкладка похожих артистов на странице группы"""

import re

from pyquery import PyQuery

from metallum.models.metallum import Metallum

BAND_LINK_RE = re.compile(r"/bands/\S+/\d+$")


class SimilarArtists(Metallum, list):
    """Записи во вкладке похожих артистов"""

    def __init__(self, url, result_handler):
        super().__init__(url)

        for row in PyQuery(self._content)("tr"):
            link = self._band_link(row)
            if link is None:
                continue
            details = [link]
            details.extend(row.text_content().split("\n")[1:-1])
            self.append(result_handler(details))
        self.result_count = len(self)

    @staticmethod
    def _band_link(row) -> str | None:
        """Первый href на страницу группы в строке, иначе None."""
        for a in PyQuery(row)("a"):
            href = a.attrib.get("href") or ""
            if BAND_LINK_RE.search(href):
                return href
        return None

    def __repr__(self):
        def similar_artist_str(similar_artists_result):
            return f"{similar_artists_result.name} ({similar_artists_result.score})"

        if not self:
            return "<SimilarArtists: None>"
        names = list(map(similar_artist_str, self))
        s = " | ".join(names)
        return f"<SimilarArtists: {s}>"
