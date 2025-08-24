# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from math import isfinite
# from typing import Dict, List
# import json
# from pydantic import BaseModel, Field
# from typing import List, Literal


# app = FastAPI()   # <-- this must come before any @app.get or @app.post


# class OilInput(BaseModel):
#     oil: str = Field(..., description="Oil name exactly as in SAP table.")
#     weight_g: float = Field(..., gt=0, description="Weight of this oil in grams.")

# class LyeRequest(BaseModel):
#     oils: List[OilInput] = Field(..., min_length=1)
#     superfat_percent: float = Field(5.0, ge=0, le=20, description="Superfat percentage (0–20, default 5)")
#     lye_type: Literal["NaOH", "KOH"] = "NaOH"
#     water_ratio: float | None = Field(None, gt=0, description="Water:lye ratio (e.g., 2.5)")


# # --- constants ---
# KOH_CONVERSION = 1.403
# DEFAULT_WATER_RATIO_NAOH = 2.5
# DEFAULT_WATER_RATIO_KOH = 3.0

# # --- load SAP table ---
# with open("sap_values.json", "r", encoding="utf-8") as f:
#     SAP_NAOH: Dict[str, float] = json.load(f)







# # --- FastAPI app ---
# app = FastAPI(title="Lye Calculator API", version="1.0.0")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # restrict in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get("/health")
# def health():
#     return {"ok": True}

# @app.get("/oils")
# def list_oils():
#     return {"oils": sorted(SAP_NAOH.keys())}

# @app.post("/calculate")
# def calculate_lye(payload: LyeRequest):
#     per_oil = []
#     total_naoh_before_sf = 0.0
#     total_oils_g = 0.0

#     # Validate oils exist
#     for item in payload.oils:
#         if item.oil not in SAP_NAOH:
#             raise HTTPException(status_code=400, detail=f"Unknown oil: {item.oil}")

#         sap = SAP_NAOH[item.oil]
#         lye_before = item.weight_g * sap
#         total_naoh_before_sf += lye_before
#         total_oils_g += item.weight_g

#         per_oil.append({
#             "oil": item.oil,
#             "sap_naoh": sap,
#             "lye_g_before_superfat": round(lye_before, 3),
#             "lye_g_after_superfat": 0.0
#         })

#     # Apply superfat
#     sf_factor = 1 - (payload.superfat_percent / 100.0)
#     total_naoh_after_sf = total_naoh_before_sf * sf_factor

#     # Fill per oil proportionally
#     ratio = total_naoh_after_sf / total_naoh_before_sf if total_naoh_before_sf else 1.0
#     for item in per_oil:
#         item["lye_g_after_superfat"] = round(item["lye_g_before_superfat"] * ratio, 3)

#     # Adjust for lye type
#     if payload.lye_type == "NaOH":
#         total_lye_g = total_naoh_after_sf
#         default_water_ratio = DEFAULT_WATER_RATIO_NAOH
#     else:
#         total_lye_g = total_naoh_after_sf * KOH_CONVERSION
#         default_water_ratio = DEFAULT_WATER_RATIO_KOH

#     water_ratio_used = payload.water_ratio if (payload.water_ratio and isfinite(payload.water_ratio)) else default_water_ratio
#     total_water_g = total_lye_g * water_ratio_used

#     return {
#         "total_oils_g": round(total_oils_g, 2),
#         "total_lye_g": round(total_lye_g, 2),
#         "total_water_g": round(total_water_g, 2),
#         "lye_type": payload.lye_type,
#         "superfat_percent": payload.superfat_percent,
#         "water_ratio_used": water_ratio_used,
#         "per_oil": per_oil
#     }


#THIS IS  A CLEAN CODE

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Literal, Dict
import json
from math import isfinite

# --- config/constants ---
KOH_CONVERSION = 1.403  # multiply NaOH amount by this for KOH
DEFAULT_WATER_RATIO_NAOH = 2.5
DEFAULT_WATER_RATIO_KOH = 3.0

# --- load SAP table ---
with open("sap_values.json", "r", encoding="utf-8") as f:
    SAP_NAOH: Dict[str, float] = json.load(f)


with open("fatty_acids.json", "r", encoding="utf-8") as f:
    FATTY_ACIDS = json.load(f)

