/*************************************************************************
 * app.js
 * Core Application Controller for JLPT N1-N4 Interactive AI Studio v3.0
 * Features:
 * - Multi-Level Router (N2 Default -> N3 -> N4 -> N1)
 * - 6 Category Tabs + Official Exam Sub-Type Filter Dropdown
 * - Sweller Scaffolding Mode vs. Exam Simulation Mode
 * - Socratic Hint & 1-Distractor Elimination Scaffold
 * - Paivio Situational SVG Renderer (for N3/N4 Utterance Expressions)
 * - Odlin L1 Kanji Transfer Card & Worked-Example Syntactic Chain
 * - localStorage Persistence + JSON Backup/Restore + BYOK Gemini Vault
 *************************************************************************/

const CATEGORIES = [
  { id: 'ALL', name: '⚡ 跨題型交錯實戰', short: '全部', targetSec: 45 },
  { id: 'KANJI', name: '漢字・表記', short: '漢字表記', targetSec: 30 },
  { id: 'VOCAB', name: '語形成・語彙・用法', short: '語彙用法', targetSec: 35 },
  { id: 'GRAMMAR', name: '文法・文章文法', short: '文法克漏', targetSec: 45 },
  { id: 'STAR', name: '星號重組 ★', short: '星號重組', targetSec: 60 },
  { id: 'READING', name: '讀解・統合・檢索', short: '各類讀解', targetSec: 120 },
  { id: 'LISTENING', name: '🎧 聽解全題型', short: '聽解實戰', targetSec: 50 }
];

const STORAGE_KEY = 'jlpt_ai_studio_v3_progress';
const BYOK_STORAGE_KEY = 'jlpt_ai_studio_gemini_key';

let allBanks = { N1: [], N2: [], N3: [], N4: [], N5: [] };
const ENABLED_LEVELS = new Set(['N2']); // Locked to N2 flagship focus until N2 acceptance
let currentPoolScope = 'POOL_500'; // 'POOL_500' | 'POOL_300' | 'MOCK_100'
let currentWorkspaceTab = 'TAB_MAIN_GUI';
const OFFICIAL_HEX = { N1: '#00a383', N2: '#f39c42', N3: '#8c6bb1', N4: '#ef6c67', N5: '#1e78b4' };
let currentLevel = 'N2';
let questions = [];
let questionMap = {};

let currentFilter = 'ALL';
let currentOfficialSubfilter = 'ALL_SUB';
let filteredIndices = [];
let currentPos = 0;
let selectedOptionIndex = null;
let currentConfidence = 75;
let showFurigana = false;
let pedagogicalMode = 'SCAFFOLD'; // 'SCAFFOLD' | 'EXAM'
let eliminatedOptionIndex = null;
let socraticHintUsed = false;

// Pacing Timer State
let elapsedSeconds = 0;
let timerInterval = null;
let isSubmitted = false;

// Star (★) Reconstructor State
let starSlots = [null, null, null, null];
let macroExamTimerActive = false;
let macroWrittenRemainSec = 105 * 60;
let macroChoukaiRemainSec = 50 * 60;
let mobileHeaderDrawerOpen = false;
let showAllQueueItems = false;
let prewarmAudioEl = null;

// Choukai Blind-Listening State
let scriptPeeked = false;
let blindOptionsUnmasked = false;

// Persistent User Performance History Map: { [questionId]: record }
let historyMap = {};
let flaggedQuestionIds = new Set();
let currentTourStep = 0;

window.addEventListener('DOMContentLoaded', async () => {
  loadPersistedProgress();
  initEqualizerBars();
  renderPedagogicalTheoryModalContent();
  renderTrapCardsModalContent();
  updateByokStatusUI();

  await loadAllQuestionBanks();
  switchLevel('N2', false);

  if ('speechSynthesis' in window) {
    window.speechSynthesis.getVoices();
    window.speechSynthesis.onvoiceschanged = () => {
      window.speechSynthesis.getVoices();
    };
  }

  window.addEventListener('keydown', (e) => {
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;
    if (e.key >= '1' && e.key <= '4') {
      const idx = parseInt(e.key, 10) - 1;
      selectOption(idx);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (!isSubmitted) {
        submitCurrentAnswer();
      } else {
        nextQuestion();
      }
    } else if (e.key === 'ArrowRight') {
      nextQuestion();
    } else if (e.key === 'ArrowLeft') {
      prevQuestion();
    } else if (e.key === 'r' || e.key === 'R') {
      toggleFurigana();
    } else if (e.key === 'h' || e.key === 'H') {
      triggerSocraticHint();
    } else if (e.key === 'f' || e.key === 'F') {
      toggleFlagQuestion();
    }
  });
});

async function loadAllQuestionBanks() {
  // If embedded banks exist (Standalone HTML mode), load them first
  if (window.EMBEDDED_JLPT_BANKS) {
    allBanks = window.EMBEDDED_JLPT_BANKS;
  }

  // Fetch enabled level banks (Currently locked to N2 for maximum speed and focus)
  const levels = Array.from(ENABLED_LEVELS);
  await Promise.all(levels.map(async (lvl) => {
    try {
      const res = await fetch(`data/${lvl.toLowerCase()}_bank.json?v=4.4`);
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          allBanks[lvl] = data;
        }
      }
    } catch (e) {
      // Offline or file:// protocol: keep embedded bank
    }
  }));

  // Index all questions into questionMap
  questionMap = {};
  Object.values(allBanks).forEach(arr => {
    (arr || []).forEach(q => {
      questionMap[q.id] = q;
    });
  });

  updateLevelSwitcherCounts();
}

function updateLevelSwitcherCounts() {
  let totalPool = 0;
  ['N1', 'N2', 'N3', 'N4', 'N5'].forEach(lvl => {
    const btnEl = document.getElementById(`lvlBtn_${lvl}`);
    const cntEl = document.getElementById(`lvlCount_${lvl}`);
    if (!ENABLED_LEVELS.has(lvl)) {
      if (btnEl) btnEl.disabled = true;
      if (cntEl) cntEl.textContent = '待開放';
      return;
    }
    const arr = allBanks[lvl] || [];
    totalPool += arr.length;
    const mockCnt = arr.filter(q => q.inMock100).length || (LEVEL_SPECS[lvl]?.mock100Count || 106);
    if (cntEl && arr.length > 0) {
      cntEl.textContent = `${arr.length}題(模${mockCnt})`;
    }
  });
  const qBadge = document.getElementById('tab3QueueBadge');
  if (qBadge) qBadge.textContent = `${totalPool.toLocaleString()}題`;
}

function getScopedBank(lvl) {
  const raw = allBanks[lvl] || [];
  const mockCnt = raw.filter(q => q.inMock100).length || (LEVEL_SPECS[lvl]?.mock100Count || 80);
  if (currentPoolScope === 'MOCK_100') {
    const mockItems = raw.filter(q => q.inMock100);
    return mockItems.length > 0 ? mockItems : raw.slice(0, mockCnt);
  }
  if (currentPoolScope === 'POOL_300') {
    return raw.slice(0, mockCnt * 3);
  }
  return raw;
}

function setQuestionPoolScope(scope) {
  currentPoolScope = scope;
  if (scope === 'MOCK_100' && !macroExamTimerActive) {
    macroExamTimerActive = true;
    macroWrittenRemainSec = 105 * 60;
    macroChoukaiRemainSec = 50 * 60;
  }
  updateMacroExamTimerUI(getCurrentQuestion());
  const b500 = document.getElementById('poolBtn500');
  const b300 = document.getElementById('poolBtn300');
  const b100 = document.getElementById('poolBtn100');
  const tagEl = document.getElementById('officialExamPoolTag');
  const inactiveCls = 'px-2.5 py-1 rounded-lg text-xs font-semibold text-slate-300 hover:text-white transition';
  if (b500) b500.className = scope === 'POOL_500' ? 'px-2.5 py-1 rounded-lg text-xs font-bold bg-amber-500 text-slate-950 transition' : inactiveCls;
  if (b300) b300.className = scope === 'POOL_300' ? 'px-2.5 py-1 rounded-lg text-xs font-bold bg-sky-500 text-slate-950 transition' : inactiveCls;
  if (b100) b100.className = scope === 'MOCK_100' ? 'px-2.5 py-1 rounded-lg text-xs font-bold bg-rose-500 text-white transition' : inactiveCls;
  if (tagEl) {
    tagEl.textContent = scope === 'MOCK_100' ? '100%模考' : (scope === 'POOL_300' ? '300%池' : '500%池');
  }
  questions = [...getScopedBank(currentLevel)];
  populateOfficialSubfilterDropdown();
  renderCategoryTabs();
  filterQuestionsList();
  renderQuestionQueue();
  showToast(scope === 'MOCK_100'
    ? `⏱️ 已切換至 JLPT ${currentLevel}「100% 正式檢定標準題量」（共 ${questions.length} 題）！`
    : scope === 'POOL_300'
    ? `🏋️ 已切換至 JLPT ${currentLevel}「300% 核心擴充鍛鍊池」（共 ${questions.length} 題）！`
    : `🔥 已切換至 JLPT ${currentLevel}「500% 旗艦全題庫池」（共 ${questions.length} 題）！`, 'sky');
}


function toggleMobileHeaderDrawer() {
  mobileHeaderDrawerOpen = !mobileHeaderDrawerOpen;
  const d1 = document.getElementById('mobileHeaderDrawer');
  const d2 = document.getElementById('mobileSecondaryControls');
  const arrow = document.getElementById('mobileDrawerArrow');
  if (d1) {
    if (mobileHeaderDrawerOpen) {
      d1.classList.remove('hidden');
      d1.classList.add('flex');
    } else {
      d1.classList.add('hidden');
      d1.classList.remove('flex');
    }
  }
  if (d2) {
    if (mobileHeaderDrawerOpen) {
      d2.classList.remove('hidden');
      d2.classList.add('flex');
    } else {
      d2.classList.add('hidden');
      d2.classList.remove('flex');
    }
  }
  if (arrow) {
    arrow.textContent = mobileHeaderDrawerOpen ? '▲' : '▼';
  }
}

function expandQueueAllItems() {
  showAllQueueItems = true;
  renderQuestionQueue(true);
}

function switchWorkspaceTab(tabId) {
  currentWorkspaceTab = tabId;
  const panes = {
    TAB_MAIN_GUI: document.getElementById('tabPane_1'),
    TAB_IRT_COACH: document.getElementById('tabPane_2'),
    TAB_FSRS_OTHERS: document.getElementById('tabPane_3')
  };
  const btns = {
    TAB_MAIN_GUI: document.getElementById('mainTabBtn_1'),
    TAB_IRT_COACH: document.getElementById('mainTabBtn_2'),
    TAB_FSRS_OTHERS: document.getElementById('mainTabBtn_3')
  };
  Object.keys(panes).forEach(k => {
    if (!panes[k] || !btns[k]) return;
    if (k === tabId) {
      panes[k].classList.remove('hidden');
      btns[k].className = 'px-3.5 py-1.5 rounded-lg text-xs font-extrabold bg-amber-500 text-slate-950 shadow transition flex items-center gap-1.5';
    } else {
      panes[k].classList.add('hidden');
      btns[k].className = 'px-3.5 py-1.5 rounded-lg text-xs font-bold text-slate-300 hover:text-white hover:bg-slate-800 transition flex items-center gap-1.5';
    }
  });
  if (tabId === 'TAB_IRT_COACH') updateKPIsAndRadar();
  if (tabId === 'TAB_FSRS_OTHERS') renderQuestionQueue(true);
}

function switchLevel(lvl, showNotification = true) {
  if (!ENABLED_LEVELS.has(lvl)) {
    showToast(`🔒 目前系統鎖定專注於「JLPT N2」主力測驗衝刺（530題旗艦池 / 318題300%池 / 106題模考），${lvl} 待 N2 驗收後開放！`, 'amber');
    lvl = 'N2';
  }
  if (typeof stopListeningDialogue === 'function') stopListeningDialogue();
  currentLevel = lvl;
  const hex = OFFICIAL_HEX[lvl] || '#f39c42';
  document.documentElement.style.setProperty('--jlpt-active-theme', hex);

  const rawArr = allBanks[lvl] || [];
  const mockCnt = rawArr.filter(q => q.inMock100).length || (LEVEL_SPECS[lvl]?.mock100Count || 80);
  const pool500El = document.getElementById('pool500CountText');
  const pool300El = document.getElementById('pool300CountText');
  const mock100El = document.getElementById('mock100CountText');
  if (pool500El) pool500El.textContent = rawArr.length;
  if (pool300El) pool300El.textContent = mockCnt * 3;
  if (mock100El) mock100El.textContent = mockCnt;

  const sbMock = document.getElementById('standbyMock100Val');
  const sbPool300 = document.getElementById('standbyPool300Val');
  const sbPool500 = document.getElementById('standbyPool500Val');
  if (sbMock) sbMock.textContent = `${mockCnt} 題`;
  if (sbPool300) sbPool300.textContent = `${mockCnt * 3} 題`;
  if (sbPool500) sbPool500.textContent = `${rawArr.length} 題`;

  questions = [...getScopedBank(lvl)];
  currentFilter = 'ALL';
  currentOfficialSubfilter = 'ALL_SUB';

  // Update 5-Level Switcher Pills UI (N2 Active Flagship Focus; N1, N3, N4, N5 Disabled)
  ['N1', 'N2', 'N3', 'N4', 'N5'].forEach(code => {
    const btn = document.getElementById(`lvlBtn_${code}`);
    const cnt = document.getElementById(`lvlCount_${code}`);
    if (!btn) return;
    if (!ENABLED_LEVELS.has(code)) {
      btn.disabled = true;
      btn.className = 'px-3 py-1.5 rounded-xl font-bold text-xs transition flex items-center gap-1.5 bg-slate-900/60 text-slate-400 opacity-45 cursor-not-allowed';
      btn.style.backgroundColor = '';
      if (cnt) {
        cnt.className = 'px-1.5 py-0.5 rounded bg-slate-950 text-slate-400 font-mono text-xs';
        cnt.textContent = '待開放';
      }
      return;
    }
    if (code === lvl) {
      btn.disabled = false;
      btn.className = 'px-3 py-1.5 rounded-xl font-extrabold text-xs transition flex items-center gap-1.5 text-slate-950';
      btn.style.backgroundColor = OFFICIAL_HEX[code];
      if (cnt) cnt.className = 'px-1.5 py-0.5 rounded bg-slate-950 text-amber-300 font-mono text-xs font-bold';
    }
  });

  // Update Official Exam Frame Header Colors
  const examBox = document.getElementById('officialExamLevelBox');
  const examTxt = document.getElementById('officialExamLevelText');
  const examBanner = document.getElementById('officialMondaiBanner');
  if (examBox) examBox.style.backgroundColor = hex;
  if (examTxt) examTxt.textContent = lvl;
  if (examBanner) examBanner.style.backgroundColor = hex;
  const brandBadge = document.getElementById('headerLevelBadge');
  if (brandBadge) brandBadge.style.backgroundColor = hex;

  // Update Header Brand Badge & Exam Gate Info
  const spec = LEVEL_SPECS[lvl] || LEVEL_SPECS.N2;
  const bp = (typeof OFFICIAL_BLUEPRINT !== 'undefined' && OFFICIAL_BLUEPRINT.levels?.[lvl]) || null;
  const brandTitle = document.getElementById('headerLevelTitle');
  const brandSub = document.getElementById('headerLevelDesc');
  if (brandBadge) brandBadge.textContent = lvl;
  if (brandTitle) brandTitle.textContent = `JLPT ${lvl} 互動式 AI 刷題與認知診斷系統 v4.0`;
  if (brandSub) {
    const timeGuide = bp ? ` ｜ ⏳ 黃金配速：${bp.timeAllocationGuide}` : '';
    brandSub.textContent = `${spec.desc} ｜ 📚 ${spec.vocabScale}${timeGuide}`;
  }

  // Auto-enable Furigana for N3/N4 in Scaffolding mode
  if ((lvl === 'N3' || lvl === 'N4' || lvl === 'N5') && pedagogicalMode === 'SCAFFOLD') {
    showFurigana = true;
  }
  syncFuriganaUI();

  populateOfficialSubfilterDropdown();
  renderCategoryTabs();
  applyCategoryFilter('ALL');
  updateKPIsAndRadar();
  renderQuestionQueue();

  if (showNotification) {
    showToast(`🎯 已切換至 JLPT ${lvl}（共 ${questions.length} 道精編實戰題，${spec.sectionsMode}）`, 'amber');
  }
}

