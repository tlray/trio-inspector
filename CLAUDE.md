# Trio Loop Inspector — working notes for Claude

Single-file HTML app that visualizes oref1 (Trio/OpenAPS) loop decisions from the user's
own Nightscout site. Fully rewritten July 2026 (clean "design" redesign).

## Files
- `index.html` — THE app and the only source of truth (HTML+CSS+JS, no build step, no
  placeholders, no baked data or secrets). Deployed as-is to GitHub Pages and published as
  a claude.ai artifact. Personal "baked data" builds were removed on purpose.
- `build_versions.py` — deploy-time only (run by pages.yml): snapshots each past `index.html`
  from git history to `versions/<epoch>-<sha>.html` (with a fixed "go to latest" banner) and
  writes `versions.json` for the in-app version selector. Needs full history (checkout
  fetch-depth:0). Run locally to test: `python3 build_versions.py <outdir>`.
- `variable-map.html`, `playground.html` — standalone experiments (data-flow map; executable
  annotated source). Not wired into the app.

## Test
- Syntax check: extract the `<script>` body and `new Function()` it.
- Browser tests: Playwright with `executablePath:'/opt/pw-browsers/chromium'` (symlink to the
  chrome binary). Hermetic setup: serve `index.html` on a fake origin via `context.route`
  (`https://app.test/`), answer `https://fake-ns.test/api/v1/*` from fixtures captured with
  curl from the real Nightscout (env NIGHTSCOUT_URL/NIGHTSCOUT_TOKEN; `curl -g` for the
  bracketed query params). Fulfilled cross-origin responses NEED an
  `access-control-allow-origin:*` header or every fetch fails CORS. Beware:
  `'devicestatus.json'.endsWith('status.json')` is true — match `/status.json`.
  Pre-auth via `context.addInitScript(a=>localStorage.setItem('trioInspector.auth',a), ...)`.
  Set `timezoneId:'Europe/Amsterdam'` for stable assertions; test light+dark (`colorScheme`)
  and mobile (390×844 + `hasTouch`).
- ALWAYS run a full pass after edits: both themes screenshot, mobile snapshot + chart toggle,
  click/hover/legend, arrow-stepping (incl. across midnight), step expand/collapse, variable
  chips, login flow + sign-out, deep link.

