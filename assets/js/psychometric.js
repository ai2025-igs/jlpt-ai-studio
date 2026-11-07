/*************************************************************************
 * psychometric.js
 * 1. JLPT N1-N4 Official Exam Passing Gates & Sectional Structure
 * 2. 2PL-IRT Bayesian Ability (Theta) Estimator & Veto Redline Defense
 * 3. FSRS v5 Spaced Repetition Scheduler (Stability S, Difficulty D)
 * 4. Zimmerman SRL Confidence Calibration & Bloom's Taxonomy Analytics
 *************************************************************************/

const LEVEL_SPECS = {
  N1: {
    level: 'N1',
    badge: 'N1 最高級',
    color: 'rose',
    sectionsMode: '2-SECTION (110m 筆試 + 55m 聽解)',
    timerSpec: '筆試 110m ｜ 聽解 55m',
    passTotal: 100,
    maxTotal: 180,
    combinedWrittenGate: false,
    cutoffs: { lang: 19, read: 19, listen: 19 },
    vocabScale: '~2,000 漢字 / ~10,000 詞',
    desc: '二節制測驗（總分 ≥100/180，言語知識・讀解・聽解三科皆須 ≥19/60）'
  },
  N2: {
    level: 'N2',
    badge: 'N2 進階主力艦',
    color: 'amber',
    sectionsMode: '2-SECTION (105m 筆試 + 50m 聽解)',
    timerSpec: '筆試 105m ｜ 聽解 50m',
    passTotal: 90,
    maxTotal: 180,
    combinedWrittenGate: false,
    cutoffs: { lang: 19, read: 19, listen: 19 },
    vocabScale: '~1,000 漢字 / ~6,000 詞',
    desc: '二節制測驗（總分 ≥90/180，言語知識・讀解・聽解三科皆須 ≥19/60）'
  },
  N3: {
    level: 'N3',
    badge: 'N3 中級橋樑',
    color: 'sky',
    sectionsMode: '3-SECTION (30m 字彙 + 70m 文法讀解 + 40m 聽解)',
    timerSpec: '字彙 30m ｜ 文法讀解 70m ｜ 聽解 40m',
    passTotal: 95,
    maxTotal: 180,
    combinedWrittenGate: false,
    cutoffs: { lang: 19, read: 19, listen: 19 },
    vocabScale: '~650 漢字 / ~3,750 詞',
    desc: '三節制測驗（總分 ≥95/180，言語知識・讀解・聽解三科皆須 ≥19/60）'
  },
  N4: {
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
  },
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
  }
};

const PEDAGOGICAL_THEORIES = [
  {
    code: 'P1',
    title: "Bloom's Revised Taxonomy (布魯姆六階認知鷹架)",
    scholar: 'Anderson & Krathwohl (2001)',
    summary: '將每道題目標註 L1 記憶（字音/表記）➔ L2 理解（文脈/類義）➔ L3 應用（用法/發話）➔ L4 分析（★星號語法樹/克漏字）➔ L5 評鑑（A/B 統合比較/多方討論）➔ L6 創造（AI 延伸造句）。'
  },
  {
    code: 'P2',
    title: 'Zimmerman 3-Phase SRL Confidence Calibration (自我調節與信心校準)',
    scholar: 'Zimmerman (2002)',
    summary: '作答前強制設定 25%~100% 把握度，量化「主觀信心 - 實際正確率」校準差，精準攔截最致命的「高信心盲點 (High-Confidence Blindspot)」。'
  },
  {
    code: 'P3',
    title: 'Sweller Cognitive Load & Fading Scaffolding (認知負荷與漸進鷹架)',
    scholar: 'Sweller (1988, 2011)',
    summary: '提供「🌱 教學鷹架模式」（開啟分級振假名、蘇格拉底產婆提示、排除1個誘答項）與「⚔️ 考場實戰模式」（全盲聽、嚴格配速計時）一鍵切換。'
  },
  {
    code: 'P4',
    title: 'Odlin Contrastive Analysis & L1 Kanji Transfer (台日漢字正負遷移理論)',
    scholar: 'Odlin (1989)',
    summary: '專為台灣高中生設計「🇹🇼⇄🇯🇵 漢字母語正負遷移透鏡」，拆解國語清濁音干擾（妥協 だきょう）、同形異義假朋友（我慢・手紙）與助詞格關係盲區。'
  },
  {
    code: 'P5',
    title: 'Paivio Dual-Coding Theory (視覺與聽覺雙碼理論)',
    scholar: 'Paivio (1986)',
    summary: 'N3/N4 聽解「発話表現」配備 SVG 情境角色箭頭卡；情報検索配備結構化傳單表格；聽解配備 24 段動態頻譜與男女雙聲道色標。'
  },
  {
    code: 'P6',
    title: 'Worked Example & Syntactic Chunking (工作範例與語塊接續鏈)',
    scholar: 'Miller (1956); Sweller',
    summary: '針對「＿ ＿ ★ ＿」星號排句題，提供 4 格互動沙盒與「🔗 語法接續鏈圖解」，訓練從句尾逆向推導助詞與動詞活用接續。'
  },
  {
    code: 'P7',
    title: 'Bjork Desirable Difficulties & Interleaving (必要難度與交錯檢索)',
    scholar: 'Bjork & Bjork (2011)',
    summary: '透過跨題型交錯練習與「🙈 考場盲聽防呆遮罩 (Poka-Yoke)」，防止視覺文字搶奪聽覺工作記憶。'
  },
  {
    code: 'P8',
    title: 'Lord 2PL-IRT + Jarrett Ye FSRS v5 (項目反應理論與自由間隔重複)',
    scholar: 'Lord (1980); Jarrett Ye (2023)',
    summary: '即時推估 /180 量尺分數與單科 19 分死亡紅線風險，並根據記憶穩定度 S 與難度 D 排定 T+1d / T+3d / T+14d 最佳複習時機。'
  }
];

