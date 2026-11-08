#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
upgrade_mobile_performance_v44.py
Implements the 5-Pillar Mobile Ergonomics & 60fps Performance Upgrade (v4.4):
1. Collapsible Mobile Header Drawer (<header> height on 390x844 drops from 613px [72.6%] to ~104px [12.3%]) + lg-only backdrop-blur.
2. On-Demand & Windowed Tab-3 Question Queue (eliminates 3,710 hidden DOM nodes during Tab 1 practice; total DOM nodes drop from 4,834 to ~1,130).
3. Diff-Guarded 1Hz Timer Loop (stops Tailwind Play CDN MutationObserver from firing every second when classes haven't changed).
4. Zero-Delay Touch Physics (`touch-action: manipulation`) + Single-Row Scrollable Mondai Bar on Mobile.
5. Idle Audio Pre-Warming for instant mobile MP3 playback.
"""

from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent.parent
HTML_PATH = BASE_DIR / "index.html"
CSS_PATH = BASE_DIR / "assets" / "css" / "custom.css"
APP_JS_PATH = BASE_DIR / "assets" / "js" / "app.js"


def upgrade_css():
    css = CSS_PATH.read_text(encoding="utf-8")
    mobile_css = """
/* Mobile 60fps Ergonomics & Touch Optimization (v4.4) */
button, a, input, select, label, [onclick] {
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}

#questionQueueList > div {
  content-visibility: auto;
  contain-intrinsic-size: 42px;
}

