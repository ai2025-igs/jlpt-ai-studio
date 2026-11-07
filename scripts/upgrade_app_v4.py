# -*- coding: utf-8 -*-
"""
upgrade_app_v4.py
Upgrades assets/js/app.js for JLPT N1-N5 Interactive AI Studio v4.0:
- 5 Levels (N1 -> N2 -> N3 -> N4 -> N5) with Official JLPT Theme Colors
- 3-Tab 1080P Workspace Switcher (TAB_MAIN_GUI, TAB_IRT_COACH, TAB_FSRS_OTHERS)
- Dual Question Pool Scope (POOL_300 [1,443 items] vs MOCK_100 [481 items])
- Official JLPT Sample Top Mondai Bar (1..14 Written + 🔊15..19 Listening)
- Official 2x2 Capsule Option Pills & SVG Click-to-Zoom Lightbox
"""
from pathlib import Path

p = Path(r"d:\MuseAcademy_50_25C16\jlpt-ai-studio\assets\js\app.js")
txt = p.read_text(encoding="utf-8")

# 1. Expand allBanks to include N5 and add currentPoolScope / currentWorkspaceTab
txt = txt.replace(
    "let allBanks = { N1: [], N2: [], N3: [], N4: [] };",
    "let allBanks = { N1: [], N2: [], N3: [], N4: [], N5: [] };\nlet currentPoolScope = 'POOL_300'; // 'POOL_300' | 'MOCK_100'\nlet currentWorkspaceTab = 'TAB_MAIN_GUI';\nconst OFFICIAL_HEX = { N1: '#00a383', N2: '#f39c42', N3: '#8c6bb1', N4: '#ef6c67', N5: '#1e78b4' };"
)

# 2. Fetch N1..N5 in loadAllQuestionBanks
txt = txt.replace(
    "const levels = ['N1', 'N2', 'N3', 'N4'];",
    "const levels = ['N1', 'N2', 'N3', 'N4', 'N5'];"
)

# 3. Replace updateLevelSwitcherCounts & switchLevel
old_switch = """function updateLevelSwitcherCounts() {
  ['N1', 'N2', 'N3', 'N4'].forEach(lvl => {
    const cntEl = document.getElementById(`lvlCount_${lvl}`);
    if (cntEl && allBanks[lvl]) {
      cntEl.textContent = `${allBanks[lvl].length}題`;
    }
  });
}

function switchLevel(lvl, showNotification = true) {
  if (typeof stopListeningDialogue === 'function') stopListeningDialogue();
  currentLevel = lvl;
  questions = [...(allBanks[lvl] || [])];
  currentFilter = 'ALL';
  currentOfficialSubfilter = 'ALL_SUB';

  // Update Level Switcher Pills UI (Ordered N1 -> N2 -> N3 -> N4 with High-Contrast Count Badge)
  ['N1', 'N2', 'N3', 'N4'].forEach(code => {
    const btn = document.getElementById(`lvlBtn_${code}`);
    const cnt = document.getElementById(`lvlCount_${code}`);
    if (!btn) return;
    if (code === lvl) {
      btn.className = 'px-3.5 py-2 rounded-xl font-bold text-xs transition flex items-center gap-2 bg-gradient-to-r from-amber-400 to-amber-500 text-slate-950 shadow-lg shadow-amber-500/20 border border-amber-300';
      if (cnt) cnt.className = 'px-1.5 py-0.5 rounded-md bg-slate-950 text-amber-300 border border-amber-300/40 font-mono text-[10px] font-bold shadow-inner';
    } else {
      btn.className = 'px-3.5 py-2 rounded-xl font-semibold text-xs transition flex items-center gap-2 bg-slate-800/90 hover:bg-slate-700 text-slate-300 border border-slate-700';
      if (cnt) cnt.className = 'px-1.5 py-0.5 rounded-md bg-slate-950 text-slate-300 border border-slate-700/80 font-mono text-[10px]';
    }
  });"""

