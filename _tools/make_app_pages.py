#!/usr/bin/env python3
"""make_app_pages.py - create or refresh the app pages (apps/<slug>/index.html).

Run from the ravindran.in-main folder:   python3 _tools/make_app_pages.py [slug ...]

It reads _tools/apps.txt, finds each app's card on ai-automation.html (the card whose
"Source on GitHub" link points at the app's repo), and writes a page with the card's
facts and the live app in a frame. The app itself (apps/<slug>/app/) is built from
GitHub by _tools/build-apps.sh during every Cloudflare build.
"""
import html, os, re, sys

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNER = 'ravindranmani1980'
CSS_VERSION = '20261024'

# One-line description shown under the app name on its page.
TAGLINE = {
    'cloudparity':          'Multi-cloud cost and performance analytics',
    'invoice-consolidator': 'Multi-subscription Azure invoice analyzer',
    'cloudcostiq':          'Cost savings analyzer and FinOps benchmarks',
    'cloudbounty':          'FinOps bounty dashboard and zombie-resource game',
    'azureshield':          'Azure Storage and RBAC security auditor',
    'aws-sentinel':         'AWS S3 and IAM security auditor',
    'cybershield':          'Cyber defense training suite',
    'threatguard':          'Cyber defense game for teens and young adults',
}
# Optional extra link on an app page: slug -> (url, label)
EXTRA_LINK = {
    'cybershield': ('https://ais-pre-elolfngen6z6f37daibx6g-647805725217.us-east1.run.app/', 'Full version'),
}
NOTE = {}   # optional: slug -> short note shown under the links

def read_apps():
    apps = []
    for line in open(os.path.join(SITE, '_tools', 'apps.txt'), encoding='utf-8'):
        line = line.strip()
        if line and not line.startswith('#'):
            slug, repo = line.split()[:2]
            apps.append((slug, repo))
    return apps

src = open(os.path.join(SITE, 'ai-automation.html'), encoding='utf-8').read()

def card_for(repo):
    for m in re.finditer(r'<article class="card"[^>]*>.*?</article>', src, re.S):
        card = m.group(0)
        if f'github.com/{OWNER}/{repo}"' in card:
            kicker = re.search(r'<span class="idx mono">([^<]*)</span>', card).group(1)
            title = re.sub(r'<[^>]+>', '', re.search(r'<h3>(.*?)</h3>', card, re.S).group(1)).strip()
            facts = re.search(r'(<dl class="proj-facts">.*?</dl>)', card, re.S).group(1)
            return kicker, html.unescape(title), facts
    return None

head_tpl = src.split('<title>')[0]
fonts = re.search(r'(<link rel="preconnect".*?</noscript>)', src, re.S).group(1)
header = re.search(r'(<header class="site">.*?</header>)', src, re.S).group(1)
header = re.sub(r'href="(?!https?:|#|mailto:)([^"]+)"', r'href="../../\1"', header)
FOOTER = '''<footer>
  &copy; <span id="year">2026</span> Ravindran Mani. All rights reserved.
</footer>
<script>
document.getElementById('year').textContent=new Date().getFullYear();
const btn=document.getElementById('navBtn'),links=document.getElementById('navlinks');
btn.addEventListener('click',()=>{const open=links.classList.toggle('open');btn.setAttribute('aria-expanded',String(open))});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&links.classList.contains('open')){links.classList.remove('open');btn.setAttribute('aria-expanded','false');btn.focus()}});
</script>
</body></html>
'''
ARROW = '<span aria-hidden="true">&#8599;</span>'

def page(slug, repo, kicker, title, facts, tagline):
    extra = ''
    if slug in EXTRA_LINK:
        u, label = EXTRA_LINK[slug]
        extra = f'<a class="card-link" href="{u}" target="_blank" rel="noopener">{label} {ARROW}</a>'
    note = f'\n    <p class="app-note">{NOTE[slug]}</p>' if slug in NOTE else ''
    url = f'https://ravindran.in/apps/{slug}/'
    desc = html.escape(f'{title}: {tagline}. A live demo built by Ravindran Mani, running in the browser with sample data.')
    t = html.escape(f'{title} | Ravindran Mani')
    ht = html.escape(title)
    return f'''{head_tpl}<title>{t}</title>
<link rel="icon" href="../../favicon.ico" type="image/x-icon">

<meta name="description" content="{desc}">
<meta name="author" content="Ravindran Mani">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{url}">

<meta property="og:type" content="website">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="Ravindran Mani">
<meta property="og:image" content="https://ravindran.in/images/og-card.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="https://ravindran.in/images/og-card.png">
{fonts}
<link rel="stylesheet" href="../../css/style.css?v={CSS_VERSION}">
</head><body><a class="skip-link" href="#main">Skip to content</a>
{header}
<main id="main">
<section class="alt app-intro">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="../../ai-automation.html">AI &amp; Projects</a> <span aria-hidden="true">/</span> {ht}</nav>
    <div class="section-head">
      <div class="kicker mono">{kicker}</div>
      <h1>{ht}</h1>
      <p>{html.escape(tagline)}. Try it below: it runs in your browser with built-in sample data.</p>
    </div>
    {facts}
    <div class="card-links"><a class="card-link" href="app/" target="_blank" rel="noopener">Open full screen {ARROW}</a>{extra}<a class="card-link" href="https://github.com/{OWNER}/{repo}" target="_blank" rel="noopener">Source on GitHub {ARROW}</a><a class="card-link" href="../../ai-automation.html"><span aria-hidden="true">&larr;</span> All projects</a></div>{note}
  </div>
</section>
<section class="app-stage" aria-label="{ht} live demo">
  <div class="app-frame"><iframe src="app/" title="{ht} live demo" loading="lazy" allow="clipboard-write; fullscreen" allowfullscreen></iframe></div>
  <p class="app-hint">On a phone? <a href="app/" target="_blank" rel="noopener">Open it full screen</a> for the best view.</p>
</section>
</main>
{FOOTER}'''

only = set(sys.argv[1:])
for slug, repo in read_apps():
    if only and slug not in only:
        continue
    found = card_for(repo)
    if not found:
        print(f'skip {slug}: no card on ai-automation.html links to github.com/{OWNER}/{repo}')
        continue
    kicker, title, facts = found
    d = os.path.join(SITE, 'apps', slug)
    os.makedirs(d, exist_ok=True)
    target = os.path.join(d, 'index.html')
    new = page(slug, repo, kicker, title, facts, TAGLINE.get(slug, title))
    old = open(target, encoding='utf-8').read() if os.path.exists(target) else None
    if new == old:
        print('unchanged apps/%s/index.html' % slug)
        continue
    with open(target, 'w', encoding='utf-8') as f:
        f.write(new)
    print('wrote apps/%s/index.html  (%s)' % (slug, title))
