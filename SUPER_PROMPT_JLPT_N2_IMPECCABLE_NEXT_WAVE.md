# 🏛️ JLPT N2 AI Studio — Design Conversation Forensics (`7320681b`) & Next-Wave Impeccable Super Prompt
<!-- ========================================================================= -->
<!-- Target Repo: D:\MuseAcademy_50_25C16\jlpt-ai-studio                       -->
<!-- Live URL: https://ai2025-igs.github.io/jlpt-ai-studio/                    -->
<!-- Design Conversation: 7320681b-b594-467d-991d-09e6dec036d3                 -->
<!-- Impeccable Engine Status: 0 Static Findings / 0 Live DOM Findings (exit 0)-->
<!-- ========================================================================= -->

## 1. Executive BLUF & Forensic Reconstruction of Conversation `7320681b`

Through full-transcript inspection of design conversation `7320681b-b594-467d-991d-09e6dec036d3` (`629` steps across a 24-Wave overnight evolution + multi-subagent N1–N5 content audit) and static/live DOM telemetry on `D:\MuseAcademy_50_25C16\jlpt-ai-studio`, we reconstructed the complete engineering trajectory, root-cause failure modes, and next-stage N2 mastery gaps:

| Forensic Dimension | Trajectory in Conversation `7320681b` | Root Cause & Architectural Lesson | Current Verified State (`a230b936`) |
| :--- | :--- | :--- | :--- |
| **1. UI Click Freeze Incident (Steps 508–516)** | User reported all N1–N5 level buttons and question pool buttons (`100% / 300% / 500%`) were completely unclickable on GitHub Pages. | Automated wave script (`overnight_wave_crucible.py`) injected a duplicate `const brandBadge = document.getElementById('headerLevelBadge');` inside `switchLevel()` (`app.js:260` & `266`). V8 threw a parse-time `SyntaxError`, aborting all global `onclick` registrations before runtime. | Fixed in `app.js` + hardened in `scripts/validate_jlpt_studio.py` via `node --check` and regex handler verification (`0` errors). |
| **2. N2 Exclusive Sprint Lock (Steps 605–628)** | User directed: *"先專注在 N2，把 N1, N3, N4, N5 先關掉，把 N2 做到好之後再開啟其他級別"*. | `ENABLED_LEVELS = new Set(['N2'])` locked N1/N3/N4/N5 with disabled badges (`待開放`) and focused default boot state on `N2` (`530` total items: `106` official `inMock100` + `424` extended pool). | Active & verified (`N2` default boot, `530` items across all `19` official JEES Mondai). |
| **3. N2 Content & Answer Audit (`Subagent d1a3083f`)** | Parallel subagents audited all `2,405` items (`530` in `data/n2_bank.json`). | `Subagent-Audit-N2` repaired `132` schema/stem defects (missing `<u>...</u>` target underlines in `V1_KANJI_READ` / `V2_ORTHOGRAPHY`, nested `<ruby>` tags, rotated `L6_INTEGRATED_LISTEN` options) and purged `28` `socraticHint` answer spoilers. | `530 / 530` N2 items pass `--strict-aqe` (`325` `<ruby>` items, `0` schema or spoiler errors). |
| **4. Impeccable v4.8.0 Visual & DOM Craft Audit (`CP-01`..`CP-10`)** | Prior to Impeccable integration, `jlpt-ai-studio` accumulated **`82` static** and **`69` live DOM** violations across 24 rapid feature waves. | `#f39c42` N2 badge paired with `#ffffff` text (`2.1:1` contrast fail); `47` micro-labels at `9px–11px`; `55` static / `8` live `nested-cards` (`border + rounded + bg` inside outer cards); skipped `h1 -> h3`; `animate-pulse` dots and `border-l-4` toast. | **All `82` static and `69` live DOM findings eliminated (`0` findings, `exit 0`)** via `PRODUCT.md`, `DESIGN.md`, and surgical `CP-01`..`CP-10` refactor. |
| **5. `startOfficialMockExam('FULL')` Slice Bug (`app.js:1683`)** | Clicking *"啟動 N2 100% 標準模擬考 (106題)"* executed `fullBank.slice(0, 106)`. | Because `n2_bank.json` orders items sequentially by Mondai or wave batch, `.slice(0, 106)` grabbed only the first 106 array items rather than the `106` balanced `inMock100 === true` items across all 19 Mondai. | **Fixed in `app.js:1688`**: `startOfficialMockExam('FULL')` now invokes `setQuestionPoolScope('MOCK_100')`, loading the exact `106` balanced mock items. |

