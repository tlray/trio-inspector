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
- Tests freeze the app clock via addInitScript (shifted Date class, real timers) at a moment
  covered by the fixtures — otherwise every run after local midnight breaks on "today".
- Flex-column pitfall: `.cols>*` needs `min-width:0;max-width:100%` or a wide `white-space:pre`
  formula block blows the panel past the mobile viewport.
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
- Layout: header (title=go-to-latest, updated-at, ⋯ menu = refresh + older versions +
  sign out) → `.cols` grid: left `.daysec` (topbar row: ‹ date ▾ › day nav — click opens
  the native picker via `showPicker()` with a visible-input fallback —, "Today ↦" when
  off-today, inline day stats with 34px mini bars; then the day chart card) + snapshot
  panel (400px). Mobile (≤980px): `.daysec` is ONE tappable card (nav+stats; tap or
  chevron expands the chart inside it), stat labels hidden; decision panel below; fixed
  bottom pager with wide ‹ time › buttons + a "now" button that doubles as live indicator
  (green ● on the newest decision, blue ↦ otherwise → goLatest); at the newest decision
  the forward buttons get `.end` (dimmed); the panel's ‹ › next to the time are hidden on
  mobile; the day ‹ › sit absolutely at the card edges. Swipe gestures: day block ⇄ days,
  panel ⇄ decisions (addSwipe: dx≥45px, <700ms, |dx|>1.5|dy|; a teaser "ghost card" of the
  neighbouring day/decision appears beside the block and both follow the finger; on release
  the cards slide over and the handler fires; teaser returning null = nothing that side =
  snap back; horizontal moves preventDefault so the page doesn't scroll mid-swipe).
  Day switches via ‹ ›/picker/swipe go through `gotoDay` and keep the selected decision's
  time of day. `touch-action:manipulation` everywhere
  (kills iOS double-tap zoom + tap delay), sticky :hover reset under `@media (hover:none)`,
  inputs 16px on coarse pointers (no focus zoom). Stepping → past the newest decision of
  today quietly re-fetches (catch-up).
- Day chart mirrors the Trio app's MainChartView (see tlray/Trio,
  `Trio/Sources/Modules/Home/View/Chart/`): a basal strip on TOP with temp-basal bars
  hanging DOWN from the top edge (gradient fill + solid insulin rate line at the bar edge;
  the app rotates its plot 180°), scheduled basal as a blue dashed step line, grey blocks
  for pump suspensions; then the glucose area (~204px; in-range band, right-side y labels,
  dashed grid, per-cycle target STEP line from `c.tgt` — overrides/temp targets show up
  automatically as steps —, override periods as thick purple lines at the active target
  level with their name, temp targets green, forecast curves for the selected cycle,
  bolus/SMB ▼ at BG+20 mg/dL with value label ≥0.5 U, carbs ▲ at BG−20, sgv dots colored by
  range, dashed "now" marker, selected-cycle line + time pill); then the IOB/COB strip
  (IOB scaled ×8 pos / ×9 neg like the app's CobIobChart, area+line); then the safety-limits
  strip (`LIMROWS` lanes: unrestricted dosing / hypo guard / forecast<target / IOB ceiling /
  SMB limited / SMB interval / basal limited — runs of consecutive cycles whose
  `parseReason(c).limits` keys match; `limKeys(c)` caches keys NON-enumerably so persisted
  day JSON stays clean; lane order top→bottom = `#limleg` legend order, an always-visible
  chips+counts row BELOW the chart; hover tooltip also names active limits) and hour labels.
  Legend appears ONLY on hover (bottom of chart, hover-capable pointers only).
- Snapshot panel = "what the app showed at that moment": big colored BG + trend arrow
  (computed from the two sgv readings before t) left, ‹ time › nav top-right (steps across
  midnight), IOB/COB/basal/target row, then a SIMPLE forecast chart: ~45 min of real sgv
  dots, a "now" divider, the four forecast curves capped at +2.5 h (like the app), actual
  readings AFTER the decision at 50% opacity (forecast vs reality), bolus/SMB ▼ and
  carbs ▲ (same shapes/sizes as the day chart; ones after the decision also at 50% —
  everything right of "now" reads soft = hadn't happened yet, and the curves themselves
  are drawn at 50% so they don't shout over the real dots), target+threshold
  dashed lines, hover readout line under it — deliberately NO markers/points/rail; the y-domain always spans the full in-range band so the axis stays put between decisions. The
  conclusion card sits BELOW the chart and has a CONSTANT height (`.conc.main`,
  min-height 80px, content vertically centered) so the steps below never shift while
  stepping. Enacted/suggested is ONLY the small `.cdot` badge top-right (green ✓ =
  enacted, dashed circle = suggested); the → deliver step spells it out next to the same
  badge so users learn the mapping — don't reintroduce a text chip on the card. Variants:
  hypo-guard red / below-target purple / a ONE-ROW given-vs-needed bar (dashed outline =
  needed, filled = given, "given / needed U" + %) / idle. Below: the 8 pipeline steps (rail with status dots) with
  the full formula/why/source/glossary-chip bodies, then the raw reason log.
- Data model per day (dayCache/localStorage): {a,b,sgv[[t,mgdl]],cycles[],smb,bolus,carbs,
  notes,siteChange,overrides[[t,durMin,label]],tempTargets[[t,durMin,targetBottom]],segs}.
  `cycles[]` items carry t/bg/iob/cob/thr/ebg/req/rate/dur/tgt/units(SMB U)/rec/reason/
  creq(carbsReq g)/xd(expectedDelta)/md(minDelta, both mg/dL-per-5m)/
  pred{IOB,ZT,COB,UAM arrays in mg/dL}. Old cached days (pre-redesign) lack
  overrides/tempTargets — always `(dd.overrides||[])`; pre-carbsReq days lack creq/xd/md.
- Units: display follows profile units — `M()` (mg/dL→display), `fBG()`, `bgUnit()`,
  `isMmol()`. Reason-string numbers are in profile units ONLY in the Swift-formatted
  devicestatus record (see dual upload below); the raw oref twin's reason is always mg/dL —
  parseReason has a guard (mmol profile + parsed ISF>20 ⇒ convert BG-scale fields).
  Devicestatus FIELDS (bg, ebg, pred, expectedDelta, minDelta) are always mg/dL;
  `suggested.threshold` follows the record variant. NS temp-target treatments are mg/dL.
- Times: browser-local, DST-safe via `localMidnight/nextDay/prevDay`. Never add fixed offsets.
- `parseReason(c)` extracts values + limit classification from the oref reason string.
  Numbers may be negative, may have a colon (`minGuardBG: -0.6`) AND may have spaces around
  comparators (`Eventual BG 99 < 110` in the raw variant) — regexes must allow all three.
  Limit keys: guard/zero/rising (below target but minDelta>expectedDelta ⇒ basal held, NOT
  wound down)/maxiob (IOB>max_iob ⇒ neutral temp)/smbjump (maxDelta>20% of BG ⇒ SMB off)/
  maxbolus/smbwait/maxbasal. Also fills p.creq+p.creqMin ("N add'l carbs req w/in Mm") and
  p.maxIob. carbsReq is ALSO a devicestatus field (`suggested.carbsReq`) — preferred source.
- Exit model in `buildSteps`: guard exits after step 3, zero/rising after 4, maxiob after 5
  (matches the real early returns in determine-basal.js). Step 7 is NOT dimmed on an early
  exit — it shows the temp that the guard/target check decided ("set by the hypo guard").
- `buildSteps(c,p)` computes derived values (thr via `thrOf`, naive, guard minima, capVal,
  ratio, impliedF, impliedSmbMin), fills `VALS` (live values in glossary chips) and returns
  {rows,conc,thr}.
- Settings references: `SETT` maps the Trio app settings to each step — exact UI labels +
  paths from `SettingItems.swift` (tlray/Trio) and condensed in-app hint texts. Rendered
  per step via `schips([...])` as a ⚙ `.vrow.set` row; clicking uses the same `.vardef`
  box (`data-s` vs `data-v`) and appends an `.spath` line (path · app default · value
  provenance). `SVALS` (filled in buildSteps) holds the FEW values the daily data proves:
  UAM on (a pred.UAM curve any cycle today), DIA (NS profile), implied max(UAM)SMBBasal-
  Minutes from a capped SMB, smbjump tripped, closed loop (any enacted cycle today).
  Trio uploads NO preferences to Nightscout (profile.json = schedules/ISF/CR/DIA/targets
  only), so every other chip honestly says "not exported — check it in the app"; keep it
  that way. Settings that sit 1:1 behind an existing variable chip (threshold, maxIOB,
  maxBolus, smb_delivery_ratio, SMBInterval, maxSafeBasal, ISF, CR, …) carry their ⚙ path
  inside the VD text instead of a duplicate ⚙ chip. When Trio's settings tree changes,
  re-check labels/paths against `SettingItems.swift`.
- Settings-export import: the CSV from Trio's Settings → Trio Backup → Export Settings
  (`TrioSettings_yyyyMMdd_HHmmss.csv`) can be imported via the ⋯ menu → localStorage
  `trioInspector.trioSettings` (cleared on sign-out). CSV names AND values are LOCALIZED
  on the phone: `IMPMAP` is generated from Trio's `Localizable.xcstrings` (all languages,
  whitespace/case-normalized) — regenerate it when Trio's strings change. Imported values
  fill the ⚙ chips and the maxIOB/smb_delivery_ratio/SMBInterval variable chips with a ⇣
  provenance line carrying the export date (parsed from the FILE NAME — the in-file date
  row is locale-formatted); anything proven by the day's own data always wins (IMPUSED/
  VIMP). This import is the ONLY way to see oref preferences: they are not in NS, and
  Tidepool only receives maxBasal/maxBolus/threshold_setting/closedLoop/insulin model
  (verified in TidepoolManager.createStoredSettings).
