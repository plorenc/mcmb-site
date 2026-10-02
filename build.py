"""Build the static MCMB site from the docs of the (private) mcmb repo.

Usage: python build.py [path-to-mcmb-repo]   (default: ../meshcore-message-box)
Writes the finished site to ./docs (GitHub Pages serves that folder).
"""
import html
import re
import sys
from pathlib import Path

import markdown

HERE = Path(__file__).parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "meshcore-message-box"
OUT = HERE / "docs"

NAV = [("index.html", "O projekcie"), ("komendy.html", "Komendy"), ("zmiany.html", "Co nowego")]

PAGE = """<!doctype html>
<html lang="pl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — MeshCore Message Box</title>
<link rel="stylesheet" href="style.css"></head>
<body><header><div class="wrap"><a class="brand" href="index.html">MeshCore Message Box</a>
<nav>{nav}</nav></div></header>
<main class="wrap">{body}</main>
<footer class="wrap">Strona generowana automatycznie z dokumentacji projektu · {stamp}</footer>
</body></html>"""


def md(text: str) -> str:
    return markdown.markdown(text, extensions=["fenced_code", "tables", "sane_lists"])


def page(name: str, title: str, body: str) -> None:
    nav = "".join(
        f'<a href="{h}"{" class=on" if h == name else ""}>{t}</a>' for h, t in NAV
    )
    stamp = (SRC / "docs" / "architecture.md").stat().st_mtime
    import time
    OUT.joinpath(name).write_text(
        PAGE.format(title=title, nav=nav, body=body, stamp=time.strftime("%Y-%m-%d", time.localtime(stamp))),
        encoding="utf-8", newline="\n")


def commands() -> str:
    text = (SRC / "docs" / "sciaga.md").read_text(encoding="utf-8")
    text = re.sub(r"^# .*\n", "", text, count=1)
    text = text.replace("[instrukcja.md](instrukcja.md)", "instrukcji")
    return "<h1>Komendy</h1>" + md(text)


def changelog() -> str:
    text = (SRC / "docs" / "architecture.md").read_text(encoding="utf-8")
    items = []
    for m in re.finditer(r"^#{2,3} D-(\d+) — (.+)$", text, re.M):
        num, title = int(m.group(1)), m.group(2).strip()
        d = re.search(r"\((\d{4}-\d{2}-\d{2})\)\s*$", title)
        date = d.group(1) if d else ""
        title = re.sub(r"\s*\(\d{4}-\d{2}-\d{2}\)\s*$", "", title)
        items.append((num, date, title))
    items.sort(reverse=True)
    rows = []
    for num, date, title in items[:60]:
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", html.escape(title, quote=False).replace("&#x27;", "'"))
        t = t.replace("&lt;code&gt;", "<code>").replace("&lt;/code&gt;", "</code>")
        rows.append(f'<li><span class="d">D-{num}</span> {t}<span class="date">{date}</span></li>')
    return (
        "<h1>Co nowego</h1><p>Każda istotna zmiana projektu jest zapisana jako numerowana decyzja. "
        "Poniżej 60 najnowszych, od najświeższej.</p><ul class=log>" + "".join(rows) + "</ul>"
    )


def main() -> None:
    OUT.mkdir(exist_ok=True)
    (OUT / "style.css").write_text((HERE / "style.css").read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    (OUT / ".nojekyll").write_text("")
    page("index.html", "O projekcie", (HERE / "index.body.html").read_text(encoding="utf-8"))
    page("komendy.html", "Komendy", commands())
    page("zmiany.html", "Co nowego", changelog())
    print("built", OUT)


main()