---

## 2. Five Strategic Insights & Remaining N2 Mastery Opportunities for Conversation `7320681b`

While the visual craft floor (`0` Impeccable findings) and the `MOCK_100` filter bug are now resolved, forensic inspection of `assets/js/audio-engine.js`, `assets/js/psychometric.js`, and `data/n2_bank.json` reveals **5 high-leverage architectural & pedagogical upgrades** that should be executed next in the design conversation (`7320681b-b594-467d-991d-09e6dec036d3`):

### Insight 1: N2 Choukai (`聴解`) Dedicated Neural MP3 Coverage (`11 / 155` Static MP3s vs. Web Speech Fallback)
- **Evidence (`audio-engine.js:220–265`)**: `playListeningDialogue()` checks `hasDedicatedQuestionMp3 = q.audioFile && q.audioFile.includes("${q.id}.mp3")`. Currently, `audio/n2/` contains only `11` seed MP3 files (`N2_V1_001.mp3`, `N2_L1_001.mp3`, etc.), meaning **`144` out of `155` N2 listening items** (`L1_TASK_COMP` through `L6_INTEGRATED_LISTEN`) fall back to browser `window.speechSynthesis` (which lacks reliable male/female voice alternation on many mobile/Windows browsers).
- **Recommendation**: Run `scripts/generate_listening_mp3.py` (using `edge-tts` dual neural voices `ja-JP-KeitaNeural` [Male] and `ja-JP-NanamiNeural` [Female] with `-8%` N2 exam cadence and `400ms` turn pauses) to pre-generate all `155` N2 listening dialogues (`audio/n2/N2_L*.mp3`), achieving 100% offline/GitHub Pages neural audio parity.

### Insight 2: Official JLPT N2 `L5_QUICK_RESP` (`聴解問題4：即時応答`) 3-Option Authenticity
- **Evidence (`data/n2_bank.json` & `psychometric.js:76`)**: In the real JLPT N2 exam (`聴解問題4 即時応答`, `12` items in `100%` mock, `60` items in `500%` pool), examinees hear a short utterance and choose from **3 spoken responses (`1, 2, 3`)**—never 4 options. Currently, `L5_QUICK_RESP` items in `n2_bank.json` have 4 options (`options.length === 4`), and options are displayed as visible text before answering even when `blindListeningMode` is off.
- **Recommendation**:
  1. For `L5_QUICK_RESP`, enforce **Audio-First Masked Options** by default (showing only `[選択肢 1]`, `[選択肢 2]`, `[選択肢 3]` until the user clicks an option, then revealing the full Japanese script + pitch accent + distractor breakdown).
  2. Trim or mark the 4th distractor in `L5_QUICK_RESP` so `100%` Mock Mode strictly mirrors the 3-choice official JEES format.

### Insight 3: Official 2-Section Exam Countdown Mode (`言語知識・読解 105 分鐘` + `聴解 50 分鐘`)
- **Evidence (`app.js:882–915`)**: Currently, `startQuestionTimer()` runs a **per-question stopwatch** (`00:00` counting up with target thresholds `35s / 60s / 120s`). However, the #1 reason Taiwanese N2 candidates fail the Reading (`読解`) section is **macro time-allocation collapse** across the `105-minute` combined `言語知識（文字・語彙・文法）・読解` section (spending `>45` minutes on Vocabulary/Grammar and leaving `<60` minutes for `21` Reading items across `R1_SHORT`, `R2_MID`, `R3_INTEGRATED`, `R4_THEMATIC`, `R5_INFO_SEARCH`).
- **Recommendation**: Add a toggleable **「N2 正式計時模擬考模式 (105m + 50m Countdown Bar)」** inside `#officialMondaiBanner` with live pace telemetry (`建議進度：文字語彙 15m ➔ 文法 20m ➔ 読解 70m`), warning the student if their cumulative written-section pace drifts behind the `105m` cutoff.

