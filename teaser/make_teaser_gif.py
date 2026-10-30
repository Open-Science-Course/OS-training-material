#!/usr/bin/env python3
"""Capture the Star Wars teaser HTML as an animated GIF (slow crawl, then freeze)."""

from __future__ import annotations

import pathlib
import subprocess
import tempfile

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent
HTML = ROOT / "starwars_teaser.html"
OUT = ROOT / "lunch_seminar_teaser.gif"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Slower crawl + long readable hold
N_MOVE = 48
N_HOLD = 1  # one freeze frame with long duration
MOVE_MS = 180  # ~8.6s of motion
HOLD_MS = 5500  # hold so people can read
WIDTH, HEIGHT = 960, 540


def capture_frame(path: pathlib.Path, t: float) -> None:
    """Screenshot one frame at crawl progress t in [0, 1]."""
    url = HTML.as_uri()
    subprocess.run(
        [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            f"--window-size={WIDTH},{HEIGHT}",
            f"--screenshot={path}",
            "--virtual-time-budget=2500",
            "--run-all-compositor-stages-before-draw",
            "--default-background-color=00000000",
            f"{url}?t={t}",
        ],
        check=True,
        capture_output=True,
    )


def main() -> None:
    frames: list[Image.Image] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = pathlib.Path(tmp)
        steps = [i / (N_MOVE - 1) for i in range(N_MOVE)] + [1.0] * N_HOLD
        for i, t in enumerate(steps):
            shot = tmpdir / f"frame_{i:03d}.png"
            print(f"frame {i + 1}/{len(steps)}  t={t:.3f}")
            capture_frame(shot, t)
            im = Image.open(shot).convert("RGB")
            if im.size != (WIDTH, HEIGHT):
                im = im.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
            frames.append(im)

    durations = [MOVE_MS] * N_MOVE + [HOLD_MS] * N_HOLD
    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=False,
    )
    total = sum(durations) / 1000
    print(f"Wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB, ~{total:.1f}s)")


if __name__ == "__main__":
    main()
