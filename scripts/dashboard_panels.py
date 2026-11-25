"""Build profile cards from the same public calendar and repository snapshot."""
from collections import Counter
from datetime import date
from html import escape

ACCENTS = ['#edaa88','#88c8b4','#c2a1e2','#e8c67c','#86badd','#d99dab']
WHITE, MUTED = '#e6edf3', '#a9b4bf'
FEATURED = {'Sales-Forecasting-Dashboard-':'Sales Forecasting Dashboard','customer-retention-agent':'Customer Retention Agent','Customer-Churn-Prediction':'Customer Churn Prediction','Sales-Forecasting-Dashboard-mini':'Mini Sales Dashboard'}

def rect(x,y,w,h,fill='#121922',stroke='#303943',radius=15):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'

def label(x,y,value,size=23,color=WHITE,bold=False,mono=False):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{("monospace" if mono else "Arial,sans-serif")}" font-weight="{700 if bold else 400}" font-size="{size}">{escape(str(value))}</text>'

def svg(w,h,title,content):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img"><title>{escape(title)}</title>{content}</svg>'

def tiles(items,x,y,width,height):
    step=width/len(items)
    return ''.join(rect(x+i*step,y,step-12,height)+label(x+i*step+20,y+33,name,16,MUTED,True,True)+label(x+i*step+20,y+height-21,value,35,ACCENTS[i%6],True) for i,(name,value) in enumerate(items))

