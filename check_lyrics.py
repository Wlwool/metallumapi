import metallum


def check_metallica_lyrics():
    print("Проверка текста песни Metallica")
    bands = metallum.band_search("Metallica")
    band = bands[0].get()
    # Сортировка по году, чтобы найти первый альбом
    full_lengths = [a for a in band.albums if a.type.lower() == "full-length"]
    if not full_lengths:
        print("Полноформатные альбомы не найдены")
        return
    first_album = sorted(full_lengths, key=lambda x: x.year)[0]
    print(f"Альбом: {first_album.title} ({first_album.year})")
    # Hit the Lights
    track = first_album.tracks[0]
    print(f"Трек: {track.title}")
    lyrics = track.lyrics
    content = str(lyrics)
    if content:
        print("\nТекст (первые 200 символов):")
        print(content[:800] + "...")
    else:
        print("\nТекст не найден или пуст.")


if __name__ == "__main__":
    check_metallica_lyrics()
