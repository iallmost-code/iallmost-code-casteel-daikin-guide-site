from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class AuditRegressions(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.p=sync_playwright().start();cls.b=cls.p.chromium.launch()
 @classmethod
 def tearDownClass(cls):cls.b.close();cls.p.stop()
 def setUp(self):
  self.g=self.b.new_page(viewport={'width':1440,'height':1000});self.g.set_default_timeout(5000);self.errors=[];self.g.on('pageerror',lambda e:self.errors.append(str(e)));self.g.goto((ROOT/'index.html').as_uri())
 def tearDown(self):self.g.close();self.assertEqual(self.errors,[])
 def field(self,id,v,event='input'):self.g.evaluate('([id,v,event])=>{const e=document.getElementById(id);e.value=v;e.dispatchEvent(new Event(event,{bubbles:true}))}',[id,str(v),event])
 def nav(self,id):self.g.locator('#field-nav label[for='+id+']').click()
 def model(self,model):
  self.nav('page-models');self.field('eu-query',model);self.g.locator('#eu-search').evaluate('(e)=>e.dispatchEvent(new Event("submit",{bubbles:true,cancelable:true}))')
 def charge(self,ref='410',model='OWN',tons=None):
  self.nav('page-charge');self.g.locator('#q-ref [data-r="'+ref+'"]').click();self.field('q-unit',model,'change')
  if tons is not None:self.field('q-tons',tons,'change')
  self.field('q-operation','cool','change');self.field('q-od','85')
 def test_specs_ignore_comparison_rows(self):
  self.model('DC4SEA2410A');self.assertIn('MCA',self.g.locator('#eu-specs').inner_text());self.assertNotIn('CATALOG',self.g.locator('#eu-family').inner_text())
 def test_dc6vs_aliases_have_exact_charge_handoff(self):
  for model,target in [('DC6VSS2410A','DC6VSS'),('DC6VSA241WA','DC6VSA'),('DC6VSS4210AA','DC6VSS')]:
   self.model(model);self.g.locator('[data-eu-tab=charging]').click();self.assertTrue(self.g.locator('#eu-open-charge').is_visible(),model);self.g.locator('#eu-open-charge').click();self.assertEqual(self.g.locator('#q-unit').input_value(),target)
 def test_actual_au_model_selects_2039_airflow(self):
  self.model('DR80SN0603AUA');self.g.locator('[data-eu-tab=airflow]').click();self.g.locator('#eu-air-actions button').click();self.assertEqual(self.g.locator('#ag-manual').input_value(),'2039');self.assertEqual(self.g.locator('#ag-model').input_value(),'DR80SN0603AU*')
 def test_ambiguous_model_pattern_has_no_automatic_airflow(self):
  self.model('DR80SN0603A*A');self.g.locator('[data-eu-tab=airflow]').click();self.assertEqual(self.g.locator('#eu-air-actions button').count(),0);self.assertIn('exact',self.g.locator('#eu-air-context').inner_text().lower())
 def test_faults_respect_fit_size(self):
  self.model('DC9VSA2410A');self.g.locator('[data-eu-tab=faults]').click();self.assertNotIn('DH9VS/DH7VS(60)',self.g.locator('#eu-fault-list').inner_text())
  self.model('DH7VSA6010A');self.g.locator('[data-eu-tab=faults]').click();self.assertNotIn('DC9VS(24-48)',self.g.locator('#eu-fault-list').inner_text())
 def test_conflicting_catalog_metadata_not_applied(self):
  self.model('DX4SQA2410A');self.assertIn('conflict',self.g.locator('#eu-status').inner_text().lower());self.assertEqual(self.g.locator('#eu-manual-list a').count(),0)
 def test_submitting_search_does_not_reset_tab_later(self):
  self.model('DC9VSA3610A');self.g.locator('[data-eu-tab=manuals]').click();self.g.wait_for_timeout(250);self.assertTrue(self.g.locator('#eu-panel-manuals').is_visible())
 def test_txv_superheat_alone_does_not_judge_charge(self):
  self.charge();self.field('q-tsh',10);self.field('q-ss',40);self.field('q-st',60);out=self.g.locator('#q-out').inner_text();self.assertNotIn('add refrigerant',out);self.assertIn('subcooling',out.lower())
 def test_negative_tolerance_rejected(self):
  self.charge();self.field('q-tsc',8);self.field('q-ls',100);self.field('q-lt',92);self.field('q-tol',-1);out=self.g.locator('#q-out').inner_text();self.assertIn('tolerance',out.lower());self.assertNotIn('LOW charge',out)
 def test_positive_line_length_required(self):
  for ref,model,tons in [('410','DZ6VSA','2.0'),('32','DC5SE','1.5')]:
   self.charge(ref,model,tons);self.g.locator('#q-line').evaluate('(e)=>e.open=true');self.field('q-len',-20);self.assertIn('positive',self.g.locator('#q-line-out').inner_text().lower())
 def test_unknown_charge_units_not_added_to_ounces(self):
  self.charge('32','DC5SE','1.5');self.g.locator('#q-line').evaluate('(e)=>e.open=true');self.field('q-len',25);out=self.g.locator('#q-line-out').inner_text();self.assertNotIn('Total:',out);self.assertIn('nameplate',out.lower())
 def test_refrigerant_switch_clears_placeholder(self):
  self.charge('32','DH4SE','3');self.field('q-sp',155);self.assertEqual(self.g.locator('#q-ss').get_attribute('placeholder'),'53');self.g.locator('#q-ref [data-r="410"]').click();self.assertEqual(self.g.locator('#q-ss').get_attribute('placeholder'),'')
 def test_model_switch_clears_measurements(self):
  self.charge('32','DH4SE','3');self.field('q-ss',53);self.field('q-st',61);self.field('q-unit','DH5SE','change');self.assertEqual(self.g.locator('#q-ss').input_value(),'');self.assertEqual(self.g.locator('#q-st').input_value(),'')
 def test_fit_uses_selected_procedure_only(self):
  self.charge('32','DC9VS','2');self.assertEqual(self.g.locator('#q-fit-procedure').count(),1)
  self.field('q-fit-procedure','test','change');self.field('q-ls',100);self.field('q-lt',92);self.assertIn('within target',self.g.locator('#q-out').inner_text())
  self.field('q-fit-procedure','full','change');self.field('q-ls',100);self.field('q-lt',92);self.assertIn('below target',self.g.locator('#q-out').inner_text())
 def test_dh5se5_low_stage_target_is_specific(self):
  self.charge('32','DH5SE','5');self.field('q-ls',100);self.field('q-lt',94);out=self.g.locator('#q-out').inner_text();self.assertIn('within target',out);self.assertNotIn('matches some',out)
 def test_airflow_search_does_not_leave_unrelated_cfm(self):
  self.nav('page-start');self.g.locator('#global-search').fill('AMST24BU1300');self.g.locator('.start-hit[data-sid=sec-air]:visible').first.click();self.assertTrue(self.g.locator('#ag-comparison').is_hidden() or self.g.locator('#ag-model').input_value()=='AMST24BU1300')
 def test_missing_airflow_watts_do_not_get_units(self):
  self.nav('page-air');self.field('ag-model','DR80SN1005C*','change');self.field('ag-pressure','6','change');self.g.locator('[data-ag-tap="1"]').click();self.assertIn('Not available',self.g.locator('#ag-detail').inner_text());self.assertNotIn('N/A* W',self.g.locator('#ag-detail').inner_text())
 def test_amst_t9_source_conflict_resolved_by_pdf(self):
  text=self.g.locator('#reference-67').text_content();self.assertNotIn('looks like a copy error',text);self.assertIn('Table 9',text)
 def test_dmvt_conflicting_values_flagged(self):
  self.assertGreater(self.g.locator('#reference-73 .reference-data-warning').count(),0)
 def test_airflow_print_black_text_and_source(self):
  self.nav('page-air');self.g.emulate_media(media='print');self.g.evaluate('window.dispatchEvent(new Event("beforeprint"))');self.assertEqual(self.g.locator('#ag-cfm').evaluate('(e)=>getComputedStyle(e).color'),'rgb(17, 17, 17)');self.assertTrue(self.g.locator('#ag-raw table').is_visible());self.g.evaluate('window.dispatchEvent(new Event("afterprint"))')

 def test_equipment_airflow_clears_prior_reference_search(self):
  self.nav('page-air');self.g.locator('#global-search').fill('DMVT');self.assertTrue(self.g.locator('#airflow-guide').is_hidden())
  self.model('DR80SN0603AUA');self.g.locator('[data-eu-tab=airflow]').click();self.g.locator('#eu-air-actions button').click();self.assertTrue(self.g.locator('#airflow-guide').is_visible());self.assertEqual(self.g.locator('#ag-manual').input_value(),'2039')
 def test_reference_search_print_keeps_results(self):
  self.nav('page-air');self.g.locator('#global-search').fill('DMVT');self.g.emulate_media(media='print');self.g.evaluate('window.dispatchEvent(new Event("beforeprint"))');self.assertTrue(self.g.locator('#reference-73').is_visible());self.g.evaluate('window.dispatchEvent(new Event("afterprint"))')
 def test_fit_below_80_adjustment_is_test_only(self):
  self.charge('32','DC6VSA','2');self.field('q-od',75)
  for procedure,sc in [('test',10),('full',12)]:
   self.field('q-fit-procedure',procedure,'change');self.field('q-ls',100);self.field('q-lt',100-sc);self.assertIn('within target',self.g.locator('#q-out').inner_text())
 def test_airflow_only_amst_model_opens_original_source(self):
  self.model('AMST36CU1300');self.assertNotIn('QminCFM',self.g.locator('#eu-specs').inner_text());self.g.locator('#eu-open-equipment').click();self.assertTrue(self.g.locator('#reference-85').is_visible())
