#!/usr/bin/env python3
"""Verify every CSS class in src/*.liquid exists in the shipped TRMNL Framework stylesheet.

    python tools/classcheck.py

The framework version comes from src/settings.yml. The stylesheet is ~18MB, so it is
downloaded once into the system temp folder and reused; pass --refresh to fetch it again,
or --css PATH to point at a copy you already have.

Why this exists: every review of this plugin so far has proposed at least one class that
does not exist in the bundle (`border-l`, `w--px`, `ml--negative`, `col--span-6`). A class
that does not exist fails silently — the markup renders, just without the styling — so
nothing catches it until a panel looks wrong on a device you did not test. Sizes are the
same trap: `w--19` and `w--22` are off the 4px scale and do nothing at all.
"""
import argparse, pathlib, re, sys, tempfile, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
URL = "https://raw.githubusercontent.com/usetrmnl/trmnl-framework/main/public/css/{ver}/plugins.css"

# Defined by this plugin (shared.liquid) or supplied by the platform rather than plugins.css.
OWN = {"sw-contrast", "title_bar", "instance", "image-dither"}

# plugins.css escapes these characters inside class selectors.
ESCAPED = set(":[]./%")


def framework_version():
    text = (SRC / "settings.yml").read_text(encoding="utf-8")
    m = re.search(r"^framework_version:\s*'?\"?([\d.]+)", text, re.M)
    if not m:
        sys.exit("could not read framework_version from src/settings.yml")
    return m.group(1)


def stylesheet(version, override=None, refresh=False):
    if override:
        return pathlib.Path(override).read_text(encoding="utf-8", errors="replace")
    cache = pathlib.Path(tempfile.gettempdir()) / f"trmnl-plugins-{version}.css"
    if refresh or not cache.exists():
        url = URL.format(ver=version)
        print(f"fetching {url}")
        with urllib.request.urlopen(url, timeout=60) as r:
            cache.write_bytes(r.read())
    return cache.read_text(encoding="utf-8", errors="replace")


def selector(token):
    return "." + "".join(("\\" + c if c in ESCAPED else c) for c in token)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--css", help="use this stylesheet instead of downloading one")
    ap.add_argument("--refresh", action="store_true", help="re-download the cached stylesheet")
    args = ap.parse_args()

    version = framework_version()
    css = stylesheet(version, args.css, args.refresh)

    tokens = {}
    for path in sorted(SRC.glob("*.liquid")):
        markup = path.read_text(encoding="utf-8")
        for m in re.finditer(r'class="([^"]*)"', markup):
            # drop Liquid tags so {{ av_extra }} and {% if %} are not read as class names
            value = re.sub(r"\{%.*?%\}|\{\{.*?\}\}", " ", m.group(1), flags=re.S)
            for token in value.split():
                tokens.setdefault(token, set()).add(path.name)

    missing = []
    for token, files in sorted(tokens.items()):
        if token in OWN:
            continue
        sel = selector(token)
        # a selector is followed by '{', ',', ' ' (descendant) or ':' (pseudo) in the bundle
        if not any(sel + c in css for c in "{, :"):
            missing.append((token, sorted(files)))

    print(f"framework {version}: {len(tokens)} distinct class tokens in src/*.liquid")
    if missing:
        print("\nNOT FOUND IN THE STYLESHEET:")
        for token, files in missing:
            print(f"  {token:40s} {', '.join(files)}")
        print("\nA class that does not exist fails silently. Check the bundle before assuming\n"
              "a reviewer's suggested class name is real.")
        sys.exit(1)
    print(f"all {len(tokens)} resolve")


if __name__ == "__main__":
    main()
