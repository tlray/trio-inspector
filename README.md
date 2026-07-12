# Trio Loop Inspector

A single-file, interactive HTML app to understand **why** [Trio](https://github.com/nightscout/Trio)
(the oref algorithm) dosed the way it did — decision by decision, day by day.

Point it at your own [Nightscout](https://nightscout.github.io/) site and it shows, for every
5-minute loop cycle:

- **A decision snapshot**, like the app showed at that moment: time (with ‹ › stepping, also
  across midnight), the glucose value with trend, IOB/COB/basal/target, the conclusion
  ("needed vs given", hypo guard, forecast below target…) and a compact forecast chart —
  the last ~45 minutes of real readings followed by the four forecast curves
  (IOB · ZT · COB · UAM, in Trio's own colors).
- **A day overview** styled after the Trio app's main chart: temp basal hanging from the top
  with the schedule as a dashed line, SMB/bolus ▼ and carbs ▲ around the glucose trace,
  overrides and temp targets on the target line, the IOB/COB strip below — with the selected
  cycle's forecast curves drawn in place. The legend appears only while hovering the chart.
- **How the decision was made**: the oref pipeline as expandable steps — inputs, forecast,
  hypo guard, target check, insulin need, SMB, temp basal, delivery — each with the real
  numbers, the formula, an explanation, a glossary and the matching algorithm source.
- **Day stats**: time in range, average, insulin (split into basal / SMB / bolus) and carbs.

Everything is one self-contained HTML file: no server, no build step, no dependencies.

## Use it

Open `index.html` in a browser (double-click works). On first use it asks for:

- your **Nightscout URL**, and
- an **access token** with the *readable* role (Nightscout → Admin tools → Subjects).

Both are stored **only in your browser** (`localStorage`) — they are never part of the file, so
`index.html` is safe to share or host. Fetched days are cached in the browser too (last ~6 days),
so revisiting is instant. While you're looking at today, the app quietly refreshes about once a
minute (plus a ↻ button in the header). **Sign out** wipes the credentials and the cached data.

The layout adapts to phones: you start at the newest decision and page through with ‹ ›; the day
overview opens with a button.

## Experiments

`variable-map.html` renders the algorithm as a clickable data-flow map: ~30 variable nodes
filled with a real cycle's values, grouped inputs → state → forecast → quantities → decision →
delivery. Click any node to trace its full ancestry (blue) and influence (orange), with a
definition and the formula instantiated for that cycle.

`playground.html` is a standalone prototype that renders the ~35-line decision layer of
determine-basal.js as live, executable annotated code: pick a real cycle as a starting point,
drag the input sliders (BG, forecasts, ISF, target, SMB settings) and watch the code re-run —
untaken branches fade, safety limits light up, and the outcome recomputes. Educational only.

## Hosting

The app is deployed to **GitHub Pages** at
[tlray.github.io/trio-inspector](https://tlray.github.io/trio-inspector/). Every push to `main`
that touches `index.html` redeploys automatically (`.github/workflows/pages.yml`).
Because `index.html` carries no secrets, the site is safe to host publicly, and the stable
origin means your Nightscout URL/token (kept only in your browser) survive across releases — no
re-login.

A **🕘 versions** menu in the header lists past builds: the root URL always serves the newest,
while older builds stay available as frozen snapshots (generated at deploy time by
`build_versions.py`).

> One-time setup: the repo must be **Public** (GitHub Pages free tier) and **Settings → Pages →
> Source** set to **"GitHub Actions"**. That source toggle is what enables Pages — the
> workflow's `enablement: true` can't create the site on its own.

## Develop

`index.html` is the app *and* the source — edit it directly; there is no build step.

Units follow your Nightscout profile automatically (mmol/L or mg/dL). Times are shown in your
browser's local timezone (Nightscout stores UTC), DST-safe. The tool reads Trio and other
oref-based uploads (OpenAPS/AAPS `devicestatus.openaps`); sites uploaded by Loop show glucose
but no loop decisions.

## Origin

Built as a learning tool for reading oref's behaviour, with the limit/forecast semantics taken
from the algorithm source in `trio-oref` (`determine-basal.js`) and the chart design and colors
matching the Trio app itself.
