# storeshots

Turn raw app screenshots into polished **App Store / Play Store** marketing
images — dropped into a real device frame, with a bold caption, a brand-color
accent underline, and a clean background. Ships as a **[Claude Code][claude-code]
skill** — you drive it entirely through the `/storeshots` command.

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
- **Two modes** — `poster` (framed phone + caption on a styled background, a
  store-listing image) or `bare` (just the device frame with the screenshot
  inside, on a **transparent** background, tightly cropped — a drop-in overlay
  PNG).

## Example

Raw screenshot → framed store shot:

| Input (raw capture) | Output (store-ready) |
| --- | --- |
| a plain `IMG_1234.png` | device frame + caption + accent on a styled background, at 1320×2868 |

## Install

```bash
git clone https://github.com/launchborn/storeshots.git ~/.claude/skills/storeshots
```

**Restart Claude Code** afterwards so it registers the `/storeshots` command
(skills are indexed at startup).

## Usage

Run the **`/storeshots`** command (or just ask in plain language, e.g. *"make
App Store screenshots from these captures"*). Claude reads `SKILL.md` and runs a
short interview — you never touch a config file:

1. **Path** — give a folder of screenshots or a single screenshot file. It must
   be a real file on disk (a pasted-in-chat image isn't enough — drag the file
   in or paste its path).
2. **Mode** — **Poster** (framed phone + caption on a styled background) or
   **Bare frame** (device + screenshot only, transparent, tight-cropped).
3. **Caption** *(poster)* — pick one of three benefit-focused suggestions or
   type your own.
4. **Background** *(poster)* — pick one of three styles or give your own colors.
5. **Where to save** — **beside the sources** (as `mockup_*.png`) or into an
   **`appstore/` subfolder**.

Claude writes a throwaway config to a temp dir, runs the composer, and shows you
the result to iterate on — it never clutters your screenshot folder with configs.

> If the command isn't recognized right after cloning, **restart Claude Code** —
> skills (and their slash commands) are indexed at startup.

The config it generates under the hood is documented in
[`config.example.json`](config.example.json) and [`SKILL.md`](SKILL.md); the
fields are summarized below for reference.

## Config reference (short)

| Field | Meaning |
| --- | --- |
| `mode` | `"poster"` (default: framed phone + caption on a styled background) or `"bare"` (device frame + screenshot only, transparent background, tight crop, no caption/margins). Per-screenshot override allowed. |
| `frame` | `"auto"` (match by aspect) or a slug from `frames/` / a PNG path. Per-screenshot override allowed. |
| `frame_color` | Bias `"auto"` ties toward a finish (`"black"`, `"natural"`, `"deep-blue"`, …). |
| `src_dir` | Folder with the raw screenshots, relative to the config file. |
| `output_dir` | Where mockups are written, relative to the config file. Omit to save beside the sources (falls back to `src_dir`); set `"appstore"` for a subfolder. |
| `out_prefix` | Prepended to each output filename (default `"mockup_"`); `""` disables. |
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
[numpy](https://numpy.org/) — the skill sets up its own `venv` on first run.

## License

Code: [MIT](LICENSE). Device-frame images in `frames/` are **not** covered by
the MIT license — they belong to their respective owners (Apple / Meta). See
[CREDITS.md](CREDITS.md).

[claude-code]: https://claude.com/claude-code
