#!/usr/bin/env python3
"""Build the Trio Loop Inspector from template.html.

Outputs:
  index.html               shareable app: no data, no credentials; asks for a
                           Nightscout URL + token on first open (stored in the
                           browser's localStorage only).
  personal-snapshot.html   OPTIONAL personal build with ~3 days of your own
                           data baked in (works fully offline). Only produced
                           when NIGHTSCOUT_URL and NIGHTSCOUT_TOKEN are set.
                           Git-ignored: contains medical data. Never share it.

Usage:
  python3 build.py                          # index.html only
  NIGHTSCOUT_URL=https://... NIGHTSCOUT_TOKEN=... python3 build.py
"""
import json, os, sys, datetime, urllib.request, urllib.parse

TEMPLATE = open(os.path.join(os.path.dirname(__file__) or '.', 'template.html')).read()
EMPTY = ('{"generatedAt":"","tzOffsetHours":2,"profile":{"basal":[],"target":null,'
         '"isf":null,"cr":[],"dia":10},"sgv":[],"tempBasal":[],"smb":[],"bolus":[],'
         '"carbs":[],"notes":[],"siteChange":[],"cycles":[]}')

def build_share():
    out = (TEMPLATE.replace('/*__DATA__*/null', EMPTY)
                   .replace('const SHARE = /*__SHARE__*/false;', 'const SHARE = /*__SHARE__*/true;'))
    open('index.html', 'w').write(out)
    print(f'index.html written ({len(out)//1024} KB) — shareable, no data/credentials')

def api(base, token, path, query):
    q = f'{path}?{query}&token={urllib.parse.quote(token)}'
    with urllib.request.urlopen(f'{base}/api/v1/{q}') as r:
        return json.load(r)

def ts(s):
    return int(datetime.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp())

def build_snapshot(base, token, days=3):
    since = (datetime.datetime.now(datetime.timezone.utc)
             - datetime.timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%SZ')
    entries = api(base, token, 'entries.json', f'find[dateString][$gte]={since}&count=5000')
    treatments = api(base, token, 'treatments.json', f'find[created_at][$gte]={since}&count=8000')
    dev = api(base, token, 'devicestatus.json', f'find[created_at][$gte]={since}&count=8000')
    profile = api(base, token, 'profile.json', 'count=1')
    store = profile[0]['store'][profile[0].get('defaultProfile', 'default')]

    sgv = sorted([[ts(e['dateString']), e['sgv']] for e in entries
                  if e.get('type') == 'sgv' and e.get('sgv')])
    tb, smb, bolus, carbs, notes, site = [], [], [], [], [], []
    for t in treatments:
        ca = t.get('created_at')
        if not ca:
            continue
        x, et = ts(ca), t.get('eventType')
        if et == 'Temp Basal':
            r = t.get('rate', t.get('absolute'))
            if r is not None:
                tb.append([x, round(r, 2), round(t.get('duration', 0), 1)])
        elif et == 'SMB':
            if t.get('insulin'):
                smb.append([x, round(t['insulin'], 2)])
        elif et in ('Bolus', 'Correction Bolus', 'Meal Bolus'):
            if t.get('insulin'):
                bolus.append([x, round(t['insulin'], 2)])
            if t.get('carbs'):
                carbs.append([x, round(t['carbs'], 1)])
        elif et == 'Carb Correction' or t.get('carbs'):
            if t.get('carbs'):
                carbs.append([x, round(t['carbs'], 1)])
        elif et == 'Note':
            notes.append([x, t.get('notes', '')])
        elif et == 'Site Change':
            site.append(x)
    for l in (tb, smb, bolus, carbs, notes):
        l.sort()

    cycles = {}
    for r in dev:
        oa = r.get('openaps') or {}
        en = oa.get('enacted') or oa.get('suggested') or {}
        da = en.get('deliverAt') or en.get('timestamp')
        if not en or en.get('bg') is None or not da:
            continue
        x = ts(da)
        if x in cycles:
            continue
        preds = en.get('predBGs') or {}
        cycles[x] = {
            't': x, 'bg': en.get('bg'), 'iob': round(en.get('IOB', 0), 2),
            'cob': en.get('COB', 0), 'ebg': en.get('eventualBG'),
            'req': en.get('insulinReq'), 'rate': en.get('rate'), 'dur': en.get('duration'),
            'tgt': en.get('current_target'), 'sens': en.get('sensitivityRatio'),
            'tdd': en.get('TDD'), 'units': en.get('units'),
            'reason': (en.get('reason') or '').replace('&lt;', '<').replace('&gt;', '>'),
            'rec': 1 if (oa.get('enacted') and oa['enacted'].get('received')) else 0,
            'pred': {k: [int(v) for v in preds[k]]
                     for k in ('IOB', 'ZT', 'COB', 'UAM') if k in preds},
        }
    data = json.dumps({
        'generatedAt': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'tzOffsetHours': 2,
        'profile': {
            'basal': [[b['timeAsSeconds'], b['value']] for b in store['basal']],
            'target': store['target_low'][0]['value'],
            'isf': store['sens'][0]['value'],
            'cr': [[c['timeAsSeconds'], c['value']] for c in store['carbratio']],
            'dia': store['dia'],
        },
        'sgv': sgv, 'tempBasal': tb, 'smb': smb, 'bolus': bolus, 'carbs': carbs,
        'notes': notes, 'siteChange': site,
        'cycles': sorted(cycles.values(), key=lambda c: c['t']),
    }, separators=(',', ':'))
    assert '</script' not in data.lower()
    out = TEMPLATE.replace('/*__DATA__*/null', data)
    open('personal-snapshot.html', 'w').write(out)
    print(f'personal-snapshot.html written ({len(out)//1024} KB) — PERSONAL, do not share')

if __name__ == '__main__':
    build_share()
    base, token = os.environ.get('NIGHTSCOUT_URL', '').rstrip('/'), os.environ.get('NIGHTSCOUT_TOKEN', '')
    if base and token:
        build_snapshot(base, token)
    else:
        print('NIGHTSCOUT_URL/NIGHTSCOUT_TOKEN not set — skipped personal snapshot')
