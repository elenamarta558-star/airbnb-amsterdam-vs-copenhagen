import pandas as pd

# --- LOAD ---
df_ams = pd.read_csv('DATA/amsterdam/AMS.gz', compression='gzip', low_memory=False)
df_cph = pd.read_csv('DATA/copenhagen/COPEN.gz', compression='gzip', low_memory=False)
df_ams['market_city'] = 'Amsterdam'
df_cph['market_city'] = 'Copenhagen'

# --- CHECK: are the files really the right cities? ---
print("=== FILE CHECK ===")
for name, d in [('Amsterdam', df_ams), ('Copenhagen', df_cph)]:
    print(f"{name}: rows={len(d)} | median lat={d['latitude'].median():.2f}, "
          f"median lon={d['longitude'].median():.2f} | snapshot={d['last_scraped'].max()}")
print("(Amsterdam should be ~52.37, 4.89 | Copenhagen should be ~55.68, 12.57)\n")

df_raw = pd.concat([df_ams, df_cph], ignore_index=True)

print("=== DATA CLEANING ===")
print(f"Initial raw rows combined: {len(df_raw)}")

# 1. Price formatting
df_raw['price'] = df_raw['price'].astype(str).str.replace(r'[^0-9.]', '', regex=True)
df_raw['price'] = pd.to_numeric(df_raw['price'], errors='coerce')

# 2. DKK -> EUR for Copenhagen (before any filter)
cph_mask = df_raw['market_city'] == 'Copenhagen'
df_raw.loc[cph_mask, 'price'] = df_raw.loc[cph_mask, 'price'] * 0.134

# 3. Zero / missing prices
df_step1 = df_raw[df_raw['price'] > 0].dropna(subset=['price'])
print(f"-> Dropped zero/missing prices: {len(df_raw) - len(df_step1)}")

# 4. Active listings only
active = (df_step1['availability_365'] > 0) | (df_step1['number_of_reviews_ltm'] > 0)
df_step2 = df_step1[active]
print(f"-> Dropped inactive listings: {len(df_step1) - len(df_step2)}")

# 5. Outliers (> 1000 EUR, after conversion)
df_clean = df_step2[df_step2['price'] <= 1000]
print(f"-> Dropped outliers (>1000 EUR): {len(df_step2) - len(df_clean)}")

print(f"\nFinal clean rows: {len(df_clean)}")
print(df_clean['market_city'].value_counts().to_string())

df_clean.to_csv('DATA/listings_processed.csv', index=False)
print("\nSaved: DATA/listings_processed.csv")