### Insight 4: ★ Star Grammar (`G2_STAR_ORDER` 文の組み立て) Auto-Grading & Permutation Trace
- **Evidence (`app.js:775–865`)**: The interactive 4-slot ★ (`★` 排序題) widget allows students to click tokens into slots `1..4`, and `resetStarSlots()` / `placeStarToken()` updates the visual slots, but students still have to manually click the corresponding `1..4` radio option in `#optionsContainer` below, or if they click the radio option directly, the 4-slot sentence preview does not auto-populate the complete 4-token permutation.
- **Recommendation**: Bidirectionally bind the 4-slot ★ composer with `#optionsContainer`:
  - When all 4 slots are filled in `#starInteractiveWidget`, automatically highlight the token placed in the `★` (`starPosition`) slot and offer a one-click `「確認 ★ 位置並送出診斷」` button.
  - When the student answers (or clicks an option in `#optionsContainer`), automatically animate the 4 tokens into their exact grammatical order (`S + O + V` / `連体修飾節`) inside `#starInteractiveWidget` so the student reads the complete, natural Japanese sentence.

### Insight 5: Permanent Impeccable CI Gate inside `scripts/validate_jlpt_studio.py`
- **Evidence (`scripts/validate_jlpt_studio.py`)**: Wave scripts in conversation `7320681b` repeatedly modified `index.html` and `app.js` without an automated CSS/DOM craft gate, causing `nested-cards`, `low-contrast`, and `undersized-ui-text` regressions.
- **Recommendation**: Embed `impeccable.cmd detect --json index.html assets/css/custom.css assets/js/app.js` directly into `validate_jlpt_studio.py` as **Gate 0 (Neuro-Symbolic UI Craft Gate)** so any future wave that introduces a single slop or contrast violation fails `validate_jlpt_studio.py` with a non-zero exit code.

---

## 3. Master Copy-Paste Super Prompt for Design Conversation (`7320681b-b594-467d-991d-09e6dec036d3`)

Copy and paste the entire block below directly into conversation **`7320681b-b594-467d-991d-09e6dec036d3`** to execute the next N2 Mastery Wave while preserving **100% Impeccable Zero-Violation Craft (`exit 0`)**:

```markdown
/plan2 /goal2 We have completed a full Impeccable v4.8.0 (Rust Engine v0.1.18) Neuro-Symbolic UI & Cognitive Optimization across `D:\MuseAcademy_50_25C16\jlpt-ai-studio`:
1. `PRODUCT.md` and `DESIGN.md` are now anchored in the repo root as our Single Source of Truth (SSOT).
2. All `82` static findings and `69` live DOM findings (`low-contrast` on `#f39c42`, `cramped-padding`, `nested-cards`, `undersized-ui-text` `<12px`, `tiny-text`, `skipped-heading`, `flat-type-hierarchy`, `pulsing-dot`, `dark-glow`, `side-tab`) have been eliminated down to **`0` findings (`exit 0`)** in both static and live headless browser scans.
3. `startOfficialMockExam('FULL')` in `assets/js/app.js` has been fixed to call `setQuestionPoolScope('MOCK_100')` (`106` balanced `inMock100: true` N2 items across all 19 Mondai) instead of `.slice(0, 106)`.

Now, keeping our 100% focus on **JLPT N2** (`data/n2_bank.json`, `530` items) and strictly maintaining **`0` Impeccable detector findings (`impeccable.cmd detect --json`)**, please execute the following **5-Wave N2 Exam Mastery Upgrade**:

