#!/usr/bin/env python3
"""Build a subscribable iCalendar feed from the School Compass page data.
usage: python3 tools/make_ics.py <artifact index.html> <output .ics>"""
import sys, re, json, hashlib, datetime as dt

def esc(s):
    return str(s or '').replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')

def fold(line):
    b = line.encode('utf-8'); out = []; cur = b''
    for ch in line:
        c = ch.encode('utf-8')
        if len(cur) + len(c) > (75 if not out else 74):
            out.append(cur); cur = b''
        cur += c
    out.append(cur)
    return '\r\n '.join(x.decode('utf-8') for x in out)

def T(x, k='ar'):
    if x is None: return ''
    if isinstance(x, str): return x
    return x.get(k) or x.get('ar') or x.get('en') or ''

def main(src, dst):
    h = open(src, encoding='utf-8').read()
    m = re.search(r'<script id="data" type="application/json">(.*?)</script>', h, re.S)
    D = json.loads(m.group(1))
    today = dt.date.today()
    evs = list(D.get('events', [])) + list((D.get('doctors') or {}).get('upcoming', []) or [])
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    L = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//School Compass//AR', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
         'X-WR-CALNAME:بوصلة المدرسة — ساندرا وناتالي', 'X-WR-TIMEZONE:America/Chicago',
         'REFRESH-INTERVAL;VALUE=DURATION:PT1H', 'X-PUBLISHED-TTL:PT1H',
         'BEGIN:VTIMEZONE', 'TZID:America/Chicago',
         'BEGIN:DAYLIGHT', 'TZOFFSETFROM:-0600', 'TZOFFSETTO:-0500', 'TZNAME:CDT', 'DTSTART:19700308T020000', 'RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU', 'END:DAYLIGHT',
         'BEGIN:STANDARD', 'TZOFFSETFROM:-0500', 'TZOFFSETTO:-0600', 'TZNAME:CST', 'DTSTART:19701101T020000', 'RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU', 'END:STANDARD',
         'END:VTIMEZONE']
    seen = set()
    for e in evs:
        try: d = dt.date.fromisoformat(e['d'])
        except Exception: continue
        if d < today - dt.timedelta(days=30): continue
        k = e.get('k', 'all')
        who = {'s': 'ساندرا: ', 'n': 'ناتالي: ', 'off': '🚫 '}.get(k, '')
        title = who + T(e.get('t'))
        uid = hashlib.sha1((e['d'] + '|' + T(e.get('t'), 'en') + '|' + k).encode()).hexdigest()[:20] + '@school-compass'
        if uid in seen: continue
        seen.add(uid)
        desc = '\n'.join(x for x in [T(e.get('m')), T(e.get('m'), 'en') if T(e.get('m'), 'en') != T(e.get('m')) else '', T(e.get('t'), 'en')] if x)
        L += ['BEGIN:VEVENT', 'UID:' + uid, 'DTSTAMP:' + stamp, 'SUMMARY:' + esc(title)]
        if desc: L.append('DESCRIPTION:' + esc(desc))
        tm = re.match(r'\s*(\d{1,2}):(\d{2})(?:\s*[–-]\s*(\d{1,2}):(\d{2}))?', e.get('time') or '')
        if tm:
            st = dt.datetime(d.year, d.month, d.day, int(tm[1]), int(tm[2]))
            en = dt.datetime(d.year, d.month, d.day, int(tm[3]), int(tm[4])) if tm[3] else st + dt.timedelta(hours=1)
            if en <= st: en = st + dt.timedelta(hours=1)
            L += ['DTSTART;TZID=America/Chicago:' + st.strftime('%Y%m%dT%H%M%S'), 'DTEND;TZID=America/Chicago:' + en.strftime('%Y%m%dT%H%M%S')]
            prev8 = dt.datetime(d.year, d.month, d.day) - dt.timedelta(hours=4)
            mins = int((st - prev8).total_seconds() // 60)
            L += ['BEGIN:VALARM', 'ACTION:DISPLAY', 'DESCRIPTION:' + esc('بكرة: ' + title), 'TRIGGER:-PT%dM' % mins, 'END:VALARM']
            L += ['BEGIN:VALARM', 'ACTION:DISPLAY', 'DESCRIPTION:' + esc(title), 'TRIGGER:-PT60M', 'END:VALARM']
        else:
            L += ['DTSTART;VALUE=DATE:' + d.strftime('%Y%m%d'), 'DTEND;VALUE=DATE:' + (d + dt.timedelta(days=1)).strftime('%Y%m%d'), 'TRANSP:TRANSPARENT']
            L += ['BEGIN:VALARM', 'ACTION:DISPLAY', 'DESCRIPTION:' + esc('بكرة: ' + title), 'TRIGGER:-PT4H', 'END:VALARM']
        L.append('END:VEVENT')
    L.append('END:VCALENDAR')
    open(dst, 'w', encoding='utf-8', newline='').write('\r\n'.join(fold(x) for x in L) + '\r\n')
    print('events:', len(seen))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
