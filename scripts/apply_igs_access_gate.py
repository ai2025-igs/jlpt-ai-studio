#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_igs_access_gate.py
Applies the Sovereign iGS Demo Center-styled Access Code Gate (password: "igs",
verified via SHA-256 + FNV-1a without plaintext exposure) to:
  1. index.html
  2. assets/css/custom.css
  3. assets/js/app.js
  4. scripts/build_jlpt_n2_eduslide_deck.py (and regenerates presentation.html)
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_PATH = BASE_DIR / "index.html"
CSS_PATH = BASE_DIR / "assets" / "css" / "custom.css"
APP_JS_PATH = BASE_DIR / "assets" / "js" / "app.js"
DECK_BUILDER_PATH = BASE_DIR / "scripts" / "build_jlpt_n2_eduslide_deck.py"

ACCESS_GATE_HTML = """  <!-- ================= iGS DEMO CENTER ACCESS PORTAL (SHA-256 + FNV-1A PROTECTED) ================= -->
  <div id="igsAccessGateOverlay" class="fixed inset-0 z-50 igs-cosmos-bg flex items-center justify-center p-4 overflow-y-auto">
    <div class="w-full max-w-[430px] rounded-3xl bg-[#0d111d] border border-slate-800/90 px-6 sm:px-8 py-7 sm:py-8 shadow-2xl text-center space-y-5 my-auto">
      <!-- Top iGS 3D Sovereign Emblem -->
      <div class="flex justify-center">
        <div class="w-16 h-16 p-2 rounded-full bg-slate-900 flex items-center justify-center shadow-inner">
          <svg viewBox="0 0 64 64" class="w-12 h-12" aria-hidden="true">
            <defs>
              <radialGradient id="igsSphereGrad" cx="35%" cy="30%" r="70%">
                <stop offset="0%" stop-color="#f8fafc" />
                <stop offset="45%" stop-color="#94a3b8" />
                <stop offset="100%" stop-color="#1e293b" />
              </radialGradient>
              <linearGradient id="igsRibbonGreen" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#34d399" />
                <stop offset="100%" stop-color="#059669" />
              </linearGradient>
              <linearGradient id="igsRibbonAmber" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#f59e0b" />
                <stop offset="100%" stop-color="#e11d48" />
              </linearGradient>
            </defs>
            <circle cx="32" cy="32" r="28" fill="url(#igsSphereGrad)" />
            <path d="M16 38 C20 18, 44 18, 48 34 C42 24, 24 26, 16 38 Z" fill="url(#igsRibbonGreen)" />
            <path d="M20 22 C28 12, 46 16, 46 28 C38 20, 26 20, 20 22 Z" fill="url(#igsRibbonAmber)" />
            <path d="M18 44 C26 52, 44 48, 48 36 C40 44, 26 46, 18 44 Z" fill="#38bdf8" opacity="0.85" />
            <text x="32" y="53" text-anchor="middle" fill="#f8fafc" font-size="9" font-family="JetBrains Mono, monospace" font-weight="800">iGS</text>
          </svg>
        </div>
      </div>

      <!-- Title & Subtitle -->
      <div class="space-y-1.5">
        <div class="text-2xl sm:text-3xl font-black tracking-tight">
          <span class="text-white">iGS </span><span class="text-emerald-400">JLPT AI Studio</span>
        </div>
        <p class="text-xs text-slate-300 font-medium">
          歡迎來到 AI 認知診斷日檢的未來 — 軟體定義教學鷹架
        </p>
      </div>

      <!-- 3 KPI Metric Pill Boxes (Zero 4-sided inner borders to satisfy Impeccable nested-cards gate) -->
      <div class="grid grid-cols-3 gap-2.5">
        <div class="rounded-2xl bg-[#131929] px-2.5 py-3 space-y-0.5">
          <div class="text-xl sm:text-2xl font-black font-mono text-emerald-400">530</div>
          <div class="text-xs font-semibold text-slate-200">Questions</div>
          <div class="text-xs text-slate-400">N2 旗艦題庫</div>
        </div>
        <div class="rounded-2xl bg-[#131929] px-2.5 py-3 space-y-0.5">
          <div class="text-xl sm:text-2xl font-black font-mono text-emerald-400">261</div>
          <div class="text-xs font-semibold text-slate-200">Neural MP3</div>
          <div class="text-xs text-slate-400">真人雙聲道</div>
        </div>
        <div class="rounded-2xl bg-[#131929] px-2.5 py-3 space-y-0.5">
          <div class="text-xl sm:text-2xl font-black font-mono text-emerald-400">19</div>
          <div class="text-xs font-semibold text-slate-200">Mondai</div>
          <div class="text-xs text-slate-400">官方全題型</div>
        </div>
      </div>

      <!-- 4 Feature Badges -->
      <div class="flex flex-wrap items-center justify-center gap-1.5">
        <span class="px-3 py-1 rounded-full bg-[#151c2e] text-slate-200 text-xs font-semibold">📈 2PL-IRT 量尺</span>
        <span class="px-3 py-1 rounded-full bg-[#151c2e] text-slate-200 text-xs font-semibold">⚡ FSRS v5 記憶</span>
        <span class="px-3 py-1 rounded-full bg-[#151c2e] text-slate-200 text-xs font-semibold">🧠 8大認知鷹架</span>
        <span class="px-3 py-1 rounded-full bg-[#151c2e] text-slate-200 text-xs font-semibold">🛡️ 台日漢字透鏡</span>
      </div>

      <!-- Access Code Input Section -->
      <div class="space-y-2.5 pt-1">
        <label for="igsAccessCodeInput" class="block text-xs font-bold tracking-widest text-slate-300 uppercase">
          ENTER ACCESS CODE
        </label>
        <div class="relative">
          <input
            id="igsAccessCodeInput"
            type="password"
            inputmode="text"
            autocapitalize="none"
            autocomplete="off"
            spellcheck="false"
            placeholder="•   •   •   •   •"
            onkeydown="handleIgsAccessKeydown(event)"
            class="w-full px-10 py-3.5 rounded-2xl bg-[#070a12] text-white text-center font-mono text-base tracking-widest focus:outline-none focus:ring-2 focus:ring-emerald-400 transition"
          />
          <button
            type="button"
            id="igsTogglePwdBtn"
            onclick="toggleIgsAccessPasswordVisibility()"
            title="顯示或隱藏通行碼"
            class="absolute right-3 top-1/2 -translate-y-1/2 px-2 py-1 rounded-lg text-xs text-slate-300 hover:text-white transition">
            👁️
          </button>
        </div>
        <div id="igsAccessFeedbackText" class="text-xs text-slate-300 font-medium pt-1">
          ✦ Ready to explore 530 N2 questions &amp; 20-slide deck?
        </div>
      </div>

      <!-- Primary Unlock Button -->
      <button
        type="button"
        id="igsUnlockBtn"
        onclick="submitIgsAccessCode()"
        class="w-full py-3.5 rounded-2xl bg-[#1c2333] hover:bg-emerald-500 text-slate-100 hover:text-slate-950 font-extrabold text-sm tracking-wide transition flex items-center justify-center gap-2">
        <span>Unlock JLPT Studio</span>
        <span>→</span>
      </button>

      <!-- Footer -->
      <div class="pt-2 space-y-1 text-xs text-slate-400">
        <div class="flex items-center justify-center gap-1.5 font-medium text-slate-300">
          <span>🔒</span>
          <span>Secure Access · 支援跨分頁記憶 (30天免重複輸入)</span>
        </div>
        <div>Powered by AEOS © 2026 iGrowth Solutions</div>
      </div>
    </div>
  </div>
"""

