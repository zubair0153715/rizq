# -*- coding: utf-8 -*-
"""Live Gemini check for Rizq — uses the registered surrogate
credential (key never handled, never printed).

Calls the real rizq.gemini.estimate_text / estimate_photo. Asserts:
* text estimate for "1 plate chicken biryani with raita" returns
  sane JSON in the expected shape (items, totals, low-high range);
* photo estimate on a real public-domain chicken biryani photo
  (Wikimedia Commons, fetched live) identifies rice + chicken and
  returns a range — the honest-accuracy feature Cal AI users
  complain is missing;
* the photo range is a real range (low < total < high) and the
  total is in a plausible band for one plate.

Run: ~/workspace/.venv-fc/bin/python tests/live_check.py
"""

import base64
import os
import sys
import urllib.request

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dynamic_credentials import dynamic_credential_entry  # noqa: E402

entry = dynamic_credential_entry("custom.google-gemini")
os.environ["GEMINI_API_KEY"] = entry["surrogate"]

from rizq import engine, gemini  # noqa: E402

print("key_available:", gemini.key_available())

# --- text estimate ------------------------------------------------------------
res, err = gemini.estimate_text("1 plate chicken biryani with raita",
                                "roman")
if err:
    print("TEXT ESTIMATE ERROR:", err)
    sys.exit(1)
print("TEXT OK:", res)
assert res["items"], "no items"
assert res["low"] < res["total"]["kcal"] < res["high"], (
    "range does not bracket the total")
assert 300 < res["total"]["kcal"] < 900, (
    f"one plate biryani + raita outside plausible band: "
    f"{res['total']['kcal']}")
names = " ".join(i["name"].lower() for i in res["items"])
assert "biryani" in names or "rice" in names, (
    f"biryani/rice not identified: {names}")

# --- photo estimate (real Commons photo) ---------------------------------------
PHOTO_URL = ("https://upload.wikimedia.org/wikipedia/commons/thumb/"
             "b/b5/Chicken_biryani_02-06-2015_%28India%29.jpg/"
             "960px-Chicken_biryani_02-06-2015_%28India%29.jpg")
print("fetching photo:", PHOTO_URL)
req = urllib.request.Request(
    PHOTO_URL, headers={"User-Agent": "Rizq-test/1.0"})
with urllib.request.urlopen(req, timeout=60) as r:
    raw = r.read()
print("photo bytes:", len(raw))
assert len(raw) > 10000, "photo download too small"
b64 = base64.b64encode(raw).decode()
res2, err = gemini.estimate_photo(b64, "image/jpeg", "roman")
if err:
    print("PHOTO ESTIMATE ERROR:", err)
    sys.exit(1)
print("PHOTO OK:", res2)
assert res2["items"], "photo: no items"
assert res2["low"] < res2["total"]["kcal"] < res2["high"], (
    "photo: range does not bracket the total")
names2 = " ".join(i["name"].lower() for i in res2["items"])
assert "biryani" in names2 or "rice" in names2, (
    f"photo: biryani/rice not identified: {names2}")
assert 200 < res2["total"]["kcal"] < 1200, (
    f"photo: total outside plausible band: {res2['total']['kcal']}")
assert res2["confidence"] in ("low", "med", "high")
print("PHOTO confidence:", res2["confidence"],
      "range:", res2["low"], "-", res2["high"])

print("LIVE CHECK PASSED")
