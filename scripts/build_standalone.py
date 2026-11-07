#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_standalone.py
1. Audits DOM IDs between index.html and assets/js/*.js (Zero Missing DOM ID Gate).
2. Compiles a 100% self-contained single-file HTML (embedding CSS, N1-N4 JSON banks, and JS)
   to both:
   - d:/MuseAcademy_50_25C16/jlpt-ai-studio/dist/jlpt_n1_n4_standalone_v3.html
   - R:/jlpt_n2_ai.html (Upgraded v3.0 standalone flagship)
"""

import json
import os
import re
import sys

ROOT = r"d:\MuseAcademy_50_25C16\jlpt-ai-studio"


def audit_dom_ids(html_text: str, js_texts: list[str]) -> list[str]:
    html_ids = set(re.findall(r'id="([^"]+)"', html_text))
    # Also dynamic IDs like lvlCount_N2, lvlBtn_N2, spdBtn085
    missing = []
    for js in js_texts:
        for m in re.finditer(r"getElementById\(['\"]([^'\"]+)['\"]\)", js):
            target_id = m.group(1)
            if "${" in target_id:
                continue
            if target_id not in html_ids:
                missing.append(target_id)
    return sorted(set(missing))


def main():
    index_path = os.path.join(ROOT, "index.html")
    css_path = os.path.join(ROOT, "assets", "css", "custom.css")
    js_files = [
        os.path.join(ROOT, "assets", "js", "psychometric.js"),
        os.path.join(ROOT, "assets", "js", "audio-engine.js"),
        os.path.join(ROOT, "assets", "js", "app.js"),
    ]

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    js_contents = []
    for p in js_files:
        with open(p, "r", encoding="utf-8") as f:
            js_contents.append(f.read())

    missing_ids = audit_dom_ids(html, js_contents)
    if missing_ids:
        print(f"ERROR: Missing DOM IDs in index.html: {missing_ids}")
        sys.exit(1)
    print("DOM ID Audit PASSED: 0 missing IDs between JS controllers and index.html.")

    banks = {}
    for lvl in ["N1", "N2", "N3", "N4"]:
        bpath = os.path.join(ROOT, "data", f"{lvl.lower()}_bank.json")
        with open(bpath, "r", encoding="utf-8") as f:
            banks[lvl] = json.load(f)

    # Inline CSS
    standalone_html = html.replace(
        '<link rel="stylesheet" href="assets/css/custom.css" />',
        f"<style>\n{css}\n</style>",
    )

    # Inline Embedded JSON Banks + JS Scripts
    banks_json_str = json.dumps(banks, ensure_ascii=False)
    combined_js = (
        f"window.EMBEDDED_JLPT_BANKS = {banks_json_str};\n\n"
        + "\n\n".join(js_contents)
    )

    script_tags = (
        '  <script src="assets/js/psychometric.js"></script>\n'
        '  <script src="assets/js/audio-engine.js"></script>\n'
        '  <script src="assets/js/app.js"></script>'
    )
    standalone_html = standalone_html.replace(
        script_tags, f"  <script>\n{combined_js}\n  </script>"
    )

    dist_dir = os.path.join(ROOT, "dist")
    os.makedirs(dist_dir, exist_ok=True)
    dist_path = os.path.join(dist_dir, "jlpt_n1_n4_standalone_v3.html")
    with open(dist_path, "w", encoding="utf-8") as f:
        f.write(standalone_html)
    print(f"Created standalone bundle: {dist_path} ({len(standalone_html):,} bytes)")

    r_path = r"R:\jlpt_n2_ai.html"
    if os.path.exists("R:\\"):
        with open(r_path, "w", encoding="utf-8") as f:
            f.write(standalone_html)
        print(f"Upgraded R:\\jlpt_n2_ai.html to v3.0 ({len(standalone_html):,} bytes)")


if __name__ == "__main__":
    main()
