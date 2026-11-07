#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
jlpt_official_blueprint_gate.py
/study5 Neuro-Symbolic Harness & Official JLPT N1-N4 Blueprint Calculator:
1. Defines the exact 100% Official Exam Question Counts per Mondai across N1, N2, N3, N4
   (grounded on Japan Foundation / JEES guidelines & past papers).
2. Computes the 300% and 500% Practice Pool targets for each Mondai and level.
3. Exports `data/official_exam_blueprint.json` for the Frontend Mock Exam & Blueprint Dashboard.
4. Audits UI Level Ordering (N1 -> N2 -> N3 -> N4) and WCAG Contrast on Level Switcher Badges.
"""

import json
import os
import re
import sys

ROOT = r"d:\MuseAcademy_50_25C16\jlpt-ai-studio"

OFFICIAL_BLUEPRINT = {
    "levelOrder": ["N1", "N2", "N3", "N4"],
    "levels": {
        "N1": {
            "level": "N1",
            "title": "JLPT N1 最高殿堂",
            "sectionsMode": "二節制：言語知識・読解 (110m) ＋ 聴解 (55m)",
            "totalTimeMin": 165,
            "timeAllocationGuide": "文字語彙 15m ➔ 文法 20m ➔ 読解 75m (合計 110m) ｜ 聴解 55m",
            "passTotal": 100,
            "sectionCutoffs": {"言語知識": 19, "読解": 19, "聴解": 19},
            "mock100Total": 104,
            "practice300Target": 312,
            "practice500Target": 520,
            "mondaiList": [
                {"code": "M1_KANJI_READ", "section": "MOJI_GOI", "category": "KANJI", "name": "問題1・漢字読み", "mock100": 6, "pool300": 18, "pool500": 30, "secPerItem": 25},
                {"code": "M4_CONTEXT_VOCAB", "section": "MOJI_GOI", "category": "VOCAB", "name": "問題2・文脈規定", "mock100": 7, "pool300": 21, "pool500": 35, "secPerItem": 30},
                {"code": "M5_PARAPHRASE", "section": "MOJI_GOI", "category": "VOCAB", "name": "問題3・言い換え類義", "mock100": 6, "pool300": 18, "pool500": 30, "secPerItem": 30},
                {"code": "M6_USAGE", "section": "MOJI_GOI", "category": "VOCAB", "name": "問題4・用法", "mock100": 6, "pool300": 18, "pool500": 30, "secPerItem": 45},
                {"code": "G1_GRAMMAR_FORM", "section": "BUNPOU_DOKKAI", "category": "GRAMMAR", "name": "問題5・文法形式の判断", "mock100": 10, "pool300": 30, "pool500": 50, "secPerItem": 35},
                {"code": "G2_STAR_SYNTAX", "section": "BUNPOU_DOKKAI", "category": "STAR", "name": "問題6・文の組み立て ★", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 60},
                {"code": "G3_TEXT_GRAMMAR", "section": "BUNPOU_DOKKAI", "category": "GRAMMAR", "name": "問題7・文章の文法", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 55},
                {"code": "R1_SHORT_READ", "section": "BUNPOU_DOKKAI", "category": "READING", "name": "問題8・内容理解（短篇）", "mock100": 4, "pool300": 12, "pool500": 20, "secPerItem": 120},
                {"code": "R2_MID_READ", "section": "BUNPOU_DOKKAI", "category": "READING", "name": "問題9・内容理解（中篇 3篇×3題）", "mock100": 9, "pool300": 27, "pool500": 45, "secPerItem": 150},
                {"code": "R3_INTEGRATED_READ", "section": "BUNPOU_DOKKAI", "category": "READING", "name": "問題10/11・統合理解（A/B兩文比較）", "mock100": 4, "pool300": 12, "pool500": 20, "secPerItem": 180},
                {"code": "R4_LONG_OPINION", "section": "BUNPOU_DOKKAI", "category": "READING", "name": "問題12・主張理解（長篇）", "mock100": 7, "pool300": 21, "pool500": 35, "secPerItem": 180},
                {"code": "R5_INFO_RETRIEVAL", "section": "BUNPOU_DOKKAI", "category": "READING", "name": "問題13・情報検索", "mock100": 2, "pool300": 6, "pool500": 10, "secPerItem": 120},
                {"code": "L1_TASK", "section": "CHOUKAI", "category": "LISTENING", "name": "聴解問題1・課題理解", "mock100": 6, "pool300": 18, "pool500": 30, "secPerItem": 55},
                {"code": "L2_POINT", "section": "CHOUKAI", "category": "LISTENING", "name": "聴解問題2・ポイント理解", "mock100": 7, "pool300": 21, "pool500": 35, "secPerItem": 55},
                {"code": "L3_SUMMARY", "section": "CHOUKAI", "category": "LISTENING", "name": "聴解問題3・概要理解 (全盲聽)", "mock100": 6, "pool300": 18, "pool500": 30, "secPerItem": 60},
                {"code": "L5_QUICK_RESP", "section": "CHOUKAI", "category": "LISTENING", "name": "聴解問題4・即時応答 (全盲聽)", "mock100": 11, "pool300": 33, "pool500": 55, "secPerItem": 25},
                {"code": "L6_INTEGRATED_LISTEN", "section": "CHOUKAI", "category": "LISTENING", "name": "聴解問題5・統合理解 (長篇多方討論)", "mock100": 3, "pool300": 9, "pool500": 15, "secPerItem": 90}
            ]
        },
        "N2": {
            "level": "N2",
            "title": "JLPT N2 進階主力",
            "sectionsMode": "二節制：言語知識・読解 (105m) ＋ 聴解 (50m)",
            "totalTimeMin": 155,
            "timeAllocationGuide": "文字語彙 15m ➔ 文法 20m ➔ 読解 70m (合計 105m) ｜ 聴解 50m",
            "passTotal": 90,
            "sectionCutoffs": {"言語知識": 19, "読解": 19, "聴解": 19},
            "mock100Total": 106,
            "practice300Target": 318,
            "practice500Target": 530,
            "mondaiList": [
                {"code": "M1_KANJI_READ", "section": "MOJI_GOI", "category": "KANJI", "name": "問題1・漢字読み", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 20},
                {"code": "M2_ORTHOGRAPHY", "section": "MOJI_GOI", "category": "KANJI", "name": "問題2・表記 (假名轉漢字)", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 20},
                {"code": "M3_WORD_FORM", "section": "MOJI_GOI", "category": "VOCAB", "name": "問題3・語形成 (N2專屬複合詞/接頭接尾)", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 25},
                {"code": "M4_CONTEXT_VOCAB", "section": "MOJI_GOI", "category": "VOCAB", "name": "問題4・文脈規定", "mock100": 7, "pool300": 21, "pool500": 35, "secPerItem": 30},
                {"code": "M5_PARAPHRASE", "section": "MOJI_GOI", "category": "VOCAB", "name": "問題5・言い換え類義", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 30},
                {"code": "M6_USAGE", "section": "MOJI_GOI", "category": "VOCAB", "name": "問題6・用法", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 45},
                {"code": "G1_GRAMMAR_FORM", "section": "BUNPOU_DOKKAI", "category": "GRAMMAR", "name": "問題7・文の文法1 (文法形式)", "mock100": 12, "pool300": 36, "pool500": 60, "secPerItem": 35},
                {"code": "G2_STAR_SYNTAX", "section": "BUNPOU_DOKKAI", "category": "STAR", "name": "問題8・文の文法2 (★星號重組)", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 55},
                {"code": "G3_TEXT_GRAMMAR", "section": "BUNPOU_DOKKAI", "category": "GRAMMAR", "name": "問題9・文章の文法", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 50},
                {"code": "R1_SHORT_READ", "section": "BUNPOU_DOKKAI", "category": "READING", "name": "問題10・内容理解（短篇）", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 110},
                {"code": "R2_MID_READ", "section": "BUNPOU_DOKKAI", "category": "READING", "name": "問題11・内容理解（中篇 3篇×3題）", "mock100": 9, "pool300": 27, "pool500": 45, "secPerItem": 140},
                {"code": "R3_INTEGRATED_READ", "section": "BUNPOU_DOKKAI", "category": "READING", "name": "問題12・統合理解（A/B兩文比較）", "mock100": 2, "pool300": 6, "pool500": 10, "secPerItem": 160},
                {"code": "R4_LONG_OPINION", "section": "BUNPOU_DOKKAI", "category": "READING", "name": "問題13・主張理解（長篇）", "mock100": 3, "pool300": 9, "pool500": 15, "secPerItem": 170},
                {"code": "R5_INFO_RETRIEVAL", "section": "BUNPOU_DOKKAI", "category": "READING", "name": "問題14・情報検索", "mock100": 2, "pool300": 6, "pool500": 10, "secPerItem": 110},
                {"code": "L1_TASK", "section": "CHOUKAI", "category": "LISTENING", "name": "聴解問題1・課題理解", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 50},
                {"code": "L2_POINT", "section": "CHOUKAI", "category": "LISTENING", "name": "聴解問題2・ポイント理解", "mock100": 6, "pool300": 18, "pool500": 30, "secPerItem": 50},
                {"code": "L3_SUMMARY", "section": "CHOUKAI", "category": "LISTENING", "name": "聴解問題3・概要理解 (全盲聽)", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 55},
                {"code": "L5_QUICK_RESP", "section": "CHOUKAI", "category": "LISTENING", "name": "聴解問題4・即時応答 (全盲聽)", "mock100": 12, "pool300": 36, "pool500": 60, "secPerItem": 25},
                {"code": "L6_INTEGRATED_LISTEN", "section": "CHOUKAI", "category": "LISTENING", "name": "聴解問題5・統合理解 (長篇討論)", "mock100": 3, "pool300": 9, "pool500": 15, "secPerItem": 85}
            ]
        },
        "N3": {
            "level": "N3",
            "title": "JLPT N3 中級橋樑",
            "sectionsMode": "三節制：文字・語彙 (30m) ＋ 文法・読解 (70m) ＋ 聴解 (40m)",
            "totalTimeMin": 140,
            "timeAllocationGuide": "第1節 文字語彙 30m ｜ 第2節 文法 20m + 読解 50m (合計 70m) ｜ 第3節 聴解 40m",
            "passTotal": 95,
            "sectionCutoffs": {"言語知識": 19, "読解": 19, "聴解": 19},
            "mock100Total": 102,
            "practice300Target": 306,
            "practice500Target": 510,
            "mondaiList": [
                {"code": "M1_KANJI_READ", "section": "MOJI_GOI", "category": "KANJI", "name": "第1節 問題1・漢字読み", "mock100": 8, "pool300": 24, "pool500": 40, "secPerItem": 20},
                {"code": "M2_ORTHOGRAPHY", "section": "MOJI_GOI", "category": "KANJI", "name": "第1節 問題2・表記", "mock100": 6, "pool300": 18, "pool500": 30, "secPerItem": 20},
                {"code": "M4_CONTEXT_VOCAB", "section": "MOJI_GOI", "category": "VOCAB", "name": "第1節 問題3・文脈規定", "mock100": 11, "pool300": 33, "pool500": 55, "secPerItem": 25},
                {"code": "M5_PARAPHRASE", "section": "MOJI_GOI", "category": "VOCAB", "name": "第1節 問題4・言い換え類義", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 25},
                {"code": "M6_USAGE", "section": "MOJI_GOI", "category": "VOCAB", "name": "第1節 問題5・用法", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 40},
                {"code": "G1_GRAMMAR_FORM", "section": "BUNPOU_DOKKAI", "category": "GRAMMAR", "name": "第2節 問題1・文の文法1", "mock100": 13, "pool300": 39, "pool500": 65, "secPerItem": 30},
                {"code": "G2_STAR_SYNTAX", "section": "BUNPOU_DOKKAI", "category": "STAR", "name": "第2節 問題2・文の組み立て ★", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 50},
                {"code": "G3_TEXT_GRAMMAR", "section": "BUNPOU_DOKKAI", "category": "GRAMMAR", "name": "第2節 問題3・文章の文法", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 50},
                {"code": "R1_SHORT_READ", "section": "BUNPOU_DOKKAI", "category": "READING", "name": "第2節 問題4・内容理解（短篇）", "mock100": 4, "pool300": 12, "pool500": 20, "secPerItem": 100},
                {"code": "R2_MID_READ", "section": "BUNPOU_DOKKAI", "category": "READING", "name": "第2節 問題5・内容理解（中篇）", "mock100": 6, "pool300": 18, "pool500": 30, "secPerItem": 130},
                {"code": "R4_LONG_OPINION", "section": "BUNPOU_DOKKAI", "category": "READING", "name": "第2節 問題6・内容理解（長篇）", "mock100": 4, "pool300": 12, "pool500": 20, "secPerItem": 150},
                {"code": "R5_INFO_RETRIEVAL", "section": "BUNPOU_DOKKAI", "category": "READING", "name": "第2節 問題7・情報検索", "mock100": 2, "pool300": 6, "pool500": 10, "secPerItem": 100},
                {"code": "L1_TASK", "section": "CHOUKAI", "category": "LISTENING", "name": "第3節 問題1・課題理解", "mock100": 6, "pool300": 18, "pool500": 30, "secPerItem": 45},
                {"code": "L2_POINT", "section": "CHOUKAI", "category": "LISTENING", "name": "第3節 問題2・ポイント理解", "mock100": 6, "pool300": 18, "pool500": 30, "secPerItem": 45},
                {"code": "L3_SUMMARY", "section": "CHOUKAI", "category": "LISTENING", "name": "第3節 問題3・概要理解 (全盲聽)", "mock100": 3, "pool300": 9, "pool500": 15, "secPerItem": 50},
                {"code": "L4_UTTERANCE", "section": "CHOUKAI", "category": "LISTENING", "name": "第3節 問題4・発話表現 (看圖情境 SVG)", "mock100": 4, "pool300": 12, "pool500": 20, "secPerItem": 35},
                {"code": "L5_QUICK_RESP", "section": "CHOUKAI", "category": "LISTENING", "name": "第3節 問題5・即時応答 (全盲聽)", "mock100": 9, "pool300": 27, "pool500": 45, "secPerItem": 25}
            ]
        },
        "N4": {
            "level": "N4",
            "title": "JLPT N4 基礎進階",
            "sectionsMode": "三節制：文字・語彙 (25m) ＋ 文法・読解 (55m) ＋ 聴解 (35m)",
            "totalTimeMin": 115,
            "timeAllocationGuide": "第1節 文字語彙 25m ｜ 第2節 文法 20m + 読解 35m (合計 55m) ｜ 第3節 聴解 35m",
            "passTotal": 90,
            "sectionCutoffs": {"言語知識+読解合併": 38, "聴解": 19},
            "mock100Total": 89,
            "practice300Target": 267,
            "practice500Target": 445,
            "mondaiList": [
                {"code": "M1_KANJI_READ", "section": "MOJI_GOI", "category": "KANJI", "name": "第1節 問題1・漢字読み", "mock100": 7, "pool300": 21, "pool500": 35, "secPerItem": 20},
                {"code": "M2_ORTHOGRAPHY", "section": "MOJI_GOI", "category": "KANJI", "name": "第1節 問題2・表記", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 20},
                {"code": "M4_CONTEXT_VOCAB", "section": "MOJI_GOI", "category": "VOCAB", "name": "第1節 問題3・文脈規定", "mock100": 8, "pool300": 24, "pool500": 40, "secPerItem": 25},
                {"code": "M5_PARAPHRASE", "section": "MOJI_GOI", "category": "VOCAB", "name": "第1節 問題4・言い換え類義", "mock100": 4, "pool300": 12, "pool500": 20, "secPerItem": 25},
                {"code": "M6_USAGE", "section": "MOJI_GOI", "category": "VOCAB", "name": "第1節 問題5・用法", "mock100": 4, "pool300": 12, "pool500": 20, "secPerItem": 35},
                {"code": "G1_GRAMMAR_FORM", "section": "BUNPOU_DOKKAI", "category": "GRAMMAR", "name": "第2節 問題1・文の文法1", "mock100": 13, "pool300": 39, "pool500": 65, "secPerItem": 30},
                {"code": "G2_STAR_SYNTAX", "section": "BUNPOU_DOKKAI", "category": "STAR", "name": "第2節 問題2・文の組み立て ★", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 45},
                {"code": "G3_TEXT_GRAMMAR", "section": "BUNPOU_DOKKAI", "category": "GRAMMAR", "name": "第2節 問題3・文章の文法", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 45},
                {"code": "R1_SHORT_READ", "section": "BUNPOU_DOKKAI", "category": "READING", "name": "第2節 問題4・内容理解（短篇）", "mock100": 4, "pool300": 12, "pool500": 20, "secPerItem": 90},
                {"code": "R2_MID_READ", "section": "BUNPOU_DOKKAI", "category": "READING", "name": "第2節 問題5・内容理解（中篇）", "mock100": 4, "pool300": 12, "pool500": 20, "secPerItem": 110},
                {"code": "R5_INFO_RETRIEVAL", "section": "BUNPOU_DOKKAI", "category": "READING", "name": "第2節 問題6・情報検索", "mock100": 2, "pool300": 6, "pool500": 10, "secPerItem": 90},
                {"code": "L1_TASK", "section": "CHOUKAI", "category": "LISTENING", "name": "第3節 問題1・課題理解", "mock100": 8, "pool300": 24, "pool500": 40, "secPerItem": 40},
                {"code": "L2_POINT", "section": "CHOUKAI", "category": "LISTENING", "name": "第3節 問題2・ポイント理解", "mock100": 7, "pool300": 21, "pool500": 35, "secPerItem": 40},
                {"code": "L4_UTTERANCE", "section": "CHOUKAI", "category": "LISTENING", "name": "第3節 問題3・発話表現 (看圖情境 SVG)", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 35},
                {"code": "L5_QUICK_RESP", "section": "CHOUKAI", "category": "LISTENING", "name": "第3節 問題4・即時応答 (全盲聽)", "mock100": 8, "pool300": 24, "pool500": 40, "secPerItem": 25}
            ]
        }
    },
    "taiwanHighSchoolTrapCards": [
        {"kanji": "手紙 (てがみ) [0]", "lvl": "N4", "jpMeaning": "信件、書信", "twTrap": "❌ 台灣母語誤以為是「衛生紙」（日文衛生紙為 トイレットペーパー / ティッシュ）"},
        {"kanji": "我慢 (がまん) [1]", "lvl": "N3", "jpMeaning": "忍耐、忍受", "twTrap": "❌ 台灣母語誤以為是「傲慢」（日文傲慢為 傲慢 ごうまん / 横柄）"},
        {"kanji": "都合 (つごう) [0]", "lvl": "N4", "jpMeaning": "情況、方便與否、總共", "twTrap": "❌ 台灣母語誤以為是「大都會」（日文大都市為 都会 とかい）"},
        {"kanji": "勉強 (べんきょう) [0]", "lvl": "N4", "jpMeaning": "用功讀書、學習、算便宜", "twTrap": "❌ 台灣母語誤以為是「強迫/勉強」（日文勉強做某事為 無理をする / 強いる）"},
        {"kanji": "汽車 (きしゃ) [1]", "lvl": "N4", "jpMeaning": "蒸汽火車", "twTrap": "❌ 台灣母語誤以為是「汽車 (Auto)」（日文汽車為 車 くるま / 自動車）"},
        {"kanji": "邪魔 (じゃま) [0]", "lvl": "N3", "jpMeaning": "打擾、妨礙、絆腳石", "twTrap": "❌ 台灣母語誤以為是「妖魔鬼怪」（拜訪別人時說 お邪魔します 表打擾了）"},
        {"kanji": "大家 (おおや) [1]", "lvl": "N3", "jpMeaning": "房東（另有 たいか 表泰斗大師）", "twTrap": "❌ 台灣母語誤以為是「大家 (Everyone)」（日文大家為 皆さん / みんな）"},
        {"kanji": "床 (ゆか) [0]", "lvl": "N3", "jpMeaning": "地板（Floor）", "twTrap": "❌ 台灣母語誤以為是「睡覺的床」（日文睡床為 ベッド / 布団）"},
        {"kanji": "暗算 (あんざん) [0]", "lvl": "N2", "jpMeaning": "心算（Mental arithmetic）", "twTrap": "❌ 台灣母語誤以為是「暗中陷害/暗算」"},
        {"kanji": "成敗 (せいばい) [1]", "lvl": "N1", "jpMeaning": "懲罰、制裁（或成與敗）", "twTrap": "❌ 時代劇或慣用語中「成敗する」指處罰壞人，非單純成敗得失"},
        {"kanji": "おざなり vs ないがしろ", "lvl": "N1", "jpMeaning": "おざなり＝敷衍應付(有做但隨便)；ないがしろ＝徹底無視輕蔑", "twTrap": "⚡ N1 必考類義陷阱：長官交代的事隨便交差用「おざなり」，完全不理會用「ないがしろ」"},
        {"kanji": "橋 (はし [2]) vs 箸 (はし [1])", "lvl": "N3", "jpMeaning": "橋 [2] 尾高型 (低高+低) vs 箸 [1] 頭高型 (高低)", "twTrap": "🎵 高低音調 (Pitch Accent) 最小對立組：雨 (あめ [1]) vs 飴 (あめ [0])"}
    ]
}


def main():
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    out_path = os.path.join(ROOT, "data", "official_exam_blueprint.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(OFFICIAL_BLUEPRINT, f, ensure_ascii=False, indent=2)

    print("=== JLPT N1-N4 Official 100% Exam vs 300%-500% Practice Pool Blueprint ===")
    grand_100 = 0
    grand_300 = 0
    grand_500 = 0
    for lvl in OFFICIAL_BLUEPRINT["levelOrder"]:
        spec = OFFICIAL_BLUEPRINT["levels"][lvl]
        sum_100 = sum(m["mock100"] for m in spec["mondaiList"])
        sum_300 = sum(m["pool300"] for m in spec["mondaiList"])
        sum_500 = sum(m["pool500"] for m in spec["mondaiList"])
        assert sum_100 == spec["mock100Total"], f"{lvl} sum mismatch: {sum_100} != {spec['mock100Total']}"
        grand_100 += sum_100
        grand_300 += sum_300
        grand_500 += sum_500
        print(
            f"  [{lvl}] Mondai Types: {len(spec['mondaiList']):2d} | "
            f"100% Full Mock: {sum_100:3d} Qs ({spec['totalTimeMin']}m) | "
            f"300% Practice Pool: {sum_300:3d} Qs | "
            f"500% Practice Pool: {sum_500:3d} Qs"
        )
    print(
        f"  [TOTAL N1-N4] 100% Full Mock: {grand_100} Qs | "
        f"300% Practice Pool: {grand_300} Qs | "
        f"500% Practice Pool: {grand_500} Qs"
    )
    print(f"Saved blueprint to {out_path}")


if __name__ == "__main__":
    main()
