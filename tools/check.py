#!/usr/bin/env python3
"""Pre-push checks for the SUB/WAVE TRMNL plugin.

Runs on a bare Python install. PyYAML is used when present for a full parse;
without it the settings check falls back to scanning for the specific mistakes
that break TRMNL's parser, which matters because TRMNL silently ignores a
settings.yml it cannot read rather than reporting an error.
"""
import sys, re, glob, pathlib

root = pathlib.Path(__file__).resolve().parent.parent / "src"
fail = []

# ── settings.yml ───────────────────────────────────────────────────────────
settings = (root / "settings.yml").read_text(encoding="utf-8")
try:
    import yaml
    d = yaml.safe_load(settings)
    print("  settings.yml parses      %d fields, id %s" % (len(d["custom_fields"]), d["id"]))
    urls = [l for l in d["polling_url"].splitlines() if l.strip()]
    print("  polling URLs             %d" % len(urls))
except ImportError:
    # An unquoted YAML scalar cannot contain ": " — that turns the rest of the
    # value into a nested mapping and the whole document fails to load.
    bad = []
    for n, line in enumerate(settings.splitlines(), 1):
        m = re.match(r'^(\s*-?\s*)([A-Za-z_][\w-]*):\s+(.*)$', line)
        if not m:
            continue
        value = m.group(3).strip()
        if not value or value[0] in "\"'|>[{#":
            continue
        if re.search(r':\s', value):
            bad.append((n, m.group(2), value[:60]))
    if bad:
        for n, k, v in bad:
            fail.append("settings.yml:%d  '%s' has an unquoted value containing ': '  -> %s..." % (n, k, v))
    else:
        print("  settings.yml             no unquoted ': ' values (install pyyaml for a full parse)")
except Exception as e:
    fail.append("settings.yml does NOT parse: %s" % e)

# ── templates ──────────────────────────────────────────────────────────────
KNOWN = {"trmnl","shows","personas","schedule","IDX_0","IDX_1","cf",
         "show","persona","forloop","pair","h","h2","x"}
for f in sorted(glob.glob(str(root / "*.liquid"))):
    src  = pathlib.Path(f).read_text(encoding="utf-8")
    name = pathlib.Path(f).name
    used     = set(re.findall(r"\{\{\s*([a-z_][a-z0-9_]*)[\s.|}]", src))
    assigned = set(re.findall(r"\{%\s*(?:assign|capture)\s+([a-z_][a-z0-9_]*)", src))
    undef    = sorted(used - assigned - KNOWN)
    # w--N / h--N must land on the 4px scale; anything else silently does nothing
    SCALE = {"0","0.5","1","1.5","2","2.5","3","3.5","4","5","6","7","8","9","10",
             "11","12","14","16","20","24","28","32","36","40","44","48","52","56",
             "60","64","72","80","96","full","auto"}
    offscale = sorted({t for t in re.findall(r"[wh]--([0-9.]+|full|auto)\b", src)
                       if t not in SCALE})
    if offscale:
        fail.append("%s uses off-scale size tokens %s (use w--[Npx] instead)" % (name, offscale))
    imgs     = re.findall(r"<img[^>]*>", src)
    nodither = [i for i in imgs if "image-dither" not in i]
    inline   = [t for t in re.findall(r"<[^>]*>", src) if 'style="' in t]
    styleblk = 0 if name == "shared.liquid" else src.count("<style>")
    for mark in ("<<<<<<<", ">>>>>>>"):
        if mark in src:
            fail.append("%s contains a merge conflict marker %s" % (name, mark))
    if undef:    fail.append("%s references undefined variables: %s" % (name, undef))
    if nodither: fail.append("%s has %d <img> without image-dither" % (name, len(nodither)))
    if inline:   fail.append("%s has %d inline style attribute(s)" % (name, len(inline)))
    if styleblk: fail.append("%s has a <style> block (belongs in shared.liquid)" % name)
    print("  %-24s %d img  %d undefined  %d inline-style" % (name, len(imgs), len(undef), len(inline)))

if fail:
    print("\nFAIL")
    for m in fail: print("  x", m)
    sys.exit(1)
print("\nALL CHECKS PASS")
