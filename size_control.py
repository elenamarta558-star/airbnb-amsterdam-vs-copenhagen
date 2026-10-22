import pandas as pd
import numpy as np

df = pd.read_csv('DATA/listings_processed.csv')

df_homes = df[df['room_type'] == 'Entire home/apt'].copy()
df_size = df_homes.dropna(subset=['accommodates']).copy()
df_size['price_per_guest'] = df_size['price'] / df_size['accommodates']
df_size['size_band'] = pd.cut(df_size['accommodates'], bins=[0, 2, 4, np.inf],
                              labels=['1-2 guests', '3-4 guests', '5+ guests'])

g = df_size.groupby(['size_band', 'market_city'], observed=False)

print("=== N (entire homes) ===")
print(g.size().unstack().to_string())

print("\n=== MEDIAN PRICE (EUR) ===")
price = g['price'].median().unstack()
print(price.round(1).to_string())

print("\n=== MEDIAN PRICE PER GUEST (EUR) ===")
print(g['price_per_guest'].median().unstack().round(1).to_string())

print("\n=== RATIO Amsterdam / Copenhagen (median price) ===")
print((price['Amsterdam'] / price['Copenhagen']).round(2).to_string())

print(f"\nEntire homes excluded (missing 'accommodates'): {len(df_homes) - len(df_size)}")

print("\n=== LINEAR FIT: price vs guest capacity ===")
for city in ['Amsterdam', 'Copenhagen']:
    d = df_size[df_size['market_city'] == city]
    slope, intercept = np.polyfit(d['accommodates'], d['price'], 1)
    print(f"{city}: {slope:+.2f} EUR/night per extra guest | intercept {intercept:.1f} EUR")



