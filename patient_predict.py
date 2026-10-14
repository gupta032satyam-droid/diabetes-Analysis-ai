"""
=============================================================
  DIABETES DETECTION — Console Patient Input & Prediction
  Run: python true_patient.py
  Requires: diabetes_rf_model.pkl in the same folder
=============================================================
"""

import numpy as np
import pandas as pd
import os
import sys

try:
    import joblib
except ImportError:
    print("ERROR: joblib not installed. Run: pip install joblib")
    sys.exit(1)

# Import medicine recommender
try:
    import medicine_recommender
except ImportError:
    medicine_recommender = None

# ── Config ────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "diabetes_rf_model.pkl")

LABEL_MAP = {
    0: "No Diabetes",
    1: "Pre-Diabetes",
    2: "Type 1 Diabetes",
    3: "Type 2 Diabetes",
    4: "Gestational Diabetes",
    5: "Child/Pediatric Type 1",
    6: "Child/Pediatric Type 2",
}

ALL_FEATURES = [
    "age", "gender_enc", "bmi", "glucose", "hba1c",
    "hba1c_prediab", "hba1c_diabetic", "glucose_prediab", "glucose_diabetic",
    "bmi_overweight", "bmi_obese", "c_peptide_ng_ml",
    "cpeptide_low", "cpeptide_high", "cpeptide_tested",
    "autoantibodies", "autoab_positive", "autoab_negative",
    "is_child", "is_female", "is_pregnant",
    "child_t1_signal", "child_t2_signal", "gestational_signal",
    "adult_t1_signal", "adult_t2_signal",
    "systolic_bp", "diastolic_bp", "blood_pressure",
    "smoking_history", "family_history_diabetes", "cholesterol",
    "insulin", "hypertension", "heart_disease",
    "pregnancies", "pregnancy_week", "has_pregnancy_data",
]


# ── Helpers ───────────────────────────────────────────────

def sep(char="─", n=56):
    print(char * n)

def ask_required(prompt, cast=float, validate=None):
    """Keep asking until a valid value is entered."""
    while True:
        raw = input(f"  {prompt}: ").strip()
        if raw == "":
            print("    ✖  This field is required. Please enter a value.")
            continue
        try:
            val = cast(raw)
            if validate and not validate(val):
                print("    ✖  Value out of range. Try again.")
                continue
            return val
        except (ValueError, TypeError):
            print("    ✖  Invalid input. Expected a number. Try again.")

def ask_optional(prompt, cast=float):
    """Returns -1 if the user skips (presses Enter)."""
    while True:
        raw = input(f"  {prompt} [Enter to skip]: ").strip()
        if raw == "":
            return -1
        try:
            return cast(raw)
        except (ValueError, TypeError):
            print("    ✖  Invalid input. Enter a number or press Enter to skip.")

def ask_choice(prompt, choices, default_idx=None):
    """
    choices : list of (display_label, return_value)
    default_idx : 1-based index used when user presses Enter (optional)
    Returns the return_value of the selected choice.
    """
    print(f"\n  {prompt}")
    for i, (lbl, _) in enumerate(choices, 1):
        marker = "  (default)" if default_idx and i == default_idx else ""
        print(f"    {i}) {lbl}{marker}")
    hint = f"1-{len(choices)}"
    if default_idx:
        hint += ", Enter = default"
    while True:
        raw = input(f"  Choice [{hint}]: ").strip()
        if raw == "" and default_idx:
            return choices[default_idx - 1][1]
        try:
            idx = int(raw)
            if 1 <= idx <= len(choices):
                return choices[idx - 1][1]
            print(f"    ✖  Please enter a number between 1 and {len(choices)}.")
        except ValueError:
            print("    ✖  Invalid input. Try again.")

def ask_yesno(prompt, default="n"):
    hint = "Y/n" if default == "y" else "y/N"
    while True:
        raw = input(f"\n  {prompt} [{hint}]: ").strip().lower()
        if raw == "":
            return default == "y"
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("    ✖  Please enter y or n.")


# ── Feature Builder ───────────────────────────────────────

