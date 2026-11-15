# -*- coding: utf-8 -*-
"""Rizq food database — Pakistan-first.

Every number in this file is arithmetic, not a guess:
* BASE holds per-100g values (kcal, protein, carbs, fat) for generic
  ingredients, taken from USDA FoodData Central generic entries,
  rounded to one decimal. GI is the published glycaemic index of
  the closest generic food (Atkinson et al., Diabetes Care 2008
  tables; 0 = negligible carbs, GI not applicable).
* Each FOOD is a recipe: grams of BASE ingredients that make one
  serving. Serving values are computed by `values_for` — no
  hand-typed totals anywhere, so tests can recompute every dish
  from its recipe and check the energy equation
  kcal ~= 4*protein + 4*carbs + 9*fat.
* Serving sizes are standard Pakistani portions (1 roti ~40 g,
  1 plate ~300 g, 1 katori ~200 g, 1 cup ~200 ml). Home recipes
  vary — more/less oil changes everything — so the app labels
  every value with its source.

Fries note: the recipe uses 25 g absorbed oil per 100 g because
frying drives water out and oil in; plain boiled potato (87
kcal/100 g) would understate a fried product badly.
"""

# base_id -> (kcal, protein_g, carbs_g, fat_g) per 100 g, and GI
BASE = {
    "rice_white": (130, 2.7, 28.2, 0.3, 73),
    "rice_brown": (123, 2.6, 25.6, 1.0, 68),
    "roti_ww": (297, 9.7, 49.0, 3.4, 62),
    "naan": (310, 9.0, 56.0, 5.6, 70),
    "paratha": (330, 7.0, 45.0, 13.0, 65),
    "daal_masoor": (116, 9.0, 20.1, 0.4, 30),
    "daal_moong": (105, 7.0, 19.0, 0.4, 30),
    "chana": (164, 8.9, 27.4, 2.6, 28),
    "rajma": (132, 8.9, 22.8, 0.5, 28),
    "chicken": (165, 31.0, 0.0, 3.6, 0),
    "mutton": (250, 25.0, 0.0, 16.0, 0),
    "beef": (250, 26.0, 0.0, 15.0, 0),
    "fish": (120, 22.0, 0.0, 3.0, 0),
    "egg": (155, 12.6, 1.1, 10.6, 0),
    "milk": (61, 3.2, 4.8, 3.3, 31),
    "yogurt": (59, 3.5, 4.7, 3.3, 15),
    "paneer": (265, 18.3, 3.6, 20.8, 0),
    "cheese": (402, 25.0, 1.3, 33.0, 0),
    "ghee": (900, 0.0, 0.0, 99.6, 0),
    "oil": (884, 0.0, 0.0, 100.0, 0),
    "potato": (87, 1.9, 20.1, 0.1, 78),
    "okra": (35, 2.0, 7.0, 0.2, 0),
    "spinach": (23, 3.0, 3.6, 0.4, 0),
    "cauliflower": (23, 1.8, 4.0, 0.3, 0),
    "carrot": (41, 0.9, 9.6, 0.2, 39),
    "onion": (40, 1.1, 9.3, 0.1, 0),
    "tomato": (18, 0.9, 3.9, 0.2, 0),
    "veg_mix": (30, 1.5, 6.0, 0.2, 0),
    "peas": (81, 5.4, 14.5, 0.4, 48),
    "banana": (89, 1.1, 22.8, 0.3, 51),
    "apple": (52, 0.3, 13.8, 0.2, 36),
    "mango": (60, 0.8, 15.0, 0.4, 51),
    "orange": (47, 0.9, 11.8, 0.1, 43),
    "dates": (282, 1.8, 75.0, 0.2, 47),
    "almonds": (579, 21.2, 21.6, 49.9, 0),
    "peanuts": (567, 25.8, 16.1, 49.2, 14),
    "sugar": (387, 0.0, 99.8, 0.0, 65),
    "flour_ww": (340, 13.2, 72.0, 2.5, 70),
    "bun_white": (290, 9.0, 50.0, 5.0, 75),
    "mayo": (680, 1.0, 1.0, 75.0, 0),
}