- Cycle identity (`buildRaw`): key each loop cycle on `suggested.deliverAt`, NOT
  `enacted.deliverAt`. The enacted deliverAt only advances when a NEW temp/SMB is sent; on a
  "no change" cycle Trio re-reports the previous enact, so keying on it silently drops every
  unchanged cycle. Read the enacted block only when its deliverAt matches this cycle (fresh);
  otherwise read `suggested`.
- DUAL UPLOAD: Trio uploads each cycle TWICE (~1–4 s apart, same deliverAt): a
  Swift-formatted record (reason/threshold in profile units, `suggested.timestamp` SET,
  has TDD) and a raw oref record (reason always mg/dL, NO `suggested.timestamp`). buildRaw
  scores duplicates (formatted=2 + freshEnacted=1) and keeps the higher score; a losing twin
  can still set `rec` (enacted proof). Never prefer by created_at — order is not stable.
- Overrides arrive as `eventType:"Exercise"` treatments (name in `notes`, duration min,
  43200 = indefinite). Trio uploads the PLAN at start and the RUN at end/cancel (created_at
  ~1s later, ACTUAL duration, often named "Custom Override" — Trio's own delete-the-plan
  check misses because `copyRunningOverride` shifts the date 1s, so both stay in NS).
  `mergePlanRuns` (buildRaw) merges entries starting <120s apart with LATER-END-WINS —
  never max(): a cancelled indefinite override would keep its 43200-min plan forever —
  keeps the non-"Custom Override" name, and clamps each end to the next entry's start
  (only one override runs at a time). Temp targets get the same treatment (dual upload,
  run carries actual duration; a dur-0 NS cancel entry acts as a terminator via the clamp).
  There is NO target in the Exercise treatment; the drawn level comes from the cycle
  target at that time (`targetAt`). Trio DOES upload its override PRESETS in profile.json
  (`overridePresets`: name/duration/percentage/target, target in mg/dL) → `PROFILE.ovPresets`;
  `ovPreset/ovInfo` match by trimmed name. Shown in the bar label/tooltip and as an
  `.adjline` pill under the panel snapkv for adjustments active at the selected cycle —
  ALWAYS marked "≈ current preset" (presets can be edited later; "Custom Override" runs
  never match a preset). Temp targets keep their NS name (`name`/`reason` field → tt[3];
  old cached days have 3-element tt entries, so guard e[3]).
