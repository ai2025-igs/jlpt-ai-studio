#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
forge_jlpt_n2_cin_3videos.py
============================
End-to-End Sovereign Production & VQE Verification Engine for the 3 x 2.5-Minute (150.0s, 4,500 frames @ 30fps)
/vids_cin (CinematicRenderer) Introduction & User-Guide Videos for JLPT N2 AI Studio (N2 First).

Executes Nodes N2, N3, N4, N5, and N6 of D:/MuseAcademy_50_25C16/jlpt-ai-studio/plans/jlpt_n2_vids_cin_3videos.json:
  - N2: Capture 12 real 1920x1080 states of JLPT N2 AI Studio via Playwright Headless Chromium,
        overlay high-contrast callout HUD banners, and render 12 x 16-second 30fps Ken-Burns motion video plates.
  - N3 (Episode 1, 150.0s): jlpt_n2_intro_ep1_flagship_overview.mp4
        Theme: 【總綱首映篇】為什麼台灣學習者需要 JLPT N2 認知診斷平台？ (8 大教學理論 × 530/318/106 三層題庫 × 三大模式)
        Voice: zh-TW-YunJheNeural | BGM: 03_cinematic_epic_titans.mp3 (10.5% speech / 14.2% pause)
  - N4 (Episode 2, 150.0s): jlpt_n2_intro_ep2_tab1_walkthrough.mp4
        Theme: 【實戰操作篇】Tab 1 互動刷題、星號組裝、讀解標記與 286 軌純神經聽解完全指南
        Voice: zh-TW-HsiaoChenNeural | BGM: 08_quant_executive_pulse.mp3 (10.5% speech / 14.2% pause)
  - N5 (Episode 3, 150.0s): jlpt_n2_intro_ep3_irt_fsrs_mastery.mp4
        Theme: 【診斷與記憶複利篇】Tab 2 量尺預測、19分紅線防禦、合否通知書與 Tab 3 FSRS 百寶箱攻略
        Voice: zh-TW-YunJheNeural | BGM: 10_majestic_classical_violin.mp3 (10.5% speech / 14.2% pause)
  - N6: VQE G1–G5 Zero-Defect Multimedia Audit (-14.5 LUFS, 0 SRT overlap, HUD contrast > 12.0, exact 150.0s duration).
