#!/usr/bin/env python3
"""Build the 550 prompts site into dist/ ready for GitHub Pages."""
import json, os, re, shutil, sys, html

ROOT = "/Users/apple/.openclaw-autoclaw/workspace/550-image-prompts-site"
SRC_IMG = "/Users/apple/.openclaw-autoclaw/workspace/550 Image Prompt/550 chatgpt image prompts "
DIST = os.path.join(ROOT, "dist")

data = json.load(open(os.path.join(ROOT, "data/prompts.json"), encoding="utf-8"))
items, sections, tail = data["items"], data["sections"], data["tail"]
howto = data["intro_howto"]

# ── 1. images ────────────────────────────────────────────────────────────────
img_dist = os.path.join(DIST, "images")
if os.path.exists(img_dist):
    shutil.rmtree(img_dist)
os.makedirs(img_dist)
copied = 0
for f in os.listdir(SRC_IMG):
    m = re.match(r"^(\d+)\. .+\.webp$", f)
    if not m:
        continue
    shutil.copy2(os.path.join(SRC_IMG, f), os.path.join(img_dist, f"{m.group(1)}.webp"))
    copied += 1
print(f"images copied: {copied}")
if copied != 550:
    print("FATAL: expected 550 images", file=sys.stderr); sys.exit(1)

# ── 1.5 static assets ──────────────────────────────────────────────────────
assets_dst = os.path.join(DIST, "assets")
if os.path.exists(assets_dst):
    shutil.rmtree(assets_dst)
shutil.copytree(os.path.join(ROOT, "assets"), assets_dst,
                ignore=shutil.ignore_patterns(".DS_Store"))
print("assets copied")

# ── 2. prompts.js (window.PROMPTS_DATA) ─────────────────────────────────
with open(os.path.join(DIST, "data.js"), "w", encoding="utf-8") as f:
    f.write("window.PROMPTS_DATA=")
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"), write=True) if False else f.write(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    f.write(";\n")

# ── 3. noscript fallback list ────────────────────────────────────────────────
nos = "\n".join(
    f'<li><a href="#prompt-{n}">#{n} — {html.escape(items[str(n)]["t"])}</a></li>'
    for n in range(1, 551)
)

# ── 4. tail blocks html ──────────────────────────────────────────────────────
tail_html = ""
pro_tips = next((b for b in tail if b["title"] == "Pro Tips"), None)
truth = next((b for b in tail if b["title"] == "The Truth"), None)
quick = next((b for b in tail if b["title"] == "Quick Start"), None)
bottom = next((b for b in tail if b["title"] == "Bottom Line"), None)

if pro_tips:
    tips = "".join(f'<li class="tip"><p>{html.escape(l)}</p></li>' for l in pro_tips["lines"])
    tail_html += f"""
  <section class="info-section" id="tips" aria-labelledby="tips-h">
    <div class="container">
      <div class="section-head">
        <span class="eyebrow">Pro tips</span>
        <h2 id="tips-h">Twenty habits that make prompts work harder</h2>
        <p>The small choices — purpose first, subject before style, one change at a time — are what separate a usable image from a lucky one.</p>
      </div>
      <ul class="tip-grid">{tips}</ul>
    </div>
  </section>"""

if truth or bottom:
    tp = "".join(f"<p>{html.escape(l)}</p>" for l in (truth["lines"] if truth else []))
    bl = "".join(f"<p>{html.escape(l)}</p>" for l in (bottom["lines"] if bottom else []))
    tail_html += f"""
  <section class="info-section tinted" aria-labelledby="truth-h">
    <div class="container">
      <div class="truth-block">
        <h3 id="truth-h">The truth about long prompts</h3>
        {tp}{bl}
      </div>
    </div>
  </section>"""

if quick:
    qs = "".join(f"<li>{html.escape(l)}</li>" for l in quick["lines"])
    tail_html += f"""
  <section class="info-section" aria-labelledby="quickstart-h">
    <div class="container">
      <div class="section-head">
        <span class="eyebrow">Quick start</span>
        <h2 id="quickstart-h">From blank chat to finished image in ten steps</h2>
      </div>
      <ol class="steps" style="grid-template-columns:repeat(auto-fit,minmax(280px,1fr));list-style:none">{qs}</ol>
    </div>
  </section>"""

# quick start rendered as steps would need numbers; keep as styled list instead
if quick:
    tail_html = tail_html.replace('<ol class="steps" style="grid-template-columns:repeat(auto-fit,minmax(280px,1fr));list-style:none">',
                                  '<ol class="tip-grid" style="counter-reset:none">')

