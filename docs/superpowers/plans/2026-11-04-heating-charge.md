# Heating Charge Mode

Problem: charge sheet has no operating-mode input and applies cooling targets to heat-pump heating readings, producing inappropriate high/low charge instructions.
Verified source: DH4SE IOD-4047A p.11, manufacturer PDF downloaded November 4, 2026. Heating method is by weight with line-size, length and component adjustments; final adjustments in cooling. Heating superheat 8±1°F at 4–6 inches from compressor; true suction access port for pressure measurement.

Plan: add required operating-mode selection; clear readings and measurement confirmation when mode changes; disable cooling liquid-side inputs in heating; gate heating superheat comparison on confirmation of true suction location; show source-specific DH4SE heating reference only. Other heat-pump families get explicit no-connected-heating-target state, never cooling verdicts. AC-only equipment must not receive a heating charge assessment. Keep weigh-in tables and cooling calculations intact. Refresh offline version, run existing and new browser regressions, review and deploy.

Verification: 28 browser tests passed, including seven heating regressions that failed before implementation. Independent review confirmed manual applicability and routing with no important issue; positional UI wording corrected. Original references, numeric datasets, equipment workspace and airflow script unchanged. Desktop widths 800–1920 fit. Offline cache updated.