new_switch = """function updateLevelSwitcherCounts() {
  let totalPool = 0;
  ['N1', 'N2', 'N3', 'N4', 'N5'].forEach(lvl => {
    const cntEl = document.getElementById(`lvlCount_${lvl}`);
    const arr = allBanks[lvl] || [];
    totalPool += arr.length;
    const mockCnt = arr.filter(q => q.inMock100).length || (LEVEL_SPECS[lvl]?.mock100Count || 80);
    if (cntEl && arr.length > 0) {
      cntEl.textContent = `${arr.length}題(模${mockCnt})`;
    }
  });
  const qBadge = document.getElementById('tab3QueueBadge');
  if (qBadge) qBadge.textContent = `${totalPool.toLocaleString()}題`;
}

function getScopedBank(lvl) {
  const raw = allBanks[lvl] || [];
  if (currentPoolScope === 'MOCK_100') {
    const mockItems = raw.filter(q => q.inMock100);
    return mockItems.length > 0 ? mockItems : raw;
  }
  return raw;
}

function setQuestionPoolScope(scope) {
  currentPoolScope = scope;
  const b300 = document.getElementById('poolBtn300');
  const b100 = document.getElementById('poolBtn100');
  const tagEl = document.getElementById('officialExamPoolTag');
  if (scope === 'POOL_300') {
    if (b300) b300.className = 'px-2.5 py-1 rounded-lg text-[11px] font-bold bg-sky-500 text-slate-950 transition';
    if (b100) b100.className = 'px-2.5 py-1 rounded-lg text-[11px] font-semibold text-slate-300 hover:text-white transition';
    if (tagEl) tagEl.textContent = '300%池';
  } else {
    if (b100) b100.className = 'px-2.5 py-1 rounded-lg text-[11px] font-bold bg-rose-500 text-white transition';
    if (b300) b300.className = 'px-2.5 py-1 rounded-lg text-[11px] font-semibold text-slate-300 hover:text-white transition';
    if (tagEl) tagEl.textContent = '100%模考';
  }
  questions = [...getScopedBank(currentLevel)];
  populateOfficialSubfilterDropdown();
  renderCategoryTabs();
  filterQuestionsList();
  renderQuestionQueue();
  showToast(scope === 'MOCK_100'
    ? `⏱️ 已切換至 JLPT ${currentLevel}「100% 正式檢定標準題量」（共 ${questions.length} 題）！`
    : `🏋️ 已切換至 JLPT ${currentLevel}「300% 擴充實戰鍛鍊池」（共 ${questions.length} 題）！`, 'sky');
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
  if (tabId === 'TAB_FSRS_OTHERS') renderQuestionQueue();
}

function switchLevel(lvl, showNotification = true) {
  if (typeof stopListeningDialogue === 'function') stopListeningDialogue();
  currentLevel = lvl;
  const hex = OFFICIAL_HEX[lvl] || '#f39c42';
  document.documentElement.style.setProperty('--jlpt-active-theme', hex);

  const rawArr = allBanks[lvl] || [];
  const mockCnt = rawArr.filter(q => q.inMock100).length || (LEVEL_SPECS[lvl]?.mock100Count || 80);
  const pool300El = document.getElementById('pool300CountText');
  const mock100El = document.getElementById('mock100CountText');
  if (pool300El) pool300El.textContent = rawArr.length;
  if (mock100El) mock100El.textContent = mockCnt;

  const sbMock = document.getElementById('standbyMock100Val');
  const sbPool300 = document.getElementById('standbyPool300Val');
  const sbPool500 = document.getElementById('standbyPool500Val');
  if (sbMock) sbMock.textContent = `${mockCnt} 題`;
  if (sbPool300) sbPool300.textContent = `${rawArr.length} 題`;
  if (sbPool500) sbPool500.textContent = `${mockCnt * 5} 題`;

  questions = [...getScopedBank(lvl)];
  currentFilter = 'ALL';
  currentOfficialSubfilter = 'ALL_SUB';

  // Update 5-Level Switcher Pills UI (Ordered N1 -> N2 -> N3 -> N4 -> N5 with Official JLPT Hex Colors)
  ['N1', 'N2', 'N3', 'N4', 'N5'].forEach(code => {
    const btn = document.getElementById(`lvlBtn_${code}`);
    const cnt = document.getElementById(`lvlCount_${code}`);
    if (!btn) return;
    if (code === lvl) {
      btn.className = 'px-3 py-1.5 rounded-xl font-extrabold text-xs transition flex items-center gap-1.5 text-white shadow-lg border-2 border-white';
      btn.style.backgroundColor = OFFICIAL_HEX[code];
      if (cnt) cnt.className = 'px-1.5 py-0.5 rounded bg-slate-950 text-amber-300 border border-white/40 font-mono text-[10px] font-bold';
    } else {
      btn.className = 'px-3 py-1.5 rounded-xl font-bold text-xs transition flex items-center gap-1.5 bg-slate-800/90 hover:bg-slate-700 text-slate-200 border border-slate-700';
      btn.style.backgroundColor = '';
      if (cnt) cnt.className = 'px-1.5 py-0.5 rounded bg-slate-950 text-slate-300 border border-slate-700 font-mono text-[10px]';
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
  if (brandBadge) brandBadge.style.backgroundColor = hex;"""

