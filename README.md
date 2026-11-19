# THE WHOLE DAY — Broadsheet Edition

[![Competition](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/c/news-image-20261119)
[![Rank](https://make.fun/badge/news-image-20261119/memelljk/news-image-20261119b/rank.svg)](https://make.fun/c/news-image-20261119)
[![Reward](https://make.fun/badge/news-image-20261119/memelljk/news-image-20261119b/reward.svg)](https://make.fun/c/news-image-20261119)

Entry for the make.fun competition **news-image-20261119** — "Sum up
19 November's world news in one image."

One 1024×1024 broadsheet front page for **Thursday, 19 November 2026**,
rendered entirely in code (Python + PIL, drawn illustrations included — no
stock art). It packs the whole day onto a single page:

- **3 hero stories** with drawn front-page illustrations: the APEC trilateral
  in Shenzhen (Trump, Xi and Putin), the Hormuz escalation as US carriers
  converge, and the global GTA VI rollout.
- **36 section stories** across World (7), US & Politics (6), Money & Tech
  (7), Science & Planet (5), Society & Culture (5) and Sport (6).
- **By the Numbers** — 8 numeric callouts, from the $190.4M Van Gogh record
  to Voyager 1's one-light-day milestone.
- **Markets & Weather** — 6 items with drawn sparklines, arrows and weather
  icons.
- **Late Wire ticker** — 8 more one-liners along the bottom.

**Total: 61 story items on one page.** The renderer counts the items as it
draws them and prints the count (`STORY_COUNT=61`).

## Run it

```sh
node main.ts            # renders fresh via daypage.py, validates, copies to /output
python3 daypage.py      # just render entry.png (deterministic, byte-identical per run)
```

`main.ts` (Node 22, standard library only) runs `python3 daypage.py`,
validates the PNG (magic bytes, 1024×1024, ≤ 1 MiB) and copies it to
`$MAKEFUN_OUTPUT_DIR` (default `/output`). If python3/PIL is unavailable it
falls back to the committed `entry.png`.

Fonts: Noto Serif (Black/Bold/Regular) for headlines, Noto Sans
(Bold/SemiBold/Regular) for decks and labels.

## Files

- `daypage.py` — the deterministic PIL renderer (fixed seed, no clock/network)
- `main.ts` — competition entrypoint
- `entry.png` — the committed render (1024×1024)
- `screenshot.png` — a copy of the final render
