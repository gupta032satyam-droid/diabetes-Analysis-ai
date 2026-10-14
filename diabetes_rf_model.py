"""
=============================================================================
  DIABETES MULTI-CLASS CLASSIFICATION — RANDOM FOREST
  Dataset  : finaldeta_set.csv  (56,572 records, 20 columns)
  Target   : diabetes_type_name  (7 classes)
  Strategy : Medically-grounded feature engineering + class-balanced RF

  Clinical logic baked into features:
    • Type 1     — positive autoantibodies + LOW C-peptide  (autoimmune)
    • Type 2     — high glucose + high BMI + high HbA1c + HIGH C-peptide
    • Gestational— female + pregnant + elevated glucose/HbA1c/BMI
    • Pre-Diab   — borderline glucose (100-125) + borderline HbA1c (5.7-6.4)
    • Child T1/T2— age ≤ 18 + corresponding Type 1 / Type 2 signal
=============================================================================
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    balanced_accuracy_score
)
from sklearn.utils.class_weight import compute_class_weight
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import joblib, os, sys

# ─────────────────────────────────────────────
# 0.  PATHS
# ─────────────────────────────────────────────
CSV_PATH   = Path(__file__).parent / "finaldeta_set.csv"
OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH  = OUTPUT_DIR / "diabetes_rf_model.pkl"
REPORT_PATH = OUTPUT_DIR / "diabetes_classification_report.txt"
CM_PATH     = OUTPUT_DIR / "confusion_matrix.png"
FI_PATH     = OUTPUT_DIR / "feature_importance.png"

# ─────────────────────────────────────────────
# 1.  LOAD DATA
# ─────────────────────────────────────────────
print("=" * 65)
print("  STEP 1 — Loading Dataset")
print("=" * 65)

df = pd.read_csv(CSV_PATH, low_memory=False)
print(f"  Shape loaded  : {df.shape}")
print(f"  Target counts :\n{df['diabetes_type_name'].value_counts()}\n")

# ─────────────────────────────────────────────
# 2.  MISSING VALUE HANDLING
#     Strategy: fill NaN → -1 (sentinel for RF)
# ─────────────────────────────────────────────
print("=" * 65)
print("  STEP 2 — Missing Value Handling (fill → -1)")
print("=" * 65)

TARGET_COL  = "diabetes_type_name"

# Label-encode categorical columns first
OBJECT_COLS = df.select_dtypes(include="object").columns.tolist()
OBJECT_COLS = [c for c in OBJECT_COLS if c != TARGET_COL]
print(f"  Categorical columns to encode: {OBJECT_COLS}")

label_encoders = {}
for col in OBJECT_COLS:
    le = LabelEncoder()
    non_null_mask = df[col].notna()
    le.fit(df.loc[non_null_mask, col].astype(str))
    encoded = le.transform(df.loc[non_null_mask, col].astype(str)).astype(float)
    new_series = pd.Series(np.nan, index=df.index, dtype=float)
    new_series[non_null_mask] = encoded
    df[col] = new_series
    label_encoders[col] = le

# Convert all feature columns to numeric, fill NaN → -1
FEATURE_COLS = [c for c in df.columns if c != TARGET_COL]
for col in FEATURE_COLS:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df[FEATURE_COLS] = df[FEATURE_COLS].fillna(-1)

missing_after = df[FEATURE_COLS].isna().sum().sum()
print(f"  Missing values after fill: {missing_after}  ✓\n")

# ─────────────────────────────────────────────
# 3.  DOMAIN-AWARE FEATURE ENGINEERING
#     Clinical rules encoded as numeric signals
# ─────────────────────────────────────────────
print("=" * 65)
print("  STEP 3 — Domain-Aware Feature Engineering")
print("=" * 65)

# ── Shorthand helpers ──────────────────────────────────────
age   = df["age"]
bmi   = df["bmi"]
glu   = df["glucose"]
hba   = df["hba1c"]
cpep  = df["c_peptide_ng_ml"]
abod  = df["autoantibodies"]
pw    = df["pregnancy_week"]
preg  = df["pregnancies"]
hp    = df["has_pregnancy_data"]
ins   = df["insulin"]
sbp   = df["systolic_bp"]
dbp   = df["diastolic_bp"]

# -- Female code lookup -----------------------------------------------
female_codes = set()
if "gender" in label_encoders:
    for idx, cls in enumerate(label_encoders["gender"].classes_):
        if cls.lower() == "female":
            female_codes.add(idx)
is_female = df["gender"].isin(female_codes)

# ── 3a. Pediatric flag (age ≤ 18) ────────────────────────────────────
df["is_pediatric"] = (age <= 18).astype(int)

# ── 3b. Gestational context (female + pregnant + pregnancy data) ──────
df["is_gestational_context"] = (
    is_female & (hp == 1) & (pw > 0)
).astype(int)

# ── 3c. TYPE 1 SIGNAL: autoimmune pattern ────────────────────────────
#   Positive autoantibodies (>0) AND low C-peptide (<0.6 ng/mL or missing)
#   Missing C-peptide treated as "possibly low" (common in real-world T1)
cpep_valid   = cpep != -1
cpep_low     = cpep_valid & (cpep < 0.6)
cpep_missing = ~cpep_valid                            # unknown → allow T1

df["t1d_autoimmune_signal"] = (
    (abod > 0) & (cpep_low | cpep_missing)
).astype(int)

# Strong T1 signal: antibody positive + confirmed very low C-peptide
df["t1d_strong_signal"] = (
    (abod > 0) & cpep_valid & (cpep < 0.4)
).astype(int)

# ── 3d. TYPE 2 SIGNAL: metabolic / insulin-resistance pattern ─────────
#   High glucose (≥126 mg/dL) + high HbA1c (≥6.5%) + high BMI (≥30)
#   + HIGH C-peptide (≥1.5 ng/mL, indicating insulin resistance, not deficiency)
bmi_obese     = (bmi != -1) & (bmi >= 30)
glu_diabetic  = (glu != -1) & (glu >= 126)
hba_diabetic  = (hba != -1) & (hba >= 6.5)
cpep_high     = cpep_valid & (cpep >= 1.5)

df["metabolic_syndrome_score"] = (
    bmi_obese.astype(int) +
    glu_diabetic.astype(int) +
    hba_diabetic.astype(int)
)

df["t2d_insulin_resistance_signal"] = (
    bmi_obese & glu_diabetic & hba_diabetic
).astype(int)

# High C-peptide strongly suggests T2 (body producing excess insulin)
df["t2d_high_cpeptide"] = cpep_high.astype(int)

# ── 3e. GESTATIONAL SIGNAL ────────────────────────────────────────────
#   Female + pregnant + elevated glucose or HbA1c
#   Gestational HbA1c threshold is lower (≥5.7%) and glucose (≥92 mg/dL)
glu_gest = (glu != -1) & (glu >= 92)
hba_gest = (hba != -1) & (hba >= 5.7)
bmi_gest = (bmi != -1) & (bmi >= 25)

df["gestational_diabetes_signal"] = (
    is_female & (hp == 1) & (pw > 0) &
    (glu_gest | hba_gest)
).astype(int)

# Combined gestational risk score (0-4)
df["gestational_risk_score"] = (
    (is_female & (hp == 1) & (pw > 0)).astype(int) +
    glu_gest.astype(int) +
    hba_gest.astype(int) +
    bmi_gest.astype(int)
)

# ── 3f. PRE-DIABETES SIGNAL ──────────────────────────────────────────
#   Glucose 100-125 mg/dL (IFG) OR HbA1c 5.7-6.4%
#   Not yet in diabetic range
glu_prediab = (glu != -1) & (glu >= 100) & (glu < 126)
hba_prediab = (hba != -1) & (hba >= 5.7) & (hba < 6.5)

df["prediabetes_signal"] = (glu_prediab | hba_prediab).astype(int)

# ── 3g. PEDIATRIC TYPE 1 / TYPE 2 SIGNALS ────────────────────────────
df["pediatric_t1d_signal"] = (
    (age <= 18) & (abod > 0) & (cpep_low | cpep_missing)
).astype(int)

df["pediatric_t2d_signal"] = (
    (age <= 18) & bmi_obese & glu_diabetic
).astype(int)

# ── 3h. Interaction: glucose × HbA1c (glycaemic severity) ───────────
valid_gh = (glu != -1) & (hba != -1)
df["glucose_hba1c_product"] = np.where(valid_gh, glu * hba, -1)

# ── 3i. Pregnancy intensity: week × number of pregnancies ────────────
valid_preg = (pw != -1) & (preg != -1)
df["pregnancy_intensity"] = np.where(valid_preg, pw * preg, -1)

# ── 3j. Availability flags ───────────────────────────────────────────
df["cpeptide_available"]    = (cpep != -1).astype(int)
df["autoantibody_available"]= (abod != -1).astype(int)

# ── 3k. BMI × glucose interaction ────────────────────────────────────
valid_bg = (bmi != -1) & (glu != -1)
df["bmi_glucose_product"] = np.where(valid_bg, bmi * glu, -1)

# ── 3l. Insulin resistance proxy (insulin × BMI) ─────────────────────
valid_ib = (ins != -1) & (bmi != -1)
df["insulin_bmi_product"] = np.where(valid_ib, ins * bmi, -1)

new_feats = [
    "is_pediatric", "is_gestational_context",
    "t1d_autoimmune_signal", "t1d_strong_signal",
    "metabolic_syndrome_score", "t2d_insulin_resistance_signal", "t2d_high_cpeptide",
    "gestational_diabetes_signal", "gestational_risk_score",
    "prediabetes_signal",
    "pediatric_t1d_signal", "pediatric_t2d_signal",
    "glucose_hba1c_product", "pregnancy_intensity",
    "cpeptide_available", "autoantibody_available",
    "bmi_glucose_product", "insulin_bmi_product",
]
print(f"  New engineered features: {len(new_feats)}")
for f in new_feats:
    print(f"    + {f}")
print(f"  Total features for training: {len(df.columns) - 1}\n")

# ─────────────────────────────────────────────
# 4.  TARGET ENCODING
# ─────────────────────────────────────────────
print("=" * 65)
print("  STEP 4 — Target Label Encoding")
print("=" * 65)

le_target = LabelEncoder()
y = le_target.fit_transform(df[TARGET_COL])
X = df.drop(columns=[TARGET_COL])

CLASS_NAMES = le_target.classes_
print(f"  Classes ({len(CLASS_NAMES)}): {list(CLASS_NAMES)}\n")

# ─────────────────────────────────────────────
# 5.  TRAIN / TEST SPLIT  (stratified)
# ─────────────────────────────────────────────
print("=" * 65)
print("  STEP 5 — Stratified Train/Test Split (80/20)")
print("=" * 65)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    random_state=42,
    stratify=y
)
print(f"  Train size : {X_train.shape[0]:,}")
print(f"  Test  size : {X_test.shape[0]:,}\n")

# ─────────────────────────────────────────────
# 6.  CLASS WEIGHTS  (handle severe imbalance)
#     Child/Pediatric types and Gestational are
#     rare — boost their weights significantly
# ─────────────────────────────────────────────
print("=" * 65)
print("  STEP 6 — Computing Class Weights")
print("=" * 65)

cw = compute_class_weight("balanced", classes=np.unique(y_train), y=y_train)
class_weight_dict = dict(enumerate(cw))

# Extra boost for the rare minority classes to prevent them being drowned out
rare_boosts = {
    "Child/Pediatric Type 1": 2.0,
    "Child/Pediatric Type 2": 3.0,   # rarest class
    "Gestational Diabetes":   1.5,
    "Type 1 Diabetes":        1.5,
}
for label, boost in rare_boosts.items():
    if label in CLASS_NAMES:
        idx = list(CLASS_NAMES).index(label)
        class_weight_dict[idx] *= boost

print("  Class → Weight")
for idx, cls in enumerate(CLASS_NAMES):
    print(f"    [{idx}] {cls:<35} → {class_weight_dict[idx]:.4f}")
print()

# ─────────────────────────────────────────────
# 7.  RANDOM FOREST — OPTIMISED HYPER-PARAMS
# ─────────────────────────────────────────────
print("=" * 65)
print("  STEP 7 — Training Random Forest Classifier")
print("=" * 65)

rf = RandomForestClassifier(
    n_estimators      = 500,       # more trees → more stable for rare classes
    max_depth         = None,      # let trees grow fully
    min_samples_split = 3,         # allow finer splits for rare classes
    min_samples_leaf  = 1,         # allow single-leaf for minority classes
    max_features      = "sqrt",    # standard for classification
    class_weight      = class_weight_dict,
    bootstrap         = True,
    oob_score         = True,
    n_jobs            = -1,
    random_state      = 42,
    verbose           = 0,
)

print("  Fitting model …")
rf.fit(X_train, y_train)
print(f"  OOB Score (train estimate) : {rf.oob_score_:.4f}  ({rf.oob_score_*100:.2f}%)\n")

# ─────────────────────────────────────────────
# 8.  EVALUATION
# ─────────────────────────────────────────────
print("=" * 65)
print("  STEP 8 — Model Evaluation")
print("=" * 65)

y_pred = rf.predict(X_test)

acc     = accuracy_score(y_test, y_pred)
bal_acc = balanced_accuracy_score(y_test, y_pred)

print(f"\n  ┌─────────────────────────────────────────────┐")
print(f"  │  Overall Accuracy          : {acc*100:6.2f}%         │")
print(f"  │  Balanced Accuracy         : {bal_acc*100:6.2f}%         │")
print(f"  │  OOB Score (train side)    : {rf.oob_score_*100:6.2f}%         │")
print(f"  └─────────────────────────────────────────────┘\n")

report_str = classification_report(
    y_test, y_pred,
    target_names=CLASS_NAMES,
    digits=4
)
print("  Per-Class Report:")
print(report_str)

# Save text report
with open(REPORT_PATH, "w") as f:
    f.write("DIABETES RANDOM FOREST — CLASSIFICATION REPORT\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Overall  Accuracy  : {acc*100:.4f}%\n")
    f.write(f"Balanced Accuracy  : {bal_acc*100:.4f}%\n")
    f.write(f"OOB Score          : {rf.oob_score_*100:.4f}%\n\n")
    f.write(report_str)
print(f"  Report saved → {REPORT_PATH}\n")

# ─────────────────────────────────────────────
# 9.  5-FOLD CROSS VALIDATION
# ─────────────────────────────────────────────
print("=" * 65)
print("  STEP 9 — 5-Fold Stratified Cross Validation")
print("=" * 65)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(rf, X, y, cv=cv, scoring="accuracy", n_jobs=-1)

print(f"  Fold Scores : {[f'{s*100:.2f}%' for s in cv_scores]}")
print(f"  Mean        : {cv_scores.mean()*100:.2f}%  ± {cv_scores.std()*100:.2f}%\n")

with open(REPORT_PATH, "a") as f:
    f.write("\n5-Fold CV Scores:\n")
    f.write(f"  Folds : {list(np.round(cv_scores*100, 2))}\n")
    f.write(f"  Mean  : {cv_scores.mean()*100:.4f}% ± {cv_scores.std()*100:.4f}%\n")

# ─────────────────────────────────────────────
# 10.  CONFUSION MATRIX PLOT
# ─────────────────────────────────────────────
print("=" * 65)
print("  STEP 10 — Saving Confusion Matrix Plot")
print("=" * 65)

cm = confusion_matrix(y_test, y_pred)

fig, ax = plt.subplots(figsize=(12, 9))
sns.heatmap(
    cm, annot=True, fmt="d", cmap="Blues",
    xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES,
    ax=ax, linewidths=0.5, linecolor="gray"
)
ax.set_xlabel("Predicted Label", fontsize=13, labelpad=10)
ax.set_ylabel("True Label",      fontsize=13, labelpad=10)
ax.set_title(
    f"Random Forest — Confusion Matrix\n"
    f"Accuracy: {acc*100:.2f}%  |  Balanced Accuracy: {bal_acc*100:.2f}%",
    fontsize=14, pad=15
)
plt.xticks(rotation=35, ha="right", fontsize=10)
plt.yticks(rotation=0, fontsize=10)
plt.tight_layout()
plt.savefig(CM_PATH, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved → {CM_PATH}\n")

# ─────────────────────────────────────────────
# 11.  FEATURE IMPORTANCE PLOT
# ─────────────────────────────────────────────
print("=" * 65)
print("  STEP 11 — Feature Importance Plot (Top 25)")
print("=" * 65)

fi = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
top_fi = fi.head(25)

fig, ax = plt.subplots(figsize=(13, 9))
colors = ["#1565C0" if i < 5 else ("#42A5F5" if i < 10 else "#BBDEFB") for i in range(len(top_fi))]
bars = ax.barh(top_fi.index[::-1], top_fi.values[::-1], color=colors[::-1])
ax.set_xlabel("Feature Importance (Gini Impurity Reduction)", fontsize=12)
ax.set_title("Random Forest — Top 25 Feature Importances\n(Dark Blue = Top 5  |  Mid Blue = Top 10)", fontsize=13)
ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=1, decimals=1))
for bar, val in zip(bars, top_fi.values[::-1]):
    ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2,
            f"{val:.4f}", va="center", fontsize=9)
plt.tight_layout()
plt.savefig(FI_PATH, dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved → {FI_PATH}\n")
print("  Top 15 Features:")
for rank, (feat, score) in enumerate(fi.head(15).items(), 1):
    print(f"    {rank:2}. {feat:<40}  {score:.6f}")

# ─────────────────────────────────────────────
# 12.  SAVE MODEL
# ─────────────────────────────────────────────
print()
print("=" * 65)
print("  STEP 12 — Saving Trained Model")
print("=" * 65)

joblib.dump(
    {
        "model"          : rf,
        "label_encoders" : label_encoders,
        "target_encoder" : le_target,
        "feature_cols"   : X.columns.tolist(),
    },
    MODEL_PATH
)
print(f"  Model saved → {MODEL_PATH}\n")

# Also copy to project root for predict_patient.py auto-discovery
import shutil
root_model = Path(__file__).parent / "diabetes_rf_model.pkl"
shutil.copy(MODEL_PATH, root_model)
print(f"  Model also copied → {root_model}\n")

# ─────────────────────────────────────────────
# 13.  SUMMARY
# ─────────────────────────────────────────────
print("=" * 65)
print("  FINAL SUMMARY")
print("=" * 65)
print(f"""
  Dataset           : 56,572 rows × 20 columns
  Target Classes    : {len(CLASS_NAMES)} diabetes types
  Missing Values    : Filled with -1 (sentinel strategy)
  New Features      : {len(new_feats)} medically-grounded engineered features
  Algorithm         : Random Forest (500 trees, boosted minority weights)
  Train / Test      : 80% / 20%  (stratified)

  Clinical Feature Logic:
    • Type 1        → autoantibody+ & low C-peptide signal
    • Type 2        → high BMI + glucose + HbA1c + high C-peptide
    • Gestational   → female + pregnant + elevated glucose/HbA1c/BMI
    • Pre-Diabetes  → borderline glucose (100-125) or HbA1c (5.7-6.4)
    • Child T1/T2   → pediatric age + corresponding T1/T2 clinical signal

  ┌────────────────────────────────────────┐
  │  Overall Accuracy   : {acc*100:6.2f}%           │
  │  Balanced Accuracy  : {bal_acc*100:6.2f}%           │
  │  OOB Score          : {rf.oob_score_*100:6.2f}%           │
  │  5-Fold CV Mean     : {cv_scores.mean()*100:6.2f}% ± {cv_scores.std()*100:.2f}%  │
  └────────────────────────────────────────┘

  Outputs saved:
    • diabetes_rf_model.pkl  (outputs/ + project root)
    • diabetes_classification_report.txt
    • confusion_matrix.png
    • feature_importance.png
""")
print("  ✓ Done!")