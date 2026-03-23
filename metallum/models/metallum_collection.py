"""Базовый класс Metallum для коллекций (например, альбомов)"""
import asyncio
from concurrent.futures import ThreadPoolExecutor

from metallum.consts import REQUEST_TIMEOUT
from metallum.models.metallum import Metallum
import time

class MetallumCollection(Metallum, list):
    """Базовый класс Metallum для коллекций (например, альбомов)"""

    def load_all(self, max_workers=100, items=None):
        """
        Параллельная загрузка деталей всех элементов коллекции или переданного списка
        """
        target_items = items if items is not None else self

        def _load_item(item):
            retries = 3
            while retries > 0:
                try:
                    if hasattr(item, "label"):
                        _ = item.label
                    break
                except Exception as e:
                    if "429" in str(e):
                        retries -= 1
                        time.sleep(REQUEST_TIMEOUT * (4 - retries) * 2)
                        continue
                    raise e
            return item

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            list(executor.map(_load_item, target_items))
        return self

    async def load_all_async(self, max_workers=100, items=None):
        """
        Асинхронная обёртка над load_all() через ThreadPoolExecutor.
        Args:
            max_workers: Максимальное количество одновременных запросов
            items: Список элементов для загрузки (по умолчанию все)
        """
        target_items = items if items is not None else self
        semaphore = asyncio.Semaphore(max_workers)

        async def _load_item(item):
            async with semaphore:
                retries = 3
                delay = REQUEST_TIMEOUT
                while retries > 0:
                    try:
                        await asyncio.to_thread(item._load_sync)
                        break
                    except Exception as e:
                        if "429" in str(e):
                            retries -= 1
                            await asyncio.sleep(delay * (4 - retries) * 2)
                            continue
                        raise e
                return item

        tasks = [_load_item(item) for item in target_items]
        await asyncio.gather(*tasks)
        return self


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