## Architecture (inside index.html)
- CSS tokens 4× (":root", media-dark, data-theme light/dark) — edit ALL FOUR blocks.
  Chart colors mirror the Trio app asset catalog (insulin #1e96fc, ZT #7161ef, UAM #d12bf7,
  COB orange, darkerBlue #1e49ff for the IOB line, override purple `--ov`). `--txt-*`
  variants exist for TEXT (WCAG); chart strokes use the base tokens. SVG is built as HTML
  strings using `var(--x)` fills/strokes, so theme switching needs no re-render.
- Layout: header (title=go-to-latest, updated-at, ↻ refresh, 🕘 versions, sign out) →
  centered day bar (‹ date ›, date label overlays a hidden `<input type=date>`, "Today ↦"
  when off-today) → stats row (TIR+bar, average, insulin total + basal/SMB/bolus split bar,
  carbs — no boxes, negative space) → `.cols` grid: day chart card + snapshot panel (400px).
  Mobile (≤980px): snapshot-first; the day chart card hides behind a full-width
  "Day overview" toggle button.
- Day chart mirrors the Trio app's MainChartView (see tlray/Trio,
  `Trio/Sources/Modules/Home/View/Chart/`): a basal strip on TOP with temp-basal bars
  hanging DOWN from the top edge (gradient fill + solid insulin rate line at the bar edge;
  the app rotates its plot 180°), scheduled basal as a blue dashed step line, grey blocks
  for pump suspensions; then the glucose area (~278px; in-range band, right-side y labels,
  dashed grid, per-cycle target STEP line from `c.tgt` — overrides/temp targets show up
  automatically as steps —, override periods as thick purple lines at the active target
  level with their name, temp targets green, forecast curves for the selected cycle,
  bolus/SMB ▼ at BG+20 mg/dL with value label ≥0.5 U, carbs ▲ at BG−20, sgv dots colored by
  range, dashed "now" marker, selected-cycle line + time pill); then the IOB/COB strip
  (IOB scaled ×8 pos / ×9 neg like the app's CobIobChart, area+line) and hour labels.
  Legend appears ONLY on hover (bottom of chart, hover-capable pointers only).
- Snapshot panel = "what the app showed at that moment": ‹ time › nav (steps across
  midnight), copy-link 🔗, enacted/suggested pill, big colored BG + trend arrow (computed
  from the two sgv readings before t), IOB/COB/basal/target row, conclusion card
  (hypo-guard red / below-target purple / needed-vs-given bars / idle), then a SIMPLE
  forecast chart: ~45 min of real sgv dots, a "now" divider, the four forecast curves
  capped at +2.5 h (like the app), target+threshold dashed lines, hover readout line under
  it — deliberately NO markers/points/rail. Below: the 8 pipeline steps (rail with status
  dots) with the full formula/why/source/glossary-chip bodies, then the raw reason log.
- Data model per day (dayCache/localStorage): {a,b,sgv[[t,mgdl]],cycles[],smb,bolus,carbs,
  notes,siteChange,overrides[[t,durMin,label]],tempTargets[[t,durMin,targetBottom]],segs}.
  `cycles[]` items carry t/bg/iob/cob/thr/ebg/req/rate/dur/tgt/units(SMB U)/rec/reason/
  pred{IOB,ZT,COB,UAM arrays in mg/dL}. Old cached days (pre-redesign) lack
  overrides/tempTargets — always `(dd.overrides||[])`.
- Units: display follows profile units — `M()` (mg/dL→display), `fBG()`, `bgUnit()`,
  `isMmol()`. Reason-string numbers are ALREADY in profile units; devicestatus fields
  (bg, ebg, pred) are always mg/dL. NS temp-target treatments are mg/dL by convention.
- Times: browser-local, DST-safe via `localMidnight/nextDay/prevDay`. Never add fixed offsets.
- `parseReason(c)` extracts values + limit classification from the oref reason string.
  Numbers may be negative and may have a colon (`minGuardBG: -0.6`) — regexes must allow both.
- `buildSteps(c,p)` computes derived values (thr via `thrOf`, naive, guard minima, capVal,
  ratio, impliedF, impliedSmbMin), fills `VALS` (live values in glossary chips) and returns
  {rows,conc,thr}.
- Cycle identity (`buildRaw`): key each loop cycle on `suggested.deliverAt`, NOT
  `enacted.deliverAt`. The enacted deliverAt only advances when a NEW temp/SMB is sent; on a
  "no change" cycle Trio re-reports the previous enact, so keying on it silently drops every
  unchanged cycle. Read the enacted block only when its deliverAt matches this cycle (fresh);
  otherwise read `suggested`.
- Overrides arrive as `eventType:"Exercise"` treatments (name in `notes`, duration min,
  43200 = indefinite) and are uploaded TWICE by Trio (override + run, ~1s apart) — buildRaw
  merges pairs starting <120s apart, preferring the non-"Custom Override" name and the
  longer duration. There is NO target in the treatment; the drawn level comes from the
  cycle target at that time (`targetAt`).
- Nightscout access: localStorage only — keys `trioInspector.auth` {url,token},
  `trioInspector.day.<epoch>` (max ~6 days, pruned), `trioInspector.profile`. KEEP these
  key names — the stable Pages/artifact origin means existing users stay signed in across
  releases. `fetchDay` = 4 API calls, 25s timeout.
- Refresh: manual ↻ header button + `pollTick` every 30s (fetches only when viewing today,
  tab visible, cache >55s old ⇒ effectively ~1/min); also on visibilitychange. Nightscout
  has no practical push for third-party web clients (only a socket.io channel), so polling
  it is. Historical days refetch only if they were cached before the day ended.

## Conventions & pitfalls
- English UI, Trio/Nightscout terminology, U (not E), dots as decimal separator.
- Python-driven bulk edits on index.html: `assert s.count(old)==n` before replace; a
  replaced block must NOT end with the text used as the end-anchor (causes duplication bugs).
- No hardcoded therapy settings: threshold comes from cycle data (`c.thr`) → reason → derived
  from target; SMB ratio shown as measured. Mark derived values with ≈, missing with
  "— (not exported)".
- Nightscout access in dev: env vars NIGHTSCOUT_URL + NIGHTSCOUT_TOKEN (the user's own site).
  Never commit data/tokens; .gitignore covers data dumps.
- The reference algorithm source lives in the Trio repo (`trio-oref/lib/determine-basal/`) —
  add `tlray/Trio` to the session when verifying algorithm or app-UI claims
  (chart layout: `Trio/Sources/Modules/Home/View/Chart/`).

## Deep-linking & default selection
- On load with a clean URL (no hash) the app selects the NEWEST decision (today; falls back
  one day if today is empty). `#<epoch>` selects that specific decision (cross-day: `goDeep`
  does `selectDay(localMidnight(t))` then matches by `t`). Explicit navigation (chart click,
  arrows, panel nav) writes the hash via `setDeep`; clicking the title (`goLatest(true)`)
  jumps to newest AND clears the hash, so a shared clean URL always resolves to newest.
  The panel 🔗 button copies the current decision's deep link.
- Hosting: `.github/workflows/pages.yml` deploys `index.html` to GitHub Pages on push to
  `main` (and runs `build_versions.py` for the version selector). Stable origin ⇒ the entered
  Nightscout URL/token persists in localStorage across releases (no re-login). No secrets are
  ever in `index.html`. ONE-TIME enablement is MANUAL and cannot be automated from here: the
  repo must be Public (free tier) and Settings→Pages→Source set to "GitHub Actions". The
  agent proxy also blocks `github.io`, so the live site can't be curled from here — verify
  via the workflow run conclusion.
- Version selector: a `🕘` dropdown in the header lazily fetches `versions.json` and lists
  past builds (newest = "current" → root URL, older → frozen snapshot). Stays hidden when
  `versions.json` is absent (local file / claude.ai artifact).

## Publishing
- The app is published as a claude.ai artifact. To keep updating the SAME page from a new
  session, pass the existing URL to the Artifact tool:
  https://claude.ai/code/artifact/1f0e27e1-220b-4c84-9812-e7d89375c6c1 (main app, favicon 🩸)
  Experiments: variable map …/7a827d7c-2bbe-408b-96d6-0a16f301aaff (🗺️),
  playground …/ec095d69-f763-40d2-a5ce-ed686c43f9f4 (🧪).
- After each accepted change: test, commit+push, republish the artifact, and send the user
  the fresh `index.html` as a file.
