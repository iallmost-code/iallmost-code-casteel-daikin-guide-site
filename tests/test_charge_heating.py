import os
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class HeatingTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.p=sync_playwright().start();cls.b=cls.p.chromium.launch(**({'executable_path':os.environ['GUIDE_TEST_BROWSER']} if os.environ.get('GUIDE_TEST_BROWSER') else {}))
 @classmethod
 def tearDownClass(cls):cls.b.close();cls.p.stop()
 def setUp(self):
  self.page=self.b.new_page();self.page.set_default_timeout(2500);self.errors=[];self.page.on('pageerror',lambda e:self.errors.append(str(e)));self.page.goto((ROOT/'index.html').as_uri());self.page.locator('#field-nav label[for=page-charge]').click();self.page.locator('#q-ref [data-r="32"]').click();self.page.locator('#q-unit').select_option('DH4SE');self.page.locator('#q-tons').select_option('3')
 def tearDown(self):self.page.close();self.assertEqual(self.errors,[])
 def test_mode_selection_required(self):
  self.page.locator('#q-od').fill('65');self.assertIn('Select operating mode',self.page.locator('#q-out').inner_text())
 def test_screenshot_does_not_recommend_recovery_in_heating(self):
  self.page.locator('#q-operation').select_option('heat')
  for id,v in [('q-od','65'),('q-sp','155'),('q-st','180')]:self.page.locator('#'+id).fill(v)
  out=self.page.locator('#q-out').inner_text();self.assertIn('true suction',out.lower());self.assertNotIn('remove refrigerant',out);self.assertNotIn('HIGH charge',out)
  self.assertTrue(self.page.locator('#q-lp').is_disabled())
  self.page.locator('#q-heating-location').check();out=self.page.locator('#q-out').inner_text();self.assertIn('127',out);self.assertIn('8',out);self.assertNotIn('remove refrigerant',out);self.assertNotIn('HIGH charge',out)
 def test_heating_reference_in_range_is_not_charge_certification(self):
  self.page.locator('#q-operation').select_option('heat');self.page.locator('#q-heating-location').check()
  self.page.locator('#q-sp').fill('155');self.page.locator('#q-st').fill('61')
  out=self.page.locator('#q-out').inner_text();self.assertIn('8 °F',out);self.assertIn('within reference',out);self.assertIn('by weight',out);self.assertNotIn('Charge looks RIGHT',out)
 def test_cooling_still_uses_cooling_table(self):
  self.page.locator('#q-operation').select_option('cool')
  for id,v in [('q-od','65'),('q-ls','100'),('q-lt','92')]:self.page.locator('#'+id).fill(v)
  self.assertIn('Charge looks RIGHT',self.page.locator('#q-out').inner_text())
 def test_mode_change_clears_old_readings(self):
  self.page.locator('#q-operation').select_option('cool');self.page.locator('#q-lt').fill('20');self.page.locator('#q-st').fill('180');self.page.locator('#q-operation').select_option('heat');self.assertEqual(self.page.locator('#q-st').input_value(),'');self.assertEqual(self.page.locator('#q-lt').input_value(),'')
 def test_other_platform_does_not_borrow_dh4se_target(self):
  self.page.locator('#q-operation').select_option('heat');self.page.locator('#q-unit').select_option('DH6VS');out=self.page.locator('#q-out').inner_text();self.assertIn('No verified heating target',out);self.assertNotIn('8 ± 1',out)
 def test_ac_only_unit_cannot_get_heating_verdict(self):
  self.page.locator('#q-operation').select_option('heat');self.page.locator('#q-unit').select_option('DC9VS');self.assertIn('AC-only',self.page.locator('#q-out').inner_text())
