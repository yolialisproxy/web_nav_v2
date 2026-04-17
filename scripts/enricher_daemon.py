
import subprocess
import time
import os

while True:
    p = subprocess.Popen(["python3", "scripts/webnav-content-enricher.py", "--input", "data/websites.json", "--output", "data/websites.json"])
    p.wait()
    time.sleep(60)
