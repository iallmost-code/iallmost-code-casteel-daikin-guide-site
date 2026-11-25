# Full audit of the live guide (Nov 25, 2026)

Base build: site repo `2931830` (the newest build, including the Compressor Check tab and the reference cross-check corrections).

## What was checked and passed

- **Navigation and layout.** Every page shows exactly one section. There is no sideways scroll at 1024 or 1440 px wide, no missing tab targets, no empty cards and no duplicate ids.
- **Home search.** All 15 test searches return results.
- **Equipment lookup.** All 142 models open, every tab works and no errors appear.
- **Charge sheet.** 376 input combinations were run: none gave a blank result or NaN. The Fit TEST/FULL targets match 3P761829-1B p.31. DH9VS and the 60k units correctly show no FULL target.
- **Airflow.** 1642 table values match the manuals.
- **Spec tables.** 834 values match their spec sheets.
- **Fault charts.** These match the manual text: DR80TC, the Fit troubleshooting tables, DFVE/DMVT network, CoreSense and the A2L LED codes. CoreSense timings and lockout counts match RSD6200301.
- **Compressor tab.** Every number and code was found in SiUS612209EB / SiUS612412E.
- **DIP switches:**
  - The R-410A DS-1 to DS-6 table matches SiUS612209EB p.35.
  - The R-32 DS1/DS7 termination combinations match 3P761829-1B p.47.
  - The emergency mode timings (8/8 and 7/15 min; 95 °F / 70 °F compressor speed) match SiUS612209EB p.33.
  - The 1st–7th heater kit switch patterns match IOD-4039B p.15 and IOD-4054 p.17.
- **Links.** 46 of 48 work. The other 2 are on backend.daikincomfort.com, which this audit environment couldn't reach, so they weren't tested.

## Fixed

| # | Problem | Fix |
|---|---|---|
| 1 | Clicking a Home search result left the Home results showing above the page you went to. | The results now show only on the Home page. They are still there when you go back to Home. |
| 2 | DR96TC/DR92SN chart: "integrated c o n t r o l m o d u le ." | Now reads "control module." |
| 3 | DR96TC chart: "Induced drati blower" (3 places). IOD-2044 p.51 prints "draft". | Changed to "draft". |
| 4 | DR96TC chart: "Furnacefailstooperate IntegratedcontrolmoduleLED displayprovidesEEderrorcode" (and the same for EEF). | Words separated. |
| 5 | DR80SN chart: "Lorem ipsum" in the EE7 row. | Kept, because Daikin prints it in IOD-2039C p.30. A note now marks it as a manual misprint. |
| 6 | Two console errors (net::ERR_INVALID_URL). A small background image was cut off when it was embedded: its data holds the text "[... ELLIPSIZATION ...]". It never loaded in any version, and no intact copy exists in either repo's history. | Removed the broken image layer and kept the color gradient. The page looks the same as before, without the errors. |
| 7 | 115V DFVE card: "Daikin's fix is S9–S12 all OFF and heating emergency mode OFF (IOD-4055)". IOD-4055 p.20 (Eb) actually says set "Backup Defrost heat" to "always OFF" (outdoor setting) and S9–S12 all OFF. | Rewritten to match the manual. |
| 8 | The heater kit sizes table lists 36k–60k models without 3 kW. Daikin's DFVE/DMVE tables (IOD-4039B p.15, IOD-4054 p.17) print the first valid kit as "3/5". | Your table values are left as you gave them. A note under the table points to the manual's "3/5". |

## Also included

- PR #7's cards, rebuilt on this build:
  - DFVE IOD-4054 pp.22-23 chart.
  - DMVT IOD-4053 pp.31-34 chart.
  - Goodman RS6612301 codes and menu.
  - The four RSD6200301 field checks.

## Left as is

- The Compressor Check tab scrolls inside its own box, which is how GPT built it. Its layout is fine in this build, and the main search now finds it.
- IOD-4054 citation "p.17" for the "Do not change any other dip switches" line: in this copy of the manual the line is on p.16 and the table is on p.17. The manual revision may differ, so it was not changed.