def build_features(d, required_features=None):
    gender_enc  = {"Male": 0, "Female": 1, "Other": 2}.get(d["gender"], 2)
    is_female   = int(gender_enc == 1)
    is_child    = int(d["age"] < 18)
    pw          = d.get("pregnancy_week", -1)
    is_pregnant = int(pw is not None and pw > 0)

    cpep   = d.get("c_peptide_ng_ml", -1)
    autoab = d.get("autoantibodies",  -1)
    hba1c  = d["hba1c"]
    glu    = d["glucose"]
    bmi    = d["bmi"]
    ins    = d.get("insulin", -1)
    preg   = d.get("pregnancies", -1)

    # Base Signals
    autoab_pos  = int(autoab == 1)
    autoab_neg  = int(autoab == 0)
    cpep_low    = int(cpep != -1 and cpep < 0.6)
    cpep_high   = int(cpep != -1 and cpep > 2.0)
    cpep_tested = int(cpep != -1)

    hba1c_pre  = int(5.7 <= hba1c < 6.5)
    hba1c_diab = int(hba1c >= 6.5)
    glu_pre    = int(100 <= glu < 126)
    glu_diab   = int(glu >= 126)
    bmi_ow     = int(25 <= bmi < 30)
    bmi_ob     = int(bmi >= 30)

    # Composite Signals (Set 1)
    child_t1 = int(is_child and glu_diab and autoab_pos and cpep_low)
    child_t2 = int(is_child and glu_diab and autoab_neg and cpep_high)
    gest     = int(is_female and is_pregnant and glu > 92)
    adult_t1 = int(not is_child and autoab_pos and cpep_low)
    adult_t2 = int(not is_child and bmi_ob and cpep_high)

    # Composite Signals (Set 2 - for advanced model)
    t1d_autoimmune = int((autoab > 0) and (cpep == -1 or cpep < 0.6))
    metabolic_score = int(bmi_ob) + int(glu_diabetic := (glu >= 126)) + int(hba1c_diabetic := (hba1c >= 6.5))
    
    # Blood Pressure Calculation
    sys_bp = d.get("systolic_bp",  -1)
    dia_bp = d.get("diastolic_bp", -1)
    bp = round(dia_bp + (sys_bp - dia_bp) / 3, 1) if (sys_bp != -1 and dia_bp != -1) else -1

    row = {
        "age": d["age"], "gender_enc": gender_enc, "gender": gender_enc,
        "bmi": bmi, "glucose": glu, "hba1c": hba1c,
        "hba1c_prediab": hba1c_pre, "hba1c_diabetic": hba1c_diab,
        "glucose_prediab": glu_pre, "glucose_diabetic": glu_diab,
        "bmi_overweight": bmi_ow, "bmi_obese": bmi_ob,
        "c_peptide_ng_ml": cpep, "cpeptide_low": cpep_low, "cpeptide_high": cpep_high, "cpeptide_tested": cpep_tested,
        "autoantibodies": autoab, "autoab_positive": autoab_pos, "autoab_negative": autoab_neg,
        "is_child": is_child, "is_pediatric": is_child, "is_female": is_female, "is_pregnant": is_pregnant,
        "child_t1_signal": child_t1, "child_t2_signal": child_t2,
        "gestational_signal": gest, "adult_t1_signal": adult_t1, "adult_t2_signal": adult_t2,
        "systolic_bp": sys_bp, "diastolic_bp": dia_bp, "blood_pressure": bp,
        "smoking_history": d.get("smoking_history", -1), "family_history_diabetes": d.get("family_history_diabetes", -1),
        "cholesterol": d.get("cholesterol", -1), "insulin": ins,
        "hypertension": d.get("hypertension", -1), "heart_disease": d.get("heart_disease", -1),
        "pregnancies": preg, "pregnancy_week": pw, "has_pregnancy_data": int(is_pregnant),
        
        # Advanced Features
        "is_gestational_context": int(is_female and is_pregnant),
        "t1d_autoimmune_signal": t1d_autoimmune,
        "t1d_strong_signal": int(autoab > 0 and 0 < cpep < 0.4),
        "metabolic_syndrome_score": metabolic_score,
        "t2d_insulin_resistance_signal": int(bmi_ob and glu_diabetic and hba1c_diabetic),
        "t2d_high_cpeptide": int(cpep >= 1.5),
        "gestational_diabetes_signal": gest,
        "gestational_risk_score": int(is_female and is_pregnant) + int(glu >= 92) + int(hba1c >= 5.7),
        "prediabetes_signal": int(glu_pre or hba1c_pre),
        "pediatric_t1d_signal": int(is_child and t1d_autoimmune),
        "pediatric_t2d_signal": int(is_child and bmi_ob and glu_diabetic),
        "glucose_hba1c_product": (glu * hba1c) if (glu > 0 and hba1c > 0) else -1.0,
        "pregnancy_intensity": (pw * preg) if (pw > 0 and preg > 0) else -1.0,
        "cpeptide_available": int(cpep != -1),
        "autoantibody_available": int(autoab != -1),
        "bmi_glucose_product": (bmi * glu) if (bmi > 0 and glu > 0) else -1.0,
        "insulin_bmi_product": (ins * bmi) if (ins > 0 and bmi > 0) else -1.0,
    }
    
    # If model specifies features, use exactly those in that order
    if required_features:
        return pd.DataFrame([row])[required_features].astype(float)
    return pd.DataFrame([row])[ALL_FEATURES].astype(float)