# Food entry: id, names, category, serving label, GI of the dish,
# vegetarian flag, recipe = [(base_id, grams), ...] summing to the
# serving weight. Dish GI is the published GI of the closest generic
# dish (rice dishes ~70, daal ~30, fried snacks ~65).
# name_ur is Urdu script; name_roman is Roman-Urdu search text.
FOODS = [
    # --- breads ---
    {"id": "roti", "en": "Roti / Chapati", "roman": "roti chapati",
     "ur": "روٹی", "cat": "bread", "serving": "1 roti", "gi": 62,
     "veg": True, "recipe": [("roti_ww", 40)]},
    {"id": "naan", "en": "Naan", "roman": "naan",
     "ur": "نان", "cat": "bread", "serving": "1 naan", "gi": 70,
     "veg": True, "recipe": [("naan", 90)]},
    {"id": "paratha", "en": "Paratha", "roman": "paratha",
     "ur": "پراٹھا", "cat": "bread", "serving": "1 paratha", "gi": 65,
     "veg": True, "recipe": [("paratha", 80)]},
    {"id": "aloo-paratha", "en": "Aloo Paratha", "roman": "aloo paratha",
     "ur": "آلو پراٹھا", "cat": "bread", "serving": "1 paratha", "gi": 68,
     "veg": True, "recipe": [("paratha", 70), ("potato", 50)]},
    # --- rice ---
    {"id": "chicken-biryani", "en": "Chicken Biryani",
     "roman": "chicken biryani", "ur": "چکن بریانی", "cat": "rice",
     "serving": "1 plate", "gi": 70, "veg": False,
     "recipe": [("rice_white", 180), ("chicken", 60), ("oil", 15),
                ("onion", 30), ("tomato", 15)]},
    {"id": "beef-biryani", "en": "Beef Biryani", "roman": "beef biryani",
     "ur": "بیف بریانی", "cat": "rice", "serving": "1 plate", "gi": 70,
     "veg": False,
     "recipe": [("rice_white", 180), ("beef", 60), ("oil", 15),
                ("onion", 30), ("tomato", 15)]},
    {"id": "sindhi-biryani", "en": "Sindhi Biryani",
     "roman": "sindhi biryani", "ur": "سندھی بریانی", "cat": "rice",
     "serving": "1 plate", "gi": 71, "veg": False,
     "recipe": [("rice_white", 170), ("chicken", 60), ("potato", 30),
                ("oil", 15), ("onion", 15), ("tomato", 10)]},
    {"id": "chicken-pulao", "en": "Chicken Pulao",
     "roman": "chicken pulao", "ur": "چکن پلاؤ", "cat": "rice",
     "serving": "1 plate", "gi": 70, "veg": False,
     "recipe": [("rice_white", 190), ("chicken", 55), ("oil", 12),
                ("onion", 25), ("tomato", 10), ("peas", 8)]},
    {"id": "daal-chawal", "en": "Daal Chawal", "roman": "daal chawal",
     "ur": "دال چاول", "cat": "rice", "serving": "1 plate", "gi": 62,
     "veg": True,
     "recipe": [("rice_white", 200), ("daal_masoor", 100)]},
    {"id": "white-rice", "en": "White Rice (cooked)",
     "roman": "white rice chawal", "ur": "سفید چاول", "cat": "rice",
     "serving": "1 cup cooked", "gi": 73, "veg": True,
     "recipe": [("rice_white", 158)]},
    {"id": "brown-rice", "en": "Brown Rice (cooked)",
     "roman": "brown rice", "ur": "براؤن چاول", "cat": "rice",
     "serving": "1 cup cooked", "gi": 68, "veg": True,
     "recipe": [("rice_brown", 195)]},
    # --- daal / sabzi (1 katori = 200 g) ---
    {"id": "daal-masoor", "en": "Daal Masoor", "roman": "daal masoor",
     "ur": "دال مسور", "cat": "daal-sabzi", "serving": "1 katori",
     "gi": 30, "veg": True,
     "recipe": [("daal_masoor", 190), ("oil", 5), ("onion", 5)]},
    {"id": "daal-moong", "en": "Daal Moong", "roman": "daal moong",
     "ur": "دال مونگ", "cat": "daal-sabzi", "serving": "1 katori",
     "gi": 30, "veg": True,
     "recipe": [("daal_moong", 190), ("oil", 5), ("onion", 5)]},
    {"id": "chana-masala", "en": "Chana Masala", "roman": "chana masala",
     "ur": "چنا مصالحہ", "cat": "daal-sabzi", "serving": "1 katori",
     "gi": 28, "veg": True,
     "recipe": [("chana", 170), ("oil", 8), ("onion", 15),
                ("tomato", 7)]},
    {"id": "rajma", "en": "Rajma (Kidney Beans)", "roman": "rajma lobia",
     "ur": "راجما", "cat": "daal-sabzi", "serving": "1 katori",
     "gi": 28, "veg": True,
     "recipe": [("rajma", 180), ("oil", 5), ("onion", 10),
                ("tomato", 5)]},
    {"id": "aloo-gobi", "en": "Aloo Gobi", "roman": "aloo gobi",
     "ur": "آلو گوبھی", "cat": "daal-sabzi", "serving": "1 katori",
     "gi": 65, "veg": True,
     "recipe": [("potato", 120), ("cauliflower", 60), ("oil", 10),
                ("onion", 10)]},
    {"id": "bhindi", "en": "Bhindi (Okra)", "roman": "bhindi okra",
     "ur": "بھنڈی", "cat": "daal-sabzi", "serving": "1 katori",
     "gi": 0, "veg": True,
     "recipe": [("okra", 170), ("oil", 10), ("onion", 20)]},
    {"id": "palak-paneer", "en": "Palak Paneer", "roman": "palak paneer",
     "ur": "پالک پنیر", "cat": "daal-sabzi", "serving": "1 katori",
     "gi": 0, "veg": True,
     "recipe": [("spinach", 120), ("paneer", 60), ("oil", 8),
                ("onion", 12)]},
    {"id": "mix-sabzi", "en": "Mix Sabzi", "roman": "mix sabzi",
     "ur": "مکس سبزی", "cat": "daal-sabzi", "serving": "1 katori",
     "gi": 0, "veg": True,
     "recipe": [("veg_mix", 170), ("oil", 8), ("onion", 15),
                ("tomato", 7)]},
    # --- meat ---
    {"id": "chicken-karahi", "en": "Chicken Karahi",
     "roman": "chicken karahi", "ur": "چکن کڑاہی", "cat": "meat",
     "serving": "1 serving", "gi": 0, "veg": False,
     "recipe": [("chicken", 140), ("oil", 15), ("tomato", 30),
                ("onion", 15)]},
    {"id": "chicken-curry", "en": "Chicken Curry (Shorba)",
     "roman": "chicken curry shorba", "ur": "چکن سالن", "cat": "meat",
     "serving": "1 serving", "gi": 0, "veg": False,
     "recipe": [("chicken", 120), ("oil", 10), ("onion", 30),
                ("tomato", 30), ("yogurt", 10)]},
    {"id": "mutton-karahi", "en": "Mutton Karahi",
     "roman": "mutton karahi gosht", "ur": "مٹن کڑاہی", "cat": "meat",
     "serving": "1 serving", "gi": 0, "veg": False,
     "recipe": [("mutton", 140), ("oil", 15), ("tomato", 30),
                ("onion", 15)]},
    {"id": "nihari", "en": "Nihari", "roman": "nihari",
     "ur": "نہاری", "cat": "meat", "serving": "1 plate", "gi": 45,
     "veg": False,
     "recipe": [("beef", 130), ("oil", 12), ("onion", 20),
                ("flour_ww", 15), ("tomato", 10), ("veg_mix", 63)]},
    {"id": "haleem", "en": "Haleem", "roman": "haleem",
     "ur": "حلیم", "cat": "meat", "serving": "1 bowl", "gi": 45,
     "veg": False,
     "recipe": [("flour_ww", 40), ("daal_masoor", 60), ("chana", 40),
                ("chicken", 40), ("oil", 10), ("onion", 20),
                ("veg_mix", 40)]},
    {"id": "seekh-kebab", "en": "Seekh Kebab", "roman": "seekh kebab",
     "ur": "سیخ کباب", "cat": "meat", "serving": "2 pieces", "gi": 0,
     "veg": False,
     "recipe": [("beef", 90), ("onion", 15), ("oil", 8),
                ("flour_ww", 7)]},
    {"id": "shami-kebab", "en": "Shami Kebab", "roman": "shami kebab",
     "ur": "شامی کباب", "cat": "meat", "serving": "2 pieces", "gi": 20,
     "veg": False,
     "recipe": [("beef", 50), ("chana", 35), ("egg", 10),
                ("onion", 5)]},
    {"id": "chicken-tikka", "en": "Chicken Tikka",
     "roman": "chicken tikka", "ur": "چکن ٹکا", "cat": "meat",
     "serving": "1 leg piece", "gi": 0, "veg": False,
     "recipe": [("chicken", 140), ("yogurt", 10)]},
    {"id": "fish-fry", "en": "Fried Fish", "roman": "fried fish machli",
     "ur": "فرائی مچھلی", "cat": "meat", "serving": "1 piece",
     "gi": 40, "veg": False,
     "recipe": [("fish", 130), ("flour_ww", 10), ("oil", 10)]},
    # --- breakfast ---
    {"id": "anda-paratha", "en": "Anda Paratha", "roman": "anda paratha",
     "ur": "انڈا پراٹھا", "cat": "breakfast", "serving": "1 set",
     "gi": 60, "veg": True,
     "recipe": [("paratha", 100), ("egg", 60), ("oil", 10),
                ("onion", 15), ("tomato", 15)]},
    {"id": "halwa-puri", "en": "Halwa Puri", "roman": "halwa puri",
     "ur": "حلوہ پوری", "cat": "breakfast", "serving": "1 plate",
     "gi": 70, "veg": True,
     "recipe": [("flour_ww", 60), ("sugar", 30), ("oil", 20),
                ("potato", 60), ("veg_mix", 30)]},
    {"id": "doodh-patti", "en": "Doodh Patti (Milk Tea)",
     "roman": "doodh patti chai", "ur": "دودھ پتی", "cat": "breakfast",
     "serving": "1 cup", "gi": 45, "veg": True,
     "recipe": [("milk", 150), ("sugar", 8)]},
    {"id": "lassi-sweet", "en": "Sweet Lassi", "roman": "meethi lassi",
     "ur": "میٹھی لسی", "cat": "breakfast", "serving": "1 glass",
     "gi": 30, "veg": True,
     "recipe": [("yogurt", 200), ("sugar", 15), ("milk", 35)]},
    {"id": "lassi-salted", "en": "Salted Lassi", "roman": "namkeen lassi",
     "ur": "نمکین لسی", "cat": "breakfast", "serving": "1 glass",
     "gi": 15, "veg": True,
     "recipe": [("yogurt", 200), ("milk", 50)]},
    {"id": "omelette", "en": "Omelette (2 eggs)", "roman": "omelette anda",
     "ur": "آملٹ", "cat": "breakfast", "serving": "2 eggs", "gi": 0,
     "veg": True,
     "recipe": [("egg", 100), ("oil", 8), ("onion", 12)]},
    {"id": "boiled-egg", "en": "Boiled Egg", "roman": "boiled egg anda",
     "ur": "ابلا انڈا", "cat": "breakfast", "serving": "1 egg",
     "gi": 0, "veg": True, "recipe": [("egg", 50)]},
    # --- snacks / street ---
    {"id": "samosa", "en": "Samosa", "roman": "samosa",
     "ur": "سموسہ", "cat": "snacks", "serving": "1 piece", "gi": 65,
     "veg": True,
     "recipe": [("potato", 50), ("flour_ww", 30), ("oil", 15),
                ("peas", 5)]},
    {"id": "pakora", "en": "Pakora", "roman": "pakora",
     "ur": "پکوڑا", "cat": "snacks", "serving": "5 pieces", "gi": 65,
     "veg": True,
     "recipe": [("flour_ww", 40), ("potato", 30), ("onion", 15),
                ("oil", 15)]},
    {"id": "chaat", "en": "Chana Chaat", "roman": "chaat chana",
     "ur": "چاٹ", "cat": "snacks", "serving": "1 plate", "gi": 45,
     "veg": True,
     "recipe": [("chana", 80), ("potato", 60), ("yogurt", 30),
                ("onion", 15), ("tomato", 10), ("sugar", 5)]},
    {"id": "dahi-bhalla", "en": "Dahi Bhalla", "roman": "dahi bhalla",
     "ur": "دہی بھلا", "cat": "snacks", "serving": "1 plate", "gi": 35,
     "veg": True,
     "recipe": [("chana", 60), ("yogurt", 100), ("sugar", 8),
                ("onion", 10), ("tomato", 5), ("veg_mix", 17)]},
    {"id": "gol-gappa", "en": "Gol Gappa (Pani Puri)",
     "roman": "gol gappa pani puri", "ur": "گول گپا", "cat": "snacks",
     "serving": "6 pieces", "gi": 65, "veg": True,
     "recipe": [("flour_ww", 50), ("potato", 30), ("chana", 10),
                ("veg_mix", 10)]},
    # --- sweets ---
    {"id": "gulab-jamun", "en": "Gulab Jamun", "roman": "gulab jamun",
     "ur": "گلاب جامن", "cat": "sweets", "serving": "2 pieces",
     "gi": 65, "veg": True,
     "recipe": [("flour_ww", 25), ("sugar", 35), ("milk", 25),
                ("ghee", 10), ("veg_mix", 5)]},
    {"id": "jalebi", "en": "Jalebi", "roman": "jalebi",
     "ur": "جلیبی", "cat": "sweets", "serving": "2 pieces", "gi": 70,
     "veg": True,
     "recipe": [("flour_ww", 40), ("sugar", 40), ("oil", 15),
                ("veg_mix", 5)]},
    {"id": "kheer", "en": "Kheer (Rice Pudding)", "roman": "kheer",
     "ur": "کھیر", "cat": "sweets", "serving": "1 katori", "gi": 55,
     "veg": True,
     "recipe": [("milk", 110), ("rice_white", 20), ("sugar", 15),
                ("almonds", 5)]},
    {"id": "gajar-halwa", "en": "Gajar Halwa", "roman": "gajar halwa",
     "ur": "گاجر حلوہ", "cat": "sweets", "serving": "1 katori",
     "gi": 50, "veg": True,
     "recipe": [("carrot", 70), ("milk", 40), ("sugar", 15),
                ("ghee", 10), ("almonds", 5)]},
    # --- fruit / dairy ---
    {"id": "banana", "en": "Banana", "roman": "banana kela",
     "ur": "کیلا", "cat": "fruit-dairy", "serving": "1 medium",
     "gi": 51, "veg": True, "recipe": [("banana", 118)]},
    {"id": "apple", "en": "Apple", "roman": "apple seb",
     "ur": "سیب", "cat": "fruit-dairy", "serving": "1 medium",
     "gi": 36, "veg": True, "recipe": [("apple", 182)]},
    {"id": "mango", "en": "Mango", "roman": "mango aam",
     "ur": "آم", "cat": "fruit-dairy", "serving": "1 cup", "gi": 51,
     "veg": True, "recipe": [("mango", 165)]},
    {"id": "orange", "en": "Orange", "roman": "orange santra",
     "ur": "سنترا", "cat": "fruit-dairy", "serving": "1 medium",
     "gi": 43, "veg": True, "recipe": [("orange", 140)]},
    {"id": "dates", "en": "Dates (Khajoor)", "roman": "dates khajoor",
     "ur": "کھجور", "cat": "fruit-dairy", "serving": "3 pieces",
     "gi": 47, "veg": True, "recipe": [("dates", 24)]},
    {"id": "yogurt-plain", "en": "Plain Yogurt (Dahi)",
     "roman": "yogurt dahi", "ur": "دہی", "cat": "fruit-dairy",
     "serving": "1 cup", "gi": 15, "veg": True,
     "recipe": [("yogurt", 200)]},
    {"id": "milk-glass", "en": "Milk (1 glass)", "roman": "milk doodh",
     "ur": "دودھ", "cat": "fruit-dairy", "serving": "1 glass",
     "gi": 31, "veg": True, "recipe": [("milk", 250)]},
    {"id": "almonds", "en": "Almonds (Badam)", "roman": "almonds badam",
     "ur": "بادام", "cat": "fruit-dairy", "serving": "1 handful",
     "gi": 0, "veg": True, "recipe": [("almonds", 28)]},
    {"id": "peanuts", "en": "Peanuts (Moong Phali)",
     "roman": "peanuts moong phali", "ur": "مونگ پھلی",
     "cat": "fruit-dairy", "serving": "1 handful", "gi": 14,
     "veg": True, "recipe": [("peanuts", 28)]},
    # --- fast food / international ---
    {"id": "grilled-chicken", "en": "Grilled Chicken Breast",
     "roman": "grilled chicken", "ur": "گرل چکن", "cat": "fast-food",
     "serving": "100 g", "gi": 0, "veg": False,
     "recipe": [("chicken", 100)]},
    {"id": "salad-bowl", "en": "Salad Bowl", "roman": "salad",
     "ur": "سلاد", "cat": "fast-food", "serving": "1 bowl", "gi": 0,
     "veg": True,
     "recipe": [("veg_mix", 120), ("tomato", 20), ("onion", 10)]},
    {"id": "zinger-burger", "en": "Zinger-style Burger",
     "roman": "zinger burger", "ur": "زنگر برگر", "cat": "fast-food",
     "serving": "1 burger", "gi": 70, "veg": False,
     "recipe": [("bun_white", 70), ("chicken", 90), ("flour_ww", 10),
                ("oil", 8), ("mayo", 15), ("veg_mix", 20),
                ("cheese", 10)]},
    {"id": "fries", "en": "French Fries", "roman": "fries chips",
     "ur": "فرائز", "cat": "fast-food", "serving": "medium",
     "gi": 75, "veg": True,
     "recipe": [("potato", 70), ("oil", 25), ("veg_mix", 5)]},
    {"id": "pizza-slice", "en": "Pizza Slice", "roman": "pizza",
     "ur": "پیزا", "cat": "fast-food", "serving": "1 slice",
     "gi": 70, "veg": True,
     "recipe": [("flour_ww", 55), ("cheese", 30), ("tomato", 20),
                ("oil", 8), ("veg_mix", 12)]},
    {"id": "shawarma", "en": "Shawarma Roll", "roman": "shawarma",
     "ur": "شاورما", "cat": "fast-food", "serving": "1 roll",
     "gi": 60, "veg": False,
     "recipe": [("roti_ww", 70), ("chicken", 100), ("yogurt", 20),
                ("veg_mix", 40), ("oil", 10), ("onion", 10)]},
]