howto_steps = "".join(f'<li class="step"><p>{html.escape(s)}</p></li>' for s in howto)

# ── 5. page shell ────────────────────────────────────────────────────────────
page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>550 ChatGPT Image Prompts — by Sifu Yik</title>
<meta name="description" content="A searchable gallery of 550 ChatGPT image prompts by Sifu Yik — portraits, products, food, travel, diagrams, fantasy and more. Every prompt ships with a real example image. Copy, paste, and make it yours.">
<meta property="og:title" content="550 ChatGPT Image Prompts — by Sifu Yik">
<meta property="og:description" content="550 copy-paste ChatGPT image prompts, each with a real example image. Search, filter by category, and copy in one click.">
<meta property="og:type" content="website">
<meta property="og:image" content="images/1.webp">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='16' fill='%23c81e5b'/%3E%3Ctext x='32' y='42' font-family='Arial Black,sans-serif' font-size='30' font-weight='900' fill='%23fff' text-anchor='middle'%3E550%3C/text%3E%3C/svg%3E">
<link rel="preload" href="assets/fonts/baloo2-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/nunito-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
<a class="skip-link" href="#gallery">Skip to the gallery</a>

<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="#top" aria-label="550 ChatGPT Image Prompts — home">
      <span class="brand-mark" aria-hidden="true">550</span>
      <span>Image Prompts</span>
      <span class="brand-by">by Sifu Yik</span>
    </a>
    <nav class="site-nav" aria-label="Site">
      <a href="#gallery">Gallery</a>
      <a href="#how-to">How to use</a>
      <a href="#tips">Pro tips</a>
      <button class="btn btn-sub btn-sm" id="random-btn" type="button">Surprise me</button>
      <a class="btn btn-primary btn-sm" href="https://sifuyik.substack.com/subscribe" target="_blank" rel="noopener">Subscribe</a>
    </nav>
  </div>
</header>

<main id="top">
  <section class="hero">
    <div class="container hero-grid">
      <div>
        <p class="eyebrow">Free copy-paste library</p>
        <h1>550 ChatGPT image prompts, each with the picture to prove it</h1>
        <p class="lead">Stop asking ChatGPT to “make it look nice.” Every prompt below pairs a real generated image with the exact words that made it — portraits, products, food, travel, diagrams, fantasy worlds and more. Copy one, swap the [brackets], and make it yours.</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="#gallery">Browse the gallery</a>
          <button class="btn btn-sub" id="random-btn-2" type="button">Surprise me</button>
        </div>
        <p class="hero-meta">550 prompts · 23 categories · one click to copy · works free in ChatGPT</p>
      </div>
      <div class="hero-strip" aria-hidden="true">
        <div class="col">
          <img src="images/1.webp" alt="" loading="eager" width="640" height="800">
          <img src="images/257.webp" alt="" loading="lazy" width="640" height="800">
        </div>
        <div class="col">
          <img src="images/34.webp" alt="" loading="lazy" width="640" height="800">
          <img src="images/441.webp" alt="" loading="lazy" width="640" height="800">
        </div>
 <div class="col">
          <img src="images/131.webp" alt="" loading="lazy" width="640" height="800">
          <img src="images/486.webp" alt="" loading="lazy" width="640" height="800">
        </div>
      </div>
    </div>
  </section>

  <section class="gallery-section" id="gallery" aria-labelledby="gallery-h">
    <div class="container">
      <div class="gallery-head">
        <div>
          <h2 id="gallery-h">The gallery</h2>
          <p class="sub">Filter by category or search by keyword — click any card to see the full prompt.</p>
        </div>
      </div>
      <div class="search-wrap">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
        <label class="sr-only" for="search">Search prompts</label>
        <input id="search" type="search" placeholder="Search 550 prompts — try “headshot”, “poster”, “sunset”…" autocomplete="off">
        <button class="search-clear" id="search-clear" type="button" hidden aria-label="Clear search">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>
        </button>
      </div>
      <div class="chip-row" id="chip-row" role="group" aria-label="Filter by category"></div>
      <p class="count-line" id="count-line" role="status"></p>
      <ul class="grid" id="grid"></ul>
      <div class="empty-state" id="empty-state" hidden>
        <h3>No prompts match that search</h3>
        <p>Try a broader keyword — or clear the category filter to browse all 550.</p>
        <button class="btn btn-sub" type="button" id="empty-reset">Clear search &amp; filters</button>
      </div>
      <div class="sentinel" id="sentinel" aria-hidden="true"></div>
      <p class="load-note" id="load-note" hidden>Scroll for more…</p>
      <noscript>
        <p style="font-weight:700;margin:18px 0 10px">All 550 prompts (enable JavaScript for search, copy buttons and the image viewer):</p>
        <ul class="noscript-list">{nos}</ul>
      </noscript>
    </div>
  </section>

  <section class="info-section tinted" id="how-to" aria-labelledby="howto-h">
    <div class="container">
      <div class="section-head">
        <span class="eyebrow">How to use</span>
        <h2 id="howto-h">Six steps from prompt to picture</h2>
        <p>These prompts are written as templates. The [brackets] are yours to fill — that is where your subject, product or story goes.</p>
      </div>
      <ul class="steps">{howto_steps}</ul>
    </div>
  </section>
{tail_html}
  <section class="cta-section" aria-labelledby="cta-h">
    <div class="container">
      <div class="cta-card">
        <h2 id="cta-h">Want more prompts like these?</h2>
        <p>I share practical AI playbooks, prompt collections and behind-the-scenes tests with my Substack readers — free, no spam, unsubscribe anytime.</p>
        <a class="btn" href="https://sifuyik.substack.com/subscribe" target="_blank" rel="noopener">Subscribe on Substack</a>
      </div>
    </div>
  </section>
