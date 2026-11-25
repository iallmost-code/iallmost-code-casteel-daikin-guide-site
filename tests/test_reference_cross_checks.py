from pathlib import Path
import unittest

from playwright.sync_api import expect, sync_playwright


class ReferenceCrossChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.browser.new_page(viewport={"width": 1440, "height": 1000})
        self.page.set_default_timeout(3000)
        self.page.goto((Path(__file__).resolve().parents[1] / "index.html").as_uri())

    def tearDown(self):
        self.page.close()

    def nav(self, page):
        self.page.locator(f'#field-nav label[for="page-{page}"]').click()

    def weigh_in(self, model, tons, length):
        self.nav("charge")
        self.page.locator('#q-ref [data-r="32"]').click()
        self.page.locator("#q-unit").select_option(model)
        self.page.locator("#q-tons").select_option(tons)
        self.page.locator("#q-line summary").click()
        self.page.locator("#q-len").fill(str(length))
        return self.page.locator("#q-line-out")

    def test_fit_actual_length_and_nameplate_difference(self):
        result = self.weigh_in("DH6VS", "2", 25)
        expect(self.page.get_by_label("Actual line length", exact=False)).to_be_visible()
        expect(result).to_contain_text("Total charge (A): 76 oz")
        expect(result).not_to_contain_text("Add 3 oz")
        self.page.locator("#q-factory").fill("74")
        expect(result).to_contain_text("Nameplate-based adjustment: 2 oz")

    def test_fit_hp_only_entry_blocks_ac_weight(self):
        result = self.weigh_in("DC6VSA", "2", 15)
        self.page.locator("#q-pipe").select_option("2")
        expect(result).to_contain_text("HP only")
        expect(result).not_to_contain_text("Total charge (A)")

    def test_se_long_line_requires_long_line_guide(self):
        result = self.weigh_in("DH4SE", "3", 80)
        expect(result).to_contain_text("TP-110")
        expect(result).not_to_contain_text("Additional:")

    def test_large_fit_conflicting_limits_blocks_generic_result(self):
        result = self.weigh_in("DH9VS", "5", 110)
        expect(result).to_contain_text("100 ft")
        expect(result).not_to_contain_text("Total charge (A)")

    def test_compressor_summary_preserves_r32_uncertainty(self):
        self.nav("compressor")
        frame = self.page.frame_locator(".compressor-viewer")
        frame.locator('[data-k="plain"].tab').click()
        card = frame.locator("#pane-plain details").filter(has_text="Does it pump?")
        card.locator("summary").click()
        expect(card).to_contain_text("might be faulty")

    def test_home_search_finds_compressor_check(self):
        self.page.locator("#global-search").fill("compressor check")
        self.page.locator('[data-chip="sec-compressor"]').click()
        self.page.locator('[data-sid="sec-compressor"].start-hit').click()
        expect(self.page.locator(".compressor-viewer")).to_be_visible()

    def test_zoning_search_selects_named_board_despite_cross_references(self):
        self.nav("zoning")
        self.page.locator('[data-zoning-tab="zoning-ut3000"]').click()
        self.page.locator("#global-search").fill("DOZP")
        expect(self.page.locator('[data-zoning-tab="zoning-dozp"]')).to_have_attribute("aria-selected", "true")
        self.page.locator("#global-search").fill("UT3000")
        expect(self.page.locator('[data-zoning-tab="zoning-ut3000"]')).to_have_attribute("aria-selected", "true")

    def test_r410_fit_uses_printed_actual_length_and_nameplate(self):
        self.nav("charge")
        self.page.locator("#q-unit").select_option("DX6VSA")
        self.page.locator("#q-tons").select_option("2.0")
        self.page.locator("#q-line summary").click()
        expect(self.page.get_by_label("Actual line length", exact=False)).to_be_visible()
        self.page.locator("#q-len").fill("25")
        self.page.locator("#q-factory").fill("75")
        result = self.page.locator("#q-line-out")
        expect(result).to_contain_text("Total charge (A): 78 oz")
        expect(result).to_contain_text("Nameplate-based adjustment: 3 oz")

    def test_own_txv_does_not_show_fit_charge_mode_instructions(self):
        self.nav("charge")
        self.page.locator("#q-unit").select_option("OWN")
        self.page.locator("#q-operation").select_option("cool")
        self.page.locator("summary").filter(has_text="How to take the readings").click()
        expect(self.page.locator("#q-rules")).to_contain_text("exact outdoor unit manual")
        expect(self.page.locator("#q-rules")).not_to_contain_text("CHARGE MODE")

    def test_r410_dx6vsa_does_not_inherit_larger_ac_sizes(self):
        self.nav("charge")
        self.page.locator("#q-unit").select_option("DX6VSS")
        self.page.locator("#q-tons").select_option("5.0")
        self.page.locator("#q-unit").select_option("DX6VSA")
        self.assertEqual(
            self.page.locator("#q-tons option").evaluate_all("(options) => options.map(option => option.value)"),
            ["1.5", "2.0", "2.5", "3.0"],
        )
