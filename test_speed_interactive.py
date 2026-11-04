import asyncio
import time
import metallum


def test_band_speed():
    band_name = input("Введите название группы для поиска: ").strip()
    if not band_name:
        print("Название не может быть пустым.")
        return

    print(f"Поиск группы '{band_name}'...")
    bands = metallum.band_search(band_name)
    if not bands:
        print("Группа не найдена.")
        return
    band = bands[0].get()
    albums = band.albums
    total_albums = len(albums)
    print(f"\nНайдена группа: {band.name}")
    print(f"Всего релизов: {total_albums}")
    try:
        limit_input = input(
            f"Сколько альбомов загрузить для теста? (по умолч. 50, макс {total_albums}): ").strip()
        count = int(limit_input) if limit_input else 50
    except ValueError:
        count = 50

    count = min(count, total_albums)
    
    # Настройки batch processing
    try:
        batch_input = input("Размер пачки (batch_size, по умолч. 100): ").strip()
        batch_size = int(batch_input) if batch_input else 100
    except ValueError:
        batch_size = 100
    
    try:
        delay_input = input("Задержка между пачками (batch_delay, сек, по умолч. 0.5): ").strip()
        batch_delay = float(delay_input) if delay_input else 0.5
    except ValueError:
        batch_delay = 0.5
    
    print(f"\nЗагрузка деталей для {count} альбомов через load_all (100 workers, batch={batch_size}, delay={batch_delay}s)...")
    start_time = time.time()
    albums.load_all(max_workers=100, items=albums[:count], batch_size=batch_size, batch_delay=batch_delay)
    end_time = time.time()

    total_time = end_time - start_time
    avg_time = total_time / count if count > 0 else 0
    print(f"Результаты для {band.name}:")
    print(f"Затрачено времени: {total_time:.2f} сек.")
    print(f"Среднее время на один альбом: {avg_time:.2f} сек.")
    if total_albums > count:
        projected = (avg_time * total_albums) / 60
        print(f"Прогноз для всех {total_albums} альбомов: {projected:.2f} мин.")
    if count > 0:
        print("\nПоследние 3 загруженных альбома:")
        for album in albums[max(0, count - 3):count]:
            print(f"- {album.year} • {album.title} (Лейбл: {album.label})")

async def test_band_speed_async():
    band_name = input("Введите название группы для поиска: ").strip()
    if not band_name:
        print("Название не может быть пустым.")
        return

    print(f"Поиск группы '{band_name}'...")
    bands = metallum.band_search(band_name)
    if not bands:
        print("Группа не найдена.")
        return
    band = bands[0].get()
    albums = band.albums
    total_albums = len(albums)
    print(f"\nНайдена группа: {band.name}")
    print(f"Всего релизов: {total_albums}")
    try:
        limit_input = input(
            f"Сколько альбомов загрузить для теста? (по умолч. 50, макс {total_albums}): ").strip()
        count = int(limit_input) if limit_input else 50
    except ValueError:
        count = 50

    count = min(count, total_albums)
    
    # Настройки batch processing
    try:
        batch_input = input("Размер пачки (batch_size, по умолч. 100): ").strip()
        batch_size = int(batch_input) if batch_input else 100
    except ValueError:
        batch_size = 100
    
    try:
        delay_input = input("Задержка между пачками (batch_delay, сек, по умолч. 0.5): ").strip()
        batch_delay = float(delay_input) if delay_input else 0.5
    except ValueError:
        batch_delay = 0.5
    
    print(f"\nЗагрузка деталей для {count} альбомов через load_all_async (100 workers, batch={batch_size}, delay={batch_delay}s)...")
    start_time = time.time()
    await albums.load_all_async(max_workers=100, items=albums[:count], batch_size=batch_size, batch_delay=batch_delay)
    end_time = time.time()

    total_time = end_time - start_time
    avg_time = total_time / count if count > 0 else 0
    print(" -" * 40)
    print(f"Результаты для {band.name}:")
    print(f"Затрачено времени: {total_time:.2f} сек.")
    print(f"Среднее время на один альбом: {avg_time:.2f} сек.")
    if total_albums > count:
        projected = (avg_time * total_albums) / 60
        print(f"Прогноз для всех {total_albums} альбомов: {projected:.2f} мин.")
    if count > 0:
        print("\nПоследние 3 загруженных альбома:")
        for album in albums[max(0, count - 3):count]:
            print(f"- {album.year} • {album.title} (Лейбл: {album.label})")
    print(" -" * 40)

if __name__ == "__main__":
    try:
        mode = input("Режим (1=потоки, 2=async): ").strip()
        if mode == "2":
            asyncio.run(test_band_speed_async())
        else:
            test_band_speed()
    except KeyboardInterrupt:
        print("\nТест прерван")
