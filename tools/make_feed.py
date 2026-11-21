#!/usr/bin/env python3
"""Write netlify/data/feed.json: the small, server-only data the push functions need.
Not published (lives outside site/). usage: python3 tools/make_feed.py <artifact index.html> <password> <repo root>"""
import sys, re, json, hashlib, datetime as dt, os

src, pw, root = sys.argv[1], sys.argv[2], sys.argv[3]
raw = open(src, encoding='utf-8').read()
D = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', raw, re.S).group(1))

def T(x):
    if x is None: return ''
    if isinstance(x, str): return x
    return x.get('ar') or x.get('en') or ''
WHO = {'s': 'ساندرا', 'n': 'ناتالي'}
def who(k): return (' — ' + WHO[k]) if k in WHO else ''
def hid(*p): return hashlib.sha1('|'.join(map(str, p)).encode()).hexdigest()[:16]

today = dt.date.today()
lunch = {d['date']: T(d.get('food')) for m in (D.get('lunch', {}).get('months') or []) for d in (m.get('days') or []) if d.get('date')}

days = {}
evs = list(D.get('events', [])) + [dict(e, t={'ar': 'موعد طبي', 'en': 'Medical appointment'}) for e in (D.get('doctors', {}).get('upcoming') or [])]
for i in range(-1, 45):
    d = (today + dt.timedelta(days=i)).isoformat()
    lst = sorted([e for e in evs if e.get('d') == d], key=lambda e: e.get('time') or '')
    days[d] = {
        'events': [{'t': T(e.get('t')) + who(e.get('k')), 'time': (e.get('time') or '').split(' ')[0], 'off': e.get('k') == 'off'} for e in lst],
        'lunch': lunch.get(d, ''),
    }

def kidu(k, tab, other):
    return f'{k}/{tab}' if k in ('s', 'n') else other

items = []  # things worth a "new" notification (sent once each)
cut = (today - dt.timedelta(days=10)).isoformat()
for a in D.get('alerts', []):
    if a.get('d', '') >= cut:
        items.append({'id': hid('a', a.get('d'), T(a.get('t'))), 'title': '🔔 ' + T(a.get('t')), 'body': T(a.get('m'))[:180], 'x': T(a.get('m'))[:900], 'u': 'inbox'})
for f in D.get('followups', []) or []:
    if not f.get('due') or f['due'] >= today.isoformat():
        items.append({'id': hid('f', f.get('due'), T(f.get('t'))), 'title': '📌 مطلوب منكم' + who(f.get('k')), 'body': T(f.get('t'))[:180], 'x': (T(f.get('t')) + ('\n' + T(f.get('m')) if f.get('m') else '') + ('\n⏰ ' + f['due'] if f.get('due') else ''))[:900], 'u': kidu(f.get('k'), 'sum', 'inbox')})
for h in (D.get('library') or {}).get('holds', []) or []:
    if not h.get('by') or h['by'] >= today.isoformat():
        items.append({'id': hid('l', h.get('t'), h.get('by')), 'title': '📚 كتاب جاهز في المكتبة', 'body': f"{h.get('t','')} — استلموه قبل {h.get('by','')}", 'u': 'library'})
for e in evs:
    d = e.get('d', '')
    if today.isoformat() <= d <= (today + dt.timedelta(days=14)).isoformat():
        tm = (e.get('time') or '').split(' ')[0]
        items.append({'id': hid('e', d, T(e.get('t')), e.get('time')), 'title': '📅 ' + T(e.get('t')) + who(e.get('k')), 'body': d + (' · ' + tm if tm else ''), 'x': (d + (' · ' + tm if tm else '') + ('\n' + T(e.get('m')) if e.get('m') else ''))[:900], 'u': kidu(e.get('k'), 'sum', 'week')})
