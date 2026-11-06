#!/usr/bin/env python3
"""Добавляет в ваш build.py автоматическую расстановку неразрывных пробелов (висячие предлоги).
Запуск: положите файл рядом с build.py и выполните  python3 add_typography.py
Тексты и настройки в build.py не меняются, рядом сохраняется копия build.py.bak."""
import pathlib, shutil, sys

path = pathlib.Path(__file__).parent / "build.py"
s = path.read_text(encoding="utf-8")
if "def nb(" in s:
    sys.exit("Уже установлено: в build.py есть функция nb(). Ничего не изменено.")

BLOCK = r'''
# ---- Типографика: неразрывные пробелы, чтобы не оставались «висячие» предлоги ----
NBSP = "\u00a0"
# Короткие слова, после которых пробел становится неразрывным. Нужное слово можно дописать через |
SHORT_WORDS = ("в|во|к|ко|с|со|у|о|об|и|а|я|но|на|по|за|от|до|из|не|ни|же|ли|бы|для|без|при|про|над|под|или"
               "|a|an|in|on|to|of|at|by|or|as")
_re_short = re.compile(r"(?<![\w\-])(" + SHORT_WORDS + r")\s+", re.I)
_re_dash = re.compile(r"\s+—")                                    # пробел перед тире
_re_init = re.compile(r"\b([А-ЯЁA-Z])\.\s+(?=[А-ЯЁA-Z])")             # инициалы: А. С. Гольфингер
_re_unit = re.compile(r"(\d)\s+(?=(?:мм|см|км|кг|м|сек|мин|ГБ|МБ|КБ|₽|%)(?!\w))")  # число + единица
_re_grp = re.compile(r"(?<=\d{4})\s(?=\d{4})")                    # 1108 0674 5223

def nb(s):
    """Расставляет неразрывные пробелы в тексте. Теги (<b>) не затрагиваются."""
    if not s: return s
    s = _re_short.sub(lambda m: m.group(1) + NBSP, s)
    s = _re_dash.sub(NBSP + "—", s)
    s = _re_init.sub(lambda m: m.group(1) + "." + NBSP, s)
    s = _re_unit.sub(lambda m: m.group(1) + NBSP, s)
    return _re_grp.sub(NBSP, s)
'''

edits = [
    ("import json, pathlib\n", "import json, pathlib, re\n"),
    ('def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")',
     'def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")\n\n' + BLOCK),
    ('    HOME = t["home"]\n',
     '    HOME = t["home"]\n'
     '    t = dict(t)   # копия, в которой расставлены неразрывные пробелы\n'
     '    for key in ("hi", "h1", "lead", "contact_h", "contact_p", "footer", "services_h", "portfolio"):\n'
     '        t[key] = nb(t[key])\n'
     '    t["services"] = [(nb(h), nb(p)) for h, p in t["services"]]\n'),
    ("        title, goal, task, role, result = c[l]\n",
     "        title, goal, task, role, result = (nb(x) for x in c[l])\n"),
    ('extra=c.get(l + "_extra", [])', 'extra=[(nb(a), nb(b)) for a, b in c.get(l + "_extra", [])]'),
    ("h1,h2,h3{font-family:var(--head);font-weight:700;margin:0}",
     "h1,h2,h3{font-family:var(--head);font-weight:700;margin:0;text-wrap:balance}\np,dd,li{text-wrap:pretty}"),
]
for old, _ in edits:
    if s.count(old) != 1:
        sys.exit(f"Не удалось применить правку: фрагмент найден {s.count(old)} раз(а), нужен ровно 1:\n{old[:80]}\nbuild.py не изменён.")
shutil.copy(path, path.with_name("build.py.bak"))
for old, new in edits:
    s = s.replace(old, new)
path.write_text(s, encoding="utf-8")
print("Готово. Теперь запустите: python3 build.py")
