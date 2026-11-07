#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enrich_inline_ruby.py
Wave 2 Pedagogical Improvement:
Injects inline <ruby>漢字<rt>かんじ</rt></ruby> into `stem` for non-KANJI items (outside <u>...</u> tags)
across N1, N2, N3, and N4 so toggling `あ 振假名: ON` in Scaffolding Mode renders inline ruby across ALL 4 levels.
"""

import json
import os
import re

ROOT = r"d:\MuseAcademy_50_25C16\jlpt-ai-studio"

COMMON_RUBY_DICT = [
    ("個人情報保護", "こじんじょうほうほご"),
    ("証拠映像", "しょうこえいぞう"),
    ("専門書", "せんもんしょ"),
    ("案内放送", "あんないほうそう"),
    ("忘れ物", "わすれもの"),
    ("婦人服売り場", "ふじんふくうりば"),
    ("中古車", "ちゅうこしゃ"),
    ("栄養価", "えいようか"),
    ("連絡先", "れんらくさき"),
    ("体調", "たいちょう"),
    ("階段", "かいだん"),
    ("冗談", "じょうだん"),
    ("不正", "ふせい"),
    ("監査", "かんさ"),
    ("観点", "かんてん"),
    ("了承", "りょうしょう"),
    ("鮮明", "せんめい"),
    ("宿泊", "しゅくはく"),
    ("協力", "きょうりょく"),
    ("判断", "はんだん"),
    ("状態", "じょうたい"),
    ("試行錯誤", "しこうさくご"),
    ("画期的", "かっきてき"),
    ("入場券", "にゅうじょうけん"),
    ("払い戻し", "はらいもどし"),
    ("再発行", "さいはっこう"),
    ("窓口", "まどぐち"),
    ("製造過程", "せいぞうかてい"),
    ("徹底的", "てっていてき"),
    ("品質管理", "ひんしつかんり"),
    ("語学学習", "ごがくがくしゅう"),
    ("暗記", "あんき"),
    ("文脈", "ぶんみゃく"),
    ("推測", "すいそく"),
    ("効率化", "こうりつか"),
    ("情報", "じょうほう"),
    ("検証", "けんしょう"),
    ("姿勢", "しせい"),
    ("不可欠", "ふかけつ"),
    ("伝統文化", "でんとうぶんか"),
    ("継承", "けいしょう"),
    ("革新", "かくしん"),
    ("人工知能", "じんこうちのう"),
    ("急速", "きゅうそく"),
    ("普及", "ふきゅう"),
    ("懸念", "けねん"),
    ("倫理的", "りんりてき"),
    ("課題", "かだい"),
    ("克服", "こくふく"),
    ("多様性", "たようせい"),
    ("尊重", "そんちょう"),
    ("相互理解", "そうごりかい"),
    ("促進", "そくしん"),
    ("環境保護", "かんきょうほご"),
    ("経済成長", "けいざいせいちょう"),
    ("両立", "りょうりつ"),
    ("持続可能", "じぞくかのう"),
    ("社会", "しゃかい"),
    ("構築", "こうちく"),
    ("図書館", "としょかん"),
    ("体育館", "たいいくかん"),
    ("奨学金", "しょうがくきん"),
    ("締め切り", "しめきり"),
    ("提出", "ていしゅつ"),
    ("申請", "しんせい"),
    ("審査", "しんさ"),
    ("対象", "たいしょう"),
    ("条件", "じょうけん"),
    ("確認", "かくにん"),
    ("参加費", "さんかひ"),
    ("無料", "むりょう"),
    ("定員", "ていいん"),
    ("先着順", "せんちゃくじゅん"),
    ("申し込み", "もうしこみ"),
    ("天気予報", "てんきよほう"),
    ("美術館", "びじゅつかん"),
    ("博物館", "はくぶつかん"),
    ("映画館", "えいがかん"),
    ("郵便局", "ゆうびんきょく"),
    ("報告書", "ほうこくしょ"),
    ("担当者", "たんとうしゃ"),
    ("会議", "かいぎ"),
    ("準備", "じゅんび"),
    ("練習", "れんしゅう"),
    ("連絡", "れんらく"),
    ("相談", "そうだん"),
    ("経験", "けいけん"),
    ("説明", "せつめい"),
    ("約束", "やくそく"),
    ("都合", "つごう"),
    ("理由", "りゆう"),
    ("健康", "けんこう"),
    ("運動", "うんどう"),
    ("食事", "しょくじ"),
    ("睡眠", "すいみん"),
    ("成績", "せいせき"),
    ("試験", "しけん"),
    ("宿題", "しゅくだい"),
    ("授業", "じゅぎょう"),
    ("先生", "せんせい"),
    ("学生", "がくせい"),
    ("友達", "ともだち"),
    ("家族", "かぞく"),
    ("両親", "りょうしん"),
    ("電車", "でんしゃ"),
    ("空港", "くうこう"),
    ("病院", "びょういん"),
    ("銀行", "ぎんこう"),
    ("台風", "たいふう"),
    ("地震", "じしん"),
    ("交通", "こうつう"),
    ("事故", "じこ"),
    ("渋滞", "じゅうたい"),
    ("予約", "よやく"),
    ("変更", "へんこう"),
    ("受付", "うけつけ"),
    ("資料", "しりょう"),
]


def extract_pairs(hint: str) -> list[tuple[str, str]]:
    pairs = []
    if hint:
        # Format 1: 漢字（かんじ）
        for m in re.finditer(r"([一-龯々ヶ]+)[（\(]([ぁ-んァ-ンー]+)[）\)]", hint):
            pairs.append((m.group(1), m.group(2)))
    pairs.extend(COMMON_RUBY_DICT)
    # Sort longer kanji compounds first to avoid partial match
    pairs.sort(key=lambda x: len(x[0]), reverse=True)
    return pairs


def inject_ruby_outside_u(stem: str, pairs: list[tuple[str, str]]) -> str:
    if "<ruby>" in stem or not pairs:
        return stem
    parts = re.split(r"(<u>.*?</u>|<[^>]+>)", stem)
    for idx, part in enumerate(parts):
        if part.startswith("<"):
            continue
        for kanji, reading in pairs:
            if kanji in part and f"<ruby>{kanji}" not in part:
                part = part.replace(kanji, f"<ruby>{kanji}<rt>{reading}</rt></ruby>", 1)
        parts[idx] = part
    return "".join(parts)


def process_bank(level: str):
    path = os.path.join(ROOT, "data", f"{level.lower()}_bank.json")
    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)

    enriched = 0
    for q in items:
        if q.get("category") in ("KANJI",):
            continue
        pairs = extract_pairs(q.get("furiganaHint", ""))
        new_stem = inject_ruby_outside_u(q.get("stem", ""), pairs)
        if new_stem != q.get("stem", ""):
            q["stem"] = new_stem
            enriched += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"[{level}] Enriched {enriched} items with inline <ruby> furigana tags.")


if __name__ == "__main__":
    for lvl in ["N1", "N2", "N3", "N4", "N5"]:
        process_bank(lvl)
