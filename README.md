# Trio Loop Inspector

A single-file, interactive HTML app to understand **why** [Trio](https://github.com/nightscout/Trio)
(the oref algorithm) dosed the way it did — cycle by cycle, day by day.

Point it at your own [Nightscout](https://nightscout.github.io/) site and it shows, for every
5-minute loop cycle:

- **Glucose & delivery** in the familiar Trio layout: temp basal deflecting downward from the top,
  SMB/bolus triangles, carbs along the bottom — with the four forecast curves (IOB · ZT · COB · UAM,
  in Trio's own colors) drawn from any cycle you click.
- **What Trio knew, forecast and decided**: BG, IOB, COB, autosens, effective ISF, eventualBG,
  the computed insulin need, and what was actually delivered ("needed vs given").
- **Which safety limits stepped in**: hypo guard (minGuardBG), forecast-below-target zero temps,
  maxBolus, the SMB interval and maxSafeBasal — as a compact per-day timeline plus a per-cycle
  explanation parsed from the raw oref `reason` log.
- **A live decision tree** that lights up the route the algorithm took for the selected cycle,
  with the real numbers in the decision nodes.

Everything is one self-contained HTML file: no server, no build step, no dependencies.

## Use it

Open `index.html` in a browser (double-click works). On first use it asks for:

- your **Nightscout URL**, and
- an **access token** with the *readable* role (Nightscout → Admin tools → Subjects).

Both are stored **only in your browser** (`localStorage`) — they are never part of the file, so
`index.html` is safe to share or host. Fetched days are cached in the browser too (last ~6 days),
so revisiting is instant; "Today" auto-refreshes when the cache is older than 2 minutes.
**Sign out** wipes the credentials and the cached data.

> ⚠️ The `build.py` script can also produce `personal-snapshot.html` with your own data baked in
> for offline use. That file (and `trio_data.json`) is git-ignored on purpose: it contains
> medical data. Don't commit or share it.

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
that touches `index.html` rebuilds and redeploys automatically (`.github/workflows/pages.yml`).
Because `index.html` carries no secrets, the site is safe to host publicly, and the stable
origin means your Nightscout URL/token (kept only in your browser) survive across releases — no
re-login.

A **🕘 Versions** menu in the header lists past builds: the root URL always serves the newest,
while older builds stay available as frozen snapshots (generated at deploy time by
`build_versions.py`).

> One-time setup: the repo must be **Public** (GitHub Pages free tier) and **Settings → Pages →
> Source** set to **"GitHub Actions"**. That source toggle is what enables Pages — the
> workflow's `enablement: true` can't create the site on its own.

## Develop

`template.html` is the single source. It contains three placeholders:

| Placeholder | Meaning |
|---|---|
| `/*__DATA__*/null` | replaced with a dataset JSON (empty skeleton for the shareable build) |
| `/*__LIVE__*/null` | optionally replaced with `{url, token}` for a personal auto-connected build |
| `/*__SHARE__*/false` | `true` enables the connect screen + persistent browser cache |

`python3 build.py` regenerates `index.html` from the template (and, with `NIGHTSCOUT_URL` /
`NIGHTSCOUT_TOKEN` set, a personal snapshot).

Units follow your Nightscout profile automatically (mmol/L or mg/dL). Times are shown in your
browser's local timezone (Nightscout stores UTC), DST-safe. The tool reads Trio and other
oref-based uploads (OpenAPS/AAPS `devicestatus.openaps`); sites uploaded by Loop show glucose
but no loop decisions.

## Origin

Built as a learning tool for reading oref's behaviour, with the limit/forecast semantics taken
from the algorithm source in `trio-oref` (`determine-basal.js`) and colors matching the Trio app's
asset catalog.