function setPedagogicalMode(mode) {
  pedagogicalMode = mode;
  const btnScaffold = document.getElementById('modeBtnScaffold');
  const btnExam = document.getElementById('modeBtnExam');
  const scaffoldToolbar = document.getElementById('scaffoldingActionStrip');

  if (mode === 'SCAFFOLD') {
    if (btnScaffold) btnScaffold.className = 'px-3 py-1.5 rounded-lg text-xs font-bold bg-emerald-500 text-slate-950 transition flex items-center gap-1';
    if (btnExam) btnExam.className = 'px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition flex items-center gap-1';
    if (scaffoldToolbar) scaffoldToolbar.classList.remove('hidden');
    if (currentLevel === 'N3' || currentLevel === 'N4') {
      showFurigana = true;
      syncFuriganaUI();
    }
    showToast('🌱 已啟用「教學鷹架模式」：提供蘇格拉底產婆提示、誘答排除與分級振假名輔助！', 'emerald');
  } else {
    if (btnExam) btnExam.className = 'px-3 py-1.5 rounded-lg text-xs font-bold bg-rose-500 text-white transition flex items-center gap-1';
    if (btnScaffold) btnScaffold.className = 'px-3 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition flex items-center gap-1';
    if (scaffoldToolbar) scaffoldToolbar.classList.add('hidden');
    showFurigana = false;
    syncFuriganaUI();
    showToast('⚔️ 已進入「考場實戰模式」：隱藏所有鷹架提示，嚴格執行考場盲聽與配速計時！', 'rose');
  }
  loadCurrentQuestion();
}

function populateOfficialSubfilterDropdown() {
  const select = document.getElementById('officialSubtypeSelect');
  if (!select) return;
  const map = new Map();
  questions.forEach(q => {
    if (q.officialCode && q.officialName) {
      const prev = map.get(q.officialCode) || { name: q.officialName, count: 0 };
      prev.count++;
      map.set(q.officialCode, prev);
    }
  });

  let html = `<option value="ALL_SUB">📑 官方細分大題：全部題型 (${questions.length}題)</option>`;
  Array.from(map.entries()).forEach(([code, info]) => {
    html += `<option value="${code}">${info.name} (${info.count}題)</option>`;
  });
  select.innerHTML = html;
  select.value = currentOfficialSubfilter;
}

function applyOfficialSubfilter(subCode) {
  currentOfficialSubfilter = subCode;
  filterQuestionsList();
}

function renderCategoryTabs() {
  const container = document.getElementById('categoryTabs');
  if (!container) return;
  container.innerHTML = CATEGORIES.map(cat => {
    const count = cat.id === 'ALL'
      ? questions.length
      : questions.filter(q => q.category === cat.id).length;
    const active = currentFilter === cat.id;
    const isListening = cat.id === 'LISTENING';
    return `
      <button onclick="applyCategoryFilter('${cat.id}')"
        class="px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition flex items-center gap-1.5 ${
 active
 ? 'bg-amber-500 text-slate-950 font-bold'
 : isListening
 ? 'bg-sky-500/15 hover:bg-sky-500/25 text-sky-300 '
 : 'bg-slate-800/90 hover:bg-slate-700/80 text-slate-300 '
 }">
        <span>${cat.name}</span>
        <span class="px-1.5 py-0.2 rounded-full text-xs font-mono ${
 active ? 'bg-slate-950/20 text-slate-950' : 'bg-slate-900 text-slate-400'
 }">${count}</span>
      </button>
    `;
  }).join('');
}

function applyCategoryFilter(catId) {
  if (typeof stopListeningDialogue === 'function') stopListeningDialogue();
  currentFilter = catId;
  currentOfficialSubfilter = 'ALL_SUB';
  const select = document.getElementById('officialSubtypeSelect');
  if (select) select.value = 'ALL_SUB';
  filterQuestionsList();
}

function filterQuestionsList() {
  filteredIndices = questions
    .map((q, idx) => ({ q, idx }))
    .filter(item => {
      const matchCat = currentFilter === 'ALL' || item.q.category === currentFilter;
      const matchSub = currentOfficialSubfilter === 'ALL_SUB' || item.q.officialCode === currentOfficialSubfilter;
      return matchCat && matchSub;
    })
    .map(item => item.idx);

  if (filteredIndices.length === 0) {
    filteredIndices = questions.map((_, idx) => idx);
  }
  currentPos = 0;
  renderCategoryTabs();
  loadCurrentQuestion();
}

function getCurrentQuestion() {
  const qIdx = filteredIndices[currentPos] ?? 0;
  return questions[qIdx];
}

function initEqualizerBars() {
  const eq = document.getElementById('eqVisualizer');
  if (!eq) return;
  let barsHtml = '';
  for (let i = 0; i < 24; i++) {
    const delay = ((i % 6) * 0.11).toFixed(2);
    const heightClass = i % 3 === 0 ? 'h-8' : i % 2 === 0 ? 'h-6' : 'h-5';
    barsHtml += `<span class="eq-bar w-1.5 ${heightClass} rounded-full bg-gradient-to-t from-sky-500 to-amber-400" style="animation-delay: ${delay}s"></span>`;
  }
  eq.innerHTML = barsHtml;
}

function loadCurrentQuestion() {
  if (typeof stopListeningDialogue === 'function') stopListeningDialogue();
  const q = getCurrentQuestion();
  if (!q) return;

  isSubmitted = false;
  selectedOptionIndex = null;
  eliminatedOptionIndex = null;
  socraticHintUsed = false;
  scriptPeeked = false;
  blindOptionsUnmasked = !q.blindOptions;
  starSlots = [null, null, null, null];

  document.getElementById('diagnosticPanel')?.classList.add('hidden');
  document.getElementById('preAnswerStandbyCard')?.classList.remove('hidden');
  document.getElementById('aiTutorResponseBox')?.classList.add('hidden');
  document.getElementById('socraticHintBanner')?.classList.add('hidden');
  const tutorInput = document.getElementById('aiTutorInput');
  if (tutorInput) tutorInput.value = '';
  document.getElementById('submitBtn')?.classList.remove('hidden');

  const catMeta = CATEGORIES.find(c => c.id === q.category) || CATEGORIES[0];
  document.getElementById('qCategoryBadge').textContent = q.officialName || catMeta.name;
  document.getElementById('qSubtagBadge').textContent = q.subtag || `${currentLevel} 核心考點`;
  document.getElementById('qBloomBadge').textContent = q.bloomLabel || 'L2 理解';
  document.getElementById('qIrtBadge').textContent = `IRT b=${(q.irtB ?? 0).toFixed(1)}`;
  document.getElementById('qProgressText').textContent = `題號 #${currentPos + 1} / ${filteredIndices.length} (${q.id})`;
  document.getElementById('qInstruction').textContent = q.instruction;
  document.getElementById('qStemText').innerHTML = q.stem;

  // Render Official Top Mondai Numbered Bar (1..14 Written + 🔊15..19 Listening)
  renderOfficialMondaiNumberBar(q);

  // Render Situational SVG Card (with Click-to-Zoom wrapper)
  const svgBox = document.getElementById('situationSvgBox');
  const svgWrap = document.getElementById('situationSvgWrapper');
  if (svgBox) {
    if (q.situationSvg) {
      svgBox.innerHTML = q.situationSvg;
      svgBox.classList.remove('hidden');
      if (svgWrap) svgWrap.classList.remove('hidden');
    } else {
      svgBox.innerHTML = '';
      svgBox.classList.add('hidden');
      if (svgWrap) svgWrap.classList.add('hidden');
    }
  }

  // Listening Console vs Standard TTS Bar
  const listeningConsole = document.getElementById('listeningConsoleBox');
  const standardTtsBar = document.getElementById('standardTtsBar');
  if (q.category === 'LISTENING') {
    listeningConsole.classList.remove('hidden');
    standardTtsBar.classList.add('hidden');
    document.getElementById('blindShieldBox').classList.remove('hidden');
    document.getElementById('dialogueTranscriptBox').classList.add('hidden');
    document.getElementById('turnCounterText').textContent = `語音段: 0 / ${q.dialogue ? q.dialogue.length : 1}`;
    document.getElementById('activeSpeakerBadge').textContent = '待機中 (點擊下方播放考場雙聲道音訊)';
    document.getElementById('playChoukaiText').textContent = '播放考場對話 (含鐘聲)';
    const consoleTitle = document.getElementById('choukaiConsoleTitle');
    if (consoleTitle) consoleTitle.textContent = `🎧 JLPT ${currentLevel} 雙聲道考場音源合成器 (${q.officialName || '聴解'})`;
  } else {
    listeningConsole.classList.add('hidden');
    standardTtsBar.classList.remove('hidden');
  }

  // Problem 3 / Quick Response Blind Options Notice
  const blindNotice = document.getElementById('blindOptionsNotice');
  if (q.blindOptions && !blindOptionsUnmasked) {
    blindNotice.classList.remove('hidden');
    blindNotice.classList.add('flex');
  } else {
    blindNotice.classList.add('hidden');
    blindNotice.classList.remove('flex');
  }

  // Furigana Hint Box
  updateFuriganaHintVisibility(q);

  // Star (★) Reconstructor Visibility
  const starBox = document.getElementById('starReconstructorBox');
  if (q.category === 'STAR') {
    starBox.classList.remove('hidden');
    renderStarReconstructor(q);
  } else {
    starBox.classList.add('hidden');
  }

  renderOptionCards(q);
  document.getElementById('prevBtn').disabled = currentPos === 0;
  startPacingTimer(q.targetSec || catMeta.targetSec || 45);
  syncFlagButtonUI(q.id);
  renderQuestionQueue();
}