def apply_clinical_logic(proba, data):
    """
    Applies ADA diagnostic thresholds, clinical boosts, and logical constraints 
    to the raw model probabilities.
    """
    proba = proba.copy()
    hba1c = data["hba1c"]
    glu   = data["glucose"]
    age   = data["age"]
    
    # 1. Diagnostic Tiers (Pregnancy-Aware)
    is_preg_female = (data["gender"] == "Female" and data.get("pregnancy_week", -1) > 0)
    
    if is_preg_female:
        is_diabetic = (hba1c >= 6.5 or glu >= 92)
    else:
        is_diabetic = (hba1c >= 6.5 or glu >= 126)
        
    is_prediabetic = (not is_diabetic) and ((5.7 <= hba1c < 6.5) or (100 <= glu < 126))
    is_healthy     = (not is_diabetic) and (not is_prediabetic) and (hba1c < 5.7 and glu < 100)

    # 2. Soft Clinical Bias (ADA Guidelines)
    boost = np.zeros(7)
    DIABETES_CLASSES = {2, 3, 4, 5, 6}
    PRE_CLASS        = 1
    HEALTHY_CLASS    = 0
    
    if is_diabetic:
        cpep   = data.get("c_peptide_ng_ml", -1)
        autoab = data.get("autoantibodies", -1)
        is_child = age < 18
        
        is_t1_signature = (autoab == 1 and (cpep != -1 and cpep < 0.6))
        is_t2_signature = (autoab == 0 and (cpep != -1 and cpep > 2.0))
        
        if is_child:
            target_idx = 5 if (autoab == 1 or (cpep != -1 and cpep < 0.6)) else 6
        elif data["gender"] == "Female" and data.get("pregnancy_week", -1) > 0:
            target_idx = 4
        elif autoab == 1 or (cpep != -1 and cpep < 0.6):
            target_idx = 2
        else:
            target_idx = 3
        
        boost[target_idx] = 2.0 if (is_t1_signature or is_t2_signature) else 1.5
        
        if is_t1_signature:
            boost[3], boost[6] = 0.0, 0.0
        elif is_t2_signature:
            boost[2], boost[5] = 0.0, 0.0

        for ci in DIABETES_CLASSES:
            if ci != target_idx:
                if is_t1_signature and ci in {3, 6}: continue
                if is_t2_signature and ci in {2, 5}: continue
                boost[ci] = 0.3
        
        proba[HEALTHY_CLASS] *= 0.1
        proba[PRE_CLASS]     *= 0.1
        
    elif is_prediabetic:
        boost[PRE_CLASS] = 1.2
        proba[HEALTHY_CLASS] *= 0.1
        for ci in DIABETES_CLASSES: proba[ci] *= 0.1
        
    elif is_healthy:
        boost[HEALTHY_CLASS] = 2.0
        for i in range(1, 7): proba[i] *= 0.05

    if boost.sum() > 0:
        boost = boost / boost.sum()
    
    proba = (proba * 0.4) + (boost * 0.6)
    
    # Final Logical Exclusions
    if is_diabetic:
        is_t1_sig = (data.get("autoantibodies", -1) == 1 and (data.get("c_peptide_ng_ml", -1) != -1 and data["c_peptide_ng_ml"] < 0.6))
        is_t2_sig = (data.get("autoantibodies", -1) == 0 and (data.get("c_peptide_ng_ml", -1) != -1 and data["c_peptide_ng_ml"] > 2.0))
        if is_t1_sig: proba[3], proba[6] = 0.0, 0.0
        elif is_t2_sig: proba[2], proba[5] = 0.0, 0.0

    # Hard Constraints
    is_adult = age >= 18
    is_preg_f = (data["gender"] == "Female" and data.get("pregnancy_week", -1) > 0)
    
    if is_adult: proba[5], proba[6] = 0.0, 0.0
    else: proba[2], proba[3], proba[4] = 0.0, 0.0, 0.0
        
    if not is_preg_f: proba[4] = 0.0
        
    total = proba.sum()
    if total > 0: proba = proba / total
    return proba


