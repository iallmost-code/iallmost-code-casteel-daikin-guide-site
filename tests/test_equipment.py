import os
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class EquipmentTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.p=sync_playwright().start();cls.b=cls.p.chromium.launch(**({'executable_path':os.environ['GUIDE_TEST_BROWSER']} if os.environ.get('GUIDE_TEST_BROWSER') else {}))
 @classmethod
 def tearDownClass(cls):cls.b.close();cls.p.stop()
 def setUp(self):
  self.page=self.b.new_page(viewport={'width':1440,'height':1000});self.page.set_default_timeout(3000);self.errors=[];self.page.on('pageerror',lambda e:self.errors.append(str(e)));self.page.goto((ROOT/'index.html').as_uri())
 def tearDown(self):self.page.close();self.assertEqual(self.errors,[])
 def open(self):
  self.assertEqual(self.page.locator('#field-nav label[for=page-models]').count(),1,'Unified lookup is missing')
  self.page.locator('#field-nav label[for=page-models]').click()
 def test_model_overview(self):
  self.open();self.assertIn('DC9VSA2410A',self.page.locator('#eu-model-name').inner_text());self.assertIn('22.4',self.page.locator('#eu-specs').inner_text());self.assertIn('76 oz',self.page.locator('#eu-charge-note').inner_text())
 def test_matchups_hidden_but_catalog_preserved(self):
  self.open();self.assertEqual(self.page.locator('[data-eu-tab=ahri]:visible').count(),0)
  self.assertEqual(self.page.locator('label[for=page-ahri]:visible').count(),0)
  self.assertGreater(self.page.evaluate('window.daikinAhriCatalog.length'),1000)
  self.page.evaluate('let r=document.getElementById("page-ahri");r.checked=true;r.dispatchEvent(new Event("change"))')
  self.assertTrue(self.page.locator('#sec-ahri').is_hidden())
  self.assertEqual(self.page.locator('.page-radio:checked').get_attribute('id'),'page-models')
 def test_unknown_and_ambiguous(self):
  self.open();self.page.locator('#eu-query').fill('UNKNOWN');self.page.locator('#eu-search button').click();self.assertTrue(self.page.locator('#eu-workspace').is_hidden());self.assertIn('No model',self.page.locator('#eu-status').inner_text())
  self.page.locator('#eu-query').fill('DC9VS');self.page.locator('#eu-search button').click();self.assertGreater(self.page.locator('#eu-suggestions button').count(),1);self.assertTrue(self.page.locator('#eu-workspace').is_hidden())
 def test_charging_context(self):
  self.open();self.page.locator('[data-eu-tab=charging]').click();self.page.locator('#eu-open-charge').click();self.assertEqual(self.page.locator('.page-radio:checked').get_attribute('id'),'page-charge');self.assertEqual(self.page.locator('#q-unit').input_value(),'DC9VS');self.assertEqual(self.page.locator('#q-tons').input_value(),'2')
 def test_sources_and_ahri_navigation(self):
  self.open();self.page.locator('[data-eu-tab=manuals]').click();self.assertGreater(self.page.locator('#eu-manual-list a').count(),0);self.assertIn('#page=39',self.page.locator('#eu-wiring-link').get_attribute('href'))
  self.page.locator('main label[for=page-sources]:visible').click();self.assertTrue(self.page.locator('#sec-source-documents').is_visible())
 def test_print_summary_omits_matchup_information(self):
  self.open();self.page.evaluate('window.print=()=>{window.printCalled=true}');self.page.locator('#eu-print').click();self.assertTrue(self.page.evaluate('window.printCalled'))
  text=self.page.locator('#equipment-print-sheet').inner_text();self.assertIn('DC9VSA2410A',text);self.assertNotIn('Catalog AHRI',text);self.assertNotIn('SEER2',text)
  self.page.evaluate('window.dispatchEvent(new Event("afterprint"))')

 def test_header_search_changes_model_and_clears_old_data(self):
  self.open();self.page.locator('#global-search').fill('DC9VSA3610A');self.page.wait_for_timeout(250)
  self.assertIn('DC9VSA3610A',self.page.locator('#eu-model-name').inner_text())
  self.page.locator('#global-search').fill('UNRECOGNIZED');self.page.wait_for_timeout(250);self.assertTrue(self.page.locator('#eu-workspace').is_hidden())
 def test_saved_model_variant_does_not_claim_exact_suffix(self):
  self.open();self.page.locator('#eu-query').fill('DC9VSA2410AA');self.page.locator('#eu-search button').click()
  self.assertIn('*',self.page.locator('#eu-model-name').inner_text());self.assertIn('confirm',self.page.locator('#eu-status').inner_text())

 def test_internal_source_wildcard_finds_installed_variant(self):
  self.open();self.page.locator('#eu-query').fill('DR80SN0403AXA');self.page.locator('#eu-search button').click()
  self.assertIn('DR80SN0403A*A',self.page.locator('#eu-model-name').inner_text());self.assertTrue(self.page.locator('#eu-workspace').is_visible())
 def test_catalog_alias_inherits_applicable_source_pattern(self):
  self.open();self.page.locator('#eu-query').fill('DH4SEA1810A');self.page.locator('#eu-search button').click()
  self.assertIn('71',self.page.locator('#eu-specs').inner_text());self.assertIn('DH4SEA1810*',self.page.locator('#eu-spec-pattern').inner_text())
  self.page.locator('[data-eu-tab=charging]').click();self.assertTrue(self.page.locator('#eu-open-charge').is_visible())
  self.page.locator('#eu-query').fill('DH4SEA1810AA');self.page.locator('#eu-search button').click();self.assertTrue(self.page.locator('#eu-workspace').is_visible())
 def test_direct_model_lookup_keeps_header_in_sync(self):
  self.open();self.page.locator('#eu-query').fill('DC9VSA6010A');self.page.locator('#eu-search button').click();self.assertEqual(self.page.locator('#global-search').input_value(),'DC9VSA6010A')