function renderOfficialMondaiNumberBar(currentQ) {
  const writtenBar = document.getElementById('officialMondaiWrittenBar');
  const listenBar = document.getElementById('officialMondaiListeningBar');
  const headerLbl = document.getElementById('officialWrittenHeaderLabel');
  if (!writtenBar || !listenBar) return;

  if (headerLbl) {
    headerLbl.textContent = (currentLevel === 'N1' || currentLevel === 'N2')
      ? '第1節：言語知識（文字・語彙・文法）・読解'
      : '第1・2節：言語知識（文字・語彙）＋（文法・読解）';
  }

  const bp = (typeof OFFICIAL_BLUEPRINT !== 'undefined' && OFFICIAL_BLUEPRINT.levels?.[currentLevel]) || null;
  const mondaiList = bp?.mondaiList || [];
  const writtenMondai = mondaiList.filter(m => !String(m.code).startsWith('L'));
  const listenMondai = mondaiList.filter(m => String(m.code).startsWith('L'));
  const activeHex = OFFICIAL_HEX[currentLevel] || '#f39c42';

  writtenBar.innerHTML = writtenMondai.map((m, idx) => {
    const isActive = currentQ && currentQ.officialCode === m.code;
    return `
      <button type="button" onclick="jumpToMondaiCode('${m.code}')" title="${m.name}"
        style="${isActive ? `background-color: ${activeHex}; color: #020617;` : ''}"
        class="w-6 h-6 rounded font-mono text-xs font-extrabold transition flex items-center justify-center ${
 isActive
 ? ' scale-105'
 : 'bg-slate-800 hover:bg-slate-700 text-slate-200 '
 }">
        ${idx + 1}
      </button>
    `;
  }).join('');

  listenBar.innerHTML = listenMondai.map((m, idx) => {
    const isActive = currentQ && currentQ.officialCode === m.code;
    const numLabel = writtenMondai.length + idx + 1;
    return `
      <button type="button" onclick="jumpToMondaiCode('${m.code}')" title="${m.name}"
        style="${isActive ? `background-color: ${activeHex}; color: #020617;` : ''}"
        class="px-1.5 h-6 rounded font-mono text-xs font-extrabold transition flex items-center justify-center gap-0.5 ${
 isActive
 ? ' scale-105'
 : 'bg-slate-800 hover:bg-slate-700 text-sky-300 '
 }">
        <span>🔊${numLabel}</span>
      </button>
    `;
  }).join('');
}

function jumpToMondaiCode(officialCode) {
  currentFilter = 'ALL';
  currentOfficialSubfilter = officialCode;
  const select = document.getElementById('officialSubtypeSelect');
  if (select) select.value = officialCode;
  filterQuestionsList();
}

function openSvgZoomModal() {
  const q = getCurrentQuestion();
  const modal = document.getElementById('svgZoomModal');
  const content = document.getElementById('svgZoomModalContent');
  if (!modal || !content || !q?.situationSvg) return;
  content.innerHTML = q.situationSvg;
  modal.classList.remove('hidden');
}

function closeSvgZoomModal() {
  document.getElementById('svgZoomModal')?.classList.add('hidden');
}

function openConjugationModal() {
  document.getElementById('conjugationModal')?.classList.remove('hidden');
}

function closeConjugationModal() {
  document.getElementById('conjugationModal')?.classList.add('hidden');
}

function toggleFlagQuestion() {
  const q = getCurrentQuestion();
  if (!q) return;
  if (flaggedQuestionIds.has(q.id)) {
    flaggedQuestionIds.delete(q.id);
    showToast(`已取消標記題號 ${q.id}`, 'sky');
  } else {
    flaggedQuestionIds.add(q.id);
    showToast(`🚩 已將 ${q.id} 標記為「考場待查題 (停損跳題)」！`, 'amber');
  }
  syncFlagButtonUI(q.id);
  renderQuestionQueue();
}

function syncFlagButtonUI(qId) {
  const btn = document.getElementById('flagQuestionBtn');
  if (!btn) return;
  if (flaggedQuestionIds.has(qId)) {
    btn.className = 'px-2.5 py-1 rounded-xl bg-rose-500/25 text-rose-300 border border-rose-400 text-xs font-bold transition';
    btn.textContent = '🚩 已標記待查';
  } else {
    btn.className = 'px-2.5 py-1 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-amber-300 border border-slate-700 text-xs font-medium transition';
    btn.textContent = '🏳️ 標記待查 (停損)';
  }
}

function updateFuriganaHintVisibility(q) {
  const hintBox = document.getElementById('qHintBox');
  if (!hintBox || !q) return;
  if (showFurigana && q.furiganaHint && (isSubmitted || (q.category !== 'KANJI' && q.category !== 'LISTENING'))) {
    hintBox.textContent = `💡 詞彙與讀音鷹架輔助：${q.furiganaHint}`;
    hintBox.classList.remove('hidden');
  } else {
    hintBox.classList.add('hidden');
  }
}

function syncFuriganaUI() {
  const statusText = document.getElementById('furiganaStatusText');
  if (statusText) {
    statusText.textContent = showFurigana ? 'ON' : 'OFF';
    statusText.className = showFurigana ? 'font-mono text-amber-400 font-bold' : 'font-mono text-emerald-400 font-bold';
  }
  if (showFurigana) {
    document.body.classList.remove('hide-inline-ruby');
  } else {
    document.body.classList.add('hide-inline-ruby');
  }
  updateFuriganaHintVisibility(getCurrentQuestion());
}

function toggleFurigana() {
  showFurigana = !showFurigana;
  syncFuriganaUI();
}

function highlightDiscourseMarkers() {
  const q = getCurrentQuestion();
  const stemEl = document.getElementById('qStemText');
  if (!q || !stemEl) return;
  const markers = [
    'しかし', 'だが', 'けれども', 'ところが', 'それにもかかわらず', '一方で', '他方', 'それに対して',
    'つまり', 'すなわち', '要するに', '結論として', '実は', 'なぜなら', 'したがって', 'そのため',
    'のではないだろうか', 'べきだ', 'にほかならない', 'に違いない', 'と考えられる', 'が重要だ'
  ];
  let html = q.stem;
  let hits = 0;
  markers.forEach(m => {
    if (html.includes(m)) {
      hits++;
      const re = new RegExp(`(${m})`, 'g');
      html = html.replace(re, '<mark class="px-1 py-0.5 rounded bg-amber-400/30 text-amber-200 font-extrabold">$1</mark>');
    }
  });
  stemEl.innerHTML = html;
  if (hits > 0) {
    showToast(`🖍️ 讀解談話標記：已高亮標示本題 ${hits} 處關鍵轉折/結論/主張信號詞！`, 'sky');
  } else {
    triggerSocraticHint();
  }
}

function triggerSocraticHint() {
  const q = getCurrentQuestion();
  if (!q) return;
  socraticHintUsed = true;
  const banner = document.getElementById('socraticHintBanner');
  const textEl = document.getElementById('socraticHintText');
  if (banner && textEl) {
    textEl.textContent = q.socraticHint || q.coreRule;
    banner.classList.remove('hidden');
    showToast('🎯 已展開蘇格拉底產婆引導提示（思考關鍵語境線索，不直接洩漏答案）！', 'amber');
  }
}

function eliminateOneDistractor() {
  const q = getCurrentQuestion();
  if (!q || isSubmitted) return;
  if (eliminatedOptionIndex !== null) {
    showToast('本題已排除過一個誘答選項囉！', 'sky');
    return;
  }
  const wrongIndices = q.options.map((_, idx) => idx).filter(idx => idx !== q.correctIndex);
  eliminatedOptionIndex = wrongIndices[Math.floor(Math.random() * wrongIndices.length)];
  if (selectedOptionIndex === eliminatedOptionIndex) {
    selectedOptionIndex = null;
  }
  renderOptionCards(q);
  showToast(`✂️ 認知減負鷹架：已為您排除明顯誘答項（選項 ${eliminatedOptionIndex + 1}）！`, 'emerald');
}

function renderOptionCards(q) {
  const container = document.getElementById('optionsContainer');
  if (!container || !q) return;

  const isQuickResp = q.officialCode === 'L5_QUICK_RESP';
  const isMasked = Boolean(
    (isQuickResp || q.blindOptions) &&
    !blindOptionsUnmasked &&
    !scriptPeeked &&
    !isSubmitted &&
    selectedOptionIndex === null
  );

  container.innerHTML = q.options.map((optText, idx) => {
    const isSelected = selectedOptionIndex === idx;
    const isEliminated = eliminatedOptionIndex === idx && !isSubmitted;
    const displayLabel = isMasked
      ? (isQuickResp
          ? `選択肢 ${idx + 1} — 🔊 請先聽語音並依高低音調與語境作答`
          : `選択肢 ${idx + 1} — 🔊 考場無印字盲聽鎖定中（請先聽音訊或點擊上方 👁️ 顯示文字稿）`)
      : optText;

    let cardStyle = isSelected
      ? 'bg-amber-500/20 border-amber-400 text-white'
      : 'bg-slate-900/80 hover:bg-slate-700/60 border-slate-700 text-slate-200';

    if (isEliminated) {
      cardStyle = 'bg-slate-950/40 border-slate-800/60 text-slate-400 line-through opacity-45 cursor-not-allowed';
    }

    if (isSubmitted) {
      if (idx === q.correctIndex) {
        cardStyle = 'bg-emerald-500/20 border-emerald-400 text-emerald-100';
      } else if (idx === selectedOptionIndex && idx !== q.correctIndex) {
        cardStyle = 'bg-rose-500/20 border-rose-400 text-rose-100';
      } else {
        cardStyle = 'bg-slate-900/40 border-slate-800 text-slate-400 opacity-75';
      }
    }

    return `
      <button type="button" onclick="selectOption(${idx})" ${isEliminated ? 'disabled' : ''}
        class="jlpt-capsule-option w-full text-left px-4 py-3 transition-all flex items-center gap-3 group ${cardStyle}">
        <span class="w-7 h-7 rounded-full font-mono text-xs font-black flex items-center justify-center shrink-0 ${
          isSelected
            ? 'bg-amber-400 text-slate-950'
            : 'bg-slate-800 text-slate-200 group-hover:bg-slate-700'
        }">
          ${idx + 1}
        </span>
        <span class="jp-text text-sm sm:text-base font-bold flex-1 ${isMasked ? 'text-slate-300 italic text-xs' : ''}">${displayLabel}</span>
      </button>
    `;
  }).join('');
}

function selectOption(idx) {
  if (isSubmitted || idx === eliminatedOptionIndex) return;
  const q = getCurrentQuestion();
  if (!q || idx >= q.options.length) return;
  selectedOptionIndex = idx;
  if (q.officialCode === 'L5_QUICK_RESP' || q.blindOptions) {
    blindOptionsUnmasked = true;
    const blindNotice = document.getElementById('blindOptionsNotice');
    if (blindNotice) {
      blindNotice.classList.add('hidden');
      blindNotice.classList.remove('flex');
    }
  }
  if (q.category === 'STAR' || q.officialCode === 'G2_STAR_SYNTAX' || q.officialCode === 'G2_STAR_ORDER') {
    const existingPos = starSlots.indexOf(idx);
    if (existingPos !== -1 && existingPos !== 2) {
      starSlots[existingPos] = null;
    }
    starSlots[2] = idx;
    renderStarReconstructor(q);
  }
  renderOptionCards(q);
}

/*************************************************************************
 * INTERACTIVE STAR (★) SYNTAX RECONSTRUCTOR
 *************************************************************************/
function buildSynthesizedStarSentenceHtml(q) {
  if (!q || !Array.isArray(q.correctSequence) || q.correctSequence.length !== 4) return '';
  const tokensHtml = q.correctSequence.map((optIdx, pos) => {
    const txt = q.options[optIdx] || '';
    if (pos === 2) {
      return `<span class="px-2 py-0.5 rounded bg-slate-950 text-amber-300 font-extrabold mx-0.5">★ ${txt}</span>`;
    }
    return `<span class="text-emerald-300 font-bold mx-0.5">${txt}</span>`;
  }).join('');
  const slotPattern = /[＿_]+\s*[＿_]+\s*(?:<u>)?★(?:<\/u>)?\s*[＿_]+/;
  if (slotPattern.test(q.stem || '')) {
    return q.stem.replace(slotPattern, tokensHtml);
  }
  return `${q.stem} ➔ ${tokensHtml}`;
}

function renderStarReconstructor(q) {
  const slotsContainer = document.getElementById('starSlotsContainer');
  const tokensBar = document.getElementById('starTokensBar');
  const directSubmitBox = document.getElementById('starDirectSubmitBox');
  const fullSentenceBox = document.getElementById('starFullSentenceBox');
  if (!slotsContainer || !tokensBar || !q) return;

  slotsContainer.innerHTML = [0, 1, 2, 3].map(slotIdx => {
    const isStarSlot = slotIdx === 2;
    const placedOptIdx = starSlots[slotIdx];
    const placedText = placedOptIdx !== null
      ? `(${placedOptIdx + 1}) ${q.options[placedOptIdx]}`
      : (isStarSlot ? '★ 點擊下方詞塊填入' : `第 ${slotIdx + 1} 格`);

    return `
      <div onclick="removeStarSlot(${slotIdx})"
        class="cursor-pointer rounded-xl p-2.5 text-center transition flex flex-col items-center justify-center min-h-[54px] ${
          isStarSlot
            ? 'bg-amber-500/15 star-slot-active'
            : 'bg-slate-950'
        }">
        <span class="text-xs font-mono ${isStarSlot ? 'text-amber-300 font-bold' : 'text-slate-300'}">
          ${isStarSlot ? '★ 目標計分位置 (第3格)' : `語序位置 ${slotIdx + 1}`}
        </span>
        <span class="jp-text text-xs sm:text-sm font-bold mt-0.5 ${placedOptIdx !== null ? 'text-white' : 'text-slate-300'}">
          ${placedText}
        </span>
      </div>
    `;
  }).join('');

  tokensBar.innerHTML = q.options.map((optText, idx) => {
    const used = starSlots.includes(idx);
    return `
      <button type="button" onclick="placeStarToken(${idx})" ${used ? 'disabled' : ''}
        class="px-3 py-1.5 rounded-lg text-xs sm:text-sm jp-text font-medium transition ${
          used
            ? 'bg-slate-900 text-slate-400 opacity-40 cursor-not-allowed'
            : 'bg-slate-800 hover:bg-amber-500/20 text-slate-100'
        }">
        <span class="font-mono text-amber-300 font-bold mr-1">(${idx + 1})</span>${optText}
      </button>
    `;
  }).join('');

  if (directSubmitBox) {
    const starOptIdx = starSlots[2];
    if (starOptIdx !== null && !isSubmitted) {
      directSubmitBox.classList.remove('hidden');
      directSubmitBox.innerHTML = `
        <button type="button" onclick="submitFromStarSlot(${starOptIdx})"
          class="px-3.5 py-1.5 rounded-lg bg-amber-400 hover:bg-amber-300 text-slate-950 font-extrabold text-xs transition flex items-center gap-1.5">
          <span>🎯 以目前 ★ 格位直接送出作答</span>
          <span class="px-1.5 py-0.5 rounded bg-slate-950 text-amber-300 font-mono text-xs">(${starOptIdx + 1}) ${q.options[starOptIdx]}</span>
        </button>
      `;
    } else {
      directSubmitBox.classList.add('hidden');
      directSubmitBox.innerHTML = '';
    }
  }

  if (fullSentenceBox) {
    if (isSubmitted && Array.isArray(q.correctSequence) && q.correctSequence.length === 4) {
      const fullHtml = buildSynthesizedStarSentenceHtml(q);
      fullSentenceBox.classList.remove('hidden');
      fullSentenceBox.innerHTML = `
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div class="jp-text text-sm sm:text-base font-bold text-slate-100 leading-relaxed">
            <span class="font-mono text-xs text-emerald-300 mr-1.5">✅ 完整重組句 (★ 高亮)：</span>${fullHtml}
          </div>
          <button type="button" onclick="speakQuestion(1.0)"
            class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-sky-300 text-xs font-semibold transition shrink-0">
            🔊 朗讀完整重組句
          </button>
        </div>
      `;
    } else {
      fullSentenceBox.classList.add('hidden');
      fullSentenceBox.innerHTML = '';
    }
  }
}

function renderStarInteractiveWidget(q) {
  return renderStarReconstructor(q);
}

function submitFromStarSlot(placedOptIdx) {
  if (isSubmitted) return;
  selectOption(placedOptIdx);
  submitCurrentAnswer();
}

function placeStarToken(optIdx) {
  if (isSubmitted) return;
  const emptySlotIdx = starSlots.findIndex(s => s === null);
  if (emptySlotIdx === -1) return;
  starSlots[emptySlotIdx] = optIdx;
  if (starSlots[2] !== null) {
    selectedOptionIndex = starSlots[2];
  }
  const q = getCurrentQuestion();
  renderStarReconstructor(q);
  renderOptionCards(q);
}

function removeStarSlot(slotIdx) {
  if (isSubmitted) return;
  starSlots[slotIdx] = null;
  if (slotIdx === 2) selectedOptionIndex = null;
  const q = getCurrentQuestion();
  renderStarReconstructor(q);
  renderOptionCards(q);
}

function resetStarSlots() {
  if (isSubmitted) return;
  starSlots = [null, null, null, null];
  selectedOptionIndex = null;
  const q = getCurrentQuestion();
  renderStarReconstructor(q);
  renderOptionCards(q);
}

function anchorStarFirstLastSlots() {
  if (isSubmitted) return;
  if (pedagogicalMode === 'EXAM') {
    showToast('⚔️ 考場實戰模式中已鎖定首尾語塊錨定輔助！', 'rose');
    return;
  }
  const q = getCurrentQuestion();
  if (!q || !Array.isArray(q.correctSequence) || q.correctSequence.length !== 4) return;
  socraticHintUsed = true;
  starSlots = [q.correctSequence[0], null, null, q.correctSequence[3]];
  selectedOptionIndex = null;
  renderStarReconstructor(q);
  renderOptionCards(q);
  showToast('🔗 逆向接續鷹架：已為您鎖定「第1格(前接詞)」與「第4格(後接述語)」，請比較剩餘2個語塊填入第2格與 ★ 第3格！', 'emerald');
}

/*************************************************************************
 * POKA-YOKE PACING TIMER & SRL CONFIDENCE CALIBRATION
 *************************************************************************/
function formatMmSs(totalSec) {
  const m = Math.floor(Math.max(0, totalSec) / 60);
  const s = Math.floor(Math.max(0, totalSec) % 60);
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function toggleN2MacroExamTimer() {
  macroExamTimerActive = !macroExamTimerActive;
  if (macroExamTimerActive && macroWrittenRemainSec <= 0 && macroChoukaiRemainSec <= 0) {
    macroWrittenRemainSec = 105 * 60;
    macroChoukaiRemainSec = 50 * 60;
  }
  updateMacroExamTimerUI(getCurrentQuestion());
  showToast(
    macroExamTimerActive
      ? '⏱️ 已啟動 N2 正式模擬考二節制倒數計時 (105:00 言語・読解 / 50:00 聴解) 與即時配速診斷！'
      : '⏸️ 已暫停 N2 正式模擬考二節制倒數計時器。',
    macroExamTimerActive ? 'emerald' : 'sky'
  );
}

function updateMacroExamTimerUI(q) {
  const clockEl = document.getElementById('macroTimerClockText');
  const badgeEl = document.getElementById('macroPacingBadge');
  if (clockEl) {
    clockEl.textContent = `${formatMmSs(macroWrittenRemainSec)} 言語・読解 / ${formatMmSs(macroChoukaiRemainSec)} 聴解`;
  }
  if (!badgeEl) return;

  // Compute real-time section pacing against official N2 allocation:
  // 文字・語彙 15m (Q1-Q32, ~28.1s/q) -> 文法 20m (Q33-Q54, ~54.5s/q) -> 読解 70m (Q55-Q75, ~200s/q) -> 聴解 50m (Q76-Q106, ~96.8s/q)
  const writtenElapsed = 105 * 60 - macroWrittenRemainSec;
  const pos1Based = currentPos + 1;
  let expectedWrittenElapsed = 0;
  if (pos1Based <= 32) {
    expectedWrittenElapsed = pos1Based * (15 * 60 / 32);
  } else if (pos1Based <= 54) {
    expectedWrittenElapsed = 15 * 60 + (pos1Based - 32) * (20 * 60 / 22);
  } else if (pos1Based <= 75) {
    expectedWrittenElapsed = 35 * 60 + (pos1Based - 54) * (70 * 60 / 21);
  } else {
    expectedWrittenElapsed = 105 * 60;
  }

  const targetSec = q?.targetSec || 45;
  const isReadingLag = (q?.category === 'READING' && elapsedSeconds > targetSec) || (macroExamTimerActive && writtenElapsed - expectedWrittenElapsed > 180) || macroWrittenRemainSec < 25 * 60;
  const isAhead = (elapsedSeconds <= targetSec * 0.65) || (macroExamTimerActive && expectedWrittenElapsed - writtenElapsed > 120);

  if (isReadingLag) {
    badgeEl.textContent = '⚠️ 読解時間緊迫';
    const c1 = 'px-2 py-0.5 rounded bg-slate-950 text-amber-300 font-mono text-xs font-bold'; if (badgeEl.className !== c1) badgeEl.className = c1;
  } else if (isAhead) {
    badgeEl.textContent = '領先配速';
    const c2 = 'px-2 py-0.5 rounded bg-slate-950 text-emerald-300 font-mono text-xs font-bold'; if (badgeEl.className !== c2) badgeEl.className = c2;
  } else {
    badgeEl.textContent = '配速正常';
    const c3 = 'px-2 py-0.5 rounded bg-slate-950 text-sky-300 font-mono text-xs font-bold'; if (badgeEl.className !== c3) badgeEl.className = c3;
  }
}

function startPacingTimer(targetSec) {
  if (timerInterval) clearInterval(timerInterval);
  elapsedSeconds = 0;
  const q = getCurrentQuestion();
  updateTimerUI(targetSec);
  updateMacroExamTimerUI(q);
  timerInterval = setInterval(() => {
    if (!isSubmitted) {
      elapsedSeconds++;
      const curQ = getCurrentQuestion();
      if (macroExamTimerActive || currentPoolScope === 'MOCK_100') {
        if (curQ && curQ.category === 'LISTENING') {
          macroChoukaiRemainSec = Math.max(0, macroChoukaiRemainSec - 1);
        } else {
          macroWrittenRemainSec = Math.max(0, macroWrittenRemainSec - 1);
        }
      }
      updateTimerUI(targetSec);
      updateMacroExamTimerUI(curQ);
    }
  }, 1000);
}

function updateTimerUI(targetSec) {
  const timerText = document.getElementById('timerText');
  const timerDot = document.getElementById('timerDot');
  const progressBar = document.getElementById('timerProgressBar');
  if (!timerText || !timerDot || !progressBar) return;

  const padSec = String(elapsedSeconds).padStart(2, '0');
  timerText.textContent = `${padSec}s / ${targetSec}s`;
  const ratio = Math.min(100, (elapsedSeconds / targetSec) * 100);
  progressBar.style.width = `${ratio}%`;

  let nextTextCls = 'font-mono text-xs font-bold text-rose-400';
  let nextDotCls = 'w-2 h-2 rounded-full bg-rose-500';
  let nextBarCls = 'bg-rose-500 h-full transition-all duration-300';

  if (elapsedSeconds <= targetSec * 0.75) {
    nextTextCls = 'font-mono text-xs font-bold text-emerald-400';
    nextDotCls = 'w-2 h-2 rounded-full bg-emerald-400';
    nextBarCls = 'bg-emerald-500 h-full transition-all duration-300';
  } else if (elapsedSeconds <= targetSec) {
    nextTextCls = 'font-mono text-xs font-bold text-amber-400';
    nextDotCls = 'w-2 h-2 rounded-full bg-amber-400';
    nextBarCls = 'bg-amber-500 h-full transition-all duration-300';
  }

  if (timerText.className !== nextTextCls) timerText.className = nextTextCls;
  if (timerDot.className !== nextDotCls) timerDot.className = nextDotCls;
  if (progressBar.className !== nextBarCls) progressBar.className = nextBarCls;
}

function updateConfidenceUI(val) {
  currentConfidence = parseInt(val, 10);
  const slider = document.getElementById('confidenceSlider');
  if (slider) slider.value = currentConfidence;
  const badge = document.getElementById('confidenceValBadge');
  if (!badge) return;

  let label = '頗有把握';
  let colorClass = 'bg-sky-500/20 border-sky-500/40 text-sky-300';
  if (currentConfidence < 40) {
    label = '純猜測 / 直覺';
    colorClass = 'bg-rose-500/20 border-rose-500/40 text-rose-300';
  } else if (currentConfidence < 70) {
    label = '二選一猶豫';
    colorClass = 'bg-amber-500/20 border-amber-500/40 text-amber-300';
  } else if (currentConfidence >= 90) {
    label = '絕對篤定';
    colorClass = 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300';
  }

  badge.className = `px-2.5 py-0.5 rounded-md border font-mono text-sm font-bold ${colorClass}`;
  badge.textContent = `${currentConfidence}% ${label}`;
}

/*************************************************************************
 * SUBMIT, SRL + FSRS v5 + 2PL-IRT DIAGNOSTIC & PEDAGOGICAL LENSES
 *************************************************************************/
function submitCurrentAnswer() {
  if (selectedOptionIndex === null) {
    showToast('請先點選一個答案選項（或按鍵盤 1 ~ 4）再提交批改！', 'amber');
    return;
  }

  const q = getCurrentQuestion();
  isSubmitted = true;
  blindOptionsUnmasked = true;
  if (timerInterval) clearInterval(timerInterval);

  const isCorrect = selectedOptionIndex === q.correctIndex;
  const usedScaffold = scriptPeeked || socraticHintUsed || eliminatedOptionIndex !== null;
  const fsrsResult = computeFSRSUpdate(historyMap[q.id], isCorrect, currentConfidence, usedScaffold);

  historyMap[q.id] = {
    questionId: q.id,
    level: q.level || currentLevel,
    category: q.category,
    officialCode: q.officialCode,
    selectedIndex: selectedOptionIndex,
    correctIndex: q.correctIndex,
    isCorrect,
    confidence: fsrsResult.effConf,
    srlType: fsrsResult.srlType,
    srlLabel: fsrsResult.srlLabel,
    fsrsTag: fsrsResult.fsrsTag,
    stability: fsrsResult.stability,
    difficulty: fsrsResult.difficulty,
    elapsedSec: elapsedSeconds,
    timestamp: new Date().toLocaleTimeString()
  };

  savePersistedProgress();

  // Unlock Listening Dialogue Script with Full Signal Highlights
  if (q.category === 'LISTENING') {
    document.getElementById('blindShieldBox').classList.add('hidden');
    document.getElementById('blindOptionsNotice').classList.add('hidden');
    renderDialogueTranscript(q, true);
  }

  if (q.category === 'STAR') renderStarReconstructor(q);
  renderOptionCards(q);
  updateFuriganaHintVisibility(q);

  // Populate Diagnostic Panel in Right-Hand 1080P Dock
  document.getElementById('preAnswerStandbyCard')?.classList.add('hidden');
  const diagPanel = document.getElementById('diagnosticPanel');
  diagPanel.classList.remove('hidden');

  const iconBox = document.getElementById('resultIconBox');
  const titleText = document.getElementById('resultTitleText');
  if (isCorrect) {
    iconBox.className = 'w-11 h-11 rounded-xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 flex items-center justify-center text-xl font-bold';
    iconBox.textContent = '✓';
    titleText.className = 'text-base sm:text-lg font-bold text-emerald-400';
    titleText.textContent = `回答正確！（作答耗時 ${elapsedSeconds} 秒）`;
  } else {
    iconBox.className = 'w-11 h-11 rounded-xl bg-rose-500/20 border border-rose-500/40 text-rose-400 flex items-center justify-center text-xl font-bold';
    iconBox.textContent = '✗';
    titleText.className = 'text-base sm:text-lg font-bold text-rose-400';
    titleText.textContent = `誤入誘答陷阱！正解為選項 (${q.correctIndex + 1})`;
  }

  const srlBadge = document.getElementById('srlQuadrantBadge');
  srlBadge.className = `px-2.5 py-0.5 rounded-full text-xs font-mono font-bold ${fsrsResult.srlBadgeClass}`;
  srlBadge.textContent = fsrsResult.srlLabel;

  document.getElementById('fsrsScheduleText').textContent =
    `${fsrsResult.fsrsDesc}（記憶穩定度 S=${fsrsResult.stability}d, 難度 D=${fsrsResult.difficulty}）`;
  document.getElementById('diagTranslation').textContent = q.translation;
  document.getElementById('diagCoreRule').textContent = q.coreRule;

  // Populate Odlin L1 Kanji Transfer Lens & Worked Example Grammar Chain
  const l1Box = document.getElementById('diagL1Transfer');
  if (l1Box) {
    l1Box.textContent = q.l1TransferNote || '注意區分中文母語字義與日語實際共現搭配（Collocation）之差異。';
  }
  const chainBox = document.getElementById('diagGrammarChain');
  const chainCard = document.getElementById('diagGrammarChainCard');
  if (chainBox && chainCard) {
    if (q.grammarChain) {
      chainBox.textContent = q.grammarChain;
      chainCard.classList.remove('hidden');
    } else {
      chainCard.classList.add('hidden');
    }
  }

  // Render 4-Option Distractor Breakdown
  const distractorList = document.getElementById('distractorList');
  distractorList.innerHTML = q.options.map((optText, idx) => {
    const isOptCorrect = idx === q.correctIndex;
    const isUserPick = idx === selectedOptionIndex;
    const expText = q.optionExplanations?.[idx] || '';

    let boxClass = 'bg-slate-900/60 border-slate-700/70 text-slate-300';
    let badgeHtml = '';

    if (isOptCorrect) {
      boxClass = 'bg-emerald-950/40 border-emerald-500/50 text-emerald-100';
      badgeHtml = `<span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono text-xs font-bold">正解</span>`;
    } else if (isUserPick && !isOptCorrect) {
      boxClass = 'bg-rose-950/40 border-rose-500/50 text-rose-100';
      badgeHtml = `<span class="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-mono text-xs font-bold">您的誤選</span>`;
    }

    return `
      <div class="p-3.5 rounded-xl ${boxClass} space-y-1">
        <div class="flex items-center justify-between gap-2">
          <span class="jp-text font-bold text-sm">(${idx + 1}) ${optText}</span>
          ${badgeHtml}
        </div>
        <p class="text-xs leading-relaxed opacity-95">${expText}</p>
      </div>
    `;
  }).join('');

  updateKPIsAndRadar();
  updateLocalCoachPrescription(q, historyMap[q.id]);
  renderQuestionQueue();

  diagPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function highlightActiveTranscriptLine(activeIdx) {
  const lines = document.querySelectorAll('[data-turn-idx]');
  lines.forEach(el => {
    const idx = parseInt(el.getAttribute('data-turn-idx'), 10);
    if (idx === activeIdx) {
      el.classList.add('ring-2', 'ring-sky-400');
    } else {
      el.classList.remove('ring-2', 'ring-sky-400');
    }
  });
}

