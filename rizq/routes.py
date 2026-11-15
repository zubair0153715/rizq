# -*- coding: utf-8 -*-
"""Rizq routes — free AI nutrition tracker, Pakistan-first
(Cal AI gap build).

Original clean-room build. Not affiliated with Cal AI or
MyFitnessPal. Stateless: nothing is stored server-side; the diary
lives in the user's own browser (localStorage). No account, no
card, no trial, no paywall, no ads.
"""

import json

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, JSONResponse

from . import engine, foods, gemini
from .pages import RIZQ_HTML

router = APIRouter(prefix="/rizq")


def _bad(msg):
    return JSONResponse({"ok": False, "error": msg}, status_code=200)


@router.get("", response_class=HTMLResponse)
def index():
    return RIZQ_HTML


@router.get("/api/ai-status")
def ai_status():
    return {"ai_available": gemini.key_available()}


@router.get("/api/foods")
def list_foods(q: str = "", cat: str = "", veg: int = 0,
               diabetes: int = 0):
    results = engine.search(q, category=cat or None,
                            veg_only=bool(veg),
                            diabetes_only=bool(diabetes))
    return {"ok": True, "count": len(results), "foods": results,
            "categories": foods.CATEGORIES}


@router.get("/api/foods/{fid}")
def one_food(fid: str):
    f = foods.food_by_id(fid)
    if not f:
        return _bad("Khana nahi mila.")
    return {"ok": True, "food": f}


@router.post("/api/targets")
def targets(body: dict):
    result, err = engine.compute_targets(
        body.get("sex"), body.get("age"), body.get("weight_kg"),
        body.get("height_cm"), body.get("activity"), body.get("goal"))
    if err:
        return _bad(err)
    return {"ok": True, "targets": result}


@router.post("/api/estimate")
def estimate(body: dict):
    req, err = engine.validate_estimate_request(body)
    if err:
        return _bad(err)
    lang = body.get("language", "en")
    if req["kind"] == "text":
        result, err = gemini.estimate_text(req["description"], lang)
    else:
        result, err = gemini.estimate_photo(req["image_b64"],
                                            req["mime"], lang)
    if err:
        return _bad(err)
    return {"ok": True, "estimate": result}


@router.get("/api/demo")
def demo():
    entries = engine.demo_day_entries()
    return {"ok": True, "entries": entries,
            "total": engine.diary_totals(entries)}
