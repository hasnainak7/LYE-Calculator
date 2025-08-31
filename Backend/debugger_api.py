from fastapi import FastAPI
import json
from pathlib import Path

app = FastAPI()

# ---------- Load files ----------
sap_values = json.load(open(Path("sap_values.json"), "r", encoding="utf-8"))
fatty_acids = json.load(open(Path("fatty_acids.json"), "r", encoding="utf-8"))

sap_keys = set(sap_values.keys())
fatty_keys = set(fatty_acids.keys())


@app.get("/")
def home():
    return {"message": "Oil Name Debugger API is running (no normalization)!"}


@app.get("/debug/matches")
def get_matches():
    """Get all oils that matched exactly between SAP and Fatty Acids"""
    matches = list(sap_keys & fatty_keys)  # intersection
    return {"matches": sorted(matches)}


@app.get("/debug/mismatches")
def get_mismatches():
    """Get oils in SAP but not in Fatty acids and vice versa"""
    sap_not_in_fatty = sorted(list(sap_keys - fatty_keys))
    fatty_not_in_sap = sorted(list(fatty_keys - sap_keys))

    return {
        "sap_missing": sap_not_in_fatty,
        "fatty_missing": fatty_not_in_sap
    }


@app.get("/debug/all")
def get_full_debug():
    """Full debug report in one response"""
    matches = sorted(list(sap_keys & fatty_keys))
    sap_not_in_fatty = sorted(list(sap_keys - fatty_keys))
    fatty_not_in_sap = sorted(list(fatty_keys - sap_keys))

    return {
        "matches": matches,
        "sap_missing": sap_not_in_fatty,
        "fatty_missing": fatty_not_in_sap
    }


@app.get("/debug/search")
def search_oil(name: str):
    """Check a single oil manually"""
    in_sap = name in sap_keys
    in_fatty = name in fatty_keys
    return {
        "oil": name,
        "in_sap": in_sap,
        "in_fatty": in_fatty
    }