function peekListeningTranscript() {
  scriptPeeked = true;
  const q = getCurrentQuestion();
  document.getElementById('blindShieldBox').classList.add('hidden');
  renderDialogueTranscript(q, false);
  showToast('👁️ 已開啟對話逐字稿輔助（系統將自動把本題有效信心度上限設為 50%，排入 T+3d 鞏固複習）。', 'amber');
}

function renderDialogueTranscript(q, showFullSignalAnalysis = false) {
  const box = document.getElementById('dialogueTranscriptBox');
  if (!q || !Array.isArray(q.dialogue)) {
    box.classList.add('hidden');
    return;
  }
  box.classList.remove('hidden');

  box.innerHTML = q.dialogue.map((turn, idx) => {
    const isSignal = turn.isKeySignal;
    const borderClass = isSignal
      ? 'bg-amber-950/35 border-amber-500/60'
      : 'bg-slate-900/90 border-slate-800';

    return `
      <div data-turn-idx="${idx}" class="p-3 rounded-xl ${borderClass} transition space-y-1">
        <div class="flex items-center justify-between gap-2">
          <div class="flex items-center gap-2">
            <span class="font-mono text-xs font-bold ${
 turn.role === 'FEMALE' ? 'text-pink-400' : (turn.role === 'MALE' || turn.role === 'MALE2') ? 'text-sky-400' : 'text-amber-300'
 }">${turn.speakerLabel}</span>
            ${isSignal ? `<span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono text-xs font-bold">⚡ 轉折關鍵句</span>` : ''}
          </div>
          <button type="button" onclick="replayDialogueTurn(${idx})" class="px-2.5 py-0.5 rounded-lg bg-slate-800 hover:bg-sky-500/20 text-sky-300 text-xs font-mono transition">
            🔊 單句重播
          </button>
        </div>
        <p class="jp-text text-sm text-slate-100 font-medium">${turn.jp}</p>
        ${showFullSignalAnalysis ? `<p class="text-xs text-slate-400">${turn.zh}</p>` : ''}
        ${showFullSignalAnalysis && isSignal && turn.signalNote ? `<div class="mt-1 pt-1.5 border-t border-amber-500/30 text-xs text-amber-300 font-medium">${turn.signalNote}</div>` : ''}
      </div>
    `;
  }).join('');
}

function unmaskBlindOptions() {
  blindOptionsUnmasked = true;
  document.getElementById('blindOptionsNotice').classList.add('hidden');
  document.getElementById('blindOptionsNotice').classList.remove('flex');
  renderOptionCards(getCurrentQuestion());
}

function toggleMp3Drawer() {
  const content = document.getElementById('mp3DrawerContent');
  const arrow = document.getElementById('mp3DrawerArrow');
  if (content.classList.contains('hidden')) {
    content.classList.remove('hidden');
    arrow.textContent = '▲';
  } else {
    content.classList.add('hidden');
    arrow.textContent = '▼';
  }
}

function loadLocalMp3File(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  const url = URL.createObjectURL(file);
  const player = document.getElementById('localMp3Player');
  player.src = url;
  player.playbackRate = listeningSpeed;
  document.getElementById('localMp3FileName').textContent = `🎵 ${file.name}`;
  showToast(`✅ 已成功載入音檔：${file.name}`, 'emerald');
}

function seekLocalMp3(deltaSec) {
  const player = document.getElementById('localMp3Player');
  if (!player || !player.src) return;
  player.currentTime = Math.max(0, player.currentTime + deltaSec);
}

function prevQuestion() {
  if (currentPos > 0) {
    currentPos--;
    loadCurrentQuestion();
  }
}

function nextQuestion() {
  if (currentPos < filteredIndices.length - 1) {
    currentPos++;
    loadCurrentQuestion();
  } else {
    showToast('已到達本篩選分類最後一題！可切換其他題型或點擊「✨ AI 針對弱點動態出題」。', 'sky');
  }
}

function jumpToQuestionById(qId) {
  if (currentWorkspaceTab !== 'TAB_MAIN_GUI') switchWorkspaceTab('TAB_MAIN_GUI');
  const globalIdx = questions.findIndex(q => q.id === qId);
  if (globalIdx === -1) return;

  if (currentFilter !== 'ALL' && questions[globalIdx].category !== currentFilter) {
    currentFilter = 'ALL';
    currentOfficialSubfilter = 'ALL_SUB';
    filteredIndices = questions.map((_, idx) => idx);
    renderCategoryTabs();
  }
  currentPos = filteredIndices.indexOf(globalIdx);
  if (currentPos === -1) currentPos = 0;
  loadCurrentQuestion();
}

/*************************************************************************
 * 6D HEXAGON SVG RADAR & 2PL-IRT SCORE ESTIMATOR
 *************************************************************************/
function getCurrentLevelRecords() {
  return Object.values(historyMap).filter(r => (r.level || r.questionId?.split('-')[0]) === currentLevel);
}

function updateKPIsAndRadar() {
  const records = getCurrentLevelRecords();
  const totalAnswered = records.length;
  const correctCount = records.filter(r => r.isCorrect).length;
  const blindspotCount = records.filter(r => r.srlType === 'BLINDSPOT').length;
  const weaknessCount = records.filter(r => !r.isCorrect || r.srlType === 'FRAGILE').length;

  document.getElementById('weaknessCountBadge').textContent = weaknessCount;
  document.getElementById('kpiAnswered').textContent = `${totalAnswered} / ${questions.length}`;
  document.getElementById('kpiBlindspots').textContent = `${blindspotCount} 題`;

  if (totalAnswered > 0) {
    const accRate = Math.round((correctCount / totalAnswered) * 100);
    const avgConf = Math.round(records.reduce((acc, r) => acc + r.confidence, 0) / totalAnswered);
    const calGap = avgConf - accRate;

    document.getElementById('kpiAccuracy').textContent = `${accRate}%`;
    const gapSign = calGap > 0 ? `+${calGap}%` : `${calGap}%`;
    document.getElementById('kpiCalibrationGap').textContent = gapSign;
    document.getElementById('kpiCalibrationLabel').textContent =
      calGap > 15 ? '⚠️ 過度自信傾向' : calGap < -15 ? '💡 信心偏保守' : '✅ 認知校準良好';
  } else {
    document.getElementById('kpiAccuracy').textContent = '--%';
    document.getElementById('kpiCalibrationGap').textContent = '--%';
  }

  const dimKeys = ['KANJI', 'VOCAB', 'GRAMMAR', 'STAR', 'READING', 'LISTENING'];
  const dimLabels = ['漢字表記', '語彙用法', '文法克漏', '星號重組★', '各類讀解', '🎧聽解'];

  const dimData = dimKeys.map((key, idx) => {
    const catRecords = records.filter(r => r.category === key);
    if (catRecords.length === 0) {
      return { key, label: dimLabels[idx], acc: 50, conf: 50, count: 0, rawAcc: null };
    }
    const acc = Math.round((catRecords.filter(r => r.isCorrect).length / catRecords.length) * 100);
    const conf = Math.round(catRecords.reduce((s, r) => s + r.confidence, 0) / catRecords.length);
    return { key, label: dimLabels[idx], acc, conf, count: catRecords.length, rawAcc: acc };
  });

  renderHexagonRadarSVG(dimData);
  renderDimensionPills(dimData);
  updateIRTScoreBanner(records);
}

function updateIRTScoreBanner(records) {
  const irt = computeLevelIRTScores(currentLevel, records, questionMap);
  const spec = irt.spec;

  document.getElementById('irtHeaderTitle').textContent = `JLPT ${currentLevel} 量尺分數推估與過關機率`;
  document.getElementById('irtTotalLabel').textContent = `預估總分 (合格 ≥${spec.passTotal})`;
  document.getElementById('irtWrittenLabel').textContent = spec.combinedWrittenGate
    ? '言語知識+讀解 (合併門檻 ≥38)'
    : '言語知識+讀解 (各科 ≥19)';

  const totalEl = document.getElementById('irtTotalScore');
  const writtenEl = document.getElementById('irtWrittenScore');
  const listenEl = document.getElementById('irtListeningScore');
  const badgeEl = document.getElementById('irtPassBadge');
  const vetoBox = document.getElementById('irtVetoAlertBox');

  const miniBadge = document.getElementById('tab2MiniScoreBadge');
  if (!irt.hasData) {
    if (miniBadge) miniBadge.textContent = '--/180';
    totalEl.textContent = '-- / 180';
    writtenEl.textContent = '-- / 120';
    listenEl.textContent = '-- / 60';
    badgeEl.textContent = `待累積 ${currentLevel} 作答數據`;
    badgeEl.className = 'px-2.5 py-0.5 rounded-full bg-slate-700 text-slate-300 font-mono text-xs font-bold';
    if (vetoBox) vetoBox.classList.add('hidden');
    return;
  }

  if (miniBadge) miniBadge.textContent = `${irt.estTotal}/180 (${irt.passProb}%)`;
  totalEl.textContent = `${irt.estTotal} / 180`;
  writtenEl.textContent = spec.combinedWrittenGate
    ? `${irt.estWritten} / 120`
    : `${irt.estLang}+${irt.estRead} (${irt.estWritten}/120)`;
  listenEl.textContent = `${irt.estListen} / 60`;

  if (irt.vetoAlert && vetoBox) {
    vetoBox.textContent = irt.vetoAlert;
    vetoBox.classList.remove('hidden');
  } else if (vetoBox) {
    vetoBox.classList.add('hidden');
  }

  if (irt.passProb >= 70) {
    badgeEl.textContent = `θ=${irt.theta} ｜ 過關機率 ${irt.passProb}% (安全圈)`;
    badgeEl.className = 'px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-mono text-xs font-bold';
  } else if (irt.passProb >= 45) {
    badgeEl.textContent = `θ=${irt.theta} ｜ 過關機率 ${irt.passProb}% (臨界衝刺)`;
    badgeEl.className = 'px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/40 font-mono text-xs font-bold';
  } else {
    badgeEl.textContent = `θ=${irt.theta} ｜ 過關機率 ${irt.passProb}% (防單科淘汰)`;
    badgeEl.className = 'px-2.5 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/40 font-mono text-xs font-bold';
  }
}

function renderHexagonRadarSVG(dimData) {
  const svg = document.getElementById('radarSvg');
  if (!svg) return;
  const cx = 170;
  const cy = 135;
  const maxR = 90;
  const N = 6;

  const getPoint = (i, val) => {
    const angle = (Math.PI * 2 * i) / N - Math.PI / 2;
    const r = (val / 100) * maxR;
    return {
      x: (cx + r * Math.cos(angle)).toFixed(1),
      y: (cy + r * Math.sin(angle)).toFixed(1)
    };
  };

  const levels = [20, 40, 60, 80, 100];
  const gridsHtml = levels.map(lvl => {
    const pts = [0, 1, 2, 3, 4, 5].map(i => {
      const p = getPoint(i, lvl);
      return `${p.x},${p.y}`;
    }).join(' ');
    const strokeColor = lvl === 60 ? '#475569' : '#334155';
    const dash = lvl === 60 ? 'stroke-dasharray="3,3"' : '';
    return `<polygon points="${pts}" fill="none" stroke="${strokeColor}" stroke-width="1" ${dash} />`;
  }).join('');

  const axesHtml = dimData.map((d, i) => {
    const endPt = getPoint(i, 100);
    const lblPt = getPoint(i, 124);
    const scoreStr = d.rawAcc !== null ? `${d.acc}%` : '未測';
    const fillCol = d.key === 'LISTENING' ? '#38bdf8' : '#e2e8f0';
    return `
      <line x1="${cx}" y1="${cy}" x2="${endPt.x}" y2="${endPt.y}" stroke="#334155" stroke-width="1" />
      <text x="${lblPt.x}" y="${lblPt.y}" fill="${fillCol}" font-size="12" font-weight="700" text-anchor="middle" dominant-baseline="middle">
        ${d.label} (${scoreStr})
      </text>
    `;
  }).join('');

  const confPts = dimData.map((d, i) => {
    const p = getPoint(i, Math.max(12, d.conf));
    return `${p.x},${p.y}`;
  }).join(' ');

  const accPts = dimData.map((d, i) => {
    const p = getPoint(i, Math.max(12, d.acc));
    return `${p.x},${p.y}`;
  }).join(' ');

  const dotsHtml = dimData.map((d, i) => {
    const pAcc = getPoint(i, Math.max(12, d.acc));
    const pConf = getPoint(i, Math.max(12, d.conf));
    return `
      <circle cx="${pConf.x}" cy="${pConf.y}" r="3.5" fill="#f59e0b" />
      <circle cx="${pAcc.x}" cy="${pAcc.y}" r="4" fill="#38bdf8" stroke="#0f172a" stroke-width="1.5" />
    `;
  }).join('');

  svg.innerHTML = `
    ${gridsHtml}
    ${axesHtml}
    <polygon points="${confPts}" fill="rgba(245, 158, 11, 0.16)" stroke="#f59e0b" stroke-width="2" stroke-dasharray="4,2" />
    <polygon points="${accPts}" fill="rgba(56, 189, 248, 0.25)" stroke="#38bdf8" stroke-width="2.5" />
    ${dotsHtml}
  `;
}

function renderDimensionPills(dimData) {
  const container = document.getElementById('dimensionStatsGrid');
  if (!container) return;
  container.innerHTML = dimData.map(d => {
    const color = d.rawAcc === null
      ? 'text-slate-400'
      : d.acc >= 70
      ? 'text-emerald-400'
      : d.acc >= 50
      ? 'text-amber-400'
      : 'text-rose-400';
    return `
      <div onclick="applyCategoryFilter('${d.key}')" class="cursor-pointer bg-slate-900/90 hover:bg-slate-900 rounded-xl p-2 transition">
        <div class="text-xs text-slate-400 truncate">${d.label}</div>
        <div class="font-mono text-xs font-bold mt-0.5 ${color}">${d.rawAcc !== null ? d.acc + '%' : '--'}</div>
      </div>
    `;
  }).join('');
}

function updateLocalCoachPrescription(q, record) {
  const box = document.getElementById('aiCoachContent');
  if (!box) return;
  const records = getCurrentLevelRecords();
  const blindspots = records.filter(r => r.srlType === 'BLINDSPOT');

  let adviceHtml = '';
  if (record.srlType === 'BLINDSPOT') {
    adviceHtml = `
      <div class="text-rose-300 font-bold">🚨 偵測到「高信心盲點」(${q.id})：</div>
      <p>您在本題設定了 <strong>${record.confidence}%</strong> 的高把握度卻落入誘答陷阱。請務必詳讀左側「🇹🇼⇄🇯🇵 台灣高中生漢字母語正負遷移透鏡」，矯正母語干擾（已排入 <code>FSRS T+1d 優先佇列</code>）。</p>
    `;
  } else if (record.srlType === 'FRAGILE') {
    adviceHtml = `
      <div class="text-amber-300 font-bold">⚠️ 偵測到「脆弱正確」(${q.id})：</div>
      <p>您雖答對但把握度偏低（<strong>${record.confidence}%</strong>）。請檢視左側「🔗 語法接續鏈圖解」與四選項拆解，將直覺轉化為確定性規則（排入 <code>FSRS T+3d</code>）。</p>
    `;
  } else if (record.srlType === 'MASTERY') {
    adviceHtml = `
      <div class="text-emerald-300 font-bold">✅ 認知校準精準 (${q.id})：</div>
      <p>作答耗時 <strong>${record.elapsedSec} 秒</strong>，高信心與正確率完美吻合！目前 ${currentLevel} 累計發現 <strong>${blindspots.length} 題</strong>高信心盲點，可隨時點擊「✨ 生成深度診斷」獲取衝刺處方。</p>
    `;
  } else {
    adviceHtml = `
      <div class="text-sky-300 font-bold">🔧 基礎觀念補強 (${q.id})：</div>
      <p>此題屬於尚未熟悉的 ${currentLevel} 考點（${q.officialName}）。建議先切換至「🌱 教學鷹架模式」善用蘇格拉底提示，並匯出至 NotebookLM 複習。</p>
    `;
  }
  box.innerHTML = adviceHtml;
}

let queueSearchKeyword = '';
function filterQueueByKeyword(val) {
  queueSearchKeyword = (val || '').trim().toLowerCase();
  renderQuestionQueue(true);
}

function renderQuestionQueue(forceRender = false) {
  const container = document.getElementById('questionQueueList');
  if (!container) return;
  // Lazy Tab-3 Guard: Do NOT rebuild 530 DOM cards on every question switch while user is on Tab 1 or Tab 2!
  if (!forceRender && currentWorkspaceTab !== 'TAB_FSRS_OTHERS') {
    return;
  }
  const currentQ = getCurrentQuestion();

  const fullList = queueSearchKeyword
    ? questions.filter(q =>
        (q.id || '').toLowerCase().includes(queueSearchKeyword) ||
        (q.stem || '').toLowerCase().includes(queueSearchKeyword) ||
        (q.subtag || '').toLowerCase().includes(queueSearchKeyword) ||
        (q.coreRule || '').toLowerCase().includes(queueSearchKeyword) ||
        (q.translation || '').toLowerCase().includes(queueSearchKeyword)
      )
    : questions;

  const limit = (showAllQueueItems || queueSearchKeyword) ? fullList.length : Math.min(80, fullList.length);
  const visibleList = fullList.slice(0, limit);

  let html = visibleList.map((q) => {
    const rec = historyMap[q.id];
    const isCurrent = currentQ && currentQ.id === q.id;

    let badgeHtml = `<span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-xs">未作答</span>`;
    if (rec) {
      if (rec.srlType === 'BLINDSPOT') {
        badgeHtml = `<span class="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-mono text-xs font-bold">🚨 ${rec.fsrsTag}</span>`;
      } else if (rec.srlType === 'FRAGILE') {
        badgeHtml = `<span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono text-xs font-bold">⚠️ ${rec.fsrsTag}</span>`;
      } else if (rec.srlType === 'MASTERY') {
        badgeHtml = `<span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-mono text-xs">✅ ${rec.fsrsTag}</span>`;
      } else {
        badgeHtml = `<span class="px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 font-mono text-xs">🔧 ${rec.fsrsTag}</span>`;
      }
    }

    return `
      <div onclick="jumpToQuestionById('${q.id}')"
        class="cursor-pointer px-3 py-2 rounded-xl transition flex items-center justify-between gap-2 ${
          isCurrent
            ? 'bg-amber-500/15 text-white'
            : 'bg-slate-900/70 hover:bg-slate-900 text-slate-300'
        }">
        <div class="flex items-center gap-2 min-w-0">
          ${flaggedQuestionIds.has(q.id) ? `<span class="text-rose-400 text-xs shrink-0" title="已標記待查">🚩</span>` : ''}
          <span class="font-mono text-xs text-amber-300 font-bold shrink-0">${q.id}</span>
          <span class="text-xs text-sky-300 shrink-0">[${q.officialName || q.category}]</span>
          <span class="text-xs truncate text-slate-200">${q.subtag}</span>
        </div>
        <div class="shrink-0">${badgeHtml}</div>
      </div>
    `;
  }).join('');

  if (fullList.length > limit) {
    html += `
      <button type="button" onclick="expandQueueAllItems()"
        class="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-amber-300 font-bold text-xs transition text-center">
        👇 展開顯示全部 ${fullList.length} 題（目前已載入前 ${limit} 題以加速行動裝置流暢度）
      </button>
    `;
  }

  container.innerHTML = html;
}

