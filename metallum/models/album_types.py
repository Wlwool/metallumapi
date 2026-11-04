"""Перечисление всех возможных типов альбомов"""


from enum import Enum


class AlbumTypes(Enum):
    """Перечисление всех возможных типов альбомов"""

    FULL_LENGTH = "Full-length"
    EP = "EP"
    SINGLE = "Single"
    DEMO = "Demo"
    VIDEO = "Video/VHS"
    COMPILATION = "Compilation"
    DVD = "DVD"
    LIVE = "Live album"
    SPLIT = "Split"