- Nightscout access: localStorage only — keys `trioInspector.auth` {url,token},
  `trioInspector.day.<epoch>` (max ~6 days, pruned), `trioInspector.profile`. KEEP these
  key names — the stable Pages/artifact origin means existing users stay signed in across
  releases. `fetchDay` = 4 API calls, 25s timeout.
- Loading: when a day is fetched with NOTHING cached (first load, uncached day),
  `renderSkeleton()` fills the chart (height = SVG_H), stats and panel with pulsing `.skel`
  placeholders in the final layout's sizes, so the page never starts as a tiny empty card
  and doesn't jump when data lands; the normal renderers replace them (renderDayChart
  removes `svg,.chartempty,.skel`). Global prefers-reduced-motion rule kills the pulse.
- Refresh: manual ↻ header button + `pollTick` every 30s (fetches only when viewing today,
  tab visible, cache >55s old ⇒ effectively ~1/min); also on visibilitychange. Nightscout
  has no practical push for third-party web clients (only a socket.io channel), so polling
  it is. Historical days refetch only if they were cached before the day ended.

## Conventions & pitfalls
- English UI, Trio/Nightscout terminology, U (not E), dots as decimal separator.
- `index.html` MUST start with `<meta charset="utf-8">` — the file is full of em dashes,
  arrows and emoji; served without a charset header (or via file://) everything mojibakes.
  Test servers must also send `text/html; charset=utf-8`.
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
- After each accepted change: test, commit+push, DEPLOY to main (standing approval from the
  user — "ook altijd deployen": fast-forward main to the working branch,
  `git push origin <branch>:main`, then verify the pages.yml run conclusion via the GitHub
  MCP actions tools; if the push is rejected, open a PR and merge it), republish the
  artifact, and send the user the fresh `index.html` as a file. The user prefers the deploy
  to be carried out by a subagent.