### Wave 1: Permanent Impeccable Craft Gate in `scripts/validate_jlpt_studio.py`
- Add `validate_impeccable_craft()` to `scripts/validate_jlpt_studio.py` that runs:
  `C:\Users\horac\.gemini\config\skills\impeccable\scripts\impeccable.cmd detect --json index.html assets/css/custom.css assets/js/app.js assets/js/audio-engine.js`
- Enforce `len(findings) == 0` (`exit 0`). Never introduce `text-[9px]`, `text-[10px]`, `text-[11px]`, `text-slate-500` on dark slate, `#ffffff` text on `#f39c42`, `animate-pulse`, `border-l-4`, or 4-sided `border`/`shadow-*` on inner rounded elements inside outer cards (`nested-cards`).

### Wave 2: Bidirectional ★ Star Grammar (`G2_STAR_ORDER`) Composer & Full Sentence Synthesis
- In `assets/js/app.js` (`renderStarInteractiveWidget`, `placeStarToken`, `selectOption`):
  1. Add a canonical `starOrder` array (or derive the natural 4-token sequence from `q.explanation` / `q.correctIndex`) so that when a student submits an answer to any `G2_STAR_ORDER` question (`N2` Problem 8, 5 mock / 25 pool items), `#starInteractiveWidget` displays the **complete, grammatically ordered 4-slot sentence** with the `★` slot highlighted in `bg-slate-950 text-amber-300`.
  2. When a student fills the `★` slot (`starSlotIdx`) in `#starInteractiveWidget`, provide a one-click button `「🎯 以目前 ★ 格位直接送出作答」` that automatically triggers `selectOption(placedOptIdx)` without requiring a redundant click on the radio list below.

### Wave 3: Official N2 2-Section Exam Countdown & Pacing HUD (`105m Written + 50m Choukai`)
- In `index.html` and `assets/js/app.js`:
  1. Add a compact **「⏱️ N2 模擬考倒數 (105:00 言語・読解 / 50:00 聴解)」** mode alongside the per-question timer when `currentPoolScope === 'MOCK_100'`.
  2. Compute real-time section pacing against the official N2 time allocation (`文字・語彙 15m` [Q1–Q32] ➔ `文法 20m` [Q33–Q54] ➔ `読解 70m` [Q55–Q75] ➔ `聴解 50m` [Q76–Q106]) and show a non-pulsing semantic badge (`領先配速` / `配速正常` / `⚠️ 読解時間緊迫`) using `font-variant-numeric: tabular-nums` and `text-xs`.

### Wave 4: `L5_QUICK_RESP` (N2 聴解問題4：即時応答) Authentic Audio-First 3-Choice Masking
- In `assets/js/app.js` and `data/n2_bank.json`:
  1. When rendering `L5_QUICK_RESP` (`問題4 即時応答`), automatically enable audio-first option masking before submission (displaying `選択肢 1 — 🔊 請先聽語音並依高低音調與語境作答` until the student clicks an option or toggles `👁️ 顯示文字稿`), matching the real N2 test booklet where Problem 4 has zero printed text.
  2. Ensure every `L5_QUICK_RESP` item in `data/n2_bank.json` highlights the exact conversational register (`敬語・謙譲語・ビジネス謝罪・婉曲断り`) in its post-answer diagnostic card.

### Wave 5: N2 Dual-Voice Neural Audio Batch Synthesis (`audio/n2/*.mp3`) & Standalone Rebuild
- Check/update `scripts/generate_listening_mp3.py` to support batch generation of missing N2 listening MP3s (`ja-JP-KeitaNeural` & `ja-JP-NanamiNeural`) and verify `audio-engine.js` seamlessly routes between dedicated MP3s and multi-speaker Web Speech synthesis.
- Run full verification:
  1. `python scripts/validate_jlpt_studio.py --level N2 --min-questions 530 --check-furigana --check-audio --strict-aqe` (`exit 0`)
  2. `C:\Users\horac\.gemini\config\skills\impeccable\scripts\impeccable.cmd detect --json index.html assets/css/custom.css assets/js/app.js` (`[]`, `exit 0`)
  3. `python scripts/build_standalone.py` (`exit 0`)