function compute2PLProbability(theta, a = 1.5, b = 0.0) {
  return 1.0 / (1.0 + Math.exp(-a * (theta - b)));
}

function estimateIRTTheta(records, questionMap) {
  if (!records || records.length === 0) return 0.0;
  // EAP / MAP estimation over grid [-2.5, +2.5] with N(0, 1) prior
  let bestTheta = 0.0;
  let num = 0.0;
  let den = 0.0;

  for (let t = -2.5; t <= 2.5; t += 0.1) {
    // Prior log-density
    let logL = -0.5 * t * t;
    for (const r of records) {
      const q = questionMap[r.questionId];
      const a = q?.irtA || 1.5;
      const b = q?.irtB || 0.2;
      const p = compute2PLProbability(t, a, b);
      // Weight by SRL confidence calibration
      const effY = r.isCorrect ? (r.confidence >= 70 ? 1.0 : 0.85) : (r.confidence >= 75 ? 0.0 : 0.1);
      logL += effY * Math.log(Math.max(1e-6, p)) + (1 - effY) * Math.log(Math.max(1e-6, 1 - p));
    }
    const w = Math.exp(Math.max(-60, logL));
    num += t * w;
    den += w;
  }
  bestTheta = den > 0 ? num / den : 0.0;
  return Number(bestTheta.toFixed(2));
}

function computeFSRSUpdate(prevCard, isCorrect, confidence, scriptPeeked) {
  const effConf = scriptPeeked ? Math.min(confidence, 50) : confidence;
  // Rating: 1=Again (Blindspot/Gap), 2=Hard (Fragile), 3=Good, 4=Easy (Mastery)
  let rating = 1;
  let srlType = 'GAP';
  let srlLabel = '🔧 基礎觀念缺口 (Knowledge Gap)';
  let srlBadgeClass = 'bg-sky-500/20 text-sky-300 border border-sky-500/40';
  let fsrsTag = 'T+1d';
  let fsrsDesc = 'FSRS v5 排程：尚未熟悉此考點，建議熟讀下方核心規則並排入 T+1d 重練。';

  if (isCorrect && effConf >= 70) {
    rating = effConf >= 90 ? 4 : 3;
    srlType = 'MASTERY';
    srlLabel = '✅ 穩固精通 (Mastery)';
    srlBadgeClass = 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40';
    fsrsTag = rating === 4 ? 'T+14d' : 'T+7d';
    fsrsDesc = `FSRS v5 排程：觀念穩固且信心匹配，排入 ${fsrsTag} 長期記憶維護。`;
  } else if (isCorrect && effConf < 70) {
    rating = 2;
    srlType = 'FRAGILE';
    srlLabel = '⚠️ 脆弱正確 (Fragile Correct)';
    srlBadgeClass = 'bg-amber-500/20 text-amber-300 border border-amber-500/40';
    fsrsTag = 'T+3d';
    fsrsDesc = 'FSRS v5 排程：雖答對但把握度偏低（或曾開啟提示/逐字稿），排入 T+3d 鞏固佇列！';
  } else if (!isCorrect && effConf >= 70) {
    rating = 1;
    srlType = 'BLINDSPOT';
    srlLabel = '🚨 高信心盲點 (High-Confidence Blindspot)';
    srlBadgeClass = 'bg-rose-500/25 text-rose-300 border border-rose-500/50';
    fsrsTag = 'T+1d 優先';
    fsrsDesc = 'FSRS v5 排程：極危險的「以為自己懂卻掉入誘答陷阱」！強制鎖定 T+1d 第一優先矯正。';
  }

  // FSRS v5 simplified stability S (days) and difficulty D (1..10)
  const prevS = prevCard?.stability || 1.0;
  const prevD = prevCard?.difficulty || 5.0;
  const nextD = Math.min(10, Math.max(1, Number((prevD - 0.6 * (rating - 3)).toFixed(2))));
  let nextS = prevS;
  if (rating === 1) {
    nextS = 1.0;
  } else if (rating === 2) {
    nextS = Math.max(3.0, Number((prevS * 1.4).toFixed(1)));
  } else if (rating === 3) {
    nextS = Math.max(7.0, Number((prevS * 2.2).toFixed(1)));
  } else {
    nextS = Math.max(14.0, Number((prevS * 3.1).toFixed(1)));
  }

  return {
    rating,
    srlType,
    srlLabel,
    srlBadgeClass,
    fsrsTag,
    fsrsDesc,
    stability: nextS,
    difficulty: nextD,
    effConf
  };
}