CATEGORIES = {
    "bread": "Breads / Roti",
    "rice": "Rice Dishes",
    "daal-sabzi": "Daal & Sabzi",
    "meat": "Meat Dishes",
    "breakfast": "Breakfast",
    "snacks": "Snacks & Street Food",
    "sweets": "Sweets",
    "fruit-dairy": "Fruit & Dairy",
    "fast-food": "Fast Food",
}


def values_for(food):
    """Per-serving (kcal, protein, carbs, fat, grams, glycaemic load)
    computed from the food's recipe. Values rounded to 1 decimal."""
    kcal = protein = carbs = fat = grams = 0.0
    for base_id, g in food["recipe"]:
        b = BASE[base_id]
        f = g / 100.0
        kcal += b[0] * f
        protein += b[1] * f
        carbs += b[2] * f
        fat += b[3] * f
        grams += g
    gl = food["gi"] * carbs / 100.0
    return (round(kcal, 1), round(protein, 1), round(carbs, 1),
            round(fat, 1), round(grams, 1), round(gl, 1))


def food_view(food):
    """Public dict for one food, with computed values and flags."""
    kcal, protein, carbs, fat, grams, gl = values_for(food)
    return {
        "id": food["id"], "en": food["en"], "roman": food["roman"],
        "ur": food["ur"], "cat": food["cat"],
        "cat_label": CATEGORIES[food["cat"]],
        "serving": food["serving"], "grams": grams,
        "kcal": kcal, "protein": protein, "carbs": carbs, "fat": fat,
        "gi": food["gi"], "gl": gl, "veg": food["veg"],
        "high_protein": protein >= 15,
        "diabetes_friendly": gl <= 10,
        "source": "USDA FoodData Central generic values + documented "
                  "standard recipe (see repo rizq/foods.py)",
    }


def all_foods():
    return [food_view(f) for f in FOODS]


def food_by_id(fid):
    for f in FOODS:
        if f["id"] == fid:
            return food_view(f)
    return None
