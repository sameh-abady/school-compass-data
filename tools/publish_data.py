#!/usr/bin/env python3
"""Write the live, ENCRYPTED data files for https://sandra-natalie-school.netlify.app into this repo.
payload.json  - the page, AES-GCM encrypted with a key derived from the family password
feed.enc / cal.enc - AES-GCM with a random key, wrapped with RSA-OAEP using datakey.pub.pem
                     (only the Netlify functions hold the private key)
usage: python3 tools/publish_data.py <artifact index.html> <make_ics.py> <password>
Run from anywhere; files are written to the repo root (the parent of tools/)."""
import sys, os, json, base64, subprocess, tempfile, shutil, hmac, hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
src, ics_py, pw = sys.argv[1:4]
here = os.path.dirname(os.path.abspath(__file__)); repo = os.path.dirname(here)
pub = serialization.load_pem_public_key(open(os.path.join(repo, 'datakey.pub.pem'), 'rb').read())
SIGN = hashlib.sha256(('sc-sign:' + pw).encode()).digest()   # only someone with the family password can sign
def enc(b):
    k = AESGCM.generate_key(256); iv = os.urandom(12)
    wk = pub.encrypt(k, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    ct = AESGCM(k).encrypt(iv, b, None)
    sig = hmac.new(SIGN, iv + ct, hashlib.sha256).digest()
    return json.dumps({'v': 2, 'k': base64.b64encode(wk).decode(), 'iv': base64.b64encode(iv).decode(),
                       'ct': base64.b64encode(ct).decode(), 'sig': base64.b64encode(sig).decode()})
tmp = tempfile.mkdtemp()
try:
    site = os.path.join(tmp, 'site'); os.makedirs(site)
    subprocess.run([sys.executable, os.path.join(here, 'build.py'), src, pw, site], check=True)  # also writes <tmp>/netlify/data/feed.json
    subprocess.run([sys.executable, ics_py, src, os.path.join(tmp, 'cal.ics')], check=True)
    shutil.copy(os.path.join(site, 'payload.json'), os.path.join(repo, 'payload.json'))
    open(os.path.join(repo, 'feed.enc'), 'w').write(enc(open(os.path.join(tmp, 'netlify', 'data', 'feed.json'), 'rb').read()))
    open(os.path.join(repo, 'cal.enc'), 'w').write(enc(open(os.path.join(tmp, 'cal.ics'), 'rb').read()))
    print('encrypted data written to', repo)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
