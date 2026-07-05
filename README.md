# storeshots

Turn raw app screenshots into polished **App Store / Play Store** marketing
images — dropped into a real device frame, with a bold caption, a brand-color
accent underline, and a clean background. Ships as a **[Claude Code][claude-code]
skill** and works standalone from the command line.

- **Real device frames** — genuine iPhone frames (Dynamic Island + buttons),
  not a hand-drawn rectangle. Screen corners clip perfectly.
- **Auto frame selection** — measures each screenshot's aspect ratio and picks
  the matching bundled frame (a 15 Pro shot → a 15-class frame, a 16 Pro Max
  shot → a 16 Pro Max frame). No per-model coordinates to maintain — the screen
  cutout is detected from the frame PNG's own alpha channel.
- **Fixed output size** — always renders at a valid App Store dimension
  (default 1320×2868, 6.9"), regardless of the source device.
- **One JSON config** — map each screenshot to a caption; tweak frame color,
  background, accent, margins, and per-image crops/patches.

## Example

Raw screenshot → framed store shot:

| Input (raw capture) | Output (store-ready) |
| --- | --- |
| a plain `IMG_1234.png` | device frame + caption + accent on a styled background, at 1320×2868 |

## Install

### As a Claude Code skill (recommended)

```bash
git clone https://github.com/launchborn/storeshots.git ~/.claude/skills/storeshots
```

Then just ask Claude Code: *"make App Store screenshots from these captures"* —
it reads `SKILL.md` and drives the rest.

### Standalone

```bash
git clone https://github.com/launchborn/storeshots.git
cd storeshots
./setup.sh            # creates ./venv and installs Pillow + numpy
```

## Usage

1. Put your screenshots in a folder.
2. Copy `config.example.json` next to them and edit the `screenshots` list.
3. Run:

```bash
./venv/bin/python3 compose.py --config path/to/your-config.json
```

Outputs land in the config's `output_dir`.

### Minimal config

```json
{
  "frame": "auto",
  "frame_color": "black",
  "src_dir": ".",
  "output_dir": "out",
  "canvas": { "width": 1320, "height": 2868 },
  "background": { "type": "gradient", "top": [22, 25, 32], "bottom": [6, 7, 9] },
  "accent": [58, 209, 122],
  "caption": { "font_size": 82, "line_height": 104, "top": 180 },
  "screenshots": [
    { "src": "IMG_0001.png", "caption": "Real apartments\nacross the country", "out": "01.png" },
    { "src": "IMG_0002.png", "caption": "Filter by what\nmatters to you",       "out": "02.png" }
  ]
}
```

See [`config.example.json`](config.example.json) for the full field list, and
[`SKILL.md`](SKILL.md) for detailed docs and per-field notes.

## Config reference (short)

| Field | Meaning |
| --- | --- |
| `frame` | `"auto"` (match by aspect) or a slug from `frames/` / a PNG path. Per-screenshot override allowed. |
| `frame_color` | Bias `"auto"` ties toward a finish (`"black"`, `"natural"`, `"deep-blue"`, …). |
| `src_dir` / `output_dir` | Resolved relative to the config file. |
| `canvas` | Final image size. Use 1320×2868 (6.9") or 1290×2796. |
| `background` | `{"type":"gradient","top":[r,g,b],"bottom":[r,g,b]}` or `{"type":"solid","color":[r,g,b]}`. |
| `accent` | `[r,g,b]` underline under the caption (omit to skip). Set to your brand color. |
| `caption` | `font_size`, `line_height`, `top`, `color`. Use `\n` for line breaks. |
| `font` | Path to a `.ttf`/`.ttc`; omit to auto-pick a bold system font. |
| `margins` | `side`, `bottom`, `gap_after_caption`. |
| per-shot `crop_top` | Trim N px off the top of a raw screenshot (status-bar artifacts). |
| per-shot `patches` | `[[x0,y0,x1,y1], …]` black rectangles over stray pixels (e.g. screen-recording touch dots). |

## Bundled frames

iPhone 15 / 16 / 17 Pro & Pro Max in several titanium/aluminum finishes — see
[`frames/`](frames). Drop any transparent-background device PNG into `frames/`
to add a model (the cutout is auto-detected).

Frame assets are third-party — see [CREDITS.md](CREDITS.md).

## Requirements

Python 3.9+, [Pillow](https://python-pillow.org/) and
[numpy](https://numpy.org/) (installed by `setup.sh`).

## License

Code: [MIT](LICENSE). Device-frame images in `frames/` are **not** covered by
the MIT license — they belong to their respective owners (Apple / Meta). See
[CREDITS.md](CREDITS.md).

[claude-code]: https://claude.com/claude-code
