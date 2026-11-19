#!/usr/bin/env python3
"""THE WHOLE DAY — Broadsheet Edition. Deterministic PIL renderer.

Renders a dense 1024x1024 newspaper front page for Thursday, 19 November 2026
and writes entry.png beside this file. Fixed seed, no clock, no network:
two runs produce byte-identical output. Prints the story count it rendered.
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = Path(__file__).resolve().parent / "entry.png"

NOTO = "/usr/share/fonts/truetype/noto"
SERIF_BLACK = f"{NOTO}/NotoSerif-Black.ttf"
SERIF_BOLD = f"{NOTO}/NotoSerif-Bold.ttf"
SERIF_REG = f"{NOTO}/NotoSerif-Regular.ttf"
SANS_BOLD = f"{NOTO}/NotoSans-Bold.ttf"
SANS_SEMI = f"{NOTO}/NotoSans-SemiBold.ttf"
SANS_REG = f"{NOTO}/NotoSans-Regular.ttf"

_fonts = {}


def F(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


INK = (28, 24, 20)
PAPER = (246, 240, 226)
PANEL = (252, 249, 240)
GREY = (105, 98, 88)
RULE = (60, 54, 46)

# ---------------------------------------------------------------- data ----
HEROES = [
    {
        "kind": "shenzhen",
        "kicker": "APEC SUMMIT · SHENZHEN",
        "headline": "Trump, Xi and Putin Meet in Shenzhen",
        "deck": "APEC trilateral: Xi embraced Trump on the tarmac as the "
                "leaders gather in China. (NYT/BBC)",
    },
    {
        "kind": "hormuz",
        "kicker": "STRAIT OF HORMUZ · ESCALATION",
        "headline": "Iran Strikes US Sites as Carriers Converge on Hormuz",
        "deck": "Iran hit US drone and missile sites in Kuwait and Bahrain; "
                "the US struck Qeshm Island. USS Theodore Roosevelt arrives "
                "\u2014 three US carriers in the region, a merchant ship "
                "attacked in the strait.",
    },
    {
        "kind": "vicecity",
        "kicker": "VICE CITY · LAUNCH DAY",
        "headline": "GTA VI Begins Global Rollout",
        "deck": "Gamers enter Vice City as Grand Theft Auto VI launches "
                "worldwide after a 13-year wait. (AP/BBC)",
    },
]

# (title, colour, [(kicker, headline, deck), ...])
SECTIONS = [
    ("WORLD", (122, 31, 31), [
        ("UKRAINE", "Crimean Bridge Attacked Again",
         "Russian official reports a fresh strike on the Kerch crossing"),
        ("BRUSSELS", "EU Proposes \u20ac45bn Ukraine Loan",
         "Repaid only after Russia pays reparations, under the plan"),
        ("GAZA", "Israel Launches Rare Gaza Ground Op",
         "Forces move beyond the Yellow Line in a rare ground operation"),
        ("DIPLOMACY", "Four Nations Demand Gaza Aid Access",
         "Australia, Canada, Italy and UK press Israel on flooded Gaza"),
        ("WEST BANK", "Australia Sanctions Israeli Settlers",
         "Canberra targets settlers over West Bank expansion"),
        ("KOREA", "North Korea Fires Ballistic Missiles",
         "Launch comes hours after US\u2013South Korea\u2013Japan drill"),
        ("THE HAGUE", "Myanmar Faces UN Genocide Verdict",
         "Historic ruling due over the Rohingya at the United Nations"),
    ]),
    ("US & POLITICS", (31, 58, 110), [
        ("CAPITOL", "Democrats Nominate Hakeem Jeffries",
         "Set to be the first Black Speaker of the House"),
        ("SENATE", "Peltola Wins Alaska for Democrats",
         "Victory secures a 56\u201344 Senate majority"),
        ("CYBER", "Senators Warn on AI Cyber Threats",
         "AI-enabled attacks are outpacing US defenses, senators warn"),
        ("STATE DEPT", "State Dept Details $12bn Venezuela Take",
         "Oil and mineral revenue from Venezuela itemised at $12bn"),
        ("DEFENSE", "Hegseth Makes Surprise Venezuela Trip",
         "Signs a defense pact on a surprise trip to Venezuela"),
        ("ISRAEL", "Eisenkot Tapped to Form Government",
         "Israel's president bypasses Netanyahu in picking Eisenkot"),
    ]),
    ("MONEY & TECH", (20, 83, 45), [
        ("IPO", "Anthropic Raises $81.3bn in Record IPO",
         "Biggest IPO of all time; poised for a $1.4tn market debut"),
        ("CHIPS", "Nvidia Founder Jensen Huang Steps Down",
         "Kress promises raises, more stock; H-series to China halted"),
        ("FED", "Fed Minutes Point to Further Hikes",
         "Most officials expect further rate hikes, minutes show"),
        ("ENERGY", "Oil Prices Drop on Improving Supply",
         "Supply gains outweigh Middle East tensions in trading"),
        ("INDIA", "Amazon Puts $7bn Into India Renewables",
         "Renewable-energy investment in India by 2030 announced"),
        ("TRADE", "Germany Blocks Cosco Hamburg Takeover",
         "Berlin stops Cosco's bid for logistics firm Zippel"),
        ("ESPIONAGE", "Russian Held for Spying on Palantir",
         "Arrested for spying on US defense firm Palantir"),
    ]),
    ("SCIENCE & PLANET", (14, 90, 109), [
        ("DEEP SPACE", "Voyager 1 Reaches One-Light-Day Mark",
         "NASA probe hits the milestone nearly 50 years after launch"),
        ("OCEANS", "Nearly All Coral Reefs Face Extinction",
         "IUCN study: reefs could vanish within 50 years"),
        ("ENERGY", "Finland Approves Nuclear Waste Vault",
         "World's first permanent nuclear waste repository approved"),
        ("CYCLONE", "Cyclone Akvan Bears Down on India",
         "Set to cross the Machilipatnam\u2013Puri coast on 20 November"),
        ("ORBIT", "ESA Chief Calls for Space Laws",
         "Calls for space laws and satellite surveillance"),
    ]),
    ("SOCIETY & CULTURE", (109, 42, 90), [
        ("ART MARKET", "Van Gogh Sells for Record $190.4m",
         "Record price after a row over the painting's Nazi history"),
        ("FAITH", "Islam on Track to Be Largest Religion",
         "Pew: largest in the world by 2035, the study projects"),
        ("FRANCE", "France: Fourth Weekend of Protests",
         "Protests over living costs roll into a fourth weekend"),
        ("ROYALS", "Modi Meets Prince & Princess of Wales",
         "UK\u2013India ties in focus as PM Modi meets the royals"),
        ("OBITUARY", "Pearl Harbor Survivor Dies at 105",
         "Gebhard Galle, who survived the 1941 attack, was 105"),
    ]),
    ("SPORT", (154, 52, 18), [
        ("FOOTBALL", "India Beat Pakistan 2\u20131 in SAFF Final",
         "Final in Dhaka \u2014 India win the SAFF Championship"),
        ("NBA", "Mavericks 116, Warriors 94",
         "Cooper Flagg scores 33 with 9 assists for Dallas"),
        ("NBA", "Cavaliers Edge Grizzlies 105\u2013102",
         "Cleveland take a tight one in the NBA, by three points"),
        ("CRICKET", "Duckett Hits 133 as England Take Charge",
         "Third ODI against Australia: Duckett's 133 leads England"),
        ("HOCKEY", "India Women Open Hockey Campaign",
         "Asian Champions Trophy opener vs Malaysia, in Bhopal"),
        ("POLICY", "Sports Ministry Forms League Committee",
         "14-member committee for professionally run leagues"),
    ]),
]

NUMBERS = [
    ("$190.4M", "Van Gogh record sale"),
    ("$81.3BN", "Anthropic IPO raise"),
    ("\u20ac45BN", "EU loan for Ukraine"),
    ("$12BN", "Venezuelan oil detailed"),
    ("$7BN", "Amazon India renewables"),
    ("1 LIGHT-DAY", "Voyager 1 milestone"),
    ("56\u201344", "US Senate majority"),
    ("105 YRS", "Pearl Harbor survivor"),
]

MARKETS = [  # (name, note, points, colour, up?)
    ("OIL", "\u25bc on improving supply", [38, 34, 35, 28, 29, 22, 18], (178, 34, 34), False),
    ("GOLD", "\u25bc on a strong dollar", [36, 33, 34, 27, 28, 21, 17], (178, 34, 34), False),
    ("FED FUNDS", "\u25b2 hawkish minutes", [14, 18, 17, 24, 23, 30, 34], (22, 128, 57), True),
]

WEATHER = [  # (place, note, icon)
    ("ANDHRA COAST", "Cyclone Akvan landfall 20 Nov", "storm"),
    ("SOUTH FLORIDA", "El Ni\u00f1o downpours flood roads", "rain"),
    ("SAN FRANCISCO", "Heavy rain, flooding", "sun"),
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

STORY_COUNT = (
    len(HEROES)
    + sum(len(cards) for _, _, cards in SECTIONS)
    + len(NUMBERS)
    + len(MARKETS)
    + len(WEATHER)
    + len(TICKER)
)

# ------------------------------------------------------------- helpers ----


def tw(d, text, font):
    return d.textlength(text, font=font)


def wrap(d, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = f"{cur} {w_}".strip()
        if tw(d, t, font) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def fit_lines(d, text, path, start, minimum, max_w, max_lines):
    """Largest font size whose wrap fits max_lines; returns (font, lines)."""
    size = start
    while size > minimum:
        f = F(path, size)
        lines = wrap(d, text, f, max_w)
        if len(lines) <= max_lines:
            return f, lines
        size -= 1
    f = F(path, minimum)
    lines = wrap(d, text, f, max_w)[:max_lines]
    if lines:  # ellipsise an over-long last line
        last = lines[-1]
        while last and tw(d, last + "\u2026", f) > max_w:
            last = last[:-1]
        lines[-1] = last + "\u2026"
    return f, lines


def one_line(d, text, path, start, minimum, max_w):
    """Single line, shrunk then ellipsised to fit."""
    size = start
    while size > minimum and tw(d, text, F(path, size)) > max_w:
        size -= 1
    f = F(path, size)
    if tw(d, text, f) > max_w:
        while text and tw(d, text + "\u2026", f) > max_w:
            text = text[:-1]
        text += "\u2026"
    return f, text


def panel(d, x, y, x2, y2, fill=PANEL):
    d.rectangle([x + 3, y + 3, x2 + 3, y2 + 3], fill=(214, 206, 188))
    d.rectangle([x, y, x2, y2], fill=fill, outline=RULE, width=1)


# --------------------------------------------------------- illustrations --


def illus_shenzhen(d, x, y, x2, y2):
    d.rectangle([x, y, x2, y2], fill=(168, 205, 228))
    d.rectangle([x, y + 26, x2, y2], fill=(188, 216, 233))
    d.ellipse([x + 16, y + 6, x + 34, y + 24], fill=(250, 205, 84))
    rng = random.Random(7)
    bx = x + 6
    while bx < x2 - 16:  # skyline
        bw = rng.choice([16, 20, 24, 14])
        bh = rng.choice([20, 30, 38, 26, 34])
        d.rectangle([bx, y2 - 12 - bh, bx + bw, y2 - 12], fill=(52, 74, 102))
        for wy in range(y2 - 12 - bh + 4, y2 - 16, 7):
            for wx in range(bx + 3, bx + bw - 3, 6):
                if rng.random() < 0.55:
                    d.rectangle([wx, wy, wx + 3, wy + 3], fill=(250, 220, 130))
        bx += bw + 4
    d.rectangle([x, y2 - 12, x2, y2], fill=(96, 92, 84))  # tarmac
    d.line([x, y2 - 12, x2, y2 - 12], fill=(240, 240, 230), width=1)
    flags = [((207, 42, 42), "star"), ((38, 74, 150), "stripes"),
             ((235, 235, 235), "bands")]
    for i, (col, kind) in enumerate(flags):  # three flags on poles
        fx = x + 52 + i * 86
        d.line([fx, y + 10, fx, y2 - 12], fill=(40, 40, 40), width=2)
        d.rectangle([fx + 2, y + 10, fx + 34, y + 26], fill=col)
        if kind == "star":
            d.polygon([(fx + 8, y + 14), (fx + 10, y + 19), (fx + 15, y + 19),
                       (fx + 11, y + 22), (fx + 12, y + 27), (fx + 8, y + 24),
                       (fx + 4, y + 27), (fx + 5, y + 22), (fx + 1, y + 19),
                       (fx + 6, y + 19)], fill=(250, 210, 60))
        elif kind == "stripes":
            for s in range(3):
                d.line([fx + 3, y + 13 + s * 4, fx + 33, y + 13 + s * 4],
                       fill=(235, 235, 235), width=1)
        else:
            d.rectangle([fx + 2, y + 15, fx + 34, y + 20], fill=(52, 84, 170))
            d.rectangle([fx + 2, y + 20, fx + 34, y + 26], fill=(198, 48, 49))
    # two figures shaking hands on the tarmac
    for cx, col in [(x + 128, (30, 50, 96)), (x + 158, (120, 30, 30))]:
        d.ellipse([cx - 4, y2 - 26, cx + 4, y2 - 18], fill=(232, 190, 150))
        d.rectangle([cx - 4, y2 - 18, cx + 4, y2 - 4], fill=col)
    d.line([x + 132, y2 - 14, x + 154, y2 - 14], fill=(232, 190, 150), width=3)


def illus_hormuz(d, x, y, x2, y2):
    d.rectangle([x, y, x2, y2], fill=(176, 208, 226))
    d.ellipse([x2 - 36, y + 5, x2 - 18, y + 23], fill=(250, 205, 84))
    d.polygon([(x, y + 22), (x + 52, y + 8), (x + 104, y + 22)], fill=(150, 138, 120))
    d.polygon([(x2 - 96, y + 22), (x2 - 44, y + 10), (x2, y + 22)], fill=(158, 146, 128))
    sea = y + 24
    d.rectangle([x, sea, x2, y2], fill=(38, 96, 138))
    rng = random.Random(11)
    for wy in range(sea + 5, y2 - 3, 7):  # wave arcs
        for wx in range(x + rng.randint(0, 8), x2 - 12, 22):
            d.arc([wx, wy, wx + 12, wy + 5], 180, 360, fill=(150, 200, 232), width=1)
    cx, cy = x + 58, sea + 12  # aircraft carrier
    d.polygon([(cx, cy + 16), (cx + 14, cy + 24), (cx + 168, cy + 24),
               (cx + 182, cy + 16)], fill=(44, 48, 54))
    d.rectangle([cx + 4, cy + 10, cx + 178, cy + 16], fill=(70, 76, 84))
    d.rectangle([cx + 118, cy - 2, cx + 140, cy + 10], fill=(58, 63, 70))
    d.line([cx + 129, cy - 12, cx + 129, cy - 2], fill=(40, 42, 46), width=2)
    for px in (cx + 26, cx + 56, cx + 86):  # jets on deck
        d.polygon([(px, cy + 13), (px + 14, cy + 11), (px + 20, cy + 13),
                   (px + 14, cy + 15)], fill=(196, 204, 212))
    for bx, col in [(x + 20, (214, 60, 50)), (x2 - 34, (240, 180, 40))]:
        d.rectangle([bx, sea + 4, bx + 8, sea + 12], fill=col)  # strait buoys
        d.line([bx + 4, sea, bx + 4, sea + 4], fill=(30, 30, 30), width=1)


def illus_vicecity(d, x, y, x2, y2):
    d.rectangle([x, y, x2, y2], fill=(24, 18, 52))
    d.rectangle([x, y + 30, x2, y2], fill=(44, 24, 74))
    d.ellipse([x2 - 34, y + 5, x2 - 16, y + 23], fill=(238, 232, 200))
    rng = random.Random(23)
    bx = x + 4
    neon = [(255, 80, 180), (60, 220, 255), (255, 200, 60), (140, 255, 140)]
    ci = 0
    while bx < x2 - 14:  # neon skyline
        bw = rng.choice([15, 19, 23])
        bh = rng.choice([18, 27, 35, 24])
        d.rectangle([bx, y2 - 10 - bh, bx + bw, y2 - 10], fill=(16, 14, 34))
        for wy in range(y2 - 10 - bh + 3, y2 - 14, 6):
            for wx in range(bx + 3, bx + bw - 3, 5):
                if rng.random() < 0.5:
                    d.rectangle([wx, wy, wx + 2, wy + 3], fill=neon[ci % 4])
        ci += 1
        bx += bw + 3
    d.rectangle([x, y2 - 10, x2, y2], fill=(70, 30, 84))
    for px in (x + 34, x + 96, x2 - 52):  # palm trees
        top = y2 - 40
        d.line([px, y2 - 8, px + 4, top], fill=(30, 110, 60), width=3)
        for ang in (-52, -26, 0, 26, 52):
            import math
            ex = px + 4 + int(17 * math.sin(math.radians(ang)))
            ey = top + int(8 * (1 - math.cos(math.radians(ang)))) - 2
            d.line([px + 4, top, ex, ey + 5], fill=(46, 170, 90), width=2)
    d.rectangle([x + 128, y + 8, x + 216, y + 24], outline=(255, 80, 180), width=2)
    f = F(SANS_BOLD, 11)
    d.text((x + 172 - tw(d, "VICE CITY", f) / 2, y + 10), "VICE CITY", font=f,
           fill=(255, 140, 210))


ILLUS = {"shenzhen": illus_shenzhen, "hormuz": illus_hormuz, "vicecity": illus_vicecity}

# ---------------------------------------------------------------- draw ----


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    rng = random.Random(20261119)  # deterministic paper texture
    for _ in range(7000):
        px, py = rng.randrange(W), rng.randrange(H)
        shade = rng.choice([(238, 231, 214), (240, 234, 218), (236, 229, 210)])
        d.point((px, py), fill=shade)
    for gx in range(0, W, 4):  # faint halftone grid
        for gy in range(0, H, 4):
            if (gx // 4 + gy // 4) % 37 == 0:
                d.point((gx, gy), fill=(232, 225, 205))

    M = 12           # page margin
    CW = W - 2 * M   # content width = 1000

    # ---- masthead ------------------------------------------------------
    d.rectangle([M, 8, W - M, 10], fill=INK)
    d.rectangle([M, 13, W - M, 14], fill=INK)
    f_title = F(SERIF_BLACK, 47)
    title = "THE WHOLE DAY"
    d.text(((W - tw(d, title, f_title)) / 2, 17), title, font=f_title, fill=INK)
    f_side = F(SANS_BOLD, 9)
    d.text((M + 2, 30), "Vol. I \u00b7 No. 19", font=f_side, fill=GREY)
    d.text((M + 2, 43), "EST. 2026 \u00b7 DAILY", font=f_side, fill=GREY)
    right = f"{STORY_COUNT} STORIES"
    d.text((W - M - 2 - tw(d, right, f_side), 30), right, font=f_side, fill=GREY)
    d.text((W - M - 2 - tw(d, "ONE PAGE \u00b7 ONE DAY", f_side), 43),
           "ONE PAGE \u00b7 ONE DAY", font=f_side, fill=GREY)
    f_date = F(SERIF_BOLD, 12)
    d.text((M + 2, 56), "Thursday, 19 November 2026", font=f_date, fill=INK)
    f_ed = F(SANS_BOLD, 10)
    ed = "BROADSHEET EDITION \u2014 ALL THE DAY'S NEWS ON ONE PAGE"
    d.text((W - M - 2 - tw(d, ed, f_ed), 57), ed, font=f_ed, fill=(122, 31, 31))
    d.rectangle([M, 74, W - M, 75], fill=INK)
    d.rectangle([M, 78, W - M, 81], fill=INK)

    # ---- heroes ----------------------------------------------------------
    hy, hh = 86, 152
    hgap = 6
    hw = (CW - 2 * hgap) // 3
    for i, hero in enumerate(HEROES):
        x = M + i * (hw + hgap)
        x2, y2 = x + hw, hy + hh
        panel(d, x, hy, x2, y2)
        ILLUS[hero["kind"]](d, x + 5, hy + 5, x2 - 5, hy + 57)
        d.rectangle([x + 5, hy + 5, x2 - 5, hy + 57], outline=RULE, width=1)
        ky = hy + 62
        fk = F(SANS_BOLD, 9)
        d.text((x + 8, ky), hero["kicker"], font=fk, fill=(122, 31, 31))
        fh, hlines = fit_lines(d, hero["headline"], SERIF_BLACK, 19, 13,
                               hw - 16, 2)
        ty = ky + 13
        for ln in hlines:
            d.text((x + 8, ty), ln, font=fh, fill=INK)
            ty += fh.size + 3
        fd, dlines = fit_lines(d, hero["deck"], SANS_REG, 11, 9,
                               hw - 16, 3)
        for ln in dlines:
            d.text((x + 8, ty + 1), ln, font=fd, fill=(52, 48, 42))
            ty += fd.size + 3

    # ---- six sections, 3 columns x 2 rows --------------------------------
    sy = hy + hh + 8            # 246
    sh_total = 566
    row_h = sh_total // 2
    sgap = 6
    sw = (CW - 2 * sgap) // 3
    for idx, (name, colour, cards) in enumerate(SECTIONS):
        col, row = idx % 3, idx // 3
        x = M + col * (sw + sgap)
        y = sy + row * row_h
        x2, y2 = x + sw, y + row_h - 6
        panel(d, x, y, x2, y2)
        d.rectangle([x, y, x2, y + 21], fill=colour)
        f_sec = F(SERIF_BOLD, 13)
        d.text((x + 8, y + 4), name, font=f_sec, fill=(255, 252, 244))
        cnt = f"{len(cards)} STORIES"
        f_cnt = F(SANS_BOLD, 8)
        d.text((x2 - 8 - tw(d, cnt, f_cnt), y + 7), cnt, font=f_cnt,
               fill=(255, 252, 244))
        n = len(cards)
        card_h = (y2 - (y + 25)) / n
        for j, (kick, head, deck) in enumerate(cards):
            cy = y + 25 + j * card_h
            if j:
                d.line([x + 7, cy, x2 - 7, cy], fill=(206, 198, 180), width=1)
            d.rectangle([x + 7, cy + 5, x + 10, cy + card_h - 5], fill=colour)
            fk = F(SANS_BOLD, 8)
            kw = tw(d, kick, fk)
            d.text((x + 14, cy + 4), kick, font=fk, fill=colour)
            fh, headline = one_line(d, head, SERIF_BOLD, 13, 11,
                                    sw - 28 - kw)
            d.text((x + 16 + kw, cy + 1), headline, font=fh, fill=INK)
            max_dl = 2 if card_h >= 44 else 1
            fd, dlines = fit_lines(d, deck, SANS_REG, 10, 9, sw - 22, max_dl)
            dy = cy + 17
            for ln in dlines:
                d.text((x + 14, dy), ln, font=fd, fill=(62, 57, 50))
                dy += fd.size + 2

    # ---- by the numbers ----------------------------------------------------
    ny = sy + sh_total + 6       # 818
    nh = 58
    panel(d, M, ny, W - M, ny + nh)
    f_lab = F(SANS_BOLD, 10)
    d.text((M + 8, ny + 4), "BY THE NUMBERS", font=f_lab, fill=(122, 31, 31))
    cell_w = CW / len(NUMBERS)
    for i, (val, lab) in enumerate(NUMBERS):
        cx = M + i * cell_w
        if i:
            d.line([cx, ny + 20, cx, ny + nh - 5], fill=(206, 198, 180), width=1)
        fv, vtxt = one_line(d, val, SERIF_BLACK, 17, 12, cell_w - 8)
        d.text((cx + (cell_w - tw(d, vtxt, fv)) / 2, ny + 17), vtxt, font=fv,
               fill=INK)
        fl, llines = fit_lines(d, lab, SANS_REG, 9, 8, cell_w - 8, 2)
        ly = ny + 38
        for ln in llines:
            d.text((cx + (cell_w - tw(d, ln, fl)) / 2, ly), ln, font=fl,
                   fill=GREY)
            ly += fl.size + 1

    # ---- markets & weather -------------------------------------------------
    my = ny + nh + 6             # 882
    mh = 64
    half = (CW - sgap) // 2
    for side in range(2):
        x = M + side * (half + sgap)
        x2 = x + half
        panel(d, x, my, x2, my + mh)
        title = "MARKETS" if side == 0 else "WEATHER"
        d.rectangle([x, my, x2, my + 17], fill=(38, 36, 32))
        f_mt = F(SERIF_BOLD, 11)
        d.text((x + 8, my + 3), title, font=f_mt, fill=(255, 252, 244))
    # markets: three rows with sparklines
    mx = M
    for i, (name, note, pts, colr, _up) in enumerate(MARKETS):
        ry = my + 20 + i * 14
        f_mn = F(SANS_BOLD, 10)
        d.text((mx + 8, ry), name, font=f_mn, fill=INK)
        sx0, sy0 = mx + 92, ry + 1
        for a, b in zip(pts, pts[1:]):
            pass
        prev = None
        for k, p in enumerate(pts):
            px = sx0 + k * 11
            py = ry + 12 - int(p * 0.30)
            if prev:
                d.line([prev[0], prev[1], px, py], fill=colr, width=2)
            prev = (px, py)
        d.polygon([(prev[0] + 5, prev[1]), (prev[0] - 2, prev[1] - 3),
                   (prev[0] - 1, prev[1] + 4)], fill=colr)
        f_no = F(SANS_REG, 10)
        d.text((mx + 190, ry), note, font=f_no, fill=(52, 48, 42))
    # weather: three columns with icons
    wx0 = M + half + sgap
    wcell = half / 3
    for i, (place, note, icon) in enumerate(WEATHER):
        cx = wx0 + i * wcell
        ix, iy = cx + 10, my + 24
        if icon == "storm":
            d.ellipse([ix, iy, ix + 26, iy + 13], fill=(110, 116, 124))
            d.polygon([(ix + 12, iy + 11), (ix + 6, iy + 22), (ix + 12, iy + 22),
                       (ix + 9, iy + 30), (ix + 19, iy + 19), (ix + 13, iy + 19)],
                      fill=(240, 180, 30))
        elif icon == "rain":
            d.ellipse([ix, iy, ix + 26, iy + 13], fill=(110, 116, 124))
            for dx in (4, 12, 20):
                d.line([ix + dx, iy + 16, ix + dx - 2, iy + 22],
                       fill=(52, 110, 180), width=2)
        else:  # sun-shower
            d.ellipse([ix + 12, iy - 4, ix + 26, iy + 10], fill=(250, 195, 60))
            d.ellipse([ix, iy + 4, ix + 26, iy + 17], fill=(130, 136, 144))
            for dx in (6, 15):
                d.line([ix + dx, iy + 20, ix + dx - 2, iy + 26],
                       fill=(52, 110, 180), width=2)
        f_wp = F(SANS_BOLD, 9)
        d.text((cx + 42, my + 23), place, font=f_wp, fill=INK)
        f_wn, wlines = fit_lines(d, note, SANS_REG, 9, 8, wcell - 46, 3)
        wy = my + 35
        for ln in wlines:
            d.text((cx + 42, wy), ln, font=f_wn, fill=(62, 57, 50))
            wy += f_wn.size + 1

    # ---- bottom ticker -------------------------------------------------------
    ty0 = my + mh + 6            # 952
    th = 62
    d.rectangle([M, ty0, W - M, ty0 + th], fill=(26, 23, 20))
    f_tl = F(SANS_BOLD, 9)
    d.text((M + 8, ty0 + 4), "LATE WIRE", font=f_tl, fill=(250, 205, 84))
    tick = "  \u25c6  ".join(TICKER)
    f_tk, tlines = fit_lines(d, tick, SANS_REG, 10, 9, CW - 16, 4)
    ly = ty0 + 17
    for ln in tlines:
        d.text((M + 8, ly), ln, font=f_tk, fill=(245, 240, 226))
        ly += f_tk.size + 3

    img.save(OUT, format="PNG")
    print(f"STORY_COUNT={STORY_COUNT}")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