assert old_switch in txt, "old_switch not found"
txt = txt.replace(old_switch, new_switch)

# 4. Update title version to v4.0 in switchLevel
txt = txt.replace(
    "if (brandTitle) brandTitle.textContent = `JLPT ${lvl} 互動式 AI 刷題與認知診斷系統 v3.1`;",
    "if (brandTitle) brandTitle.textContent = `JLPT ${lvl} 互動式 AI 刷題與認知診斷系統 v4.0`;"
)
txt = txt.replace(
    "if ((lvl === 'N3' || lvl === 'N4') && pedagogicalMode === 'SCAFFOLD') {",
    "if ((lvl === 'N3' || lvl === 'N4' || lvl === 'N5') && pedagogicalMode === 'SCAFFOLD') {"
)

# 5. Add Official Mondai Number Bar renderer & Standby/Diagnostic toggle inside loadCurrentQuestion
old_load_top = """  document.getElementById('diagnosticPanel')?.classList.add('hidden');
  document.getElementById('aiTutorResponseBox')?.classList.add('hidden');"""

new_load_top = """  document.getElementById('diagnosticPanel')?.classList.add('hidden');
  document.getElementById('preAnswerStandbyCard')?.classList.remove('hidden');
  document.getElementById('aiTutorResponseBox')?.classList.add('hidden');"""

assert old_load_top in txt, "old_load_top not found"
txt = txt.replace(old_load_top, new_load_top)

# Update situationSvgWrapper visibility in loadCurrentQuestion
old_svg_block = """  // Render Situational SVG Card (for N3/N4 Utterance Expressions L4_UTTERANCE)
  const svgBox = document.getElementById('situationSvgBox');
  if (svgBox) {
    if (q.situationSvg) {
      svgBox.innerHTML = q.situationSvg;
      svgBox.classList.remove('hidden');
    } else {
      svgBox.innerHTML = '';
      svgBox.classList.add('hidden');
    }
  }"""

new_svg_block = """  // Render Official Top Mondai Numbered Bar (1..14 Written + 🔊15..19 Listening)
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
  }"""

assert old_svg_block in txt, "old_svg_block not found"
txt = txt.replace(old_svg_block, new_svg_block)

# 6. Upgrade renderOptionCards to use Official JLPT 2x2 Capsule Pill styling
old_opt_btn = """      <button type="button" onclick="selectOption(${idx})" ${isEliminated ? 'disabled' : ''}
        class="w-full text-left p-4 rounded-xl border transition-all flex items-start gap-3 group ${cardStyle}">
        <span class="w-7 h-7 rounded-lg font-mono text-xs font-bold flex items-center justify-center shrink-0 mt-0.5 ${
          isSelected
            ? 'bg-amber-400 text-slate-950'
            : 'bg-slate-800 text-slate-300 group-hover:bg-slate-700'
        }">
          ${idx + 1}
        </span>
        <span class="jp-text text-base font-medium flex-1 ${isMasked ? 'text-slate-500 italic text-xs' : ''}">${displayLabel}</span>
      </button>"""

new_opt_btn = """      <button type="button" onclick="selectOption(${idx})" ${isEliminated ? 'disabled' : ''}
        class="jlpt-capsule-option w-full text-left px-4 py-3 border-2 transition-all flex items-center gap-3 group ${cardStyle}">
        <span class="w-7 h-7 rounded-full font-mono text-xs font-black flex items-center justify-center shrink-0 ${
          isSelected
            ? 'bg-amber-400 text-slate-950 shadow'
            : 'bg-slate-800 text-slate-200 border border-slate-600 group-hover:bg-slate-700'
        }">
          ${idx + 1}
        </span>
        <span class="jp-text text-sm sm:text-base font-bold flex-1 ${isMasked ? 'text-slate-500 italic text-xs' : ''}">${displayLabel}</span>
      </button>"""

assert old_opt_btn in txt, "old_opt_btn not found"
txt = txt.replace(old_opt_btn, new_opt_btn)

# 7. Hide preAnswerStandbyCard when diagnosticPanel opens on submitCurrentAnswer
txt = txt.replace(
    "  // Populate Diagnostic Panel\n  const diagPanel = document.getElementById('diagnosticPanel');\n  diagPanel.classList.remove('hidden');",
    "  // Populate Diagnostic Panel in Right-Hand 1080P Dock\n  document.getElementById('preAnswerStandbyCard')?.classList.add('hidden');\n  const diagPanel = document.getElementById('diagnosticPanel');\n  diagPanel.classList.remove('hidden');"
)

