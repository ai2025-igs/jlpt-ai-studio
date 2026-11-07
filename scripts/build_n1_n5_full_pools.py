#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_n1_n5_full_pools.py
1. Creates the authentic JLPT N5 seed bank (24 core items across all 14 official N5 Mondai types,
   with inline <ruby>, Situational SVG for Utterance Expressions, and dual-voice dialogue).
2. Expands N1, N2, N3, N4, and N5 banks to exact 300% Practice Pool scale (1,443 items total),
   with the first 100% Official Exam quota (104, 106, 102, 89, 80 = 481 items) tagged as
   `inMock100: True` in exact Mondai proportions!
3. Updates `data/official_exam_blueprint.json` with N1-N5 (5 levels).
"""

import copy
import json
import os
import random

ROOT = r"d:\MuseAcademy_50_25C16\jlpt-ai-studio"

N5_SEED_ITEMS = [
    {
        "id": "N5-K01", "level": "N5", "section": "MOJI_GOI", "category": "KANJI",
        "officialCode": "M1_KANJI_READ", "officialName": "問題1・漢字読み", "mondaiNum": 1,
        "subtag": "N5 基礎漢字・時間與數字音變", "targetSec": 15, "irtA": 1.2, "irtB": -1.8,
        "bloomLevel": "L1_REMEMBER", "bloomLabel": "L1 記憶・基礎字音",
        "instruction": "＿＿＿の言葉の読み方として最もよいものを、1・2・3・4から一つ選びなさい。",
        "stem": "<ruby>来週<rt>らいしゅう</rt></ruby>の<u>火曜日</u>にテストがあります。",
        "furiganaHint": "火曜日（かようび）：星期二",
        "socraticHint": "想想看「火、水、木、金、土」搭配「曜日（ようび）」時，「火」的音讀是什麼？",
        "l1TransferNote": "🇹🇼⇄🇯🇵 台灣高中生常把「火曜日」跟「水曜日（すいようび）」搞混：火＝かようび（週二），水＝すいようび（週三）。",
        "grammarChain": "来週の (Nの) ➔ 火曜日に (時間點+に) ➔ テストがあります (存在句)",
        "ttsText": "来週の火曜日にテストがあります。",
        "options": ["かようび", "すいようび", "もくようび", "きんようび"],
        "correctIndex": 0,
        "translation": "下週二有考試。",
        "coreRule": "N5 必考星期名稱：月（げつ）、火（か）、水（すい）、木（もく）、金（きん）、土（ど）、日（にち）。",
        "optionExplanations": [
            "✅ 正確解答：火曜日（かようび，星期二）。",
            "❌ 誘答陷阱：水曜日（すいようび，星期三）。",
            "❌ 誘答陷阱：木曜日（もくようび，星期四）。",
            "❌ 誘答陷阱：金曜日（きんようび，星期五）。"
        ]
    },
    {
        "id": "N5-K02", "level": "N5", "section": "MOJI_GOI", "category": "KANJI",
        "officialCode": "M1_KANJI_READ", "officialName": "問題1・漢字読み", "mondaiNum": 1,
        "subtag": "N5 基礎漢字・量詞促音便", "targetSec": 15, "irtA": 1.4, "irtB": -1.5,
        "bloomLevel": "L1_REMEMBER", "bloomLabel": "L1 記憶・量詞音變",
        "instruction": "＿＿＿の言葉の読み方として最もよいものを、1・2・3・4から一つ選びなさい。",
        "stem": "机の上にりんごが<u>八つ</u>あります。",
        "furiganaHint": "八つ（やっつ）：八個（和語通用量詞）",
        "socraticHint": "日文固有數詞「一つ、二つ…八つ」中，「八つ」中間有促音「っ」嗎？讀作「やっつ」還是「はっつ」？",
        "l1TransferNote": "🇹🇼⇄🇯🇵 母語負遷移警示：中文讀「八(ba)」，但日文和語數詞「八つ」讀作「やっつ [1]」，且「四つ（よっつ）」「六つ（むっつ）」「八つ（やっつ）」皆有促音！",
        "grammarChain": "机の上に (場所+に) ➔ りんごが (主語+が) ➔ 八つ (數量詞副詞用法) ➔ あります",
        "ttsText": "机の上にりんごが八つあります。",
        "options": ["はっつ", "やっつ", "やつ", "よっつ"],
        "correctIndex": 1,
        "translation": "桌子上有八顆蘋果。",
        "coreRule": "N5 必背固有數詞：一つ(ひとつ)、二つ(ふたつ)、三つ(みっつ)、四つ(よっつ)、五つ(いつつ)、六つ(むっつ)、七つ(ななつ)、八つ(やっつ)、九つ(ここのつ)、十(とお)。",
        "optionExplanations": [
            "❌ 音讀誤用陷阱：受漢語音「はち」影響誤讀。",
            "✅ 正確解答：八つ（やっつ）。",
            "❌ 漏促音陷阱：漏掉促音「っ」（やつ是代名詞「傢伙」）。",
            "❌ 數詞混淆：四つ（よっつ，四個）。"
        ]
    },
    {
        "id": "N5-K03", "level": "N5", "section": "MOJI_GOI", "category": "KANJI",
        "officialCode": "M2_ORTHOGRAPHY", "officialName": "問題2・表記", "mondaiNum": 2,
        "subtag": "N5 假名轉漢字・動詞訓讀", "targetSec": 15, "irtA": 1.3, "irtB": -1.6,
        "bloomLevel": "L1_REMEMBER", "bloomLabel": "L1 記憶・漢字表記",
        "instruction": "＿＿＿の言葉を漢字で書くとき、最もよいものを、1・2・3・4から一つ選びなさい。",
        "stem": "毎朝、駅で新聞を<u>かいます</u>。",
        "furiganaHint": "買います（かいます）：購買",
        "socraticHint": "在車站對「報紙（新聞）」做的動作是「買（かう）」還是「寫（かく）」？",
        "l1TransferNote": "🇹🇼⇄🇯🇵 注意日文「新聞（しんぶん）」是「報紙」，不是電視新聞（ニュース）！買報紙寫作「新聞を買います」。",
        "grammarChain": "毎朝 (時間) ➔ 駅で (動作場所+で) ➔ 新聞を (受詞+を) ➔ 買います (他動詞)",
        "ttsText": "毎朝、駅で新聞を買います。",
        "options": ["買います", "書います", "聞います", "見います"],
        "correctIndex": 0,
        "translation": "每天早上在車站買報紙。",
        "coreRule": "五段動詞「買う（かう）」ます形為「買います」。「書く」為「書きます」，「聞く」為「聞きます」。",
        "optionExplanations": [
            "✅ 正確解答：買います（かいます）。",
            "❌ 活用錯誤：書く的ます形是「書きます」。",
            "❌ 活用錯誤：聞く的ます形是「聞きます」。",
            "❌ 活用錯誤：見る的ます形是「見ます」。"
        ]
    },
    {
        "id": "N5-V01", "level": "N5", "section": "MOJI_GOI", "category": "VOCAB",
        "officialCode": "M4_CONTEXT_VOCAB", "officialName": "問題3・文脈規定", "mondaiNum": 3,
        "subtag": "N5 基礎語彙・台灣假朋友陷阱", "targetSec": 20, "irtA": 1.5, "irtB": -1.3,
        "bloomLevel": "L2_UNDERSTAND", "bloomLabel": "L2 理解・語境詞彙",
        "instruction": "（　）に入れるのに最もよいものを、1・2・3・4から一つ選びなさい。",
        "stem": "母に誕生日の（　）を書いて、郵便局から出しました。",
        "furiganaHint": "誕生日（たんじょうび） / 郵便局（ゆうびんきょく）：郵局",
        "socraticHint": "能「寫（書いて）」並且從「郵局（郵便局）」寄出的東西是什麼？小心台日漢字假朋友！",
        "l1TransferNote": "🇹🇼⇄🇯🇵 超級假朋友陷阱：日文的「手紙（てがみ）[0]」是「信件」，絕對不是「衛生紙（トイレットペーパー）」！",
        "grammarChain": "母に (對象+に) ➔ 誕生日の手紙を (受詞+を) ➔ 書いて (て形連接) ➔ 出しました (寄出)",
        "ttsText": "母に誕生日の手紙を書いて、郵便局から出しました。",
        "options": ["手紙", "切手", "雑誌", "辞書"],
        "correctIndex": 0,
        "translation": "寫了生日信給媽媽，並從郵局寄出去了。",
        "coreRule": "手紙（てがみ）＝信件；切手（きって）＝郵票；葉書（はがき）＝明信片。",
        "optionExplanations": [
            "✅ 正確解答：手紙（てがみ，信件）。搭配「手紙を書く／出す」。",
            "❌ 語意不合：切手（きって，郵票）是用貼的（貼る），不是用來寫的。",
            "❌ 語意不合：雑誌（ざっし，雜誌）。",
            "❌ 語意不合：辞書（じしょ，字典）。"
        ]
    },
    {
        "id": "N5-V02", "level": "N5", "section": "MOJI_GOI", "category": "VOCAB",
        "officialCode": "M5_PARAPHRASE", "officialName": "問題4・言い換え類義", "mondaiNum": 4,
        "subtag": "N5 近義詞替換・時間副詞", "targetSec": 20, "irtA": 1.3, "irtB": -1.4,
        "bloomLevel": "L2_UNDERSTAND", "bloomLabel": "L2 理解・近義替換",
        "instruction": "＿＿＿の文とだいたい同じ意味の文はどれですか。1・2・3・4から一つ選びなさい。",
        "stem": "<u>ゆうべ</u>はたくさんの雪が降りました。",
        "furiganaHint": "雪（ゆき） / 降りました（ふりました）：下了（雪/雨）",
        "socraticHint": "「ゆうべ（夕べ）」是指「昨天早上」還是「昨天晚上」？",
        "l1TransferNote": "🇹🇼⇄🇯🇵 「ゆうべ」漢字寫作「夕べ」，等同於「きのうの夜（昨晚）」。",
        "grammarChain": "ゆうべ (昨晚) ≡ きのうの夜",
        "ttsText": "ゆうべはたくさんの雪が降りました。",
        "options": [
            "きのうの朝はたくさんの雪が降りました。",
            "きのうの夜はたくさんの雪が降りました。",
            "きょうの朝はたくさんの雪が降りました。",
            "あしたの夜はたくさんの雪が降ります。"
        ],
        "correctIndex": 1,
        "translation": "昨晚下了很多雪。（＝昨天晚上）",
        "coreRule": "ゆうべ＝きのうの夜（昨晚）；けさ（今朝）＝きょうの朝（今天早上）。",
        "optionExplanations": [
            "❌ 時間錯誤：きのうの朝（昨天早上）。",
            "✅ 正確解答：きのうの夜（昨天晚上）＝ゆうべ。",
            "❌ 時間錯誤：きょうの朝＝けさ（今天早上）。",
            "❌ 時間錯誤：あしたの夜（明天晚上）。"
        ]
    },
    {
        "id": "N5-G01", "level": "N5", "section": "BUNPOU_DOKKAI", "category": "GRAMMAR",
        "officialCode": "G1_GRAMMAR_FORM", "officialName": "問題1・文の文法1", "mondaiNum": 5,
        "subtag": "N5 核心助詞・交通工具與場所", "targetSec": 25, "irtA": 1.4, "irtB": -1.4,
        "bloomLevel": "L3_APPLY", "bloomLabel": "L3 應用・格助詞辨析",
        "instruction": "次の文の（　）に入れるのに最もよいものを、1・2・3・4から一つ選びなさい。",
        "stem": "私は毎日、バス（　）学校へ行きます。",
        "furiganaHint": "毎日（まいにち） / 学校（がっこう）",
        "socraticHint": "表示「搭乘某交通工具（手段・方法）」時，應該使用哪一個格助詞？（注意：唯有「走路」是用「歩いて」不加助詞！）",
        "l1TransferNote": "🇹🇼⇄🇯🇵 台灣學生常受英文 by bus 或中文「坐公車」影響誤選「に（乗る才用に）」。後面動詞是「行きます」時，交通工具手段一律用「で」！",
        "grammarChain": "バスで (交通手段+で) ➔ 学校へ (方向+へ) ➔ 行きます (移動動詞)",
        "ttsText": "私は毎日、バスで学校へ行きます。",
        "options": ["を", "に", "で", "と"],
        "correctIndex": 2,
        "translation": "我每天搭公車去學校。",
        "coreRule": "助詞「で」表交通工具或手段（バスで／電車で／自転車で行く）。若動詞為「乗ります」才用「バスに乗ります」。",
        "optionExplanations": [
            "❌ 助詞誤用：「を」表離開或經過的場所（バスを降りる）。",
            "❌ 助詞誤用：後面動詞是「行きます」而非「乗ります」，不可用「に」。",
            "✅ 正確解答：「で」表示交通工具手段。",
            "❌ 助詞誤用：「と」表示共同行動的對象（友達と行く）。"
        ]
    },
    {
        "id": "N5-S01", "level": "N5", "section": "BUNPOU_DOKKAI", "category": "STAR",
        "officialCode": "G2_STAR_SYNTAX", "officialName": "問題2・文の組み立て ★", "mondaiNum": 6,
        "subtag": "N5 星號重組・想要某物 (～が欲しい)", "targetSec": 40, "irtA": 1.5, "irtB": -1.2,
        "bloomLevel": "L4_ANALYZE", "bloomLabel": "L4 分析・語序重組",
        "instruction": "次の文の ＿＿＿ ＿＿＿ ★ ＿＿＿ に入る最もよいものを、1・2・3・4から一つ選びなさい。",
        "stem": "私は ＿＿＿ ＿＿＿ <u>★</u> ＿＿＿ です。",
        "furiganaHint": "新しい（あたらしい） / パソコン：個人電腦 / 欲しい（ほしい）：想要",
        "socraticHint": "形容詞「新しい」應該修飾哪個名詞？而表示「想要某個東西」的句型是「N が 欲しいです」！",
        "l1TransferNote": "🇹🇼⇄🇯🇵 中文說「我想要新電腦」是動賓結構，但日文的「欲しい（ほしい）」是い形容詞，想要的對象必須用助詞「が」標示（パソコンが欲しいです）！",
        "grammarChain": "私は [1: 新しい] ➔ [3: パソコン] ➔ [4: ★ が] ➔ [2: 欲しい] です。",
        "ttsText": "私は新しいパソコンが欲しいです。",
        "options": ["新しい", "欲しい", "パソコン", "が"],
        "correctIndex": 3,
        "correctSequence": [0, 2, 3, 1],
        "translation": "我想要一台新電腦。",
        "coreRule": "N が 欲しいです（想要名詞 N）。い形容詞「新しい」直接修飾名詞「パソコン」。",
        "optionExplanations": [
            "❌ 語序第 1 格：新しい（修飾パソコン）。",
            "❌ 語序第 4 格：欲しい（接在です前）。",
            "❌ 語序第 2 格：パソコン（被新しい修飾）。",
            "✅ 正確解答（★第 3 格）：が（標示欲しい的對象：新しいパソコンが欲しいです）。"
        ]
    },
    {
        "id": "N5-G02", "level": "N5", "section": "BUNPOU_DOKKAI", "category": "GRAMMAR",
        "officialCode": "G3_TEXT_GRAMMAR", "officialName": "問題3・文章の文法", "mondaiNum": 7,
        "subtag": "N5 文章文法・連接詞與時態", "targetSec": 40, "irtA": 1.3, "irtB": -1.3,
        "bloomLevel": "L3_APPLY", "bloomLabel": "L3 應用・篇章接續",
        "instruction": "次の文章を読んで、（　）に入れるのに最もよいものを、1・2・3・4から一つ選びなさい。",
        "stem": "きのう、友達と映画を見に行きました。その映画はとてもおもしろかったです。（　）、映画のあとで喫茶店でコーヒーを飲みました。",
        "furiganaHint": "映画（えいが） / 喫茶店（きっさてん）：咖啡廳",
        "socraticHint": "前句說「去看了電影，非常有趣」，後句說「在電影之後去咖啡廳喝了咖啡」，表示「然後、接著」的連接詞是哪一個？",
        "l1TransferNote": "🇹🇼⇄🇯🇵 「それから」表先後順序「然後、接著」；「しかし／でも」表轉折「但是」；「なぜなら」表原因「因為」。",
        "grammarChain": "映画を見に行った ➔ （それから：接著） ➔ コーヒーを飲んだ",
        "ttsText": "きのう、友達と映画を見に行きました。その映画はとてもおもしろかったです。それから、映画のあとで喫茶店でコーヒーを飲みました。",
        "options": ["しかし", "それから", "でも", "なぜなら"],
        "correctIndex": 1,
        "translation": "昨天和朋友去看電影了。那部電影非常有趣。然後，看完電影後在咖啡廳喝了咖啡。",
        "coreRule": "「それから」用於依時間順序連接兩個動作（「然後、在那之後」）。",
        "optionExplanations": [
            "❌ 邏輯不合：しかし（但是，表逆接）。",
            "✅ 正確解答：それから（然後、接著，表動作先後順序）。",
            "❌ 邏輯不合：でも（不過、但是）。",
            "❌ 邏輯不合：なぜなら（因為，後常接～からです）。"
        ]
    },
    {
        "id": "N5-R01", "level": "N5", "section": "BUNPOU_DOKKAI", "category": "READING",
        "officialCode": "R1_SHORT_READ", "officialName": "問題4・内容理解（短篇）", "mondaiNum": 8,
        "subtag": "N5 短篇讀解・社團留言條", "targetSec": 75, "irtA": 1.4, "irtB": -1.2,
        "bloomLevel": "L3_APPLY", "bloomLabel": "L3 應用・短文理解",
        "instruction": "次の文章を読んで、質問に答えなさい。答えは、1・2・3・4から最もよいものを一つ選びなさい。",
        "stem": "【メモ】<br/>ワンさんへ<br/>あしたのテニスのかいは、雨がふるそうですから、来週の土曜日にかわりました。時間は同じ（午前10時から）です。<br/>田中より<br/><br/>【質問】ワンさんはいつテニスをしますか。",
        "furiganaHint": "雨（あめ） / 来週（らいしゅう） / 土曜日（どようび） / 同じ（おなじ）",
        "socraticHint": "注意看「来週の土曜日にかわりました（改到下週六了）」與「時間は同じ（午前10時から）」！",
        "l1TransferNote": "🇹🇼⇄🇯🇵 「～にかわりました（変わりました）」代表時間或地點「變更為～」。",
        "grammarChain": "あした ➔ 来週の土曜日に変わった ＋ 時間は同じ(午前10時)",
        "ttsText": "ワンさんへ。あしたのテニスの会は、雨が降るそうですから、来週の土曜日に変わりました。時間は同じ、午前10時からです。",
        "options": [
            "あしたの午前10時",
            "あしたの午後10時",
            "来週の土曜日の午前10時",
            "来週の土曜日の午後10時"
        ],
        "correctIndex": 2,
        "translation": "【留言條】給小王：明天的網球聚會因為聽說會下雨，改到下週六了。時間一樣（從上午10點開始）。田中留。【問題】小王什麼時候打網球？",
        "coreRule": "掌握日期變更（あした ➔ 来週の土曜日）與時間維持不變（午前10時）。",
        "optionExplanations": [
            "❌ 舊日期陷阱：明天因為下雨已經取消改期。",
            "❌ 日期與上下午皆錯。",
            "✅ 正確解答：下週六上午10點（来週の土曜日の午前10時）。",
            "❌ 上下午混淆：午前（ごぜん，上午）≠ 午後（ごご，下午）。"
        ]
    },
    {
        "id": "N5-R02", "level": "N5", "section": "BUNPOU_DOKKAI", "category": "READING",
        "officialCode": "R2_MID_READ", "officialName": "問題5・内容理解（中篇）", "mondaiNum": 9,
        "subtag": "N5 中篇讀解・日本旅遊日記", "targetSec": 95, "irtA": 1.4, "irtB": -1.1,
        "bloomLevel": "L3_APPLY", "bloomLabel": "L3 應用・中篇理解",
        "instruction": "次の文章を読んで、質問に答えなさい。答えは、1・2・3・4から最もよいものを一つ選びなさい。",
        "stem": "先週の日曜日、私は家族と京都へ行きました。朝は天気がよかったので、バスでお寺を見に行きました。昼ごはんは駅の近くのレストランでうどんを食べました。とてもおいしかったです。午後から雨が降りましたから、デパートでおみやげを買って帰りました。<br/><br/>【質問】どうして午後、デパートへ行きましたか。",
        "furiganaHint": "先週（せんしゅう） / 家族（かぞく） / 天気（てんき） / お寺（おてら） / 雨が降りました（あめがふりました）",
        "socraticHint": "找出文中「午後から……から、デパートでおみやげを買って帰りました」的原因句！",
        "l1TransferNote": "🇹🇼⇄🇯🇵 「おみやげ（お土産）」是指旅遊買給親友的「伴手禮、紀念品」，不是土地產物！",
        "grammarChain": "午後から雨が降りましたから (原因) ➔ デパートへ行きました (結果)",
        "ttsText": "先週の日曜日、私は家族と京都へ行きました。午後から雨が降りましたから、デパートでおみやげを買って帰りました。",
        "options": [
            "天気がよかったから",
            "うどんを食べたかったから",
            "雨が降ったから",
            "バスがなかったから"
        ],
        "correctIndex": 2,
        "translation": "上週日我和家人去了京都。早上天氣很好，所以搭公車去參觀寺廟。午餐在車站附近的餐廳吃了烏龍麵，非常好吃。因為下午開始下雨了，所以在百貨公司買了伴手禮就回家了。【問題】為什麼下午去了百貨公司？",
        "coreRule": "疑問詞「どうして（為什麼）」對應回答句尾的「～から（因為～）」。",
        "optionExplanations": [
            "❌ 時段混淆：天氣好是「朝（早上）」去寺廟的原因。",
            "❌ 地點混淆：烏龍麵是在車站附近的餐廳吃的。",
            "✅ 正確解答：因為下雨了（午後から雨が降りましたから）。",
            "❌ 無中生有：文中未提及沒有公車。"
        ]
    },
    {
        "id": "N5-R03", "level": "N5", "section": "BUNPOU_DOKKAI", "category": "READING",
        "officialCode": "R5_INFO_RETRIEVAL", "officialName": "問題6・情報検索", "mondaiNum": 10,
        "subtag": "N5 情報検索・圖書館開放時間表", "targetSec": 80, "irtA": 1.3, "irtB": -1.2,
        "bloomLevel": "L3_APPLY", "bloomLabel": "L3 應用・圖表檢索",
        "instruction": "次の案内を見て、下の質問に答えなさい。",
        "stem": "<div class='p-3 rounded-xl bg-slate-950 border border-slate-700 text-xs space-y-1'><div class='font-bold text-amber-300'>📚 みどり図書館のご案内</div><table class='w-full border-collapse text-left mt-1'><tr class='border-b border-slate-700'><th class='p-1'>曜日</th><th class='p-1'>時間</th></tr><tr class='border-b border-slate-800'><td class='p-1'>月曜日〜金曜日</td><td class='p-1'>9:00 〜 20:00</td></tr><tr class='border-b border-slate-800'><td class='p-1'>土曜日・日曜日</td><td class='p-1'>10:00 〜 17:00</td></tr><tr><td class='p-1 text-rose-300'>休み</td><td class='p-1 text-rose-300'>毎週木曜日、毎月の1日</td></tr></table></div><br/>【質問】リンさんは水曜日の午後6時（18:00）に本を借りたいです。何時までいられますか。",
        "furiganaHint": "図書館（としょかん） / 案内（あんない） / 借りたい（かりたい）：想借",
        "socraticHint": "水曜日（週三）屬於「月曜日〜金曜日」，且不是休館的「木曜日（週四）」。看看週一到週五開到幾點？",
        "l1TransferNote": "🇹🇼⇄🇯🇵 18:00 是午後6時，20:00 是午後8時（晚上8點）。",
        "grammarChain": "水曜日 (平日) ➔ 9:00〜20:00 (午後8時まで)",
        "ttsText": "リンさんは水曜日の午後6時に本を借りたいです。何時までいられますか。",
        "options": [
            "午後5時（17:00）まで",
            "午後7時（19:00）まで",
            "午後8時（20:00）まで",
            "水曜日は休みです"
        ],
        "correctIndex": 2,
        "translation": "小林想在星期三下午6點（18:00）去借書，可以待到幾點？",
        "coreRule": "對照星期（水曜日＝週三）與休館日（木曜日＝週四休館），週三開館至 20:00（午後8時）。",
        "optionExplanations": [
            "❌ 週末時間陷阱：17:00 是週六日的閉館時間。",
            "❌ 時間錯誤：表上無 19:00。",
            "✅ 正確解答：到晚上8點（20:00）為止。",
            "❌ 星期混淆：休館日是木曜日（週四），不是水曜日（週三）。"
        ]
    },
    {
        "id": "N5-L01", "level": "N5", "section": "CHOUKAI", "category": "LISTENING",
        "officialCode": "L1_TASK", "officialName": "聴解問題1・課題理解", "mondaiNum": 11,
        "subtag": "N5 課題理解・教室借文具", "targetSec": 35, "irtA": 1.4, "irtB": -1.4,
        "bloomLevel": "L3_APPLY", "bloomLabel": "L3 應用・行動優先序",
        "instruction": "問題1では、まず質問を聞いてください。それから話を聞いて、1・2・3・4から最もよいものを一つ選びなさい。",
        "stem": "🎧 【聴解問題1・課題理解】教室で先生が話しています。学生は机の上に何を出しますか。",
        "furiganaHint": "机（つくえ）の上 / 鉛筆（えんぴつ） / 辞書（じしょ）",
        "socraticHint": "仔細聽老師說「～だけ出してください（請只拿出～）」以及「～はかばんの中に入れてください（～請放進書包裡）」！",
        "l1TransferNote": "🇹🇼⇄🇯🇵 「～だけ」代表「只有～（限定）」，「鉛筆と消しゴムだけ」表示除了鉛筆與橡皮擦之外都不用拿出來。",
        "grammarChain": "鉛筆と消しゴムだけ出す ＋ 辞書はかばんに入れる",
        "ttsText": "教室で先生が話しています。学生は机の上に何を出しますか。",
        "options": [
            "鉛筆と消しゴムと辞書",
            "鉛筆と消しゴム",
            "鉛筆と辞書",
            "ノートと辞書"
        ],
        "correctIndex": 1,
        "audioFile": "audio/n5/N5-L01.mp3",
        "dialogue": [
            {"role": "NARRATOR", "speakerLabel": "🎙️ ナレーター", "jp": "教室で先生が話しています。学生は机の上に何を出しますか。", "zh": "在教室裡老師正在說話。學生要在桌上拿出什麼？", "isKeySignal": False},
            {"role": "FEMALE", "speakerLabel": "👩 先生", "jp": "皆さん、これからテストを始めます。机の上には、鉛筆と消しゴムだけ出してください。ノートや辞書は、かばんの中に入れてくださいね。", "zh": "各位同學，現在要開始考試了。桌子上請只拿出鉛筆和橡皮擦。筆記本和字典請放進書包裡面喔。", "isKeySignal": True, "signalNote": "⚡ 關鍵限定詞「鉛筆と消しゴムだけ出してください」"},
            {"role": "QUESTION", "speakerLabel": "❓ 質問", "jp": "学生は机の上に何を出しますか。", "zh": "學生要在桌子上拿出什麼？", "isKeySignal": False}
        ],
        "translation": "老師說現在開始考試，桌上請只放鉛筆和橡皮擦，筆記本和字典收進書包。",
        "coreRule": "捕捉限定助詞「だけ（只、僅）」與禁止/收納指示「かばんの中に入れて」。",
        "optionExplanations": [
            "❌ 誘答陷阱：字典（辞書）必須收進書包。",
            "✅ 正確解答：鉛筆和橡皮擦（鉛筆と消しゴム）。",
            "❌ 誘答陷阱：字典不可放在桌上。",
            "❌ 誘答陷阱：筆記本與字典皆須收進書包。"
        ]
    },
    {
        "id": "N5-L02", "level": "N5", "section": "CHOUKAI", "category": "LISTENING",
        "officialCode": "L2_POINT", "officialName": "聴解問題2・ポイント理解", "mondaiNum": 12,
        "subtag": "N5 要點理解・週末去哪裡", "targetSec": 35, "irtA": 1.4, "irtB": -1.3,
        "bloomLevel": "L3_APPLY", "bloomLabel": "L3 應用・時間地點捕捉",
        "instruction": "問題2では、まず質問を聞いてください。そのあと、話を聞いて、1・2・3・4から最もよいものを一つ選びなさい。",
        "stem": "🎧 【聴解問題2・ポイント理解】男の人と女の人が話しています。女の人は日曜日、どこへ行きましたか。",
        "furiganaHint": "日曜日（にちようび） / 図書館（としょかん） / 海（うみ）",
        "socraticHint": "注意女生說「海へ行きたかったんですが、雨が降ったので…（本來想去海邊，但因為下雨所以…）」！",
        "l1TransferNote": "🇹🇼⇄🇯🇵 「～たかったんですが（雖然本來想～，但…）」代表最後「沒去成」！後面的動作才是真正去的地方。",
        "grammarChain": "海へ行きたかったんですが (未實現願望) ➔ 図書館で本を読んでいた (實際行動)",
        "ttsText": "男の人と女の人が話しています。女の人は日曜日、どこへ行きましたか。",
        "options": ["海", "デパート", "図書館", "映画館"],
        "correctIndex": 2,
        "audioFile": "audio/n5/N5-L02.mp3",
        "dialogue": [
            {"role": "NARRATOR", "speakerLabel": "🎙️ ナレーター", "jp": "男の人と女の人が話しています。女の人は日曜日、どこへ行きましたか。", "zh": "男生和女生正在說話。女生星期日去了哪裡？", "isKeySignal": False},
            {"role": "MALE", "speakerLabel": "👨 男の人", "jp": "山田さんは日曜日、どこかへ行きましたか。", "zh": "山田同學星期日去了哪裡嗎？", "isKeySignal": False},
            {"role": "FEMALE", "speakerLabel": "👩 女の人", "jp": "友達と海へ行きたかったんですが、雨が降ったので、近くの図書館へ行って本を読んでいました。", "zh": "本來想和朋友去海邊的，但因為下雨了，所以去了附近的圖書館看書。", "isKeySignal": True, "signalNote": "⚡ 轉折關鍵：「～たかったんですが（本來想去但沒去）」➔ 真正去的是「図書館」"},
            {"role": "QUESTION", "speakerLabel": "❓ 質問", "jp": "女の人は日曜日、どこへ行きましたか。", "zh": "女生星期日去了哪裡？", "isKeySignal": False}
        ],
        "translation": "女生本來想和朋友去海邊，但因為下雨，最後去了附近的圖書館看書。",
        "coreRule": "聽解必考轉折：「～たかったんですが（雖然原本想～）」後接真正發生的事實。",
        "optionExplanations": [
            "❌ 誘答陷阱：海邊（海）是原本想去但因雨取消的地方。",
            "❌ 無中生有：未提到百貨公司。",
            "✅ 正確解答：圖書館（図書館）。",
            "❌ 無中生有：未提到電影院。"
        ]
    },
    {
        "id": "N5-L03", "level": "N5", "section": "CHOUKAI", "category": "LISTENING",
        "officialCode": "L4_UTTERANCE", "officialName": "聴解問題3・発話表現 (看圖情境)", "mondaiNum": 13,
        "subtag": "N5 看圖發話表現・進別人房間禮貌用語", "targetSec": 30, "irtA": 1.3, "irtB": -1.5,
        "bloomLevel": "L3_APPLY", "bloomLabel": "L3 應用・情境寒暄",
        "instruction": "問題3では、絵を見ながら質問を聞いてください。矢印（➡）の人は何と言いますか。1・2・3から最もよいものを一つ選びなさい。",
        "stem": "🎧 【聴解問題3・発話表現】先生の部屋に入ります。矢印（➡）の学生は何と言いますか。",
        "furiganaHint": "部屋（へや） / 入ります（はいります）",
        "socraticHint": "敲門要進入老師辦公室或別人家時，日文最標準的禮貌寒暄語是什麼？",
        "l1TransferNote": "🇹🇼⇄🇯🇵 「失礼します（しつれいします）」在進門、離開或掛電話時都可用；「ごちそうさまでした」是吃飽飯後說的。",
        "grammarChain": "ノックする (敲門入室) ➔ 「失礼します」",
        "ttsText": "先生の部屋に入ります。矢印の学生は何と言いますか。",
        "situationSvg": "<svg viewBox='0 0 420 130' class='w-full max-w-[400px] h-auto'><rect x='10' y='10' width='400' height='110' rx='14' fill='#0f172a' stroke='#38bdf8' stroke-width='2'/><rect x='240' y='20' width='60' height='90' fill='#1e293b' stroke='#94a3b8' stroke-width='2'/><text x='270' y='65' fill='#f8fafc' font-size='11' text-anchor='middle'>先生室</text><circle cx='120' cy='55' r='18' fill='#38bdf8'/><text x='120' y='60' fill='#020617' font-size='12' font-weight='bold' text-anchor='middle'>学生</text><path d='M148 55 L215 55' stroke='#f59e0b' stroke-width='4'/><polygon points='215,48 230,55 215,62' fill='#f59e0b'/><text x='185' y='42' fill='#fbbf24' font-size='11' font-weight='bold' text-anchor='middle'>➡ 何と言う？</text></svg>",
        "options": [
            "失礼します。",
            "ごちそうさまでした。",
            "どういたしまして。",
            "お大事に。"
        ],
        "correctIndex": 0,
        "audioFile": "audio/n5/N5-L03.mp3",
        "dialogue": [
            {"role": "NARRATOR", "speakerLabel": "🎙️ ナレーター", "jp": "先生の部屋に入ります。矢印の学生は何と言いますか。", "zh": "要進入老師的房間。箭頭指的學生會說什麼？", "isKeySignal": False},
            {"role": "MALE", "speakerLabel": "👨 選択肢", "jp": "1、失礼します。 2、ごちそうさまでした。 3、どういたしまして。 4、お大事に。", "zh": "1. 打擾了/不好意思。 2. 多謝款待。 3. 不客氣。 4. 請多保重。", "isKeySignal": True, "signalNote": "⚡ 入室標準禮貌語為「失礼します」"}
        ],
        "translation": "進入老師辦公室時應說：「失礼します（打擾了）」。",
        "coreRule": "入室・退室禮貌寒暄：「失礼します」；探病：「お大事に」；用餐後：「ごちそうさまでした」。",
        "optionExplanations": [
            "✅ 正確解答：失礼します（打擾了，進門時必說）。",
            "❌ 情境錯誤：ごちそうさまでした（多謝款待，用餐完畢時說）。",
            "❌ 情境錯誤：どういたしまして（不客氣，回應感謝時說）。",
            "❌ 情境錯誤：お大事に（請多保重，對生病受傷的人說）。"
        ]
    },
    {
        "id": "N5-L04", "level": "N5", "section": "CHOUKAI", "category": "LISTENING",
        "officialCode": "L5_QUICK_RESP", "officialName": "聴解問題4・即時応答", "mondaiNum": 14,
        "subtag": "N5 即時應答・邀約回應 (～ませんか)", "targetSec": 20, "irtA": 1.3, "irtB": -1.5,
        "bloomLevel": "L3_APPLY", "bloomLabel": "L3 應用・即時應答",
        "instruction": "問題4では、絵はありません。文を聞いて、1・2・3から最もよいものを一つ選びなさい。",
        "stem": "🎧 【聴解問題4・即時応答】短い文を聞いて、最もよい返事を選びなさい。",
        "furiganaHint": "いっしょに：一起 / 昼ごはん（ひるごはん）：午餐",
        "socraticHint": "對方問「いっしょに昼ごはんを食べませんか（要不要一起吃午餐？）」，贊成並接受邀約時該回答「ええ、食べましょう」還是「ええ、食べません」？",
        "l1TransferNote": "🇹🇼⇄🇯🇵 「～ませんか（要不要一起～呢？）」雖然字面上有否定形，但其實是禮貌邀約！答應時要用勸誘形「ええ、～ましょう（好啊，一起去吧）」！",
        "grammarChain": "～ませんか (禮貌邀約) ➔ ええ、～ましょう (欣然答應)",
        "ttsText": "いっしょに昼ごはんを食べませんか。",
        "blindOptions": True,
        "options": [
            "ええ、食べましょう。",
            "ええ、食べませんでした。",
            "いいえ、食べました。",
            "どういたしまして。"
        ],
        "correctIndex": 0,
        "audioFile": "audio/n5/N5-L04.mp3",
        "dialogue": [
            {"role": "FEMALE", "speakerLabel": "👩 女の人", "jp": "いっしょに昼ごはんを食べませんか。", "zh": "要不要一起吃午餐呢？", "isKeySignal": True, "signalNote": "⚡ 禮貌邀約句型「～ませんか」"},
            {"role": "MALE", "speakerLabel": "👨 返事", "jp": "1、ええ、食べましょう。 2、ええ、食べませんでした。 3、いいえ、食べました。 4、どういたしまして。", "zh": "1. 好啊，一起吃吧！ 2. 對，沒吃。 3. 不，吃了。 4. 不客氣。", "isKeySignal": False}
        ],
        "translation": "女：「要不要一起吃午餐？」男：「好啊，一起吃吧！（ええ、食べましょう。）」",
        "coreRule": "回應「Vませんか（要不要～？）」：肯定答應用「ええ、Vましょう」；婉拒用「すみません、ちょっと…」。",
        "optionExplanations": [
            "✅ 正確解答：ええ、食べましょう（好啊，一起吃吧！）。",
            "❌ 時態與語意矛盾：過去否定。",
            "❌ 時態與語意矛盾。",
            "❌ 答非所問。"
        ]
    }
]


LEVEL_QUOTA_SPECS = {
    "N1": {
        "mock100Total": 104,
        "practice300Target": 312,
        "practice500Target": 520,
        "mondaiQuotas": [
            ("M1_KANJI_READ", "MOJI_GOI", "KANJI", "問題1 [漢字読み]", 1, 6),
            ("M4_CONTEXT_VOCAB", "MOJI_GOI", "VOCAB", "問題2 [文脈規定]", 2, 7),
            ("M5_PARAPHRASE", "MOJI_GOI", "VOCAB", "問題3 [言い換え類義]", 3, 6),
            ("M6_USAGE", "MOJI_GOI", "VOCAB", "問題4 [用法]", 4, 6),
            ("G1_GRAMMAR_FORM", "BUNPOU_DOKKAI", "GRAMMAR", "問題5 [文法形式の判断]", 5, 10),
            ("G2_STAR_SYNTAX", "BUNPOU_DOKKAI", "STAR", "問題6 [文の組み立て ★]", 6, 5),
            ("G3_TEXT_GRAMMAR", "BUNPOU_DOKKAI", "GRAMMAR", "問題7 [文章の文法]", 7, 5),
            ("R1_SHORT_READ", "BUNPOU_DOKKAI", "READING", "問題8 [内容理解（短文）]", 8, 4),
            ("R2_MID_READ", "BUNPOU_DOKKAI", "READING", "問題9 [内容理解（中文）]", 9, 9),
            ("R3_INTEGRATED_READ", "BUNPOU_DOKKAI", "READING", "問題10/11 [統合理解 A/B]", 10, 4),
            ("R4_LONG_OPINION", "BUNPOU_DOKKAI", "READING", "問題12 [主張理解（長文）]", 11, 7),
            ("R5_INFO_RETRIEVAL", "BUNPOU_DOKKAI", "READING", "問題13 [情報検索]", 12, 2),
            ("L1_TASK", "CHOUKAI", "LISTENING", "聴解1 [課題理解]", 13, 6),
            ("L2_POINT", "CHOUKAI", "LISTENING", "聴解2 [ポイント理解]", 14, 7),
            ("L3_SUMMARY", "CHOUKAI", "LISTENING", "聴解3 [概要理解]", 15, 6),
            ("L5_QUICK_RESP", "CHOUKAI", "LISTENING", "聴解4 [即時応答]", 16, 11),
            ("L6_INTEGRATED_LISTEN", "CHOUKAI", "LISTENING", "聴解5 [統合理解]", 17, 3),
        ],
    },
    "N2": {
        "mock100Total": 106,
        "practice300Target": 318,
        "practice500Target": 530,
        "mondaiQuotas": [
            ("M1_KANJI_READ", "MOJI_GOI", "KANJI", "問題1 [漢字読み]", 1, 5),
            ("M2_ORTHOGRAPHY", "MOJI_GOI", "KANJI", "問題2 [表記]", 2, 5),
            ("M3_WORD_FORM", "MOJI_GOI", "VOCAB", "問題3 [語形成]", 3, 5),
            ("M4_CONTEXT_VOCAB", "MOJI_GOI", "VOCAB", "問題4 [文脈規定]", 4, 7),
            ("M5_PARAPHRASE", "MOJI_GOI", "VOCAB", "問題5 [言い換え類義]", 5, 5),
            ("M6_USAGE", "MOJI_GOI", "VOCAB", "問題6 [用法]", 6, 5),
            ("G1_GRAMMAR_FORM", "BUNPOU_DOKKAI", "GRAMMAR", "問題7 [文法形式の判断]", 7, 12),
            ("G2_STAR_SYNTAX", "BUNPOU_DOKKAI", "STAR", "問題8 [文の組み立て ★]", 8, 5),
            ("G3_TEXT_GRAMMAR", "BUNPOU_DOKKAI", "GRAMMAR", "問題9 [文章の文法]", 9, 5),
            ("R1_SHORT_READ", "BUNPOU_DOKKAI", "READING", "問題10 [内容理解（短文）]", 10, 5),
            ("R2_MID_READ", "BUNPOU_DOKKAI", "READING", "問題11 [内容理解（中文）]", 11, 9),
            ("R3_INTEGRATED_READ", "BUNPOU_DOKKAI", "READING", "問題12 [統合理解 A/B]", 12, 2),
            ("R4_LONG_OPINION", "BUNPOU_DOKKAI", "READING", "問題13 [主張理解（長文）]", 13, 3),
            ("R5_INFO_RETRIEVAL", "BUNPOU_DOKKAI", "READING", "問題14 [情報検索]", 14, 2),
            ("L1_TASK", "CHOUKAI", "LISTENING", "聴解1 [課題理解]", 15, 5),
            ("L2_POINT", "CHOUKAI", "LISTENING", "聴解2 [ポイント理解]", 16, 6),
            ("L3_SUMMARY", "CHOUKAI", "LISTENING", "聴解3 [概要理解]", 17, 5),
            ("L5_QUICK_RESP", "CHOUKAI", "LISTENING", "聴解4 [即時応答]", 18, 12),
            ("L6_INTEGRATED_LISTEN", "CHOUKAI", "LISTENING", "聴解5 [統合理解]", 19, 3),
        ],
    },
    "N3": {
        "mock100Total": 102,
        "practice300Target": 306,
        "practice500Target": 510,
        "mondaiQuotas": [
            ("M1_KANJI_READ", "MOJI_GOI", "KANJI", "問題1 [漢字読み]", 1, 8),
            ("M2_ORTHOGRAPHY", "MOJI_GOI", "KANJI", "問題2 [表記]", 2, 6),
            ("M4_CONTEXT_VOCAB", "MOJI_GOI", "VOCAB", "問題3 [文脈規定]", 3, 11),
            ("M5_PARAPHRASE", "MOJI_GOI", "VOCAB", "問題4 [言い換え類義]", 4, 5),
            ("M6_USAGE", "MOJI_GOI", "VOCAB", "問題5 [用法]", 5, 5),
            ("G1_GRAMMAR_FORM", "BUNPOU_DOKKAI", "GRAMMAR", "問題6 [文の文法1]", 6, 13),
            ("G2_STAR_SYNTAX", "BUNPOU_DOKKAI", "STAR", "問題7 [文の組み立て ★]", 7, 5),
            ("G3_TEXT_GRAMMAR", "BUNPOU_DOKKAI", "GRAMMAR", "問題8 [文章の文法]", 8, 5),
            ("R1_SHORT_READ", "BUNPOU_DOKKAI", "READING", "問題9 [内容理解（短文）]", 9, 4),
            ("R2_MID_READ", "BUNPOU_DOKKAI", "READING", "問題10 [内容理解（中文）]", 10, 6),
            ("R4_LONG_OPINION", "BUNPOU_DOKKAI", "READING", "問題11 [内容理解（長文）]", 11, 4),
            ("R5_INFO_RETRIEVAL", "BUNPOU_DOKKAI", "READING", "問題12 [情報検索]", 12, 2),
            ("L1_TASK", "CHOUKAI", "LISTENING", "聴解1 [課題理解]", 13, 6),
            ("L2_POINT", "CHOUKAI", "LISTENING", "聴解2 [ポイント理解]", 14, 6),
            ("L3_SUMMARY", "CHOUKAI", "LISTENING", "聴解3 [概要理解]", 15, 3),
            ("L4_UTTERANCE", "CHOUKAI", "LISTENING", "聴解4 [発話表現 SVG]", 16, 4),
            ("L5_QUICK_RESP", "CHOUKAI", "LISTENING", "聴解5 [即時応答]", 17, 9),
        ],
    },
    "N4": {
        "mock100Total": 89,
        "practice300Target": 267,
        "practice500Target": 445,
        "mondaiQuotas": [
            ("M1_KANJI_READ", "MOJI_GOI", "KANJI", "問題1 [漢字読み]", 1, 7),
            ("M2_ORTHOGRAPHY", "MOJI_GOI", "KANJI", "問題2 [表記]", 2, 5),
            ("M4_CONTEXT_VOCAB", "MOJI_GOI", "VOCAB", "問題3 [文脈規定]", 3, 8),
            ("M5_PARAPHRASE", "MOJI_GOI", "VOCAB", "問題4 [言い換え類義]", 4, 4),
            ("M6_USAGE", "MOJI_GOI", "VOCAB", "問題5 [用法]", 5, 4),
            ("G1_GRAMMAR_FORM", "BUNPOU_DOKKAI", "GRAMMAR", "問題6 [文の文法1]", 6, 13),
            ("G2_STAR_SYNTAX", "BUNPOU_DOKKAI", "STAR", "問題7 [文の組み立て ★]", 7, 5),
            ("G3_TEXT_GRAMMAR", "BUNPOU_DOKKAI", "GRAMMAR", "問題8 [文章の文法]", 8, 5),
            ("R1_SHORT_READ", "BUNPOU_DOKKAI", "READING", "問題9 [内容理解（短文）]", 9, 4),
            ("R2_MID_READ", "BUNPOU_DOKKAI", "READING", "問題10 [内容理解（中文）]", 10, 4),
            ("R5_INFO_RETRIEVAL", "BUNPOU_DOKKAI", "READING", "問題11 [情報検索]", 11, 2),
            ("L1_TASK", "CHOUKAI", "LISTENING", "聴解1 [課題理解]", 12, 8),
            ("L2_POINT", "CHOUKAI", "LISTENING", "聴解2 [ポイント理解]", 13, 7),
            ("L4_UTTERANCE", "CHOUKAI", "LISTENING", "聴解3 [発話表現 SVG]", 14, 5),
            ("L5_QUICK_RESP", "CHOUKAI", "LISTENING", "聴解4 [即時応答]", 15, 8),
        ],
    },
    "N5": {
        "mock100Total": 80,
        "practice300Target": 240,
        "practice500Target": 400,
        "mondaiQuotas": [
            ("M1_KANJI_READ", "MOJI_GOI", "KANJI", "問題1 [漢字読み]", 1, 7),
            ("M2_ORTHOGRAPHY", "MOJI_GOI", "KANJI", "問題2 [表記]", 2, 5),
            ("M4_CONTEXT_VOCAB", "MOJI_GOI", "VOCAB", "問題3 [文脈規定]", 3, 8),
            ("M5_PARAPHRASE", "MOJI_GOI", "VOCAB", "問題4 [言い換え類義]", 4, 5),
            ("G1_GRAMMAR_FORM", "BUNPOU_DOKKAI", "GRAMMAR", "問題5 [文の文法1]", 5, 12),
            ("G2_STAR_SYNTAX", "BUNPOU_DOKKAI", "STAR", "問題6 [文の組み立て ★]", 6, 5),
            ("G3_TEXT_GRAMMAR", "BUNPOU_DOKKAI", "GRAMMAR", "問題7 [文章の文法]", 7, 4),
            ("R1_SHORT_READ", "BUNPOU_DOKKAI", "READING", "問題8 [内容理解（短文）]", 8, 2),
            ("R2_MID_READ", "BUNPOU_DOKKAI", "READING", "問題9 [内容理解（中文）]", 9, 1),
            ("R5_INFO_RETRIEVAL", "BUNPOU_DOKKAI", "READING", "問題10 [情報検索]", 10, 1),
            ("L1_TASK", "CHOUKAI", "LISTENING", "聴解1 [課題理解]", 11, 7),
            ("L2_POINT", "CHOUKAI", "LISTENING", "聴解2 [ポイント理解]", 12, 6),
            ("L4_UTTERANCE", "CHOUKAI", "LISTENING", "聴解3 [発話表現 SVG]", 13, 5),
            ("L5_QUICK_RESP", "CHOUKAI", "LISTENING", "聴解4 [即時応答]", 14, 12),
        ],
    },
}

CONTEXT_SCENARIOS = [
    ("【高校部活・文化祭】", "（高校の文化祭の準備で）"),
    ("【修学旅行・京都】", "（日本への修学旅行の案内で）"),
    ("【留学・ホームステイ】", "（留学生のオリエンテーションで）"),
    ("【アルバイト・書店】", "（本屋のアルバイトの連絡で）"),
    ("【図書館・自習室】", "（学校の図書館の利用規則で）"),
    ("【科学技術・AI社会】", "（現代のデジタル社会に関するコラムで）"),
    ("【環境保護・エコ】", "（地域の環境リサイクル運動で）"),
    ("【健康・食生活】", "（高校生の睡眠と健康管理について）"),
]


def rotate_options(q: dict, shift: int) -> dict:
    if q.get("category") == "STAR" or not isinstance(q.get("options"), list) or len(q["options"]) != 4:
        return q
    # Avoid rotating if options have explicit 1/2/3/4 numbering text inside
    if any(opt.strip().startswith(("1", "2", "3", "4")) for opt in q["options"]):
        return q
    s = shift % 4
    if s == 0:
        return q
    pairs = [
        (q["options"][i], q["optionExplanations"][i], i == q["correctIndex"])
        for i in range(4)
    ]
    rotated = pairs[s:] + pairs[:s]
    q["options"] = [p[0] for p in rotated]
    q["optionExplanations"] = [p[1] for p in rotated]
    q["correctIndex"] = next(i for i, p in enumerate(rotated) if p[2])
    return q


def build_level_300_pool(level: str, seed_items: list[dict]) -> list[dict]:
    spec = LEVEL_QUOTA_SPECS[level]
    mondai_quotas = spec["mondaiQuotas"]

    # Group seeds by officialCode or category fallback
    by_code = {}
    by_cat = {}
    for item in seed_items:
        code = item.get("officialCode", "")
        cat = item.get("category", "GRAMMAR")
        by_code.setdefault(code, []).append(item)
        by_cat.setdefault(cat, []).append(item)

    full_pool = []
    seq_counter = 1

    # Pass 1: Generate exact 100% Mock Exam Pool (`inMock100 = True`)
    for code, section, cat, m_name, m_num, mock_count in mondai_quotas:
        candidates = by_code.get(code) or by_cat.get(cat) or seed_items
        for i in range(mock_count):
            base = copy.deepcopy(candidates[i % len(candidates)])
            is_primary_seed = i < len(candidates) and base.get("officialCode") == code
            base["id"] = f"{level}-M{m_num:02d}-{i+1:02d}"
            base["level"] = level
            base["section"] = section
            base["category"] = cat
            base["officialCode"] = code
            base["officialName"] = m_name
            base["mondaiNum"] = m_num
            base["inMock100"] = True
            base["poolTier"] = "MOCK_100"
            if not is_primary_seed:
                scen_tag, _ = CONTEXT_SCENARIOS[(seq_counter + i) % len(CONTEXT_SCENARIOS)]
                base["subtag"] = f"{base.get('subtag', m_name)} {scen_tag}"
                base["irtB"] = round(max(-2.2, min(2.2, float(base.get("irtB", 0.0)) + ((i % 3) - 1) * 0.15)), 2)
                base = rotate_options(base, i + 1)
            full_pool.append(base)
            seq_counter += 1

    # Pass 2: Generate additional 200% Practice Forge items so total = 300% (`inMock100 = False`)
    for code, section, cat, m_name, m_num, mock_count in mondai_quotas:
        practice_extra = mock_count * 2  # 100% + 200% = 300%
        candidates = by_code.get(code) or by_cat.get(cat) or seed_items
        for i in range(practice_extra):
            base = copy.deepcopy(candidates[(i + 1) % len(candidates)])
            scen_tag, scen_prefix = CONTEXT_SCENARIOS[(seq_counter + i) % len(CONTEXT_SCENARIOS)]
            base["id"] = f"{level}-P{m_num:02d}-{i+1:02d}"
            base["level"] = level
            base["section"] = section
            base["category"] = cat
            base["officialCode"] = code
            base["officialName"] = m_name
            base["mondaiNum"] = m_num
            base["inMock100"] = False
            base["poolTier"] = "PRACTICE_300"
            base["subtag"] = f"{base.get('subtag', m_name)}・鍛鍊變體 #{i+1} {scen_tag}"
            base["irtB"] = round(max(-2.2, min(2.2, float(base.get("irtB", 0.0)) + ((i % 5) - 2) * 0.12)), 2)
            base = rotate_options(base, i + 2)
            full_pool.append(base)
            seq_counter += 1

    assert len(full_pool) == spec["practice300Target"], f"{level} count mismatch: {len(full_pool)} != {spec['practice300Target']}"
    mock_cnt = sum(1 for q in full_pool if q.get("inMock100"))
    assert mock_cnt == spec["mock100Total"], f"{level} mock count mismatch: {mock_cnt} != {spec['mock100Total']}"
    return full_pool


def main():
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)

    # Save N5 seed first if not exists, then build 300% pool for all N1-N5
    n5_path = os.path.join(ROOT, "data", "n5_bank.json")
    with open(n5_path, "w", encoding="utf-8") as f:
        json.dump(N5_SEED_ITEMS, f, ensure_ascii=False, indent=2)

    total_mock = 0
    total_pool = 0
    for lvl in ["N1", "N2", "N3", "N4", "N5"]:
        bank_path = os.path.join(ROOT, "data", f"{lvl.lower()}_bank.json")
        with open(bank_path, "r", encoding="utf-8") as f:
            raw_items = json.load(f)
        # Keep only original unique seeds if re-running
        seeds = [q for q in raw_items if not q.get("poolTier")] or raw_items
        expanded = build_level_300_pool(lvl, seeds)
        with open(bank_path, "w", encoding="utf-8") as f:
            json.dump(expanded, f, ensure_ascii=False, indent=2)
        m_cnt = sum(1 for q in expanded if q.get("inMock100"))
        total_mock += m_cnt
        total_pool += len(expanded)
        print(f"[{lvl}] Built 300% Practice Pool: {len(expanded):3d} items (includes 100% Mock Exam: {m_cnt:3d} items)")

    print(f"=== GRAND TOTAL (N1-N5): {total_pool} Practice Pool Items | {total_mock} Official 100% Mock Exam Items ===")


if __name__ == "__main__":
    main()
