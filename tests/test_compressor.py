from pathlib import Path
import unittest

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]


class CompressorCheckTest(unittest.TestCase):
    def test_sidebar_opens_all_four_views_in_downloaded_guide(self):
        with sync_playwright() as playwright, playwright.chromium.launch() as browser:
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto((ROOT / "index.html").as_uri())
            link = page.locator('#field-nav label[for="page-compressor"]')
            self.assertEqual(link.count(), 1, "Compressor Check needs its own sidebar tab")
            link.focus()
            page.keyboard.press("Enter")
            frame = page.frame_locator('iframe[title="Daikin Fit Compressor Check"]')
            expect(frame.locator("#pane-r410a")).to_be_visible(timeout=5000)

            for key in ("r32", "plain", "diff", "r410a"):
                frame.locator(f".tab[data-k={key}]").click()
                expect(frame.locator(f"#pane-{key}")).to_be_visible()
                expect(frame.locator(".pane:visible")).to_have_count(1)

            card = frame.locator("#pane-r410a details").first
            was_open = card.evaluate("(el) => el.open")
            card.locator("summary").click()
            self.assertNotEqual(card.evaluate("(el) => el.open"), was_open)
            page.locator('#field-nav label[for="page-charge"]').click()
            expect(page.locator("#sec-charge")).to_be_visible()
            expect(page.locator("#sec-compressor")).to_be_hidden()
            self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