function computeLevelIRTScores(levelCode, records, questionMap) {
  const spec = LEVEL_SPECS[levelCode] || LEVEL_SPECS.N2;
  if (!records || records.length === 0) {
    return {
      hasData: false,
      spec,
      theta: 0.0,
      estLang: null,
      estRead: null,
      estWritten: null,
      estListen: null,
      estTotal: null,
      passProb: null,
      vetoAlert: null
    };
  }

  const theta = estimateIRTTheta(records, questionMap);
  const langRecs = records.filter(r => ['KANJI', 'VOCAB', 'GRAMMAR', 'STAR'].includes(r.category));
  const readRecs = records.filter(r => r.category === 'READING');
  const listenRecs = records.filter(r => r.category === 'LISTENING');

  const calcRatio = (arr) => {
    if (arr.length === 0) {
      // Fall back to global theta probability at b=0.2
      return compute2PLProbability(theta, 1.4, 0.2);
    }
    const sum = arr.reduce((acc, r) => {
      if (r.isCorrect) return acc + (r.confidence >= 70 ? 1.0 : 0.86);
      return acc + (r.confidence >= 75 ? 0.0 : 0.12);
    }, 0);
    return Math.min(0.98, Math.max(0.1, sum / arr.length));
  };

  const langRatio = calcRatio(langRecs);
  const readRatio = calcRatio(readRecs);
  const listenRatio = calcRatio(listenRecs);

  const estLang = Math.round(langRatio * 60);
  const estRead = Math.round(readRatio * 60);
  const estWritten = estLang + estRead;
  const estListen = Math.round(listenRatio * 60);
  const estTotal = estWritten + estListen;

  // Check sectional veto risk (< 22/60 or < 42/120 for N4)
  let vetoAlert = null;
  let vetoPenalty = 0;

  if (spec.combinedWrittenGate) {
    if (estWritten < 38) {
      vetoPenalty += 2.2;
      vetoAlert = `🚨 言語知識+讀解預估 ${estWritten}/120（低於 N4 合併門檻 38 分）！`;
    } else if (estWritten < 44) {
      vetoAlert = `⚠️ 言語知識+讀解預估 ${estWritten}/120，逼近 38 分門檻紅線！`;
    }
    if (estListen < 19) {
      vetoPenalty += 2.2;
      vetoAlert = `🚨 聽解單科預估 ${estListen}/60（低於 19 分單科淘汰紅線）！`;
    } else if (estListen < 22) {
      vetoAlert = `⚠️ 聽解單科預估 ${estListen}/60，逼近 19 分死亡紅線（系統已將聽解抽樣權重調升至 70%）！`;
    }
  } else {
    if (estLang < 19 || estRead < 19 || estListen < 19) {
      vetoPenalty += 2.4;
      const weakSec = estListen < 19 ? `聽解 (${estListen}/60)` : estRead < 19 ? `讀解 (${estRead}/60)` : `言語知識 (${estLang}/60)`;
      vetoAlert = `🚨 單科否決警報：${weakSec} 低於官方 19 分合格底線！`;
    } else if (estLang < 22 || estRead < 22 || estListen < 22) {
      const nearSec = estListen < 22 ? `聽解 (${estListen}/60)` : estRead < 22 ? `讀解 (${estRead}/60)` : `言語知識 (${estLang}/60)`;
      vetoAlert = `⚠️ 臨界預警：${nearSec} 逼近 19 分死亡紅線（已啟動 70% 弱點防禦加權）！`;
    }
  }

  const logit = (estTotal - spec.passTotal) / 11.5 - vetoPenalty;
  const passProb = Math.min(99, Math.max(4, Math.round((1 / (1 + Math.exp(-logit))) * 100)));

  return {
    hasData: true,
    spec,
    theta,
    estLang,
    estRead,
    estWritten,
    estListen,
    estTotal,
    passProb,
    vetoAlert
  };
}

