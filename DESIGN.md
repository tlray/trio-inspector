# Trio Loop Inspector — design system

Working notes for keeping the app coherent. Written in English to match `CLAUDE.md`/`README.md`.
This doc is the *reference*; the tokens live in `template.html` (four `:root` blocks — see below).
When code and this doc disagree, fix one of them — don't let them drift.

## The one rule everything follows

**Colour is reserved for meaning. The interface itself is quiet.**

There are exactly two colour vocabularies, and they never mix:

1. **Semantic hues** — every coloured pixel in the *data plane* maps to a therapy concept a
   Trio user already knows (insulin = blue, zero-temp = purple, COB = orange, low = red, …).
2. **One interface accent** — a single Action Blue (`--accent`) that means exactly one thing:
   *interactive*. Links, the focus ring, the primary CTA, form-field focus, selected chrome.
   Nothing else in the chrome is coloured.

Everything else — backgrounds, cards, borders, most buttons, tabs — is neutral.

Two consequences you apply on every edit:

- A new coloured element is either a **semantic token** (it names a therapy concept) or the
  **`--accent`** (it's interactive). If it's neither, it's neutral (`--ink`/`--ink2`/`--muted`).
- **The blue tension is deliberate and bounded.** Action Blue (`--accent`, `#0066cc`) and
  insulin blue (`--iob`, `#1e96fc`) are *different blues in different planes*: `--accent`
  lives only in the chrome, `--iob` only in the chart. Never put `--accent` on a data mark,
  and never use `--iob`/`--txt-iob` for an interactive control. Kept apart, they don't
  compete; mixed, they'd both stop meaning anything.

The interface language is Apple's (apple.com): SF Pro with tight tracking, a parchment/near-
black surface system, pill controls, near-flat elevation, and the single blue accent. We run
it at a **data-dense** volume — this is an instrument, not the 80px-padding marketing gallery,
so we take Apple's *language*, not its low density.

## Two palettes

### 1. Semantic palette — frozen, mirrors the Trio asset catalog

These are the recognition anchors. **Do not restyle them to taste** — their whole job is
that they match what the user sees inside Trio. If Trio ever ships new catalog values,
update here to match; otherwise leave them.

**Forecast curves** (the four prediction lines — the heart of the app)

| Token | Light | Dark | Meaning |
|---|---|---|---|
| `--iob` | `#1e96fc` | `#1e96fc` | IOB curve / insulin |
| `--zt`  | `#7161ef` | `#7161ef` | Zero-temp curve |
| `--cob` | `#e08600` | `#ff9500` | COB curve |
| `--uam` | `#d12bf7` | `#d12bf7` | UAM curve |
| `--iobline` | `#1e49ff` | `#4a67ff` | IOB delivery line (darkerBlue) |

**Glucose ranges** (Apple system colours, as in Trio)

| Token | Light | Dark | Meaning |
|---|---|---|---|
| `--bgin`   | `#34c759` | `#30d158` | in range |
| `--bghigh` | `#ff9500` | `#ff9f0a` | high |
| `--bglow`  | `#ff3b30` | `#ff453a` | low |

**Delivery**: `--insulin` (= `--iob`), `--carb` (= `--cob`), `--basalfill` (translucent insulin).

**Limit / status** — the safety states parsed from the oref reason string:

| Token | Meaning |
|---|---|
| `--lo` | hypo guard fired / hard stop |
| `--hi` | maxBolus reached |
| `--good` | passed / delivered as needed |
| `--serious` | maxSafeBasal cap |
| `--smbwait` | waiting on SMB interval |

**WCAG rule — read this before using a semantic colour for TEXT.**
The base tokens above are tuned for **chart strokes** on the chart surface. For **text**
(chips, inline labels) use the `--txt-*` variant of the same colour, which is darkened in
the light theme to pass contrast (`--txt-iob`, `--txt-zt`, `--txt-cob`, `--txt-uam`,
`--txt-good`, `--txt-hi`, `--txt-lo`, `--txt-serious`, `--txt-smbwait`). Stroke a curve
with `--iob`; label it with `--txt-iob`.

### 2. Interface palette — Apple language, neutrals + one accent

The chrome. Apple's cool parchment-and-white in light, pure-black-and-graphite in dark, plus
the single Action Blue accent. Neutrals are Apple's system greys — picked, not defaulted.

| Token | Light | Dark | Use |
|---|---|---|---|
| `--page`      | `#f5f5f7` | `#000000` | app background (Apple parchment / true black) |
| `--surface`   | `#ffffff` | `#1c1c1e` | cards, tiles, panel |
| `--ink`       | `#1d1d1f` | `#f5f5f7` | primary text; **active-control fill** (softened near-black) |
| `--ink2`      | `#424245` | `#a1a1a6` | secondary text |
| `--muted`     | `#6e6e73` | `#8e8e93` | labels, hints, axis text |
| `--grid`      | `#e8e8ed` | `#2a2a2c` | hairline dividers, chart grid |
| `--axis`      | `#d2d2d7` | `#3a3a3c` | axis lines, inert dots |
| `--border`    | `rgba(0,0,0,.09)` | `rgba(255,255,255,.12)` | card / control borders |
| `--hover`     | `rgba(0,0,0,.05)` | `rgba(255,255,255,.07)` | row / button hover |
| `--sel`       | `#1d1d1f` | `#f5f5f7` | selected marker (ink, **not** accent) |
| `--accent`    | `#0066cc` | `#2997ff` | **the one interactive colour** — links, focus, primary CTA |
| `--accentHov` | `#0071e3` | `#3ba0ff` | accent hover/press |
| `--onAccent`  | `#ffffff` | `#ffffff` | text/icon on an accent fill |

Note the parchment trick: `--page` and `--surface` differ just enough that a white card reads
against the parchment ground **without a heavy border** — Apple separates by value, not lines.

**Controls, stated once so we stay consistent:**

- **Tab / secondary button (rest):** `--surface` fill, `--border`, `--ink2` text, **pill**
  radius (`980px`).
- **Tab (active / selected day):** `--ink` fill, `--surface` text — Apple's ink "utility"
  toggle. Selection is value, not hue (keeps blue for genuine *actions*).
- **Primary CTA (Connect):** `--accent` fill, `--onAccent` text, pill. This is the one place
  a filled blue button appears.
- **Hover:** `--hover` background; **press:** `transform: scale(.96)` (Apple's micro-press).
- **Focus:** 2px `--accent` ring, `outline-offset:2px`. Form fields also take an `--accent`
  focus glow (`box-shadow` ring).
- **Links** (source refs, in-copy): `--accent`. (`--txt-iob` is retired from chrome — it's a
  data colour now, chart-only.)

## Typography

- **Body / UI:** `system-ui, -apple-system, "Segoe UI", sans-serif` — resolves to **SF Pro**
  on Apple (matching both Trio and the Apple look). Base `14px/1.45`, `-webkit-font-smoothing:
  antialiased`, a faint global `letter-spacing:-.006em`.
- **Data / numbers / reason log:** `ui-monospace, SFMono-Regular, Menlo, monospace`. Any
  figure that a user might compare column-to-column also gets
  `font-variant-numeric: tabular-nums`.
- **Weight ladder (Apple):** 400 / 500 / 600. Headlines and emphasis sit at **600, not 700**;
  secondary wordmark text at 400. Avoid 700 in chrome.
- **Tight tracking at display sizes.** The h1 wordmark is `21px / 600 / letter-spacing:-.021em`
  — the "Apple tight" cadence. The tightening grows with size; body stays near-neutral.
- **Scale** (stay on it): 21px h1 · 17px tile value · 13–13.5px body/rows · 12–12.5px mono
  data · 10.5–11px micro-labels.
- **Micro-labels** (section headings, tile keys, "chart title"): currently uppercase,
  `letter-spacing:.05em`, `--muted` — a dashboard-legend convention. (Apple itself favours
  sentence case; switching these is a deliberate open option, not a default.)
- Keep prose columns readable: `max-width` ~72ch on explanatory `<p>`.

## Space & shape

- **Radii (Apple):** **pill** `980px` for buttons / tabs / the primary CTA · `11px` inputs ·
  `14px` tiles · `18px` the big surfaces (charts, panel, explain). Bigger surface → bigger
  radius; interactive → pill. Don't introduce new steps.
- **Chips / swatches:** 2–4px radius, 8–10px square.
- **Borders:** one hairline, `--border`; internal dividers use `--grid`. On the parchment
  ground, value contrast does most of the separating — keep borders whisper-light.
- **Elevation:** near-flat, Apple-style. No shadows on cards or buttons. The only shadow is
  the chart tooltip (`0 3px 14px rgba(0,0,0,.14)`) because it floats over content.
- **Layout:** `.wrap` centred, `max-width:1280px`. Main view is a two-column grid
  `minmax(0,1fr) 380px` (chart + sticky decision panel) that collapses to one column at
  **≤1080px**; the panel becomes static there. Tiles auto-fit at `minmax(128px,1fr)`.
- **Spacing:** lay groups out with flex/grid `gap`, not per-element margins.

## Motion

Minimal and functional, all gated behind `@media (prefers-reduced-motion: no-preference)`.
Tab/button colour transitions (~.18s), the step caret rotate (.12s), and Apple's system
micro-press on controls (`transform: scale(.96)` on `:active`). No entrance animations, no
parallax — the data is the show.

## Theming — the four-block rule (easy to get wrong)

Tokens are declared **four times** and every colour edit must touch **all four**:

1. `:root` — light defaults
2. `@media (prefers-color-scheme: dark)` — follows the OS
3. `:root[data-theme="light"]` — explicit light (overrides the media query)
4. `:root[data-theme="dark"]` — explicit dark

Blocks 3–4 exist so the in-app theme toggle can win over the OS in *both* directions. Style
components through tokens only — never hard-code a hex inside a component or inside the media
query. Give dark the same care as light: it's not an inversion (note the semantic hues that
brighten in dark, e.g. `--cob` `#e08600`→`#ff9500`, so they hold up on a near-black ground).

## Where we mirror Trio, and where we don't

- **Mirror Trio exactly:** the semantic palette (curves, glucose ranges, delivery), tabular
  figures, light/dark-follows-system. This is the recognition layer — untouchable.
- **Borrow Apple's interface language:** SF Pro with tight tracking and the 400/500/600
  ladder, the parchment/near-black surface system, pill controls, the single Action Blue
  accent, near-flat elevation, the scale(.96) press. Adapted to a **dense instrument**, not
  the low-density marketing gallery.
- **Neither Trio nor literal Apple:** the strict "colour = meaning" discipline that keeps the
  data plane and the chrome from ever sharing a hue. That's what lets a busy oref read-out
  stay calm.

## Checklist before shipping a visual change

- [ ] New colour? Semantic token (data) **or** `--accent` (interactive) — never both, never
      decorative. `--accent` stays out of the chart; `--iob` stays out of the chrome.
- [ ] Used a semantic colour on text? Switched to its `--txt-*` variant.
- [ ] Edited a token in all **four** `:root` blocks (incl. the new `--accent*` tokens).
- [ ] Checked **both** themes (screenshot light + dark).
- [ ] Numbers that line up use `tabular-nums`.
- [ ] Interactive element is a **pill**; card radius matches its size step (14/18px).
- [ ] Focus ring visible in `--accent`; `prefers-reduced-motion` still respected.
