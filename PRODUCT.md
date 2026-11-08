# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Taiwanese high-school and university learners preparing for the Japanese-Language Proficiency Test (JLPT N1–N5), with immediate flagship focus on **JLPT N2**. They already know the exam structure and want a high-velocity, distraction-free interactive practice and cognitive diagnostic workspace that catches L1 Mandarin Kanji false-friend interference (Odlin L1 transfer) and high-confidence blindspots (Self-Regulated Learning calibration).

## Product Purpose

`jlpt-ai-studio` provides an authentic, zero-scroll 1080p exam simulation and real-time cognitive diagnostic platform aligned with the official JEES/JLPT sample interface (`jlpt.jp/tw/samples/`). Success is measured by two outcomes: (1) learners complete timed N2 written (`105m`) and dual-voice listening (`50m`) practice across the 106-question Official Mock, 318-question 300% Pool, and 530-question 500% Flagship Pool with zero visual friction, and (2) immediate post-answer diagnostics expose distractor traps, syntactic chunking chains, and 2PL-IRT scaled score projections (`/180` total, `>=90/180` pass threshold, and `>=19/60` per-section cutoff).

## Positioning

`jlpt-ai-studio` combines an official-sample-aligned exam console (`Operate` mode) with a side-by-side psychometric and pedagogical diagnostic dock (`Read` mode), backed by pre-compiled 500% question banks (`2,405` total questions across N1–N5; `530` in N2), 33 neural dual-voice (`ja-JP-KeitaNeural` & `ja-JP-NanamiNeural`) listening tracks, 2PL-IRT ability estimation, and FSRS v5 spaced-repetition scheduling.

## Operating Context

Students use the web application at `https://ai2025-igs.github.io/jlpt-ai-studio/` or the offline single-file bundle (`dist/jlpt_n1_n4_standalone_v3.html`) on 1920x1080 desktop displays, laptops, or tablets. They navigate primarily via keyboard shortcuts (`1–4`, `Enter`, `←/→`, `R`, `H`, `F`) across three workspace tabs:
- **Tab 1 (`#tabPane_1`)**: 7-column Official JLPT Sample Exam Console + 5-column Real-Time Pedagogical & Diagnostic Dock.
- **Tab 2 (`#tabPane_2`)**: 2PL-IRT Scaled Score Estimator (`/180`), 6D Cognitive Radar Chart, Official Score Report Card Printer, and AI Coach Prescription.
- **Tab 3 (`#tabPane_3`)**: FSRS v5 Spaced-Repetition Queue, Full-Text Search, NotebookLM Podcast Exporter, and Exam Reference Treasure Box (Verb Conjugations, Transitive/Intransitive Pairs, Benefactive Arrows, 23 Taiwan-Japan False Friends & Tokyo Pitch Accent Cards).

## Capabilities and Constraints

- **N2 Flagship Focus**: N2 (`#f39c42`) is the active primary exam target (`530` questions across `19` official Mondai subtypes, including N2-exclusive Mondai 3 Word Formation `語形成`, Mondai 11 A/B Integrated Reading `統合理解`, and Mondai 13 Information Retrieval `情報検索`). N1, N3, N4, and N5 remain locked in the UI switcher until N2 mastery verification completes.
- **DOM Contract Preservation**: All existing element IDs (`#headerLevelBadge`, `#lvlBtn_N2`, `#officialExamLevelBox`, `#officialMondaiBanner`, `#scaffoldingActionStrip`, `#standardTtsBar`, `#listeningConsoleBox`, `#qStemText`, `#starReconstructorBox`, `#optionsContainer`, `#srlConfidenceCard`, `#preAnswerStandbyCard`, `#diagnosticPanel`, `#tabPane_1..3`) must remain intact for `assets/js/app.js`, `scripts/validate_jlpt_studio.py`, and `scripts/build_standalone.py`.
- **Zero Slop & Zero Distraction**: No pulsing status dots at rest, no colored glow shadows on dark backgrounds, no `border-l-4` side-tab tells, and no card-in-card nesting (`nested-cards`) that wastes vertical viewport height.

## Brand Commitments

Authoritative, calm, exam-precise. The interface pairs official JEES/JLPT structural clarity with high-contrast dark-studio ergonomics designed for long reading and listening sessions.

Three-word personality: **precise, focused, pedagogical**.

Specifically avoid:
- **Low-contrast white-on-amber text**: Never place `#ffffff` text directly on `#f39c42` N2 amber backgrounds (`2.2:1` fail); always pair `#f39c42` surfaces with deep slate ink (`#0f172a` / `#020617`, `>= 9.4:1` WCAG AAA).
- **Undersized micro-labels**: Never set functional UI text below `12px` (`0.75rem`) or body prose below `14px` (`0.875rem`).
- **Nested card clutter**: Use `1px` structural hairlines (`border-slate-800`) and spacing groups rather than wrapping every sub-element in its own bordered card.

## Accessibility & Inclusion

Baseline: WCAG 2.1 AA across all three workspace tabs.
- All text and interactive badges meet `>= 4.5:1` contrast (`>= 9.4:1` on primary N2 amber surfaces).
- Heading hierarchy strictly follows `h1 -> h2 -> h3` with zero skipped levels and `>= 1.25x` scale progression.
- Full keyboard operability with visible `:focus-visible` outlines (`2px solid #f39c42`).
- `@media (prefers-reduced-motion: reduce)` respected for all audio equalizer and slot animations.
