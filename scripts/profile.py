"""Render the profile's contribution and repository panels using GitHub's public data."""
from datetime import date
from html import escape
from math import log2
from pathlib import Path
import json
import os
import urllib.request

OUT = Path(__file__).resolve().parents[1] / 'assets' / 'dashboard'
USER = 'pratuyshswain'
COLORS = ['#202a30', '#314f43', '#427554', '#67a66e', '#96cd89']
STYLE = '<style>text{font-family:Arial,sans-serif}.mono{font-family:monospace}</style>'

def text(x, y, value, size=20, color='#e8edf2', mono=False):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" class="{("mono" if mono else "")}">{escape(str(value))}</text>'

def save(name, height, title, body):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / (name+'.svg')).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 {height}" role="img"><title>{escape(title)}</title>{STYLE}<rect x="1" y="1" width="958" height="{height-2}" rx="18" fill="#0d1117" stroke="#30363d"/>{body}</svg>')

def fetch(url, query=None):
    data = None if query is None else json.dumps({'query':query}).encode()
    request = urllib.request.Request(url, data=data, headers={'Authorization':'Bearer '+os.environ['GITHUB_TOKEN'], 'User-Agent':'profile-dashboard'})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)

def github_data():
    query = '{user(login:"pratuyshswain"){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}'
    calendar = fetch('https://api.github.com/graphql',query)['data']['user']['contributionsCollection']['contributionCalendar']
    days = [(d['date'],d['contributionCount']) for w in calendar['weeks'] for d in w['contributionDays']]
    repos = []
    page = 1
    while True:
        batch = fetch(f'https://api.github.com/users/{USER}/repos?per_page=100&page={page}&sort=pushed')
        repos.extend(dict(name=r['name'], stars=r['stargazers_count'], push=r['pushed_at'], fork=r['fork']) for r in batch)
        if len(batch)<100:
            break
        page += 1
    return days,repos

def render(days,repos):
    assert days and all(n>=0 for _,n in days)
    end = days[-1][0]
    body=text(30,39,'CONTRIBUTION SKYLINE   /   '+end,16,'#aab5c0',True)
    start=date.fromisoformat(days[0][0])
    for day,count in days:
        stamp=date.fromisoformat(day)
        offset=(stamp-start).days+(start.weekday()+1)%7
        week,row=divmod(offset,7)
        x=70+week*15-row*6
        y=165+row*6-week*.85
        h=min(88,round(12*log2(count+1)))
        color=COLORS[min(4,count.bit_length())]
        body+=f'<path d="M{x} {y-h}l12 -1  -5 5 -12 1z" fill="{color}"/>'
        if h:
            body+=f'<path d="M{x-5} {y+5-h}l12 -1v{h}l-12 1z" fill="#446448"/><path d="M{x+7} {y+4-h}l5 -5v{h}l-5 5z" fill="#304738"/>'
    body+=text(30,245,'One tile per day  ·  Column height increases with contribution count',16,'#aab5c0',True)
    save('skyline',266,'Isometric contribution calendar',body)

if __name__=='__main__':
    from animation import skyline
    from name_box import render as render_name_box
    days, repos = github_data()
    from dashboard_panels import FEATURED, panels
    releases = {}
    for name in FEATURED:
        page = 1
        while True:
            entries = fetch(f'https://api.github.com/repos/{USER}/{name}/releases?per_page=100&page={page}')
            published = next((entry for entry in entries if entry.get('published_at') and not entry['draft']), None)
            if published or len(entries) < 100:
                releases[name] = published
                break
            page += 1
    for name, image in panels(days, repos, releases).items():
        (OUT / (name + '.svg')).write_text(image, encoding='utf-8')
    render(days, repos)
    skyline(days)
    (OUT / 'name-box.svg').write_text(render_name_box(days), encoding='utf-8')
