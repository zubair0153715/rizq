# -*- coding: utf-8 -*-
"""Rizq AI layer — photo and text meal estimates via Gemini.

Same call pattern as the other gap builds (Kirdar/Daftar/Poda):
urllib, key read from the environment AT CALL TIME only, never
stored or logged. Every AI JSON is validated by engine before it
reaches the page.

The honest-accuracy rule, wired into the prompt and the engine:
* the model returns a per-item breakdown with a confidence
  (high/med/low) per item — never one bare number;
* the engine recomputes totals and a low–high range from the
  worst confidence, and checks kcal ~= 4P+4C+9F per item;
* the user edits any item or portion BEFORE it is logged.

Without a key, estimates are unavailable; the food database,
diary, targets, flags and export/import still work fully.
"""

import json
import os
import urllib.error
import urllib.request

from . import engine

MODEL = "gemini-2.5-flash"
TIMEOUT = 120


def _get_key():
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_APIkey")


def key_available():
    return bool(_get_key())


def _call(parts, max_tokens=3000, temperature=0.3):
    """One Gemini generateContent call. parts = list of part dicts.
    Returns (text, error)."""
    key = _get_key()
    if not key:
        return None, ("AI ke liye GEMINI_API_KEY set nahi hai. Food "
                      "database, diary, targets aur flags phir bhi "
                      "poore kaam karte hain.")
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           f"{MODEL}:generateContent?key={key}")
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": temperature,
                             "maxOutputTokens": max_tokens},
    }
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            return None, "AI quota khatam (429). Thodi der baad dobara try karein."
        return None, f"AI error (HTTP {e.code}). Dobara try karein."
    except Exception as exc:  # network, timeout, bad JSON
        return None, f"AI se rabta nahi hua ({exc}). Dobara try karein."
    try:
        return body["candidates"][0]["content"]["parts"][0]["text"].strip(), None
    except (KeyError, IndexError, TypeError):
        return None, "AI ne khaali jawab diya. Dobara try karein."


def _parse_json(raw):
    text = (raw or "").strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1] if "\n" in text else ""
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]
    try:
        data = json.loads(text.strip())
    except (json.JSONDecodeError, ValueError):
        return None, "AI ka jawab JSON nahi tha. Dobara try karein."
    if not isinstance(data, dict):
        return None, "AI ka jawab samajh nahi aaya."
    return data, None


ESTIMATE_SCHEMA = """Reply with ONLY a JSON object, no markdown, no
extra text:
{"items": [{"name": "item name in English", "grams": 0,
"kcal": 0, "protein": 0, "carbs": 0, "fat": 0,
"confidence": "high" | "med" | "low"}],
"note": "one short line about what is uncertain, e.g. hidden oil"}
Rules: identify every distinct food on the plate. Estimate grams
from a normal serving. Calories must satisfy kcal ~= 4*protein +
4*carbs + 9*fat. Confidence is "high" only for plain, clearly
visible foods (rice, roti, egg, fruit); mixed dishes, curries,
fried food and anything with hidden oil or sauce is "med" or
"low". Never invent a brand. If you cannot identify the food at
all, return {"items": [], "note": "could not identify"}."""


def estimate_text(description, language="en"):
    """Estimate a typed meal description. Returns (result, error)."""
    if language not in engine.LANGUAGES:
        return None, "Language ghalat hai — English, Roman-Urdu ya Urdu chunein."
    desc = (description or "").strip()
    if not desc:
        return None, "Khana likhein — masalan '1 plate chicken biryani'."
    if len(desc) > engine.MAX_DESCRIPTION:
        return None, "Description 500 harf se chhoti rakhein."
    prompt = ("You are a nutrition estimator for Pakistani and "
              "international food. Estimate this meal, in grams and "
              "macros, as eaten. Pakistani portions: 1 plate biryani "
              "~300 g, 1 roti ~40 g, 1 katori daal ~200 g, 1 cup chai "
              "~200 ml. Be honest about uncertainty.\n\nMEAL: "
              f"{desc}\n\n{ESTIMATE_SCHEMA}")
    raw, err = _call([{"text": prompt}], max_tokens=2500, temperature=0.3)
    if err:
        return None, err
    data, err = _parse_json(raw)
    if err:
        return None, err
    if not data.get("items"):
        return None, ("AI khana pehchan nahi saka. Food database mein "
                      "search karke manual log karein.")
    return engine.validate_ai_estimate(data)


def estimate_photo(image_b64, mime, language="en"):
    """Estimate a meal photo. Returns (result, error)."""
    if language not in engine.LANGUAGES:
        return None, "Language ghalat hai."
    if not image_b64 or mime not in ("image/jpeg", "image/png",
                                     "image/webp"):
        return None, "Photo JPEG, PNG ya WebP honi chahiye."
    prompt = ("You are a nutrition estimator. Look at this meal photo "
              "and estimate every distinct food on the plate, in grams "
              "and macros, as eaten. Pakistani portions: 1 plate "
              "biryani ~300 g, 1 roti ~40 g, 1 katori daal ~200 g. "
              "You cannot see hidden oil, sugar or salt — say so in "
              "the note and use med/low confidence where it applies. "
              "Be honest about uncertainty.\n\n"
              f"{ESTIMATE_SCHEMA}")
    parts = [{"text": prompt},
             {"inline_data": {"mime_type": mime, "data": image_b64}}]
    raw, err = _call(parts, max_tokens=2500, temperature=0.3)
    if err:
        return None, err
    data, err = _parse_json(raw)
    if err:
        return None, err
    if not data.get("items"):
        return None, ("AI photo mein khana pehchan nahi saka. Food "
                      "database mein search karke manual log karein.")
    return engine.validate_ai_estimate(data)
