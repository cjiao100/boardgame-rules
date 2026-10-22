#!/usr/bin/env python3
"""Build site/index.html from src/head.html + src/NN-*.html game sections.
App home and chapters are generated automatically from each
<section class="game" id=".." data-short=".."> and its <h3 id=".."> headings."""
import glob, os, re, html, datetime
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
now = datetime.datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M")

head = open(os.path.join(SRC, "head.html"), encoding="utf-8").read()
files = sorted(f for f in glob.glob(os.path.join(SRC, "[0-9][0-9]-*.html")))
sections, cards = [], []
strip = lambda s: re.sub(r"<[^>]+>", "", s).strip()
for f in files:
    body = open(f, encoding="utf-8").read()
    m = re.search(r'<section class="game" id="([^"]+)" data-short="([^"]+)">', body)
    if not m:
        raise SystemExit(f"{f}: missing <section class=game id data-short>")
    gid, short = m.groups()
    h2 = re.search(r"<h2>(.*?)</h2>", body, re.S).group(1)
    h3s = re.findall(r'<h3 id="([^"]+)">(.*?)</h3>', body, re.S)
    # Wrap chapters without inserting UI text into game sections.
    body = re.sub(r'(<h3 id="([^"]+)">.*?</h3>)(.*?)(?=<h3 id=|</section>)',
                  r'<div class="chapter" data-chapter="\2">\1\3</div>\n',
                  body, flags=re.S)
    body = re.sub(r'class="(ok|part|todo)"', r'class="badge \1"', body)
    # Only decorate text nodes; attributes and link destinations stay untouched.
    body = ''.join(part if part.startswith('<') else part.replace('⚠️', '<span class="badge caution">⚠️</span>')
                   for part in re.split(r'(<[^>]+>)', body))
    # Classify tables without rewriting any rule text or cell markup.
    def decorate_table(match):
        markup = match[0]
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', markup, re.S)
        is_pair = bool(rows) and all(
            len(re.findall(r'<(?:td|th)\b', row)) == 2 and
            not re.search(r'\b(?:colspan|rowspan)=', row) for row in rows)
        kind = 'kv' if is_pair else 'data'
        return markup.replace('class="tw"', f'class="tw {kind}"', 1)
    body = re.sub(r'<div class="tw"><table>.*?</table></div>', decorate_table, body, flags=re.S)
    sections.append(body)
    title = html.unescape(strip(h2.split('<span')[0]))
    subtitle = title.removeprefix(html.unescape(short)).lstrip(" ：:").strip() or title
    badge = re.search(r'<span.*?</span>', h2).group(0) if '<span' in h2 else ''
    cards.append(f'<a class="game-card" href="#{gid}" data-route="/g/{gid}">'
                 f'<span class="card-copy"><strong>{html.escape(short)}</strong>'
                 f'<span class="subtitle">{html.escape(subtitle)}</span></span>{badge}'
                 '<span class="chevron" aria-hidden="true">›</span></a>')

page = head + f"""<header class="app-bar"><a id="back" href="#/" hidden>‹ 返回</a><h1 id="app-title" tabindex="-1">桌游规则</h1></header>
<main>
<div id="home">
<div class="game-grid" aria-label="游戏入口">{''.join(cards)}</div>
<p class="meta">最后更新：{now}（北京时间 UTC+8）· 共 {len(files)} 款游戏</p>
<p class="intro">本页只收录<b>中文文字摘要</b>，整理自各游戏官方规则书；不收录规则书 PDF、规则书照片或卡图。<span class="badge caution">⚠️</span> = 未核实 / 有疑问，【推断】= 规则书未明写。实际以自己那盒的规则书和卡面为准。官方链接见各游戏「来源」。</p>
</div>
<nav id="chapter-tabs" class="app-ui" aria-label="章节" hidden></nav>
{''.join(sections)}
<nav id="chapter-pager" aria-label="章节翻页" hidden><button id="previous" type="button">‹ 上一章</button><span id="chapter-count" aria-live="polite"></span><button id="next" type="button">下一章 ›</button></nav>
<footer>整理：Grok Bot · 最后更新 {now}（北京时间）· 资料仅供个人查阅，版权归各出版社所有。</footer>
</main>
</body>
</html>
"""

out = os.path.join(HERE, "index.html")
open(out, "w", encoding="utf-8").write(page)
print(f"wrote {out} ({len(page.encode())} bytes, {len(files)} games, updated {now})")
