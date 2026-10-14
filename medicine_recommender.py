"""
medicine_recommender.py
=======================
Connect this file to your existing Random Forest diabetes detection project.

STEP 1 — Place this file in the same folder as your detection script.
STEP 2 — Place medicine.csv in the same folder too.
STEP 3 — In your detection script, add 2 lines after your RF prediction:

    from medicine_recommender import recommend
    result = recommend(predicted_type, age, bmi, hba1c, blood_glucose, gender)

Full example at the bottom of this file.
"""

import pandas as pd
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), "medicine.csv")
_df = None


def _load():
    global _df
    if _df is None:
        if not os.path.exists(CSV_PATH):
            raise FileNotFoundError(
                f"\n[ERROR] '{CSV_PATH}' not found.\n"
                "Put medicine.csv in the same folder as this script."
            )
        _df = pd.read_csv(CSV_PATH)
    return _df


def _get_severity(hba1c: float, diabetes_type: str) -> str:
    """Auto-detect severity from HbA1c (ADA guidelines)."""
    if diabetes_type == "Prediabetes":
        return "Mild"
    if hba1c < 7.0:
        return "Mild"
    elif hba1c < 9.5:
        return "Moderate"
    else:
        return "Severe"


def _pick_medicine(diabetes_type, severity, hba1c, age, bmi, gender) -> str:
    """
    Clinical rule-based selection — medicine names match exactly with medicine.csv.
    Based on ADA (American Diabetes Association) treatment guidelines.
    """
    if diabetes_type == "Type 1":
        if severity == "Severe" or hba1c >= 10.0:
            return "Insulin Aspart"
        elif severity == "Moderate":
            return "Insulin Glargine" if hba1c >= 8.5 else "Insulin Lispro"
        else:
            return "Insulin NPH" if age < 20 else "Insulin Detemir"

    elif diabetes_type == "Type 2":
        if severity == "Severe" or hba1c >= 10.0:
            return "Sitagliptin"
        elif severity == "Moderate":
            return "Empagliflozin" if bmi >= 30 else "Metformin"
        else:
            if age >= 60:
                return "Glipizide"
            elif bmi >= 28:
                return "Pioglitazone"
            else:
                return "Glyburide"

    elif diabetes_type == "Gestational":
        if severity == "Moderate" or hba1c >= 7.5:
            return "Insulin Regular"
        elif hba1c >= 6.5:
            return "Insulin Glargine" if age >= 30 else "Insulin NPH"
        else:
            return "Metformin (pregnancy-safe)"

    elif diabetes_type == "Prediabetes":
        if bmi >= 35:
            return "Orlistat"
        elif hba1c >= 6.2:
            return "Metformin 500mg"
        elif hba1c >= 5.9:
            return "Metformin 250mg"
        elif bmi >= 27:
            return "Acarbose"
        elif age >= 50:
            return "Berberine"
        else:
            return "Lifestyle intervention"

    return "Consult physician"


def _get_details(diabetes_type, medicine) -> dict:
    """Fetch dosage, precautions, diet, avoid from medicine.csv."""
    df = _load()
    rows = df[(df["diabetes_type"] == diabetes_type) & (df["medicine"] == medicine)]
    if rows.empty:
        rows = df[df["medicine"] == medicine]
    if rows.empty:
        return {"dosage": "As prescribed", "precautions": "Consult physician",
                "diet": "Diabetic diet", "avoid": "Consult physician"}
    row = rows.iloc[0]
    return {k: row[k] for k in ["dosage", "precautions", "diet", "avoid"]}


# ════════════════════════════════════════════════════════
#  MAIN FUNCTION — import and call this from your script
# ════════════════════════════════════════════════════════

