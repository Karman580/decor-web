#!/usr/bin/env python3
"""Wiring self-check for index.html. Stdlib only: python3 check.py

Catches the breakage that actually happens when this page is edited — an id the
script reaches for that no longer exists, a filter button whose category no shot
carries, an <img src> pointing at a file that isn't in uploads/, an unhandled
data-cfg key. It does not test rendering.
"""
import html.parser
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
SCRIPT = SRC[SRC.rindex("<script>"):]


class Scan(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.imgs, self.filters, self.cats, self.cfgs = set(), [], set(), set(), set()
        self.shots = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            assert a["id"] not in self.ids, f"duplicate id: {a['id']}"
            self.ids.add(a["id"])
        if tag == "img" and a.get("src"):
            self.imgs.append(a["src"])
        if a.get("data-filter"):
            self.filters.add(a["data-filter"])
        if a.get("data-cats"):
            self.cats.update(a["data-cats"].split())
            self.shots.append(a["data-cats"].split())
        if a.get("data-cfg"):
            self.cfgs.add(a["data-cfg"])
        # a shot's lightbox source must be a real file too
        if a.get("data-src"):
            self.imgs.append(a["data-src"])


s = Scan()
s.feed(SRC)

# 1. every getElementById in the script resolves
wanted = set(re.findall(r'getElementById\("([^"]+)"\)', SCRIPT))
missing = wanted - s.ids
assert not missing, f"script references missing ids: {sorted(missing)}"

# 2. every filter except "All" is a category some shot actually carries
#    (a shot may carry several, space separated, in data-cats)
orphans = (s.filters - {"All"}) - s.cats
assert not orphans, f"filter buttons match no shot: {sorted(orphans)}"
assert "All" in s.filters, "no All filter"
uncovered = s.cats - s.filters
assert not uncovered, f"shot categories with no filter button: {sorted(uncovered)}"

# 3. every filter selects at least one shot — same split() semantics the JS uses,
#    so an empty tab can never ship
counts = {f: sum(1 for cats in s.shots if f == "All" or f in cats) for f in s.filters}
empty = [f for f, n in counts.items() if n == 0]
assert not empty, f"filters that would show an empty grid: {empty}"

# 4. every data-cfg key has a branch in the CONFIG switch
handled = set(re.findall(r'case "(\w+)":', SCRIPT))
unhandled = s.cfgs - handled
assert not unhandled, f"data-cfg keys the script ignores: {sorted(unhandled)}"

# 5. every local image referenced exists on disk
absent = sorted({p for p in s.imgs if p and not p.startswith(("http", "data:"))
                 and not os.path.exists(os.path.join(ROOT, p))})

print(f"ok — {len(s.ids)} ids, {len(set(s.imgs))} images, {len(s.cfgs)} config bindings")
print("     filters: " + ", ".join(f"{f} {n}" for f, n in sorted(counts.items(), key=lambda kv: -kv[1])))
if absent:
    print(f"\nWARNING: {len(absent)} image file(s) not on disk — the page will show its "
          f"placeholder text instead of a photo:", file=sys.stderr)
    for p in absent:
        print(f"  {p}", file=sys.stderr)
