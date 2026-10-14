import pandas as pd
import numpy as np

# ── Load all 4 datasets ────────────────────────────────────────────────────
ds1 = pd.read_csv('datasets/diabetes_prediction_dataset.csv')
ds2 = pd.read_csv('datasets/pima_diabetes.csv')
ds3 = pd.read_csv('datasets/diabetes_012_health_indicators_BRFSS2015.csv')
ds4 = pd.read_csv('datasets/Dataset_of_Diabetes.csv')

print("All datasets loaded successfully!")

# ══════════════════════════════════════════════════════════════════════════
# STEP 1 — Standardise DS1 (100,000 rows → sample 40,000)
# Columns: gender, age, hypertension, heart_disease, smoking_history,
#          bmi, HbA1c_level, blood_glucose_level, diabetes
# ══════════════════════════════════════════════════════════════════════════
ds1_std = pd.DataFrame({
    'gender'         : ds1['gender'],
    'age'            : ds1['age'],
    'bmi'            : ds1['bmi'],
    'glucose'        : ds1['blood_glucose_level'],
    'hba1c'          : ds1['HbA1c_level'],
    'insulin'        : np.nan,
    'pregnancies'    : np.nan,
    'blood_pressure' : np.nan,
    'cholesterol'    : np.nan,
    'hypertension'   : ds1['hypertension'],
    'heart_disease'  : ds1['heart_disease'],
    'smoking_history': ds1['smoking_history'],
    'diabetes_label' : ds1['diabetes'],        # 0 or 1
    'source'         : 'ds1_general'
})
ds1_sampled = ds1_std.sample(n=40000, random_state=42)
print(f"DS1 sampled: {ds1_sampled.shape}")

# ══════════════════════════════════════════════════════════════════════════
# STEP 2 — Standardise DS2 (768 rows → use ALL)
# Columns: Pregnancies, Glucose, BloodPressure, SkinThickness,
#          Insulin, BMI, DiabetesPedigreeFunction, Age, Outcome
# ══════════════════════════════════════════════════════════════════════════
ds2_std = pd.DataFrame({
    'gender'         : 'Female',              # PIMA = all female
    'age'            : ds2['Age'],
    'bmi'            : ds2['BMI'],
    'glucose'        : ds2['Glucose'],
    'hba1c'          : np.nan,
    'insulin'        : ds2['Insulin'],
    'pregnancies'    : ds2['Pregnancies'],
    'blood_pressure' : ds2['BloodPressure'],
    'cholesterol'    : np.nan,
    'hypertension'   : np.nan,
    'heart_disease'  : np.nan,
    'smoking_history': np.nan,
    'diabetes_label' : ds2['Outcome'],        # 0 or 1
    'source'         : 'ds2_pima'
})
print(f"DS2 all rows: {ds2_std.shape}")

# ══════════════════════════════════════════════════════════════════════════
# STEP 3 — Standardise DS3 (253,680 rows → sample 34,232)
# Columns: Diabetes_012, HighBP, HighChol, BMI, Sex, Age (coded 1-13)...
# Sex: 0=Female, 1=Male  |  Age: 1=18-24, 2=25-29 ... 13=80+
# ══════════════════════════════════════════════════════════════════════════
# Convert coded age bands to real approximate ages
age_band_map = {
    1: 21, 2: 27, 3: 32, 4: 37, 5: 42,
    6: 47, 7: 52, 8: 57, 9: 62, 10: 67,
    11: 72, 12: 77, 13: 82
}

ds3_std = pd.DataFrame({
    'gender'         : ds3['Sex'].map({0: 'Female', 1: 'Male'}),
    'age'            : ds3['Age'].map(age_band_map),
    'bmi'            : ds3['BMI'],
    'glucose'        : np.nan,
    'hba1c'          : np.nan,
    'insulin'        : np.nan,
    'pregnancies'    : np.nan,
    'blood_pressure' : ds3['HighBP'].map({0: 'Normal', 1: 'High'}),
    'cholesterol'    : ds3['HighChol'].map({0: 'Normal', 1: 'High'}),
    'hypertension'   : ds3['HighBP'],
    'heart_disease'  : ds3['HeartDiseaseorAttack'],
    'smoking_history': ds3['Smoker'].map({0: 'never', 1: 'current'}),
    'diabetes_label' : ds3['Diabetes_012'],   # 0=No, 1=Pre, 2=Yes
    'source'         : 'ds3_brfss'
})

# Stratified sample — keep all 3 classes proportional
target_n = 34232
ds3_sampled = ds3_std.groupby('diabetes_label', group_keys=False).apply(
    lambda x: x.sample(
        n=max(1, int(round(target_n * len(x) / len(ds3_std)))),
        random_state=42
    )
).reset_index(drop=True)
print(f"DS3 sampled: {ds3_sampled.shape}")
print(f"DS3 class split:\n{ds3_sampled['diabetes_label'].value_counts()}")