"""

from __future__ import annotations

import argparse
import concurrent.futures
import http.server
import json
import os
import shutil
import socketserver
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

JLPT_ROOT = Path("D:/MuseAcademy_50_25C16/jlpt-ai-studio")
VIDEOS_DIR = JLPT_ROOT / "videos"
OPENMONTAGE_ROOT = Path("D:/OpenMontage")
REMOTION_DIR = OPENMONTAGE_ROOT / "remotion-composer"
PUBLIC_STAGE_DIR = REMOTION_DIR / "public" / "igs_stage" / "jlpt_n2_cin"
OUTPUT_DIR = OPENMONTAGE_ROOT / "output"
RAMDISK_ROOT = Path("R:/OpenMontage_JLPT_N2_Cin")

sys.path.insert(0, str(OPENMONTAGE_ROOT))
sys.path.insert(0, str(OPENMONTAGE_ROOT / "scripts"))

from igs_forge_first3_mp4 import (
    _get_cjk_font,
    _sync_project_backlot,
    audit_and_improve_video,
    build_captions_and_srt,
    synthesize_mastered_audio,
)
from lib.checkpoint import init_project


def _annotate_screenshot(img_path: Path, badge_text: str, sub_text: str, highlight_box: tuple[int, int, int, int] | None = None) -> None:
    """Add a sleek top-right / bottom-left architectural callout pill and optional amber highlight frame to a 1920x1080 screenshot."""
    im = Image.open(img_path).convert("RGBA")
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    if highlight_box:
        x0, y0, x1, y1 = highlight_box
        draw.rounded_rectangle([x0, y0, x1, y1], radius=16, outline=(245, 158, 11, 235), width=6)
        draw.rounded_rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], radius=18, outline=(56, 189, 248, 160), width=2)

    f_title = _get_cjk_font(28, True)
    f_sub = _get_cjk_font(20, False)

    # Bottom-left floating HUD callout bar (positioned above Remotion caption zone y=880..1040)
    bx0, by0, bx1, by1 = 48, 745, 1020, 845
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=14, fill=(2, 6, 23, 225), outline=(243, 156, 66, 240), width=3)
    draw.rectangle([bx0, by0, bx0 + 12, by1], fill=(243, 156, 66, 255))
    draw.text((bx0 + 28, by0 + 14), badge_text, fill=(254, 243, 199, 255), font=f_title)
    draw.text((bx0 + 28, by0 + 54), sub_text, fill=(148, 163, 184, 255), font=f_sub)

    combined = Image.alpha_composite(im, overlay).convert("RGB")
    combined.save(img_path, format="PNG")


def capture_12_live_ui_screenshots_and_plates(force: bool = False) -> list[str]:
    """Capture 12 live 1920x1080 states of jlpt-ai-studio via Playwright and compile 12 x 16s 30fps motion plates."""
    PUBLIC_STAGE_DIR.mkdir(parents=True, exist_ok=True)
    shots_dir = RAMDISK_ROOT / "live_shots"
    shots_dir.mkdir(parents=True, exist_ok=True)

    plate_rels = [f"igs_stage/jlpt_n2_cin/plate_{i:02d}.mp4" for i in range(1, 13)]
    if not force and all((PUBLIC_STAGE_DIR / f"plate_{i:02d}.mp4").exists() and (PUBLIC_STAGE_DIR / f"plate_{i:02d}.mp4").stat().st_size > 80_000 for i in range(1, 13)):
        print("[N2 PLATE CACHE] All 12 live UI motion plates already exist and are valid.")
        return plate_rels

    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(*args, directory=str(JLPT_ROOT), **kwargs)
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()

    shot_paths: list[Path] = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 1080})
            url = f"http://127.0.0.1:{port}/index.html"
            page.goto(url, wait_until="networkidle")
            page.wait_for_timeout(400)

            # Shot 1: Tab 1 Overview — N2 Flagship 500% Pool (530 Questions) + Mondai 1 Kanji Reading
            s1 = shots_dir / "shot_01.png"
            page.screenshot(path=str(s1))
            _annotate_screenshot(
                s1,
                "🏆 JLPT N2 主力艦工作台 (1080P 零捲動雙欄架構)",
                "左欄 7 Cols 官方樣題測驗主控台 × 右欄 5 Cols 即時教學鷹架與認知診斷塢",
                (24, 130, 1115, 730),
            )
            shot_paths.append(s1)

            # Shot 2: 3-Mode Pool Switcher (100% Mock 106 vs 300% Pool 318 vs 500% Pool 530)
            page.click("#poolBtn100")
            page.wait_for_timeout(200)
            s2 = shots_dir / "shot_02.png"
            page.screenshot(path=str(s2))
            _annotate_screenshot(
                s2,
                "⏱️ 三階段題庫池切換：106 題正式模考 / 318 題鍛鍊池 / 530 題滿載池",
                "100% 對齊日本國際交流基金會 (JEES) 官方考綱配額與 105m+50m 雙節計時器",
                (410, 62, 1140, 122),
            )
            shot_paths.append(s2)
            page.click("#poolBtn500")
            page.wait_for_timeout(150)

            # Shot 3: Scaffolding Mode vs Exam Mode + Hint / Eliminate Option / Ruby Toggle
            page.evaluate("triggerSocraticHint(); eliminateOneDistractor();")
            page.wait_for_timeout(200)
            s3 = shots_dir / "shot_03.png"
            page.screenshot(path=str(s3))
            _annotate_screenshot(
                s3,
                "🌱 教學鷹架模式 vs. ⚔️ 考場實戰模式 (Sweller 認知負荷漸進撤除)",
                "支援分級 <ruby> 振假名開關、蘇格拉底不洩題引導提示、以及一鍵排除明顯誘答",
                (45, 250, 1090, 395),
            )
            shot_paths.append(s3)

            # Shot 4: Post-Answer Right Dock — Taiwan-Japan L1 Kanji Interference Lens & 4-Option Distractor Breakdown
            page.evaluate("selectOption(0); submitCurrentAnswer();")
            page.wait_for_timeout(250)
            s4 = shots_dir / "shot_04.png"
            page.screenshot(path=str(s4))
            _annotate_screenshot(
                s4,
                "🇹🇼⇄🇯🇵 台日漢字母語正負遷移透鏡 (Odlin L1 Transfer) & 誘答全解析",
                "提交答案瞬間原地展開：精準剖析清濁音、長短音、同形異義詞陷阱與 SRL 信心校準差",
                (1125, 130, 1895, 860),
            )
            shot_paths.append(s4)

            # Shot 5: N2-Exclusive Mondai 3 Word Formation (語形成)
            page.evaluate("jumpToMondaiCode('V3_WORD_FORM'); selectOption(1); submitCurrentAnswer();")
            page.wait_for_timeout(250)
            s5 = shots_dir / "shot_05.png"
            page.screenshot(path=str(s5))
            _annotate_screenshot(
                s5,
                "🧩 N2 獨有必考大題：問題3 語形成 (複合語・接頭接尾辞)",
                "系統性拆解 ～っぱなし、～がち、～だらけ、不～、～率 等 N2 核心構詞規律",
                (45, 140, 1105, 690),
            )
            shot_paths.append(s5)

            # Shot 6: Mondai 7 Star Arrangement (＿ ＿ ★ ＿) + First/Last Anchor Lock + Dependency Chain
            page.evaluate("jumpToMondaiCode('G2_STAR'); anchorStarFirstLastSlots(); selectOption(2); submitCurrentAnswer();")
            page.wait_for_timeout(250)
            s6 = shots_dir / "shot_06.png"
            page.screenshot(path=str(s6))
            _annotate_screenshot(
                s6,
                "⭐ 問題7 星號重組沙盒 (＿ ＿ ★ ＿) + 🔗 鎖定首尾錨點 + 語法接續鏈",
                "4 格互動排句沙盒搭配 [1 ➔ 2 ➔ ★3 ➔ 4] 前後接續形態圖解，徹底終結漢字跳讀猜意",
                (45, 340, 1105, 720),
            )
            shot_paths.append(s6)

            # Shot 7: Mondai 10/11 Dokkai Reading + Discourse Marker Highlighter (🖍️ 標記轉折與主張詞)
            page.evaluate("jumpToMondaiCode('R3_INTEGRATED'); highlightDiscourseMarkers();")
            page.wait_for_timeout(250)
            s7 = shots_dir / "shot_07.png"
            page.screenshot(path=str(s7))
            _annotate_screenshot(
                s7,
                "📖 問題11 A/B 兩文統合比較讀解 & 🖍️ 轉折主張詞雷達",
                "一鍵高亮 しかし、つまり、むしろ、～のではないだろうか 等作者核心主張信號",
                (45, 290, 1105, 680),
            )
            shot_paths.append(s7)

            # Shot 8: Mondai 15-19 Choukai Listening Console + 4-Step 答え方 + 286 Neural MP3s
            page.evaluate("jumpToMondaiCode('L1_TASK');")
            page.wait_for_timeout(250)
            s8 = shots_dir / "shot_08.png"
            page.screenshot(path=str(s8))
            _annotate_screenshot(
                s8,
                "🎧 聽解問題15–19：4 步 答え方 跳段精聽 & 286 首純神經雙聲道 MP3",
                "預渲染 KeitaNeural 男聲與 NanamiNeural 女聲，支援點擊任意對話氣泡 🔊 單句零延遲重播",
                (45, 250, 1105, 650),
            )
            shot_paths.append(s8)

            # Shot 9: Mondai 17 (Q3 Overview Comprehension) Poka-Yoke Blind Listening Shield
            page.evaluate("jumpToMondaiCode('L3_OVERVIEW');")
            page.wait_for_timeout(250)
            s9 = shots_dir / "shot_09.png"
            page.screenshot(path=str(s9))
            _annotate_screenshot(
                s9,
                "🙈 聽解問題17 概要理解：Poka-Yoke 防呆盲聽遮罩",
                "音訊播放期間自動鎖定選項或支援手動切換盲聽，防止視覺搶奪聽覺工作記憶",
                (45, 420, 1105, 720),
            )
            shot_paths.append(s9)

            # Shot 10: Tab 2 — 2PL-IRT Scaled Score (/180), 19/60 Cutoff Alert & 6D Cognitive Radar
            page.evaluate("switchWorkspaceTab(2); updateKPIsAndRadar(); updateIRTScoreBanner();")
            page.wait_for_timeout(350)
            s10 = shots_dir / "shot_10.png"
            page.screenshot(path=str(s10))
            _annotate_screenshot(
                s10,
                "📊 Tab 2：2PL-IRT 量尺分數推估 (/180) × 19/60 單科死亡紅線防禦",
                "即時換算言語知識、讀解、聽解三科量尺分數，搭配 6D 六角認知雷達與 AI 弱點處方箋",
                (30, 130, 1890, 735),
            )
            shot_paths.append(s10)

            # Shot 11: Tab 3 — FSRS v5 Spaced Repetition Queue + Full-Text Search + NotebookLM Podcast Exporter
            page.evaluate("switchWorkspaceTab(3); renderQuestionQueue();")
            page.wait_for_timeout(300)
            s11 = shots_dir / "shot_11.png"
            page.screenshot(path=str(s11))
            _annotate_screenshot(
                s11,
                "📋 Tab 3：FSRS v5 自由間隔重複排程 × 即時全文檢索 × NotebookLM 匯出",
                "自動追蹤高信心盲點題，一鍵匯出雙人對談 Podcast 學習包 (.md) 供通勤精聽複習",
                (30, 130, 1180, 735),
            )
            shot_paths.append(s11)

            # Shot 12: Tab 3 Reference Treasure Box — 23 Taiwan-Japan False Friends & Tokyo Pitch Accent [0][1][2] Cards
            page.evaluate("openTrapCardsModal();")
            page.wait_for_timeout(300)
            s12 = shots_dir / "shot_12.png"
            page.screenshot(path=str(s12))
            _annotate_screenshot(
                s12,
                "🎴 考綱百寶箱：23 張台日漢字假朋友 & 東京高低音調 [0][1][2] 純神經閃卡",
                "手紙、勉強、我慢、汽車、床、大家……每張閃卡皆綁定 NanamiNeural 真人預渲染發音",
                (180, 90, 1740, 735),
            )
            shot_paths.append(s12)

            browser.close()
    finally:
        httpd.shutdown()

    # Compile each 1920x1080 PNG into a 16-second 30fps Ken-Burns dynamic motion plate MP4
    def _encode_plate(idx_and_path: tuple[int, Path]) -> str:
        idx, png_p = idx_and_path
        out_mp4 = PUBLIC_STAGE_DIR / f"plate_{idx:02d}.mp4"
        # Alternate gentle zoom-in and zoom-out with high-contrast dark studio grade
        if idx % 2 == 1:
            zp = "zoompan=z='min(zoom+0.00018,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=480:s=1920x1080:fps=30"
        else:
            zp = "zoompan=z='if(eq(on,1),1.08,max(1.0,zoom-0.00018))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=480:s=1920x1080:fps=30"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-loop",
                "1",
                "-i",
                str(png_p),
                "-t",
                "16",
                "-vf",
                f"{zp},format=yuv420p",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "20",
                "-pix_fmt",
                "yuv420p",
                str(out_mp4),
            ],
            check=True,
            capture_output=True,
        )
        return f"igs_stage/jlpt_n2_cin/plate_{idx:02d}.mp4"

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(_encode_plate, enumerate(shot_paths, start=1)))

    print(f"[N2 PASS] Captured 12 live 1080P UI states and compiled {len(results)} motion video plates.")
    return results


def _render_cinematic_episode(
    proj_id: str,
    title: str,
    final_mp4: Path,
    srt_path: Path,
    duration_s: float,
    voice: str,
    bgm_track: str,
    segments: list[tuple[float, float, str]],
    scenes: list[dict[str, Any]],
    sfx_events: list[tuple[float, str, float]],
    force: bool = False,
) -> dict[str, Any]:
    t0 = time.time()
    if not force and final_mp4.exists() and final_mp4.stat().st_size > 2_000_000:
        return {"video": final_mp4.name, "path": str(final_mp4), "elapsed_sec": 0.0, "cached": True}

    init_project(
        proj_id,
        title=title,
        pipeline_type="cinematic",
        style_playbook="flat-motion-graphics",
    )
    work_dir = RAMDISK_ROOT / proj_id
    work_dir.mkdir(parents=True, exist_ok=True)
    PUBLIC_STAGE_DIR.mkdir(parents=True, exist_ok=True)

    captions = build_captions_and_srt(segments, srt_path)
    mastered_wav = synthesize_mastered_audio(
        segments,
        duration_s,
        work_dir,
        voice=voice,
        bgm_style=bgm_track,
        sfx_events=sfx_events,
    )
    stage_wav_name = f"{proj_id}_narration.wav"
    shutil.copy2(mastered_wav, PUBLIC_STAGE_DIR / stage_wav_name)

    props = {
        "titleFontSize": 66,
        "titleWidth": 1480,
        "signalLineCount": 20,
        "soundtrack": {
            "src": f"igs_stage/jlpt_n2_cin/{stage_wav_name}",
            "volume": 1.0,
            "fadeInSeconds": 0.2,
            "fadeOutSeconds": 0.6,
        },
        "captions": {
            "words": captions,
            "wordsPerPage": 6,
            "fontSize": 42,
            "color": "#F8FAFC",
            "highlightColor": "#F59E0B",
            "backgroundColor": "rgba(2, 6, 23, 0.88)",
        },
        "scenes": scenes,
    }

    props_path = work_dir / f"{proj_id}_props.json"
    props_path.write_text(json.dumps(props, indent=2, ensure_ascii=False), encoding="utf-8")

    raw_mp4 = work_dir / f"{proj_id}_raw.mp4"
    npx_cmd = shutil.which("npx.cmd") or shutil.which("npx") or "npx.cmd"
    subprocess.run(
        [
            npx_cmd,
            "remotion",
            "render",
            "src/index.tsx",
            "CinematicRenderer",
            str(raw_mp4),
            "--props",
            str(props_path),
            "--codec",
            "h264",
            "--concurrency",
            "4",
        ],
        cwd=REMOTION_DIR,
        check=True,
    )

    final_mp4.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(raw_mp4),
            "-i",
            str(mastered_wav),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(final_mp4),
        ],
        check=True,
        capture_output=True,
    )

    # Mirror to D:\OpenMontage\output\ as well
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(final_mp4, OUTPUT_DIR / final_mp4.name)
    shutil.copy2(srt_path, OUTPUT_DIR / srt_path.name)

    _sync_project_backlot(
        proj_id,
        title,
        "cinematic",
        "flat-motion-graphics",
        final_mp4,
        duration_s,
    )
    elapsed = round(time.time() - t0, 2)
    print(f"[RENDER PASS] {final_mp4.name} ({duration_s}s) rendered in {elapsed}s -> {final_mp4}")
    return {"video": final_mp4.name, "path": str(final_mp4), "elapsed_sec": elapsed, "cached": False}


def build_episode_1(plates: list[str], force: bool = False) -> dict[str, Any]:
    """Episode 1 (150.0s / 2m30s): Flagship Overview & 8 Pedagogical Theories (Why JLPT N2 First)."""
    proj_id = "jlpt_n2_intro_ep1_flagship_overview"
    final_mp4 = VIDEOS_DIR / f"{proj_id}.mp4"
    srt_path = VIDEOS_DIR / f"{proj_id}.srt"

    segments = [
        (0.0, 10.0, "歡迎來到 JLPT N2 互動式 AI 刷題與認知診斷系統！這是專為台灣高中生與日語自學者打造的超進階檢定通關平台。"),
        (10.0, 20.0, "為什麼我們需要一套超越傳統題庫的認知工程系統？因為台灣學習者擁有全球獨一無二的漢字母語雙刃劍效應。"),
        (20.0, 30.0, "我們看漢字猜意思極快，卻極易掉入三大落榜黑洞：第一是清濁音與連濁誤判，以及手紙、勉強、我慢等台日同形異義詞陷阱。"),
        (30.0, 40.0, "第二是習慣用漢字跳讀法，遇到問題七的星號排句題時，缺乏格助詞與用言接續形態的語法樹組裝能力。"),
        (40.0, 50.0, "第三則是進入聽解測驗時，一旦失去漢字視覺支撐，加上口語縮約音與轉折信號，極易觸發單科未滿十九分的淘汰紅線！"),
        (50.0, 60.0, "為此，本平台採取 N2 主力艦優先策略，百分之百對齊日本國際交流基金會官方考綱的全部十九個大題與計分規格。"),
        (60.0, 70.0, "在頂部題庫池切換器中，我們提供三種訓練規模：第一是完整一百零六題、嚴格計時一百五十五分鐘的百分之百正式模擬考。"),
        (70.0, 80.0, "第二是三百一十八題的三倍速核心鍛鍊池；第三則是高達五百三十題的百分之五百旗艦滿載題庫池，徹底消除考場陌生感！"),
        (80.0, 90.0, "針對一零八零 P 桌機黃金視窗，系統首創零捲動三分頁架構：分頁一將左側七欄官方樣題主控台，與右側五欄即時診斷塢完美並排。"),
        (90.0, 100.0, "分頁二搭載雙參數項目反應理論，即時推估一百八十分制量尺分數與六維度認知雷達；分頁三則整合自由間隔重複排程與考綱百寶箱。"),
        (100.0, 110.0, "更關鍵的是，系統將八大教育心理學理論直接編譯為互動按鈕：您可以隨時一鍵切換教學鷹架模式與考場實戰模式。"),
        (110.0, 120.0, "在教學鷹架模式下，系統提供分級振假名標註、蘇格拉底不洩題引導提示，以及一鍵排除一個明顯誘答選項，降低初期認知負荷。"),
        (120.0, 130.0, "當您準備好挑戰極限，切換至考場實戰模式，系統將隱藏所有輔助提示並啟動盲聽遮罩，百分之百還原真實考場高壓節奏。"),
        (130.0, 140.0, "全站更預先渲染兩百八十六首微軟純神經男女雙聲道日語音檔，並支援單一 HTML 離線封裝與自攜金鑰安全艙。"),
        (140.0, 150.0, "從漢字母語正負遷移到精準量尺預測，立即啟動 JLPT N2 AI Studio，開啟您的高分合格之路！"),
    ]

    scenes = [
        {"id": "ep1-s01", "kind": "title", "startSeconds": 0, "durationSeconds": 6, "text": "JLPT N2 AI STUDIO v4.3\nSOVEREIGN COGNITIVE EXAM FORGE", "accent": "#F59E0B", "intensity": 1.25, "backgroundSrc": plates[0], "variant": "plate"},
        {"id": "ep1-s02", "kind": "video", "startSeconds": 6, "durationSeconds": 10, "src": plates[0], "tone": "cold", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep1-s03", "kind": "title", "startSeconds": 16, "durationSeconds": 6, "text": "L1 KANJI DUAL-TRANSFER PARADOX\n3 FATAL BLINDSPOTS OF TAIWAN LEARNERS", "accent": "#38BDF8", "intensity": 1.2, "backgroundSrc": plates[3], "variant": "plate"},
        {"id": "ep1-s04", "kind": "video", "startSeconds": 22, "durationSeconds": 14, "src": plates[3], "tone": "steel", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep1-s05", "kind": "video", "startSeconds": 36, "durationSeconds": 14, "src": plates[5], "tone": "cold", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep1-s06", "kind": "title", "startSeconds": 50, "durationSeconds": 6, "text": "N2 FLAGSHIP FOCUS MODE\n106 MOCK · 318 DRILL · 530 FULL POOL", "accent": "#F59E0B", "intensity": 1.25, "backgroundSrc": plates[1], "variant": "plate"},
        {"id": "ep1-s07", "kind": "video", "startSeconds": 56, "durationSeconds": 12, "src": plates[1], "tone": "cold", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep1-s08", "kind": "video", "startSeconds": 68, "durationSeconds": 12, "src": plates[4], "tone": "steel", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep1-s09", "kind": "title", "startSeconds": 80, "durationSeconds": 6, "text": "1080P ZERO-SCROLL 3-TAB CONSOLE\nOPERATE MODE × DIAGNOSTIC DOCK", "accent": "#34D399", "intensity": 1.2, "backgroundSrc": plates[9], "variant": "plate"},
        {"id": "ep1-s10", "kind": "video", "startSeconds": 86, "durationSeconds": 14, "src": plates[9], "tone": "cold", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep1-s11", "kind": "title", "startSeconds": 100, "durationSeconds": 6, "text": "8 PEDAGOGICAL THEORIES COMPILED\nSCAFFOLDING MODE VS. EXAM MODE", "accent": "#A78BFA", "intensity": 1.2, "backgroundSrc": plates[2], "variant": "plate"},
        {"id": "ep1-s12", "kind": "video", "startSeconds": 106, "durationSeconds": 12, "src": plates[2], "tone": "steel", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep1-s13", "kind": "video", "startSeconds": 118, "durationSeconds": 12, "src": plates[7], "tone": "cold", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep1-s14", "kind": "video", "startSeconds": 130, "durationSeconds": 12, "src": plates[11], "tone": "steel", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep1-s15", "kind": "title", "startSeconds": 142, "durationSeconds": 8, "text": "JLPT N2 AI STUDIO\nBEYOND 100% MASTERY STARTS NOW", "accent": "#F59E0B", "intensity": 1.3, "backgroundSrc": plates[0], "variant": "plate"},
    ]

    sfx = [
        (0.1, "impact-bass-1.mp3", 0.40),
        (16.0, "whoosh-cinematic.mp3", 0.35),
        (50.0, "impact-bass-2.mp3", 0.38),
        (80.0, "whoosh-short.mp3", 0.32),
        (100.0, "riser.mp3", 0.34),
        (142.0, "sparkle.mp3", 0.38),
    ]

    return _render_cinematic_episode(
        proj_id=proj_id,
        title="Ep.1: JLPT N2 AI Studio Flagship Overview & 8 Pedagogical Theories (2m30s)",
        final_mp4=final_mp4,
        srt_path=srt_path,
        duration_s=150.0,
        voice="zh-TW-YunJheNeural",
        bgm_track="03_cinematic_epic_titans.mp3",
        segments=segments,
        scenes=scenes,
        sfx_events=sfx,
        force=force,
    )


def build_episode_2(plates: list[str], force: bool = False) -> dict[str, Any]:
    """Episode 2 (150.0s / 2m30s): Tab 1 Interactive Hands-On Walkthrough (Mondai 1-19, Star Sandbox & 286 Neural MP3s)."""
    proj_id = "jlpt_n2_intro_ep2_tab1_walkthrough"
    final_mp4 = VIDEOS_DIR / f"{proj_id}.mp4"
    srt_path = VIDEOS_DIR / f"{proj_id}.srt"

    segments = [
        (0.0, 10.0, "歡迎來到第二集：分頁一實戰操作完全指南！接下來兩分半鐘，我們將手把手帶您掌握十九個官方大題的解題神器。"),
        (10.0, 20.0, "進入分頁一左側主控台，頂部雙層號碼列完美復刻官方樣題介面：第一至十四號為筆試大題，第十五至十九號為聽解大題。"),
        (20.0, 30.0, "點擊任一題號或右側藍色問號按鈕，即可秒速切換大題並查看官方答え方作答指引；下方則提供筆試與聽解獨立倒數計時器。"),
        (30.0, 40.0, "在選出答案前，請務必先設定作答信心度：從百分之二十五猜測到百分之百確信，系統會依此精準揪出您的高信心盲點！"),
        (40.0, 50.0, "面對言語知識題，特別是 N2 獨有的問題三語形成，您可以點擊提示按鈕獲取構詞線索，或點擊朗讀聽取無重複假名的純神經發音。"),
        (50.0, 60.0, "來到台灣考生最頭痛的問題七星號排句題：您只需點擊下方四個語塊膠囊，就能在四格互動沙盒中自由組裝句子。"),
        (60.0, 70.0, "若一時卡關，點擊鎖定首尾錨點按鈕，系統會自動幫您填妥第一格與第四格，讓您專注攻克中間星號位置的助詞接續關係！"),
        (70.0, 80.0, "按下解答與診斷後，右側診斷塢會零捲動原地展開：呈現完整的語法接續鏈圖解、台日漢字正負遷移透鏡，以及四個選項的誘答剖析。"),
        (80.0, 90.0, "進入問題十至十三的讀解測驗，面對長篇社論與 A B 兩文統合比較，點擊標記轉折與主張詞按鈕，即可高亮所有關鍵邏輯信號。"),
        (90.0, 100.0, "像是逆接的しかし、總結的つまり，以及表露作者核心立場的のではないだろうか瞬間一目了然，大幅提升長文定位速度！"),
        (100.0, 110.0, "切換至問題十五至十九的聽解大題，系統內建與真實考場完全一致的八百八十赫茲雙音考場鐘聲，以及四步驟互動精聽綠框。"),
        (110.0, 120.0, "點擊步驟一至步驟四，音軌會精準跳轉至情境導入、男女對話本文、最終提問與作答停頓；問題十七更配備防呆盲聽遮罩！"),
        (120.0, 130.0, "為徹底解決手機瀏覽器機械音問題，我們預先合成了兩百八十六首微軟純神經雙聲道音檔：男聲 Keita 與女聲 Nanami 自然對話。"),
        (130.0, 140.0, "在檢討聽解時，您甚至能直接點擊對話腳本中的任何一句台詞，零延遲單句重播該名角色的純神經原音，直到完全聽懂縮約音為止！"),
        (140.0, 150.0, "最後，別忘了善用全鍵盤熱鍵：數字鍵一到四選答案、Enter 批改、R 朗讀、H 提示、F 標記待查，讓刷題效率翻倍躍升！"),
    ]

    scenes = [
        {"id": "ep2-s01", "kind": "title", "startSeconds": 0, "durationSeconds": 6, "text": "EPISODE 2 · TAB 1 WALKTHROUGH\n19 OFFICIAL MONDAI & NEURAL AUDIO", "accent": "#38BDF8", "intensity": 1.25, "backgroundSrc": plates[0], "variant": "plate"},
        {"id": "ep2-s02", "kind": "video", "startSeconds": 6, "durationSeconds": 14, "src": plates[0], "tone": "cold", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep2-s03", "kind": "video", "startSeconds": 20, "durationSeconds": 14, "src": plates[1], "tone": "steel", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep2-s04", "kind": "video", "startSeconds": 34, "durationSeconds": 14, "src": plates[2], "tone": "cold", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep2-s05", "kind": "title", "startSeconds": 48, "durationSeconds": 6, "text": "MONDAI 7 STAR SANDBOX (＿ ＿ ★ ＿)\nANCHOR LOCK & DEPENDENCY CHAIN", "accent": "#F59E0B", "intensity": 1.25, "backgroundSrc": plates[5], "variant": "plate"},
        {"id": "ep2-s06", "kind": "video", "startSeconds": 54, "durationSeconds": 16, "src": plates[5], "tone": "cold", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep2-s07", "kind": "video", "startSeconds": 70, "durationSeconds": 10, "src": plates[3], "tone": "steel", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep2-s08", "kind": "title", "startSeconds": 80, "durationSeconds": 5, "text": "DOKKAI DISCOURSE HIGHLIGHTER\nA/B INTEGRATED READING RADAR", "accent": "#34D399", "intensity": 1.2, "backgroundSrc": plates[6], "variant": "plate"},
        {"id": "ep2-s09", "kind": "video", "startSeconds": 85, "durationSeconds": 15, "src": plates[6], "tone": "cold", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep2-s10", "kind": "title", "startSeconds": 100, "durationSeconds": 6, "text": "286 PURE NEURAL MP3 TRACKS\n4-STEP CHOUKAI & SINGLE-TURN REPLAY", "accent": "#A78BFA", "intensity": 1.25, "backgroundSrc": plates[7], "variant": "plate"},
        {"id": "ep2-s11", "kind": "video", "startSeconds": 106, "durationSeconds": 14, "src": plates[7], "tone": "steel", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep2-s12", "kind": "video", "startSeconds": 120, "durationSeconds": 12, "src": plates[8], "tone": "cold", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep2-s13", "kind": "video", "startSeconds": 132, "durationSeconds": 10, "src": plates[4], "tone": "steel", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep2-s14", "kind": "title", "startSeconds": 142, "durationSeconds": 8, "text": "KEYBOARD SHORTCUT VELOCITY\n1-4 · ENTER · R · H · F", "accent": "#38BDF8", "intensity": 1.3, "backgroundSrc": plates[0], "variant": "plate"},
    ]

    sfx = [
        (0.1, "whoosh-cinematic.mp3", 0.38),
        (20.0, "click.mp3", 0.34),
        (48.0, "impact-bass-1.mp3", 0.38),
        (70.0, "chime.mp3", 0.34),
        (80.0, "whoosh-short.mp3", 0.32),
        (100.0, "riser.mp3", 0.35),
        (142.0, "sparkle.mp3", 0.36),
    ]

    return _render_cinematic_episode(
        proj_id=proj_id,
        title="Ep.2: JLPT N2 Tab 1 Interactive Hands-On Walkthrough & 286 Neural MP3s (2m30s)",
        final_mp4=final_mp4,
        srt_path=srt_path,
        duration_s=150.0,
        voice="zh-TW-HsiaoChenNeural",
        bgm_track="08_quant_executive_pulse.mp3",
        segments=segments,
        scenes=scenes,
        sfx_events=sfx,
        force=force,
    )


def build_episode_3(plates: list[str], force: bool = False) -> dict[str, Any]:
    """Episode 3 (150.0s / 2m30s): Tab 2 2PL-IRT Diagnostics & Tab 3 FSRS v5 + 23 Trap Cards Mastery."""
    proj_id = "jlpt_n2_intro_ep3_irt_fsrs_mastery"
    final_mp4 = VIDEOS_DIR / f"{proj_id}.mp4"
    srt_path = VIDEOS_DIR / f"{proj_id}.srt"

    segments = [
        (0.0, 10.0, "歡迎來到第三集：分頁二量尺分數預測與分頁三記憶複利完全攻略！刷完題目後，如何確保考場上穩拿九十分以上且零單科淘汰？"),
        (10.0, 20.0, "點擊上方導覽列進入分頁二，系統採用與正式日檢同源的雙參數項目反應理論，根據每道題目的難度與鑑別度即時更新能力值。"),
        (20.0, 30.0, "畫面頂部清晰呈現預估總分與三科獨立量尺分數：N2 合格門檻為總分九十分，且言語知識、讀解、聽解三科皆須達到十九分以上！"),
        (30.0, 40.0, "一旦任一科目預估低於二十二分，系統會立即亮起十九分死亡紅線警報，並在抽題時自動提高該弱項大題的出現權重。"),
        (40.0, 50.0, "右側六維度認知雷達圖與後設認知校準矩陣，能幫您一眼看穿哪些題型屬於高信心卻答錯的致命盲點，點擊處方箋即可啟動專項特訓。"),
        (50.0, 60.0, "完成模擬考後，點擊列印官方格式合否結果通知書，系統會立即生成包含三科量尺分數、百分位排名與診斷評語的正式成績單供存檔！"),
        (60.0, 70.0, "接著切換至分頁三：這是讓學習效果產生長期複利的自由間隔重複排程中心與考綱百寶箱。"),
        (70.0, 80.0, "系統會依據您的作答表現與信心度，自動計算每道題目的記憶穩定度與下次複習時間，將錯題排入十分鐘、一天、三天與十四天佇列。"),
        (80.0, 90.0, "需要針對特定語法或單字做橫向複習嗎？在題庫即時全文檢索框輸入關鍵字，五百三十道 N2 題目瞬間完成毫秒級過濾，一點即跳轉！"),
        (90.0, 100.0, "更棒的是，點擊下載 NotebookLM 雙人 Podcast 學習包，系統會將您的錯題與高信心盲點自動編譯為結構化 Markdown 講義。"),
        (100.0, 110.0, "您只需將該檔案上傳至 Google NotebookLM，即可一鍵生成男女雙主持人深度對談音檔，在搭車通勤途中輕鬆攻克個人弱點！"),
        (110.0, 120.0, "分頁三下方更內建台灣考生專屬的考綱百寶箱：完整收錄五段與上下一段動詞活用表、十六組自動詞與他動詞黃金配對。"),
        (120.0, 130.0, "在敬語與授受表現專區，透過視覺化恩惠方向箭頭與純神經發音示範，徹底釐清てあげる、てくださる與ていただく的視點差異。"),
        (130.0, 140.0, "還有二十三張台日漢字假朋友與東京高低音調閃卡，從手紙、勉強到おざなり，每張卡片都能點擊朗讀，矯正發音與詞義負遷移！"),
        (140.0, 150.0, "結合頂部待查專項複習、JSON 跨裝置進度備份與 Google 試算表同步，祝您旗開得勝，高分制霸 JLPT N2 日文檢定！"),
    ]

    scenes = [
        {"id": "ep3-s01", "kind": "title", "startSeconds": 0, "durationSeconds": 6, "text": "EPISODE 3 · TAB 2 & TAB 3 MASTERY\n2PL-IRT SCALED SCORE & FSRS v5", "accent": "#F59E0B", "intensity": 1.25, "backgroundSrc": plates[9], "variant": "plate"},
        {"id": "ep3-s02", "kind": "video", "startSeconds": 6, "durationSeconds": 14, "src": plates[9], "tone": "cold", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep3-s03", "kind": "title", "startSeconds": 20, "durationSeconds": 6, "text": "19 / 60 SECTIONAL CUTOFF GUARD\n6D COGNITIVE RADAR & SCORE REPORT", "accent": "#38BDF8", "intensity": 1.2, "backgroundSrc": plates[9], "variant": "plate"},
        {"id": "ep3-s04", "kind": "video", "startSeconds": 26, "durationSeconds": 18, "src": plates[9], "tone": "steel", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep3-s05", "kind": "video", "startSeconds": 44, "durationSeconds": 16, "src": plates[3], "tone": "cold", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep3-s06", "kind": "title", "startSeconds": 60, "durationSeconds": 6, "text": "TAB 3 · FSRS v5 SPACED REPETITION\nINSTANT FULL-TEXT SEARCH & PODCAST", "accent": "#34D399", "intensity": 1.25, "backgroundSrc": plates[10], "variant": "plate"},
        {"id": "ep3-s07", "kind": "video", "startSeconds": 66, "durationSeconds": 18, "src": plates[10], "tone": "cold", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep3-s08", "kind": "video", "startSeconds": 84, "durationSeconds": 18, "src": plates[10], "tone": "steel", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep3-s09", "kind": "title", "startSeconds": 102, "durationSeconds": 6, "text": "23 KANJI FALSE-FRIEND FLASHCARDS\nTOKYO PITCH ACCENT & KEIGO ARROWS", "accent": "#A78BFA", "intensity": 1.25, "backgroundSrc": plates[11], "variant": "plate"},
        {"id": "ep3-s10", "kind": "video", "startSeconds": 108, "durationSeconds": 18, "src": plates[11], "tone": "cold", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep3-s11", "kind": "video", "startSeconds": 126, "durationSeconds": 16, "src": plates[11], "tone": "steel", "filter": "contrast(1.06) saturate(1.02) brightness(0.95)"},
        {"id": "ep3-s12", "kind": "title", "startSeconds": 142, "durationSeconds": 8, "text": "PASS JLPT N2 WITH CERTAINTY\nai2025-igs.github.io/jlpt-ai-studio", "accent": "#F59E0B", "intensity": 1.3, "backgroundSrc": plates[0], "variant": "plate"},
    ]

    sfx = [
        (0.1, "impact-bass-1.mp3", 0.38),
        (20.0, "whoosh-cinematic.mp3", 0.35),
        (60.0, "chime.mp3", 0.34),
        (102.0, "riser.mp3", 0.34),
        (142.0, "sparkle.mp3", 0.38),
    ]

    return _render_cinematic_episode(
        proj_id=proj_id,
        title="Ep.3: JLPT N2 Tab 2 2PL-IRT Diagnostics & Tab 3 FSRS Mastery Guide (2m30s)",
        final_mp4=final_mp4,
        srt_path=srt_path,
        duration_s=150.0,
        voice="zh-TW-YunJheNeural",
        bgm_track="10_majestic_classical_violin.mp3",
        segments=segments,
        scenes=scenes,
        sfx_events=sfx,
        force=force,
    )


def run_vqe_audit_all3() -> dict[str, Any]:
    specs = [
        (
            VIDEOS_DIR / "jlpt_n2_intro_ep1_flagship_overview.mp4",
            VIDEOS_DIR / "jlpt_n2_intro_ep1_flagship_overview.srt",
            150.0,
        ),
        (
            VIDEOS_DIR / "jlpt_n2_intro_ep2_tab1_walkthrough.mp4",
            VIDEOS_DIR / "jlpt_n2_intro_ep2_tab1_walkthrough.srt",
            150.0,
        ),
        (
            VIDEOS_DIR / "jlpt_n2_intro_ep3_irt_fsrs_mastery.mp4",
            VIDEOS_DIR / "jlpt_n2_intro_ep3_irt_fsrs_mastery.srt",
            150.0,
        ),
    ]
    audits = []
    for mp4_p, srt_p, target_dur in specs:
        assert mp4_p.exists(), f"Missing MP4: {mp4_p}"
        assert srt_p.exists(), f"Missing SRT: {srt_p}"
        res = audit_and_improve_video(mp4_p, srt_p, target_dur)
        for gate_name, status in res["vqe_gates"].items():
            assert status == "PASS", f"VQE Gate {gate_name} failed on {mp4_p.name}: {res}"
        audits.append(res)

    report = {
        "status": "ALL_3_VIDEOS_VQE_PASS",
        "videos_dir": str(VIDEOS_DIR),
        "openmontage_mirror_dir": str(OUTPUT_DIR),
        "bgm_gain_contract": {"speech_gain": 0.105, "pause_gain": 0.142, "band": "10% - 15%"},
        "audits": audits,
    }
    report_path = VIDEOS_DIR / "vqe_audit_report_3videos.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Forge 3 x 2.5-Minute (150s) /vids_cin Introduction Videos for JLPT N2 AI Studio")
    parser.add_argument("--episode", type=int, choices=[1, 2, 3], help="Render specific episode (1, 2, or 3)")
    parser.add_argument("--plates-only", action="store_true", help="Only capture 12 live Playwright UI states and build motion plates")
    parser.add_argument("--audit-only", action="store_true", help="Run VQE G1-G5 audit on existing 3 MP4s")
    parser.add_argument("--force", action="store_true", help="Force re-render even if cached")
    args = parser.parse_args()

    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    RAMDISK_ROOT.mkdir(parents=True, exist_ok=True)

    if args.audit_only:
        rep = run_vqe_audit_all3()
        print(json.dumps(rep, indent=2, ensure_ascii=False))
        return 0

    plates = capture_12_live_ui_screenshots_and_plates(force=args.force)
    if args.plates_only:
        print(json.dumps({"plates": plates}, indent=2, ensure_ascii=False))
        return 0

    results = []
    if args.episode == 1:
        results.append(build_episode_1(plates, force=args.force))
    elif args.episode == 2:
        results.append(build_episode_2(plates, force=args.force))
    elif args.episode == 3:
        results.append(build_episode_3(plates, force=args.force))
    else:
        results.append(build_episode_1(plates, force=args.force))
        results.append(build_episode_2(plates, force=args.force))
        results.append(build_episode_3(plates, force=args.force))

    rep = run_vqe_audit_all3()
    rep["production_results"] = results

    # Clean intermediate RAMDisk workdir while keeping public stage plates
    if RAMDISK_ROOT.exists():
        shutil.rmtree(RAMDISK_ROOT, ignore_errors=True)

    print(json.dumps(rep, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
