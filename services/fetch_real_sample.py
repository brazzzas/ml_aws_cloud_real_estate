import psycopg
import pandas as pd
import random

# Credentials from notebook (Sprint 3)
postgres_creds = {
    'sslmode': 'require',
    'host': 'rc1b-uh7kdmcx67eomesf.mdb.yandexcloud.net',
    'port': '6432',
    'dbname': 'playground_mle_20251117_22f7bc33a6',
    'user': 'mle_20251117_22f7bc33a6_freetrack',
    'password': 'e71f60657f364f8eb322bfd24e981ae4'
}

TABLE_NAME = 'df_clean'

def fetch_data():
    try:
        print("Connecting to database...")
        with psycopg.connect(**postgres_creds) as conn:
            with conn.cursor() as cur:
                # Fetch 20 random rows
                query = f"SELECT * FROM {TABLE_NAME} ORDER BY RANDOM() LIMIT 20"
                print(f"Executing: {query}")
                cur.execute(query)
                data = cur.fetchall()
                cols = [col[0] for col in cur.description]

        df = pd.DataFrame(data, columns=cols)
        print(f"Fetched {len(df)} rows.")

        # Alignment with Notebook logic and Model expectations
        # 1. Drop technical columns
        cols_to_drop = ['id', 'latitude', 'longitude']
        existing_drop = [c for c in cols_to_drop if c in df.columns]
        if existing_drop:
            print(f"Dropping columns: {existing_drop}")
            df = df.drop(columns=existing_drop)

        # 2. Drop target column 'price' (since this is for prediction input simulation)
        if 'price' in df.columns:
            print("Dropping target column 'price' for inference simulation.")
            df = df.drop(columns=['price'])
        
        # 3. Validation: Ensure 'district' is present
        if 'district' not in df.columns:
            print("WARNING: 'district' column missing!")

        # Save to CSV
        output_file = 'sample_data.csv'
        df.to_csv(output_file, index=False)
        print(f"✅ Successfully saved real sample data to {output_file}")
        print("Columns:", df.columns.tolist())
        print("\nFirst 3 rows:")
        print(df.head(3))

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fetch_data()
