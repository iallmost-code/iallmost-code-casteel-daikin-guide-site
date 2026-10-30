# Unified Equipment Workspace Plan

Goal: Implement the approved PC equipment-workspace sample using existing app data.
Spec: approved interactive equipment-workspace sample, October 30, 2026.
Architecture: new Equipment lookup section, with AHRI, equipment info, known gaps and source pages retained as subpages. Model records derive from existing specification tables and embedded catalog; no new technical values. Equipment section tabs show linked source references and select existing Airflow/Charge tools with available exact model context.

Constraints: retain original reference text, calculation scripts and catalog; distinguish catalog snapshot from current AHRI certification; scope charging/airflow to applicable model and generation; preserve unknown values and source conflicts; manual links require internet; all HTML inline for offline guide.

Tasks:
- [ ] Add browser regression tests (watch absence fail): exact model lookup, ambiguous/unknown input, selection and catalog matches, matching charging context, wiring/manufacturer sources, print summary and existing AHRI/reference navigation.
- [ ] Implement model records, unified workspace panels, selected-combination summary, original-page links, print view and header search integration. Do not infer outdoor airflow or live certification. Retain original navigation paths.
- [ ] Run full browser suite and content-integrity checks, desktop widths, independent code review, offline version refresh; publish existing site and verify live.

Review focus: wildcard model patterns and ambiguous matches, clearing stale combinations, no reference applicability overclaims, maximum 5-ton shared manual exceptions, printable content escaping, unchanged old workflow and offline functions.

User steering: hide all AHRI matching UI while retaining the embedded information. Remove AHRI selection from the new workspace, prevent legacy page access, hide matchup search shortcuts, omit matched ratings from printing. Direct indoor-model lookup remains available.

Verification: 21 tests passed, including existing airflow coverage. Review findings for internal wildcards, source-pattern catalog aliases and header synchronization were reproduced failing and fixed. Specification inheritance is only from a unique matching source pattern in the same family, labeled in the workspace and printout. AHRI matching UI hidden, original catalog script unchanged. Original reference-card HTML, charge dataset and airflow script unchanged. Final release step is live deployment verification.
