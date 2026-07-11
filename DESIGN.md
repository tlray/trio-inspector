# Trio Loop Inspector — design system

Working notes for keeping the app coherent. Written in English to match `CLAUDE.md`/`README.md`.
This doc is the *reference*; the tokens live in `template.html` (four `:root` blocks — see below).
When code and this doc disagree, fix one of them — don't let them drift.

## The one rule everything follows

**Colour is reserved for meaning. The interface itself is quiet.**

Every coloured pixel in this app maps to a therapy concept a Trio user already knows
(insulin = blue, zero-temp = purple, COB = orange, low = red, …). So the *chrome* —
buttons, tabs, backgrounds, borders, links, focus rings — stays **neutral**. A coloured
control would be a colour that means nothing, and it would compete with the signals that
do mean something. This is the deliberate place where we diverge from the Trio app, whose
tinted buttons and busier chrome we are *not* copying.

Two consequences you apply on every edit:

- A new coloured element must resolve to a **semantic token**. If you can't name its
  meaning, it should be neutral (`--ink` / `--ink2` / `--muted`).
- Interactive ≠ coloured. "This is clickable" is carried by weight, the ink-fill on the
  active tab, hover background, and the focus ring — not by hue.

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

### 2. Interface palette — ours, calm and neutral

The chrome. Warm off-white grounds and warm greys (a faint olive bias, not a pure/clinical
grey — chosen, not defaulted). No accent hue of its own.

| Token | Light | Dark | Use |
|---|---|---|---|
| `--page`    | `#f9f9f7` | `#0d0d0d` | app background |
| `--surface` | `#fcfcfb` | `#1a1a19` | cards, tiles, panel |
| `--ink`     | `#0b0b0b` | `#ffffff` | primary text; **active-control fill** |
| `--ink2`    | `#52514e` | `#c3c2b7` | secondary text |
| `--muted`   | `#6e6c66` | `#898781` | labels, hints, axis text |
| `--grid`    | `#e1e0d9` | `#2c2c2a` | hairline dividers, chart grid |
| `--axis`    | `#c3c2b7` | `#383835` | axis lines, inert dots |
| `--border`  | `rgba(11,11,11,.10)` | `rgba(255,255,255,.10)` | card / control borders |
| `--hover`   | `rgba(9,9,9,.045)` | `rgba(255,255,255,.06)` | row / button hover |
| `--sel`     | `#0b0b0b` | `#ffffff` | selected marker |

**Controls, stated once so we stay consistent:**

- **Tab / button (rest):** `--surface` fill, `--border`, `--ink2` text.
- **Tab / button (active or primary, e.g. Connect):** `--ink` fill, `--page` text. The
  emphasis is value (dark vs light), never hue.
- **Hover:** `--hover` background.
- **Focus:** a visible 2px ring, `outline-offset:2px`. It currently uses `--txt-iob`
  (blue) — the one pragmatic exception to "neutral chrome", because a blue focus ring is a
  near-universal convention. Keep it, but don't grow blue into any other chrome.
- **Links** (source refs, var chips): also lean on `--iob`/`--txt-iob` today. If you touch
  them, prefer neutralising toward `--ink2` with an underline over adding more blue.

## Typography

- **Body / UI:** `system-ui, -apple-system, "Segoe UI", sans-serif` — this resolves to SF
  on Apple, matching Trio. Base `14px/1.45`.
- **Data / numbers / reason log:** `ui-monospace, SFMono-Regular, Menlo, monospace`. Any
  figure that a user might compare column-to-column also gets
  `font-variant-numeric: tabular-nums`.
- **Scale** (stay on it): 19px h1 (weight 650, `letter-spacing:-.01em`) · 17px tile value ·
  13–13.5px body/rows · 12–12.5px mono data · 10.5–11px uppercase micro-labels.
- **Micro-labels** (section headings, tile keys, "chart title"): uppercase,
  `letter-spacing:.05em`, colour `--muted`. This is the app's quiet structural voice — use
  it for labels, never for content.
- Keep prose columns readable: `max-width` ~72ch on explanatory `<p>`.

## Space & shape

- **Radii:** 6px (nav group, small inputs) · 7px (tab, reason block, cards-in-panel) ·
  8px (tile) · 10px (the big surfaces: charts, panel, explain). Bigger surface → bigger
  radius. Don't introduce new radii.
- **Chips / swatches:** 2–4px radius, 8–10px square.
- **Borders:** one hairline, `--border`; internal dividers use `--grid`.
- **Elevation:** flat by default. The only shadow in the app is the chart tooltip
  (`0 3px 14px rgba(0,0,0,.14)`) because it floats over content. Don't shadow cards.
- **Layout:** `.wrap` centred, `max-width:1280px`. Main view is a two-column grid
  `minmax(0,1fr) 380px` (chart + sticky decision panel) that collapses to one column at
  **≤1080px**; the panel becomes static there. Tiles auto-fit at `minmax(128px,1fr)`.
- **Spacing:** lay groups out with flex/grid `gap`, not per-element margins.

## Motion

Minimal and functional. Only tab/button colour and the step caret animate, all gated behind
`@media (prefers-reduced-motion: no-preference)` with 0.12s transitions. No entrance
animations, no parallax — the data is the show.

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

- **Mirror exactly:** the semantic palette (curves, glucose ranges, delivery), the SF type
  family, tabular figures, light/dark-follows-system.
- **Deliberately ours:** neutral chrome (no tinted buttons), the calmer warm-grey ground,
  the strict "colour = meaning" discipline, generous hairline-separated card layout. This is
  the answer to Trio feeling a bit busy — we keep its *language of meaning* and drop its
  *interface noise*.

## Checklist before shipping a visual change

- [ ] New colour? It maps to a semantic token — or it's neutral. No decorative hues.
- [ ] Used a semantic colour on text? Switched to its `--txt-*` variant.
- [ ] Edited a token in all **four** `:root` blocks.
- [ ] Checked **both** themes (screenshot light + dark).
- [ ] Numbers that line up use `tabular-nums`.
- [ ] New radius/shadow reuses an existing step, doesn't invent one.
- [ ] Focus ring still visible; `prefers-reduced-motion` still respected.
