# -*- coding: utf-8 -*-
"""Rizq deterministic checks — no key, no network.

Covers: food DB arithmetic (every dish recomputes from its recipe;
energy equation kcal ~= 4P+4C+9F within 15% — USDA values run
~10% under Atwater because fibre contributes less energy),
filters, BMR/TDEE hand-checks against worked Mifflin-St Jeor
examples, diary totals, AI-estimate validation, request validation,
demo day, and route smoke via TestClient.

Run: ~/workspace/.venv-fc/bin/python tests/verify.py
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rizq import engine, foods  # noqa: E402

PASS = 0
FAIL = []


def check(name, ok, detail=""):
    global PASS
    if ok:
        PASS += 1
    else:
        FAIL.append(f"{name}: {detail}")


# --- food DB -----------------------------------------------------------------
allf = foods.all_foods()
check("db count >= 50", len(allf) >= 50, str(len(allf)))
ids = [f["id"] for f in allf]
check("db ids unique", len(ids) == len(set(ids)))

for f in allf:
    kcal, protein, carbs, fat, grams, gl = foods.values_for(
        next(x for x in foods.FOODS if x["id"] == f["id"]))
    expect = 4 * protein + 4 * carbs + 9 * fat
    check(f"energy equation {f['id']}",
          abs(kcal - expect) / max(expect, 1) <= 0.15,
          f"kcal={kcal} expect~{expect:.1f}")
    check(f"serving grams > 0 {f['id']}", grams > 0, str(grams))
    check(f"gl recompute {f['id']}",
          abs(gl - f["gi"] * carbs / 100) < 0.15, str(gl))
    check(f"flags consistent {f['id']}",
          f["high_protein"] == (protein >= 15)
          and f["diabetes_friendly"] == (gl <= 10))

# Hand-checks: roti 40 g x 297/100 = 118.8 kcal; biryani recompute.
roti = foods.food_by_id("roti")
check("roti hand calc", roti["kcal"] == 118.8
      and roti["grams"] == 40, str(roti))
biryani = foods.food_by_id("chicken-biryani")
# 180 g rice (234) + 60 g chicken (99) + 15 g oil (132.6)
# + 30 g onion (12) + 15 g tomato (2.7) = 480.3
check("biryani hand calc", abs(biryani["kcal"] - 480.3) < 0.2,
      str(biryani["kcal"]))
check("biryani protein", abs(biryani["protein"] - 23.9) < 0.2,
      str(biryani["protein"]))
check("daal-chawal carbs", abs(
    foods.food_by_id("daal-chawal")["carbs"] - 76.5) < 0.2)
check("doodh-patti kcal", abs(
    foods.food_by_id("doodh-patti")["kcal"] - 122.5) < 0.2)

# --- search ------------------------------------------------------------------
check("search en", any(f["id"] == "chicken-biryani"
                       for f in engine.search("biryani")))
check("search roman", any(f["id"] == "daal-masoor"
                          for f in engine.search("daal")))
check("search urdu", any(f["id"] == "roti"
                         for f in engine.search("روٹی")))
check("search empty = all", len(engine.search("")) == len(allf))
check("search no match", engine.search("zzzzqq") == [])
check("filter veg", all(f["veg"] for f in engine.search("", veg_only=True))
      and any(not f["veg"] for f in allf))
check("filter diabetes", all(f["diabetes_friendly"]
                             for f in engine.search("", diabetes_only=True)))
check("filter category", all(f["cat"] == "sweets"
                             for f in engine.search("", category="sweets"))
      and len(engine.search("", category="sweets")) == 4)

# --- targets (Mifflin-St Jeor hand-checks) ------------------------------------
# Male 70 kg / 175 cm / 25 y: 10*70 + 6.25*175 - 5*25 + 5 = 1673.75
t, err = engine.compute_targets("male", 25, 70, 175, "moderate", "maintain")
check("bmr male hand calc", err is None and t["bmr"] == 1674, str(t))
check("tdee male moderate", err is None and t["tdee"] == 2594,
      str(t))  # 1673.75 * 1.55 = 2594.3
check("target maintain = tdee", t["target_kcal"] == t["tdee"])
check("protein target 1.2g/kg", t["protein_target"] == 84, str(t))
t2, _ = engine.compute_targets("male", 25, 70, 175, "moderate", "lose")
check("target lose -500", t2["target_kcal"] == 2094, str(t2))
t3, _ = engine.compute_targets("male", 25, 70, 175, "moderate", "gain")
check("target gain +300", t3["target_kcal"] == 2894, str(t3))
# Female 60 kg / 160 cm / 25 y: 600 + 1000 - 125 - 161 = 1314
t4, err = engine.compute_targets("female", 25, 60, 160, "sedentary",
                                 "maintain")
check("bmr female hand calc", err is None and t4["bmr"] == 1314,
      str(t4))
check("tdee female sedentary", t4["tdee"] == 1577, str(t4))  # 1314*1.2
check("targets bad sex", engine.compute_targets(
    "other", 25, 70, 175, "moderate", "maintain")[1] is not None)
check("targets bad age", engine.compute_targets(
    "male", 5, 70, 175, "moderate", "maintain")[1] is not None)
check("targets bad weight", engine.compute_targets(
    "male", 25, 500, 175, "moderate", "maintain")[1] is not None)
check("targets bad activity", engine.compute_targets(
    "male", 25, 70, 175, "marathon", "maintain")[1] is not None)
check("targets bad goal", engine.compute_targets(
    "male", 25, 70, 175, "moderate", "bulk")[1] is not None)
check("targets formula shown", "Mifflin-St Jeor" in t["formula"])

# --- diary totals --------------------------------------------------------------
tot = engine.diary_totals([
    {"kcal": 100, "protein": 10, "carbs": 20, "fat": 5},
    {"kcal": 200.5, "protein": 5, "carbs": 10, "fat": 2.5},
])
check("diary totals", tot == {"kcal": 300.5, "protein": 15.0,
                              "carbs": 30.0, "fat": 7.5, "count": 2},
      str(tot))
check("diary empty", engine.diary_totals([])["count"] == 0)
check("diary bad values skipped",
      engine.diary_totals([{"kcal": "oops"}])["kcal"] == 0)

# --- AI estimate validation ----------------------------------------------------
good = {"items": [
    {"name": "Chicken Biryani", "grams": 300, "kcal": 480,
     "protein": 24, "carbs": 54, "fat": 18, "confidence": "med"},
    {"name": "Raita", "grams": 100, "kcal": 59, "protein": 3.5,
     "carbs": 4.7, "fat": 3.3, "confidence": "high"},
], "note": "oil uncertain"}
res, err = engine.validate_ai_estimate(good)
check("ai good passes", err is None and res is not None, str(err))
check("ai total recompute", res["total"]["kcal"] == 539.0
      and res["total"]["count"] == 2, str(res["total"]))
check("ai range med", res["low"] == round(539 * 0.85)
      and res["high"] == round(539 * 1.15)
      and res["confidence"] == "med", str((res["low"], res["high"])))
low_conf = {"items": [{"name": "Mixed curry", "grams": 250,
                       "kcal": 400, "protein": 20, "carbs": 30,
                       "fat": 22, "confidence": "low"}]}
res2, _ = engine.validate_ai_estimate(low_conf)
check("ai range low widens", res2["low"] == round(400 * 0.70)
      and res2["high"] == round(400 * 1.30), str(res2))
high_conf = {"items": [{"name": "Boiled egg", "grams": 50,
                        "kcal": 78, "protein": 6.3, "carbs": 0.6,
                        "fat": 5.3, "confidence": "high"}]}
res3, _ = engine.validate_ai_estimate(high_conf)
check("ai range high narrow", res3["low"] == round(78 * 0.92)
      and res3["high"] == round(78 * 1.08), str(res3))
bad_energy = {"items": [{"name": "Rice", "grams": 200, "kcal": 900,
                         "protein": 5, "carbs": 40, "fat": 2,
                         "confidence": "high"}]}
res4, _ = engine.validate_ai_estimate(bad_energy)
check("ai bad energy downgraded not dropped",
      res4 is not None and res4["items"][0]["confidence"] == "low",
      str(res4))
check("ai empty items rejected",
      engine.validate_ai_estimate({"items": []})[1] is not None)
check("ai missing items rejected",
      engine.validate_ai_estimate({})[1] is not None)
check("ai too many items rejected",
      engine.validate_ai_estimate(
          {"items": [{"name": f"i{i}", "grams": 10, "kcal": 10,
                      "protein": 1, "carbs": 1, "fat": 0.5,
                      "confidence": "high"} for i in range(9)]})[1]
      is not None)
check("ai long name rejected",
      engine.validate_ai_estimate(
          {"items": [{"name": "x" * 81, "grams": 10, "kcal": 10,
                      "protein": 1, "carbs": 1, "fat": 0.5,
                      "confidence": "high"}]})[1] is not None)
check("ai not dict rejected",
      engine.validate_ai_estimate("nope")[1] is not None)

# --- estimate request validation ----------------------------------------------
req, err = engine.validate_estimate_request(
    {"kind": "text", "description": "1 plate biryani"})
check("req text ok", err is None and req["kind"] == "text", str(err))
check("req text empty rejected", engine.validate_estimate_request(
    {"kind": "text", "description": "  "})[1] is not None)
check("req text too long rejected", engine.validate_estimate_request(
    {"kind": "text", "description": "x" * 501})[1] is not None)
check("req photo bad mime rejected", engine.validate_estimate_request(
    {"kind": "photo", "image_b64": "aGVsbG8=", "mime": "image/gif"})[1]
    is not None)
check("req photo ok", engine.validate_estimate_request(
    {"kind": "photo", "image_b64": "aGVsbG8=",
     "mime": "image/jpeg"})[1] is None)
check("req bad kind rejected", engine.validate_estimate_request(
    {"kind": "video"})[1] is not None)

# --- demo day -------------------------------------------------------------------
demo = engine.demo_day_entries()
check("demo day 6 entries", len(demo) == 6, str(len(demo)))
dtot = engine.diary_totals(demo)
check("demo day total sane", 1200 < dtot["kcal"] < 1800, str(dtot))
check("demo day meals", {e["meal"] for e in demo}
      <= {"breakfast", "lunch", "dinner", "snacks"})

# --- routes (TestClient) ---------------------------------------------------------
try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from rizq.routes import router  # noqa: E402

    app = FastAPI()
    app.include_router(router)
    c = TestClient(app)

    r = c.get("/rizq")
    check("route /rizq 200", r.status_code == 200
          and "Rizq" in r.text, str(r.status_code))
    check("route /rizq honest limits", "GEMINI_API_KEY" in r.text)
    check("route /rizq no fake claims", "100% accurate" not in r.text
          and "guaranteed" not in r.text.lower())
    r = c.get("/rizq/api/ai-status")
    check("route ai-status no key", r.status_code == 200
          and r.json()["ai_available"] is False, r.text[:120])
    r = c.get("/rizq/api/foods")
    check("route foods >= 50", r.status_code == 200
          and r.json()["count"] >= 50, r.text[:200])
    r = c.get("/rizq/api/foods", params={"q": "biryani"})
    check("route foods search", r.json()["count"] >= 3
          and all("biryani" in f["roman"] for f in r.json()["foods"]),
          r.text[:200])
    r = c.get("/rizq/api/foods", params={"diabetes": 1})
    check("route foods diabetes filter",
          all(f["diabetes_friendly"] for f in r.json()["foods"]))
    r = c.get("/rizq/api/foods/roti")
    check("route one food", r.json()["food"]["kcal"] == 118.8,
          r.text[:200])
    r = c.get("/rizq/api/foods/nope")
    check("route one food missing", r.json().get("ok") is False)
    r = c.post("/rizq/api/targets", json={
        "sex": "male", "age": 25, "weight_kg": 70, "height_cm": 175,
        "activity": "moderate", "goal": "maintain"})
    check("route targets", r.json().get("ok")
          and r.json()["targets"]["bmr"] == 1674, r.text[:200])
    r = c.post("/rizq/api/targets", json={
        "sex": "male", "age": 25, "weight_kg": 70, "height_cm": 175,
        "activity": "moderate", "goal": "bulk"})
    check("route targets bad goal", r.json().get("ok") is False)
    r = c.post("/rizq/api/estimate", json={
        "kind": "text", "description": "1 plate chicken biryani"})
    check("route estimate no key honest error", r.status_code == 200
          and r.json().get("ok") is False
          and "GEMINI_API_KEY" in r.json().get("error", ""),
          r.text[:200])
    r = c.post("/rizq/api/estimate", json={"kind": "text",
                                           "description": ""})
    check("route estimate empty rejected", r.json().get("ok") is False)
    r = c.get("/rizq/api/demo")
    check("route demo", r.status_code == 200 and r.json().get("ok")
          and len(r.json()["entries"]) == 6, r.text[:200])
except Exception as exc:  # noqa: BLE001 - report as failures
    check("routes import/run", False, repr(exc))

print(f"\n{PASS} passed, {len(FAIL)} failed")
for f in FAIL:
    print("FAIL:", f)
sys.exit(1 if FAIL else 0)
