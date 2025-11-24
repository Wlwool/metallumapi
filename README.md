<p align="center"><img width="750" src="https://www.metal-archives.com/css/default/images/smallerlogo.jpg" alt="python-metallum"></p>

<p align="center">
</p>

---

# MetallumAPI - неофициальный API Metal Archives

Лёгкая Python-библиотека для работы с [Metal Archives](https://www.metal-archives.com/). Позволяет искать группы, альбомы и песни, собирать дискографии, парсить трек-листы и подтягивать дополнительную информацию (лейблы, жанры, похожие артисты и т.д.).

![UML diagram](https://www.plantuml.com/plantuml/png/bLDTQnin47pNhr1_W7tGnz87kwMKGbjAOyYZMT-jBoBwEAHLuFBntwDO1C4Hxt9lrjxCUZIZsIM2IDbPzMcAC3hGEU4lJnWT3WO8_q5_3oCcVGQRKAdUGahQ8O6rsMrT6D2cxTwUiZlCKy4zgHSE97t_7gp5dapm4l8_fcofeBG-3WLWRFgY_mQFFEqsmZHXh3nucrHME_9Ble4V2fdxl5xPRtYSB-eg2IqwYJ57qtDk_y5whXiJfbGyRLVjWoVqr0OJZ5XFqaeXemNuXoT3CmEyGOZztKLcl1XNjELtPGAhEiqjDyvOYFj89b7YWC6FrtChWwgjl779fKCibLdcM4wBjpQOr1zzTYUCRHWUC9PbRIx-qI8B8OMlpvlDnxLGSjWCku4K5nIpeGAkggXChj0hhzxQkbfnfQqMt5ehaEGaX0My4ol9rGsU9DHETfYfuug7oTP3dKCWZFedUen0EEZJhBjkcZzFsTckKplqG_dr2W00)

---

## Содержание

- [Почему это нужно](#почему-это-нужно)
- [Требования](#требования)
- [Установка](#установка)
  - [PyPI](#pypi)
  - [Зависимость напрямую из GitHub](#зависимость-напрямую-из-github)
  - [uv / локальная разработка](#uv--локальная-разработка)
  - [Git clone](#git-clone)
  - [Удаление](#удаление)
- [Использование](#использование)
  - [Быстрый старт](#быстрый-старт)
  - [Поиск групп](#поиск-групп)
  - [Поиск альбомов](#поиск-альбомов)
  - [Интеграция в Telegram-бота](#интеграция-в-telegram-бота)
- [Контрибьюции](#контрибьюции)
- [Лицензия](#лицензия)

---

## Почему это нужно

Metal Archives не предоставляет официального API, поэтому приходится парсить HTML и поддерживать антибот-защиту Cloudflare. В библиотеке уже решены типовые задачи:

- корректные запросы через `curl_cffi` и обход cloudflare, которые повторяют отпечаток реального браузера;
- кеширование ответов, чтобы не ддосить сайт и ускорять разработку;
- модели для групп, альбомов, песен, треков и т.д.;
- удобные функции (`band_search`, `album_search`, `song_search`, `album_for_id`, `lyrics_for_id`).
- Автоматическое кеширование запросов для снижения нагрузки на сервер

---

## Требования

- Python `>=3.13` (см. `pyproject.toml`);
- рабочий OpenSSL (для HTTP/2 и современного TLS);
- зависимости:
  - `curl-cffi` - обход Cloudflare;
  - `requests`, `pyquery`, `lxml`, `python-dateutil`, `fake-useragent`.

> Разработка и тестирование ведутся под Linux + Python 3.13. На других версиях может работать, но гарантий нет.

---

## Установка


### uv / локальная разработка

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -e .
```

После этого можно править исходники и сразу запускать локальные скрипты/тесты.

### Git clone

```bash
git clone https://github.com/Wlwool/metallumapi.git
cd metallumapi
uv venv .venv && source .venv/bin/activate
uv pip install -e .
```

---

## Использование

### Быстрый старт

```python
import metallum

bands = metallum.band_search("metallica")
band = bands[0].get()

full_length = band.albums.search(type=metallum.AlbumTypes.FULL_LENGTH)
album = full_length[2]

print(band.name, band.country, band.genres)
print(album.title, album.date, album.label)

for track in album.tracks:
    print(track.number, track.title, track.duration)
```

### Поиск групп

```python
import metallum

results = metallum.band_search(
    name="metallica",
    strict=True,
    genre="thrash",
    countries=["United States"],
    year_created_from=1980,
)

band = results[0].get()
print(band.name, band.label, band.similar_artists[:3])
```

### Поиск альбомов

```python
import metallum

albums = metallum.album_search(
    title="seventh",
    strict=False,
    band="iron maiden",
    band_strict=False,
    year_from=1985,
    year_to=1990,
    types=[metallum.AlbumTypes.FULL_LENGTH.value],
)

release = albums[0].get()
print(release.title, release.type, release.date)
```


---

## Контрибьюции

PR приветствуются: багфиксы, актуализация моделей, поддержка новых эндпоинтов. Перед PR убедитесь, что линтеры и тесты проходят (`pytest tests/`). Если нашли проблему смело заводите issue.

---

Этот проект является производным от проекта [python-metallum](https://github.com/lcharlick/python-metallum), распространяемого под MIT License.
Мои изменения: перевод на русский язык, добавлен curl_cffi, исправления совместимости, обновлённая документация, исправлена блокировка от cloudflare и т.д.

## Лицензия

MIT. Можно использовать в закрытых и коммерческих проектах, но необходимо сохранять уведомление об авторских правах и текст лицензии.
