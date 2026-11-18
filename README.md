# Casteel Daikin office guide

Self-contained desktop reference guide served by Render. Open `index.html` directly for a downloaded copy, or serve this directory over HTTP for offline saving and update checks. Manufacturer PDFs require a network connection. AHRI matchup functionality is intentionally hidden; its original data is retained.

## Verify changes

Use Python 3 and Playwright Chromium:

```
python -m pip install playwright
python -m playwright install chromium
python -m unittest discover -s tests -v
```

Run tests serially. Browser suites can exhaust resources if run concurrently. Existing suites support `GUIDE_TEST_BROWSER` for an alternative Chromium executable.

Before deploying an asset change, run `python scripts/prepare_offline.py` and commit the updated `sw.js` with the changed assets. This gives each offline release a separate cache. Render deploys are manual for the existing service.

See `docs/audits/2026-11-17-app-audit.md` for the audit scope, corrections, and outstanding manufacturer-source conflicts.
