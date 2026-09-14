#!/usr/bin/env python3
"""Render every layout for TRMNL OG and TRMNL X, both orientations, without Ruby or Docker.

    pip install python-liquid
    export STATION_URL=https://radio.yourstation.com     # never committed anywhere
    python tools/preview.py --serve

Pages load the real Framework 3.3.0 CSS and runtime from trmnl.com, so clamps and
overflow behave as they do on the device. The runtime is injected only after the
fonts have loaded: run earlier, the clamp engine measures with a fallback font.

The station's JSON is fetched once into the output folder (`--data` to reuse a
folder, `--refresh` to fetch again). Output goes to a temp folder by default.
"""
import argparse, datetime, json, os, pathlib, sys, tempfile, urllib.request

try:
    from liquid import Environment
except ImportError:
    sys.exit("python-liquid is required:  pip install python-liquid")

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
CSS = "https://trmnl.com/css/3.3.0/plugins.css"
JS = "https://trmnl.com/js/3.3.0/plugins.js"

# device class -> screen classes trmnlp would emit (see the Devices page of the Framework docs)
DEVICES = {
    "og": "screen screen--og screen--md screen--1bit",
    "x": "screen screen--v2 screen--lg screen--4bit",
}
MASHUP = {
    "full": None,
    "half_horizontal": "mashup mashup--1Tx1B",
    "half_vertical": "mashup mashup--1Lx1R",
    "quadrant": "mashup mashup--2x2",
}
UTC = datetime.timezone.utc


def find_by(arr, key, value):
    """TRMNL's find_by filter: first element whose `key` equals `value`, else nil."""
    if not isinstance(arr, list) or not isinstance(value, (str, int, float)):
        return None
    for item in arr:
        if isinstance(item, dict) and item.get(key) == value:
            return item
    return None


def date_filter(value, fmt):
    """Ruby-style date filter over a Unix timestamp; supports %-d / %-I / %-H / %-m on Windows."""
    if isinstance(value, (int, float)):
        dt = datetime.datetime.fromtimestamp(value, tz=UTC)
    else:
        try:
            dt = datetime.datetime.fromisoformat(str(value))
        except ValueError:
            return value
    fmt = (fmt.replace("%-d", str(dt.day)).replace("%-I", str(int(dt.strftime("%I"))))
              .replace("%-H", str(dt.hour)).replace("%-m", str(dt.month)))
    return dt.strftime(fmt)


def fetch(station, out):
    for name in ("schedule", "now-playing"):
        target = out / f"{name}.json"
        with urllib.request.urlopen(f"{station.rstrip('/')}/api/{name}", timeout=20) as r:
            target.write_bytes(r.read())
        print("fetched", target)


def wrap(view, device, portrait, inner):
    classes = DEVICES[device] + (" screen--portrait" if portrait else "")
    mashup = MASHUP[view]
    open_m = f'<div class="{mashup}">' if mashup else ""
    close_m = "</div>" if mashup else ""
    return (
        '<!DOCTYPE html><html><head><meta charset="utf-8">'
        f'<link rel="stylesheet" href="{CSS}">'
        '<meta name="trmnl-framework-version" content="3.3.0">'
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap" rel="stylesheet">'
        "<style>body{margin:0;background:#888}</style></head>"
        f'<body class="environment trmnl"><div class="{classes}">{open_m}<div class="view view--{view}">'
        f"{inner}"
        f"</div>{close_m}</div>"
        '<script>window.addEventListener("load",function(){document.fonts.ready.then(function(){'
        f'var s=document.createElement("script");s.src="{JS}";document.head.appendChild(s);'
        "});});</script></body></html>"
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--station", default=os.environ.get("STATION_URL"), help="station origin (default: $STATION_URL)")
    ap.add_argument("--data", type=pathlib.Path, default=pathlib.Path(tempfile.gettempdir()) / "subwave-trmnl-preview",
                    help="folder for the fetched JSON and the rendered pages")
    ap.add_argument("--refresh", action="store_true", help="fetch the station JSON again")
    ap.add_argument("--at", default=None, help="render as of this UTC time, e.g. 2026-09-10T17:30 (default: now)")
    ap.add_argument("--utc-offset", type=int, default=None, help="device UTC offset in seconds (default: this machine's)")
    ap.add_argument("--serve", nargs="?", const=4570, type=int, metavar="PORT", help="serve the pages on localhost")
    args = ap.parse_args()

    out = args.data
    out.mkdir(parents=True, exist_ok=True)
    if args.refresh or not (out / "schedule.json").exists():
        if not args.station:
            sys.exit("set STATION_URL or pass --station")
        fetch(args.station, out)
    idx0 = json.loads((out / "schedule.json").read_text(encoding="utf-8"))
    idx1 = json.loads((out / "now-playing.json").read_text(encoding="utf-8"))

    if args.at:
        ts = int(datetime.datetime.fromisoformat(args.at).replace(tzinfo=UTC).timestamp())
    else:
        ts = int(datetime.datetime.now(UTC).timestamp())
    if args.utc_offset is None:
        args.utc_offset = int(datetime.datetime.now().astimezone().utcoffset().total_seconds())

    env = Environment()
    env.filters["find_by"] = find_by
    env.filters["date"] = date_filter
    shared = (SRC / "shared.liquid").read_text(encoding="utf-8")
    fields = dict(station_url=args.station or "https://riverside.example.com", station_name="", subtitle="",
                  tz_offset="", show_avatars="yes", topic_size="md", title_bar="no", guide_rows=16)
    ctx = dict(IDX_0=idx0, IDX_1=idx1, **fields,
               trmnl=dict(user=dict(utc_offset=args.utc_offset), system=dict(timestamp_utc=ts),
                          plugin_settings=dict(instance_name="Riverside FM", custom_fields_values=fields)))

    links = []
    for view in MASHUP:
        inner = env.from_string(shared + (SRC / f"{view}.liquid").read_text(encoding="utf-8")).render(**ctx)
        for device in DEVICES:
            for portrait in (False, True):
                name = f"{view}-{device}-{'portrait' if portrait else 'landscape'}.html"
                (out / name).write_text(wrap(view, device, portrait, inner), encoding="utf-8")
                links.append(name)
    (out / "index.html").write_text(
        "<meta charset=utf-8><body style='font:14px sans-serif'>"
        + "".join(f'<div><a href="{l}">{l}</a></div>' for l in links), encoding="utf-8")
    print(f"rendered {len(links)} pages into {out}")

    if args.serve:
        import functools, http.server
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(out))
        print(f"serving on http://127.0.0.1:{args.serve}/  (Ctrl+C to stop)")
        http.server.ThreadingHTTPServer(("127.0.0.1", args.serve), handler).serve_forever()


if __name__ == "__main__":
    main()
