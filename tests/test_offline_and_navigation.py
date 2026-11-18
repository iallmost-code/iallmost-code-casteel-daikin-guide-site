from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from threading import Thread
import shutil
import tempfile
import unittest
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  if getattr(self.server,'unavailable',False):
   self.send_error(503,'Offline fallback test');return
  super().do_GET()
class OfficeFlows(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.site=Path(cls.tmp.name)
  for name in ['index.html','sw.js','manifest.webmanifest']:shutil.copy(ROOT/name,cls.site/name)
  shutil.copytree(ROOT/'icons',cls.site/'icons')
  cls.server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(cls.site)))
  cls.thread=Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
  cls.url='http://127.0.0.1:'+str(cls.server.server_port)+'/'
  cls.p=sync_playwright().start();cls.b=cls.p.chromium.launch()
 @classmethod
 def tearDownClass(cls):cls.b.close();cls.p.stop();cls.server.shutdown();cls.server.server_close();cls.tmp.cleanup()
 def setUp(self):
  self.context=self.b.new_context(viewport={'width':1440,'height':1000});self.g=self.context.new_page();self.errors=[];self.g.on('pageerror',lambda e:self.errors.append(str(e)));self.g.set_default_timeout(10000);self.g.goto(self.url)
 def tearDown(self):self.server.unavailable=False;self.context.close();self.assertEqual(self.errors,[])
 def test_all_sidebar_destinations_and_desktop_widths(self):
  for width in [800,1024,1440,1920]:
   self.g.set_viewport_size({'width':width,'height':1000})
   for label in self.g.locator('#field-nav label[for]').all():
    if not label.is_visible():continue
    dest=label.get_attribute('for');label.click();self.assertTrue(self.g.locator('#'+dest).is_checked())
    self.assertGreater(self.g.locator('main .section-block:visible').count(),0,dest)
 def test_header_search_routes_faults_and_clears(self):
  self.g.locator('#global-search').fill('EA1');self.assertGreater(self.g.locator('.start-hit:visible').count(),0)
  self.g.locator('.start-hit[data-sid=sec-fault-codes]:visible').first.click();self.assertTrue(self.g.locator('#sec-fault-codes').is_visible())
  self.g.locator('#global-search').fill('');self.assertEqual(self.g.locator('#sec-fault-codes .section-search').input_value(),'')
 def test_offline_reload_retains_navigation_lookup_and_calculation(self):
  self.g.wait_for_function('navigator.serviceWorker.controller !== null')
  self.assertIn('Saved',self.g.locator('#offline-status').inner_text());self.context.set_offline(True);self.server.unavailable=True;response=self.g.reload();self.assertEqual(response.status,200)
  # Chromium may reset navigator.onLine on a worker navigation. Also deny
  # the origin so this test proves a cached fallback, not a network response.
  self.g.wait_for_function('document.getElementById("offline-status").textContent.includes("Saved") || document.getElementById("offline-status").textContent.includes("saved")')
  self.g.locator('#field-nav label[for=page-models]').click();self.g.locator('#eu-query').fill('AMST36CU1300');self.g.locator('#eu-search button').click();self.assertTrue(self.g.locator('#eu-workspace').is_visible())
  self.g.locator('#field-nav label[for=page-charge]').click();self.g.locator('#q-ref [data-r="32"]').click();self.g.locator('#q-unit').select_option('DH4SE');self.g.locator('#q-operation').select_option('cool')
  for id,value in [('q-od','85'),('q-ls','100'),('q-lt','92')]:self.g.locator('#'+id).fill(value)
  self.assertIn('Subcooling within target',self.g.locator('#q-out').inner_text())
 def test_waiting_update_activates_its_saved_release_offline(self):
  self.g.wait_for_function('navigator.serviceWorker.controller !== null')
  old_html=(self.site/'index.html').read_text();old_sw=(self.site/'sw.js').read_text()
  try:
   (self.site/'index.html').write_text(old_html.replace('</body>','<script>window.__auditRelease="B";</script></body>'))
   import re
   (self.site/'sw.js').write_text(re.sub(r"const CACHE='[^']+';","const CACHE='daikin-guide-audit-release-B';",old_sw))
   self.g.evaluate('async()=>{const r=await navigator.serviceWorker.getRegistration();await r.update()}')
   self.g.wait_for_function('!document.getElementById("update-guide").hidden')
   self.context.set_offline(True)
   self.g.locator('#update-guide').click();self.g.wait_for_function('window.__auditRelease === "B"')
   self.assertEqual(self.g.evaluate('caches.keys()'),['daikin-guide-audit-release-B'])
  finally:
   (self.site/'index.html').write_text(old_html);(self.site/'sw.js').write_text(old_sw)
