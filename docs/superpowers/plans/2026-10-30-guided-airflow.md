# Guided Airflow Implementation Plan

Goal: Implement the approved desktop airflow preview inside the existing guide, preserving the complete source references.
Architecture: Inline HTML/CSS/JavaScript reads the existing reference tables and saved line blocks at runtime. No duplicated numeric dataset or invented/interpolated values. Existing static HTML and offline service worker remain the delivery mechanism.
Spec: approved interactive airflow preview and conversation on October 30, 2026.

Constraints: office PC use; preserve all reference-card contents and calculation scripts; keep DR80SN manuals and model suffixes separate; label missing data; full references remain searchable and usable without the lookup.

Review focus: switching manuals must clear old results; heating must not reuse cooling; missing watts/rise remain missing; unusual/nonmonotonic source values preserved; global search must reveal references inside the new collapsible section.

- [x] Task 1: Add browser regression checks for lookup absence (red), representative original values, heating/manual separation, incomplete AMST data, original-reference access and search.
- [x] Task 2: Add guided lookup, plain-language explanations and original-table view. Read eight DR80SN 2035A model tables and their heating counterparts, five 2039C cooling blocks, and six AMST cooling blocks. Other families open exact source references with explanations. Do not calculate between static columns or recommend taps.
- [x] Task 3: Run complete tests at 800/1280/1440/1920; verify reference text and existing scripts unchanged; inspect screenshot, refresh offline hash, publish to the existing Render site and verify the live lookup.

Verification: 10 browser tests passed. Independent review found wrong-family navigation, hidden topic groups and omitted model-specific source notes; regression tests failed before fixes and passed afterward. Source notes/footnotes now accompany each model, P1300 opens only its exact official manual, and reference navigation selects the correct topic. Deployment verification remains the final release step.