# ══════════════════════════════════════════════════════════════════════════
# STEP 4 — Standardise DS4 (264 rows → use ALL)
# Columns: Gender(0/1), AGE, Urea, Cr, HbA1c, Chol, TG, HDL, LDL,
#          VLDL, BMI, Class(0/1)
# Gender: 0=Female, 1=Male  |  Class: 0=No Diabetes, 1=Diabetic
# ══════════════════════════════════════════════════════════════════════════
ds4_std = pd.DataFrame({
    'gender'         : ds4['Gender'].map({0: 'Female', 1: 'Male'}),
    'age'            : ds4['AGE'],
    'bmi'            : ds4['BMI'],
    'glucose'        : np.nan,
    'hba1c'          : ds4['HbA1c'],
    'insulin'        : np.nan,
    'pregnancies'    : np.nan,
    'blood_pressure' : np.nan,
    'cholesterol'    : ds4['Chol'],
    'hypertension'   : np.nan,
    'heart_disease'  : np.nan,
    'smoking_history': np.nan,
    'diabetes_label' : ds4['Class'],          # 0 or 1
    'source'         : 'ds4_clinical'
})
print(f"DS4 all rows: {ds4_std.shape}")

# ══════════════════════════════════════════════════════════════════════════
# STEP 5 — Combine all 4 datasets
# ══════════════════════════════════════════════════════════════════════════
unified = pd.concat(
    [ds1_sampled, ds2_std, ds3_sampled, ds4_std],
    ignore_index=True,
    sort=False
)
print(f"\nAfter concat: {unified.shape}")

# Remove duplicates
unified = unified.drop_duplicates()
print(f"After dedup: {unified.shape}")

# Shuffle rows
unified = unified.sample(frac=1, random_state=42).reset_index(drop=True)

# Trim to exactly 75,000
unified = unified.iloc[:75000]
print(f"After trim to 75K: {unified.shape}")

# ══════════════════════════════════════════════════════════════════════════
# STEP 6 — Add diabetes TYPE column (6 classes)
# 0=No Diabetes, 1=Pre-Diabetes, 2=Type1, 3=Type2,
# 4=Gestational, 5=Child Diabetes
# ══════════════════════════════════════════════════════════════════════════
def classify_diabetes_type(row):
    label   = row['diabetes_label']
    age     = row['age']
    gender  = str(row['gender']).strip().lower()
    preg    = row['pregnancies']
    insulin = row['insulin']
    glucose = row['glucose']
    hba1c   = row['hba1c']

    # No diabetes
    if label == 0:
        return 0

    # Pre-diabetes (DS3 class 1)
    if label == 1 and row['source'] == 'ds3_brfss':
        return 1

    # Borderline HbA1c → pre-diabetes
    if label == 0 and pd.notna(hba1c) and 5.7 <= hba1c < 6.5:
        return 1

    # From here: confirmed diabetic (label == 1 from DS1/DS2/DS4,
    #            or label == 2 from DS3)
    actual_diabetic = (label == 1) or (label == 2)
    if not actual_diabetic:
        return 0

    # Gestational — check FIRST (overrides age rules)
    if gender == 'female' and pd.notna(preg) and preg >= 1:
        return 4

    # Child diabetes (under 18)
    if pd.notna(age) and age < 18:
        return 5

    # Type 1 — young onset (under 30) with low/no insulin
    if pd.notna(age) and age < 30:
        low_insulin = (pd.notna(insulin) and insulin <= 15) or pd.isna(insulin)
        if low_insulin:
            return 2  # Type 1

    # Type 2 — age 30+ OR older diabetic
    return 3

unified['diabetes_type'] = unified.apply(classify_diabetes_type, axis=1)

# Map numbers to readable names
type_names = {
    0: 'No Diabetes',
    1: 'Pre-Diabetes',
    2: 'Type 1 Diabetes',
    3: 'Type 2 Diabetes',
    4: 'Gestational Diabetes',
    5: 'Child Diabetes'
}
unified['diabetes_type_name'] = unified['diabetes_type'].map(type_names)

# ══════════════════════════════════════════════════════════════════════════
# STEP 7 — Add helper columns
# ══════════════════════════════════════════════════════════════════════════
unified['has_pregnancy_data'] = unified['pregnancies'].notna().astype(int)

unified['age_group'] = pd.cut(
    unified['age'],
    bins=[0, 12, 17, 29, 44, 59, 79, 200],
    labels=['Child', 'Teen', 'Young Adult', 'Adult', 'Middle Age', 'Senior', 'Elderly']
)

# ══════════════════════════════════════════════════════════════════════════
# STEP 8 — Final verification report
# ══════════════════════════════════════════════════════════════════════════
print("\n" + "="*50)
print("       FINAL UNIFIED DATASET REPORT")
print("="*50)
print(f"Total records   : {len(unified)}")
print(f"Total columns   : {len(unified.columns)}")
print(f"Columns         : {list(unified.columns)}")

print(f"\n--- Source breakdown ---")
print(unified['source'].value_counts())

print(f"\n--- Diabetes type distribution ---")
print(unified['diabetes_type_name'].value_counts())

print(f"\n--- Gender split ---")
print(unified['gender'].value_counts())

print(f"\n--- Age group split ---")
print(unified['age_group'].value_counts())

print(f"\n--- Missing values per column ---")
print(unified.isnull().sum())

# ══════════════════════════════════════════════════════════════════════════
# STEP 9 — Save
# ══════════════════════════════════════════════════════════════════════════
unified.to_csv('unifieddataset', index=False)
print("\n✓ Saved: unifieddataset")
print(f"  Shape: {unified.shape}")