</main>

<footer class="site-footer">
  <div class="container footer-inner">
    <p class="footer-note">550 ChatGPT Image Prompts · A free collection by Sifu Yik</p>
    <nav class="footer-nav" aria-label="Footer">
      <a href="https://sifuyik.substack.com" target="_blank" rel="noopener">Substack</a>
      <a href="https://animal.sifuyik.com" target="_blank" rel="noopener">Animal Prompt Library</a>
      <a href="#gallery">Back to top</a>
    </nav>
  </div>
</footer>

<div class="modal" id="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title" hidden>
  <div class="modal-backdrop"></div>
  <div class="modal-panel">
    <button class="modal-close" id="modal-close" type="button" aria-label="Close viewer">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg>
    </button>
    <div class="modal-media">
      <img id="modal-img" src="" alt="">
      <span class="modal-num" id="modal-num"></span>
    </div>
    <div class="modal-body">
      <p class="modal-cat" id="modal-cat"></p>
      <h3 class="modal-title" id="modal-title"></h3>
      <p class="modal-why" id="modal-why"></p>
      <p class="modal-prompt-label">The prompt</p>
      <blockquote class="modal-prompt" id="modal-prompt"></blockquote>
      <div class="modal-actions">
        <button class="btn btn-primary btn-sm" id="modal-copy" type="button">Copy prompt</button>
      </div>
      <p class="copy-note" id="copy-note" role="status" aria-live="polite"></p>
      <div class="modal-nav">
        <button id="modal-prev" type="button">← Previous</button>
        <span class="modal-count" id="modal-pos"></span>
        <button id="modal-next" type="button">Next →</button>
      </div>
    </div>
  </div>
</div>

<script src="data.js"></script>
<script src="assets/js/app.js"></script>
</body>
</html>
"""

os.makedirs(DIST, exist_ok=True)
with open(os.path.join(DIST, "index.html"), "w", encoding="utf-8") as f:
    f.write(page)

# README for the repo
readme = """# 550 ChatGPT Image Prompts — by Sifu Yik

A searchable gallery of 550 ChatGPT image prompts, each paired with a real example image.

Live: https://image.sifuyik.com

## Structure

- `index.html` — the site (generated by `tools/build_site.py`)
- `data.js` — prompt data inlined as `window.PROMPTS_DATA` (generated from the source markdown)
- `images/1.webp … 550.webp` — example images, 4:5 webp
- `assets/` — self-hosted fonts (Baloo 2, Nunito), CSS, JS

## Rebuild after editing prompts

1. Update the source markdown in the workspace (`550 Image Prompt/550-chatgpt-image-prompts.md`)
2. Run `python3 tools/parse_prompts.py` → regenerates `data/prompts.json`
3. Run `python3 tools/build_site.py` → regenerates `dist/`
4. Commit the contents of `dist/` to the repo root and push

The site is static — no server, no dependencies. Images lazy-load; the grid renders 36 cards at a time via IntersectionObserver.
"""
with open(os.path.join(DIST, "README.md"), "w", encoding="utf-8") as f:
    f.write(readme)

size = sum(os.path.getsize(os.path.join(dp, f)) for dp, dn, fn in os.walk(DIST) for f in fn)
print(f"dist size: {size/1024/1024:.1f} MB")
print("build complete")
