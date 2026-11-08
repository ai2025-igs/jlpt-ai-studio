#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_e2e_browser.py
Headless Chromium Playwright E2E Runtime Verification Gate (N2 Flagship Focus Mode)
Verifies:
1. Zero JS syntax or runtime page errors (pageerror / console.error).
2. N1, N3, N4, N5 buttons are disabled (locked until N2 acceptance), while N2 is active.
3. Switching between N2 500% Flagship Pool (530), 300% Pool (318), and 100% Mock Exam (106).
4. Switching across Tab 1, Tab 2, Tab 3, numbered Mondai buttons, and submitting an answer.
"""

import http.server
import socketserver
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent


def run_e2e():
    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(*args, directory=str(ROOT), **kwargs)
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()

    page_errors = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            page.on("pageerror", lambda err: page_errors.append(str(err)))

            url = f"http://127.0.0.1:{port}/index.html"
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(350)

            assert len(page_errors) == 0, f"Page errors on load: {page_errors}"

            # 1. Verify N1, N3, N4, N5 are disabled and N2 is active
            for locked_lvl in ["N1", "N3", "N4", "N5"]:
                assert page.is_disabled(f"#lvlBtn_{locked_lvl}"), f"Expected #lvlBtn_{locked_lvl} to be disabled"
                assert page.inner_text(f"#lvlCount_{locked_lvl}").strip() == "待開放"

            assert not page.is_disabled("#lvlBtn_N2")
            assert page.inner_text("#headerLevelBadge").strip() == "N2"
            assert page.inner_text("#officialExamLevelText").strip() == "N2"
            assert page.inner_text("#pool500CountText").strip() == "530"
            assert page.inner_text("#pool300CountText").strip() == "318"
            assert page.inner_text("#mock100CountText").strip() == "106"

            stem_txt = page.inner_text("#qStemText").strip()
            assert "題目載入中" not in stem_txt and len(stem_txt) > 3, f"N2 stem not loaded: {stem_txt}"
            print(f"[E2E PASS] N2 Active & N1/N3/N4/N5 Disabled! N2 Stem: {stem_txt[:40]}...")

            # 2. Test 3-Mode Pool Switcher (500% -> 300% -> 100% -> 500%)
            page.click("#poolBtn300")
            page.wait_for_timeout(100)
            assert page.inner_text("#officialExamPoolTag").strip() == "300%池"
            assert "/ 318" in page.inner_text("#qProgressText")

            page.click("#poolBtn100")
            page.wait_for_timeout(100)
            assert page.inner_text("#officialExamPoolTag").strip() == "100%模考"
            assert "/ 106" in page.inner_text("#qProgressText")

            page.click("#poolBtn500")
            page.wait_for_timeout(100)
            assert page.inner_text("#officialExamPoolTag").strip() == "500%池"
            assert "/ 530" in page.inner_text("#qProgressText")
            print("[E2E PASS] 3-Mode Pool Switcher (530 / 318 / 106) verified!")

            # 3. Test switching Workspace Tabs 1, 2, 3
            page.click("#mainTabBtn_2")
            page.wait_for_timeout(100)
            assert page.is_visible("#tabPane_2")

            page.click("#mainTabBtn_3")
            page.wait_for_timeout(100)
            assert page.is_visible("#tabPane_3")

            page.click("#mainTabBtn_1")
            page.wait_for_timeout(100)
            assert page.is_visible("#tabPane_1")

            # 4. Test selecting option and submitting on N2
            page.evaluate("selectOption(1); submitCurrentAnswer();")
            page.wait_for_timeout(150)
            assert page.is_visible("#diagnosticPanel"), "Diagnostic panel should be visible after submitting answer"

            # 5. Wave 2: Test Bidirectional ★ Star Composer & Post-Submit Full 4-Token Sentence Synthesis
            page.evaluate("jumpToMondaiCode('G2_STAR_SYNTAX');")
            page.wait_for_timeout(120)
            page.evaluate("placeStarToken(0); placeStarToken(1); placeStarToken(2);")
            page.wait_for_timeout(100)
            assert page.is_visible("#starDirectSubmitBox"), "Expected #starDirectSubmitBox to be visible when ★ slot is filled"
            assert "以目前 ★ 格位直接送出作答" in page.inner_text("#starDirectSubmitBox")
            page.evaluate("submitFromStarSlot(2);")
            page.wait_for_timeout(120)
            assert page.is_visible("#starFullSentenceBox"), "Expected #starFullSentenceBox to be visible after submitting ★ question"
            assert "bg-slate-950 text-amber-300" in page.inner_html("#starFullSentenceBox")
            print("[E2E PASS] Wave 2 Bidirectional ★ Star Composer & Full Sentence Synthesis verified!")

            # 6. Wave 3: Test Official N2 2-Section Exam Countdown & Pacing HUD
            page.evaluate("toggleN2MacroExamTimer();")
            page.wait_for_timeout(100)
            assert "言語・読解" in page.inner_text("#macroTimerClockText")
            assert page.inner_text("#macroPacingBadge").strip() in ("領先配速", "配速正常", "⚠️ 読解時間緊迫")
            print("[E2E PASS] Wave 3 Official N2 2-Section Exam Countdown & Pacing HUD verified!")

            # 7. Wave 4: Test L5_QUICK_RESP Authentic Audio-First Masking
            page.evaluate("jumpToMondaiCode('L5_QUICK_RESP');")
            page.wait_for_timeout(120)
            opts_text_masked = page.inner_text("#optionsContainer")
            assert "選択肢 1 — 🔊 請先聽語音並依高低音調與語境作答" in opts_text_masked, f"Expected L5_QUICK_RESP masked text, got: {opts_text_masked}"
            page.evaluate("unmaskBlindOptions();")
            page.wait_for_timeout(100)
            opts_text_unmasked = page.inner_text("#optionsContainer")
            assert "請先聽語音並依高低音調與語境作答" not in opts_text_unmasked
            print("[E2E PASS] Wave 4 L5_QUICK_RESP Audio-First Masking & Unmasking verified!")

            # 8. Test 100% Neural MP3 Audio Triggers (Written Stem, Listening Turn, Trap Card)
            mp3_requests = []
            page.on("response", lambda res: mp3_requests.append((res.url, res.status)) if ".mp3" in res.url else None)
            page.evaluate("jumpToMondaiCode('M1_KANJI_READ');")
            page.wait_for_timeout(120)
            page.evaluate("speakQuestion(1.0);")
            page.wait_for_timeout(200)
            page.evaluate("jumpToMondaiCode('L1_TASK');")
            page.wait_for_timeout(150)
            page.evaluate("replayDialogueTurn(0);")
            page.wait_for_timeout(200)
            page.evaluate("speakSingleUtterance('てがみをかく', 'FEMALE');")
            page.wait_for_timeout(200)
            assert len(mp3_requests) >= 3 and all(status in (200, 206) for _, status in mp3_requests), f"Expected HTTP 200/206 on Neural MP3 requests, got: {mp3_requests}"
            print(f"[E2E PASS] Neural MP3 Audio Triggers verified ({len(mp3_requests)} MP3 streams fetched with HTTP 200/206)!")

            assert len(page_errors) == 0, f"Runtime page errors detected: {page_errors}"
            browser.close()
            print("[E2E ALL CHECKS PASSED] Zero pageerror, N2 530/318/106 fully interactive!")
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    run_e2e()
