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
