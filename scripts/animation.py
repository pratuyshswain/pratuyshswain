"""Render palette GIFs for profile readers that do not animate SVG CSS."""
import math
from datetime import date
from pathlib import Path
from xml.etree import ElementTree

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "assets" / "dashboard"
COLORS = ("#0d1117", "#182027", "#365943", "#497957", "#68a16a", "#8cc48a",
          "#ad5757", "#d69376", "#f3c99c", "#e4eadf", "#30363d", "#aab5c0")
PALETTE = [int(color[i:i+2], 16) for color in COLORS for i in (1, 3, 5)]

def panel(size):
    im = Image.new("P", size)
    im.putpalette(PALETTE + [0] * (768-len(PALETTE)))
    return im

def write_loop(name, frames, duration):
    frames[0].save(OUT / name, save_all=True, append_images=frames[1:],
                   duration=duration, loop=0, disposal=1, optimize=True)

def header():
    nodes = ElementTree.parse(OUT / "name.svg").getroot()
    cells = [(float(r.get("x")), float(r.get("y")), COLORS.index(r.get("fill")))
             for r in nodes.iter("{http://www.w3.org/2000/svg}rect")
             if r.get("width") == "12"]
    assert len(cells) > 300
    base = panel((960, 262))
    draw = ImageDraw.Draw(base)
    for x in range(6,955,15):
        for y in range(6,256,15):
            draw.rounded_rectangle((x,y,x+9,y+9),2,fill=1)
    frames = []
    for frame in range(88):
        im = base.copy()
        draw = ImageDraw.Draw(im)
        scan = -140 + frame*14.5
        for x,y,color in cells:
            distance = scan-x-.3*(y-110)
            if color == 1:
                continue
            # A travelling band lifts the letters and lights their leading edge.
            lift = round(18*math.exp(-(distance/62)**2))
            shade = 8 if abs(distance)<18 else 5 if abs(distance)<58 else color
            draw.rounded_rectangle((x,y-lift,x+11,y+11-lift),2,fill=shade)
        for segment in reversed(range(10)):
            x = scan-segment*12
            y = 225 + round(11*math.sin(x/49))
            draw.rounded_rectangle((x,y,x+11,y+11),3,fill=8 if segment==0 else 7 if segment<4 else 6)
            if segment==0:
                draw.point((x+8,y+3),fill=0)
        frames.append(im)
    write_loop("name.gif",frames,70)

def skyline(days):
    base = panel((960,266))
    font = ImageFont.truetype("DejaVuSansMono.ttf",16)
    draw = ImageDraw.Draw(base)
    draw.text((28,21),"CONTRIBUTION SKYLINE  /  "+days[-1][0],font=font,fill=11)
    draw.text((28,226),"One tile per day  /  Height represents contributions",font=font,fill=11)
    start = date.fromisoformat(days[0][0])
    tiles = []
    for day,count in days:
        offset=(date.fromisoformat(day)-start).days+(start.weekday()+1)%7
        week,row=divmod(offset,7)
        tiles.append((week,row,count))
    frames=[]
    for i in range(64):
        phase=2*math.pi*i/64
        # Orbit slightly about the centre while a highlight travels across the calendar.
        skew=5.5+3.5*math.sin(phase)
        slope=-.9+1.6*math.cos(phase)
        im=base.copy()
        draw=ImageDraw.Draw(im)
        for week,row,count in tiles:
            x=72+week*15-row*skew
            y=149+row*6+(week-26)*slope
            h=min(88,round(12*math.log2(count+1)))
            shade=min(5,1+count.bit_length())
            if abs(week-(-5+64*i/63))<1.8:
                shade=min(8,shade+2)
            top=[(x,y-h),(x+13,y+slope-h),(x+13-skew,y+slope+5-h),(x-skew,y+5-h)]
            if h:
                draw.polygon([top[3],top[2],(top[2][0],top[2][1]+h),(top[3][0],top[3][1]+h)],fill=3)
                draw.polygon([top[1],top[2],(top[2][0],top[2][1]+h),(top[1][0],top[1][1]+h)],fill=2)
            draw.polygon(top,fill=shade)
        frames.append(im)
    write_loop("skyline.gif",frames,100)