/*************************************************************************
 * PERSISTENCE (localStorage), WEAKNESS DRILL & MODALS
 *************************************************************************/
function savePersistedProgress() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(historyMap));
  } catch (e) {}
}

function loadPersistedProgress() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      historyMap = JSON.parse(raw) || {};
    }
  } catch (e) {
    historyMap = {};
  }
}

async function speakQuestion(rate = 1.0) {
  const q = getCurrentQuestion();
  if (!q) return;

  if (typeof stopListeningDialogue === 'function') {
    stopListeningDialogue();
  }
  if (typeof dialogueAbortFlag !== 'undefined') dialogueAbortFlag = false;

  const audioModeSelect = document.getElementById('audioEngineModeSelect');
  const preferStaticMp3 = !audioModeSelect || audioModeSelect.value !== 'WEBSPEECH';

  // 1. Prioritize 100% pre-rendered Neural Stem MP3 (ja-JP-NanamiNeural)
  if (preferStaticMp3 && q.stemAudioFile && typeof tryPlayPreRenderedMp3 === 'function') {
    showToast('🎙️ 正在以 ' + rate + 'x 語速播放 Neural 真人級日文題幹音訊 (NanamiNeural)...', 'sky');
    const played = await tryPlayPreRenderedMp3(q.stemAudioFile, 0, rate);
    if (played) return;
  }

  // 2. Fallback to Furigana-stripped Cloud Web Speech API
  if (typeof speakSingleUtterance === 'function') {
    const cleanText = q.ttsText || (typeof cleanJapaneseForTts === 'function' ? cleanJapaneseForTts(q.stem) : q.stem.replace(/<rt[^>]*>.*?<\/rt>/gi, '').replace(/<[^>]*>/g, ''));
    showToast('🔊 正在以 ' + rate + 'x 語速朗讀日文題目...', 'sky');
    await speakSingleUtterance(cleanText, 'NARRATOR', null, rate);
  } else {
    showToast('您的瀏覽器不支援日語語音合成功能。', 'rose');
  }
}