const OFFICIAL_BLUEPRINT = {
  "levelOrder": ["N1", "N2", "N3", "N4", "N5"],
  "levels": {
    "N1": {
      "level": "N1",
      "title": "JLPT N1 最高殿堂",
      "sectionsMode": "二節制：言語知識・読解 (110m) ＋ 聴解 (55m)",
      "totalTimeMin": 165,
      "timeAllocationGuide": "文字語彙 15m ➔ 文法 20m ➔ 読解 75m (合計 110m) ｜ 聴解 55m",
      "passTotal": 100,
      "sectionCutoffs": {
        "言語知識": 19,
        "読解": 19,
        "聴解": 19
      },
      "mock100Total": 104,
      "practice300Target": 312,
      "practice500Target": 520,
      "mondaiList": [
        {
          "code": "M1_KANJI_READ",
          "section": "MOJI_GOI",
          "category": "KANJI",
          "name": "問題1・漢字読み",
          "mock100": 6,
          "pool300": 18,
          "pool500": 30,
          "secPerItem": 25
        },
        {
          "code": "M4_CONTEXT_VOCAB",
          "section": "MOJI_GOI",
          "category": "VOCAB",
          "name": "問題2・文脈規定",
          "mock100": 7,
          "pool300": 21,
          "pool500": 35,
          "secPerItem": 30
        },
        {
          "code": "M5_PARAPHRASE",
          "section": "MOJI_GOI",
          "category": "VOCAB",
          "name": "問題3・言い換え類義",
          "mock100": 6,
          "pool300": 18,
          "pool500": 30,
          "secPerItem": 30
        },
        {
          "code": "M6_USAGE",
          "section": "MOJI_GOI",
          "category": "VOCAB",
          "name": "問題4・用法",
          "mock100": 6,
          "pool300": 18,
          "pool500": 30,
          "secPerItem": 45
        },
        {
          "code": "G1_GRAMMAR_FORM",
          "section": "BUNPOU_DOKKAI",
          "category": "GRAMMAR",
          "name": "問題5・文法形式の判断",
          "mock100": 10,
          "pool300": 30,
          "pool500": 50,
          "secPerItem": 35
        },
        {
          "code": "G2_STAR_SYNTAX",
          "section": "BUNPOU_DOKKAI",
          "category": "STAR",
          "name": "問題6・文の組み立て ★",
          "mock100": 5,
          "pool300": 15,
          "pool500": 25,
          "secPerItem": 60
        },
        {
          "code": "G3_TEXT_GRAMMAR",
          "section": "BUNPOU_DOKKAI",
          "category": "GRAMMAR",
          "name": "問題7・文章の文法",
          "mock100": 5,
          "pool300": 15,
          "pool500": 25,
          "secPerItem": 55
        },
        {
          "code": "R1_SHORT_READ",
          "section": "BUNPOU_DOKKAI",
          "category": "READING",
          "name": "問題8・内容理解（短篇）",
          "mock100": 4,
          "pool300": 12,
          "pool500": 20,
          "secPerItem": 120
        },
        {
          "code": "R2_MID_READ",
          "section": "BUNPOU_DOKKAI",
          "category": "READING",
          "name": "問題9・内容理解（中篇 3篇×3題）",
          "mock100": 9,
          "pool300": 27,
          "pool500": 45,
          "secPerItem": 150
        },
        {
          "code": "R3_INTEGRATED_READ",
          "section": "BUNPOU_DOKKAI",
          "category": "READING",
          "name": "問題10/11・統合理解（A/B兩文比較）",
          "mock100": 4,
          "pool300": 12,
          "pool500": 20,
          "secPerItem": 180
        },
        {
          "code": "R4_LONG_OPINION",
          "section": "BUNPOU_DOKKAI",
          "category": "READING",
          "name": "問題12・主張理解（長篇）",
          "mock100": 7,
          "pool300": 21,
          "pool500": 35,
          "secPerItem": 180
        },
        {
          "code": "R5_INFO_RETRIEVAL",
          "section": "BUNPOU_DOKKAI",
          "category": "READING",
          "name": "問題13・情報検索",
          "mock100": 2,
          "pool300": 6,
          "pool500": 10,
          "secPerItem": 120
        },
        {
          "code": "L1_TASK",
          "section": "CHOUKAI",
          "category": "LISTENING",
          "name": "聴解問題1・課題理解",
          "mock100": 6,
          "pool300": 18,
          "pool500": 30,
          "secPerItem": 55
        },
        {
          "code": "L2_POINT",
          "section": "CHOUKAI",
          "category": "LISTENING",
          "name": "聴解問題2・ポイント理解",
          "mock100": 7,
          "pool300": 21,
          "pool500": 35,
          "secPerItem": 55
        },
        {
          "code": "L3_SUMMARY",
          "section": "CHOUKAI",
          "category": "LISTENING",
          "name": "聴解問題3・概要理解 (全盲聽)",
          "mock100": 6,
          "pool300": 18,
          "pool500": 30,
          "secPerItem": 60
        },
        {
          "code": "L5_QUICK_RESP",
          "section": "CHOUKAI",
          "category": "LISTENING",
          "name": "聴解問題4・即時応答 (全盲聽)",
          "mock100": 11,
          "pool300": 33,
          "pool500": 55,
          "secPerItem": 25
        },
        {
          "code": "L6_INTEGRATED_LISTEN",
          "section": "CHOUKAI",
          "category": "LISTENING",
          "name": "聴解問題5・統合理解 (長篇多方討論)",
          "mock100": 3,
          "pool300": 9,
          "pool500": 15,
          "secPerItem": 90
        }
      ]
    },
    "N2": {
      "level": "N2",
      "title": "JLPT N2 進階主力",
      "sectionsMode": "二節制：言語知識・読解 (105m) ＋ 聴解 (50m)",
      "totalTimeMin": 155,
      "timeAllocationGuide": "文字語彙 15m ➔ 文法 20m ➔ 読解 70m (合計 105m) ｜ 聴解 50m",
      "passTotal": 90,
      "sectionCutoffs": {
        "言語知識": 19,
        "読解": 19,
        "聴解": 19
      },
      "mock100Total": 106,
      "practice300Target": 318,
      "practice500Target": 530,
      "mondaiList": [
        {
          "code": "M1_KANJI_READ",
          "section": "MOJI_GOI",
          "category": "KANJI",
          "name": "問題1・漢字読み",
          "mock100": 5,
          "pool300": 15,
          "pool500": 25,
          "secPerItem": 20
        },
        {
          "code": "M2_ORTHOGRAPHY",
          "section": "MOJI_GOI",
          "category": "KANJI",
          "name": "問題2・表記 (假名轉漢字)",
          "mock100": 5,
          "pool300": 15,
          "pool500": 25,
          "secPerItem": 20
        },
        {
          "code": "M3_WORD_FORM",
          "section": "MOJI_GOI",
          "category": "VOCAB",
          "name": "問題3・語形成 (N2專屬複合詞/接頭接尾)",
          "mock100": 5,
          "pool300": 15,
          "pool500": 25,
          "secPerItem": 25
        },
        {
          "code": "M4_CONTEXT_VOCAB",
          "section": "MOJI_GOI",
          "category": "VOCAB",
          "name": "問題4・文脈規定",
          "mock100": 7,
          "pool300": 21,
          "pool500": 35,
          "secPerItem": 30
        },
        {
          "code": "M5_PARAPHRASE",
          "section": "MOJI_GOI",
          "category": "VOCAB",
          "name": "問題5・言い換え類義",
          "mock100": 5,
          "pool300": 15,
          "pool500": 25,
          "secPerItem": 30
        },
        {
          "code": "M6_USAGE",
          "section": "MOJI_GOI",
          "category": "VOCAB",
          "name": "問題6・用法",
          "mock100": 5,
          "pool300": 15,
          "pool500": 25,
          "secPerItem": 45
        },
        {
          "code": "G1_GRAMMAR_FORM",
          "section": "BUNPOU_DOKKAI",
          "category": "GRAMMAR",
          "name": "問題7・文の文法1 (文法形式)",
          "mock100": 12,
          "pool300": 36,
          "pool500": 60,
          "secPerItem": 35
        },
        {
          "code": "G2_STAR_SYNTAX",
          "section": "BUNPOU_DOKKAI",
          "category": "STAR",
          "name": "問題8・文の文法2 (★星號重組)",
          "mock100": 5,
          "pool300": 15,
          "pool500": 25,
          "secPerItem": 55
        },
        {
          "code": "G3_TEXT_GRAMMAR",
          "section": "BUNPOU_DOKKAI",
          "category": "GRAMMAR",
          "name": "問題9・文章の文法",
          "mock100": 5,
          "pool300": 15,
          "pool500": 25,
          "secPerItem": 50
        },
        {
          "code": "R1_SHORT_READ",
          "section": "BUNPOU_DOKKAI",
          "category": "READING",
          "name": "問題10・内容理解（短篇）",
          "mock100": 5,
          "pool300": 15,
          "pool500": 25,
          "secPerItem": 110
        },
        {
          "code": "R2_MID_READ",
          "section": "BUNPOU_DOKKAI",
          "category": "READING",
          "name": "問題11・内容理解（中篇 3篇×3題）",
          "mock100": 9,
          "pool300": 27,
          "pool500": 45,
          "secPerItem": 140
        },
        {
          "code": "R3_INTEGRATED_READ",
          "section": "BUNPOU_DOKKAI",
          "category": "READING",
          "name": "問題12・統合理解（A/B兩文比較）",
          "mock100": 2,
          "pool300": 6,
          "pool500": 10,
          "secPerItem": 160
        },
        {
          "code": "R4_LONG_OPINION",
          "section": "BUNPOU_DOKKAI",
          "category": "READING",
          "name": "問題13・主張理解（長篇）",
          "mock100": 3,
          "pool300": 9,
          "pool500": 15,
          "secPerItem": 170
        },
        {
          "code": "R5_INFO_RETRIEVAL",
          "section": "BUNPOU_DOKKAI",
          "category": "READING",
          "name": "問題14・情報検索",
          "mock100": 2,
          "pool300": 6,
          "pool500": 10,
          "secPerItem": 110
        },
        {
          "code": "L1_TASK",
          "section": "CHOUKAI",
          "category": "LISTENING",
          "name": "聴解問題1・課題理解",
          "mock100": 5,
          "pool300": 15,
          "pool500": 25,
          "secPerItem": 50
        },
        {
          "code": "L2_POINT",
          "section": "CHOUKAI",
          "category": "LISTENING",
          "name": "聴解問題2・ポイント理解",
          "mock100": 6,
          "pool300": 18,
          "pool500": 30,
          "secPerItem": 50
        },
        {
          "code": "L3_SUMMARY",
          "section": "CHOUKAI",
          "category": "LISTENING",
          "name": "聴解問題3・概要理解 (全盲聽)",
          "mock100": 5,
          "pool300": 15,
          "pool500": 25,
          "secPerItem": 55
        },
        {
          "code": "L5_QUICK_RESP",
          "section": "CHOUKAI",
          "category": "LISTENING",
          "name": "聴解問題4・即時応答 (全盲聽)",
          "mock100": 12,
          "pool300": 36,
          "pool500": 60,
          "secPerItem": 25
        },
        {
          "code": "L6_INTEGRATED_LISTEN",
          "section": "CHOUKAI",
          "category": "LISTENING",
          "name": "聴解問題5・統合理解 (長篇討論)",
          "mock100": 3,
          "pool300": 9,
          "pool500": 15,
          "secPerItem": 85
        }
      ]
    },
    "N3": {
      "level": "N3",
      "title": "JLPT N3 中級橋樑",
      "sectionsMode": "三節制：文字・語彙 (30m) ＋ 文法・読解 (70m) ＋ 聴解 (40m)",
      "totalTimeMin": 140,
      "timeAllocationGuide": "第1節 文字語彙 30m ｜ 第2節 文法 20m + 読解 50m (合計 70m) ｜ 第3節 聴解 40m",
      "passTotal": 95,
      "sectionCutoffs": {
        "言語知識": 19,
        "読解": 19,
        "聴解": 19
      },
      "mock100Total": 102,
      "practice300Target": 306,
      "practice500Target": 510,
      "mondaiList": [
        {
          "code": "M1_KANJI_READ",
          "section": "MOJI_GOI",
          "category": "KANJI",
          "name": "第1節 問題1・漢字読み",
          "mock100": 8,
          "pool300": 24,
          "pool500": 40,
          "secPerItem": 20
        },
        {
          "code": "M2_ORTHOGRAPHY",
          "section": "MOJI_GOI",
          "category": "KANJI",
          "name": "第1節 問題2・表記",
          "mock100": 6,
          "pool300": 18,
          "pool500": 30,
          "secPerItem": 20
        },
        {
          "code": "M4_CONTEXT_VOCAB",
          "section": "MOJI_GOI",
          "category": "VOCAB",
          "name": "第1節 問題3・文脈規定",
          "mock100": 11,
          "pool300": 33,
          "pool500": 55,
          "secPerItem": 25
        },
        {
          "code": "M5_PARAPHRASE",
          "section": "MOJI_GOI",
          "category": "VOCAB",
          "name": "第1節 問題4・言い換え類義",
          "mock100": 5,
          "pool300": 15,
          "pool500": 25,
          "secPerItem": 25
        },
        {
          "code": "M6_USAGE",
          "section": "MOJI_GOI",
          "category": "VOCAB",
          "name": "第1節 問題5・用法",
          "mock100": 5,
          "pool300": 15,
          "pool500": 25,
          "secPerItem": 40
        },
        {
          "code": "G1_GRAMMAR_FORM",
          "section": "BUNPOU_DOKKAI",
          "category": "GRAMMAR",
          "name": "第2節 問題1・文の文法1",
          "mock100": 13,
          "pool300": 39,
          "pool500": 65,
          "secPerItem": 30
        },
        {
          "code": "G2_STAR_SYNTAX",
          "section": "BUNPOU_DOKKAI",
          "category": "STAR",
          "name": "第2節 問題2・文の組み立て ★",
          "mock100": 5,
          "pool300": 15,
          "pool500": 25,
          "secPerItem": 50
        },
        {
          "code": "G3_TEXT_GRAMMAR",
          "section": "BUNPOU_DOKKAI",
          "category": "GRAMMAR",
          "name": "第2節 問題3・文章の文法",
          "mock100": 5,
          "pool300": 15,
          "pool500": 25,
          "secPerItem": 50
        },
        {
          "code": "R1_SHORT_READ",
          "section": "BUNPOU_DOKKAI",
          "category": "READING",
          "name": "第2節 問題4・内容理解（短篇）",
          "mock100": 4,
          "pool300": 12,
          "pool500": 20,
          "secPerItem": 100
        },
        {
          "code": "R2_MID_READ",
          "section": "BUNPOU_DOKKAI",
          "category": "READING",
          "name": "第2節 問題5・内容理解（中篇）",
          "mock100": 6,
          "pool300": 18,
          "pool500": 30,
          "secPerItem": 130
        },
        {
          "code": "R4_LONG_OPINION",
          "section": "BUNPOU_DOKKAI",
          "category": "READING",
          "name": "第2節 問題6・内容理解（長篇）",
          "mock100": 4,
          "pool300": 12,
          "pool500": 20,
          "secPerItem": 150
        },
        {
          "code": "R5_INFO_RETRIEVAL",
          "section": "BUNPOU_DOKKAI",
          "category": "READING",
          "name": "第2節 問題7・情報検索",
          "mock100": 2,
          "pool300": 6,
          "pool500": 10,
          "secPerItem": 100
        },
        {
          "code": "L1_TASK",
          "section": "CHOUKAI",
          "category": "LISTENING",
          "name": "第3節 問題1・課題理解",
          "mock100": 6,
          "pool300": 18,
          "pool500": 30,
          "secPerItem": 45
        },
        {
          "code": "L2_POINT",
          "section": "CHOUKAI",
          "category": "LISTENING",
          "name": "第3節 問題2・ポイント理解",
          "mock100": 6,
          "pool300": 18,
          "pool500": 30,
          "secPerItem": 45
        },
        {
          "code": "L3_SUMMARY",
          "section": "CHOUKAI",
          "category": "LISTENING",
          "name": "第3節 問題3・概要理解 (全盲聽)",
          "mock100": 3,
          "pool300": 9,
          "pool500": 15,
          "secPerItem": 50
        },
        {
          "code": "L4_UTTERANCE",
          "section": "CHOUKAI",
          "category": "LISTENING",
          "name": "第3節 問題4・発話表現 (看圖情境 SVG)",
          "mock100": 4,
          "pool300": 12,
          "pool500": 20,
          "secPerItem": 35
        },
        {
          "code": "L5_QUICK_RESP",
          "section": "CHOUKAI",
          "category": "LISTENING",
          "name": "第3節 問題5・即時応答 (全盲聽)",
          "mock100": 9,
          "pool300": 27,
          "pool500": 45,
          "secPerItem": 25
        }
      ]
    },
    "N4": {
      "level": "N4",
      "title": "JLPT N4 基礎進階",
      "sectionsMode": "三節制：文字・語彙 (25m) ＋ 文法・読解 (55m) ＋ 聴解 (35m)",
      "totalTimeMin": 115,
      "timeAllocationGuide": "第1節 文字語彙 25m ｜ 第2節 文法 20m + 読解 35m (合計 55m) ｜ 第3節 聴解 35m",
      "passTotal": 90,
      "sectionCutoffs": {
        "言語知識+読解合併": 38,
        "聴解": 19
      },
      "mock100Total": 89,
      "practice300Target": 267,
      "practice500Target": 445,
      "mondaiList": [
        {
          "code": "M1_KANJI_READ",
          "section": "MOJI_GOI",
          "category": "KANJI",
          "name": "第1節 問題1・漢字読み",
          "mock100": 7,
          "pool300": 21,
          "pool500": 35,
          "secPerItem": 20
        },
        {
          "code": "M2_ORTHOGRAPHY",
          "section": "MOJI_GOI",
          "category": "KANJI",
          "name": "第1節 問題2・表記",
          "mock100": 5,
          "pool300": 15,
          "pool500": 25,
          "secPerItem": 20
        },
        {
          "code": "M4_CONTEXT_VOCAB",
          "section": "MOJI_GOI",
          "category": "VOCAB",
          "name": "第1節 問題3・文脈規定",
          "mock100": 8,
          "pool300": 24,
          "pool500": 40,
          "secPerItem": 25
        },
        {
          "code": "M5_PARAPHRASE",
          "section": "MOJI_GOI",
          "category": "VOCAB",
          "name": "第1節 問題4・言い換え類義",
          "mock100": 4,
          "pool300": 12,
          "pool500": 20,
          "secPerItem": 25
        },
        {
          "code": "M6_USAGE",
          "section": "MOJI_GOI",
          "category": "VOCAB",
          "name": "第1節 問題5・用法",
          "mock100": 4,
          "pool300": 12,
          "pool500": 20,
          "secPerItem": 35
        },
        {
          "code": "G1_GRAMMAR_FORM",
          "section": "BUNPOU_DOKKAI",
          "category": "GRAMMAR",
          "name": "第2節 問題1・文の文法1",
          "mock100": 13,
          "pool300": 39,
          "pool500": 65,
          "secPerItem": 30
        },
        {
          "code": "G2_STAR_SYNTAX",
          "section": "BUNPOU_DOKKAI",
          "category": "STAR",
          "name": "第2節 問題2・文の組み立て ★",
          "mock100": 5,
          "pool300": 15,
          "pool500": 25,
          "secPerItem": 45
        },
        {
          "code": "G3_TEXT_GRAMMAR",
          "section": "BUNPOU_DOKKAI",
          "category": "GRAMMAR",
          "name": "第2節 問題3・文章の文法",
          "mock100": 5,
          "pool300": 15,
          "pool500": 25,
          "secPerItem": 45
        },
        {
          "code": "R1_SHORT_READ",
          "section": "BUNPOU_DOKKAI",
          "category": "READING",
          "name": "第2節 問題4・内容理解（短篇）",
          "mock100": 4,
          "pool300": 12,
          "pool500": 20,
          "secPerItem": 90
        },
        {
          "code": "R2_MID_READ",
          "section": "BUNPOU_DOKKAI",
          "category": "READING",
          "name": "第2節 問題5・内容理解（中篇）",
          "mock100": 4,
          "pool300": 12,
          "pool500": 20,
          "secPerItem": 110
        },
        {
          "code": "R5_INFO_RETRIEVAL",
          "section": "BUNPOU_DOKKAI",
          "category": "READING",
          "name": "第2節 問題6・情報検索",
          "mock100": 2,
          "pool300": 6,
          "pool500": 10,
          "secPerItem": 90
        },
        {
          "code": "L1_TASK",
          "section": "CHOUKAI",
          "category": "LISTENING",
          "name": "第3節 問題1・課題理解",
          "mock100": 8,
          "pool300": 24,
          "pool500": 40,
          "secPerItem": 40
        },
        {
          "code": "L2_POINT",
          "section": "CHOUKAI",
          "category": "LISTENING",
          "name": "第3節 問題2・ポイント理解",
          "mock100": 7,
          "pool300": 21,
          "pool500": 35,
          "secPerItem": 40
        },
        {
          "code": "L4_UTTERANCE",
          "section": "CHOUKAI",
          "category": "LISTENING",
          "name": "第3節 問題3・発話表現 (看圖情境 SVG)",
          "mock100": 5,
          "pool300": 15,
          "pool500": 25,
          "secPerItem": 35
        },
        {
          "code": "L5_QUICK_RESP",
          "section": "CHOUKAI",
          "category": "LISTENING",
          "name": "第3節 問題4・即時応答 (全盲聽)",
          "mock100": 8,
          "pool300": 24,
          "pool500": 40,
          "secPerItem": 25
        }
      ]
    },
    "N5": {
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
    }
  },
  "taiwanHighSchoolTrapCards": [
    {
      "kanji": "手紙 (てがみ) [0]",
      "lvl": "N4",
      "jpMeaning": "信件、書信",
      "twTrap": "❌ 台灣母語誤以為是「衛生紙」（日文衛生紙為 トイレットペーパー / ティッシュ）"
    },
    {
      "kanji": "我慢 (がまん) [1]",
      "lvl": "N3",
      "jpMeaning": "忍耐、忍受",
      "twTrap": "❌ 台灣母語誤以為是「傲慢」（日文傲慢為 傲慢 ごうまん / 横柄）"
    },
    {
      "kanji": "都合 (つごう) [0]",
      "lvl": "N4",
      "jpMeaning": "情況、方便與否、總共",
      "twTrap": "❌ 台灣母語誤以為是「大都會」（日文大都市為 都会 とかい）"
    },
    {
      "kanji": "勉強 (べんきょう) [0]",
      "lvl": "N4",
      "jpMeaning": "用功讀書、學習、算便宜",
      "twTrap": "❌ 台灣母語誤以為是「強迫/勉強」（日文勉強做某事為 無理をする / 強いる）"
    },
    {
      "kanji": "汽車 (きしゃ) [1]",
      "lvl": "N4",
      "jpMeaning": "蒸汽火車",
      "twTrap": "❌ 台灣母語誤以為是「汽車 (Auto)」（日文汽車為 車 くるま / 自動車）"
    },
    {
      "kanji": "邪魔 (じゃま) [0]",
      "lvl": "N3",
      "jpMeaning": "打擾、妨礙、絆腳石",
      "twTrap": "❌ 台灣母語誤以為是「妖魔鬼怪」（拜訪別人時說 お邪魔します 表打擾了）"
    },
    {
      "kanji": "大家 (おおや) [1]",
      "lvl": "N3",
      "jpMeaning": "房東（另有 たいか 表泰斗大師）",
      "twTrap": "❌ 台灣母語誤以為是「大家 (Everyone)」（日文大家為 皆さん / みんな）"
    },
    {
      "kanji": "床 (ゆか) [0]",
      "lvl": "N3",
      "jpMeaning": "地板（Floor）",
      "twTrap": "❌ 台灣母語誤以為是「睡覺的床」（日文睡床為 ベッド / 布団）"
    },
    {
      "kanji": "暗算 (あんざん) [0]",
      "lvl": "N2",
      "jpMeaning": "心算（Mental arithmetic）",
      "twTrap": "❌ 台灣母語誤以為是「暗中陷害/暗算」"
    },
    {
      "kanji": "成敗 (せいばい) [1]",
      "lvl": "N1",
      "jpMeaning": "懲罰、制裁（或成與敗）",
      "twTrap": "❌ 時代劇或慣用語中「成敗する」指處罰壞人，非單純成敗得失"
    },
    {
      "kanji": "おざなり vs ないがしろ",
      "lvl": "N1",
      "jpMeaning": "おざなり＝敷衍應付(有做但隨便)；ないがしろ＝徹底無視輕蔑",
      "twTrap": "⚡ N1 必考類義陷阱：長官交代的事隨便交差用「おざなり」，完全不理會用「ないがしろ」"
    },
    {
      "kanji": "橋 (はし [2]) vs 箸 (はし [1])",
      "tts": "はし",
      "lvl": "N3",
      "jpMeaning": "橋 [2] 尾高型 (低高+が低) vs 箸 [1] 頭高型 (高低)",
      "twTrap": "🎵 高低音調 (Pitch Accent) 最小對立組：助詞「が」接在橋後會下降，接在端(はし [0])後不下降"
    },
    {
      "kanji": "新聞 (しんぶん) [0]",
      "tts": "しんぶんをよむ",
      "lvl": "N5",
      "jpMeaning": "報紙（Newspaper）",
      "twTrap": "❌ 台灣母語誤以為是「電視新聞 (News)」（日文電視新聞為 ニュース）"
    },
    {
      "kanji": "走 (はしる) [2]",
      "tts": "こうえんをはしる",
      "lvl": "N5",
      "jpMeaning": "跑步、奔跑（Run）",
      "twTrap": "❌ 台灣母語受中文「走路」影響誤以為是步行（日文走路為 歩く あるく [2]）"
    },
    {
      "kanji": "娘 (むすめ) [3]",
      "tts": "むすめさん",
      "lvl": "N4",
      "jpMeaning": "女兒、年輕女孩（Daughter）",
      "twTrap": "❌ 台灣母語誤以為是「母親/娘親」（日文自己的母親為 母 はは [1]）"
    },
    {
      "kanji": "湯 (ゆ / おゆ) [1]/[0]",
      "tts": "おゆをわかす",
      "lvl": "N4",
      "jpMeaning": "熱水、溫泉澡堂（Hot water）",
      "twTrap": "❌ 台灣母語誤以為是「喝的湯 (Soup)」（日文湯品為 スープ / 味噌汁）"
    },
    {
      "kanji": "人参 (にんじん) [0]",
      "tts": "にんじん",
      "lvl": "N4",
      "jpMeaning": "紅蘿蔔、胡蘿蔔（Carrot）",
      "twTrap": "❌ 台灣母語誤以為是「高麗人參」（日文藥用人參為 朝鮮人参 ちょうせんにんじん）"
    },
    {
      "kanji": "怪我 (けが) [2]",
      "tts": "けがをする",
      "lvl": "N3",
      "jpMeaning": "受傷、外傷（Injury）",
      "twTrap": "❌ 台灣母語誤以為是「責怪我 (Blame me)」（けがをする 為受傷之意）"
    },
    {
      "kanji": "遠慮 (えんりょ) [0]",
      "tts": "えんりょしないでください",
      "lvl": "N3",
      "jpMeaning": "客氣、推辭、節制（禁止吸菸：タバコはご遠慮ください）",
      "twTrap": "❌ 台灣母語誤以為是「深謀遠慮」；告示牌寫「ご遠慮ください」實為委婉禁止！"
    },
    {
      "kanji": "看病 (かんびょう) [1]",
      "tts": "かんびょうする",
      "lvl": "N2",
      "jpMeaning": "照顧病人、護理（Nursing a patient）",
      "twTrap": "❌ 台灣母語誤以為是「找醫生看病」（日文給醫生看診為 診てもらう / 受診する）"
    },
    {
      "kanji": "結束 (けっそく) [0]",
      "tts": "けっそくをかためる",
      "lvl": "N2",
      "jpMeaning": "團結、凝聚力（Solidarity / Unity）",
      "twTrap": "❌ 台灣母語誤以為是「會議結束 (End)」（日文結束為 終了 しゅうりょう / 終わる）"
    },
    {
      "kanji": "油断 (ゆだん) [0]",
      "tts": "ゆだんたいてき",
      "lvl": "N2",
      "jpMeaning": "粗心大意、疏忽懈怠（Negligence）",
      "twTrap": "❌ 台灣母語誤以為是「切斷供油」；「油断するな」指千萬別掉以輕心"
    },
    {
      "kanji": "雨 (あめ [1]) vs 飴 (あめ [0])",
      "tts": "あめがふる、あめをなめる",
      "lvl": "N4",
      "jpMeaning": "雨 [1] 頭高型 (高低) vs 飴 [0] 平板型 (低高)",
      "twTrap": "🎵 東京方言必考聽解高低音調對比：首拍高音後急降為「下雨」，平升不降為「糖果」"
    }
  ]
};
