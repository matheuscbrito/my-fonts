"""Render specimen/readme-card.html to docs/senna-display.png with headless Chrome."""
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SRC = os.path.join(ROOT, "specimen", "readme-card.html")
OUT = os.path.join(ROOT, "docs", "senna-display.png")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
subprocess.run([
    CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
    "--allow-file-access-from-files", "--force-device-scale-factor=2",
    "--window-size=1600,900", "--virtual-time-budget=2000",
    "--screenshot=" + OUT, "file://" + SRC,
], check=True, stderr=subprocess.DEVNULL)
print(OUT)