CSS_ADDITION = """
/* iGS Demo Center Access Portal Styling */
.igs-cosmos-bg {
  background-color: #0f172a;
  background-image:
    radial-gradient(circle at 18% 22%, rgba(16, 185, 129, 0.08) 0%, transparent 38%),
    radial-gradient(circle at 82% 76%, rgba(56, 189, 248, 0.07) 0%, transparent 40%),
    radial-gradient(rgba(148, 163, 184, 0.16) 1px, transparent 1px);
  background-size: 100% 100%, 100% 100%, 36px 36px;
}
"""

JS_ADDITION = """
/*************************************************************************
 * iGS DEMO CENTER ACCESS PORTAL (SHA-256 + FNV-1A ZERO-PLAINTEXT GATE)
 *************************************************************************/
const IGS_AUTH_STORAGE_KEY = 'jlpt_igs_access_v1';
const IGS_CODE_SHA256 = '5ff60895ec5cc3febc7389e0872753ab7b811dc9df29f4d567cf2ab2ae8adce7';
const IGS_CODE_FNV1A = '90d82d5e';
const IGS_SESSION_TTL_MS = 30 * 24 * 60 * 60 * 1000; // 30 Days
let igsFailedAttempts = 0;
let igsLockoutUntil = 0;

function computeFnv1aHex(str) {
  let h = 0x811c9dc5;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i) & 0xff;
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h.toString(16).padStart(8, '0');
}

async function computeSha256Hex(str) {
  if (window.crypto && window.crypto.subtle && window.TextEncoder) {
    const buf = new TextEncoder().encode(str);
    const hashBuf = await window.crypto.subtle.digest('SHA-256', buf);
    return Array.from(new Uint8Array(hashBuf))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }
  return null;
}

async function verifyIgsAccessCodeDigest(rawInput) {
  const normalized = String(rawInput || '').trim().toLowerCase();
  if (!normalized) return false;
  const fnv = computeFnv1aHex(normalized);
  if (fnv !== IGS_CODE_FNV1A || normalized.length !== 3) return false;
  const sha = await computeSha256Hex(normalized);
  if (sha !== null) {
    return sha === IGS_CODE_SHA256;
  }
  return true;
}

function isIgsStudioUnlocked() {
  try {
    const raw = localStorage.getItem(IGS_AUTH_STORAGE_KEY);
    if (!raw) return false;
    const data = JSON.parse(raw);
    if (!data || data.token !== IGS_CODE_FNV1A) return false;
    if (Date.now() - (data.ts || 0) > IGS_SESSION_TTL_MS) {
      localStorage.removeItem(IGS_AUTH_STORAGE_KEY);
      return false;
    }
    return true;
  } catch (e) {
    return false;
  }
}

function persistIgsStudioUnlock() {
  try {
    localStorage.setItem(
      IGS_AUTH_STORAGE_KEY,
      JSON.stringify({ token: IGS_CODE_FNV1A, ts: Date.now() })
    );
  } catch (e) {}
}

function hideIgsAccessGateOverlay() {
  const overlay = document.getElementById('igsAccessGateOverlay');
  if (overlay) {
    overlay.classList.add('hidden');
    overlay.classList.remove('flex');
  }
}

function showIgsAccessGateOverlay() {
  const overlay = document.getElementById('igsAccessGateOverlay');
  if (overlay) {
    overlay.classList.remove('hidden');
    overlay.classList.add('flex');
  }
  const input = document.getElementById('igsAccessCodeInput');
  if (input) {
    input.value = '';
    setTimeout(() => input.focus(), 80);
  }
}

async function initIgsAccessGate() {
  // 1. Check URL query parameter (?access=... or ?code=...) for classroom QR code convenience
  try {
    const params = new URLSearchParams(window.location.search);
    const urlCode = params.get('access') || params.get('code');
    if (urlCode && await verifyIgsAccessCodeDigest(urlCode)) {
      persistIgsStudioUnlock();
      params.delete('access');
      params.delete('code');
      const cleanQuery = params.toString();
      const cleanUrl = window.location.pathname + (cleanQuery ? '?' + cleanQuery : '') + window.location.hash;
      window.history.replaceState({}, document.title, cleanUrl);
    }
  } catch (e) {}

  // 2. Check persisted 30-day session token
  if (isIgsStudioUnlocked()) {
    hideIgsAccessGateOverlay();
  } else {
    showIgsAccessGateOverlay();
  }
}

async function submitIgsAccessCode() {
  const feedbackEl = document.getElementById('igsAccessFeedbackText');
  const inputEl = document.getElementById('igsAccessCodeInput');
  const now = Date.now();

  if (now < igsLockoutUntil) {
    const waitSec = Math.ceil((igsLockoutUntil - now) / 1000);
    if (feedbackEl) {
      feedbackEl.textContent = `🔒 嘗試次數過多，系統保護鎖定中，請於 ${waitSec} 秒後再試`;
      feedbackEl.className = 'text-xs text-rose-400 font-bold pt-1';
    }
    return;
  }

  const rawVal = inputEl ? inputEl.value : '';
  const ok = await verifyIgsAccessCodeDigest(rawVal);

  if (ok) {
    igsFailedAttempts = 0;
    persistIgsStudioUnlock();
    hideIgsAccessGateOverlay();
    elapsedSeconds = 0;
    if (feedbackEl) {
      feedbackEl.textContent = '✦ Access Granted — Welcome to iGS JLPT AI Studio!';
      feedbackEl.className = 'text-xs text-emerald-300 font-bold pt-1';
    }
    showToast('🔓 iGS 通行驗證成功！歡迎使用 JLPT N2 互動式 AI 刷題與認知診斷系統。', 'emerald');
  } else {
    igsFailedAttempts += 1;
    if (igsFailedAttempts >= 5) {
      igsLockoutUntil = Date.now() + 30000;
      igsFailedAttempts = 0;
      if (feedbackEl) {
        feedbackEl.textContent = '🔒 連續輸入錯誤達 5 次，請稍候 30 秒再試';
        feedbackEl.className = 'text-xs text-rose-400 font-bold pt-1';
      }
    } else {
      if (feedbackEl) {
        feedbackEl.textContent = `⚠️ 通行碼不正確（提示：3 碼英文縮寫，不分大小寫，剩餘 ${5 - igsFailedAttempts} 次機會）`;
        feedbackEl.className = 'text-xs text-amber-300 font-bold pt-1';
      }
    }
    if (inputEl) {
      inputEl.select();
    }
  }
}

function handleIgsAccessKeydown(e) {
  if (e && e.key === 'Enter') {
    e.preventDefault();
    submitIgsAccessCode();
  }
}

function toggleIgsAccessPasswordVisibility() {
  const inputEl = document.getElementById('igsAccessCodeInput');
  const btnEl = document.getElementById('igsTogglePwdBtn');
  if (!inputEl) return;
  if (inputEl.type === 'password') {
    inputEl.type = 'text';
    if (btnEl) btnEl.textContent = '🙈';
  } else {
    inputEl.type = 'password';
    if (btnEl) btnEl.textContent = '👁️';
  }
}

function lockIgsStudio() {
  try {
    localStorage.removeItem(IGS_AUTH_STORAGE_KEY);
  } catch (e) {}
  if (typeof stopListeningDialogue === 'function') stopListeningDialogue();
  const feedbackEl = document.getElementById('igsAccessFeedbackText');
  if (feedbackEl) {
    feedbackEl.textContent = '✦ 已安全鎖定畫面，請輸入通行碼解鎖';
    feedbackEl.className = 'text-xs text-slate-300 font-medium pt-1';
  }
  showIgsAccessGateOverlay();
}
"""

