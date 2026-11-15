# -*- coding: utf-8 -*-
"""Rizq engine — search, targets (Mifflin-St Jeor), diary totals,
AI-estimate validation. Pure logic, no network, no key.

Targets use the Mifflin-St Jeor equation (the formula dietitians
actually use):
  men:   BMR = 10*weight_kg + 6.25*height_cm - 5*age + 5
  women: BMR = 10*weight_kg + 6.25*height_cm - 5*age - 161
TDEE = BMR * activity multiplier. Goal budget: lose -500, maintain
0, gain +300 kcal/day. Protein target 1.2 g/kg/day (a general
starting point, not a prescription).

AI estimates are never trusted blindly: the model returns a range
and a confidence, and the engine checks the energy equation
(kcal ~= 4P+4C+9F) on every item before anything is shown.
"""

from . import foods

LANGUAGES = {"en": "English", "roman": "Roman-Urdu", "ur": "Urdu script"}

ACTIVITY = {
    "sedentary": 1.2,    # little or no exercise
    "light": 1.375,      # light exercise 1-3 days/week
    "moderate": 1.55,    # moderate exercise 3-5 days/week
    "active": 1.725,     # hard exercise 6-7 days/week
    "athlete": 1.9,      # very hard exercise, physical job
}

GOALS = {"lose": -500, "maintain": 0, "gain": 300}

MEALS = ["breakfast", "lunch", "dinner", "snacks"]
RAMADAN_MEALS = ["suhoor", "iftar"]

MAX_DESCRIPTION = 500
MAX_IMAGE_B64 = 8 * 1024 * 1024  # ~6 MB image
MAX_AI_ITEMS = 8

# Confidence -> half-width of the calorie range, as a fraction.
CONFIDENCE_SPREAD = {"high": 0.08, "med": 0.15, "low": 0.30}


def search(query, category=None, veg_only=False, diabetes_only=False):
    """Substring search over English, Roman-Urdu and Urdu names."""
    q = (query or "").strip().lower()
    out = []
    for f in foods.all_foods():
        if category and f["cat"] != category:
            continue
        if veg_only and not f["veg"]:
            continue
        if diabetes_only and not f["diabetes_friendly"]:
            continue
        if q and q not in f["en"].lower() and q not in f["roman"].lower() \
                and q not in f["ur"]:
            continue
        out.append(f)
    return out


def compute_targets(sex, age, weight_kg, height_cm, activity, goal):
    """Returns (targets, error). Targets: bmr, tdee, target kcal,
    protein target, and the formula shown to the user."""
    if sex not in ("male", "female"):
        return None, "Sex male ya female chunein."
    try:
        age = float(age)
        weight_kg = float(weight_kg)
        height_cm = float(height_cm)
    except (TypeError, ValueError):
        return None, "Age, weight aur height number mein likhein."
    if not (10 <= age <= 100):
        return None, "Age 10–100 ke darmiyan honi chahiye."
    if not (30 <= weight_kg <= 300):
        return None, "Weight 30–300 kg ke darmiyan hona chahiye."
    if not (120 <= height_cm <= 230):
        return None, "Height 120–230 cm ke darmiyan honi chahiye."
    if activity not in ACTIVITY:
        return None, "Activity level chunein."
    if goal not in GOALS:
        return None, "Goal chunein: lose, maintain ya gain."
    bmr = (10 * weight_kg + 6.25 * height_cm - 5 * age
           + (5 if sex == "male" else -161))
    tdee = bmr * ACTIVITY[activity]
    target = tdee + GOALS[goal]
    protein = 1.2 * weight_kg
    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
        "target_kcal": round(target),
        "protein_target": round(protein),
        "formula": ("Mifflin-St Jeor: BMR = 10 x weight + 6.25 x height "
                    "- 5 x age + 5 (male) / -161 (female); "
                    f"TDEE = BMR x {ACTIVITY[activity]} ({activity}); "
                    f"goal {goal} ({GOALS[goal]:+d} kcal/day)"),
    }, None


def diary_totals(entries):
    """Sum a list of diary entries {kcal, protein, carbs, fat}."""
    total = {"kcal": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0,
             "count": 0}
    for e in entries or []:
        for k in ("kcal", "protein", "carbs", "fat"):
            try:
                total[k] += float(e.get(k, 0) or 0)
            except (TypeError, ValueError):
                continue
        total["count"] += 1
    for k in ("kcal", "protein", "carbs", "fat"):
        total[k] = round(total[k], 1)
    return total


def _energy_ok(kcal, protein, carbs, fat, tol=0.20):
    """Energy equation check: kcal within tol of 4P+4C+9F."""
    expect = 4 * protein + 4 * carbs + 9 * fat
    if expect <= 0:
        return False
    return abs(kcal - expect) / expect <= tol


