#!/usr/bin/env python3
"""Prepare a persona avatar for a 1-bit TRMNL panel.

The platform dithers whatever you send it, at whatever size you send it. Both
of those are worth taking control of: a 512px portrait resampled down to 88px
and then dithered turns into noise, because the dither is applied to a soft,
low-contrast, interpolated image. Doing the work yourself -- resize to the
exact rendered size, harden the tones, sharpen, then Atkinson-dither -- keeps
the face readable.

    python dither_avatar.py in.jpg out.png                 # tone only (recommended)
    python dither_avatar.py in.jpg out.png --mode dither   # 1-bit, fixed size

Two modes, and the default is usually the right one:

  tone    Contrast, gamma and sharpening only; output stays grayscale. TRMNL
          dithers it server-side at whatever size each layout renders, so one
          file serves the 88px slot on Full and the 52px slot on Coming Up
          without either being a rescaled dither. Serve this from your station.

  dither  Also applies the Atkinson dither and outputs 1-bit at exactly --size.
          Only right when you control the final pixel size, because scaling an
          already-dithered image destroys the pattern that makes it readable.

Atkinson (the old Mac dither) only propagates 6/8 of the error, so it clips
toward pure black and white instead of spreading mud. That is what makes it
better than Floyd-Steinberg for small faces.
"""
import argparse
from PIL import Image, ImageEnhance, ImageOps, ImageFilter


def atkinson(img):
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            old = px[x, y]
            new = 255 if old > 127 else 0
            px[x, y] = new
            err = (old - new) // 8          # 6/8 distributed, 2/8 discarded
            for dx, dy in ((1,0),(2,0),(-1,1),(0,1),(1,1),(0,2)):
                nx, ny = x+dx, y+dy
                if 0 <= nx < w and 0 <= ny < h:
                    px[nx, ny] = max(0, min(255, px[nx, ny] + err))
    return img


def prepare(path, size=88, contrast=1.6, sharpen=1.8, autocontrast=True,
            gamma=1.8, mode="tone"):
    im = Image.open(path).convert("L")
    # Square-crop from the centre so faces aren't squashed by image--cover later.
    s = min(im.size)
    im = im.crop(((im.width-s)//2, (im.height-s)//2,
                  (im.width+s)//2, (im.height+s)//2))
    # Resize FIRST, at the exact rendered size. Dithering a large image and
    # then scaling it destroys the dither pattern.
    im = im.resize((size, size), Image.LANCZOS)
    if autocontrast:
        im = ImageOps.autocontrast(im, cutoff=2)
    if gamma != 1.0:
        lut = [min(255, int(((i / 255) ** (1 / gamma)) * 255)) for i in range(256)]
        im = im.point(lut)
    im = ImageEnhance.Contrast(im).enhance(contrast)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=int(sharpen*100), threshold=2))
    if mode == "dither":
        return atkinson(im).convert("1")
    return im


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("src"); p.add_argument("dst")
    p.add_argument("--size", type=int, default=88)
    p.add_argument("--mode", choices=("tone","dither"), default="tone")
    p.add_argument("--contrast", type=float, default=1.6)
    p.add_argument("--sharpen", type=float, default=1.8)
    p.add_argument("--gamma", type=float, default=1.8,
                   help="lifts shadows before dithering; 1.8 is tuned to SUB/WAVE's\n                         persona art, which runs very dark (~90%% of pixels below\n                         quarter-tone). Lower it toward 1.0 for brighter sources.")
    a = p.parse_args()
    prepare(a.src, a.size, a.contrast, a.sharpen, gamma=a.gamma, mode=a.mode).save(a.dst)
    print(f"{a.dst}  {a.size}x{a.size}  {'1-bit' if a.mode=='dither' else 'grayscale'}")
