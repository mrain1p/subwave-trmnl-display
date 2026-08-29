# Changelog

All notable changes to this plugin are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

### Removed

- **The now-playing track line.** TRMNL's fastest refresh is 15 minutes, so a
  track name is stale more often than not. The space went to the show
  description.

### Fixed

- Polling URL interpolation uses `{{ station_url }}`. TRMNL's help center writes
  this as `##{{ station_url }}`; the `##` is documentation escaping and is passed
  through into the fetched URL literally, degrading the plugin.

[1.0.0]: https://github.com/mrain1p/subwave-trmnl-display/releases/tag/v1.0.0