def validate_ai_estimate(data):
    """Validate the model's estimate JSON. Returns (clean, error).
    Clean shape: {"items": [{name, grams, kcal, protein, carbs,
    fat, confidence}], "total": {...}, "low": n, "high": n,
    "note": str} — totals recomputed here, never trusted."""
    if not isinstance(data, dict):
        return None, "AI ka jawab samajh nahi aaya."
    items = data.get("items")
    if not isinstance(items, list) or not items:
        return None, "AI ne khane ki koi cheez pehchani nahi."
    if len(items) > MAX_AI_ITEMS:
        return None, "AI ne bohat zyada items diye."
    clean_items = []
    for it in items:
        if not isinstance(it, dict):
            return None, "AI ka jawab samajh nahi aaya."
        name = str(it.get("name", "")).strip()
        if not name or len(name) > 80:
            return None, "AI ke item ka naam ghalat hai."
        try:
            grams = float(it.get("grams", 0))
            kcal = float(it.get("kcal", 0))
            protein = float(it.get("protein", 0))
            carbs = float(it.get("carbs", 0))
            fat = float(it.get("fat", 0))
        except (TypeError, ValueError):
            return None, "AI ke numbers samajh nahi aaye."
        if not (0 < grams <= 2000 and 0 < kcal <= 3000
                and 0 <= protein <= 200 and 0 <= carbs <= 400
                and 0 <= fat <= 200):
            return None, f"'{name}' ke numbers had se bahar hain."
        conf = str(it.get("confidence", "low")).lower()
        if conf not in CONFIDENCE_SPREAD:
            conf = "low"
        if not _energy_ok(kcal, protein, carbs, fat):
            # Macros contradict the calories — keep the calories
            # (the headline number) but mark it low confidence.
            conf = "low"
        clean_items.append({
            "name": name, "grams": round(grams), "kcal": round(kcal, 1),
            "protein": round(protein, 1), "carbs": round(carbs, 1),
            "fat": round(fat, 1), "confidence": conf,
        })
    total = diary_totals(clean_items)
    # Range: widen by the worst (least confident) item's spread.
    worst = max(CONFIDENCE_SPREAD[i["confidence"]] for i in clean_items)
    low = round(total["kcal"] * (1 - worst))
    high = round(total["kcal"] * (1 + worst))
    note = str(data.get("note", "")).strip()[:300]
    return {
        "items": clean_items,
        "total": total,
        "low": low,
        "high": high,
        "confidence": "low" if worst >= 0.30 else (
            "med" if worst >= 0.15 else "high"),
        "note": note,
    }, None


def validate_estimate_request(body):
    """Check a /api/estimate body: text description or image."""
    if not isinstance(body, dict):
        return None, "Request samajh nahi aaya."
    kind = body.get("kind")
    if kind == "text":
        desc = str(body.get("description", "")).strip()
        if not desc:
            return None, "Khana likhein — masalan '1 plate chicken biryani'."
        if len(desc) > MAX_DESCRIPTION:
            return None, "Description 500 harf se chhoti rakhein."
        return {"kind": "text", "description": desc}, None
    if kind == "photo":
        b64 = body.get("image_b64", "")
        mime = str(body.get("mime", "")).strip().lower()
        if not isinstance(b64, str) or not b64:
            return None, "Photo upload karein."
        if len(b64) > MAX_IMAGE_B64:
            return None, "Photo bohat bari hai (max ~6 MB)."
        if mime not in ("image/jpeg", "image/png", "image/webp"):
            return None, "Photo JPEG, PNG ya WebP honi chahiye."
        return {"kind": "photo", "image_b64": b64, "mime": mime}, None
    return None, "kind 'text' ya 'photo' hona chahiye."


DEMO_DAY = {
    "date": "demo",
    "entries": [
        {"meal": "breakfast", "food_id": "anda-paratha",
         "label": "Anda Paratha (1 set)", "qty": 1},
        {"meal": "breakfast", "food_id": "doodh-patti",
         "label": "Doodh Patti (1 cup)", "qty": 1},
        {"meal": "lunch", "food_id": "chicken-biryani",
         "label": "Chicken Biryani (1 plate)", "qty": 1},
        {"meal": "lunch", "food_id": "yogurt-plain",
         "label": "Plain Yogurt (1 cup)", "qty": 1},
        {"meal": "dinner", "food_id": "daal-masoor",
         "label": "Daal Masoor (1 katori)", "qty": 1},
        {"meal": "dinner", "food_id": "roti",
         "label": "Roti (1 roti)", "qty": 2},
    ],
}


def demo_day_entries():
    """Demo day with computed values, so the diary works with no key."""
    out = []
    for e in DEMO_DAY["entries"]:
        f = foods.food_by_id(e["food_id"])
        if not f:
            continue
        q = e["qty"]
        out.append({
            "meal": e["meal"], "food_id": e["food_id"],
            "label": e["label"], "qty": q,
            "kcal": round(f["kcal"] * q, 1),
            "protein": round(f["protein"] * q, 1),
            "carbs": round(f["carbs"] * q, 1),
            "fat": round(f["fat"] * q, 1),
        })
    return out