def panels(days,repos,releases):
    result={}
    years=sorted({day[:4] for day,_ in days},reverse=True)
    end=days[-1][0]
    body=''
    for i,year in enumerate(years):
        sample=[(day,n) for day,n in days if day.startswith(year)]
        monthly=Counter()
        for day,n in sample: monthly[day[:7]]+=n
        top=max(monthly,key=monthly.get)
        x=15+i*(1380/len(years)); width=1380/len(years)-16
        body+=rect(x,60,width,410)+label(x+26,124,year,48,ACCENTS[i%6],True)
        body+=label(x+26,177,'Contribution history',28,WHITE,True)+label(x+26,215,sample[0][0]+' — '+sample[-1][0],18,MUTED,False,True)
        body+=label(x+26,276,'Most active month',21,MUTED)+label(x+26,318,date.fromisoformat(top+'-01').strftime('%B') if monthly[top] else '—',32,ACCENTS[i%6],True)
        body+=tiles([('CONTRIBUTIONS',sum(monthly.values())),('ACTIVE DAYS',sum(n>0 for _,n in sample))],x+16,345,width-21,100)
        body+=f'<path d="M{x} 35h{width}" stroke="{ACCENTS[i%6]}"/><circle cx="{x+width/2}" cy="35" r="8" fill="{ACCENTS[i%6]}"/>'
    result['highlights']=svg(1400,496,'Yearly highlights in the available calendar',body)
    monthly=Counter()
    for day,n in days: monthly[day[:7]]+=n
    body=rect(2,2,1396,233)+label(32,48,'// PROFILE',18,ACCENTS[1],True,True)+label(32,106,'Pratyusha Swain',45,WHITE,True)+label(32,143,'@pratuyshswain',22,MUTED,False,True)+label(32,191,days[0][0]+' — '+end,20,MUTED)
    body+=tiles([('PUBLIC REPOS',len(repos)),('ACTIVE DAYS',sum(n>0 for _,n in days)),('STARS¹',sum(r['stars'] for r in repos if not r['fork']))],555,53,826,129)
    body+=rect(2,254,1396,329)+label(32,304,'Contributions by month',32,WHITE,True)
    step=1300/len(monthly)
    for i,(m,n) in enumerate(monthly.items()):
        x=50+i*step;h=140*n/max(1,max(monthly.values()))
        body+=rect(x,505-h,step*.53,max(1,h),ACCENTS[i%6],'none',3)+label(x,493-h,n,17)+label(x,539,m[2:],16,MUTED,False,True)
    body+=label(33,573,'¹ Stars on owned, non-fork repositories.',16,MUTED)
    counts=[n for _,n in days]
    run=longest=0
    for n in counts:
        run=run+1 if n else 0
        longest=max(longest,run)
    body+=label(32,651,'The numbers',33,WHITE,True)
    body+=tiles([('CONTRIBUTIONS',sum(counts)),('LONGEST STREAK',str(longest)+' days'),('PEAK DAY',max(counts)),('OWNED REPOS',sum(not r['fork'] for r in repos))],3,683,1405,119)
    body+=rect(2,827,1396,257)+label(32,877,'Featured repositories',32,WHITE,True)
    for i,(key,title) in enumerate(FEATURED.items()):
        r=next((r for r in repos if r['name']==key),None)
        if r:
            x=36+(i%2)*700;y=939+(i//2)*78
            body+=label(x,y,title,23)+label(x,y+29,str(r['stars'])+' stars  ·  pushed '+r['push'][:10],17,ACCENTS[i],False,True)
    result['stats']=svg(1400,1090,'GitHub statistics and monthly contributions',body)
    week=days[-7:];prev=days[-14:-7];count=sum(n for _,n in week)
    body=tiles([('CONTRIBUTIONS',count),('PREVIOUS 7 DAYS',sum(n for _,n in prev)),('ACTIVE DAYS',str(sum(n>0 for _,n in week))+'/7'),('PEAK DAY',max(n for _,n in week))],2,3,1407,116)
    body+=rect(2,140,685,458)+rect(706,140,692,458)+label(30,190,'Last seven days',32,WHITE,True)+label(737,190,'Recent repository pushes',32,WHITE,True)+label(32,233,week[0][0]+' — '+end,19,MUTED)
    for i,(day,n) in enumerate(week):
        x=42+i*90;h=190*n/max(1,max(v for _,v in week))
        body+=rect(x,501-h,48,max(1,h),ACCENTS[i%6],'none',3)+label(x,490-h,n,20)+label(x,546,date.fromisoformat(day).strftime('%a'),20,MUTED)
    for i,r in enumerate(sorted(repos,key=lambda r:r['push'],reverse=True)[:5]):
        y=252+i*66;body+=label(740,y,r['name'],23)+label(740,y+23,r['push'][:16].replace('T','  ')+' UTC',16,MUTED,False,True)
    result['activity']=svg(1400,604,'Seven-day activity and latest public pushes',body)
    body=rect(2,2,1396,123)+label(32,48,'// FEATURED REPOSITORIES',17,ACCENTS[2],True,True)+label(32,94,'Release desk',39,WHITE,True)+label(760,86,'Latest published release per project · '+end,19,MUTED)
    for i,(repo,title) in enumerate(FEATURED.items()):
        x=2+(i%2)*705;y=145+(i//2)*146
        release=releases.get(repo)
        body+=rect(x,y,688,130)+label(x+26,y+44,title,28,WHITE,True)+label(x+26,y+89,(release['tag_name'][:32]+'  ·  '+release['published_at'][:10]) if release else 'No published GitHub release',21,ACCENTS[i])
    result['releases']=svg(1400,435,'Latest releases for the four featured projects',body)
    body=''
    for i,year in enumerate(years):
        y=i*344;sample=[(date.fromisoformat(d),n) for d,n in days if d.startswith(year)]
        body+=rect(2,y+2,1396,327)+label(28,y+49,year+'   /   '+str(sum(n for _,n in sample))+' contributions',30,WHITE,True)
        start=date(int(year),1,1);offset=(start.weekday()+1)%7
        for month in range(1,13):
            d=date(int(year),month,1)
            w=((d-start).days+offset)//7
            body+=label(57+w*24,y+74,d.strftime('%b'),15,MUTED,False,True)
        for d,n in sample:
            w,r=divmod((d-start).days+offset,7)
            color=['#202a32','#375643','#52875e','#7fa979','#afd297'][min(4,n.bit_length())]
            body+=rect(57+w*24,y+87+r*20,17,15,color,'none',3)
        best=max(sample,key=lambda v:v[1])
        body+=label(55,y+282,'Peak day  /  '+best[0].isoformat()+'  ·  '+str(best[1])+' contributions',21,ACCENTS[i%6],False,True)
    result['year-story']=svg(1400,len(years)*344,'Daily contribution calendars by year',body)
    return result
