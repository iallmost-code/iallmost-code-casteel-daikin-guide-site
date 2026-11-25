"""Browser regression tests. Run: python -m unittest discover -s tests -v."""
import functools
import http.server
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import threading
import unittest

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class GuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = tempfile.TemporaryDirectory()
        cls.site = Path(cls.workspace.name)
        for name in ['index.html', 'sw.js', 'manifest.webmanifest']:
            shutil.copy2(ROOT / name, cls.site / name)
        shutil.copytree(ROOT / 'icons', cls.site / 'icons')
        handler = functools.partial(QuietHandler, directory=str(cls.site))
        cls.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}/'
        cls.playwright = sync_playwright().start()
        options = {'headless': True}
        if os.environ.get('GUIDE_TEST_BROWSER'):
            options['executable_path'] = os.environ['GUIDE_TEST_BROWSER']
        cls.browser = cls.playwright.chromium.launch(**options)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.workspace.cleanup()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 1440, 'height': 900})
        self.page = self.context.new_page()
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.goto(self.url)

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def navigate(self, destination):
        # Equipment tab: Model lookup, Equipment info, Known gaps and Sources share one top-level tab.
        # The AHRI matchup page is hidden on purpose; its catalog data stays in the file.
        if destination in ('page-catalog', 'page-gaps', 'page-sources'):
            self.page.locator('#field-nav label[for="page-models"]').click()
            self.page.locator(f'main .eq-subnav label[for="{destination}"]:visible').click()
        elif destination == 'page-dip':
            # DIP switches is a sub-tab of the Diagnostics tab.
            self.page.locator('#field-nav label[for="page-fault"]').click()
            self.page.locator('main .eq-subnav label[for="page-dip"]:visible').click()
        else:
            self.page.locator(f'#field-nav label[for="{destination}"]').click()

    def search(self, query):
        self.page.locator('#global-search').fill(query)

    def test_real_model_suggestions_and_dip_shortcut(self):
        self.search('DX6VS')
        names = self.page.locator('#model-suggestions button strong').all_text_contents()
        self.assertIn('DX6VS', names)
        self.assertTrue(all(name.startswith('DX6VS') for name in names))
        self.search('DC4SQA6010')
        self.assertIn('DC4SQA6010A', self.page.locator('#model-suggestions button strong').all_text_contents())
        self.search('DC9VSA2410')
        self.assertEqual(self.page.locator('#model-suggestions button strong').all_text_contents(), ['DC9VSA2410A'])
        self.page.locator('#model-suggestions button').click()
        self.page.locator('[data-model-topic="dip"]').click()
        self.page.wait_for_function("document.querySelector('#sec-dip .section-search').value==='DC9VS'")
        self.assertEqual(self.page.locator('.page-radio:checked').get_attribute('id'), 'page-dip')
        self.assertEqual(self.page.locator('#sec-dip .section-search-count').inner_text(), '1 match')

    def test_search_controls_and_topic_state(self):
        self.navigate('page-fault')
        self.search('termination')
        self.navigate('page-dip')
        self.navigate('page-fault')
        self.assertEqual(self.page.locator('#global-search').input_value(), 'termination')
        self.assertEqual(self.page.locator('#sec-fault-codes .section-search-count').inner_text(), '6 matches')  # the Goodman RS6612301 chart also mentions flue termination
        self.page.locator('#sec-fault-codes .topic-tab').first.click()
        self.assertEqual(self.page.locator('#global-search').input_value(), '')
        self.assertEqual(self.page.locator('#sec-fault-codes .section-search').input_value(), '')
        self.page.locator('#search-options').click()
        self.assertEqual(self.page.evaluate('document.activeElement.id'), 'global-search')
        for destination in ['page-start', 'page-dip', 'page-models']:
            self.navigate(destination)
            self.page.keyboard.press('Control+k')
            self.assertEqual(self.page.evaluate('document.activeElement.id'), 'global-search')
            self.page.keyboard.press('Meta+k')
            self.assertEqual(self.page.evaluate('document.activeElement.id'), 'global-search')
        self.navigate('page-start')
        self.page.locator('.start-btn[data-q="furnace"]').click()
        self.assertEqual(self.page.locator('#global-search').input_value(), 'furnace')

    def test_model_lookup_and_hidden_ahri(self):
        self.navigate('page-models')
        self.search('DC9VSA2410A')
        self.page.wait_for_timeout(250)
        self.assertIn('DC9VSA2410A', self.page.locator('#eu-model-name').inner_text())
        # AHRI matchup screens are hidden by choice; the catalog data is kept.
        self.assertEqual(self.page.locator('label[for="page-ahri"]:visible').count(), 0)
        self.assertGreater(self.page.evaluate('window.daikinAhriCatalog.length'), 1000)

    def test_offline_reload_and_manifest(self):
        self.page.evaluate('navigator.serviceWorker.ready')
        self.page.wait_for_function('navigator.serviceWorker.controller!==null')
        manifest = json.loads((self.site / 'manifest.webmanifest').read_text())
        self.assertEqual(manifest['display'], 'standalone')
        session = self.context.new_cdp_session(self.page)
        self.assertEqual(session.send('Page.getAppManifest')['errors'], [])
        keys = self.page.evaluate("caches.keys().then(async keys=>{const cache=await caches.open(keys.find(key=>key.startsWith('daikin-guide-')));return (await cache.keys()).map(request=>new URL(request.url).pathname)})")
        self.assertEqual(set(keys), {'/index.html', '/manifest.webmanifest', '/icons/guide-192.png', '/icons/guide-512.png'})
        self.context.set_offline(True)
        self.page.reload()
        self.navigate('page-models')
        self.search('DC9VSA2410A')
        self.page.wait_for_timeout(250)
        self.assertIn('DC9VSA2410A', self.page.locator('#eu-model-name').inner_text())
        self.navigate('page-start')
        self.search('DX6VS')
        self.assertGreater(self.page.locator('#start-results .start-hit').count(), 0)
        self.assertEqual(self.page.locator(".ref-card").count(), 149)

    def test_pc_pages_fit(self):
        for width in [1024, 1280, 1440, 1920]:
            self.page.set_viewport_size({'width': width, 'height': 900})
            for destination in ['page-start', 'page-fault', 'page-dip', 'page-air', 'page-charge', 'page-zoning', 'page-catalog', 'page-models', 'page-gaps', 'page-sources']:
                self.navigate(destination)
                self.assertFalse(self.page.evaluate('document.documentElement.scrollWidth>innerWidth'), (width, destination))

    def test_charge_sheet(self):
        page = self.page
        page.locator('#field-nav label[for="page-charge"]').click()
        page.select_option('#q-unit', 'DX6VSA')
        page.select_option('#q-tons', '2.0')
        page.select_option('#q-operation', 'cool')
        page.fill('#q-od', '80')
        page.fill('#q-lp', '300')  # 96 F from the manual's R-410A table
        page.fill('#q-lt', '84')
        page.fill('#q-ss', '40')
        page.fill('#q-st', '50')
        out = page.locator('#q-out').inner_text()
        self.assertIn('Subcooling within target', out)
        self.assertIn('Subcooling: 12', out)
        self.assertIn('Superheat: 10', out)
        page.fill('#q-lt', '90')
        self.assertIn('Subcooling below target', page.locator('#q-out').inner_text())
        page.locator('#q-line summary').click()
        page.select_option('#q-ind', 'CAPEA')
        page.select_option('#q-pipe', label='3/8" liquid x 3/4" suction')
        page.fill('#q-len', '52')  # linear approximation between the 50 and 55 ft rows
        self.assertIn('99.2 oz', page.locator('#q-line-out').inner_text())
        page.locator('#q-ref button[data-r="32"]').click()
        page.select_option('#q-unit', 'DH7TC')
        page.fill('#q-od', '80')
        self.assertIn('No charging data', page.locator('#q-out').inner_text())

    def test_r32_manual_tables(self):
        page = self.page
        page.locator('#field-nav label[for="page-charge"]').click()
        page.locator('#q-ref button[data-r="32"]').click()
        # DC6VSA only comes in 1.5 to 3 ton; its 3-ton target is 13 (3P761829-1B p31)
        page.select_option('#q-unit', 'DC6VSA')
        self.assertEqual(page.eval_on_selector_all('#q-tons option', 'o=>o.map(x=>x.value)'), ['1.5', '2', '2.5', '3'])
        page.select_option('#q-tons', '3')
        page.select_option('#q-operation', 'cool')
        page.select_option('#q-fit-procedure', 'full')
        page.fill('#q-od', '90')
        page.fill('#q-lp', '335')  # 102 F from the manual's R-32 table
        page.fill('#q-lt', '89')
        out = page.locator('#q-out').inner_text()
        self.assertIn('Subcooling: 13', out)
        self.assertIn('Full-capacity charging table (FULL): 13 ± 1 °F → in range', out)
        self.assertIn('3P761829-1B p. 31', page.locator('#q-hint').inner_text())
        # SE superheat by tonnage (IOD-4047A p11)
        page.select_option('#q-unit', 'DH4SE')
        page.select_option('#q-tons', '2.5')
        page.fill('#q-od', '80')  # liquid line 86 F can't be below outdoor air in cooling
        page.fill('#q-lp', '300')
        page.fill('#q-lt', '86')
        page.fill('#q-sp', '120')
        page.fill('#q-st', '57')
        self.assertIn('2.5 ton: 17 ± 1 °F (IOD-4047A p. 11) → in range', page.locator('#q-out').inner_text())
        # Fit line set table (3P761829-1B p27)
        page.select_option('#q-unit', 'DH6VS')
        page.select_option('#q-tons', '2')
        page.locator('#q-line summary').click()
        page.select_option('#q-pipe', label='3/8" liquid x 3/4" suction')
        page.fill('#q-len', '50')
        line = page.locator('#q-line-out').inner_text()
        self.assertIn('Total charge (A): 97 oz', line)
        self.assertIn('Additional charge listed in table (C): 24 oz', line)

    def test_charge_impossible_readings_and_heating_mode(self):
        page = self.page
        page.locator('#field-nav label[for="page-charge"]').click()
        page.locator('#q-ref button[data-r="32"]').click()
        # The field report: DH4SE 3 ton, 65 F outdoor, suction 155 / 180, liquid 600 / 20
        page.select_option('#q-unit', 'DH4SE')
        page.select_option('#q-tons', '3')
        page.select_option('#q-operation', 'cool')
        for field, value in [('#q-od', '65'), ('#q-sp', '155'), ('#q-st', '180'), ('#q-lp', '600'), ('#q-lt', '20')]:
            page.fill(field, value)
        out = page.locator('#q-out').inner_text()
        self.assertIn('Check your readings first', out)
        self.assertNotIn('HIGH charge', out)
        self.assertIn('set Operating mode to Heating', out)
        # Heating: no add/remove verdict
        page.select_option('#q-operation', 'heat')
        for field, value in [('#q-od', '65'), ('#q-sp', '155'), ('#q-st', '180')]:
            page.fill(field, value)
        out = page.locator('#q-out').inner_text()
        self.assertNotIn('HIGH charge', out)
        self.assertNotIn('remove refrigerant', out)
        self.assertIn('true suction', out.lower())
        # DH5SE heating: IOD-4064A p11 prints 8 +/- 1 in the table and 5 +/- 1 in the text
        page.select_option('#q-unit', 'DH5SE')
        page.select_option('#q-tons', '3')
        page.select_option('#q-operation', 'heat')
        page.check('#q-heating-location')
        page.fill('#q-sp', '120')  # 40 F
        page.fill('#q-st', '48')
        out = ' '.join(page.locator('#q-out').inner_text().split())
        self.assertIn('IOD-4064A', out)
        self.assertIn('8 ± 1 °F (within reference)', out)
        self.assertIn('5 ± 1 °F (above reference)', out)
        self.assertIn('matches one printed value but not the other', out)
        self.assertNotIn('remove refrigerant', out)
        page.select_option('#q-tons', '5')
        page.check('#q-heating-location')
        page.fill('#q-sp', '120')
        page.fill('#q-st', '45')
        out = ' '.join(page.locator('#q-out').inner_text().split())
        self.assertIn('two-stage 5-ton', out)
        self.assertIn('5 ± 1 °F (within reference)', out)
        # DC5SE is an air conditioner: no heating check
        page.select_option('#q-unit', 'DC5SE')
        page.select_option('#q-operation', 'heat')
        self.assertIn('AC-only', page.locator('#q-out').inner_text())
        page.select_option('#q-unit', 'DH4SE')
        page.select_option('#q-tons', '3')
        # Believable cooling readings still get a verdict
        page.select_option('#q-operation', 'cool')
        for field, value in [('#q-od', '80'), ('#q-ls', '100'), ('#q-lt', '92')]:
            page.fill(field, value)
        self.assertIn('Subcooling within target', page.locator('#q-out').inner_text())

    def test_new_manual_fault_charts_and_field_checks(self):
        page = self.page
        page.locator('#field-nav label[for="page-fault"]').click()
        cards = page.locator('#sec-fault-codes section.ref-card')
        labels = ' '.join(cards.locator('.fault-platform-label').all_inner_texts())
        for title in ['IOD-4054 p.22-23', 'IOD-4053 p.31-34', 'RS6612301 p.34-37', 'REVERSING VALVE', 'DEFROST CONTROL', 'UNLOADER TEST', 'CRANKCASE HEATER']:
            self.assertIn(title, labels)
        text = ' '.join(cards.all_text_contents())
        self.assertIn('Blower Motor operating in Power, Temp or Speed Limiting conditions', text)  # DFVE b3
        self.assertIn('Low Indoor Airflow (without Electric Heat mode)', text)  # DFVE b9
        self.assertIn('MOTOR LIMITS', text)  # DMVT b3
        self.assertIn('Main blower motor is consuming too much current during inducer pre-purge', text)  # Goodman EbU
        self.assertIn('should close at 31°F ± 3°F', text)  # defrost thermostat
        # the tab search finds them
        self.search('defrost thermostat')
        page.wait_for_timeout(300)
        visible = page.locator('#sec-fault-codes section.ref-card:visible .fault-platform-label').all_inner_texts()
        self.assertTrue(any('DEFROST CONTROL' in v for v in visible), visible)

    def test_saved_release_update_can_activate_offline(self):
        self.page.evaluate('navigator.serviceWorker.ready')
        self.page.wait_for_function('navigator.serviceWorker.controller!==null')
        index = self.site / 'index.html'
        worker = self.site / 'sw.js'
        initial_index, initial_worker = index.read_text(), worker.read_text()
        try:
            index.write_text(initial_index.replace('</head>', '<meta name="test-release" content="updated"></head>', 1))
            worker.write_text(re.sub(r"const CACHE='[^']+'", "const CACHE='daikin-guide-test-update'", initial_worker, count=1))
            self.page.evaluate('navigator.serviceWorker.getRegistration().then(reg=>reg.update())')
            self.page.wait_for_function("!document.querySelector('#update-guide').hidden")
            self.context.set_offline(True)
            self.page.locator('#update-guide').click()
            self.page.wait_for_function("document.querySelector('meta[name=test-release]')?.content==='updated'")
            self.navigate('page-models')
            self.search('DC9VSA2410A')
            self.page.wait_for_timeout(250)
            self.assertIn('DC9VSA2410A', self.page.locator('#eu-model-name').inner_text())
        finally:
            index.write_text(initial_index)
            worker.write_text(initial_worker)


if __name__ == '__main__':
    unittest.main()