# 8. Update tab2MiniScoreBadge in updateIRTScoreBanner
txt = txt.replace(
    "  if (!irt.hasData) {\n    totalEl.textContent = '-- / 180';",
    "  const miniBadge = document.getElementById('tab2MiniScoreBadge');\n  if (!irt.hasData) {\n    if (miniBadge) miniBadge.textContent = '--/180';\n    totalEl.textContent = '-- / 180';"
)
txt = txt.replace(
    "  totalEl.textContent = `${irt.estTotal} / 180`;",
    "  if (miniBadge) miniBadge.textContent = `${irt.estTotal}/180 (${irt.passProb}%)`;\n  totalEl.textContent = `${irt.estTotal} / 180`;"
)

# 9. Update jumpToQuestionById so clicking a question in Tab 3 automatically switches to Tab 1!
txt = txt.replace(
    "function jumpToQuestionById(qId) {",
    "function jumpToQuestionById(qId) {\n  if (currentWorkspaceTab !== 'TAB_MAIN_GUI') switchWorkspaceTab('TAB_MAIN_GUI');"
)

# 10. Include N5 in renderBlueprintModalContent
txt = txt.replace(
    "['N1', 'N2', 'N3', 'N4'].forEach(code => {",
    "['N1', 'N2', 'N3', 'N4', 'N5'].forEach(code => {"
)

# 11. Append helper functions for Official Mondai Bar, SVG Zoom Modal, and Conjugation Modal at end of file
extra_helpers = """
/*************************************************************************
 * v4.0 OFFICIAL JLPT SAMPLE MONDAI NUMBER BAR & LIGHTBOX MODALS
 *************************************************************************/
function renderOfficialMondaiNumberBar(activeQ) {
  const writtenBar = document.getElementById('officialMondaiWrittenBar');
  const listenBar = document.getElementById('officialMondaiListeningBar');
  if (!writtenBar || !listenBar) return;

  // Build unique mondai list from questions
  const mondaiMap = new Map();
  questions.forEach((q, idx) => {
    const mNum = q.mondaiNum || 1;
    if (!mondaiMap.has(mNum)) {
      mondaiMap.set(mNum, {
        mondaiNum: mNum,
        officialCode: q.officialCode,
        officialName: q.officialName,
        category: q.category,
        firstIdx: idx
      });
    }
  });

  const sorted = Array.from(mondaiMap.values()).sort((a, b) => a.mondaiNum - b.mondaiNum);
  const writtenItems = sorted.filter(m => m.category !== 'LISTENING');
  const listenItems = sorted.filter(m => m.category === 'LISTENING');
  const curMondai = activeQ?.mondaiNum || 1;

  writtenBar.innerHTML = writtenItems.map(m => `
    <button type="button" onclick="jumpToMondaiNum(${m.mondaiNum})"
      title="${m.officialName}"
      class="jlpt-mondai-btn ${m.mondaiNum === curMondai ? 'active' : ''}">
      ${m.mondaiNum}
    </button>
  `).join('');

  listenBar.innerHTML = listenItems.map(m => `
    <button type="button" onclick="jumpToMondaiNum(${m.mondaiNum})"
      title="${m.officialName}"
      class="jlpt-mondai-btn ${m.mondaiNum === curMondai ? 'active' : ''}">
      🔊${m.mondaiNum}
    </button>
  `).join('');
}

function jumpToMondaiNum(mNum) {
  if (currentFilter !== 'ALL' || currentOfficialSubfilter !== 'ALL_SUB') {
    currentFilter = 'ALL';
    currentOfficialSubfilter = 'ALL_SUB';
    filteredIndices = questions.map((_, i) => i);
    renderCategoryTabs();
  }
  const targetGlobalIdx = questions.findIndex(q => (q.mondaiNum || 1) === mNum);
  if (targetGlobalIdx !== -1) {
    currentPos = filteredIndices.indexOf(targetGlobalIdx);
    if (currentPos === -1) currentPos = 0;
    loadCurrentQuestion();
  }
}

function openSvgZoomModal() {
  const q = getCurrentQuestion();
  const box = document.getElementById('svgZoomModalContent');
  const modal = document.getElementById('svgZoomModal');
  if (!q || !q.situationSvg || !box || !modal) return;
  box.innerHTML = q.situationSvg.replace('max-w-[420px]', 'max-w-[720px] w-full');
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
"""

if "renderOfficialMondaiNumberBar" not in txt:
    txt = txt + "\n" + extra_helpers

p.write_text(txt, encoding="utf-8")
print("Upgraded assets/js/app.js to v4.0 successfully!")
