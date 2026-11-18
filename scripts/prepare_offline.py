"""Stamp the worker cache after any public guide asset changes. No dependencies."""
from pathlib import Path
import hashlib
import re
ROOT = Path(__file__).resolve().parents[1]
assets = ['index.html', 'manifest.webmanifest', 'icons/guide-192.png', 'icons/guide-512.png']
hash = hashlib.sha256()
p = ROOT / 'sw.js'
worker = p.read_text()
hash.update(re.sub(r"const CACHE='[^']+';", "const CACHE='RELEASE';", worker).encode())
for name in assets:
    hash.update(name.encode())
    hash.update((ROOT / name).read_bytes())
text, count = re.subn(r"const CACHE='daikin-guide-[^']+';", "const CACHE='daikin-guide-" + hash.hexdigest()[:16] + "';", worker)
assert count == 1
p.write_text(text)
print('Offline cache:', hash.hexdigest()[:16])