```

---

## 4. Reference Summary of the 10 Executed Impeccable Context Prompts (`CP-01`..`CP-10`)

Full copy-paste prompt templates for each of the 10 Impeccable optimization stages are archived in:
- `D:\iGS_Meta_Nexus_Studio\workshops\Impeccable_40m_ZeroToHero\05_JLPT_N2_Studio_Analysis_and_10_Impeccable_Context_Prompts.md`

| Prompt ID | Impeccable Skill / Verb | Target Surface in `jlpt-ai-studio` | Before (Violations) | After (Verified Result) |
| :--- | :--- | :--- | :--- | :--- |
| **`CP-01`** | `/impeccable init` + `shape` | `PRODUCT.md` | Missing product context (`0` files) | Created `PRODUCT.md` anchoring N2 19-Mondai scope & anti-goals |
| **`CP-02`** | `/impeccable document` | `DESIGN.md` | `21` `design-system-color` advisories | Created `DESIGN.md` with full hex/rgba/OKLCH token registry (`0` advisories) |
| **`CP-03`** | `/impeccable colorize` + `audit` | `#headerLevelBadge`, `#lvlBtn_N2`, `#officialExamLevelBox`, `#officialMondaiBanner`, `app.js:556` | `11` live / `2` static `low-contrast` (`2.1:1` white on `#f39c42`, `3.8:1` `text-slate-500`) | `#020617` ink on `#f39c42` (`10.1:1`), `bg-slate-950 text-amber-300` chips (`11.8:1`), `text-slate-400` (`6.4:1`) ➔ **`0` contrast hits** |
| **`CP-04`** | `/impeccable layout` + `distill` | `index.html` & `app.js` inner containers | `55` static / `8` live `nested-cards` + `2` `cramped-padding` | Stripped 4-sided `border`/`shadow` on inner rounded containers; added `p-2.5`/`p-3` to banners ➔ **`0` nested-cards, `0` cramped-padding** |
| **`CP-05`** | `/impeccable typeset` | `index.html`, `app.js`, `audio-engine.js`, `custom.css` | `36` `undersized-ui-text` (`<11px`), `11` `tiny-text` (`<12px`), `1` `skipped-heading`, `1` `flat-type-hierarchy` | Upgraded all `9px–11px` to `text-xs`/`text-sm`; fixed `h1 (24px) -> h2 (18px) -> h3 (15px)` (`>=1.33x` step) ➔ **`0` typography hits** |
| **`CP-06`** | `/impeccable clarify` | `#tabPane_1` N2 Exam & ★ Star / Reading panes | `.slice(0, 106)` bug in `startOfficialMockExam('FULL')`; nested option borders | Fixed `startOfficialMockExam('FULL')` to use `setQuestionPoolScope('MOCK_100')`; tonal option rows |
| **`CP-07`** | `/impeccable adapt` + `harden` | `#diagnosticPanel` & `#preAnswerStandbyCard` | Inner card borders & `9px` telemetry badges | Flattened 5-col diagnostic dock into clean tonal rows with `12px` badges |
| **`CP-08`** | `/impeccable bolder` + `quieter` | `#tabPane_2` (`2PL-IRT` + `6D Radar`) & `#tabPane_3` (`FSRS`) | `11px` SVG radar text (`undersized-ui-text`) & nested KPI borders | Upgraded SVG radar labels to `12px`, `tabular-nums` on IRT/FSRS counters |
| **`CP-09`** | `/impeccable animate` + `polish` | `custom.css`, `index.html`, `app.js`, `audio-engine.js` | `2` `pulsing-dot` (`animate-pulse`), `1` `dark-glow`, `1` `side-tab` (`border-l-4`) | Removed `animate-pulse`/`animate-ping`, removed `shadow-amber-500/20`, replaced `border-l-4` with `border`, added `prefers-reduced-motion` |
| **`CP-10`** | `/impeccable critique` + `hooks` | Static & Live Headless Browser Gate | `82` static / `69` live DOM violations (`exit 1`) | **`0` static findings (`exit 0`) & `0` live DOM findings (`exit 0`)** |
