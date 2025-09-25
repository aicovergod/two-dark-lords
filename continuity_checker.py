# continuity_checker.py
import json, re, sys, glob, os
from datetime import datetime, timezone

CANON_PATH = os.path.join("BIBLE","canon.json")

def load_canon():
    with open(CANON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_metas():
    metas = []
    for fn in glob.glob(os.path.join("BIBLE","books","**","*.meta.json"), recursive=True):
        with open(fn, "r", encoding="utf-8") as f:
            j = json.load(f)
            j["_file"] = fn
            metas.append(j)
    return metas

def parse_timestamp(ts):
    # Support 'Z' suffix or +00:00
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts)

def check_timeline(metas):
    ok = True
    metas_sorted = sorted(metas, key=lambda m: parse_timestamp(m["timestamp_utc"]))
    prev = None
    for m in metas_sorted:
        cur = parse_timestamp(m["timestamp_utc"])
        if prev and cur < prev:
            print(f"::error file={m['_file']}::Timeline conflict: {m['timestamp_utc']} precedes earlier chapter")
            ok = False
        prev = cur
    return ok

def check_anchors(metas, canon):
    ok = True
    # Only track Harry Potter for now
    anchor = canon.get("anchor_start",{}).get("Harry Potter", 3)
    for m in sorted(metas, key=lambda x: parse_timestamp(x["timestamp_utc"])):
        delta = 0
        if "anchors_changed" in m and "Harry" in m["anchors_changed"]:
            delta = m["anchors_changed"]["Harry"]
        anchor += delta
        if anchor < 0 or anchor > 5:
            print(f"::error file={m['_file']}::Anchor out of bounds ({anchor}) after this chapter")
            ok = False
    return ok

def normalize_words(text):
    # Grab capitalized sequences likely to be names/places
    tokens = re.findall(r"[A-Z][a-z]+(?:\\s+[A-Z][a-z]+)*", text)
    # Remove common sentence starts
    blacklist = {"The","A","An","I","We","He","She","They","Chapter"}
    return [t for t in tokens if t.split()[0] not in blacklist]

def check_undefined_names(chapter_files, canon):
    ok = True
    known = set(canon["characters"]) | set(canon["locations"]) | {"Harry","Voldemort"}
    for fn in chapter_files:
        with open(fn, "r", encoding="utf-8") as f:
            text = f.read()
        found = set(normalize_words(text))
        unknown = {w for w in found if w not in known}
        # Heuristic: ignore words that are all-caps acronyms already listed
        unknown = {u for u in unknown if u.upper() == u and u not in known} | {u for u in unknown if u.upper() != u}
        # Allow small set of generic capitalized words
        whitelist = {"London","Thames","January","February","March","April","May","June","July","August","September","October","November","December"}
        unknown = {u for u in unknown if u not in whitelist}
        if unknown:
            print(f"::warning file={fn}::Potential undefined names/places: {sorted(unknown)}")
    return ok

def collect_chapter_files():
    files = glob.glob(os.path.join("BIBLE","books","**","ch*.md"), recursive=True)
    return files

def check_ability_scales(metas, canon):
    ok = True
    abilities = canon.get("abilities", {})
    for m in metas:
        book = int(m.get("book", 0))
        for use in m.get("power_usage", []):
            name = use.get("ability")
            scale = use.get("scale","local")
            if name not in abilities:
                print(f"::warning file={m['_file']}::Ability '{name}' not in canon.json abilities list")
                continue
            rule = abilities[name]
            if book < rule["book_min"] or scale not in rule["allowed_scales"]:
                print(f"::error file={m['_file']}::Ability '{name}' at scale '{scale}' not allowed in book {book} (min {rule['book_min']}, allowed {rule['allowed_scales']})")
                ok = False
    return ok

def main():
    canon = load_canon()
    metas = load_metas()
    if not metas:
        print("::warning::No metadata files found. Skipping checks.")
        sys.exit(0)
    ok = True
    ok &= check_timeline(metas)
    ok &= check_anchors(metas, canon)
    ok &= check_ability_scales(metas, canon)
    chapter_files = collect_chapter_files()
    check_undefined_names(chapter_files, canon)
    sys.exit(0 if ok else 2)

if __name__ == "__main__":
    main()
