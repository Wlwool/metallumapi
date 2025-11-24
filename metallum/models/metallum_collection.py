"""Базовый класс Metallum для коллекций (например, альбомов)"""

from metallum.models.metallum import Metallum


class MetallumCollection(Metallum, list):
    """Базовый класс Metallum для коллекций (например, альбомов)"""

    def search(self, **kwargs) -> "MetallumCollection":
        """
        Запрос к коллекции на основе одной или нескольких пар ключ-значение, где
        ключи являются атрибутами содержащихся объектов:

        Args:
            **kwargs: Пары ключ-значение для фильтрации коллекции

        Returns:
            MetallumCollection: Новая коллекция, содержащая только элементы,
            соответствующие критериям поиска

        Examples:
            >>> len(band.albums.search(title='master of puppets'))
            2

            >>> len(band.albums.search(title='master of puppets', type=AlbumTypes.FULL_LENGTH))
            1
        """
        def _normalize(obj):
            if isinstance(obj, str):
                return obj.lower()
            if hasattr(obj, "value"):
                return str(obj.value).lower()
            return str(obj).lower()

        collection = self[:]
        for key, value in kwargs.items():
            for item in collection[:]:
                current = getattr(item, key)
                if _normalize(value) != _normalize(current):
                    try:
                        collection.remove(item)
                    except ValueError:
                        continue
        return collection