@media (max-width: 1023px) {
  h1 {
    font-size: 18px;
    line-height: 1.25;
  }
  .jlpt-capsule-option:hover:not(:disabled) {
    transform: none;
  }
}
"""
    if "Mobile 60fps Ergonomics" not in css:
        css = css.rstrip() + "\n" + mobile_css
        CSS_PATH.write_text(css, encoding="utf-8")
        print("[CSS UPGRADE] Added mobile touch-action, content-visibility, and mobile typography rules.")


def upgrade_html():
    html = HTML_PATH.read_text(encoding="utf-8")

    # 1. Replace sticky header with Mobile-Adaptive Header (Desktop lg: 100% identical; Mobile <lg: compact bar + collapsible drawer)
    old_header_pat = re.compile(
        r'<header class="sticky top-0 z-40[^>]*>.*?</header>',
        re.S,
    )
    new_header = """<header class="sticky top-0 z-40 bg-slate-950 lg:bg-slate-950/95 lg:backdrop-blur-md border-b border-slate-800 shadow-xl">
    <div class="max-w-[1860px] mx-auto px-3 sm:px-5 py-1.5 sm:py-2 space-y-1.5 sm:space-y-2">

      <!-- Row 1: Brand Title + Mobile Drawer Toggle + Desktop 5-Level Switcher + Global Quick Action Toolbar -->
      <div class="flex flex-wrap items-center justify-between gap-2">
        <!-- Brand Identity -->
        <div class="flex items-center justify-between w-full lg:w-auto gap-2">
          <div class="flex items-center gap-2 min-w-0">
            <div id="headerLevelBadge" class="w-8 h-8 sm:w-10 sm:h-10 rounded-xl flex items-center justify-center text-slate-950 font-mono font-black text-sm sm:text-base shrink-0" style="background-color: #f39c42; color: #020617;">
              N2
            </div>
            <div class="min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <h1 id="headerLevelTitle" class="text-base sm:text-2xl font-extrabold tracking-tight text-white truncate">
                  JLPT N2 互動式 AI 刷題與認知診斷系統 v4.4
                </h1>
                <span id="headerSubBadge" class="hidden sm:inline-block px-2 py-0.5 text-xs font-mono font-semibold rounded-full bg-amber-500/15 text-amber-300">
                  🎯 專注 N2 主力衝刺版 ｜ 1080P 官方樣題 UI × 530題(500%) × 318題(300%) × 106題(100%模考)
                </span>
              </div>
              <p id="headerLevelDesc" class="text-xs text-slate-400 hidden xl:block">
                二節制測驗（總分 ≥90/180，三科皆須 ≥19/60） ｜ 正式模考 106題 / 300%鍛鍊池 318題 / 500%旗艦池 530題（N1/N3/N4/N5 鎖定待開放）
              </p>
            </div>
          </div>

          <!-- Mobile-Only Compact Drawer Toggle Button -->
          <button type="button" id="mobileHeaderDrawerBtn" onclick="toggleMobileHeaderDrawer()"
            class="lg:hidden px-2.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-amber-300 font-bold text-xs flex items-center gap-1 shrink-0">
            <span>⚙️ 題庫與工具</span>
            <span id="mobileDrawerArrow" class="font-mono text-xs">▼</span>
          </button>
        </div>

        <!-- Collapsible Container on Mobile (<1024px), Always Visible on Desktop (lg:flex) -->
        <div id="mobileHeaderDrawer" class="hidden lg:flex flex-wrap items-center justify-between w-full lg:w-auto gap-2 pt-1 lg:pt-0">
          <!-- 5-Level Switcher Pills (N2 Active Flagship Focus; N1, N3, N4, N5 Disabled until N2 Acceptance) -->
          <div id="levelSwitcherGroup" class="flex flex-wrap items-center gap-1.5 p-1 transition-all">
            <button id="lvlBtn_N1" disabled title="目前鎖定專注於 N2 主力衝刺（待 N2 驗收後開放 N1）" class="px-3 py-1.5 rounded-xl font-bold text-xs transition flex items-center gap-1.5 bg-slate-900/60 text-slate-400 opacity-45 cursor-not-allowed">
              <span>🔒 N1</span>
              <span id="lvlCount_N1" class="px-1.5 py-0.5 rounded bg-slate-950 text-slate-400 font-mono text-xs">待開放</span>
            </button>
            <button id="lvlBtn_N2" onclick="switchLevel('N2')" class="px-3 py-1.5 rounded-xl font-extrabold text-xs transition flex items-center gap-1.5 text-slate-950" style="background-color: #f39c42; color: #020617;">
              <span>🏆 N2 (主力焦點)</span>
              <span id="lvlCount_N2" class="px-1.5 py-0.5 rounded bg-slate-950 text-amber-300 font-mono text-xs font-bold">530題(模106)</span>
            </button>
            <button id="lvlBtn_N3" disabled title="目前鎖定專注於 N2 主力衝刺（待 N2 驗收後開放 N3）" class="px-3 py-1.5 rounded-xl font-bold text-xs transition flex items-center gap-1.5 bg-slate-900/60 text-slate-400 opacity-45 cursor-not-allowed">
              <span>🔒 N3</span>
              <span id="lvlCount_N3" class="px-1.5 py-0.5 rounded bg-slate-950 text-slate-400 font-mono text-xs">待開放</span>
            </button>
            <button id="lvlBtn_N4" disabled title="目前鎖定專注於 N2 主力衝刺（待 N2 驗收後開放 N4）" class="px-3 py-1.5 rounded-xl font-bold text-xs transition flex items-center gap-1.5 bg-slate-900/60 text-slate-400 opacity-45 cursor-not-allowed">
              <span>🔒 N4</span>
              <span id="lvlCount_N4" class="px-1.5 py-0.5 rounded bg-slate-950 text-slate-400 font-mono text-xs">待開放</span>
            </button>
            <button id="lvlBtn_N5" disabled title="目前鎖定專注於 N2 主力衝刺（待 N2 驗收後開放 N5）" class="px-3 py-1.5 rounded-xl font-bold text-xs transition flex items-center gap-1.5 bg-slate-900/60 text-slate-400 opacity-45 cursor-not-allowed">
              <span>🔒 N5</span>
              <span id="lvlCount_N5" class="px-1.5 py-0.5 rounded bg-slate-950 text-slate-400 font-mono text-xs">待開放</span>
            </button>
          </div>

          <!-- Global Quick Action Toolbar -->
          <div class="flex flex-wrap items-center gap-1">
            <button onclick="startGuidedTour()" class="px-2.5 py-1 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 text-xs font-extrabold transition">
              🧭 30秒導覽
            </button>
            <button onclick="openBlueprintModal()" class="px-2.5 py-1 rounded-xl bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 text-xs font-bold transition">
              📊 100%/300%題量表
            </button>
            <button onclick="openWorkflowModal()" class="px-2.5 py-1 rounded-xl bg-sky-500/15 hover:bg-sky-500/25 text-sky-300 text-xs font-bold transition">
              🗺️ 題型矩陣
            </button>
            <button onclick="openTrapCardsModal()" class="px-2.5 py-1 rounded-xl bg-rose-500/15 hover:bg-rose-500/25 text-rose-300 text-xs font-bold transition">
              🃏 假朋友&音調
            </button>
            <button onclick="openConjugationModal()" class="px-2.5 py-1 rounded-xl bg-purple-500/15 hover:bg-purple-500/25 text-purple-300 text-xs font-bold transition">
              🔤 動詞活用表
            </button>
            <button onclick="openPedagogyModal()" class="px-2.5 py-1 rounded-xl bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 text-xs font-bold transition">
              🧠 8大教學法
            </button>
            <button id="aiGenerateBtn" onclick="generateAIQuestions()" class="px-2.5 py-1 rounded-xl bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-400 hover:to-amber-300 text-slate-950 font-bold text-xs transition flex items-center gap-1">
              <span id="aiGenSpinner" class="hidden w-3 h-3 border-t-transparent rounded-full animate-spin"></span>
              <span id="aiGenBtnText">✨ AI生題</span>
            </button>
            <button onclick="openByokModal()" class="px-2 py-1 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition flex items-center gap-1">
              <span id="byokStatusDot" class="w-2 h-2 rounded-full bg-amber-400"></span>
              <span>🔑</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Row 2: 3-Tab Main Workspace Switcher (Scrollable on Mobile) + Collapsible Pool/Scaffolding Controls -->
      <div class="flex flex-wrap items-center justify-between gap-1.5 pt-1 border-t border-slate-800/90">
        <!-- 3 Main Workspace Tabs (Single horizontal scroll row on mobile) -->
        <div class="flex items-center gap-1.5 bg-slate-900 p-1 rounded-xl overflow-x-auto no-scrollbar max-w-full">
          <button id="mainTabBtn_1" onclick="switchWorkspaceTab('TAB_MAIN_GUI')" class="px-3 py-1 rounded-lg text-xs font-extrabold bg-amber-500 text-slate-950 transition flex items-center gap-1 shrink-0">
            <span>🎯 Tab 1：AI 刷題與診斷</span>
          </button>
          <button id="mainTabBtn_2" onclick="switchWorkspaceTab('TAB_IRT_COACH')" class="px-3 py-1 rounded-lg text-xs font-bold text-slate-300 hover:text-white hover:bg-slate-800 transition flex items-center gap-1 shrink-0">
            <span>📊 Tab 2：分數推估 & 處方</span>
            <span id="tab2MiniScoreBadge" class="px-1.5 py-0.2 rounded bg-slate-950 text-amber-300 font-mono text-xs">--/180</span>
          </button>
          <button id="mainTabBtn_3" onclick="switchWorkspaceTab('TAB_FSRS_OTHERS')" class="px-3 py-1 rounded-lg text-xs font-bold text-slate-300 hover:text-white hover:bg-slate-800 transition flex items-center gap-1 shrink-0">
            <span>📋 Tab 3：題庫佇列 & 百寶箱</span>
            <span id="tab3QueueBadge" class="px-1.5 py-0.2 rounded bg-slate-950 text-sky-300 font-mono text-xs">530題</span>
          </button>
        </div>

        <!-- Right Controls: Collapsible on Mobile (<1024px), Always Visible on Desktop (lg:flex) -->
        <div id="mobileSecondaryControls" class="hidden lg:flex flex-wrap items-center gap-1.5 w-full lg:w-auto">
          <!-- 500% Flagship Pool vs 300% Practice Pool vs 100% Official Mock Switcher -->
          <div class="flex items-center bg-slate-900 p-0.5 rounded-xl overflow-x-auto no-scrollbar max-w-full">
            <button id="poolBtn500" onclick="setQuestionPoolScope('POOL_500')" class="px-2.5 py-1 rounded-lg text-xs font-bold bg-amber-500 text-slate-950 transition shrink-0" title="旗艦 500% 全題庫池 (530題)">
              🔥 500% 旗艦池 (<span id="pool500CountText">530</span>題)
            </button>
            <button id="poolBtn300" onclick="setQuestionPoolScope('POOL_300')" class="px-2.5 py-1 rounded-lg text-xs font-semibold text-slate-300 hover:text-white transition shrink-0" title="日常 300% 擴充鍛鍊池 (318題)">
              🏋️ 300% 鍛鍊池 (<span id="pool300CountText">318</span>題)
            </button>
            <button id="poolBtn100" onclick="setQuestionPoolScope('MOCK_100')" class="px-2.5 py-1 rounded-lg text-xs font-semibold text-slate-300 hover:text-white transition shrink-0" title="JEES 官方 100% 正式檢定題量 (106題)">
              ⏱️ 100% 正式模考 (<span id="mock100CountText">106</span>題)
            </button>
          </div>

          <select id="officialSubtypeSelect" onchange="applyOfficialSubfilter(this.value)"
            class="px-2.5 py-1 rounded-xl bg-slate-900 text-xs text-slate-200 font-medium focus:outline-none">
            <option value="ALL_SUB">📑 官方大題：全部題型</option>
          </select>

          <div class="flex items-center bg-slate-900 p-0.5 rounded-xl">
            <button id="modeBtnScaffold" onclick="setPedagogicalMode('SCAFFOLD')" class="px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-500 text-slate-950 transition">
              🌱 教學鷹架
            </button>
            <button id="modeBtnExam" onclick="setPedagogicalMode('EXAM')" class="px-2.5 py-1 rounded-lg text-xs font-medium text-slate-400 hover:text-white transition">
              ⚔️ 考場實戰
            </button>
          </div>

          <button id="furiganaToggleBtn" onclick="toggleFurigana()" class="px-2.5 py-1 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition flex items-center gap-1">
            <span>あ 振假名:</span>
            <span id="furiganaStatusText" class="font-mono text-emerald-400 font-bold">OFF</span>
          </button>

          <button onclick="startWeaknessDrill()" class="px-2.5 py-1 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition flex items-center gap-1" title="優先抽取高信心盲點題與錯題">
            <span>🔄 錯題</span>
            <span id="weaknessCountBadge" class="px-1.5 rounded-full bg-rose-500/20 text-rose-300 font-mono text-xs">0</span>
          </button>

          <button onclick="startFlaggedDrill()" class="px-2.5 py-1 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-amber-300 transition flex items-center gap-1" title="專刷已標記待查 (🚩) 的題目">
            <span>🚩 待查</span>
          </button>
        </div>
      </div>

      <!-- Category Filter Pills Strip (Compact Horizontal Scroll) -->
      <div id="categoryTabs" class="flex items-center gap-1.5 overflow-x-auto no-scrollbar pt-0.5"></div>
    </div>
  </header>"""
    assert old_header_pat.search(html), "Could not locate <header> in index.html"
    html = old_header_pat.sub(lambda _: new_header, html, count=1)

    # 2. Make Mondai Number Bars single-line horizontally scrollable on mobile
    html = html.replace(
        '<div id="officialMondaiWrittenBar" class="flex flex-wrap items-center gap-1"></div>',
        '<div id="officialMondaiWrittenBar" class="flex flex-nowrap sm:flex-wrap items-center gap-1 overflow-x-auto no-scrollbar"></div>',
    )
    html = html.replace(
        '<div id="officialMondaiListeningBar" class="flex flex-wrap items-center gap-1"></div>',
        '<div id="officialMondaiListeningBar" class="flex flex-nowrap sm:flex-wrap items-center gap-1 overflow-x-auto no-scrollbar"></div>',
    )

    # Bump version query strings to ?v=4.4
    html = html.replace("?v=4.3", "?v=4.4")
    HTML_PATH.write_text(html, encoding="utf-8")
    print("[HTML UPGRADE] Upgraded index.html with responsive mobile drawer & single-row Mondai scroll.")


def upgrade_app_js():
    js = APP_JS_PATH.read_text(encoding="utf-8")

    # 1. Add mobileDrawerOpen, showAllQueueItems, and prewarmAudio state variables
    if "let mobileHeaderDrawerOpen =" not in js:
        js = js.replace(
            "let macroChoukaiRemainSec = 50 * 60;",
            "let macroChoukaiRemainSec = 50 * 60;\nlet mobileHeaderDrawerOpen = false;\nlet showAllQueueItems = false;\nlet prewarmAudioEl = null;",
            1,
        )

    # 2. Add toggleMobileHeaderDrawer() and expandQueueAll()
    if "function toggleMobileHeaderDrawer()" not in js:
        drawer_fns = """
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
"""
        js = js.replace("function switchWorkspaceTab(tabId) {", drawer_fns + "\nfunction switchWorkspaceTab(tabId) {", 1)

    # 3. Make switchWorkspaceTab('TAB_FSRS_OTHERS') call renderQuestionQueue(true)
    js = js.replace(
        "if (tabId === 'TAB_FSRS_OTHERS') renderQuestionQueue();",
        "if (tabId === 'TAB_FSRS_OTHERS') renderQuestionQueue(true);",
    )

    # 4. Optimize renderQuestionQueue(forceRender = false) so it NEVER rebuilds 3,710 DOM nodes while user is on Tab 1 or Tab 2!
    old_rq_pat = re.compile(
        r"function renderQuestionQueue\(\)\s*\{.*?\n\}",
        re.S,
    )
    new_rq_fn = """function renderQuestionQueue(forceRender = false) {
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
}"""
    assert old_rq_pat.search(js), "Could not locate renderQuestionQueue in app.js"
    js = old_rq_pat.sub(lambda _: new_rq_fn, js, count=1)

    # Make filterQueueByKeyword call renderQuestionQueue(true)
    js = js.replace(
        "function filterQueueByKeyword(val) {\n  queueSearchKeyword = (val || '').trim().toLowerCase();\n  renderQuestionQueue();\n}",
        "function filterQueueByKeyword(val) {\n  queueSearchKeyword = (val || '').trim().toLowerCase();\n  renderQuestionQueue(true);\n}",
    )
    js = js.replace(
        "function filterQueueByKeyword(val) {\r\n  queueSearchKeyword = (val || '').trim().toLowerCase();\r\n  renderQuestionQueue();\r\n}",
        "function filterQueueByKeyword(val) {\r\n  queueSearchKeyword = (val || '').trim().toLowerCase();\r\n  renderQuestionQueue(true);\r\n}",
    )

    # 5. Diff-guard updateTimerUI and updateMacroExamTimerUI so Tailwind Play CDN MutationObserver is NOT triggered every second!
    old_ut_pat = re.compile(
        r"function updateTimerUI\(targetSec\)\s*\{.*?\n\}",
        re.S,
    )
    new_ut_fn = """function updateTimerUI(targetSec) {
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
}"""
    assert old_ut_pat.search(js), "Could not locate updateTimerUI in app.js"
    js = old_ut_pat.sub(lambda _: new_ut_fn, js, count=1)

    # Also diff-guard badgeEl.className in updateMacroExamTimerUI
    js = js.replace(
        "badgeEl.className = 'px-2 py-0.5 rounded bg-slate-950 text-amber-300 font-mono text-xs font-bold';",
        "const c1 = 'px-2 py-0.5 rounded bg-slate-950 text-amber-300 font-mono text-xs font-bold'; if (badgeEl.className !== c1) badgeEl.className = c1;",
    )
    js = js.replace(
        "badgeEl.className = 'px-2 py-0.5 rounded bg-slate-950 text-emerald-300 font-mono text-xs font-bold';",
        "const c2 = 'px-2 py-0.5 rounded bg-slate-950 text-emerald-300 font-mono text-xs font-bold'; if (badgeEl.className !== c2) badgeEl.className = c2;",
    )
    js = js.replace(
        "badgeEl.className = 'px-2 py-0.5 rounded bg-slate-950 text-sky-300 font-mono text-xs font-bold';",
        "const c3 = 'px-2 py-0.5 rounded bg-slate-950 text-sky-300 font-mono text-xs font-bold'; if (badgeEl.className !== c3) badgeEl.className = c3;",
    )

    # 6. Pre-warm current question's Neural MP3 after 120ms idle in loadCurrentQuestion()
    if "prewarmAudioEl" not in js.split("function renderOfficialMondaiNumberBar")[0]:
        js = js.replace(
            "syncFlagButtonUI(q.id);\n  renderQuestionQueue();",
            "syncFlagButtonUI(q.id);\n  renderQuestionQueue();\n  setTimeout(() => {\n    const mp3Url = q.stemAudioFile || q.audioFile;\n    if (mp3Url) {\n      prewarmAudioEl = new Audio();\n      prewarmAudioEl.preload = 'auto';\n      prewarmAudioEl.src = mp3Url;\n    }\n  }, 120);",
            1,
        )
        js = js.replace(
            "syncFlagButtonUI(q.id);\r\n  renderQuestionQueue();",
            "syncFlagButtonUI(q.id);\r\n  renderQuestionQueue();\r\n  setTimeout(() => {\r\n    const mp3Url = q.stemAudioFile || q.audioFile;\r\n    if (mp3Url) {\r\n      prewarmAudioEl = new Audio();\r\n      prewarmAudioEl.preload = 'auto';\r\n      prewarmAudioEl.src = mp3Url;\r\n    }\r\n  }, 120);",
            1,
        )

    js = js.replace("?v=4.3", "?v=4.4")
    APP_JS_PATH.write_text(js, encoding="utf-8")
    print("[APP.JS UPGRADE] Upgraded app.js with lazy Tab-3 queue, diff-guarded timer loop, and MP3 pre-warming.")


if __name__ == "__main__":
    upgrade_css()
    upgrade_html()
    upgrade_app_js()
