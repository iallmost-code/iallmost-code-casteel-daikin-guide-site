import os
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class AirflowTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=sync_playwright().start()
  options={'executable_path':os.environ['GUIDE_TEST_BROWSER']} if os.environ.get('GUIDE_TEST_BROWSER') else {}
  cls.b=cls.p.chromium.launch(**options)
 @classmethod
 def tearDownClass(cls):cls.b.close();cls.p.stop()
 def setUp(self):
  self.page=self.b.new_page(viewport={'width':1440,'height':1000});self.errors=[]
  self.page.set_default_timeout(3000)
  self.page.on('pageerror',lambda e:self.errors.append(str(e)))
  self.page.goto((ROOT/'index.html').as_uri());self.page.locator('#field-nav label[for=page-air]').click()
 def tearDown(self):self.page.close();self.assertEqual(self.errors,[])
 def test_cooling_pressure_tap_and_missing_watts(self):
  self.assertEqual(self.page.locator('#ag-cfm').count(),1,'Guided lookup is missing')
  self.assertEqual(self.page.locator('#ag-cfm').inner_text(),'719')
  self.page.locator('#ag-pressure').select_option('6');self.assertEqual(self.page.locator('#ag-cfm').inner_text(),'678')
  self.page.locator('#ag-pressure').select_option('1');self.assertIn('Not listed',self.page.locator('#ag-detail').inner_text())
  self.page.locator('[data-ag-tap="0"]').click();self.assertEqual(self.page.locator('#ag-cfm').inner_text(),'658')
 def test_manual_model_separation(self):
  self.page.locator('#ag-manual').select_option('2039')
  self.assertEqual(self.page.locator('#ag-model').input_value(),'DR80SN0403AU*')
  self.assertEqual(self.page.locator('#ag-cfm').inner_text(),'771')
  self.page.locator('#ag-mode').select_option('heat');self.assertTrue(self.page.locator('#ag-comparison').is_hidden())
  self.assertIn('not available',self.page.locator('#ag-message').inner_text())
 def test_heating_uses_heating_table_and_marker(self):
  self.page.locator('#ag-mode').select_option('heat')
  self.assertEqual(self.page.locator('#ag-cfm').inner_text(),'554')
  self.assertIn('53',self.page.locator('#ag-detail').inner_text())
  self.page.locator('[data-ag-tap="0"]').click();self.assertIn('not recommended',self.page.locator('#ag-message').inner_text().lower())
 def test_amst_missing_taps_not_filled(self):
  self.page.locator('#ag-family').select_option('amst');self.page.locator('#ag-model').select_option('AMST60DU1300')
  self.assertEqual(self.page.locator('#ag-taps tr').count(),5)
  self.assertIn('T2',self.page.locator('#ag-message').inner_text())
 def test_other_family_and_original_search(self):
  self.page.locator('#ag-family').select_option('communicating')
  self.assertTrue(self.page.locator('#ag-comparison').is_hidden())
  self.page.locator('#ag-open-source').click()
  self.assertTrue(self.page.locator('#ag-references').evaluate('(e)=>e.open'))
  self.assertTrue(self.page.locator('#reference-89').is_visible())
  self.page.locator('#field-nav label[for=page-start]').click();self.page.locator('#global-search').fill('DR80SN0403A')
  self.page.locator('.start-hit[data-sid=sec-air]:visible').first.click()
  self.assertTrue(self.page.locator('#ag-references').evaluate('(e)=>e.open'))
 def test_each_family_opens_correct_visible_reference(self):
  for family,source in [('twostage','reference-84'),('dmvt14','reference-73'),('communicating','reference-89'),('dr9','reference-88'),('comfortnet','reference-54')]:
   self.page.locator('#ag-family').select_option(family);self.page.locator('#ag-open-source').click()
   self.assertTrue(self.page.locator('#'+source).is_visible(),family)
   self.assertTrue(self.page.locator('#'+source).evaluate('(e)=>e.open'),family)
 def test_all_dr80_cooling_cells_match_source_and_heat_unavailable_clears(self):
  for manual,source_models in [('2035',8),('2039',5)]:
   self.page.locator('#ag-manual').select_option(manual)
   models=self.page.locator('#ag-model option').evaluate_all('(es)=>es.map(e=>e.value)')
   self.assertEqual(len(models),source_models)
   for model in models:
    self.page.locator('#ag-model').select_option(model)
    for pressure in range(1,9):
     self.page.locator('#ag-pressure').select_option(str(pressure))
     actual=self.page.locator('#ag-taps tr td:nth-child(2)').all_text_contents()
     self.assertTrue(all('undefined' not in x and 'NaN' not in x for x in actual))
     if manual=='2035':
      index=models.index(model)+92;col=pressure if pressure<=4 else 5+(pressure-5)*2
      expected=self.page.locator('#reference-'+str(index)+' tbody tr').evaluate_all('(rs,col)=>rs.map(r=>r.cells[col].textContent.trim()+" CFM")',col)
      self.assertEqual(actual,expected)
  self.page.locator('#ag-mode').select_option('heat')
  self.assertTrue(self.page.locator('#ag-comparison').is_hidden())
  self.assertEqual(self.page.locator('#ag-cfm').inner_text(),'—')

 def test_p1300_never_uses_p1400_reference(self):
  self.page.locator('#ag-family').select_option('dmvt13')
  self.assertTrue(self.page.locator('#ag-open-source').is_hidden())
  self.assertIn('im-iod-4053.pdf',self.page.locator('#ag-external-source').get_attribute('href'))
 def test_default_source_revealed(self):
  self.page.locator('#ag-open-source').click()
  self.assertTrue(self.page.locator('#reference-92').is_visible())
 def test_model_cautions_stay_visible(self):
  self.page.locator('#ag-model').select_option('DR80SN0805C*')
  self.assertIn('Y1 = F02',self.page.locator('#ag-message').inner_text())
  self.page.locator('#ag-model').select_option('DR80SN1205D*')
  self.assertIn('Y2 = F06',self.page.locator('#ag-message').inner_text())
  self.page.locator('#ag-model').select_option('DR80SN0803B*')
  self.assertIn('242',self.page.locator('#ag-message').inner_text())
