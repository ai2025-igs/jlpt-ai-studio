---
fonts:
  display: "Noto Sans JP"
  body: "Noto Sans JP"
  mono: "JetBrains Mono"
colors:
  bg-canvas: "#020617"
  bg-surface: "#0f172a"
  bg-elevated: "#1e293b"
  bg-control: "#334155"
  border-muted: "#475569"
  text-primary: "#f8fafc"
  text-secondary: "#f1f5f9"
  text-body: "#e2e8f0"
  text-muted: "#94a3b8"
  pure-white: "#ffffff"
  jlpt-n2-orange: "#f39c42"
  jlpt-n1-red: "#ef6c67"
  jlpt-n3-green: "#00a383"
  jlpt-n4-purple: "#8c6bb1"
  jlpt-n5-blue: "#1e78b4"
  accent-sky: "#38bdf8"
  accent-amber: "#f59e0b"
  accent-amber-light: "#fbbf24"
  semantic-emerald: "#10b981"
  semantic-rose: "#f43f5e"
  scrollbar-thumb: "rgba(71, 85, 105, 0.6)"
  surface-glass: "rgba(30, 41, 59, 0.9)"
  shadow-dark: "rgba(0, 0, 0, 0.45)"
  focus-glow: "rgba(245, 158, 11, 0.45)"
  focus-solid: "rgba(245, 158, 11, 1)"
radii:
  - "4px"
  - "6px"
  - "8px"
  - "12px"
  - "16px"
  - "9999px"
fontSizes:
  - "12px"
  - "14px"
  - "16px"
  - "18px"
  - "20px"
  - "24px"
  - "30px"
---

# DESIGN.md — JLPT N2 AI Studio Visual System & Craft Contract

## 1. Aesthetic Direction & Domain Exemplars
- **Persona**: Tokyo National Testing Center Precision (`JEES / Japan Foundation Official N2`) meets Linear-grade High-Density Telemetry (`Operate` + `Read` Hybrid Mode).
- **Core Principle**: Zero decorative chrome, zero neon dark-glows, zero card-inside-card nesting (`nested-cards = 0`), and strict WCAG 2.1 AA contrast (`>= 4.5:1`) on every badge and interactive control.

## 2. Color Palette & Contrast Rules (OKLCH + Hex Dual-Anchored)
- **Canvas & Surfaces**:
  - `bg-canvas`: `#020617` (`oklch(12.9% 0.042 264.7)`) — Deep ink background.
  - `bg-surface`: `#0f172a` (`oklch(20.8% 0.042 265.8)`) — Primary workspace container.
  - `bg-elevated`: `#1e293b` (`oklch(27.9% 0.041 260.0)`) — Interactive control & tonal row surface (unbordered when nested inside `bg-surface`).
- **JLPT Official Level Accents & Mandatory Text Pairing**:
  - `jlpt-n2-orange`: `#f39c42` (`oklch(75.4% 0.148 64.9)`).
    - **HARD CONTRAST INVARIANT**: Because `#f39c42` has high relative luminance (`L = 0.44`), pairing `#ffffff` on `#f39c42` yields only **`2.15:1` contrast (FAIL)**. Every `#f39c42` surface (`#headerLevelBadge`, `#lvlBtn_N2`, `#officialExamLevelBox`, `#officialMondaiBanner`, active Mondai pills) **MUST** use `#020617` (`text-slate-950`, **`10.1:1` AAA contrast**) for primary text, and solid `#020617` (`bg-slate-950`) with `#fde68a` (`text-amber-200`, **`11.8:1` contrast**) for inner metadata chips.
  - `jlpt-n1-red`: `#ef6c67`, `jlpt-n3-green`: `#00a383`, `jlpt-n4-purple`: `#8c6bb1`, `jlpt-n5-blue`: `#1e78b4` (Reserved in locked state while N2 Sprint Mode is active).

## 3. Typography & Hierarchy (`>= 1.25x` Modular Scale)
- **Font Stack**:
  - Primary CJK + UI: `'Noto Sans JP', 'Hiragino Kaku Gothic ProN', 'Yu Gothic', system-ui, sans-serif`
  - Telemetry / IRT / Timers: `'JetBrains Mono', monospace` with `font-variant-numeric: tabular-nums`
- **Hard Floor**:
  - **Minimum UI Label / Badge / Button Font Size**: `12px` (`0.75rem`, `text-xs`). Classes `text-[9px]`, `text-[10px]`, and `text-[11px]` are strictly banned (`0` occurrences).
  - **Minimum Prose / Reading Body Font Size**: `14px` (`0.875rem`, `text-sm`) for explanations/lists, `16px–18px` (`1rem–1.125rem`) for N2 exam stems and reading passages with `line-height >= 1.85` (`leading-relaxed`) to prevent `<ruby><rt>` furigana collision.
- **Heading Hierarchy**:
  - Sequential `h1` (`1.25rem` / `20px` app header) ➔ `h2` (`1.125rem` / `18px` section & modal titles) ➔ `h3` (`0.95rem` / `15.2px` sub-sections). Never skip from `h1` to `h3`.

## 4. Layout, Spatial Architecture & Anti-Nesting (`nested-cards = 0`)
- **Single-Level Card Rule**:
  - Only top-level section panels (`#tabPane_1 > section > div`, `#preAnswerStandbyCard`, `#diagnosticPanel`, `#irtScoreCardBox`, `#tabPane_2` primary cards, `#tabPane_3` primary cards, and modal dialogs) may combine `rounded-*` + `bg-slate-*` + 4-sided `border`.
  - Inner groups inside a card **MUST NOT** use 4-sided `border` or `shadow-*` together with `rounded-*` and `bg-*`. Use tonal background fills (`bg-slate-900/90 rounded-xl p-4` without `border`), single-edge dividers (`border-b border-slate-800` or `border-t border-slate-800`), or open flex rows.
- **Padding Floor**:
  - Every bordered or colored banner (`#officialExamLevelBox`, `#officialMondaiBanner`) must maintain at least `10px–16px` (`p-2.5` to `p-4`) padding on all sides.

## 5. Motion & Interaction Physics
- **No Continuous Pulsing Dots**: Status dots (`#timerDot`, `#choukaiStatusDot`) communicate state via solid semantic color, never continuous `animate-pulse` or `animate-ping`.
- **Exponential Easing**: Audio waveform (`eqWave`) and transitions use `cubic-bezier(0.22, 1, 0.36, 1)` (`ease-out-quint`) and honor `@media (prefers-reduced-motion: reduce)`.
