#!/usr/bin/env python3
"""Скачивает шрифты Inter (400) и PT Sans (700) с Google Fonts в папку fonts/ рядом со скриптом.
После этого build.py подключает их с вашего сервера, и запросов к Google на сайте больше нет.
Запуск (нужен интернет и доступ к fonts.googleapis.com):  python3 get_fonts.py"""
import json, pathlib, re, sys, urllib.request

CSS_URL = "https://fonts.googleapis.com/css2?family=Inter:wght@400&family=PT+Sans:wght@700&display=swap"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"  # чтобы получить woff2
SUBSETS = ("cyrillic", "latin")      # нужные наборы символов


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def parse_css(css):
    """Разбирает CSS Google Fonts на список шрифтов: семейство, начертание, диапазон символов, адрес файла."""
    items = []
    for subset, body in re.findall(r"/\*\s*([\w-]+)\s*\*/\s*@font-face\s*\{(.*?)\}", css, re.S):
        if subset not in SUBSETS:
            continue
        family = re.search(r"font-family:\s*['\"]([^'\"]+)['\"]", body).group(1)
        weight = re.search(r"font-weight:\s*([\d ]+);", body).group(1).strip()
        url = re.search(r"url\((https://[^)]+)\)", body).group(1)
        rng = re.search(r"unicode-range:\s*([^;]+);", body).group(1).strip()
        name = f"{family.lower().replace(' ', '-')}-{weight.split()[0]}-{subset}.woff2"
        items.append(dict(family=family, weight=weight, subset=subset, file=name, range=rng, url=url))
    return items


def main():
    out = pathlib.Path(__file__).parent / "fonts"
    out.mkdir(exist_ok=True)
    try:
        items = parse_css(fetch(CSS_URL).decode("utf-8"))
        if not items:
            sys.exit("Не удалось найти шрифты в ответе Google Fonts.")
        manifest = []
        for it in items:
            (out / it["file"]).write_bytes(fetch(it["url"]))
            print("скачано:", it["file"])
            manifest.append({k: v for k, v in it.items() if k != "url"})
    except Exception as e:
        sys.exit(f"Не удалось скачать шрифты: {e}\nЕсли Google Fonts у вас недоступен, включите VPN на время запуска скрипта.")
    (out / "fonts.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Готово. Запустите: python3 build.py, затем загрузите папку fonts/ на сайт вместе с остальными файлами.")


if __name__ == "__main__":
    main()
