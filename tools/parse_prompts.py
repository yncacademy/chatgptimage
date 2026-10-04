#!/usr/bin/env python3
"""Parse 550-chatgpt-image-prompts.md into data/prompts.json for the site. v3"""
import json, re, sys, os

SRC = "/Users/apple/.openclaw-autoclaw/workspace/550 Image Prompt/550-chatgpt-image-prompts.md"
OUT = "/Users/apple/.openclaw-autoclaw/workspace/550-image-prompts-site/data/prompts.json"
IMG_DIR = "/Users/apple/.openclaw-autoclaw/workspace/550 Image Prompt/550 chatgpt image prompts "

text = open(SRC, encoding="utf-8").read()
lines = text.split("\n")

sections, cur, cur_item = [], None, None
pending_name, intro_lines, tail_lines = None, [], []
tail_mode = False
seen_550_done = False

def start_section(name):
    global cur, pending_name
    pending_name = None
    cur = {"name": name, "items": []}
    sections.append(cur)

for raw in lines:
    line = raw.rstrip()
    if line.startswith("```"):
        continue
    if tail_mode:
        if line.strip():
            tail_lines.append(line.strip())
        continue
    if line.startswith("### "):
        header = line[4:].strip()
        mnum = re.match(r"^(\d+)\.\s*(.+)$", header)
        if not mnum:
            print("BAD HEADER:", header, file=sys.stderr); continue
        if pending_name:
            start_section(pending_name)
        elif cur is None:
            start_section("Prompts")
        num, title = int(mnum.group(1)), mnum.group(2).strip()
        cur_item = {"num": num, "title": title, "prompt": "", "why": ""}
        cur["items"].append(cur_item)
        if num == 550:
            seen_550_done = False   # tail starts only after its why-line completes
    elif line.startswith("Prompt: "):
        if cur_item is not None:
            cur_item["prompt"] = line[len("Prompt: "):].strip()
    elif line.startswith("Why it works: "):
        if cur_item is not None:
            cur_item["why"] = line[len("Why it works: "):].strip()
    elif line.strip() == "":
        continue
    else:
        if cur_item is None:
            intro_lines.append(line.strip())      # before first item
        elif cur_item["num"] == 550 and cur_item["prompt"] and cur_item["why"]:
            tail_mode = True                      # tail content starts here
            tail_lines.append(line.strip())
        elif cur_item["prompt"] and cur_item["why"]:
            pending_name = line.strip()           # new section header
        elif cur_item["why"]:
            cur_item["why"] += " " + line.strip()
        else:
            cur_item["prompt"] += " " + line.strip()

# first section: rescue its name from the last short, non-sentence intro line
if sections and sections[0]["name"] == "Prompts":
    for ln in reversed(intro_lines):
        if len(ln) < 60 and not ln.endswith((".", "!", "?", ":", "cidas")):
            sections[0]["name"] = ln
            intro_lines.remove(ln)
            break

# ── tail parse: blocks split by emoji-headed lines ──────────────────────────
tail_blocks, tb = [], None
for ln in tail_lines:
    m = re.match(r"^(?:[\U0001F300-\U0001FAFF\u2700-\u27BF\u2600-\u26FF\u2705\u23F0\U0001F4A1\U0001F50D\U0001F680\u2728\u274C\u2757\U0001F4CC\U0001F3AF\U0001F4A5\u2B50\u2764\u2728]\s*)+(.+)$", ln)
    if m and len(m.group(1)) < 40 and not ln[0].isdigit():
        tb = {"title": m.group(1).strip(), "lines": []}
        tail_blocks.append(tb)
    else:
        if tb is None:
            tb = {"title": "", "lines": []}
            tail_blocks.append(tb)
        tb["lines"].append(ln)

# flatten: keep blocks with content; drop the social "Comment LINK" CTA line
tail_clean = []
for b in tail_blocks:
    ls = [l for l in b["lines"] if not re.match(r'^Comment "LINK"', l)]
    if b["title"] or ls:
        tail_clean.append({"title": b["title"], "lines": ls})

# ── sanity ───────────────────────────────────────────────────────────────────
total = sum(len(s["items"]) for s in sections)
print(f"sections(raw)={len(sections)} items={total}")
if total != 550:
    print("FATAL: item count != 550", file=sys.stderr); sys.exit(1)

bad = [i["num"] for s in sections for i in s["items"] if not i["prompt"] or not i["why"]]
if bad:
    print("WARNING: items missing prompt/why:", bad[:20], file=sys.stderr)

# merge same-name sections (author repeated category headers)
merged = []
for s in sections:
    if merged and merged[-1]["name"].lower() == s["name"].lower():
        merged[-1]["items"].extend(s["items"])
    else:
        merged.append(s)
print(f"sections(merged)={len(merged)}")

imgs = os.listdir(IMG_DIR)
img_by_num = {int(re.match(r"^(\d+)\.", f).group(1)): f for f in imgs if re.match(r"^(\d+)\.", f)}
print(f"images={len(img_by_num)}")
missing_img = [i["num"] for s in merged for i in s["items"] if i["num"] not in img_by_num]
if missing_img:
    print("WARNING: items missing images:", missing_img[:30], file=sys.stderr)

nums = [i["num"] for s in merged for i in s["items"]]
assert nums == list(range(1, 551)), "numbers not sequential 1..550!"

def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

for s in merged:
    print(f"  {len(s['items']):3d}  {s['name']}")

# intro how-to: the numbered 1.-6. steps before the first prompt
intro_howto = [l for l in intro_lines if re.match(r"^\d+\.\s", l)]
print(f"intro howto steps={len(intro_howto)}")

data = {
    "sections": [{"name": s["name"], "slug": slugify(s["name"]), "count": len(s["items"]),
                  "nums": [i["num"] for i in s["items"]]} for s in merged],
    "items": {str(i["num"]): {"t": i["title"], "p": i["prompt"], "w": i["why"],
                              "c": slugify(s["name"]), "img": f"images/{i['num']}.webp"}
              for s in merged for i in s["items"]},
    "tail": tail_clean,
    "intro_howto": intro_howto,
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
print(f"wrote {OUT} ({os.path.getsize(OUT)/1024:.0f} KB)")
print("tail blocks:", [b["title"] or "(untitled)" for b in tail_clean])
