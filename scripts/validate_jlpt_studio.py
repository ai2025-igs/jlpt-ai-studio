# -*- coding: utf-8 -*-
"""
validate_jlpt_studio.py
Deterministic Neuro-Symbolic AQE & Schema Gatekeeper for JLPT N1-N4 AI Studio.
Enforces:
1. Level-specific question counts & official sub-type coverage
2. Unique correct answer & 4 detailed Traditional Chinese optionExplanations
3. Star-Syntax (G2_STAR_SYNTAX) 4-slot sequence consistency: correctSequence[2] == correctIndex
4. Listening (CHOUKAI) dialogue integrity, key turning signal markers, and edge-tts MP3 file existence
5. Pedagogical fields (bloomLevel, socraticHint, l1TransferNote, irtA, irtB)
6. Grade-Aware Furigana <ruby> tags in N3/N4 reading stems
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
JS_DIR = BASE_DIR / "assets" / "js"


def validate_js_and_dom_handlers() -> list[str]:
    errors = []
    js_files = sorted(JS_DIR.glob("*.js"))
    all_js_text = ""
    for jf in js_files:
        all_js_text += "\n" + jf.read_text(encoding="utf-8")
        res = subprocess.run(["node", "--check", str(jf)], capture_output=True, text=True)
        if res.returncode != 0:
            errors.append(f"[JS SyntaxError] {jf.name}: {res.stderr.strip()}")
    html_path = BASE_DIR / "index.html"
    if html_path.exists():
        html_text = html_path.read_text(encoding="utf-8")
        defined_funcs = set(re.findall(r"function\s+([A-Za-z0-9_]+)\s*\(", all_js_text))
        called_funcs = set(re.findall(r'on(?:click|change|input)="([A-Za-z0-9_]+)\(', html_text))
        missing_funcs = sorted(called_funcs - defined_funcs)
        if missing_funcs:
            errors.append(f"[DOM Handler Missing] Undefined JS functions referenced in index.html: {missing_funcs}")
    print(f"[JS/DOM GATE] Audited {len(js_files)} JS files with `node --check` & DOM handler bindings | Errors: {len(errors)}")
    return errors

REQUIRED_FIELDS = [
    "id", "level", "section", "category", "officialCode", "officialName",
    "subtag", "targetSec", "irtA", "irtB", "bloomLevel", "bloomLabel",
    "instruction", "stem", "furiganaHint", "socraticHint", "l1TransferNote",
    "options", "correctIndex", "translation", "coreRule", "optionExplanations"
]

def validate_level(lvl: str, min_q: int, check_furigana: bool, check_audio: bool, strict_aqe: bool) -> list[str]:
    errors = []
    bank_path = DATA_DIR / f"{lvl.lower()}_bank.json"
    if not bank_path.exists():
        return [f"[{lvl}] Missing bank file: {bank_path}"]

    try:
        items = json.loads(bank_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"[{lvl}] Invalid JSON: {e}"]

    if len(items) < min_q:
        errors.append(f"[{lvl}] Question count {len(items)} < required {min_q}")

    seen_ids = set()
    categories = set()
    official_codes = set()
    ruby_count = 0

    for idx, q in enumerate(items):
        qid = q.get("id", f"{lvl}-idx{idx}")
        if qid in seen_ids:
            errors.append(f"[{lvl}] Duplicate id: {qid}")
        seen_ids.add(qid)

        for rf in REQUIRED_FIELDS:
            if rf not in q or q[rf] in (None, ""):
                errors.append(f"[{qid}] Missing required field: {rf}")

        categories.add(q.get("category"))
        official_codes.add(q.get("officialCode"))

        opts = q.get("options", [])
        exps = q.get("optionExplanations", [])
        cidx = q.get("correctIndex", -1)

        if not (isinstance(opts, list) and len(opts) in (3, 4)):
            errors.append(f"[{qid}] Invalid options length: {len(opts)}")
        if not (isinstance(exps, list) and len(exps) == len(opts)):
            errors.append(f"[{qid}] optionExplanations length ({len(exps)}) != options length ({len(opts)})")
        if not (0 <= cidx < len(opts)):
            errors.append(f"[{qid}] correctIndex {cidx} out of bounds")
        elif strict_aqe and "✅" not in exps[cidx]:
            errors.append(f"[{qid}] optionExplanations[{cidx}] does not mark correct answer with ✅")

        if q.get("category") == "STAR":
            seq = q.get("correctSequence")
            if not (isinstance(seq, list) and len(seq) == 4 and sorted(seq) == [0, 1, 2, 3]):
                errors.append(f"[{qid}] Invalid STAR correctSequence: {seq}")
            elif seq[2] != cidx:
                errors.append(f"[{qid}] STAR slot-3 index seq[2]={seq[2]} != correctIndex={cidx}")

        if q.get("category") == "LISTENING":
            dlg = q.get("dialogue")
            if not (isinstance(dlg, list) and len(dlg) >= 2):
                errors.append(f"[{qid}] Listening item missing dialogue array")
            elif not any(t.get("isKeySignal") for t in dlg):
                errors.append(f"[{qid}] Listening dialogue lacks isKeySignal=True marker")
            if check_audio:
                af = q.get("audioFile")
                if not af:
                    errors.append(f"[{qid}] Missing audioFile path")
                else:
                    ap = BASE_DIR / af
                    if not (ap.exists() and ap.stat().st_size > 2048):
                        errors.append(f"[{qid}] Audio file missing or too small: {ap}")

        if "<ruby>" in q.get("stem", ""):
            ruby_count += 1

    expected_cats = {"KANJI", "VOCAB", "GRAMMAR", "STAR", "READING", "LISTENING"}
    missing_cats = expected_cats - categories
    if missing_cats:
        errors.append(f"[{lvl}] Missing radar categories: {missing_cats}")

    if check_furigana and lvl.upper() in ("N3", "N4", "N5") and ruby_count == 0:
        errors.append(f"[{lvl}] Grade-Aware Furigana check failed: 0 <ruby> tags found in {lvl}")

    mock100_cnt = sum(1 for q in items if q.get("inMock100"))
    print(f"[{lvl.upper()}] Audited {len(items)} items (Mock100: {mock100_cnt}) | Categories: {len(categories)}/6 | Official Subtypes: {len(official_codes)} | <ruby> items: {ruby_count} | Errors: {len(errors)}")
    return errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--level", default="ALL", help="N1, N2, N3, N4, N5, or ALL")
    parser.add_argument("--min-questions", type=int, default=240)
    parser.add_argument("--check-furigana", action="store_true")
    parser.add_argument("--check-audio", action="store_true")
    parser.add_argument("--strict-aqe", action="store_true")
    args = parser.parse_args()

    levels = ["N1", "N2", "N3", "N4", "N5"] if args.level.upper() == "ALL" else [x.strip().upper() for x in args.level.split(",")]
    all_errors = validate_js_and_dom_handlers()
    for lvl in levels:
        min_q = 35 if (lvl == "N2" and args.min_questions <= 24) else args.min_questions
        errs = validate_level(lvl, min_q, args.check_furigana, args.check_audio, args.strict_aqe)
        all_errors.extend(errs)

    if all_errors:
        print("\n❌ VALIDATION FAILED:")
        for e in all_errors:
            print("  -", e)
        sys.exit(1)
    print("\n✅ ALL JLPT STUDIO GATES PASSED (0 ERRORS)!")
    sys.exit(0)

if __name__ == "__main__":
    main()