def show_medications(label, d):
    """Integrates with medicine_recommender.py to show personalized advice."""
    if not medicine_recommender:
        return

    # Map our labels to medicine_recommender types
    mapping = {
        "Pre-Diabetes"          : "Prediabetes",
        "Type 1 Diabetes"       : "Type 1",
        "Type 2 Diabetes"       : "Type 2",
        "Gestational Diabetes"  : "Gestational",
        "Child/Pediatric Type 1": "Type 1",
        "Child/Pediatric Type 2": "Type 2"
    }
    
    m_type = mapping.get(label)
    if not m_type:
        return # No meds for 'No Diabetes' or unknown labels

    try:
        rec = medicine_recommender.recommend(
            diabetes_type=m_type,
            age=d["age"],
            bmi=d["bmi"],
            hba1c=d["hba1c"],
            blood_glucose=d["glucose"],
            gender=d["gender"]
        )
        
        print("\n  " + "💊  PERSONALIZED TREATMENT PLAN".center(52))
        sep("═")
        print(f"  RECOMMENDED MEDICINE : {rec['medicine']}")
        print(f"  DOSAGE               : {rec['dosage']}")
        print(f"  SEVERITY LEVEL       : {rec['severity']}")
        print()
        print(f"  PRECAUTIONS          : {rec['precautions']}")
        print(f"  DIETARY ADVICE       : {rec['diet']}")
        print(f"  THINGS TO AVOID      : {rec['avoid']}")
        sep("═")
    except Exception as e:
        print(f"\n  [Medicine Recommender] Note: {e}")


# ── Main ──────────────────────────────────────────────────

