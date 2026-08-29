# Working on this repo

Context for anyone — human or agent — picking this project up. Most of what
follows was learned by getting it wrong first; the reasoning is included so you
can tell when a rule stops applying.

## What this is

A TRMNL e-ink plugin that renders the schedule and on-air show for any
self-hosted [SUB/WAVE](https://www.getsubwave.com/) radio station. It is a
**community plugin** — independent of both SUB/WAVE and TRMNL. See README.

It began as a private plugin hardcoded to one station and was generalised so any
operator installs it and supplies one field: their station URL.

- **GitHub:** `mrain1p/subwave-trmnl-display`
- **TRMNL plugin id:** `460475` (in `src/settings.yml` — `trmnlp push` targets it)
- **Framework version:** 3.3.0
- **Current release:** 1.1.0

There is an **orphaned earlier plugin, id 460454**, from before the repo existed.
If the panel ever shows stale content, check which plugin is actually on the
playlist. The repo only drives 460475.

## Repo layout

```
src/           settings.yml + shared.liquid + the four view templates
tools/         check.py (pre-push checks), dither_avatar.py (persona artwork)
docs/          README screenshots
bin/trmnlp     local launcher: Ruby gem if present, Docker if not
.trmnlp.yml    local preview values only — never uploaded to TRMNL
```

## Privacy constraint — read before committing

**The operator's real station URL must not appear anywhere in this repo.** It
lives only in the TRMNL form field, which is never shared with recipe installers.
Screenshots and `.trmnlp.yml` use a fictional demo station (`Riverside FM`,
`riverside.example.com` — `example.com` is RFC 2606 reserved and cannot resolve).

Marketplace previews are rasterised images, so a real station URL in a *form
field* is private; one in the *masthead text* of a preview is not. That is why
the demo identity is set via the Station Name and Masthead Subtitle overrides
rather than by pointing at a fake API.

Commits use a masked GitHub noreply address. It cannot receive mail — the author
bio directs people to GitHub Issues, which is the working channel.

## The environment

The maintainer works on **Windows PowerShell 5.1**. Three things follow:

- **`&&` is not a statement separator.** One command per line.
- **A new shell opens at `C:\Users\mrain`, not the repo.** Always begin with
  `cd "C:\Users\mrain\SubWave-TRMNL Display"`. Omitting it once caused a
  `git init` over the entire home directory.
- Paste blocks are run verbatim, so never mix YAML or config into a block that
  looks like shell.

## The sync bot, and the git dance it forces

TRMNL runs its own GitHub integration that commits back as `trmnl-sync[bot]`
("Updated from TRMNL") whenever the plugin changes on their side. It can land at
any time, so local `main` is often behind.

**Always commit first, then pull, then push:**

```powershell
cd "C:\Users\mrain\SubWave-TRMNL Display"
git add -A
git commit -m "message"
git pull --rebase
python tools/check.py
git push
```

Pulling before staging fails with "cannot pull with rebase: You have unstaged
changes" — an agent writing files into the folder always leaves some.

**On conflict, `--theirs` means your commit.** Git inverts the labels during a
rebase: `--ours` is the branch being rebased *onto* (the bot's copy), `--theirs`
is the commit being replayed (yours). Reaching for `--ours` silently discards
your work.

```powershell
git checkout --theirs src/full.liquid src/half_horizontal.liquid src/half_vertical.liquid src/quadrant.liquid src/settings.yml
git add src
$env:GIT_EDITOR="true"
git rebase --continue
```

The `GIT_EDITOR` line stops `rebase --continue` opening vim.

**The bot is authoritative over `src/settings.yml`.** It has overwritten local
edits with TRMNL's older copy at least once. After a sync, verify your changes
survived the round-trip rather than assuming.

**It reverts whole commits, not just `settings.yml`.** Bot commit `f5407db`
rolled back every hunk of `774d217`: `framework_version` 3.3.0 &rarr; 3.1.2,
the `inverse` subtree in `full.liquid` back to `bg--black` + `text--white`, and
`w--[76px]` back to the off-scale `w--19`. Nothing was wrong with the work — the
bot simply pushed TRMNL's stale copy back down, because the broken `push` job
meant the repo had never sent anything up. `check.py` caught it only because of
the `w--19` token; the framework downgrade was silent. **After any bot commit,
run `python tools/check.py` and diff `src/` against your last commit.**

## Before pushing

```powershell
python tools/check.py
```

Catches: `settings.yml` that does not parse, undefined Liquid variables, inline
`style` attributes, `<img>` without `image-dither`, off-scale `w--`/`h--` tokens,
merge markers. Works without PyYAML (falls back to a targeted scan).

**The YAML check is the one that matters.** TRMNL *silently ignores* a
`settings.yml` it cannot parse — no error surfaces. A single unquoted `: ` inside
a description once dropped every form field with no visible failure.

### `trmnlp lint` is the same linter the reviewer runs

TRMNL's submission reviewer ("AI Chef") runs the checks shipped in
`trmnl_preview`. You can run them yourself:

```sh
bundle install            # uses the repo Gemfile; needs Ruby >= 4.0
bundle exec trmnlp lint
```

**Pin the version.** `lint` and `push` did not exist before 0.9.0, so an
unpinned `gem install` silently resolves to 0.3.2 — which has only `build`,
`serve`, `version` — and fails with `Could not find command "lint"`. This broke
CI's lint *and* push jobs for a long time, which is why the reviewer kept seeing
stale code: **the repo was never pushing to TRMNL.** Only the bot's
TRMNL→repo direction worked.

**The gem's declared Ruby requirement is wrong, and it lies quietly.**
`trmnl_preview` 0.11.0 advertises `ruby >= 3.4`, but it depends on
`trmnl-liquid ~> 0.7.0`, and every `trmnl-liquid` from 0.5.0 up requires
`ruby >= 4.0`. So the real floor is **Ruby 4.0**, and pinning the gem alone is
not enough. Worse, `gem install` does not say so: it dies inside its own
conflict reporter with `undefined method 'request' for nil`, which looks like a
RubyGems bug rather than a version floor. **Install through Bundler** — it
prints the actual chain. That is why the repo carries a `Gemfile` and CI runs
`ruby-version: "4.0"` with `bundle exec`.

The rules, as of 0.11.0: inline-style properties ≤ 6 occurrences across all
markup (counts `justify-content padding margin background-color border-radius
text-align object-fit font-size` as raw substrings, anywhere — not just inside
`style=`), description ≤ 35 chars, title ≤ 50 and capitalised, every
`.trmnlp.yml` custom field referenced in markup or polling settings, no
`view--full`-style classes, static `<img src>` URLs must resolve.

## Framework 3.3.0 — verified behaviour

Documentation at trmnl.com/framework/docs describes the newest release, which
has not always matched the declared `framework_version`. When a class's existence
or behaviour matters, **read the shipped stylesheet**, not the docs:

```
https://raw.githubusercontent.com/usetrmnl/trmnl-framework/main/public/css/3.3.0/plugins.css
```

Every selector is scoped `.trmnl .foo` — searching for `.pr--2` finds nothing;
search the bare class name.

Facts that cost time to learn:

- **`.layout` and `.flex--row` both centre on x and y by default.** Left-aligned
  output requires explicit modifiers.
- **`flex--left` / `flex--top` / `flex--center-*` only exist compounded with a
  direction class** (`.flex--row.flex--left`). Alone on a bare `.flex` they hit a
  different fallback rule whose meaning changed between 3.1.2 and 3.3.0. Always
  pair them with `flex--row` or `flex--col`.
- **`.flex` carries a default 10px gap.** Every nested flex container needs an
  explicit `gap--*`, or the spacing compounds and reads as excess padding.
- **`divider` is hard-coded to border level 6** — a dithered pattern, never a
  solid line. Use `border--h-black` / `border--v-black` for solid rules; they are
  the only unconditionally solid ones.
- **`grow`, `shrink-0`, `self--start` are `.flex > .x` child selectors.** They do
  nothing unless the parent carries `flex`.
- **`w--N` / `h--N` must land on the 4px scale** (…10 11 12 14 16 20 24…).
  `w--19` and `w--22` silently do nothing. Use `w--[Npx]` (0–128) or
  `w--[Ncqw]` (0–100) — those are pre-generated and reliable. `check.py` enforces
  this.
- **`image-dither` does not exist in the CSS** in any version. Dithering is
  entirely server-side. The class is kept because the linter asks for it; it has
  no client-side effect.
- **There is no filter/contrast utility.** `shared.liquid` defines `.sw-contrast`
  for that reason — the one piece of custom CSS, in Shared so no view carries a
  `<style>` block.
- **`inverse` (new in 3.3.0)** re-maps semantic tokens for a whole subtree and
  tracks bit depth, dark mode and palettes. It replaces `bg--black` plus
  `text--white` repeated on every child.

## Decisions that look like omissions

Don't "fix" these without reading why:

- **No now-playing track line.** TRMNL's fastest refresh is 15 minutes, so a
  track name is wrong more often than right. That space went to the show
  description. `/api/now-playing` is still polled — for `dj.station` and
  `dj.tagline`, which make the masthead self-configuring.
- **Two polling URLs from one form field.** `polling_url` has two lines, giving
  `IDX_0` (schedule) and `IDX_1` (now-playing). Collapsing them breaks branding.
- **`pr--2` / `pl--2` rather than a flex `gap` between columns.** The divider is
  painted by the right column's own left edge, so padding on both sides centres
  it. A `gap` would leave it hugging the guide text.
- **`w--[54cqw]` / `w--[46cqw]` rather than a 12-column grid.** Twelve columns
  cannot express 54/46 — the nearest is 58.3/41.7.
- **The title bar defaults to off.** The full layout already carries a wordmark,
  subtitle and date; the bar costs 40px and mainly earns its place in mashups.

## Known limitations

- **Time zones.** SUB/WAVE publishes the grid in station-local time and reports
  an IANA zone, but TRMNL's Liquid has no IANA→offset filter. The plugin renders
  in the device's zone, with a manual `tz_offset` override. The real fix is
  upstream: have `/api/schedule` return a numeric `utcOffset`.
- **Trailing slashes.** Field values interpolate into the polling URL verbatim
  and `{% assign %}` does not execute there, so the URL cannot be normalised
  inside the plugin. A trailing slash yields `//api/schedule` and a 404.
- **Persona artwork.** SUB/WAVE's default art is extremely dark (~90% of pixels
  below quarter-tone), which dithers to noise. `tools/dither_avatar.py` in its
  default *tone* mode fixes the tones and leaves the image grayscale so TRMNL
  dithers at the right size per slot. Serving tone-mode output from the station
  improves every layout at once — better than any client-side setting.

## Open items

1. **CI lint — done.** `bundle exec trmnlp lint` reports `✓ All checks passed!`
   as of `023c724`. It needed three things, not the one the old note claimed:
   the `~> 0.11` pin, installing through **Bundler**, and `ruby-version: "4.0"`.
   See the linter section above for why the Ruby floor is invisible in the
   gemspec. There was never a `workflow-trmnl.yml` — it was pasted into chat,
   not the repo; the workflow is committed directly now.
2. **`TRMNL_API_KEY` is not set, and it blocks everything downstream.** Not
   "confirm it" — confirmed absent: the `push` job logs `TRMNL_API_KEY:` with
   no value and dies on ``please run `trmnlp login` ``, and `gh secret list`
   returns nothing at all for the repo. Set it with `gh secret set
   TRMNL_API_KEY` (it prompts, so the key stays out of shell history) or via
   Settings → Secrets and variables → Actions, then rerun the failed job.

   **Until that push succeeds, the repo has still never sent anything to
   TRMNL** — which is exactly the condition that let the bot revert `774d217`.
   The 3.3.0 restore is safe in git, but it is not safe from the next sync.
3. **Check the plugin's Shared tab** contains `.sw-contrast`. If the sync does
   not carry `src/shared.liquid`, the High contrast artwork option silently does
   nothing and should be removed.
4. **Submit the recipe.** Unlisted first is the recommendation: no moderation
   queue, immediate link, and the audience is SUB/WAVE operators who will not
   find it by browsing categories. Public brings Plugin Licensing into scope.
5. **Smaller-layout screenshots** still use drawn placeholder avatars; only
   `docs/full.png` uses real artwork.

## On the AI reviewer

It has been reliably useful at finding real defects in the markup and settings —
undefined variables, a missing offline state, broken href escaping. It has been
unreliable whenever it asserts what does or does not exist in the Framework,
where it tends to suggest Tailwind class names (`border-l`, `w--px`,
`ml--negative`, `col--span-6` as a novelty) that are not in the bundle.

When it makes a claim about a class, check the stylesheet before acting. When it
points at something in these files, it is usually right.
