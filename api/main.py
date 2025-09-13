

# #THIS IS  A CLEAN CODE

# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, Field
# from typing import List, Literal, Dict
# import json
# from math import isfinite

# # --- config/constants ---
# KOH_CONVERSION = 1.403  # multiply NaOH amount by this for KOH
# DEFAULT_WATER_RATIO_NAOH = 2.5
# DEFAULT_WATER_RATIO_KOH = 3.0

# # --- load SAP table ---
# import os

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# with open(os.path.join(BASE_DIR, "sap_values.json"), "r", encoding="utf-8") as f:
#     SAP_NAOH: Dict[str, float] = json.load(f)

# with open(os.path.join(BASE_DIR, "fatty_acids.json"), "r", encoding="utf-8") as f:
#     FATTY_ACIDS = json.load(f)

# # with open("sap_values.json", "r", encoding="utf-8") as f:
# #     SAP_NAOH: Dict[str, float] = json.load(f)


# # with open("fatty_acids.json", "r", encoding="utf-8") as f:
# #     FATTY_ACIDS = json.load(f)



# # --- models ---
# class OilInput(BaseModel):
#     oil: str = Field(..., description="Oil name exactly as in SAP table.")
#     weight_g: float = Field(..., gt=0, description="Weight of this oil in grams.")

# class LyeRequest(BaseModel):
#     oils: List[OilInput] = Field(..., min_length=1)
#     superfat_percent: float = Field(5.0, ge=0, le=20, description="Superfat percentage (0–20, default 5)")
#     lye_type: Literal["NaOH", "KOH"] = "NaOH"
#     water_ratio: float | None = Field(None, gt=0, description="Water:lye ratio (e.g., 2.5)")

# class OilContribution(BaseModel):
#     oil: str
#     sap_naoh: float
#     lye_g_before_superfat: float
#     lye_g_after_superfat: float

# class LyeResponse(BaseModel):
#     total_oils_g: float
#     total_lye_g: float
#     total_water_g: float
#     lye_type: str
#     superfat_percent: float
#     water_ratio_used: float
#     per_oil: List[OilContribution]

# # --- app setup ---
# app = FastAPI(title="Lye Calculator API", version="1.1.0")

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],  # for dev; restrict in prod
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )
# origins = ["*"]

# app.add_middleware(
#     CORSMiddleware,
#     # allow_origins=[

#     #     "https://<your-frontend>.netlify.app",   # Netlify frontend
#     #     "https://<your-custom-domain>",          # (if you connect a domain to Netlify)
#     #     "https://<your-squarespace-site>.squarespace.com",  # your Squarespace
#     # ],
#     allow_origins=origins,
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

# @app.post("/calculate", response_model=LyeResponse)
# def calculate_lye(payload: LyeRequest):
#     per_oil: List[OilContribution] = []
#     total_naoh_before_sf = 0.0
#     total_oils_g = 0.0

#     for item in payload.oils:
#         if item.oil not in SAP_NAOH:
#             raise HTTPException(status_code=400, detail=f"Unknown oil: {item.oil}")

#         sap = SAP_NAOH[item.oil]
#         lye_before = item.weight_g * sap
#         total_naoh_before_sf += lye_before
#         total_oils_g += item.weight_g

#         per_oil.append(
#             OilContribution(
#                 oil=item.oil,
#                 sap_naoh=sap,
#                 lye_g_before_superfat=round(lye_before, 3),
#                 lye_g_after_superfat=0.0,
#             )
#         )

#     # Apply superfat
#     sf_factor = 1 - (payload.superfat_percent / 100.0)
#     total_naoh_after_sf = total_naoh_before_sf * sf_factor

#     ratio = (total_naoh_after_sf / total_naoh_before_sf) if total_naoh_before_sf > 0 else 1.0
#     for idx, item in enumerate(per_oil):
#         per_oil[idx].lye_g_after_superfat = round(item.lye_g_before_superfat * ratio, 3)

#     # Adjust for NaOH/KOH
#     if payload.lye_type == "NaOH":
#         total_lye_g = total_naoh_after_sf
#         default_water_ratio = DEFAULT_WATER_RATIO_NAOH
#     else:
#         total_lye_g = total_naoh_after_sf * KOH_CONVERSION
#         default_water_ratio = DEFAULT_WATER_RATIO_KOH

#     water_ratio_used = payload.water_ratio if (payload.water_ratio and isfinite(payload.water_ratio)) else default_water_ratio
#     total_water_g = total_lye_g * water_ratio_used

