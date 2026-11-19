#!/usr/bin/env python3
"""THE WHOLE DAY - Broadsheet Edition. Deterministic PIL renderer, from scratch."""
import random, os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 241, 222)
INK = (26, 23, 16)
MUTED = (92, 84, 66)
RULE = (40, 36, 28)
FD = "/usr/share/fonts/truetype/noto"
SERIF_BLACK = f"{FD}/NotoSerif-Black.ttf"
SERIF_BOLD = f"{FD}/NotoSerif-Bold.ttf"
SERIF_REG = f"{FD}/NotoSerif-Regular.ttf"
SANS_BOLD = f"{FD}/NotoSans-Bold.ttf"
SANS_REG = f"{FD}/NotoSans-Regular.ttf"
SANS_SEMI = f"{FD}/NotoSans-SemiBold.ttf"

_cache = {}
def F(path, size):
    k = (path, size)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(path, size)
    return _cache[k]

def tw(d, s, f):
    return d.textlength(s, font=f)

def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(d, t, f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

def block(d, x, y, s, f, maxw, lh, color=INK, max_lines=None):
    lines = wrap(d, s, f, maxw)
    if max_lines: lines = lines[:max_lines]
    for ln in lines:
        d.text((x, y), ln, font=f, fill=color); y += lh
    return y

def fit_block(d, x, y, s, path, start, maxw, lh_ratio=1.12, max_lines=2, min_size=9, color=INK):
    size = start
    while size > min_size:
        f = F(path, size)
        if len(wrap(d, s, f, maxw)) <= max_lines: break
        size -= 1
    f = F(path, size)
    return block(d, x, y, s, f, maxw, int(size*lh_ratio), color, max_lines)

def one_line(d, s, f, maxw):
    if tw(d, s, f) <= maxw: return s
    while s and tw(d, s + "\u2026", f) > maxw: s = s[:-1]
    return s + "\u2026"

# ---------------- DATA ----------------
HEROES = [
 dict(kicker="APEC SUMMIT \u00b7 SHENZHEN", art="shenzhen",
      head="Trump, Xi and Putin Meet in Shenzhen",
      deck="APEC trilateral in China: Xi embraced Trump on the tarmac as leaders gather for the summit.",
      src="SHENZHEN \u00b7 NYT / BBC"),
 dict(kicker="STRAIT OF HORMUZ \u00b7 ESCALATION", art="hormuz",
      head="Iran Strikes US Sites as Carriers Converge on Hormuz",
      deck="Iran hit US sites in Kuwait and Bahrain; US struck Qeshm; a merchant ship was attacked; USS Theodore Roosevelt arrives.",
      src="HORMUZ \u00b7 WIRE REPORTS"),
 dict(kicker="VICE CITY \u00b7 LAUNCH DAY", art="vice",
      head="GTA VI Begins Global Rollout",
      deck="Gamers enter Vice City as Grand Theft Auto VI launches worldwide after a 13-year wait.",
      src="VICE CITY \u00b7 AP / BBC"),
]

SECTIONS = [
 ("WORLD", (139,30,30), "bridge", [
   ("CRIMEA", "Crimean Bridge attacked again, Russian official says", "Russian official reports a fresh strike on the Kerch crossing."),
   ("EUROPE", "EU proposes \u20ac45bn Ukraine loan", "Repaid only after Russia pays reparations, under the EU proposal."),
   ("GAZA", "Israeli forces launch rare Gaza ground operation", "A rare ground move beyond the Yellow Line, reports say."),
   ("GAZA AID", "Four nations demand Israel let aid reach flooded Gaza", "Australia, Canada, Italy and UK press for aid access."),
   ("WEST BANK", "Australia sanctions Israeli settlers", "Sanctions over West Bank expansion, Canberra says."),
   ("KOREA", "North Korea fires ballistic missiles", "Launches hours after a US\u2013South Korea\u2013Japan drill."),
   ("MYANMAR", "Myanmar faces historic UN genocide verdict", "UN verdict over the Rohingya, a historic ruling."),
 ]),
 ("US & POLITICS", (30,58,95), "capitol", [
   ("HOUSE", "Democrats nominate Hakeem Jeffries", "Set to be the first Black Speaker of the House."),
   ("SENATE", "Democrat Peltola wins Alaska", "Victory secures a 56\u201344 Senate majority."),
   ("CYBER", "Senators warn AI cyber threats outpace US defenses", "AI-enabled threats are outpacing US defenses, senators warn."),
   ("VENEZUELA", "State Dept details $12bn in Venezuelan revenue", "Details cover oil and mineral revenue of $12bn."),
   ("DEFENSE", "Hegseth makes surprise Venezuela trip", "Signs a defense pact on the surprise visit."),
   ("ISRAEL", "Israel's president taps Eisenkot to form government", "Eisenkot tapped, bypassing Netanyahu."),
 ]),
 ("MONEY & TECH", (20,83,45), "chart", [
   ("IPO", "Anthropic raises $81.3bn in biggest IPO of all time", "Poised for a $1.4tn market debut, the biggest IPO ever."),
   ("NVIDIA", "Nvidia founder Jensen Huang steps down", "Kress promises earlier raises, more stock; H-series China shipments halt."),
   ("FED", "Fed minutes: most officials expect further rate hikes", "Most officials expect further hikes, minutes show."),
   ("OIL", "Oil prices drop as supplies improve", "Improving supplies outweigh Middle East tensions."),
   ("AMAZON", "Amazon announces $7bn renewables in India by 2030", "A $7bn renewable-energy investment in India by 2030."),
   ("GERMANY", "Germany blocks Cosco takeover of Hamburg firm Zippel", "Berlin blocks Cosco's takeover of logistics firm Zippel."),
   ("ESPIONAGE", "Russian arrested for spying on Palantir", "Arrested for spying on US defense firm Palantir."),
 ]),
 ("SCIENCE & PLANET", (15,118,110), "rocket", [
   ("SPACE", "NASA's Voyager 1 reaches one-light-day milestone", "Nearly 50 years after launch, a one-light-day first."),
   ("OCEANS", "Nearly all coral reefs face extinction within 50 years", "IUCN study warns reefs face extinction within 50 years."),
   ("FINLAND", "Finland approves first permanent nuclear waste repository", "The world's first permanent repository, approved."),
   ("CYCLONE", "Cyclone Akvan bears down on Machilipatnam\u2013Puri coast", "Set to cross the coast on 20 November."),
   ("SPACE LAW", "ESA chief calls for space laws, satellite surveillance", "Calls for space laws and satellite surveillance."),
 ]),
 ("SOCIETY & CULTURE", (124,45,90), "palette", [
   ("ART", "Van Gogh painting sells for record $190.4m", "Record sale after a row over its Nazi history."),
   ("PEW", "Islam on track to be world's largest religion by 2035", "Pew projects the shift by 2035."),
   ("FRANCE", "France sees fourth weekend of living-cost protests", "A fourth weekend of protests over living costs."),
   ("UK\u2013INDIA", "PM Modi meets Prince and Princess of Wales", "Meeting on UK\u2013India ties."),
   ("OBITUARY", "Pearl Harbor survivor Gebhard Galle dies at 105", "Survivor Gebhard Galle dies at 105."),
 ]),
 ("SPORT", (154,52,18), "trophy", [
   ("FOOTBALL", "India beat Pakistan 2\u20131 to win SAFF final", "SAFF Championship final in Dhaka: India 2\u20131 Pakistan."),
   ("NBA", "Mavericks 116, Warriors 94", "Cooper Flagg scores 33 with 9 assists."),
   ("NBA", "Cavaliers edge Grizzlies 105\u2013102", "Cleveland edge Memphis in a 105\u2013102 finish."),
   ("CRICKET", "Duckett hits 133 as England take charge", "Third ODI vs Australia: Duckett's 133 puts England on top."),
   ("HOCKEY", "India women open hockey campaign vs Malaysia", "Asian Champions Trophy opener in Bhopal."),
   ("POLICY", "Sports Ministry forms 14-member league committee", "Committee for professionally run leagues."),
 ]),
]

NUMBERS = [
 ("$190.4M", "Van Gogh record"), ("$81.3BN", "Anthropic IPO"),
 ("\u20ac45BN", "EU Ukraine loan"), ("$12BN", "Venezuelan oil detailed"),
 ("$7BN", "Amazon India renewables"), ("1 LIGHT-DAY", "Voyager 1"),
 ("56\u201344", "US Senate majority"), ("105 YRS", "Pearl Harbor survivor"),
]
MARKETS = [
 ("Oil", "supply improves", False, [8,7,7,5,5,3]),
 ("Gold", "strong dollar", False, [3,4,5,5,6,7]),
 ("Fed", "hawkish minutes", True, [7,6,5,4,3,2]),
]
WEATHER = [
 ("storm", "Andhra coast", "Cyclone Akvan landfall 20 Nov"),
 ("rain", "South Florida", "El Ni\u00f1o downpours flood roads"),
 ("sunrain", "San Francisco", "Heavy rain, flooding"),
]
TICKER = [
 "EU extends Russia sanctions three more years",
 "Berlin charges alleged Russian informant Ilona W.",
 "Jaishankar: defence ties key ahead of India\u2013Japan 2+2",
 "World COPD Day urges early diagnosis",
 "German climber survives 100-metre Alps fall",
 "LPG tanker sunk off Bulgaria was hit by projectiles, official says",
 "Congress targets Modi government over inflation, seeks white paper",
 "Saudi Arabia says danger has passed in three southern cities",
]

def count_stories():
    n = len(HEROES) + sum(len(cards) for _,_,_,cards in SECTIONS)
    n += len(NUMBERS) + len(MARKETS) + len(WEATHER) + len(TICKER)
    return n

# ---------------- ART ----------------
def art_shenzhen(d, x, y, w, h):
    d.rectangle([x,y,x+w,y+h], fill=(135,190,225))
    d.ellipse([x+w-62,y+8,x+w-18,y+52], fill=(250,205,60), outline=(220,160,20), width=2)
    for cx,cy,s in [(x+18,y+12,26),(x+52,y+8,20),(x+w-120,y+16,22)]:
        d.ellipse([cx,cy,cx+s*2,cy+s], fill=(245,248,250)); d.ellipse([cx+10,cy-6,cx+s*2-6,cy+s-4], fill=(245,248,250))
    rng = random.Random(7)
    bx = x+8
    while bx < x+w-14:
        bw = rng.choice([16,20,24]); bh = rng.randint(28,58)
        d.rectangle([bx,y+h-38-bh,bx+bw,y+h-38], fill=(52,74,102))
        for wy in range(y+h-38-bh+5, y+h-44, 9):
            for wx in range(bx+3, bx+bw-3, 6):
                d.rectangle([wx,wy,wx+3,wy+4], fill=(255,230,130))
        bx += bw+5
    d.rectangle([x,y+h-38,x+w,y+h], fill=(70,70,74))
    for px,col in [(x+26,(200,30,40)),(x+w//2-10,(30,80,180)),(x+w-58,(245,200,40))]:
        d.line([px,y+h-38,px,y+h-78], fill=(20,20,20), width=2)
        d.polygon([(px,y+h-78),(px+26,y+h-71),(px,y+h-64)], fill=col, outline=(20,20,20))
    d.polygon([(x+52,y+h-18),(x+104,y+h-25),(x+114,y+h-17),(x+66,y+h-11)], fill=(225,228,232), outline=INK)
    d.rectangle([x+128,y+h-14,x+w-110,y+h-9], fill=(190,30,40))
    for i in range(7):
        sx = x+16+i*16
        d.ellipse([sx,y+h-10,sx+6,y+h-4], fill=(25,25,30)); d.rectangle([sx+1,y+h-4,sx+5,y+h], fill=(25,25,30))

def art_hormuz(d, x, y, w, h):
    d.rectangle([x,y,x+w,y+h], fill=(170,205,225))
    d.rectangle([x,y+h-52,x+w,y+h], fill=(28,95,140))
    for i in range(5):
        yy = y+h-46+i*9
        pts = [(x+j*14, yy + (3 if (j+i)%2 else -2)) for j in range(w//14+1)]
        d.line(pts, fill=(140,200,235), width=1)
    d.polygon([(x,y+h-52),(x+52,y+h-66),(x+78,y+h-52)], fill=(196,168,110))
    d.polygon([(x+w,y+h-52),(x+w-58,y+h-68),(x+w-84,y+h-52)], fill=(196,168,110))
    for lx,ly,lab in [(x+10,y+h-86,"QESHM"),(x+w-70,y+6,"KUWAIT"),(x+w-76,y+20,"BAHRAIN")]:
        d.ellipse([lx,ly,lx+7,ly+7], fill=(200,30,30))
        d.text((lx+9,ly-2), lab, font=F(SANS_BOLD,7), fill=(120,20,20))
    cx, cy = x+58, y+h-64
    d.polygon([(cx,cy),(cx+150,cy),(cx+138,cy+14),(cx+12,cy+14)], fill=(88,96,105), outline=INK)
    d.rectangle([cx+96,cy-20,cx+118,cy], fill=(70,78,88), outline=INK)
    d.line([cx+107,cy-20,cx+107,cy-32], fill=INK, width=2)
    for i in range(3):
        px = cx+18+i*26
        d.polygon([(px,cy-6),(px+16,cy-6),(px+8,cy-13)], fill=(40,48,58))
    for i in range(4):
        d.arc([cx-8+i*4, cy+14, cx+150, cy+26], 0, 180, fill=(230,245,250), width=1)
    ex, ey = x+w-108, y+h-46
    d.polygon([(ex,ey),(ex+62,ey),(ex+54,ey+9),(ex+8,ey+9)], fill=(110,60,50), outline=INK)
    d.rectangle([ex+34,ey-12,ex+44,ey], fill=(80,50,45))

def art_vice(d, x, y, w, h):
    d.rectangle([x,y,x+w,y+h], fill=(18,16,52))
    rng = random.Random(11)
    for _ in range(26):
        sx, sy = rng.randint(x+4,x+w-4), rng.randint(y+4,y+44)
        d.ellipse([sx,sy,sx+2,sy+2], fill=(255,255,240))
    d.ellipse([x+w-52,y+8,x+w-20,y+40], fill=(238,238,210))
    d.ellipse([x+w-60,y+6,x+w-28,y+36], fill=(18,16,52))
    bx = x+6
    while bx < x+w-20:
        bw = rng.choice([26,32,38]); bh = rng.randint(34,62)
        d.rectangle([bx,y+h-30-bh,bx+bw,y+h-30], fill=(38,30,74), outline=(255,90,180))
        for wy in range(y+h-30-bh+5, y+h-36, 9):
            for wx in range(bx+4, bx+bw-4, 8):
                if rng.random() > 0.35: d.rectangle([wx,wy,wx+4,wy+5], fill=(255,220,90))
        bx += bw+6
    d.rectangle([x+8,y+6,x+94,y+22], fill=(10,10,30), outline=(0,230,210), width=2)
    d.text((x+14,y+9), "VICE CITY", font=F(SANS_BOLD,11), fill=(255,90,200))
    for px in (x+18, x+w-30):
        d.line([px,y+h-30,px,y+h-66], fill=(90,60,30), width=3)
        for a in (-34,-14,8,28):
            d.line([px,y+h-66,px+a,y+h-80-abs(a)//3], fill=(30,160,90), width=3)
    d.polygon([(x+92,y+h-14),(x+140,y+h-18),(x+152,y+h-10),(x+146,y+h-5),(x+100,y+h-5)], fill=(12,12,16), outline=(0,230,210))
    d.ellipse([x+104,y+h-11,x+114,y+h-4], fill=(60,60,70)); d.ellipse([x+132,y+h-11,x+142,y+h-4], fill=(60,60,70))
    d.rectangle([x,y+h-4,x+w,y+h], fill=(255,90,180))

def thumb(d, x, y, s, kind, col):
    d.rectangle([x,y,x+s,y+s], fill=(238,230,205), outline=col, width=1)
    if kind=="bridge":
        d.arc([x+2,y+6,x+s-2,y+s+8],180,360,fill=(60,60,60),width=2); d.line([x+3,y+s//2,x+s-3,y+s//2],fill=INK,width=2); d.line([x+6,y+6,x+6,y+s//2],fill=INK); d.line([x+s-6,y+6,x+s-6,y+s//2],fill=INK)
    elif kind=="capitol":
        d.rectangle([x+6,y+s-12,x+s-6,y+s-4],fill=(90,110,150)); d.polygon([(x+s//2,y+3),(x+7,y+13),(x+s-7,y+13)],fill=(90,110,150)); d.rectangle([x+s//2-1,y+12,x+s//2+1,y+s-12],fill=(240,240,240))
    elif kind=="chart":
        d.line([x+4,y+s-5,x+s-4,y+s-5],fill=INK); d.line([x+4,y+4,x+4,y+s-5],fill=INK)
        d.line([(x+5,y+s-10),(x+12,y+s-16),(x+18,y+s-12),(x+s-5,y+s-22)],fill=(20,140,60),width=2)
    elif kind=="rocket":
        d.ellipse([x+s//2-5,y+3,x+s//2+5,y+18],fill=(200,200,210),outline=INK); d.polygon([(x+s//2-7,y+16),(x+s//2+7,y+16),(x+s//2,y+s-3)],fill=(230,120,30))
        d.ellipse([x+s-11,y+5,x+s-4,y+12],fill=(250,210,80))
    elif kind=="palette":
        d.ellipse([x+4,y+4,x+s-4,y+s-4],fill=(245,225,170),outline=INK)
        for cx,cy,c in [(x+9,y+10,(200,40,40)),(x+18,y+8,(40,90,200)),(x+13,y+18,(40,160,70))]: d.ellipse([cx,cy,cx+6,cy+6],fill=c)
    else:
        d.polygon([(x+s//2,y+3),(x+s//2+5,y+10),(x+s-4,y+10),(x+s//2+3,y+15),(x+s//2+6,y+s-4),(x+s//2,y+18),(x+s//2-6,y+s-4),(x+s//2-3,y+15),(x+4,y+10),(x+s//2-5,y+10)],fill=(240,180,30),outline=INK)

def weather_icon(d, x, y, kind):
    if kind=="storm":
        d.ellipse([x,y,x+22,y+12],fill=(110,120,135)); d.polygon([(x+12,y+10),(x+6,y+20),(x+11,y+20),(x+8,y+28),(x+17,y+17),(x+12,y+17)],fill=(250,190,30),outline=INK)
    elif kind=="rain":
        d.ellipse([x,y,x+24,y+12],fill=(120,140,165))
        for i in range(3): d.line([x+4+i*7,y+15,x+2+i*7,y+22],fill=(40,110,190),width=2)
    else:
        d.ellipse([x+10,y,x+24,y+14],fill=(250,190,50),outline=(210,150,20))
        d.ellipse([x,y+6,x+22,y+17],fill=(150,165,185))
        for i in range(3): d.line([x+5+i*7,y+20,x+3+i*7,y+27],fill=(40,110,190),width=2)

# ---------------- RENDER ----------------
def main():
    rng = random.Random(42)
    img = Image.new("RGB", (W,H), PAPER)
    d = ImageDraw.Draw(img)
    for _ in range(2600):
        px, py = rng.randint(0,W-1), rng.randint(0,H-1)
        v = rng.choice([(240,233,210),(250,246,230),(236,228,200)])
        d.point((px,py), fill=v)
    M = 12; R = W-12
    # Masthead
    d.line([M,14,R,14], fill=RULE, width=3); d.line([M,19,R,19], fill=RULE, width=1)
    title = "THE WHOLE DAY"
    f_t = F(SERIF_BLACK, 44)
    d.text(((W-tw(d,title,f_t))/2, 22), title, font=f_t, fill=INK)
    d.text((M,30), "Vol. I \u00b7 No. 19", font=F(SANS_BOLD,9), fill=MUTED)
    rtxt = "61 STORIES \u00b7 ONE PAGE \u00b7 ONE DAY"
    d.text((R-tw(d,rtxt,F(SANS_BOLD,9)),30), rtxt, font=F(SANS_BOLD,9), fill=MUTED)
    sub = "Thursday, 19 November 2026  \u00b7  BROADSHEET EDITION \u2014 ALL THE DAY'S NEWS ON ONE PAGE"
    f_s = F(SERIF_BOLD, 12)
    d.text(((W-tw(d,sub,f_s))/2, 70), sub, font=f_s, fill=(120,30,30))
    d.line([M,90,R,90], fill=RULE, width=1); d.line([M,93,R,93], fill=RULE, width=3)
    # Heroes
    hy, hh = 98, 252
    hw = (R-M-16)//3
    arts = {"shenzhen": art_shenzhen, "hormuz": art_hormuz, "vice": art_vice}
    for i, hero in enumerate(HEROES):
        x = M + i*(hw+8); x2 = x+hw
        d.rectangle([x+2,hy+2,x2+2,hy+hh+2], fill=(215,208,185))
        d.rectangle([x,hy,x2,hy+hh], fill=(252,248,235), outline=RULE, width=1)
        d.text((x+7,hy+5), hero["kicker"], font=F(SANS_BOLD,8), fill=(160,30,30))
        arts[hero["art"]](d, x+6, hy+17, hw-12, 112)
        yy = hy+133
        yy = fit_block(d, x+7, yy, hero["head"], SERIF_BLACK, 19, hw-14, 1.08, 3, 13)
        yy += 2
        yy = block(d, x+7, yy, hero["deck"], F(SANS_REG,9), hw-14, 11, (55,50,40), 4)
        d.line([x+7,hy+hh-16,x2-7,hy+hh-16], fill=(180,170,145), width=1)
        d.text((x+7,hy+hh-13), hero["src"], font=F(SANS_BOLD,7), fill=MUTED)
    # Sections: 3 columns x 2 rows, row heights sized to card counts
    sy = hy+hh+8
    row_h = [244, 213]
    row_y = [sy, sy+row_h[0]+6]
    colw = hw
    positions = [(0,0),(1,0),(2,0),(0,1),(1,1),(2,1)]
    for idx, (name, col, tk, cards) in enumerate(SECTIONS):
        cx_i, ry_i = positions[idx]
        sec_h = row_h[ry_i]
        x = M + cx_i*(colw+8); y = row_y[ry_i]; x2 = x+colw; y2 = y+sec_h
        d.rectangle([x,y,x2,y2], fill=(252,248,235), outline=RULE, width=1)
        d.rectangle([x,y,x2,y+19], fill=col)
        d.text((x+7,y+4), name, font=F(SERIF_BOLD,11), fill=(255,255,255))
        tag = f"{len(cards)} STORIES"
        d.text((x2-7-tw(d,tag,F(SANS_BOLD,8)),y+6), tag, font=F(SANS_BOLD,8), fill=(255,235,180))
        cy = y+23
        per = (sec_h-27)//len(cards)
        for ci,(kick, head, deck) in enumerate(cards):
            tx = x+7
            if ci==0:
                thumb(d, x+7, cy+1, 30, tk, col); tx = x+43
            yend = fit_block(d, tx, cy, head, SERIF_BOLD, 11, x2-7-tx, 1.05, 2, 9, INK)
            dy = yend + 1
            kw = tw(d, kick, F(SANS_BOLD,6))
            d.text((tx,dy), kick, font=F(SANS_BOLD,6), fill=col)
            d.text((tx+kw+5, dy), one_line(d, deck, F(SANS_REG,8), x2-7-(tx+kw+5)), font=F(SANS_REG,8), fill=(60,55,45))
            cy += per
            if ci < len(cards)-1: d.line([x+6,cy-3,x2-6,cy-3], fill=(205,196,168), width=1)
    # Numbers band
    ny = row_y[1] + row_h[1] + 8
    d.rectangle([M,ny,R,ny+50], fill=(26,23,16))
    d.text((M+8,ny+4), "BY THE NUMBERS", font=F(SERIF_BOLD,9), fill=(255,205,80))
    nw = (R-M-16)//4
    for i,(big,lab) in enumerate(NUMBERS):
        col_i, row_i = i%4, i//4
        x = M+8+col_i*nw; y = ny+16+row_i*17
        d.text((x,y), big, font=F(SERIF_BLACK,12), fill=(255,240,190))
        bw_ = tw(d,big,F(SERIF_BLACK,12))
        d.text((x+bw_+5,y+3), lab, font=F(SANS_REG,7), fill=(225,218,195))
    # Markets & weather
    my = ny+56
    d.rectangle([M,my,R,my+58], fill=(252,248,235), outline=RULE, width=1)
    mid = M+500
    d.line([mid,my+4,mid,my+54], fill=RULE, width=1)
    d.text((M+8,my+4), "MARKETS", font=F(SERIF_BOLD,9), fill=(20,83,45))
    d.text((mid+8,my+4), "WEATHER", font=F(SERIF_BOLD,9), fill=(15,100,140))
    for i,(name,note,up,pts) in enumerate(MARKETS):
        x = M+8+i*164; y = my+20
        d.text((x,y), name, font=F(SANS_BOLD,10), fill=INK)
        arrow = "\u25b2" if up else "\u25bc"
        acol = (20,140,60) if up else (190,40,40)
        d.text((x+tw(d,name,F(SANS_BOLD,10))+6,y), arrow, font=F(SANS_BOLD,11), fill=acol)
        d.text((x,y+13), note, font=F(SANS_REG,7), fill=MUTED)
        sx, sy2 = x+78, y+2
        coords = [(sx+j*11, sy2+pts[j]*2) for j in range(len(pts))]
        d.line(coords, fill=acol, width=2)
        for c in coords: d.ellipse([c[0]-1,c[1]-1,c[0]+1,c[1]+1], fill=acol)
    for i,(kind,place,note) in enumerate(WEATHER):
        x = mid+8+i*164; y = my+18
        weather_icon(d, x, y, kind)
        d.text((x+28,y), place, font=F(SANS_BOLD,8), fill=INK)
        block(d, x+28, y+10, note, F(SANS_REG,7), 128, 8, MUTED, 2)
    # Ticker
    ty = my+64
    d.rectangle([M,ty,R,ty+52], fill=(139,30,30))
    d.text((M+8,ty+4), "LATE WIRE", font=F(SERIF_BOLD,10), fill=(255,220,120))
    folio = "Continued on this page \u00b7 The Whole Day \u00b7 Thursday 19 November 2026"
    d.text((R-8-tw(d,folio,F(SANS_REG,7)),ty+5), folio, font=F(SANS_REG,7), fill=(255,235,220))
    ticker_text = "  \u25c6  ".join(TICKER)
    yy = ty+17
    for ln in wrap(d, ticker_text, F(SANS_REG,8), R-M-16)[:3]:
        d.text((M+8,yy), ln, font=F(SANS_REG,8), fill=(255,248,235)); yy += 11
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, optimize=True)
    print(f"STORY_COUNT={count_stories()}")
    print(f"WROTE {out}")

if __name__ == "__main__":
    main()