for k in ('s', 'n'):
    for m in ((D.get('teacherLog') or {}).get(k) or [])[:3]:
        if m.get('d', '') >= cut:
            items.append({'id': hid('m', k, m.get('d'), T(m.get('t'))), 'title': '✉️ ' + (m.get('from') or 'المدرسة') + who(k), 'body': T(m.get('t'))[:180], 'x': (T(m.get('t')) + ('\n' + T(m.get('m')) if m.get('m') else ''))[:900], 'u': k + '/class'})
    nl = ((D.get('newsletters') or {}).get(k) or [])
    if nl and nl[0].get('d', '') >= cut:
        n = nl[0]
        items.append({'id': hid('n', k, n.get('d')), 'title': '📰 النشرة الأسبوعية' + who(k), 'body': ' · '.join(T(x) for x in n.get('items', [])[:3])[:180], 'x': '\n'.join('• ' + T(x) for x in n.get('items', []))[:900], 'u': k + '/class'})

# study: scored test papers and a new spelling list
for x in ((D.get('study') or {}).get('tests') or []):
    if x.get('score') and x.get('d', '') >= cut and x.get('src') != 'paper':
        sc = str(x.get('score')) + ('/' + str(x.get('max')) if x.get('max') else '')
        miss = ', '.join(T(m) for m in (x.get('missed') or [])[:8])
        items.append({'id': hid('ts', x.get('d'), x.get('subj'), sc), 'title': '📝 نتيجة اختبار' + who('s'), 'body': (T(x.get('t')) + ' · ' + sc)[:180],
                      'x': (T(x.get('t')) + ' · ' + sc + ('\nالأخطاء: ' + miss if miss else ''))[:900], 'u': 's/study'})
spl = D.get('spelling') or {}
if spl.get('words'):
    items.append({'id': hid('sw', T(spl.get('week')), len(spl['words'])), 'title': '✏️ كلمات Spelling الأسبوع وصلت' + who('s'),
                  'body': ', '.join(spl['words'][:8])[:180], 'x': ', '.join(spl['words'])[:900], 'u': 's/study'})

# practice tests: announce on the day they open (and the day after)
import datetime as _dt
_td = _dt.date.fromisoformat(today) if isinstance(today, str) else today
for qz in ((D.get('study') or {}).get('quizzes') or []):
    try:
        qd = _dt.date.fromisoformat(qz.get('d', ''))
    except Exception:
        continue
    if 0 <= (_td - qd).days <= 1:
        items.append({'id': hid('qz', qz.get('id')), 'title': '📝 امتحان تدريب جاهز' + who('s'),
                      'body': (T(qz.get('title')) + ' · ' + str(len(qz.get('q') or [])) + ' سؤال')[:180], 'u': 's/study'})

# timed basketball events (practices + games) for the "1 hour before" reminder
bb = []
for e in D.get('events', []):
    d = e.get('d', '')
    if not (today.isoformat() <= d <= (today + dt.timedelta(days=45)).isoformat()): continue
    en = (e.get('t') or {}).get('en', '') if isinstance(e.get('t'), dict) else str(e.get('t'))
    if not (e.get('src') == 'bb' or re.search(r'basketball|ymca', en, re.I)): continue
    tm = re.match(r'(\d{1,2}):(\d{2})', e.get('time') or '')
    if not tm: continue
    m = T(e.get('m'))
    bb.append({'id': hid('bb', d, e.get('time'), en), 'd': d, 'time': f"{int(tm.group(1)):02d}:{tm.group(2)}",
               'title': '🏀 ' + T(e.get('t')) + who(e.get('k')), 'body': m[:160], 'u': 's/bb'})

bal = None
try:
    b = float(str((D.get('lunchAccount') or {}).get('balance', '')).replace('$', ''))
    if b < 0: bal = b
except ValueError:
    pass

token = hashlib.sha256(('sc-push:' + pw).encode()).hexdigest()
feed = {'generated': dt.datetime.now(dt.timezone.utc).isoformat(), 'tokenHash': hashlib.sha256(token.encode()).hexdigest(),
        'days': days, 'items': items, 'bb': bb, 'lunchBalance': bal}
os.makedirs(os.path.join(root, 'netlify', 'data'), exist_ok=True)
json.dump(feed, open(os.path.join(root, 'netlify', 'data', 'feed.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('feed', len(items), 'items,', len(days), 'days')
