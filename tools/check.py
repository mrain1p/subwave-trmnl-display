#!/usr/bin/env python3
"""Pre-push checks. A settings.yml that does not parse is silently ignored by
TRMNL -- no error is surfaced -- so this is the one that really matters."""
import sys, re, yaml, glob, pathlib
root = pathlib.Path(__file__).parent / "repo" / "src"
fail = []
try:
    d = yaml.safe_load((root / "settings.yml").read_text(encoding="utf-8"))
    print("  settings.yml parses  (%d fields, id %s)" % (len(d["custom_fields"]), d["id"]))
except Exception as e:
    fail.append("settings.yml does NOT parse: %s" % e)

for f in sorted(glob.glob(str(root / "*.liquid"))):
    src = pathlib.Path(f).read_text(encoding="utf-8")
    name = pathlib.Path(f).name
    used = set(re.findall(r"\{\{\s*([a-z_][a-z0-9_]*)\s", src))
    assigned = set(re.findall(r"\{%\s*(?:assign|capture)\s+([a-z_][a-z0-9_]*)", src))
    known = assigned | {"trmnl","shows","personas","schedule","IDX_0","IDX_1","cf",
                        "show","persona","forloop","pair","h","h2","x"}
    undef = sorted(v for v in used - known)
    imgs = re.findall(r"<img[^>]*>", src)
    nodither = [i for i in imgs if "image-dither" not in i]
    inline   = [i for i in re.findall(r"<[^>]*>", src) if 'style="' in i]
    for m in ("<<<<<<<", ">>>>>>>"):
        if m in src: fail.append("%s: conflict marker %s" % (name, m))
    if undef:    fail.append("%s: undefined variables %s" % (name, undef))
    if nodither: fail.append("%s: %d img without image-dither" % (name, len(nodither)))
    if inline:   fail.append("%s: %d inline style attribute(s)" % (name, len(inline)))
    print("  %-26s %d img, %d undefined, %d inline-style" % (name, len(imgs), len(undef), len(inline)))

if fail:
    print("\nFAIL"); [print("  x", m) for m in fail]; sys.exit(1)
print("\nALL CHECKS PASS")
