"""Render the profile's contribution and repository panels using GitHub's public data."""
from collections import Counter
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
    active = [(d,n) for d,n in days if n]
    months = Counter()
    for day,count in days:
        months[day[:7]] += count
    body = text(30,38,'CONTRIBUTIONS BY MONTH   /   '+end,15,'#98a5b2',True)
    recent = list(months.items())[-12:]
    for i,(month,n) in enumerate(recent):
        x=34+i*76
        h=round(94*n/max(1,max(v for _,v in recent)))
        body += f'<rect x="{x}" y="{165-h}" width="40" height="{max(1,h)}" fill="#a74848"/>'
        body += text(x,156-h,n,14)+text(x,190,month[5:],15,'#adb7c1',True)
    save('highlights',210,'Monthly contributions during the displayed period',body)
    stats=[('Contributions',sum(n for _,n in days)),('Active days',len(active)),('Public repos',len(repos)),('Stars received',sum(r['stars'] for r in repos if not r['fork']))]
    body=text(32,36,days[0][0]+'  —  '+end,16,'#a1acb7',True)
    for i,(label,value) in enumerate(stats):
        x=32+i*234
        body+=text(x,102,value,48)+text(x,135,label,19,'#aeb9c3')
    save('stats',164,'Contribution and public repository statistics',body)
    body=text(30,39,'LATEST PUBLIC REPOSITORY PUSHES   /   UTC',17,'#98a5b2',True)
    for i,r in enumerate(sorted(repos,key=lambda r:r['push'],reverse=True)[:5]):
        y=81+i*39
        body+=text(32,y,r['name'],23)+text(690,y,r['push'][:16].replace('T','  '),18,'#a1b599',True)
    save('activity',260,'Most recently pushed public repositories',body)
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
    render(*github_data())
