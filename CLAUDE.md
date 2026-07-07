# Trio Loop Inspector — working notes for Claude

Single-file HTML app that visualizes oref1 (Trio/OpenAPS) loop decisions from the user's
own Nightscout site. Everything lives in ONE template; builds are string substitutions.

## Files
- `template.html` — THE source of truth (HTML+CSS+JS). All edits happen here.
  Placeholders: `/*__DATA__*/null` (dataset JSON), `/*__LIVE__*/null` ({url,token} for a
  personal auto-connected build), `/*__SHARE__*/false` (true = connect screen + localStorage).
- `index.html` — the shareable build: template + empty dataset + SHARE=true. No secrets.
- `build.py` — rebuilds index.html; with NIGHTSCOUT_URL/NIGHTSCOUT_TOKEN set also builds a
  git-ignored personal-snapshot.html (~3 days of data baked in).
- `variable-map.html`, `playground.html` — standalone experiments (data-flow map; executable
  annotated source). Not wired into the app.

## Build & test
- Build: `python3 build.py` (or replicate the two replaces inline).
- Syntax check: extract the `<script>` body and `new Function()` it (replace `let DATA =`
  with `var DATA =`).
- Browser tests: Playwright with `executablePath:'/opt/pw-browsers/chromium'`; load via
  `page.setContent('<!doctype html>...'+fileContents)`. Screenshot light+dark via
  `colorScheme` contexts; set `timezoneId:'Europe/Amsterdam'` for stable assertions.
- ALWAYS run a full pass after edits: both themes screenshot, click/hover, arrow-stepping
  (incl. across midnight), step expand/collapse, variable chips, sign-out flow.

## Architecture (inside template.html)
- CSS tokens 4× (":root", media-dark, data-theme light/dark) — edit ALL FOUR blocks.
  Chart colors mirror the Trio app asset catalog (insulin #1e96fc, ZT #7161ef, UAM #d12bf7,
  COB orange, darkerBlue #1e49ff for the IOB line). `--txt-*` variants exist for TEXT in the
  light theme (WCAG); chart strokes use the base tokens.
- Data model: `DATA` = {profile{basal,target,isf,cr,dia,units}, sgv[[t,mgdl]], tempBasal,
  smb, bolus, carbs, notes, siteChange, cycles[]}. `cycles[]` items carry t/bg/iob/cob/thr/
  ebg/req/rate/dur/tgt/units(SMB U)/rec/reason/pred{IOB,ZT,COB,UAM arrays in mg/dL}.
- Units: display follows `DATA.profile.units` — use `M()` (mg/dL→display), `fBG()`, `bgUnit()`,
  `isMmol()`. Reason-string numbers are ALREADY in profile units; devicestatus fields
  (bg, ebg, pred) are always mg/dL.
- Times: browser-local, DST-safe via `localMidnight/nextDay/prevDay`. Never add fixed offsets.
- `parseReason(c)` extracts values + limit classification from the oref reason string.
  Numbers may be negative and may have a colon (`minGuardBG: -0.6`) — regexes must allow both.
- `buildSteps(c,p)` computes ALL derived values once (thr, naive, guard minima gm, capVal,
  ratio, impliedF, impliedSmbMin) and fills `VALS` (live values shown in glossary chips).
- Per-day fetch+cache: `fetchDay` (4 API calls, 25s timeout), `dayCache` in-memory,
  localStorage persistence in SHARE mode (max ~6 days, pruned). Day switch auto-fetches.
- The forecast fan extends past midnight via `dd.ext` (fixed +4h zone, shaded, when the
  selected cycle is in the last 4h of a day).
- Forecast rendering: `fanPoints(c)` resolves each decision value (minGuardBG/minPredBG/
  eventualBG) to a curve point, a two-source blend (`srcs.length===2`, `f`=weight), or a
  float near the nearest point. The MAIN chart uses `drawFan()` (on-curve markers + labels
  via `layoutLabels`). The PANEL sparkline is a separate richer renderer: curves stop at a
  right RAIL where derived values sit as name-only chips at their BG level, vertically
  de-collided by `dodge1d`; value + full explanation appear in the `#sparkpt` card on hover,
  connectors to source points render into `#sparkhover` only on hover. Y-axis zooms to the
  data; threshold/target lines only drawn when in view (else a "↓ below" tag). `.sparkwrap`
  reclaims the step-body indent. Hit targets are `[data-pt]` → `SPARK.pts[]`.

## Conventions & pitfalls
- English UI, Trio/Nightscout terminology, U (not E), dots as decimal separator.
- Python-driven bulk edits on template.html: `assert s.count(old)==n` before replace; a
  replaced block must NOT end with the text used as the end-anchor (causes duplication bugs).
- No hardcoded therapy settings: threshold comes from cycle data (`c.thr`) → reason → derived
  from target; SMB ratio shown as measured. Mark derived values with ≈, missing with
  "— (not exported)".
- Nightscout access in dev: env vars NIGHTSCOUT_URL + NIGHTSCOUT_TOKEN (the user's own site).
  Never commit data/tokens; .gitignore covers personal builds.
- The reference algorithm source lives in the Trio repo (`trio-oref/lib/determine-basal/`) —
  add `tlray/Trio` to the session only when verifying algorithm claims.

## Publishing
- The app is published as a claude.ai artifact. To keep updating the SAME page from a new
  session, pass the existing URL to the Artifact tool:
  https://claude.ai/code/artifact/1f0e27e1-220b-4c84-9812-e7d89375c6c1 (main app, favicon 🩸)
  Experiments: variable map …/7a827d7c-2bbe-408b-96d6-0a16f301aaff (🗺️),
  playground …/ec095d69-f763-40d2-a5ce-ed686c43f9f4 (🧪).
- After each accepted change: rebuild, test, commit+push to main, republish the artifact,
  and send the user the fresh share build (index.html) as a file.
