---
name: storeshots
description: >
  Generate polished App Store / Play Store screenshots by dropping raw device
  screenshots into a real iPhone device frame with a caption, accent underline,
  and styled background. Use when the user wants to turn plain app screenshots
  into store-listing marketing images ("app store screenshots", "framed
  screenshots", "device mockups", "store listing images", "рамка айфона",
  "моки для аппстора"). Auto-picks the matching frame by aspect ratio; the
  screen cutout is auto-detected from the frame's alpha so no per-model
  coordinates are needed.
---

# storeshots — App Store screenshot composer

Turns raw phone screenshots into store-ready marketing images: real device
frame (Dynamic Island + physical buttons), a bold caption, a brand-color accent
underline, and a styled background. Output size defaults to 1320×2868 — a valid
App Store 6.9"/6.7" dimension.

Throughout, `$SKILL` is this skill's own directory (where this file lives). When
installed as a Claude skill that's typically `~/.claude/skills/storeshots`.

## How to use

Drive the skill as a short **interactive interview** with `AskUserQuestion` —
don't silently guess the inputs. Collect the inputs below, then render.

1. **Path to the screenshots** — ask for either a **folder** of raw screenshots
   or a path to **one specific screenshot file**. It must be a real file on disk:
   a pasted-in-chat image is not enough, so if the user only pasted one, ask them
   to drag the file in or give its path. Paths are free-form (ask in plain text,
   or via a question's custom-answer field). **Get this first** — you need to see
   the actual screenshot before proposing captions and backgrounds. When the path
   is a folder, ignore any files already starting with the `out_prefix` (default
   `mockup_`) — those are previous outputs, not new sources.

2. **Open the screenshot(s)** and look at what each screen does — this informs
   the next two questions.

3. **Ask output mode first**, then the mode-specific questions — batch what you
   can into one `AskUserQuestion` call (offer a custom answer on each):

   - **Mode** — two choices:
     - **Poster** (default) — framed phone on a styled background with a caption
       and accent underline. The store-listing image.
     - **Bare frame** — just the device frame with the screenshot inside, on a
       **transparent** background, tightly cropped with no caption and no side
       margins. A drop-in PNG to overlay anywhere. In this mode **skip the
       caption and background questions** — they don't apply.
   - **Caption** *(poster only)* — propose **three options** phrased as user
     *benefits*, not UI labels ("Rentals right next to you", not "Nearby
     screen"). Keep them honest: only claim what the app actually does (verify
     against the codebase if unsure). The user can also type their own.
   - **Background style** *(poster only)* — propose **three** styles that suit
     the shot, e.g. a brand-color gradient sampled from the app, a dark
     gradient, and a light neutral gradient. Plus a custom option (user gives
     colors / HEX).
   - **Where to save** *(both modes)* — two choices: **the same folder as the
     screenshots** (default — files get the `mockup_` prefix) or an
     **`appstore/` subfolder**.

4. **Set up the Python env** (once — kept inside the skill dir, gitignored):

   ```bash
   python3 -m venv "$SKILL/venv"
   "$SKILL/venv/bin/pip" install -q -r "$SKILL/requirements.txt"
   ```

5. **Write a config JSON** in a **temp / scratch directory** (copy
   `config.example.json`) — do NOT drop it next to the user's screenshots; keep
   their folders clean. Because the config no longer sits beside the shots, use
   an **absolute** `src_dir` (the folder the user pointed at, or the parent of
   the single file) and an **absolute** `output_dir`. For saving **beside the
   sources** set `output_dir` to that same source folder (or omit it — it falls
   back to `src_dir`) and keep the `mockup_` `out_prefix`; for a **subfolder**
   set `output_dir` to `<source>/appstore`. For **poster** mode apply the chosen
   caption to each shot's `caption` and the chosen background to `background`;
   for **bare** mode set `"mode": "bare"` (top-level or per-shot) and drop the
   caption/background/accent — the output is a tightly-cropped **transparent**
   RGBA PNG. Paths in `src` are relative to `src_dir`. One `screenshots` entry
   per image, in the order they should appear in the store.

6. **Run it:**

   ```bash
   "$SKILL/venv/bin/python3" "$SKILL/compose.py" --config <path-to-config>.json
   ```

7. **Review the output** by reading the generated PNGs and iterate on captions,
   frame color, or background as needed.

## Config fields

- `mode` — `"poster"` (default) renders the framed phone on the styled
  `background` with the `caption` + `accent` and `margins` (a store-listing
  image). `"bare"` outputs just the device frame with the screenshot inside, on
  a **transparent** background, tightly cropped to the device with no caption
  and no side margins (a drop-in overlay PNG). In `"bare"` mode `background`,
  `caption`, `accent`, `canvas`, and `margins` are ignored. Can be set
  per-screenshot.
- `frame` — `"auto"` (default) picks the bundled frame whose screen cutout
  aspect ratio best matches each screenshot; or a slug from `frames/` (see list
  below) / a path to force one frame for all. Can also be set per-screenshot.
- `frame_color` — optional color-name bias for `"auto"` ties (e.g. `"black"`,
  `"natural"`, `"deep-blue"`), so same-aspect models resolve to your preferred
  finish.
- `src_dir` — folder holding the raw screenshots, relative to the config file.
- `output_dir` — where finished mockups are written, relative to the config
  file. **Omit it to save into the same folder as the sources** (it falls back
  to `src_dir`); set `"appstore"` to collect them in a subfolder instead.
- `out_prefix` — string prepended to every output filename (default
  `"mockup_"`). Keeps mockups distinguishable from raw shots when they share a
  folder; set to `""` to disable. Already-prefixed `out` names aren't
  double-prefixed.
- `canvas` — final image `width`/`height`. Omit to use the frame's own screen
  size. For App Store use 1320×2868 (6.9") or 1290×2796.
- `background` — `{"type":"gradient","top":[r,g,b],"bottom":[r,g,b]}` or
  `{"type":"solid","color":[r,g,b]}`.
- `accent` — `[r,g,b]` for the underline under the caption (omit to skip it).
  Set it to the app's brand color.
- `caption` — `font_size`, `line_height`, `top` (y of first line), `color`.
  Use `\n` in a caption string for manual line breaks.
- `font` — path to a `.ttf`/`.ttc`; omit to auto-pick a bold system font.
- `margins` — `side`, `bottom`, `gap_after_caption` around the framed phone.
- Per screenshot: `src`, `caption`, `out`, optional `crop_top` (px to trim off
  the top of the raw screenshot — useful when a scroll/animation artifact bleeds
  into the status bar), optional `patches` (`[[x0,y0,x1,y1], ...]` black
  rectangles painted over the raw screenshot to hide screen-recording touch
  indicators or other stray pixels).

## Tips learned in practice

- **Caption content should be a benefit, not a UI label** ("Filter by what
  matters", not "Filters screen"). Keep the first 1–3 screenshots the strongest
  — they show in search results before the listing is opened.
- **Only claim what the product actually does.** Verify features against the
  codebase before writing captions (e.g. don't say "verified" if verification is
  optional). This burned us once on this very project.
- **Don't put the paywall first** — Apple dislikes screenshots that lead with
  aggressive monetization.
- If a raw screenshot has stray digits/indicators in the status bar (from screen
  recording), find their pixel bbox and add a `patches` entry.

## Frame selection (automatic)

With `"frame": "auto"` (the default) the tool measures each screenshot's aspect
ratio and picks the bundled frame whose screen cutout matches most closely, so a
15 Pro shot lands in a 15-class frame and a 16 Pro Max shot in a 16 Pro Max
frame — no manual choice needed. `frame_color` breaks ties toward a finish.
The **output image is always the fixed `canvas` size** (default 1320×2868)
regardless of which frame was chosen.

**Apple validates the final pixel dimensions, not the source device.** Any
screenshot rendered at `canvas` = 1320×2868 (or 1290×2796) is a valid 6.9"
asset — the source phone doesn't matter for acceptance.

For **visual** correctness, the screenshot is scaled-to-COVER the frame's screen
cutout (fills completely, overflow clipped, top-aligned), so aspect-ratio
mismatches never leave a gap. In practice:

- **Any Dynamic Island iPhone (15 / 15 Pro / 15 Plus / 15 Pro Max / 16 / 16 Pro
  / 17 …)** — aspect ratios are within ~1%, so a shot from any of these looks
  right in any Pro/Pro Max frame here. The island and status bar line up.
- **Match the frame to the source when you can** for pixel-perfection: a 15 Pro
  Max shot → a 15 Pro Max frame; a 16 Pro Max shot → a 16 Pro Max frame.
- **Notched iPhones (14 non-Pro, 13, SE) and Android** — the status-bar cutout
  shape differs from a Dynamic-Island frame, so pick a matching frame (add one
  to `frames/` if needed) rather than forcing a DI frame.

## Bundled frames

`frames/` (Apple Developer Resources / Meta Device Frames via the open
[jamesjingyi/mockup-device-frames](https://github.com/jamesjingyi/mockup-device-frames)
collection — free for mockups):

- iphone-15-pro-max-black, iphone-15-pro-max-blue, iphone-15-pro-max-natural
- iphone-16-pro-black, iphone-16-pro-natural
- iphone-16-pro-max-black, iphone-16-pro-max-natural, iphone-16-pro-max-white, iphone-16-pro-max-desert
- iphone-17-pro-deep-blue
- iphone-17-pro-max-silver, iphone-17-pro-max-deep-blue, iphone-17-pro-max-cosmic-orange

To add a frame: drop any transparent-background device PNG into `frames/` (the
screen cutout is detected automatically) and reference its filename in `frame`.
More models/colors are in the source repo above (13 mini, 14 Pro Max, 16/16
Plus, 17 Air, iPads, Android, etc.).
