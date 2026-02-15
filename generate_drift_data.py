import pandas as pd
import numpy as np

# Define columns
columns = ['build_year', 'building_type_int', 'ceiling_height', 'flats_count', 'floors_total',
           'has_elevator', 'floor', 'is_apartment', 'kitchen_area', 'living_area', 'rooms', 'total_area',
           'district']

# 1. Generate Normal Data (10 rows)
normal_data = {
    'build_year': np.random.randint(1970, 2020, 10),
    'building_type_int': np.random.randint(1, 6, 10),
    'ceiling_height': np.round(np.random.uniform(2.5, 3.2, 10), 2),
    'flats_count': np.random.randint(20, 100, 10),
    'floors_total': np.random.randint(5, 25, 10),
    'has_elevator': np.random.randint(0, 2, 10),
    'floor': np.random.randint(1, 5, 10),
    'is_apartment': np.zeros(10, dtype=int),
    'kitchen_area': np.round(np.random.uniform(6, 15, 10), 1),
    'living_area': np.round(np.random.uniform(15, 40, 10), 1),
    'rooms': np.random.randint(1, 4, 10),
    'total_area': np.round(np.random.uniform(30, 80, 10), 1),
    'district': ['Central'] * 10
}
df_normal = pd.DataFrame(normal_data)

# 2. Generate Outliers (Drift) - Large Luxury Apartments (5 rows)
drift_data = {
    'build_year': np.random.randint(2000, 2023, 5),
    'building_type_int': [6] * 5,
    'ceiling_height': [4.5] * 5,
    'flats_count': [10] * 5,
    'floors_total': [50] * 5,
    'has_elevator': [1] * 5,
    'floor': [45] * 5,
    'is_apartment': [1] * 5,
    'kitchen_area': [50.0] * 5,
    'living_area': [150.0] * 5,
    'rooms': [5] * 5,
    'total_area': [250.0, 300.0, 180.0, 400.0, 500.0], # > 120
    'district': ['Luxury'] * 5
}
df_drift = pd.DataFrame(drift_data)

# 3. Generate "Strange" Data - Very Old Buildings (3 rows)
old_data = df_normal.iloc[:3].copy()
old_data['build_year'] = [1850, 1900, 1920] # < 1950
old_data['district'] = 'OldTown'

# 4. Generate "Critical Errors" (Impossible Values) (3 rows)
error_data = df_normal.iloc[:3].copy()
# Row 1: Negative Area
error_data.iloc[0, error_data.columns.get_loc('total_area')] = -50.0
error_data.iloc[0, error_data.columns.get_loc('district')] = 'Error_NegArea'
# Row 2: Future Year
error_data.iloc[1, error_data.columns.get_loc('build_year')] = 2050
error_data.iloc[1, error_data.columns.get_loc('district')] = 'Error_Future'
# Row 3: Negative Rooms
error_data.iloc[2, error_data.columns.get_loc('rooms')] = -2
error_data.iloc[2, error_data.columns.get_loc('district')] = 'Error_NegRooms'

# Combine all
df_final = pd.concat([df_normal, df_drift, old_data, error_data], ignore_index=True)

# Save
output_file = 'sample_data_drift.csv'
df_final.to_csv(output_file, index=False)
print(f"Generated {len(df_final)} rows in {output_file}")
print("Drift rows (Area > 120):", len(df_drift))
print("Old rows (Year < 1950):", len(old_data))
print("Error rows:", len(error_data))
