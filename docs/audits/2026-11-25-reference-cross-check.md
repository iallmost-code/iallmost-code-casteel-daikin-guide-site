# Daikin guide audit · November 25, 2026

Baseline: GitHub main at `950cc16` and the matching Render copy. The baseline passed 57 browser tests. This pass checked the office app workflows and the manufacturer sources listed below.

| Area | Finding and correction |
| --- | --- |
| Compressor Check | SiUS612412E S-104 (p.20) says a failed running check means the compressor **might** be faulty. The plain-language summary now preserves that distinction. The R-410A page distinguishes S-17A insulation from S-17B ground testing. The R-32 page retains the corrected 30 MΩ criterion and directs technicians to Daikin for the approved instrument and test setting. |
| Fit weigh-in | 3P731493-1, 3P761829-1B, and 3P679063-5L use actual tubing length in the charge tables. The guide now labels the field accordingly and keeps equivalent length separate. The DX6VSA size selector follows the manual’s 1.5–3 ton coverage. The calculator shows table charges as references, calculates A minus the nameplate factory charge when entered, and withholds numbers for heat-pump-only entries selected on an AC model. |
| Larger R-32 Fit | 3P679063-5L p.15 shows a 100 ft actual limit for 5-ton units while p.24 prints longer rows. The guide withholds results beyond 100 ft until model-specific sizing is verified. The 4-ton DH9VS catalog entry has no verified matching installation-manual charging coverage, so its spec remains available without borrowed P/T, weigh-in, or subcooling targets. |
| R-32 SE/SQ weigh-in | IOD-4048B/C, IOD-4047A and IOD-4064A refer lines longer than 79 ft or elevation differences over 50 ft to TP-110. The guide now stops the standard calculation above 79 ft. |
| R-410A custom TXV | The instructions follow the entered unit’s manual and no longer show Fit Charge Mode instructions. |
| Search and references | Home search finds Compressor Check. Zoning search opens the explicitly named DOZP or EWC UT3000 pane when both panes have cross-references. The old AHRI search branch has been removed from Home while its data stays intact. The DX17VSS/DZ17VSA and light commercial DBC/DBH installation manual links now use Daikin City’s working copies of the same revisions. |

## Source checks

- [Daikin SiUS612209EB](https://www.daikinac.com/docs/default-source/dfve/sm-sius612209eb.pdf), pp.5–6 and 20–23. Capacitor reference, insulation and ground test separation, and running check.
- [Daikin SiUS612412E](https://cdn.daikincloud.io/PIM/Assets/Documents/SM-SiUS612412E.pdf), pp.5–6 and 18–21 and the revision record. Confirmed insulation threshold and running-test conclusions.
- [Daikin 3P731493-1](https://daikincomfort.com/docs/default-source/daikin-fit-heat-pump---dz6vs/im-3p731493-1.pdf), pp.23–30. Checked Fit charge table units and selected values, nameplate adjustment rule, and standard and Enhanced Capacity cooling targets.
- [Daikin 3P761829-1B](https://daikincomfort.com/docs/default-source/daikin-fit-heat-pump---dh6vs/im-3p761829-1b_em23a024a_24071.pdf), pp.27–31, and [Daikin 3P679063-5L](https://daikincomfort.com/docs/default-source/fit-aurora-heat-pump-dh9vs/im-io-01_en_3p679063-5l_web.pdf), pp.15 and 24–27. Checked actual length, selected table rows, and alternate model limits.
- Compared all 408 pressure–temperature entries across the six R-32 manual/chart comparisons. These include the shared IOD-4048 table checked independently against B and C. No mismatches in the captured points. Charging data tables are unchanged.
- The DMVT P1400 conflicting heater airflow values and the DH5SE printed heating superheat disagreement from the [previous audit](2026-11-17-app-audit.md) remain flagged. No replacement values were inferred. This pass does not certify every imported specification or fault-code transcription.

Browser coverage includes all sidebar destinations, Home and fault search, zoning tabs, resources, guided airflow, model lookup, the charge modes, compressor views, printing, offline reload, and offline update activation.