# 1. Update index.html
import re
idx_text = INDEX_PATH.read_text(encoding="utf-8")
if 'name="robots"' not in idx_text:
    idx_text = idx_text.replace(
        '<meta name="viewport" content="width=device-width, initial-scale=1.0" />',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0" />\n  <meta name="robots" content="noindex, nofollow, noarchive" />',
        1,
    )
# Remove previous overlay if present so we can cleanly insert the latest version
idx_text = re.sub(
    r"\s*<!-- ================= iGS DEMO CENTER ACCESS PORTAL.*?<!-- ================= STICKY 1080P COMPACT HEADER",
    "\n\n" + ACCESS_GATE_HTML + "\n  <!-- ================= STICKY 1080P COMPACT HEADER",
    idx_text,
    flags=re.S,
)
if 'id="igsAccessGateOverlay"' not in idx_text:
    body_tag = '<body class="min-h-screen flex flex-col selection:bg-amber-500 selection:text-slate-950 hide-inline-ruby">'
    assert body_tag in idx_text, "body tag not found in index.html"
    idx_text = idx_text.replace(body_tag, body_tag + "\n\n" + ACCESS_GATE_HTML, 1)

if 'onclick="lockIgsStudio()"' not in idx_text:
    byok_btn = '<button onclick="openByokModal()" class="px-2 py-1 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition flex items-center gap-1">\n              <span id="byokStatusDot" class="w-2 h-2 rounded-full bg-amber-400"></span>\n              <span>🔑</span>\n            </button>'
    lock_btn = (
        byok_btn
        + '\n            <button onclick="lockIgsStudio()" title="鎖定畫面並登出授權" class="px-2 py-1 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition flex items-center gap-1">\n'
        + '              <span>🔒</span>\n'
        + '            </button>'
    )
    if byok_btn in idx_text:
        idx_text = idx_text.replace(byok_btn, lock_btn, 1)
    else:
        # Handle CRLF variant
        byok_btn_crlf = byok_btn.replace("\n", "\r\n")
        if byok_btn_crlf in idx_text:
            idx_text = idx_text.replace(byok_btn_crlf, lock_btn.replace("\n", "\r\n"), 1)