# --- fatty acid dataset (short example, you’ll extend this) ---
# FATTY_ACIDS = {
#     "Acai Oil,Organic": {
#         "Oleic Acid": "40–60%",
#         "Palmitic Acid": "17–28%",
#         "Linoleic Acid": "10–22%"
#     },
#     "Almond Oil, Sweet": {
#         "Oleic Acid": "62–86%",
#         "Linoleic Acid": "20–30%",
#         "Palmitic Acid": "6–8%"
#     },
#     "Olive Oil, Extra Olive Oil": {
#         "Oleic Acid": "55–83%",
#         "Linoleic Acid": "3.5–21%",
#         "Palmitic Acid": "7.5–20%"
#     },
#     "Almond Oil": { 
#     "Oleic Acid": "60–80%", 
#     "Linoleic Acid": "10–30%", 
#     "Palmitic Acid": "5–10%", 
#     "Stearic Acid": "1–3%" 
#   }, 
#    "Aloe Vera Butter": { 
#         "Steric Acid": " 6-17%", 
#         "Lauric Acid": "44-57%", 
#         "Palmitic Acid": "7-12%", 
#         "Caprylic Acid": " 4-10%", 
#         "Capric Acid" : "4-10%" , 
#         "Myristic Acid" : "13-21%" 
#     }, 
#    "Amla Oil": { 
#         "Oleic Acid": "26.4%", 
#         "Linoleic Acid": "51%", 
#         "Linolenic Acid": "11.8%",
#         "Palmitic Acid": "2.3%", 
#         "Stearic Acid": "9%" ,
#         "Myristic Acid": "9%" 


# --- models ---
class OilInput(BaseModel):
    oil: str = Field(..., description="Oil name exactly as in SAP table.")
    weight_g: float = Field(..., gt=0, description="Weight of this oil in grams.")

class LyeRequest(BaseModel):
    oils: List[OilInput] = Field(..., min_length=1)
    superfat_percent: float = Field(5.0, ge=0, le=20, description="Superfat percentage (0–20, default 5)")
    lye_type: Literal["NaOH", "KOH"] = "NaOH"
    water_ratio: float | None = Field(None, gt=0, description="Water:lye ratio (e.g., 2.5)")

class OilContribution(BaseModel):
    oil: str
    sap_naoh: float
    lye_g_before_superfat: float
    lye_g_after_superfat: float

class LyeResponse(BaseModel):
    total_oils_g: float
    total_lye_g: float
    total_water_g: float
    lye_type: str
    superfat_percent: float
    water_ratio_used: float
    per_oil: List[OilContribution]

# --- app setup ---
app = FastAPI(title="Lye Calculator API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/oils")
def list_oils():
    return {"oils": sorted(SAP_NAOH.keys())}

@app.post("/calculate", response_model=LyeResponse)
def calculate_lye(payload: LyeRequest):
    per_oil: List[OilContribution] = []
    total_naoh_before_sf = 0.0
    total_oils_g = 0.0

    for item in payload.oils:
        if item.oil not in SAP_NAOH:
            raise HTTPException(status_code=400, detail=f"Unknown oil: {item.oil}")

        sap = SAP_NAOH[item.oil]
        lye_before = item.weight_g * sap
        total_naoh_before_sf += lye_before
        total_oils_g += item.weight_g

        per_oil.append(
            OilContribution(
                oil=item.oil,
                sap_naoh=sap,
                lye_g_before_superfat=round(lye_before, 3),
                lye_g_after_superfat=0.0,
            )
        )

    # Apply superfat
    sf_factor = 1 - (payload.superfat_percent / 100.0)
    total_naoh_after_sf = total_naoh_before_sf * sf_factor

    ratio = (total_naoh_after_sf / total_naoh_before_sf) if total_naoh_before_sf > 0 else 1.0
    for idx, item in enumerate(per_oil):
        per_oil[idx].lye_g_after_superfat = round(item.lye_g_before_superfat * ratio, 3)

    # Adjust for NaOH/KOH
    if payload.lye_type == "NaOH":
        total_lye_g = total_naoh_after_sf
        default_water_ratio = DEFAULT_WATER_RATIO_NAOH
    else:
        total_lye_g = total_naoh_after_sf * KOH_CONVERSION
        default_water_ratio = DEFAULT_WATER_RATIO_KOH

    water_ratio_used = payload.water_ratio if (payload.water_ratio and isfinite(payload.water_ratio)) else default_water_ratio
    total_water_g = total_lye_g * water_ratio_used

    return LyeResponse(
        total_oils_g=round(total_oils_g, 2),
        total_lye_g=round(total_lye_g, 2),
        total_water_g=round(total_water_g, 2),
        lye_type=payload.lye_type,
        superfat_percent=payload.superfat_percent,
        water_ratio_used=water_ratio_used,
        per_oil=per_oil,
    )

# --- NEW endpoint: fatty acid composition ---

@app.get("/fatty-acids/{oil}")
def get_fatty_acids(oil: str):
    data = FATTY_ACIDS.get(oil)
    if not data:
        raise HTTPException(status_code=404, detail=f"No fatty acid data for {oil}")
    return {"oil": oil, "fatty_acids": data}
