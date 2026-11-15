# Rizq — رزق

**Free AI nutrition tracker, Pakistan-first.** Biryani, nihari, daal,
roti — search in English, Roman-Urdu or Urdu, log by the plate, and
get honest AI photo estimates with a **range + confidence** instead of
one fake-precise number. No account, no card, no trial, no paywall,
**no ads**.

An original clean-room build from the daily-app-gap-build series. It
fills the gaps in **Cal AI** ($30M–$50M/year revenue, 15M+ downloads,
356K ratings, $29.99/year after a 3-day trial — pulled from the App
Store in April 2026 over deceptive billing). Rizq is **not
affiliated** with Cal AI or MyFitnessPal.

## Why Rizq exists

| | Cal AI | Rizq |
|---|---|---|
| Price | $9.99/mo or $29.99/yr after a 3-day trial that auto-converts; Apple pulled it in Apr 2026 over billing design | **Free, forever — no trial, no card, no paywall, no ads** (only limit is the owner's Gemini free quota, stated on the page) |
| AI accuracy | One number, no confidence; mixed/home-cooked dishes are its weak spot; same meal re-scanned gives different calories | **Range + per-item confidence** (low/med/high); user edits any item or portion **before** logging; nothing logged silently |
| Pakistani food | US brands and chains; no biryani, nihari, haleem, daal, roti in usable form; portions in cups and ounces | **Pakistan-first database**: ~59 dishes and staples with portions in local units (1 roti, 1 plate, 1 katori, 1 cup) |
| Language | English only | **Urdu-first**: English, Roman-Urdu and Urdu script search; Urdu food names on every entry |
| Local context | None | **Ramadan mode** (Suhoor/Iftar target split), **diabetes-friendly flags** (glycaemic load per serving), high-protein flags |
| Onboarding | ~20 screens of questions before the price appears | **No questionnaire** — open the page, search or snap a photo, log |

Gap report: `../market-gaps/daily/2026-11-15-rizq.md` (in the builder's workspace).

## The food database

Every value is arithmetic from USDA FoodData Central generic
per-100g values plus a documented standard recipe — no hand-typed
totals, no invented stats. Each dish is a recipe of base
ingredients; `foods.values_for` computes the serving, and the tests
recompute every dish and check the energy equation
(kcal ~= 4P+4C+9F, within 15% — USDA values run ~10% under Atwater
because fibre contributes less energy).

- **Breads:** roti, naan, paratha, aloo paratha
- **Rice:** chicken/beef/Sindhi biryani, chicken pulao, daal chawal
- **Daal & sabzi:** masoor, moong, chana masala, rajma, aloo gobi, bhindi, palak paneer, mix sabzi
- **Meat:** chicken/mutton karahi, chicken curry, nihari, haleem, seekh/shami kebab, chicken tikka, fried fish
- **Breakfast:** anda paratha, halwa puri, doodh patti, sweet/salted lassi, omelette, boiled egg
- **Snacks:** samosa, pakora, chaat, dahi bhalla, gol gappa
- **Sweets:** gulab jamun, jalebi, kheer, gajar halwa
- **Fruit & dairy:** banana, apple, mango, orange, dates, yogurt, milk, almonds, peanuts
- **Fast food:** grilled chicken, salad bowl, zinger-style burger, fries, pizza slice, shawarma

Home recipes vary — more/less oil changes everything — so every
entry shows its source in the app.

## Features

- **Search** — English, Roman-Urdu or Urdu script; filter by category, veg-only, diabetes-friendly (GL ≤ 10).
- **AI photo estimate** — snap or upload a meal; Gemini vision identifies items, estimates grams and macros, returns a low–high range with per-item confidence; edit quantities, then log.
- **AI text estimate** — type a meal ("1 plate chicken biryani with raita") and get the same ranged estimate.
- **Daily diary** — log by meal (or Suhoor/Iftar in Ramadan mode); running totals vs target; streak of days logged; JSON export/import; demo day preloaded.
- **Verified targets** — BMR by Mifflin-St Jeor, TDEE by activity multiplier, goal budget (lose −500 / maintain / gain +300); the formula is shown on the page.
- **Health flags** — glycaemic load per serving, diabetes-friendly flag, high-protein flag.

## Honest limits

- Photo estimates are **estimates, not measurements**: the camera cannot see hidden oil, sugar or salt. Rizq shows a range and a confidence instead of pretending precision — treat the number as a ballpark, and correct the portion before logging.
- Food values are computed from USDA FoodData Central generic values and documented standard recipes; your home recipe will differ.
- BMR/TDEE are population formulas — a starting point, not a medical prescription. Rizq is general nutrition information, never medical advice, never a diagnosis, never a diet prescription. Diabetes, kidney disease, pregnancy or any medical condition: see a doctor or dietitian.
- AI estimates need `GEMINI_API_KEY` in the environment (owner's free quota). Without it, the food database, diary, targets, flags and export/import still work fully.
- Glycaemic load uses published GI values for the closest generic food; mixed dishes are an approximation.

## Observed AI behaviour (live check, 2026-11-15)

Gemini's text estimate for "1 plate chicken biryani with raita"
came back at **750 kcal** (range 525–975) while Rizq's own
database says ~539 kcal for the same plate. The range brackets the
database value — which is exactly why Rizq shows a range and lets
you edit before logging, instead of presenting one number as truth.
The photo estimate on a real biryani photo identified chicken
biryani + cashews + fried onions at 661 kcal (range 463–859),
confidence low, with an explicit note about hidden oil/ghee.

## Run the tests

```bash
~/workspace/.venv-fc/bin/python tests/verify.py      # deterministic, no key — 302 checks
~/workspace/.venv-fc/bin/python tests/live_check.py  # real Gemini calls
```

## Route

Live (after deploy): `https://clinic-demo.fastapicloud.dev/rizq`
