"""Базовый класс для всех сущностей на Metal Archives"""

from typing import Optional

from pyquery import PyQuery

from metallum.models.metallum import Metallum


class MetallumEntity(Metallum):
    """Представляет сущность Metallum (артист, альбом...)"""

    def _dd_element_for_label(self, label: str) -> Optional[PyQuery]:
        """
        Данные на страницах сущностей хранятся в парах <dt> / <dd>

        Args:
            label: Метка для поиска

        Returns:
            PyQuery: Элемент <dd>, соответствующий метке
        """
        labels = list(self._page("dt").contents())

        try:
            index = labels.index(label)
        except ValueError:
            return None

        return self._page("dd").eq(index)

    def _dd_text_for_label(self, label: str) -> str:
        """
        Получить текст элемента <dd>, соответствующего метке

        Args:
            label: Метка для поиска

        Returns:
            str: Текст элемента <dd>
        """
        element = self._dd_element_for_label(label)
        return element.text() if element else ""