#     return LyeResponse(
#         total_oils_g=round(total_oils_g, 2),
#         total_lye_g=round(total_lye_g, 2),
#         total_water_g=round(total_water_g, 2),
#         lye_type=payload.lye_type,
#         superfat_percent=payload.superfat_percent,
#         water_ratio_used=water_ratio_used,
#         per_oil=per_oil,
#     )

# # --- NEW endpoint: fatty acid composition ---

# @app.get("/fatty-acids/{oil}")
# def get_fatty_acids(oil: str):
#     normalized = oil.strip().lower()

#     for key in FATTY_ACIDS.keys():
#         if key.strip().lower() == normalized:
#             return {"oil": key, "fatty_acids": FATTY_ACIDS[key]}

#     raise HTTPException(status_code=404, detail=f"No fatty acid data for {oil}")


# # --- Debugging endpoints ---}`






# 2nd part
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Literal, Dict
import json, os
from math import isfinite

# --- config/constants ---
KOH_CONVERSION = 1.403  # multiply NaOH amount by this for KOH
DEFAULT_WATER_RATIO_NAOH = 2.5
DEFAULT_WATER_RATIO_KOH = 3.0

# --- load SAP table ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "sap_values.json"), "r", encoding="utf-8") as f:
    SAP_NAOH: Dict[str, float] = json.load(f)

with open(os.path.join(BASE_DIR, "fatty_acids.json"), "r", encoding="utf-8") as f:
    FATTY_ACIDS = json.load(f)


# --- helpers ---
def parse_fatty_acid_value(val: str) -> float:
    """Convert '40–60%' or '2-6%' or '15%' into a single float (midpoint)."""
    if not val:
        return 0.0
    val = val.replace("%", "").replace("–", "-").strip()
    if "-" in val:
        parts = val.split("-")
        try:
            low, high = float(parts[0]), float(parts[1])
            return (low + high) / 2
        except Exception:
            return 0.0
    try:
        return float(val)
    except Exception:
        return 0.0


def compute_soap_metrics(fatty_acids: Dict[str, str]) -> Dict[str, float]:
    """Compute soap quality metrics using parsed fatty acid values."""
    parsed = {k: parse_fatty_acid_value(v) for k, v in fatty_acids.items()}

    hardness = parsed.get("Lauric Acid", 0) + parsed.get("Myristic Acid", 0) + \
               parsed.get("Palmitic Acid", 0) + parsed.get("Stearic Acid", 0)

    cleansing = parsed.get("Lauric Acid", 0) + parsed.get("Myristic Acid", 0)

    conditioning = parsed.get("Oleic Acid", 0) + parsed.get("Linoleic Acid", 0) + \
                   parsed.get("Linolenic Acid", 0) + parsed.get("Ricinoleic Acid", 0)

    bubbly = parsed.get("Lauric Acid", 0) + parsed.get("Myristic Acid", 0) + \
             parsed.get("Ricinoleic Acid", 0)

    creamy = parsed.get("Palmitic Acid", 0) + parsed.get("Stearic Acid", 0) + \
             parsed.get("Ricinoleic Acid", 0)

    return {
        "Hardness": round(hardness, 2),
        "Cleansing": round(cleansing, 2),
        "Conditioning": round(conditioning, 2),
        "Bubbly": round(bubbly, 2),
        "Creamy": round(creamy, 2),
    }


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
app = FastAPI(title="Lye Calculator API", version="1.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with frontend domain(s) in production
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


# --- NEW endpoints: fatty acids ---
@app.get("/fatty-acids/{oil}")
def get_fatty_acids(oil: str):
    normalized = oil.strip().lower()
    for key in FATTY_ACIDS.keys():
        if key.strip().lower() == normalized:
            return {"oil": key, "fatty_acids": FATTY_ACIDS[key]}
    raise HTTPException(status_code=404, detail=f"No fatty acid data for {oil}")


@app.get("/fatty-acids/metrics/{oil}")
def get_fatty_acid_metrics(oil: str):
    normalized = oil.strip().lower()
    for key, acids in FATTY_ACIDS.items():
        if key.strip().lower() == normalized:
            metrics = compute_soap_metrics(acids)
            return {
                "oil": key,
                "fatty_acids": acids,
                "metrics": metrics
            }
    raise HTTPException(status_code=404, detail=f"No fatty acid data for {oil}")