def main():
    sep("═")
    print("   DIABETES DETECTION SYSTEM — Patient Prediction Console")
    sep("═")

    # Load model
    if not os.path.exists(MODEL_PATH):
        print(f"\n  ERROR: '{MODEL_PATH}' not found.")
        print("  Please ensure you have trained the Random Forest model and it is in this folder.\n")
        sys.exit(1)

    model_features = None
    try:
        loaded_data = joblib.load(MODEL_PATH)
        # Handle cases where model is saved as a dictionary (from some training scripts)
        if isinstance(loaded_data, dict) and "model" in loaded_data:
            model = loaded_data["model"]
            model_features = loaded_data.get("feature_cols")
        else:
            model = loaded_data
        print(f"\n  Model loaded successfully from: {MODEL_PATH}")
    except Exception as e:
        print(f"\n  ERROR: Failed to load model from '{MODEL_PATH}'.")
        print(f"  Details: {e}")
        sys.exit(1)

    while True:
        data = {}

        # ── SECTION 1 : Required ──────────────────────────
        print()
        sep()
        print("  SECTION 1 — Patient Information  (all fields required)")
        sep()

        data["age"] = ask_required(
            "Age (years)",
            validate=lambda v: 0 < v <= 120
        )

        data["gender"] = ask_choice(
            "Gender",
            [("Male", "Male"), ("Female", "Female"), ("Other", "Other")]
        )

        data["bmi"] = ask_required(
            "BMI (kg/m²)  e.g. 24.5",
            validate=lambda v: 5 < v < 100
        )

        data["glucose"] = ask_required(
            "Fasting Glucose (mg/dL)  e.g. 110",
            validate=lambda v: 30 < v < 700
        )

        data["hba1c"] = ask_required(
            "HbA1c (%)  e.g. 6.4   [normal < 5.7]",
            validate=lambda v: 3.0 < v < 20.0
        )

        # ── SECTION 2 : Pregnancy ─────────────────────────
        print()
        sep()
        print("  SECTION 2 — Pregnancy")
        sep()

        if data["gender"] == "Female":
            pregnant = ask_yesno("Are you currently pregnant?")
            if pregnant:
                print("  (All fields optional — press Enter to skip)")
                data["pregnancy_week"] = ask_optional(
                    "Current pregnancy week  (e.g. 24)"
                )
                data["pregnancies"] = ask_optional(
                    "Total number of pregnancies including current  (e.g. 2)"
                )
            else:
                data["pregnancy_week"] = -1
                data["pregnancies"]    = -1
        else:
            print("  Not applicable — skipped.")
            data["pregnancy_week"] = -1
            data["pregnancies"]    = -1

        # ── SECTION 3 : Diagnostic Tests ─────────────────
        print()
        sep()
        print("  SECTION 3 — Diagnostic Tests  (optional — press Enter to skip)")
        sep()

        data["autoantibodies"] = ask_choice(
            "Autoantibody Test result  (GAD65 / IA-2 / ZnT8)",
            [
                ("Positive  — antibodies detected", 1),
                ("Negative  — no antibodies detected", 0),
                ("Not tested / Unknown", -1),
            ],
            default_idx=3
        )

        data["c_peptide_ng_ml"] = ask_optional(
            "C-Peptide (ng/mL)   low < 0.6 suggests Type 1,  high > 2.0 suggests Type 2"
        )

        data["insulin"] = ask_optional(
            "Insulin level (uIU/mL)"
        )

        # ── SECTION 4 : Vitals ────────────────────────────
        print()
        sep()
        print("  SECTION 4 — Vitals  (optional — press Enter to skip)")
        sep()

        data["systolic_bp"]  = ask_optional("Systolic Blood Pressure  (mmHg)  e.g. 120")
        data["diastolic_bp"] = ask_optional("Diastolic Blood Pressure (mmHg)  e.g. 80")
        data["cholesterol"]  = ask_optional("Total Cholesterol (mg/dL)")

        data["hypertension"] = ask_choice(
            "Do you have hypertension (high blood pressure)?",
            [("Yes", 1), ("No", 0), ("Unknown", -1)],
            default_idx=3
        )

        data["heart_disease"] = ask_choice(
            "History of heart disease?",
            [("Yes", 1), ("No", 0), ("Unknown", -1)],
            default_idx=3
        )

        # ── SECTION 5 : Lifestyle ─────────────────────────
        print()
        sep()
        print("  SECTION 5 — Lifestyle & Family History  (optional)")
        sep()

        data["smoking_history"] = ask_choice(
            "Smoking history?",
            [("Current or ex-smoker", 1), ("Non-smoker", 0), ("Unknown", -1)],
            default_idx=3
        )

        data["family_history_diabetes"] = ask_choice(
            "Family history of diabetes?  (parent or sibling)",
            [("Yes", 1), ("No", 0), ("Unknown", -1)],
            default_idx=3
        )

        # ── PREDICT ───────────────────────────────────────
        print()
        sep("═")
        print("  Running prediction ...")
        sep("═")

        X     = build_features(data, required_features=model_features)
        proba = model.predict_proba(X)[0]
        
        # ── 3. APPLY CLINICAL LOGIC ───────────────────────────────
        proba = apply_clinical_logic(proba, data)


        pred  = int(np.argmax(proba))
        label = LABEL_MAP[pred]
        conf  = proba[pred] * 100

        print(f"\n  PREDICTED DIAGNOSIS : {label}")
        print(f"  Confidence          : {conf:.1f}%")
        print()
        sep()
        print("  Probability breakdown:")
        sep()

        for idx, p in sorted(enumerate(proba), key=lambda x: -x[1]):
            # Skip classes with 0% probability (illogical or zeroed by clinical constraints)
            if p <= 0:
                continue
            name   = LABEL_MAP[idx]
            pct    = p * 100
            bar    = "█" * int(pct / 2)
            marker = " <-- Predicted" if idx == pred else ""
            print(f"  {name:<28}  {pct:5.1f}%  {bar}{marker}")

        sep()
        notes = {
            "No Diabetes"           : "No diabetes indicators. Maintain a healthy lifestyle.",
            "Pre-Diabetes"          : "Blood sugar above normal. Lifestyle changes can reverse this.",
            "Type 1 Diabetes"       : "Autoimmune — insulin therapy required. See an endocrinologist.",
            "Type 2 Diabetes"       : "Lifestyle changes, oral medications, or insulin may be needed.",
            "Gestational Diabetes"  : "Manage with diet and exercise; monitor fetal health closely.",
            "Child/Pediatric Type 1": "Immediate paediatric endocrinology referral recommended.",
            "Child/Pediatric Type 2": "Weight management and paediatric specialist care required.",
        }
        print(f"\n  Note: {notes.get(label, '')}")
        
        # Show medications if available
        show_medications(label, data)

        print("\n  DISCLAIMER: For educational use only.")
        print("  Always consult a qualified physician for medical decisions.")

        # ── Loop ──────────────────────────────────────────
        if not ask_yesno("Predict another patient?", default="y"):
            print("\n  Goodbye. Stay healthy!\n")
            break
        print()


if __name__ == "__main__":
    main()
