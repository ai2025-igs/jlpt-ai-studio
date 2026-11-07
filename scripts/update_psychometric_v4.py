# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(r"d:\MuseAcademy_50_25C16\jlpt-ai-studio\assets\js\psychometric.js")
txt = p.read_text(encoding="utf-8")

if "N5:" not in txt:
    n4_block = """  N4: {
    level: 'N4',
    badge: 'N4 基礎進階',
    color: 'emerald',
    sectionsMode: '3-SECTION (25m 字彙 + 55m 文法讀解 + 35m 聽解)',
    timerSpec: '字彙 25m ｜ 文法讀解 55m ｜ 聽解 35m',
    passTotal: 90,
    maxTotal: 180,
    combinedWrittenGate: true,
    cutoffs: { writtenCombined: 38, listen: 19 },
    vocabScale: '~300 漢字 / ~1,500 詞',
    desc: '三節制測驗（總分 ≥90/180，言語知識+讀解合併 ≥38/120、聽解 ≥19/60）'
  }"""
    n4_n5_block = n4_block + """,
  N5: {
    level: 'N5',
    badge: 'N5 入門基礎',
    color: 'sky',
    officialHex: '#1e78b4',
    sectionsMode: '3-SECTION (20m 字彙 + 40m 文法讀解 + 30m 聽解)',
    timerSpec: '字彙 20m ｜ 文法讀解 40m ｜ 聽解 30m',
    passTotal: 80,
    maxTotal: 180,
    combinedWrittenGate: true,
    cutoffs: { writtenCombined: 38, listen: 19 },
    vocabScale: '~100 漢字 / ~800 詞',
    desc: '三節制測驗（總分 ≥80/180，言語知識+讀解合併 ≥38/120、聽解 ≥19/60）'
  }"""
    txt = txt.replace(n4_block, n4_n5_block)

txt = txt.replace(
    '"levelOrder": [\n    "N1",\n    "N2",\n    "N3",\n    "N4"\n  ]',
    '"levelOrder": ["N1", "N2", "N3", "N4", "N5"]'
)

n5_blueprint = """    "N5": {
      "level": "N5",
      "title": "JLPT N5 入門基礎",
      "sectionsMode": "三節制：文字・語彙 (20m) ＋ 文法・読解 (40m) ＋ 聴解 (30m)",
      "totalTimeMin": 90,
      "timeAllocationGuide": "第1節 文字語彙 20m ｜ 第2節 文法 15m + 読解 25m (合計 40m) ｜ 第3節 聴解 30m",
      "passTotal": 80,
      "sectionCutoffs": { "言語知識+読解合併": 38, "聴解": 19 },
      "mock100Total": 80,
      "practice300Target": 240,
      "practice500Target": 400,
      "mondaiList": [
        { "code": "M1_KANJI_READ", "section": "MOJI_GOI", "category": "KANJI", "name": "第1節 問題1・漢字読み", "mock100": 12, "pool300": 36, "pool500": 60, "secPerItem": 15 },
        { "code": "M2_ORTHOGRAPHY", "section": "MOJI_GOI", "category": "KANJI", "name": "第1節 問題2・表記", "mock100": 8, "pool300": 24, "pool500": 40, "secPerItem": 15 },
        { "code": "M4_CONTEXT_VOCAB", "section": "MOJI_GOI", "category": "VOCAB", "name": "第1節 問題3・文脈規定", "mock100": 10, "pool300": 30, "pool500": 50, "secPerItem": 20 },
        { "code": "M5_PARAPHRASE", "section": "MOJI_GOI", "category": "VOCAB", "name": "第1節 問題4・言い換え類義", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 20 },
        { "code": "G1_GRAMMAR_FORM", "section": "BUNPOU_DOKKAI", "category": "GRAMMAR", "name": "第2節 問題1・文の文法1 (助詞・活用)", "mock100": 15, "pool300": 45, "pool500": 75, "secPerItem": 25 },
        { "code": "G2_STAR_SYNTAX", "section": "BUNPOU_DOKKAI", "category": "STAR", "name": "第2節 問題2・文の組み立て ★", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 40 },
        { "code": "G3_TEXT_GRAMMAR", "section": "BUNPOU_DOKKAI", "category": "GRAMMAR", "name": "第2節 問題3・文章の文法", "mock100": 4, "pool300": 12, "pool500": 20, "secPerItem": 40 },
        { "code": "R1_SHORT_READ", "section": "BUNPOU_DOKKAI", "category": "READING", "name": "第2節 問題4・内容理解（短篇）", "mock100": 3, "pool300": 9, "pool500": 15, "secPerItem": 75 },
        { "code": "R2_MID_READ", "section": "BUNPOU_DOKKAI", "category": "READING", "name": "第2節 問題5・内容理解（中篇）", "mock100": 2, "pool300": 6, "pool500": 10, "secPerItem": 90 },
        { "code": "R5_INFO_RETRIEVAL", "section": "BUNPOU_DOKKAI", "category": "READING", "name": "第2節 問題6・情報検索", "mock100": 1, "pool300": 3, "pool500": 5, "secPerItem": 75 },
        { "code": "L1_TASK", "section": "CHOUKAI", "category": "LISTENING", "name": "第3節 問題1・課題理解", "mock100": 7, "pool300": 21, "pool500": 35, "secPerItem": 35 },
        { "code": "L2_POINT", "section": "CHOUKAI", "category": "LISTENING", "name": "第3節 問題2・ポイント理解", "mock100": 6, "pool300": 18, "pool500": 30, "secPerItem": 35 },
        { "code": "L4_UTTERANCE", "section": "CHOUKAI", "category": "LISTENING", "name": "第3節 問題3・発話表現 (看圖情境 SVG)", "mock100": 5, "pool300": 15, "pool500": 25, "secPerItem": 30 },
        { "code": "L5_QUICK_RESP", "section": "CHOUKAI", "category": "LISTENING", "name": "第3節 問題4・即時応答 (全盲聽)", "mock100": 6, "pool300": 18, "pool500": 30, "secPerItem": 20 }
      ]
    }"""

if '"N5": {' not in txt:
    txt = txt.replace('      ]\n    }\n  },\n  "taiwanHighSchoolTrapCards"', '      ]\n    },\n' + n5_blueprint + '\n  },\n  "taiwanHighSchoolTrapCards"')

p.write_text(txt, encoding="utf-8")
print("Updated psychometric.js with N5 specs and blueprint!")
