# Credits & asset licensing

## Device frames (`frames/`)

The device-frame PNGs in `frames/` are **third-party assets** and are **not**
covered by this repository's MIT license. They are redistributed here for
convenience so the tool works out of the box.

They were collected from the open
[jamesjingyi/mockup-device-frames](https://github.com/jamesjingyi/mockup-device-frames)
project, which in turn sources them from:

- **Apple Developer Resources** — <https://developer.apple.com/design/resources/>
  (iPhone 16 / 16 Pro / 16 Pro Max, and others)
- **Meta (Facebook) Design — Devices** — <https://design.facebook.com/toolsandresources/devices/>

The device designs and marketing frames are the property of Apple Inc. and Meta
Platforms, Inc. respectively. "iPhone" is a trademark of Apple Inc. This project
is not affiliated with, endorsed by, or sponsored by Apple or Meta.

If you are a rights holder and want an asset removed, please open an issue.

### Prefer not to redistribute the frames?

You can delete the contents of `frames/` and drop in your own transparent-
background device PNGs — the screen cutout is detected automatically from each
frame's alpha channel, so any frame works without configuration.

## Code

Everything else in this repository is released under the [MIT license](LICENSE).