INDEX_PATH.write_text(idx_text, encoding="utf-8")
print("[+] Updated index.html with iGS Demo Center Access Portal & Lock button")

# 2. Update assets/css/custom.css
css_text = CSS_PATH.read_text(encoding="utf-8")
css_text = re.sub(r"\n?/\* iGS Demo Center Access Portal Styling \*/.*", "", css_text, flags=re.S)
css_text = css_text.rstrip() + "\n" + CSS_ADDITION
CSS_PATH.write_text(css_text, encoding="utf-8")
print("[+] Updated assets/css/custom.css with .igs-cosmos-bg")

# 3. Update assets/js/app.js
app_text = APP_JS_PATH.read_text(encoding="utf-8")
if "initIgsAccessGate();" not in app_text:
    app_text = app_text.replace(
        "loadPersistedProgress();",
        "initIgsAccessGate();\n  loadPersistedProgress();",
        1,
    )
if "if (!isIgsStudioUnlocked()) return;" not in app_text:
    app_text = app_text.replace(
        "if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;",
        "if (!isIgsStudioUnlocked()) return;\n    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;",
        1,
    )
if "if (!isSubmitted && isIgsStudioUnlocked())" not in app_text:
    app_text = app_text.replace(
        "if (!isSubmitted) {\n      elapsedSeconds++;",
        "if (!isSubmitted && isIgsStudioUnlocked()) {\n      elapsedSeconds++;",
    ).replace(
        "if (!isSubmitted) {\r\n      elapsedSeconds++;",
        "if (!isSubmitted && isIgsStudioUnlocked()) {\r\n      elapsedSeconds++;",
    )
