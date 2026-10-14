import pandas as pd

ds1 = pd.read_csv('datasets/diabetes_prediction_dataset.csv')
ds2 = pd.read_csv('datasets/pima_diabetes.csv')
ds3 = pd.read_csv('datasets/diabetes_012_health_indicators_BRFSS2015.csv')
ds4 = pd.read_csv('datasets/Dataset_of_Diabetes.csv')

for name, df in [('DS1',ds1),('DS2',ds2),('DS3',ds3),('DS4',ds4)]:
    print(f"\n{'='*40}")
    print(f"{name} — Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Missing values:\n{df.isnull().sum()[df.isnull().sum()>0]}")
    print(df.head(2))