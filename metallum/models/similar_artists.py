"""Вкладка похожих артистов на странице группы"""

from pyquery import PyQuery

from metallum.models.metallum import Metallum


class SimilarArtists(Metallum, list):
    """Записи во вкладке похожих артистов"""

    def __init__(self, url, result_handler):
        super().__init__(url)
        data = self._content

        links_list = PyQuery(data)("a")
        values_list = PyQuery(data)("tr")

        # assert(len(links_list) == len(values_list) - 1)
        for i in range(0, len(links_list) - 1):
            details = [links_list[i].attrib.get("href")]
            details.extend(values_list[i + 1].text_content().split("\n")[1:-1])
            self.append(result_handler(details))
            self.result_count = i

    def __repr__(self):
        def similar_artist_str(similar_artists_result):
            return f"{similar_artists_result.name} ({similar_artists_result.score})"

        if not self:
            return "<SimilarArtists: None>"
        names = list(map(similar_artist_str, self))
        s = " | ".join(names)
        return f"<SimilarArtists: {s}>"
