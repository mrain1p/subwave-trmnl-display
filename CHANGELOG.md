# Changelog

All notable changes to this plugin are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] — 2026-08-29

### Added

- **Masthead Subtitle field.** Free text for the line under the wordmark &mdash;
  a web address, a slogan. Blank falls back to the station's own tagline, then
  to its hostname.
- **Show Description Size field** (Large / Normal / Small), setting type size
  and line clamp together so long write-ups end in an ellipsis rather than a
  clipped line.
- **DJ Artwork treatments.** Dithered, High contrast, Outlined or Hidden. A
  1-bit panel dithers whatever it is sent, and dark low-contrast portraits
  become noise; High contrast drives the background to solid black first,
  Outlined adds a hairline edge.
- **TRMNL Title Bar field**, off by default. The full layout already carries a
  station wordmark; the bar earns its place in mashups.
- **`tools/dither_avatar.py`** &mdash; resizes to the rendered size, hardens the
  tones and applies an Atkinson dither before the image reaches TRMNL. Better
  results than any client-side treatment.
- **Plugin icon** (`icon.png`, `icon.svg`).

### Changed

- **Markup rewritten against the TRMNL Framework.** Inline styles went from 46
  to zero: `flex`/`gap` for layout, `p--`/`m--` for spacing, `bg--black` and
  `text--white` for inverted blocks, `divider` and `divider--v` for rules,
  `title`/`label`/`description` for type, and `data-clamp` in place of
  `-webkit-line-clamp`. The guide list uses `data-overflow` so the runtime drops
  rows that do not fit.
- **Responsive behaviour.** The full layout's two columns stack in portrait
  (`portrait:flex--col`), and the description clamps to fewer lines there.
- Masthead subtitle set at 12px so a long web address and the date fit on one
  line instead of truncating.
- **Alignment corrected against the real Framework defaults.** `.layout` and
  `.flex--row` both centre on both axes, and the `flex--left` / `flex--top`
  modifiers only exist compounded with a direction class &mdash; so they are now
  always paired. Every nested flex container carries an explicit `gap--*`,
  because bare `.flex` applies a 10px gap that was compounding into what looked
  like excess padding.
- **Solid rules.** `.divider` is hard-coded to border level 6, a 12px-period
  dithered pattern that renders as light dots. All rules now use
  `border--h-black` / `border--v-black`, the only unconditionally solid ones.

- **`src/shared.liquid`.** Shared markup is injected ahead of every view, so
  the one CSS rule the Framework has no utility for (a `filter`, used by the
  High contrast artwork option) is defined once there instead of in a `<style>`
  block per view.
- **An explicit "station unreachable" state.** Previously an offline station
  rendered as "Unscheduled", which reads as *nothing is booked right now* rather
  than *the plugin cannot see your station*. Now distinguished by checking that
  shows and the grid both came back.
- Both full-layout columns carry explicit widths, so a container-query base and
  `grow` cannot disagree about the split.

### Removed

- **The now-playing track line.** TRMNL's fastest refresh is 15 minutes, so a
  track name is stale more often than not. That space went to the show
  description. `/api/now-playing` is still polled for station name and tagline.

### Fixed

- Templates read form fields from `trmnl.plugin_settings.custom_fields_values`
  with a bare-name fallback, so they work whichever way TRMNL supplies them.
- Schedule blocks crossing midnight merge into one guide row instead of two.
- Unscheduled hours render an explicit state rather than a blank panel.

## [1.0.0] — 2026-08-29

First public release. Rebuilt from a private single-station plugin into one any
SUB/WAVE operator can install.

### Added

- **Station URL form field.** The only required setting. Station name, tagline,
  DJ personas, artwork and the weekly grid are all read from that station's API.
- **Masthead Subtitle field.** Free text for a web address or slogan; falls back
  to the station's own tagline, then to its hostname.
- **Show Description Size field.** Large / Normal / Small / Extra small, setting
  type size and line clamp together so long write-ups end in an ellipsis instead
  of a clipped line.
- **Station Name, Station UTC Offset, DJ Artwork and Programming Guide Length**
  fields, all optional with working defaults.
- **`half_vertical` and `quadrant` layouts**, which did not previously exist.
- **`/api/now-playing` polling**, used for masthead branding.
- Local preview via `bin/trmnlp serve`, and CI that lints pull requests and
  pushes to TRMNL on merge to `main`.

### Changed

- **`half_horizontal` rewritten.** It previously dumped raw JSON into a `<pre>`
  tag; it now renders the on-air show, host and description.
- Schedule blocks that cross midnight merge into a single row in the guide
  instead of appearing twice.
- Unscheduled hours render an explicit "Unscheduled" state rather than a blank
  panel.
- Templates read form fields from `trmnl.plugin_settings.custom_fields_values`
  with a bare-name fallback, so they work whichever way TRMNL supplies them.

- **`src/shared.liquid`.** Shared markup is injected ahead of every view, so
  the one CSS rule the Framework has no utility for (a `filter`, used by the
  High contrast artwork option) is defined once there instead of in a `<style>`
  block per view.
- **An explicit "station unreachable" state.** Previously an offline station
  rendered as "Unscheduled", which reads as *nothing is booked right now* rather
  than *the plugin cannot see your station*. Now distinguished by checking that
  shows and the grid both came back.
- Both full-layout columns carry explicit widths, so a container-query base and
  `grow` cannot disagree about the split.

### Removed

- **The now-playing track line.** TRMNL's fastest refresh is 15 minutes, so a
  track name is stale more often than not. The space went to the show
  description.

### Fixed

- Polling URL interpolation uses `{{ station_url }}`. TRMNL's help center writes
  this as `##{{ station_url }}`; the `##` is documentation escaping and is passed
  through into the fetched URL literally, degrading the plugin.

[1.1.0]: https://github.com/mrain1p/subwave-trmnl-display/releases/tag/v1.1.0
[1.0.0]: https://github.com/mrain1p/subwave-trmnl-display/releases/tag/v1.0.0