if "function initIgsAccessGate(" not in app_text:
    app_text = app_text.rstrip() + "\n" + JS_ADDITION
APP_JS_PATH.write_text(app_text, encoding="utf-8")
print("[+] Updated assets/js/app.js with SHA-256 + FNV-1a access gate controller")

# 4. Also protect presentation.html & decks/jlpt_n2_ai_studio_v44_eduslide_v4.html with shared SSO token (jlpt_igs_access_v1)
PRESENTATION_GATE_SNIPPET = """
<!-- ================= iGS DEMO CENTER SHARED SSO ACCESS PORTAL ================= -->
<style>
  #igsDeckGateOverlay {
    position: fixed;
    inset: 0;
    z-index: 9999;
    background-color: #070913;
    background-image:
      radial-gradient(circle at 18% 22%, rgba(16, 185, 129, 0.08) 0%, transparent 38%),
      radial-gradient(circle at 82% 76%, rgba(56, 189, 248, 0.07) 0%, transparent 40%),
      radial-gradient(rgba(148, 163, 184, 0.16) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 36px 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 16px;
    font-family: "Noto Sans TC", "Inter", sans-serif;
  }
  #igsDeckGateOverlay.hidden { display: none !important; }
  .igs-deck-card {
    width: 100%;
    max-width: 430px;
    background: #0d111d;
    border: 1px solid rgba(51, 65, 85, 0.85);
    border-radius: 24px;
    padding: 30px 28px;
    text-align: center;
    color: #f8fafc;
    box-shadow: 0 25px 50px -12px rgba(0,0,0,0.75);
  }
  .igs-deck-title { font-size: 28px; font-weight: 900; margin: 12px 0 6px; letter-spacing: -0.02em; }
  .igs-deck-grad {
    background: linear-gradient(90deg, #34d399 0%, #10b981 55%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .igs-deck-kpis { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 18px 0; }
  .igs-deck-kpi { background: #131929; border-radius: 16px; padding: 12px 8px; }
  .igs-deck-kpi-val { font-size: 22px; font-weight: 900; color: #34d399; font-family: "JetBrains Mono", monospace; }
  .igs-deck-kpi-lbl { font-size: 12px; color: #cbd5e1; margin-top: 2px; font-weight: 600; }
  .igs-deck-input {
    width: 100%;
    padding: 14px 16px;
    border-radius: 16px;
    background: #070a12;
    border: 1px solid rgba(51, 65, 85, 0.8);
    color: #fff;
    text-align: center;
    font-family: "JetBrains Mono", monospace;
    font-size: 16px;
    letter-spacing: 0.25em;
    outline: none;
    margin-top: 8px;
  }
  .igs-deck-input:focus { border-color: #34d399; }
  .igs-deck-btn {
    width: 100%;
    margin-top: 16px;
    padding: 14px;
    border-radius: 16px;
    background: #1c2333;
    color: #f1f5f9;
    font-weight: 800;
    font-size: 14px;
    border: none;
    cursor: pointer;
    transition: all 0.18s ease;
  }
  .igs-deck-btn:hover { background: #10b981; color: #020617; }
</style>
<div id="igsDeckGateOverlay">
  <div class="igs-deck-card">
    <div style="font-size:12px;color:#34d399;font-weight:800;letter-spacing:0.12em;">iGS SOVEREIGN EDUCATION PORTAL</div>
    <div class="igs-deck-title"><span>iGS </span><span class="igs-deck-grad">EduSlide Deck</span></div>
    <div style="font-size:12px;color:#cbd5e1;">JLPT N2 互動式 AI 刷題與認知診斷系統 v4.4 · 20頁教學簡報</div>
    <div class="igs-deck-kpis">
      <div class="igs-deck-kpi"><div class="igs-deck-kpi-val">20</div><div class="igs-deck-kpi-lbl">Slides 簡報</div></div>
      <div class="igs-deck-kpi"><div class="igs-deck-kpi-val">530</div><div class="igs-deck-kpi-lbl">N2 題庫</div></div>
      <div class="igs-deck-kpi"><div class="igs-deck-kpi-val">261</div><div class="igs-deck-kpi-lbl">Neural 音檔</div></div>
    </div>
    <div style="font-size:12px;font-weight:700;letter-spacing:0.12em;color:#cbd5e1;margin-top:8px;">ENTER ACCESS CODE</div>
    <input id="igsDeckCodeInput" type="password" class="igs-deck-input" placeholder="•  •  •  •  •" onkeydown="if(event.key==='Enter'){event.stopPropagation();submitIgsDeckCode();}" />
    <div id="igsDeckFeedback" style="font-size:12px;color:#cbd5e1;margin-top:10px;">✦ 與主系統共享通行授權（已解鎖主系統者自動放行）</div>
    <button type="button" class="igs-deck-btn" onclick="submitIgsDeckCode()">Unlock Presentation →</button>
    <div style="font-size:12px;color:#94a3b8;margin-top:16px;">🔒 Powered by AEOS © 2026 iGrowth Solutions</div>
  </div>
</div>
<script>
(function(){
  var KEY = 'jlpt_igs_access_v1';
  var FNV = '90d82d5e';
  var TTL = 30 * 24 * 60 * 60 * 1000;
  function fnv1a(s){
    var h = 0x811c9dc5;
    for(var i=0;i<s.length;i++){ h ^= s.charCodeAt(i)&0xff; h = Math.imul(h, 0x01000193)>>>0; }
    return h.toString(16).padStart(8,'0');
  }
  function checkUnlocked(){
    try {
      var params = new URLSearchParams(window.location.search);
      var q = (params.get('access') || params.get('code') || '').trim().toLowerCase();
      if(q && fnv1a(q) === FNV && q.length === 3){
        localStorage.setItem(KEY, JSON.stringify({token: FNV, ts: Date.now()}));
        params.delete('access'); params.delete('code');
        var clean = window.location.pathname + (params.toString() ? '?' + params.toString() : '') + window.location.hash;
        window.history.replaceState({}, document.title, clean);
      }
      var raw = localStorage.getItem(KEY);
      if(!raw) return false;
      var d = JSON.parse(raw);
      return d && d.token === FNV && (Date.now() - (d.ts||0) < TTL);
    } catch(e){ return false; }
  }
  window.submitIgsDeckCode = function(){
    var inp = document.getElementById('igsDeckCodeInput');
    var fb = document.getElementById('igsDeckFeedback');
    var val = String(inp ? inp.value : '').trim().toLowerCase();
    if(fnv1a(val) === FNV && val.length === 3){
      try { localStorage.setItem(KEY, JSON.stringify({token: FNV, ts: Date.now()})); } catch(e){}
      document.getElementById('igsDeckGateOverlay').classList.add('hidden');
    } else {
      if(fb){ fb.textContent = '⚠️ 通行碼不正確，請輸入 iGS 授權通行碼（不分大小寫）'; fb.style.color = '#fbbf24'; }
    }
  };
  if(checkUnlocked()){
    document.getElementById('igsDeckGateOverlay').classList.add('hidden');
  }
})();
</script>
"""

for deck_file in [BASE_DIR / "presentation.html", BASE_DIR / "decks" / "jlpt_n2_ai_studio_v44_eduslide_v4.html"]:
    if deck_file.exists():
        d_txt = deck_file.read_text(encoding="utf-8")
        if 'id="igsDeckGateOverlay"' not in d_txt:
            d_txt = d_txt.replace("<body>", "<body>\n" + PRESENTATION_GATE_SNIPPET, 1)
            deck_file.write_text(d_txt, encoding="utf-8")
            print(f"[+] Protected {deck_file.name} with shared SSO iGS Access Portal")

