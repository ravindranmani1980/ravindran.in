#!/usr/bin/env python3
"""build-sitemap.py - rebuilds sitemap.xml for ravindran.in.

Run from the ravindran.in-main folder:   python3 _tools/build-sitemap.py
Lists every page except folders starting with "_" or ".",
dist/, and pages marked noindex or that only redirect. lastmod is the file's modification date.
"""
import datetime, os, re
from xml.sax.saxutils import escape

SITE = 'https://ravindran.in'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAV_ORDER = ['index.html', 'about.html', 'expertise.html', 'technology.html', 'ai-automation.html',
             'aws-examples.html', 'experience.html', 'education.html', 'contact.html']


def skip(path):
    text = open(path, encoding='utf-8', errors='ignore').read()
    return re.search(r'<meta\s+name="robots"\s+content="[^"]*noindex', text, re.I) or \
           re.search(r'http-equiv="refresh"', text, re.I)

entries = []
for d, dirs, files in os.walk(ROOT):
    rel_d = os.path.relpath(d, ROOT).replace(os.sep, '/')
    dirs[:] = sorted(x for x in dirs if not x.startswith(('_', '.')) and x != 'dist')
    for f in files:
        if not f.endswith('.html') or f == '404.html':
            continue
        path = os.path.join(d, f)
        rel = os.path.relpath(path, ROOT).replace(os.sep, '/')
        if skip(path):
            continue
        url = SITE + '/' + (rel[:-len('index.html')] if rel.endswith('index.html') else rel)
        lastmod = datetime.date.fromtimestamp(os.path.getmtime(path)).isoformat()
        if rel == 'index.html':
            pri, key = '1.0', (0, 0)
        else:
            pri, key = '0.8', (1, NAV_ORDER.index(rel) if rel in NAV_ORDER else 99)
        entries.append((key, rel, url, lastmod, pri))

entries.sort()
lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for _, _, url, lastmod, pri in entries:
    lines.append(f'  <url>\n    <loc>{escape(url)}</loc>\n    <lastmod>{lastmod}</lastmod>\n    <priority>{pri}</priority>\n  </url>')
lines.append('</urlset>')
with open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8', newline='\n') as fh:
    fh.write('\n'.join(lines) + '\n')
print(f'sitemap.xml: {len(entries)} URLs')