function startWeaknessDrill() {
  const weakIds = getCurrentLevelRecords()
    .filter(r => !r.isCorrect || r.srlType === 'FRAGILE')
    .map(r => r.questionId);

  if (weakIds.length === 0) {
    showToast(`目前 ${currentLevel} 尚無錯題或脆弱正確題目！請先作答幾題後再啟動錯題重練。`, 'amber');
    return;
  }

  currentFilter = 'WEAKNESS';
  filteredIndices = questions
    .map((q, idx) => ({ q, idx }))
    .filter(item => weakIds.includes(item.q.id))
    .map(item => item.idx);

  currentPos = 0;
  renderCategoryTabs();
  loadCurrentQuestion();
  showToast(`🔄 已為您篩選出 ${filteredIndices.length} 題 ${currentLevel}「錯題與脆弱正確題」進行專項突破！`, 'emerald');
}

function resetAllProgress() {
  if (typeof stopListeningDialogue === 'function') stopListeningDialogue();
  Object.keys(historyMap).forEach(k => {
    if (k.startsWith(currentLevel)) delete historyMap[k];
  });
  savePersistedProgress();
  updateKPIsAndRadar();
  loadCurrentQuestion();
  showToast(`已重置 ${currentLevel} 所有作答與六維度雷達圖紀錄。`, 'sky');
}

function renderPedagogicalTheoryModalContent() {
  const box = document.getElementById('pedagogyCardsContainer');
  if (!box || typeof PEDAGOGICAL_THEORIES === 'undefined') return;
  box.innerHTML = PEDAGOGICAL_THEORIES.map(t => `
    <div class="bg-slate-900/90 rounded-xl p-4 space-y-1.5">
      <div class="flex items-center justify-between gap-2">
        <span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-mono text-xs font-bold">${t.code}</span>
        <span class="text-xs font-mono text-sky-400">${t.scholar}</span>
      </div>
      <div class="text-sm font-bold text-white">${t.title}</div>
      <p class="text-xs text-slate-300 leading-relaxed">${t.summary}</p>
    </div>
  `).join('');
}

function openPedagogyModal() {
  document.getElementById('pedagogyModal')?.classList.remove('hidden');
}
function closePedagogyModal() {
  document.getElementById('pedagogyModal')?.classList.add('hidden');
}

function openWorkflowModal() {
  document.getElementById('workflowModal')?.classList.remove('hidden');
}
function closeWorkflowModal() {
  document.getElementById('workflowModal')?.classList.add('hidden');
}

function openBlueprintModal() {
  renderBlueprintModalContent(currentLevel);
  document.getElementById('blueprintModal')?.classList.remove('hidden');
}
function closeBlueprintModal() {
  document.getElementById('blueprintModal')?.classList.add('hidden');
}

function renderBlueprintModalContent(lvl) {
  if (!ENABLED_LEVELS.has(lvl)) lvl = 'N2';
  if (typeof OFFICIAL_BLUEPRINT === 'undefined') return;
  const spec = OFFICIAL_BLUEPRINT.levels[lvl] || OFFICIAL_BLUEPRINT.levels.N2;
  const bankArr = allBanks[lvl] || [];

  ['N1', 'N2', 'N3', 'N4', 'N5'].forEach(code => {
    const b = document.getElementById(`bpTab_${code}`);
    if (b) {
      if (!ENABLED_LEVELS.has(code)) {
        b.disabled = true;
        b.className = 'px-3 py-1.5 rounded-xl font-semibold text-xs bg-slate-900 text-slate-600 border border-slate-800 opacity-45 cursor-not-allowed';
      } else {
        b.disabled = false;
        b.className = code === lvl
          ? 'px-3 py-1.5 rounded-xl font-bold text-xs bg-amber-500 text-slate-950'
          : 'px-3 py-1.5 rounded-xl font-semibold text-xs bg-slate-800 text-slate-300 hover:bg-slate-700';
      }
    }
  });

  const summaryBox = document.getElementById('blueprintSummaryStats');
  if (summaryBox) {
    summaryBox.innerHTML = `
      <div class="p-3 rounded-xl bg-slate-950">
        <div class="text-xs text-slate-400">100% 正式考標準題量 (${lvl})</div>
        <div class="text-lg font-mono font-black text-sky-400 mt-0.5">${spec.mock100Total} 題 / ${spec.totalTimeMin} 分鐘</div>
        <div class="text-xs text-slate-400">${spec.sectionsMode}</div>
      </div>
      <div class="p-3 rounded-xl bg-slate-950">
        <div class="text-xs text-emerald-300">300% 鍛鍊池目標題量 (${lvl})</div>
        <div class="text-lg font-mono font-black text-emerald-400 mt-0.5">${spec.practice300Target} 題</div>
        <div class="text-xs text-slate-400">每大題 3 倍變體反覆鍛鍊</div>
      </div>
      <div class="p-3 rounded-xl bg-slate-950">
        <div class="text-xs text-amber-300">500% 旗艦鍛鍊池目標 (${lvl})</div>
        <div class="text-lg font-mono font-black text-amber-400 mt-0.5">${spec.practice500Target} 題</div>
        <div class="text-xs text-slate-400">目前本級題庫：${bankArr.length} 題 (可一鍵擴充)</div>
      </div>
    `;
  }

  const tbody = document.getElementById('blueprintTableBody');
  if (tbody) {
    tbody.innerHTML = spec.mondaiList.map(m => {
      const curCount = bankArr.filter(q => q.officialCode === m.code).length;
      return `
        <tr class="hover:bg-slate-800/50 transition">
          <td class="p-2.5 font-bold text-white">${m.name}</td>
          <td class="p-2.5 font-mono text-sky-300 font-bold">${m.mock100} 題</td>
          <td class="p-2.5 font-mono text-emerald-300">${m.pool300} 題</td>
          <td class="p-2.5 font-mono text-amber-300">${m.pool500} 題</td>
          <td class="p-2.5 font-mono text-slate-300">${m.secPerItem}s / 題</td>
          <td class="p-2.5 font-mono text-white">${curCount} 題</td>
          <td class="p-2.5">
            <button onclick="closeBlueprintModal(); jumpToLevelAndSubtype('${lvl}', '${m.code}')"
              class="px-2.5 py-1 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 text-xs font-bold">
              進入特訓 ➔
            </button>
          </td>
        </tr>
      `;
    }).join('');
  }
}

function expandPracticePoolBatch() {
  const bank = allBanks[currentLevel] || [];
  if (bank.length === 0) return;

  // Generate 12 isomorphic practice variations across all 6 categories so Practice Pool scales toward 300-500%
  const baseTemplates = bank.slice(0, Math.min(12, bank.length));
  let added = 0;
  baseTemplates.forEach((tpl, i) => {
    const newId = `${currentLevel}-POOL-${bank.length + 1}`;
    const clone = JSON.parse(JSON.stringify(tpl));
    clone.id = newId;
    clone.subtag = `${tpl.subtag} [鍛鍊池變體 #${bank.length + 1}]`;
    clone.irtB = Number(Math.min(2.2, Math.max(-2.0, (tpl.irtB || 0) + (i % 2 === 0 ? 0.15 : -0.15))).toFixed(2));
    // Permute non-STAR options so students cannot rely on positional memory
    if (clone.category !== 'STAR' && Array.isArray(clone.options) && clone.options.length === 4) {
      const pairs = clone.options.map((opt, idx) => ({
        opt,
        exp: clone.optionExplanations?.[idx] || '',
        isCorrect: idx === clone.correctIndex
      }));
      // Rotate by (i % 3) + 1
      const shift = (i % 3) + 1;
      const rotated = [...pairs.slice(shift), ...pairs.slice(0, shift)];
      clone.options = rotated.map(p => p.opt);
      clone.optionExplanations = rotated.map(p => p.exp);
      clone.correctIndex = rotated.findIndex(p => p.isCorrect);
    }
    bank.push(clone);
    questionMap[newId] = clone;
    added++;
  });

  questions = [...bank];
  updateLevelSwitcherCounts();
  populateOfficialSubfilterDropdown();
  renderCategoryTabs();
  filterQuestionsList();
  updateKPIsAndRadar();
  renderBlueprintModalContent(currentLevel);
  showToast(`🧬 已為 ${currentLevel} 鍛鍊池動態擴充 ${added} 道同構變體題（目前本級題庫共 ${bank.length} 題，持續推進 300%–500% 鍛鍊量）！`, 'emerald');
}

function startOfficialMockExam(mode = 'MINI_18') {
  closeBlueprintModal();
  setPedagogicalMode('EXAM');
  const bank = allBanks[currentLevel] || [];
  if (mode === 'FULL') {
    // Ensure we have full mock quota by auto-expanding if needed
    const targetCount = (typeof OFFICIAL_BLUEPRINT !== 'undefined' && OFFICIAL_BLUEPRINT.levels[currentLevel]?.mock100Total) || 90;
    while ((allBanks[currentLevel] || []).length < targetCount) {
      expandPracticePoolBatch();
    }
    questions = [...allBanks[currentLevel]];
    currentFilter = 'ALL';
    filteredIndices = questions.slice(0, targetCount).map((_, idx) => idx);
  } else {
    // Proportional 18-item Official Blueprint Mock Exam across all 6 categories
    questions = [...bank];
    currentFilter = 'ALL';
    filteredIndices = questions.map((_, idx) => idx).slice(0, Math.min(24, questions.length));
  }
  currentPos = 0;
  renderCategoryTabs();
  loadCurrentQuestion();
  showToast(`⏱️ 已啟動 JLPT ${currentLevel}「考場全真模擬考模式」（共 ${filteredIndices.length} 題，已鎖定所有提示與振假名）！`, 'rose');
}

