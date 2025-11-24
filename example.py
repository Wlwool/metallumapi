"""Пример использования metallum API."""

from datetime import datetime

import metallum


def format_duration(seconds: int) -> str:
    """Преобразовать секунды в строку вида HH:MM:SS или MM:SS."""
    if seconds <= 0:
        return "—"
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{sec:02d}"
    return f"{minutes:d}:{sec:02d}"


def format_date(value: datetime | None) -> str:
    """Человечный вывод даты релиза."""
    if not value:
        return "дата не указана"
    return value.strftime("%d %b %Y")


def main():
    bands = metallum.band_search("metallica")
    if not bands:
        print("Ничего не найдено.")
        return

    band = bands[0].get()
    albums = band.albums
    full_length_albums = [
        album for album in albums if album.type.lower() == metallum.AlbumTypes.FULL_LENGTH.value.lower()
    ]
    if not full_length_albums:
        print(f"Для группы {band.name} не найдено полноформатных релизов.")
        return

    album = full_length_albums[2]
    tracks = album.tracks

    print(f"Группа: {band.name}")
    print(f"Страна: {band.country} • Локация: {band.location}")
    print(f"Статус: {band.status} • Основана: {band.formed_in}")
    print(f"Жанры: {', '.join(band.genres)}")
    print(f"Лейбл: {band.label}")
    print(f"Всего релизов: {len(albums)} • Full-length: {len(full_length_albums)}")

    score = (
        f"{album.score}% при {album.review_count} отзывах"
        if album.score
        else "нет пользовательских оценок"
    )

    sorted_albums = sorted(full_length_albums, key=lambda item: item.year)
    print("\nПолноформатные релизы:")
    for idx, release in enumerate(sorted_albums, start=1):
        print(f"{idx:2}. {release.year} • {release.title}")

    print()
    print(f"Альбом: {album.title} — {album.type}")
    print(
        f"Дата релиза: {format_date(album.date)} • Лейбл: {album.label} • Длительность: {format_duration(album.duration)}"
    )
    print(f"Оценка слушателей: {score}")
    print(f"Количество дисков: {album.disc_count}")

    print("\nТреки:")
    for track in tracks:
        print(f"{track.overall_number:2}. {track.title} — {format_duration(track.duration)}")


if __name__ == "__main__":
    main()
