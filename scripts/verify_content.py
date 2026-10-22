#!/usr/bin/env python3
"""Compare HEAD and rebuilt HTML text, links and table cells (stdlib only)."""
import re
import subprocess
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]

class Content(HTMLParser):
    def __init__(self, omit=()):
        super().__init__(convert_charrefs=True)
        self.omit = set(omit)
        self.stack = []
        self.text = []
        self.links = []
        self.cells = []
        self.cell = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        skip = (self.stack and self.stack[-1][1]) or tag in ('script', 'style') or bool(self.omit & set(attrs.get('class', '').split()))
        if tag not in ('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'):
            self.stack.append((tag, skip))
        if not skip:
            if tag == 'a': self.links.append(attrs.get('href'))
            if tag in ('td', 'th'): self.cell = []

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None:
            self.cells.append(normalize(''.join(self.cell)))
            self.cell = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if not self.stack or not self.stack[-1][1]:
            self.text.append(data)
            if self.cell is not None: self.cell.append(data)

def normalize(text):
    return re.sub(r'\s+', '', text)

def parse(text, omit=()):
    parser = Content(omit)
    parser.feed(text)
    return normalize(''.join(parser.text)), parser.links, parser.cells

def original(path):
    return subprocess.check_output(['git', 'show', f'HEAD:{path}'], cwd=ROOT, text=True)

page = (ROOT / 'index.html').read_text()
cells = links = 0
for path in sorted((ROOT / 'src').glob('[0-9][0-9]-*.html')):
    before = original(path.relative_to(ROOT))
    assert parse(before) == parse(path.read_text()), f'Source changed: {path}'
    gid = re.search(r'<section class="game" id="([^"]+)"', before)[1]
    built = re.search(rf'<section class="game" id="{gid}".*?</section>', page, re.S)[0]
    expected = parse(before)
    assert expected == parse(built, ('secnav', 'totop', 'app-ui')), f'Built content changed: {gid}'
    links += len(expected[1])
    cells += len(expected[2])
    print(f'PASS {path.name}: rule text, links, table cells unchanged')
# App chrome is outside static game sections; runtime tabs carry app-ui.
assert len(re.findall(r'class="game-card"', page)) == 7
assert len(re.findall(r'class="chapter"', page)) == 49
assert not re.search(r'<(?:script|img|iframe)[^>]+src=|<link[^>]+href=', page)
assert 'viewport-fit=cover' in page
assert 'apple-mobile-web-app-capable' in page
print(f'PASS: {links} rule links, {cells} table cells; 7 cards, 49 expanded chapters; no external assets')
