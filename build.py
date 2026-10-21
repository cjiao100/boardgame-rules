#!/usr/bin/env python3
"""Build site/index.html from src/head.html + src/NN-*.html game sections.
Nav bar and table of contents are generated automatically from each
<section class="game" id=".." data-short=".."> and its <h3 id=".."> headings."""
import glob, os, re, html, datetime
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
now = datetime.datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M")

head = open(os.path.join(SRC, "head.html"), encoding="utf-8").read()
files = sorted(f for f in glob.glob(os.path.join(SRC, "[0-9][0-9]-*.html")))
sections, nav, toc, cards = [], [], [], []
strip = lambda s: re.sub(r"<[^>]+>", "", s).strip()
for f in files:
    body = open(f, encoding="utf-8").read()
    m = re.search(r'<section class="game" id="([^"]+)" data-short="([^"]+)">', body)
    if not m:
        raise SystemExit(f"{f}: missing <section class=game id data-short>")
    gid, short = m.groups()
    h2 = re.search(r"<h2>(.*?)</h2>", body, re.S).group(1)
    h3s = re.findall(r'<h3 id="([^"]+)">(.*?)</h3>', body, re.S)
    chips = "".join(f'<a href="#{i}">{strip(t)}</a>' for i, t in h3s)
    body = body.replace("</h2>", f'</h2>\n<div class="secnav">{chips}</div>', 1)
    body = body.replace("</section>", '<a class="totop" href="#top">↑ 回到目录</a>\n</section>')
    # Preserve rule markup verbatim inside native disclosure elements.
    body = re.sub(r'(<h2>.*?</h2>)',
                  r'<details class="game-panel" open><summary>\1</summary><div class="game-body">',
                  body, count=1, flags=re.S)
    body = re.sub(r'(<h3 id="[^"]+">.*?</h3>)(.*?)(?=<h3 id=|<a class="totop")',
                  r'<details class="chapter"><summary>\1</summary><div class="chapter-body">\2</div></details>\n',
                  body, flags=re.S)
    body = body.replace('</section>', '</div></details></section>')
    body = re.sub(r'class="(ok|part|todo)"', r'class="badge \1"', body)
    # Only decorate text nodes; attributes and link destinations stay untouched.
    body = ''.join(part if part.startswith('<') else part.replace('⚠️', '<span class="badge caution">⚠️</span>')
                   for part in re.split(r'(<[^>]+>)', body))
    sections.append(body)
    title = html.unescape(strip(h2.split('<span')[0]))
    subtitle = title.removeprefix(html.unescape(short)).lstrip(" ：:").strip() or title
    cards.append(f'<a class="game-card" href="#{gid}"><strong>{html.escape(short)}</strong>'
                 f'<span>{html.escape(subtitle)}</span></a>')
    nav.append(f'<a href="#{gid}">{html.escape(short)}</a>')
    items = "".join(f'<li><a href="#{i}">{strip(t)}</a></li>' for i, t in h3s)
    toc.append(f'<li><a href="#{gid}"><b>{h2.split("<span")[0].strip()}</b></a>'
               + (re.search(r"<span.*?</span>", h2).group(0) if "<span" in h2 else "")
               + f"<ul>{items}</ul></li>")

page = head + f"""<nav class="top"><a href="#top">☰ 目录</a>{''.join(nav)}</nav>
<main>
<h1>俊伟的桌游规则手册</h1>
<p class="meta">最后更新：{now}（北京时间 UTC+8）· 共 {len(files)} 款游戏</p>
<div class="game-grid" aria-label="游戏入口">{''.join(cards)}</div>
<div class="warn">本页只收录<b>中文文字摘要</b>，整理自各游戏官方规则书；不收录规则书 PDF、规则书照片或卡图。<span class="badge caution">⚠️</span> = 未核实 / 有疑问，【推断】= 规则书未明写。实际以自己那盒的规则书和卡面为准。官方链接见各游戏「来源」。</div>
<details class="toc" open><summary>📖 目录（点开/收起）</summary><ul>{''.join(toc)}</ul></details>
{''.join(sections)}
<footer>整理：Grok Bot · 最后更新 {now}（北京时间）· 资料仅供个人查阅，版权归各出版社所有。</footer>
</main>
<a class="back-top" href="#top">↑ 回到顶部</a>
</body>
</html>
"""
out = os.path.join(HERE, "index.html")
open(out, "w", encoding="utf-8").write(page)
print(f"wrote {out} ({len(page.encode())} bytes, {len(files)} games, updated {now})")