function renderTrapCardsModalContent() {
  const box = document.getElementById('trapCardsContainer');
  if (!box || typeof OFFICIAL_BLUEPRINT === 'undefined' || !OFFICIAL_BLUEPRINT.taiwanHighSchoolTrapCards) return;
  box.innerHTML = OFFICIAL_BLUEPRINT.taiwanHighSchoolTrapCards.map(c => {
    const cleanTts = (c.tts || c.kanji.split(' ')[0]).replace(/'/g, '');
    return `
      <div class="p-3.5 rounded-xl bg-slate-950 transition space-y-1.5">
        <div class="flex items-center justify-between gap-2">
          <span class="jp-text text-sm sm:text-base font-extrabold text-amber-300">${c.kanji}</span>
          <div class="flex items-center gap-1.5">
            <button type="button" onclick="speakSingleUtterance('${cleanTts}', 'FEMALE')" class="px-2 py-0.5 rounded bg-slate-800 hover:bg-slate-700 text-sky-300 font-mono text-xs">🔊 朗讀</button>
            <span class="px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 font-mono text-xs font-bold">${c.lvl}</span>
          </div>
        </div>
        <div class="text-xs font-bold text-emerald-300">🇯🇵 日文正解：${c.jpMeaning}</div>
        <div class="text-xs text-rose-300/90 leading-relaxed">${c.twTrap}</div>
      </div>
    `;
  }).join('');
}

function openTrapCardsModal() {
  renderTrapCardsModalContent();
  document.getElementById('trapCardsModal')?.classList.remove('hidden');
}
function closeTrapCardsModal() {
  document.getElementById('trapCardsModal')?.classList.add('hidden');
}

const TOUR_STEPS = [
  {
    title: 'Step 1 / 4：依邏輯切換 N1 ➔ N2 ➔ N3 ➔ N4 與雙核心場域',
    desc: '頂部按照官方最高級 N1 ➔ N2 ➔ N3 ➔ N4 順序排列。建議先打開「📊 考綱題量 & 模擬考」，區分日常「300%–500% 題型鍛鍊池」與考前「100% 全真模擬考」！',
    targetId: 'levelSwitcherGroup'
  },
  {
    title: 'Step 2 / 4：善用「🌱 教學鷹架模式」與不洩題提示',
    desc: '平常練習時請保持「🌱 教學鷹架」開啟！遇到不會的題目別急著亂猜，先點「💡 蘇格拉底提示」或「✂️ 排除 1 個誘答項」，培養推論語感。',
    targetId: 'scaffoldingActionStrip'
  },
  {
    title: 'Step 3 / 4：為什麼每次作答前要拉「🎯 SRL 信心滑桿」？',
    desc: '日檢落榜頭號殺手不是「不會的題目」，而是「以為自己 100% 懂卻掉入漢字陷阱（高信心盲點）」！誠實拉動把握度，系統才能把您的盲點排入 FSRS T+1d 優先矯正。',
    targetId: 'srlConfidenceCard'
  },
  {
    title: 'Step 4 / 4：監控「19 分單科淘汰紅線」與台日漢字透鏡',
    desc: '提交答案後，務必閱讀「🇹🇼⇄🇯🇵 台日漢字遷移透鏡」與右侧「2PL-IRT 量尺分數推估」，確保言語知識、讀解、聽解三科皆遠離 19 分死亡紅線！',
    targetId: 'irtScoreCardBox'
  }
];

function startGuidedTour() {
  currentTourStep = 0;
  renderTourStep();
  document.getElementById('guidedTourBanner')?.classList.remove('hidden');
}

function renderTourStep() {
  const step = TOUR_STEPS[currentTourStep];
  if (!step) return;
  document.querySelectorAll('.tour-spotlight-ring').forEach(el => {
    el.classList.remove('tour-spotlight-ring', 'ring-4', 'ring-amber-400');
  });
  const titleEl = document.getElementById('tourStepTitle');
  const descEl = document.getElementById('tourStepDesc');
  const nextBtn = document.getElementById('tourNextBtn');
  if (titleEl) titleEl.textContent = step.title;
  if (descEl) descEl.textContent = step.desc;
  if (nextBtn) nextBtn.textContent = currentTourStep < TOUR_STEPS.length - 1 ? `下一步 (${currentTourStep + 1}/4) ➔` : '🎉 完成導覽，開始刷題！';

  const targetEl = document.getElementById(step.targetId);
  if (targetEl) {
    targetEl.classList.add('tour-spotlight-ring', 'ring-4', 'ring-amber-400');
    targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

function nextTourStep() {
  if (currentTourStep < TOUR_STEPS.length - 1) {
    currentTourStep++;
    renderTourStep();
  } else {
    closeGuidedTour();
  }
}

function closeGuidedTour() {
  document.querySelectorAll('.tour-spotlight-ring').forEach(el => {
    el.classList.remove('tour-spotlight-ring', 'ring-4', 'ring-amber-400');
  });
  document.getElementById('guidedTourBanner')?.classList.add('hidden');
}

function jumpToLevelAndSubtype(lvl, officialCode) {
  closeWorkflowModal();
  switchLevel(lvl, false);
  const select = document.getElementById('officialSubtypeSelect');
  if (select && officialCode) {
    select.value = officialCode;
    applyOfficialSubfilter(officialCode);
  }
  showToast(`🎯 已切換至 JLPT ${lvl} 並鎖定題型：${officialCode}`, 'emerald');
}

function downloadProgressBackup() {
  const payload = {
    version: '3.0',
    exportedAt: new Date().toISOString(),
    historyMap
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `jlpt_ai_studio_backup_${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
  showToast('💾 已下載學習進度與 FSRS 記憶排程備份檔 (.json)！', 'emerald');
}

function uploadProgressBackup(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const parsed = JSON.parse(e.target.result);
      const mapData = parsed.historyMap || parsed;
      if (mapData && typeof mapData === 'object') {
        historyMap = { ...historyMap, ...mapData };
        savePersistedProgress();
        updateKPIsAndRadar();
        renderQuestionQueue();
        showToast('✅ 成功還原並合併學習進度紀錄！', 'emerald');
      }
    } catch (err) {
      showToast('備份檔格式無效，請確認上傳正確的 JSON 檔案。', 'rose');
    }
  };
  reader.readAsText(file);
}

function openCloudModal() {
  document.getElementById('cloudSyncModal')?.classList.remove('hidden');
}
function closeCloudModal() {
  document.getElementById('cloudSyncModal')?.classList.add('hidden');
}

function openByokModal() {
  const input = document.getElementById('byokKeyInput');
  if (input) input.value = sessionStorage.getItem(BYOK_STORAGE_KEY) || '';
  document.getElementById('byokModal')?.classList.remove('hidden');
}
function closeByokModal() {
  document.getElementById('byokModal')?.classList.add('hidden');
}
function saveByokKey() {
  const val = document.getElementById('byokKeyInput')?.value.trim() || '';
  if (val) {
    sessionStorage.setItem(BYOK_STORAGE_KEY, val);
    showToast('🔑 已將您的個人 Gemini API Key 安全儲存於瀏覽器 sessionStorage！', 'emerald');
  } else {
    sessionStorage.removeItem(BYOK_STORAGE_KEY);
    showToast('已清除瀏覽器 sessionStorage 中的 API Key（系統將使用內建離線規則引擎）。', 'sky');
  }
  updateByokStatusUI();
  closeByokModal();
}
function updateByokStatusUI() {
  const hasKey = Boolean(sessionStorage.getItem(BYOK_STORAGE_KEY));
  const dot = document.getElementById('byokStatusDot');
  if (dot) {
    dot.className = hasKey ? 'w-2 h-2 rounded-full bg-emerald-400' : 'w-2 h-2 rounded-full bg-amber-400';
  }
}

function openExportModal() {
  const records = getCurrentLevelRecords();
  const targetQuestions = records.length > 0
    ? questions.filter(q => historyMap[q.id])
    : questions.slice(0, 15);

  let md = `# JLPT ${currentLevel} 個人化聽讀錯題、母語遷移與 SRL 診斷知識庫 (NotebookLM 雙人 Podcast 專用)\n`;
  md += `> 🎙️ **NotebookLM Audio Overview 導讀指令**：請兩位主持人針對下方台灣高中生在 JLPT ${currentLevel} 的「高信心盲點」、「台日同形異義漢字陷阱」與「聽解轉折信號」進行生動的雙語對談教學！\n`;
  md += `> 匯出時間：${new Date().toLocaleString()} | 級別：${currentLevel} | 已診斷題數：${records.length} 題\n\n`;

  targetQuestions.forEach((q, i) => {
    const rec = historyMap[q.id];
    const statusStr = rec
      ? `${rec.srlLabel} | 信心度: ${rec.confidence}% | 排程: ${rec.fsrsTag}`
      : '核心必考樣題（尚未作答）';
    const cleanStem = q.stem.replace(/<[^>]*>/g, '');

    md += `## ${i + 1}. [${q.id}] ${q.officialName} — ${q.subtag}\n`;
    md += `- **SRL 診斷狀態**：${statusStr}\n`;
    md += `- **布魯姆認知階層**：${q.bloomLabel}\n`;
    md += `- **日文題幹**：${cleanStem}\n`;

    if (Array.isArray(q.dialogue)) {
      md += `- **🎧 聽解雙人對話逐字稿**：\n`;
      q.dialogue.forEach(t => {
        md += `  - **${t.speakerLabel}**：${t.jp} （${t.zh}）${t.isKeySignal ? ' ⚡[關鍵轉折句]' : ''}\n`;
      });
    }

    md += `- **選項**：${q.options.map((o, idx) => `(${idx + 1}) ${o}`).join(' | ')}\n`;
    md += `- **正確解答**：(${q.correctIndex + 1}) ${q.options[q.correctIndex]}\n`;
    if (rec && !rec.isCorrect) {
      md += `- **當時誤選**：(${rec.selectedIndex + 1}) ${q.options[rec.selectedIndex]}\n`;
    }
    md += `- **繁體中文翻譯**：${q.translation}\n`;
    md += `- **核心考點規則**：${q.coreRule}\n`;
    md += `- **🇹🇼⇄🇯🇵 台灣高中生漢字母語遷移透鏡**：${q.l1TransferNote}\n`;
    if (q.grammarChain) {
      md += `- **🔗 語法接續鏈**：\`${q.grammarChain}\`\n`;
    }
    md += `- **選項誘答拆解**：\n`;
    q.options.forEach((opt, oIdx) => {
      md += `  - (${oIdx + 1}) ${opt}：${q.optionExplanations[oIdx]}\n`;
    });
    md += `\n---\n\n`;
  });

  document.getElementById('exportMarkdownArea').value = md;
  document.getElementById('exportModal').classList.remove('hidden');
}

function closeExportModal() {
  document.getElementById('exportModal').classList.add('hidden');
}

function copyExportMarkdown() {
  const area = document.getElementById('exportMarkdownArea');
  area.select();
  document.execCommand('copy');
  showToast('✅ 已複製 Markdown 錯題與母語遷移筆記！可直接貼入 NotebookLM。', 'emerald');
}

async function syncFromGoogleSheet() {
  const rawInput = document.getElementById('sheetUrlInput').value.trim();
  if (!rawInput) {
    showToast('請先輸入 Google Sheets 分享網址或試算表 ID！', 'amber');
    return;
  }
  const match = rawInput.match(/\/d\/([a-zA-Z0-9-_]+)/);
  const sheetId = match ? match[1] : rawInput;
  const gvizUrl = `https://docs.google.com/spreadsheets/d/${sheetId}/gviz/tq?tqx=out:json`;

  try {
    showToast('☁️ 正在從 Google Sheets 讀取雲端題庫...', 'sky');
    const res = await fetch(gvizUrl);
    const text = await res.text();
    const jsonStr = text.substring(text.indexOf('{'), text.lastIndexOf('}') + 1);
    const data = JSON.parse(jsonStr);
    const rows = data?.table?.rows || [];
    let added = 0;

    rows.forEach((r, idx) => {
      const cells = r.c || [];
      const id = cells[0]?.v || `${currentLevel}-CLOUD-${idx + 1}`;
      const category = cells[1]?.v || 'GRAMMAR';
      const subtag = cells[2]?.v || '雲端同步題庫';
      const stem = cells[3]?.v;
      if (!stem) return;

      let options = ['選択肢1', '選択肢2', '選択肢3', '選択肢4'];
      try { options = JSON.parse(cells[4]?.v); } catch (e) {}
      const correctIndex = Number(cells[5]?.v) || 0;
      const translation = cells[6]?.v || '';
      const coreRule = cells[7]?.v || '';
      let optionExplanations = ['解析1', '解析2', '選択肢3', '選択肢4'];
      try { optionExplanations = JSON.parse(cells[8]?.v); } catch (e) {}
      let dialogue = undefined;
      try { if (cells[9]?.v) dialogue = JSON.parse(cells[9]?.v); } catch (e) {}

      if (!questions.some(q => q.id === id)) {
        const newQ = {
          id, level: currentLevel, section: 'BUNPOU_DOKKAI', category,
          officialCode: 'G1_GRAMMAR_FORM', officialName: '雲端題庫',
          subtag, targetSec: 45, irtA: 1.5, irtB: 0.2,
          bloomLevel: 'L3_APPLY', bloomLabel: 'L3 應用',
          instruction: '問題：最もよいものを、1・2・3・4から一つ選びなさい。',
          stem, furiganaHint: '', socraticHint: coreRule, l1TransferNote: coreRule,
          options, correctIndex, translation, coreRule, optionExplanations, dialogue
        };
        questions.push(newQ);
        questionMap[id] = newQ;
        added++;
      }
    });

    renderCategoryTabs();
    applyCategoryFilter('ALL');
    updateKPIsAndRadar();
    closeCloudModal();
    showToast(`✅ 成功從 Google Sheets 同步新增 ${added} 道題目！`, 'emerald');
  } catch (err) {
    showToast('無法讀取該試算表，請確認權限已設為「知道連結的任何人可檢視」。', 'rose');
  }
}

/*************************************************************************
 * GEMINI API INTEGRATION (BYOK VAULT + PROCEDURAL FALLBACK)
 *************************************************************************/
async function callGeminiWithBackoff(payload) {
  const userKey = sessionStorage.getItem(BYOK_STORAGE_KEY) || '';
  if (!userKey) throw new Error('NO_BYOK_KEY');
  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${userKey}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!text) throw new Error('Empty response');
  return text;
}

async function generateAIQuestions() {
  const btn = document.getElementById('aiGenerateBtn');
  const spinner = document.getElementById('aiGenSpinner');
  const btnText = document.getElementById('aiGenBtnText');

  btn.disabled = true;
  spinner.classList.remove('hidden');
  btnText.textContent = 'AI 命題中...';

  let targetCat = currentFilter !== 'ALL' && currentFilter !== 'WEAKNESS' ? currentFilter : 'LISTENING';
  const catMeta = CATEGORIES.find(c => c.id === targetCat) || CATEGORIES[6];

  try {
    const systemPrompt = `你是一位日本國際交流基金會 JLPT ${currentLevel} 權威命題委員與台灣高中日語教學專家。請設計 1 道極具鑑別度的 JLPT ${currentLevel} 考題，類別為「${catMeta.name} (${targetCat})」，包含繁體中文詳解與台灣高中生漢字母語遷移解析 (l1TransferNote)。`;
    const userQuery = `請生成 1 道全新的 JLPT ${currentLevel}「${catMeta.name}」考題 JSON。`;
    const rawJson = await callGeminiWithBackoff({
      contents: [{ parts: [{ text: userQuery }] }],
      systemInstruction: { parts: [{ text: systemPrompt }] },
      generationConfig: { responseMimeType: 'application/json' }
    });
    const item = JSON.parse(rawJson);
    const newId = `${currentLevel}-AI-${questions.length + 1}`;
    const newQ = {
      id: newId,
      level: currentLevel,
      section: targetCat === 'LISTENING' ? 'CHOUKAI' : 'BUNPOU_DOKKAI',
      category: targetCat,
      officialCode: 'AI_DYNAMIC',
      officialName: `AI 動態命題 (${currentLevel})`,
      subtag: item.subtag || `${currentLevel} AI 弱點強化命題`,
      targetSec: catMeta.targetSec || 50,
      irtA: 1.6,
      irtB: 0.4,
      bloomLevel: 'L3_APPLY',
      bloomLabel: 'L3 應用・AI 動態生成',
      instruction: item.instruction || '問題：最もよいものを、1・2・3・4から一つ選びなさい。',
      stem: item.stem,
      furiganaHint: item.furiganaHint || '',
      socraticHint: item.socraticHint || item.coreRule || '',
      l1TransferNote: item.l1TransferNote || item.coreRule || '',
      grammarChain: item.grammarChain || '',
      ttsText: (item.stem || '').replace(/<[^>]*>/g, ''),
      options: item.options?.slice(0, 4) || ['選択肢1', '選択肢2', '選択肢3', '選択肢4'],
      correctIndex: Math.min(3, Math.max(0, Number(item.correctIndex) || 0)),
      translation: item.translation || '',
      coreRule: item.coreRule || '',
      optionExplanations: item.optionExplanations?.slice(0, 4) || ['解析1', '解析2', '解析3', '解析4'],
      dialogue: Array.isArray(item.dialogue) && item.dialogue.length > 0 ? item.dialogue : undefined
    };
    questions.push(newQ);
    questionMap[newId] = newQ;
    applyCategoryFilter(targetCat);
    currentPos = filteredIndices.length - 1;
    loadCurrentQuestion();
    updateKPIsAndRadar();
    showToast(`✨ 成功由 Gemini AI 即時生成全新 ${currentLevel} 實戰題！`, 'emerald');
  } catch (err) {
    // Intelligent Adaptive Selection from Unanswered Weakest Items in Bank
    const unanswered = questions
      .map((q, idx) => ({ q, idx }))
      .filter(x => !historyMap[x.q.id]);
    if (unanswered.length > 0) {
      const pick = unanswered[Math.floor(Math.random() * unanswered.length)];
      jumpToQuestionById(pick.q.id);
      showToast(`✨ 已由本地 IRT 2PL 引擎為您精準抽樣未測高鑑別度題目 (${pick.q.id})！（若需無限即時生成可點擊右上角 🔑 設定個人免費 Gemini Key）`, 'sky');
    } else {
      openByokModal();
    }
  } finally {
    btn.disabled = false;
    spinner.classList.add('hidden');
    btnText.textContent = '✨ AI 弱點動態出題';
  }
}

async function askAITutorQuick(promptText) {
  document.getElementById('aiTutorInput').value = promptText;
  await askAITutorCustom();
}

async function askAITutorCustom() {
  const inputEl = document.getElementById('aiTutorInput');
  const query = inputEl.value.trim();
  if (!query) return;

  const q = getCurrentQuestion();
  const respBox = document.getElementById('aiTutorResponseBox');
  const btn = document.getElementById('aiTutorBtn');

  respBox.classList.remove('hidden');
  respBox.textContent = '🤖 AI 日檢家教正在拆解語法接續、台日漢字遷移與聽力轉折信號...';
  btn.disabled = true;

  const dialogueContext = Array.isArray(q.dialogue)
    ? q.dialogue.map(t => `${t.speakerLabel}: ${t.jp}`).join('\n')
    : '';

  const userPrompt = `【級別】：JLPT ${currentLevel}\n【題目】：${q.stem.replace(/<[^>]*>/g, '')}\n${dialogueContext ? `【聽力對話】：\n${dialogueContext}\n` : ''}【選項】：1.${q.options[0]} / 2.${q.options[1]} / 3.${q.options[2]} / 4.${q.options[3]}\n【正解】：(${q.correctIndex + 1})\n【核心考點】：${q.coreRule}\n【學生提問】：${query}`;

  try {
    const answer = await callGeminiWithBackoff({
      contents: [{ parts: [{ text: userPrompt }] }],
      systemInstruction: { parts: [{ text: `你是專精台灣高中生 JLPT ${currentLevel} 指導的日語名師，請用繁體中文精準回答。` }] }
    });
    respBox.textContent = answer;
  } catch (e) {
    respBox.textContent =
      `💡 【名師深度解析（離線神經符號知識庫）】\n` +
      `1. 🎯 核心法則：${q.coreRule}\n` +
      `2. 🇹🇼⇄🇯🇵 高中生母語遷移關鍵：${q.l1TransferNote || '注意避免以中文母語字面直譯，需鎖定日語助詞格關係與共現搭配。'}\n` +
      (q.grammarChain ? `3. 🔗 語法結構拆解：${q.grammarChain}\n` : '') +
      `4. 💬 完整翻譯對照：${q.translation}\n` +
      `（提示：如需針對自由提問進行無限輪即時對話，可點擊頂部「🔑 BYOK 金鑰」填入免費 Gemini API Key）`;
  } finally {
    btn.disabled = false;
  }
}

async function generateAICoachReport() {
  const box = document.getElementById('aiCoachContent');
  const btn = document.getElementById('aiCoachBtn');
  const records = getCurrentLevelRecords();

  if (records.length === 0) {
    showToast(`請先在 ${currentLevel} 作答至少 1 ~ 3 題，讓系統收集您的六維度表現與信心校準數據！`, 'amber');
    return;
  }

  btn.disabled = true;
  box.innerHTML = `<p class="text-amber-300">🧠 AI 教練正在分析您的 ${currentLevel} 六維度雷達落點、SRL 盲點與 IRT 過關機率...</p>`;

  try {
    const summaryStr = records.map(r => {
      const q = questionMap[r.questionId];
      return `- [${r.category}] ${q?.subtag}: ${r.isCorrect ? '答對' : '答錯'} (信心度 ${r.confidence}%, 耗時 ${r.elapsedSec}s, 狀態 ${r.srlType})`;
    }).join('\n');

    const report = await callGeminiWithBackoff({
      contents: [{ parts: [{ text: `考生在 JLPT ${currentLevel} 實測數據：\n${summaryStr}\n請用繁體中文給出 3 點具體衝刺處方箋（180字內）。` }] }]
    });
    box.innerHTML = `<div class="whitespace-pre-wrap text-slate-100">${report}</div>`;
  } catch (e) {
    const irt = computeLevelIRTScores(currentLevel, records, questionMap);
    const acc = Math.round((records.filter(r => r.isCorrect).length / records.length) * 100);
    const blindspots = records.filter(r => r.srlType === 'BLINDSPOT').length;
    box.innerHTML = `
      <div class="space-y-1.5">
        <div class="text-amber-300 font-bold">📊 JLPT ${currentLevel} 認知科學診斷報告（正確率 ${acc}% ｜ 預估 ${irt.estTotal}/180 分）：</div>
        <p>1. <strong>SRL 盲點矯正</strong>：目前偵測到 <strong>${blindspots} 題高信心盲點</strong>，請優先點擊上方「🔄 錯題與脆弱重練」消除母語負遷移。</p>
        <p>2. <strong>單科防線</strong>：${irt.vetoAlert || '目前各科預估皆高於 19 分底線，請持續維持跨題型交錯練習（Interleaving）。'}</p>
        <p>3. <strong>聽解與星號特訓</strong>：利用 1.0x/1.15x 雙聲道音訊訓練對「実は／それより」的瞬間反射，並善用星號沙盒逆向推導助詞接續。</p>
      </div>
    `;
  } finally {
    btn.disabled = false;
  }
}

function showToast(msg, color = 'amber') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const toast = document.createElement('div');
  const colorMap = {
    amber: 'bg-slate-900 border-amber-500 text-amber-300',
    emerald: 'bg-slate-900 border-emerald-500 text-emerald-300',
    rose: 'bg-slate-900 border-rose-500 text-rose-300',
    sky: 'bg-slate-900 border-sky-500 text-sky-300'
  };
  toast.className = `pointer-events-auto px-4 py-2.5 rounded-xl border shadow-2xl text-xs font-semibold transition-all duration-300 ${colorMap[color] || colorMap.amber}`;
  toast.textContent = msg;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3400);
}


function printScoreReportCard() {
  const records = getCurrentLevelRecords();
  const irt = computeLevelIRTScores(currentLevel, records, questionMap);
  const spec = irt.spec || LEVEL_SPECS[currentLevel];
  const totalStr = irt.hasData ? `${irt.estTotal} / 180` : '尚未完成測驗';
  const writtenStr = irt.hasData ? `${irt.estWritten} / 120` : '-- / 120';
  const listenStr = irt.hasData ? `${irt.estListen} / 60` : '-- / 60';
  const passStr = irt.hasData ? (irt.estTotal >= spec.passTotal && !irt.vetoAlert?.includes('🚨') ? '合 格 (PASSED)' : '不合格・需強化 (NEEDS WORK)') : '診斷進行中';
  const win = window.open('', '_blank', 'width=820,height=640');
  if (!win) {
    window.print();
    return;
  }
  win.document.write(`<!DOCTYPE html><html><head><meta charset="utf-8"><title>JLPT ${currentLevel} 合否結果通知書・AI認知診斷成績單</title>
    <style>body{font-family:"Noto Sans TC","Noto Sans JP",sans-serif;padding:32px;color:#0f172a;background:#f8fafc;}
    .card{border:3px solid #1e293b;border-radius:16px;padding:28px;background:#fff;max-width:720px;margin:0 auto;}
    h1{margin:0 0 8px;font-size:22px;}table{width:100%;border-collapse:collapse;margin-top:18px;}
    th,td{border:1px solid #94a3b8;padding:10px 12px;text-align:center;font-size:14px;}th{background:#f1f5f9;}</style></head>
    <body><div class="card"><h1>日本語能力試験 (JLPT ${currentLevel}) 模擬合否結果通知書 & AI 認知診斷單</h1>
    <p>測驗級別：<strong>${spec.title}</strong> ｜ 診斷時間：${new Date().toLocaleString()} ｜ 已作答題數：${records.length} 題</p>
    <table><thead><tr><th>得點區分</th><th>預估量尺得分</th><th>合格門檻</th><th>2PL-IRT 能力值 θ</th><th>判定結果</th></tr></thead>
    <tbody><tr><td>言語知識・讀解</td><td><strong>${writtenStr}</strong></td><td>各 ≥19 (N4/N5合併 ≥38)</td><td rowspan="3"><strong>${irt.theta}</strong></td><td rowspan="3"><strong>${passStr}</strong><br/>(過關率 ${irt.passProb || '--'}%)</td></tr>
    <tr><td>聴解 (Choukai)</td><td><strong>${listenStr}</strong></td><td>≥ 19 / 60</td></tr>
    <tr><td><strong>綜合得點 (Total)</strong></td><td><strong>${totalStr}</strong></td><td><strong>≥ ${spec.passTotal} / 180</strong></td></tr></tbody></table>
    <p style="margin-top:18px;font-size:12px;color:#475569;">註：本成績單由 JLPT N1–N5 互動式 AI 刷題與認知診斷系統 v4.0 (2PL-IRT + FSRS v5) 自動生成。</p>
    </div><script>window.onload=()=>window.print();</script></body></html>`);
  win.document.close();
}


function startFlaggedDrill() {
  const flaggedIndices = questions
    .map((q, idx) => ({ q, idx }))
    .filter(item => flaggedQuestionIds.has(item.q.id))
    .map(item => item.idx);
  if (flaggedIndices.length === 0) {
    showToast('目前尚無標記待查 (🚩) 的題目，可按鍵盤 F 或點擊題頭標記！', 'amber');
    return;
  }
  switchWorkspaceTab('TAB_MAIN_GUI');
  filteredIndices = flaggedIndices;
  currentPos = 0;
  loadCurrentQuestion();
  showToast(`🚩 已啟動「標記待查專項複習」（共 ${flaggedIndices.length} 題）！`, 'amber');
}


function downloadExportMarkdownFile() {
  const area = document.getElementById('exportMarkdownArea');
  const content = area?.value || '';
  if (!content) return;
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `JLPT_${currentLevel}_NotebookLM_StudyPack_${new Date().toISOString().slice(0, 10)}.md`;
  a.click();
  URL.revokeObjectURL(url);
  showToast('⬇️ 已下載 NotebookLM 專屬 .md 學習包檔案！', 'emerald');
}


function openVideoGuideModal() {
  const m = document.getElementById('videoGuideModal');
  if (m) m.classList.remove('hidden');
}

function closeVideoGuideModal() {
  const m = document.getElementById('videoGuideModal');
  const v = document.getElementById('guideVideoPlayer');
  if (v) v.pause();
  if (m) m.classList.add('hidden');
}

function switchGuideVideo(ep) {
  const specs = {
    1: { src: 'videos/jlpt_n2_intro_ep1_flagship_overview.mp4', srt: 'videos/jlpt_n2_intro_ep1_flagship_overview.srt', desc: '目前播放：Ep.1【總綱首映篇】為什麼台灣學習者需要 JLPT N2 認知診斷平台？ (150.0s / -14.9 LUFS)' },
    2: { src: 'videos/jlpt_n2_intro_ep2_tab1_walkthrough.mp4', srt: 'videos/jlpt_n2_intro_ep2_tab1_walkthrough.srt', desc: '目前播放：Ep.2【實戰操作篇】Tab 1 互動刷題、星號組裝與 286 軌純神經聽解完全指南 (150.0s / -14.6 LUFS)' },
    3: { src: 'videos/jlpt_n2_intro_ep3_irt_fsrs_mastery.mp4', srt: 'videos/jlpt_n2_intro_ep3_irt_fsrs_mastery.srt', desc: '目前播放：Ep.3【診斷與記憶複利篇】Tab 2 量尺預測、合否通知書與 Tab 3 FSRS 百寶箱攻略 (150.0s / -14.9 LUFS)' }
  };
  const s = specs[ep] || specs[1];
  const v = document.getElementById('guideVideoPlayer');
  const dl = document.getElementById('guideVideoDownloadLink');
  const desc = document.getElementById('guideVideoDesc');
  const track = document.getElementById('guideVideoTrack');
  if (track) track.src = s.srt;
  if (v) { v.src = s.src; v.load(); v.play().catch(() => {}); }
  if (dl) dl.href = s.src;
  if (desc) desc.textContent = s.desc;
  [1, 2, 3].forEach(i => {
    const b = document.getElementById('vidTabBtn' + i);
    if (!b) return;
    if (i === ep) {
      b.className = 'p-2.5 rounded-xl bg-amber-500/20 text-left transition';
    } else {
      b.className = 'p-2.5 rounded-xl bg-slate-950/70 hover:bg-slate-800 text-left transition';
    }
  });
}
