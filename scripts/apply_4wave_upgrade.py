#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_4wave_upgrade.py
Applies Wave 2, Wave 3, and Wave 4 of the JLPT N2 Exam Mastery Upgrade
to index.html and assets/js/app.js while strictly preserving 0 Impeccable findings.
"""

from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent.parent
HTML_PATH = BASE_DIR / "index.html"
APP_JS_PATH = BASE_DIR / "assets" / "js" / "app.js"


def upgrade_index_html():
    html = HTML_PATH.read_text(encoding="utf-8")

    # 1. Wave 3: Add #macroTimerToggleBtn, #macroTimerClockText, #macroPacingBadge to #officialMondaiBanner
    if 'id="macroTimerToggleBtn"' not in html:
        old_pattern = re.compile(
            r'<span id="qProgressText"[^>]*>.*?</span>\s*<button type="button" id="flagQuestionBtn".*?</button>\s*<div class="flex items-center gap-1\.5[^>]*>\s*<span id="timerDot"[^>]*></span>\s*<span id="timerText"[^>]*>.*?</span>\s*</div>',
            re.S,
        )
        replacement = """<span id="qProgressText" class="font-mono text-xs bg-slate-950 text-amber-300 px-2 py-0.5 rounded" style="font-variant-numeric: tabular-nums;">題號 #1 / 318</span>
              <button type="button" id="flagQuestionBtn" onclick="toggleFlagQuestion()"
                class="px-2 py-0.5 rounded bg-slate-950 hover:bg-slate-900 text-amber-200 text-xs font-semibold transition">
                🏳️ 標記待查
              </button>
              <button type="button" id="macroTimerToggleBtn" onclick="toggleN2MacroExamTimer()"
                class="px-2 py-0.5 rounded bg-slate-950 hover:bg-slate-900 text-sky-300 font-mono text-xs font-bold transition"
                style="font-variant-numeric: tabular-nums;"
                title="點擊切換/重置 N2 正式模擬考二節制倒數計時器 (105:00 言語・読解 / 50:00 聴解)">
                ⏱️ N2 正式模擬考倒數 (<span id="macroTimerClockText">105:00 言語・読解 / 50:00 聴解</span>)
              </button>
              <span id="macroPacingBadge" class="px-2 py-0.5 rounded bg-slate-950 text-emerald-300 font-mono text-xs font-bold" style="font-variant-numeric: tabular-nums;">
                配速正常
              </span>
              <div class="flex items-center gap-1.5 px-2.5 py-0.5 rounded bg-slate-950 text-white">
                <span id="timerDot" class="w-2 h-2 rounded-full bg-emerald-400"></span>
                <span id="timerText" class="font-mono text-xs font-bold text-emerald-400" style="font-variant-numeric: tabular-nums;">00s / 30s</span>
              </div>"""
        assert old_pattern.search(html), "Could not locate #officialMondaiBanner right controls in index.html"
        html = old_pattern.sub(lambda _: replacement, html, count=1)

    # 2. Wave 2 & 4: Add #starInteractiveWidget, #starDirectSubmitBox, #starFullSentenceBox and update #blindOptionsNotice button text
    if 'id="starInteractiveWidget"' not in html:
        star_pat = re.compile(
            r'<div id="starSlotsContainer" class="grid grid-cols-2 sm:grid-cols-4 gap-2"></div>\s*<div id="starTokensBar" class="flex flex-wrap gap-1\.5 pt-1"></div>',
            re.S,
        )
        star_rep = """<div id="starInteractiveWidget" class="space-y-2">
              <div id="starSlotsContainer" class="grid grid-cols-2 sm:grid-cols-4 gap-2"></div>
              <div id="starTokensBar" class="flex flex-wrap gap-1.5 pt-1"></div>
              <div id="starDirectSubmitBox" class="hidden pt-1"></div>
              <div id="starFullSentenceBox" class="hidden pt-2 border-t border-slate-800"></div>
            </div>"""
        assert star_pat.search(html), "Could not locate #starSlotsContainer in index.html"
        html = star_pat.sub(lambda _: star_rep, html, count=1)

    html = html.replace("顯示選項文字", "👁️ 顯示文字稿")
    HTML_PATH.write_text(html, encoding="utf-8")
    print("[HTML UPGRADE] Updated index.html with Wave 2, 3, 4 elements.")


def upgrade_app_js():
    js = APP_JS_PATH.read_text(encoding="utf-8")

    # 1. Add Macro Exam Timer state variables near starSlots
    if "let macroExamTimerActive =" not in js:
        js = js.replace(
            "let starSlots = [null, null, null, null];",
            "let starSlots = [null, null, null, null];\nlet macroExamTimerActive = false;\nlet macroWrittenRemainSec = 105 * 60;\nlet macroChoukaiRemainSec = 50 * 60;",
            1,
        )

    # 2. Auto-enable Macro Exam Timer in setQuestionPoolScope when scope === 'MOCK_100'
    if "if (scope === 'MOCK_100' && !macroExamTimerActive)" not in js:
        js = js.replace(
            "function setQuestionPoolScope(scope) {\n  currentPoolScope = scope;",
            "function setQuestionPoolScope(scope) {\n  currentPoolScope = scope;\n  if (scope === 'MOCK_100' && !macroExamTimerActive) {\n    macroExamTimerActive = true;\n    macroWrittenRemainSec = 105 * 60;\n    macroChoukaiRemainSec = 50 * 60;\n  }\n  updateMacroExamTimerUI(getCurrentQuestion());",
            1,
        )
        # Also handle CRLF version if needed
        js = js.replace(
            "function setQuestionPoolScope(scope) {\r\n  currentPoolScope = scope;",
            "function setQuestionPoolScope(scope) {\r\n  currentPoolScope = scope;\r\n  if (scope === 'MOCK_100' && !macroExamTimerActive) {\r\n    macroExamTimerActive = true;\r\n    macroWrittenRemainSec = 105 * 60;\r\n    macroChoukaiRemainSec = 50 * 60;\r\n  }\r\n  updateMacroExamTimerUI(getCurrentQuestion());",
            1,
        )

    # 3. Wave 4: Upgrade renderOptionCards & selectOption for L5_QUICK_RESP Audio-First Masking & Bidirectional Star Sync
    old_render_opt = re.compile(
        r"function renderOptionCards\(q\)\s*\{.*?\n\}\s*\n+function selectOption\(idx\)\s*\{.*?\n\}",
        re.S,
    )
    new_render_opt = """function renderOptionCards(q) {
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
}"""
    assert old_render_opt.search(js), "Could not locate renderOptionCards/selectOption in app.js"
    js = old_render_opt.sub(lambda _: new_render_opt, js, count=1)

    # 4. Wave 2: Upgrade renderStarReconstructor (and add renderStarInteractiveWidget + submitFromStarSlot + full 4-token sentence synthesis)
    old_star_block = re.compile(
        r"function renderStarReconstructor\(q\)\s*\{.*?\n\}\s*\n+function placeStarToken\(optIdx\)\s*\{.*?\n\}",
        re.S,
    )
    new_star_block = """function buildSynthesizedStarSentenceHtml(q) {
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
}"""
    assert old_star_block.search(js), "Could not locate renderStarReconstructor/placeStarToken in app.js"
    js = old_star_block.sub(lambda _: new_star_block, js, count=1)

    # 5. Wave 3: Upgrade startPacingTimer & add toggleN2MacroExamTimer / updateMacroExamTimerUI
    old_timer_block = re.compile(
        r"function startPacingTimer\(targetSec\)\s*\{.*?\n\}\s*\n+function updateTimerUI\(targetSec\)\s*\{.*?\n\}",
        re.S,
    )
    new_timer_block = """function formatMmSs(totalSec) {
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
    badgeEl.className = 'px-2 py-0.5 rounded bg-slate-950 text-amber-300 font-mono text-xs font-bold';
  } else if (isAhead) {
    badgeEl.textContent = '領先配速';
    badgeEl.className = 'px-2 py-0.5 rounded bg-slate-950 text-emerald-300 font-mono text-xs font-bold';
  } else {
    badgeEl.textContent = '配速正常';
    badgeEl.className = 'px-2 py-0.5 rounded bg-slate-950 text-sky-300 font-mono text-xs font-bold';
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

  if (elapsedSeconds <= targetSec * 0.75) {
    timerText.className = 'font-mono text-xs font-bold text-emerald-400';
    timerDot.className = 'w-2 h-2 rounded-full bg-emerald-400';
    progressBar.className = 'bg-emerald-500 h-full transition-all duration-300';
  } else if (elapsedSeconds <= targetSec) {
    timerText.className = 'font-mono text-xs font-bold text-amber-400';
    timerDot.className = 'w-2 h-2 rounded-full bg-amber-400';
    progressBar.className = 'bg-amber-500 h-full transition-all duration-300';
  } else {
    timerText.className = 'font-mono text-xs font-bold text-rose-400';
    timerDot.className = 'w-2 h-2 rounded-full bg-rose-500';
    progressBar.className = 'bg-rose-500 h-full transition-all duration-300';
  }
}"""
    assert old_timer_block.search(js), "Could not locate startPacingTimer/updateTimerUI in app.js"
    js = old_timer_block.sub(lambda _: new_timer_block, js, count=1)

    # 6. Ensure submitCurrentAnswer calls renderStarReconstructor(q) when q.category === 'STAR'
    if "if (q.category === 'STAR') renderStarReconstructor(q);" not in js:
        js = js.replace(
            "renderOptionCards(q);\n  updateFuriganaHintVisibility(q);",
            "if (q.category === 'STAR') renderStarReconstructor(q);\n  renderOptionCards(q);\n  updateFuriganaHintVisibility(q);",
            1,
        )
        js = js.replace(
            "renderOptionCards(q);\r\n  updateFuriganaHintVisibility(q);",
            "if (q.category === 'STAR') renderStarReconstructor(q);\r\n  renderOptionCards(q);\r\n  updateFuriganaHintVisibility(q);",
            1,
        )

    APP_JS_PATH.write_text(js, encoding="utf-8")
    print("[APP.JS UPGRADE] Updated assets/js/app.js with Wave 2, 3, 4 logic.")


if __name__ == "__main__":
    upgrade_index_html()
    upgrade_app_js()