def recommend(
    diabetes_type : str,
    age           : float,
    bmi           : float,
    hba1c         : float,
    blood_glucose : float,
    gender        : str = "Male",
    severity      : str = None,
) -> dict:
    """
    Call this right after your Random Forest model predicts the diabetes type.

    Parameters
    ----------
    diabetes_type : str   → directly pass your model's output
                           "Type 1" | "Type 2" | "Gestational" | "Prediabetes"
    age           : float  patient age in years
    bmi           : float  Body Mass Index
    hba1c         : float  HbA1c percentage (e.g. 7.5)
    blood_glucose : float  fasting blood glucose mg/dL
    gender        : str    "Male" or "Female"
    severity      : str    "Mild"/"Moderate"/"Severe"  (auto-detected if None)

    Returns
    -------
    dict → { detected_type, severity, medicine, dosage, precautions, diet, avoid }
    """
    valid = {"Type 1", "Type 2", "Gestational", "Prediabetes"}
    diabetes_type = str(diabetes_type).strip()
    if diabetes_type not in valid:
        raise ValueError(f"diabetes_type must be one of {valid}, got: '{diabetes_type}'")

    if diabetes_type == "Gestational":
        gender = "Female"
    if severity is None:
        severity = _get_severity(float(hba1c), diabetes_type)

    medicine = _pick_medicine(diabetes_type, severity, float(hba1c), int(age), float(bmi), gender)
    details  = _get_details(diabetes_type, medicine)

    return {
        "detected_type" : diabetes_type,
        "severity"      : severity,
        "medicine"      : medicine,
        "dosage"        : details["dosage"],
        "precautions"   : details["precautions"],
        "diet"          : details["diet"],
        "avoid"         : details["avoid"],
    }


# ════════════════════════════════════════════════════════
#  HOW TO ADD THIS TO YOUR EXISTING DETECTION SCRIPT
# ════════════════════════════════════════════════════════
#
#  Your current detection code probably looks like this:
#  ─────────────────────────────────────────────────────
#
#  import pickle, numpy as np
#  model = pickle.load(open("diabetes_rf_model.pkl", "rb"))
#
#  patient = {
#      "age": 45, "gender": "Female", "bmi": 29.5,
#      "hba1c": 7.8, "blood_glucose": 160,
#      ...
#  }
#
#  features = np.array([[patient["age"], patient["bmi"], ...]])
#  predicted_type = model.predict(features)[0]
#  # → "Type 2"
#
#
#  ✅ ADD JUST THESE 2 LINES RIGHT AFTER YOUR PREDICTION:
#  ─────────────────────────────────────────────────────
#
#  from medicine_recommender import recommend
#
#  result = recommend(
#      diabetes_type = predicted_type,        # ← your RF output
#      age           = patient["age"],
#      bmi           = patient["bmi"],
#      hba1c         = patient["hba1c"],
#      blood_glucose = patient["blood_glucose"],
#      gender        = patient["gender"],
#  )
#
#  print("Medicine  :", result["medicine"])
#  print("Dosage    :", result["dosage"])
#  print("Diet      :", result["diet"])
#  print("Avoid     :", result["avoid"])
#  print("Caution   :", result["precautions"])
#
# ════════════════════════════════════════════════════════


if __name__ == "__main__":

    tests = [
        {"diabetes_type": "Type 1",      "age": 20, "gender": "Male",   "bmi": 21.0, "hba1c": 9.8,  "blood_glucose": 215},
        {"diabetes_type": "Type 1",      "age": 35, "gender": "Female", "bmi": 23.5, "hba1c": 7.2,  "blood_glucose": 155},
        {"diabetes_type": "Type 2",      "age": 54, "gender": "Female", "bmi": 33.0, "hba1c": 8.1,  "blood_glucose": 175},
        {"diabetes_type": "Type 2",      "age": 63, "gender": "Male",   "bmi": 25.0, "hba1c": 6.7,  "blood_glucose": 135},
        {"diabetes_type": "Gestational", "age": 27, "gender": "Female", "bmi": 25.0, "hba1c": 6.3,  "blood_glucose": 128},
        {"diabetes_type": "Gestational", "age": 34, "gender": "Female", "bmi": 28.0, "hba1c": 7.9,  "blood_glucose": 180},
        {"diabetes_type": "Prediabetes", "age": 41, "gender": "Male",   "bmi": 36.0, "hba1c": 6.0,  "blood_glucose": 112},
        {"diabetes_type": "Prediabetes", "age": 38, "gender": "Female", "bmi": 24.0, "hba1c": 5.7,  "blood_glucose": 102},
    ]

    print("\n" + "═" * 63)
    print("   MEDICINE RECOMMENDER — LIVE TEST")
    print("═" * 63)

    for p in tests:
        r = recommend(**p)
        print(f"\n  Patient  : Age {p['age']} | {p['gender']} | BMI {p['bmi']} | HbA1c {p['hba1c']}%")
        print(f"  RF Model : Detected → {r['detected_type']}  [{r['severity']}]")
        print(f"  Medicine : {r['medicine']}  —  {r['dosage']}")
        print(f"  Diet     : {r['diet']}")
        print(f"  Avoid    : {r['avoid']}")
        print(f"  Caution  : {r['precautions']}")
        print("  " + "─" * 59)
