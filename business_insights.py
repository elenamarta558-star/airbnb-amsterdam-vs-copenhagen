import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
 
sns.set_theme(style="whitegrid")
colors = {'Amsterdam': '#ff7f0e', 'Copenhagen': '#1f77b4'}
 
df = pd.read_csv('DATA/listings_processed.csv')
 
# --- DISTANCE FROM CENTER ---
centers = {
    'Amsterdam': (52.3731, 4.8926),     # Dam Square
    'Copenhagen': (55.6761, 12.5683),   # City Hall Square
}
 
def haversine(lat1, lon1, lat2, lon2):
    r = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return r * 2 * np.arcsin(np.sqrt(a))
 
df['distance'] = np.nan
for city, (lat, lon) in centers.items():
    m = df['market_city'] == city
    df.loc[m, 'distance'] = haversine(df.loc[m, 'latitude'], df.loc[m, 'longitude'], lat, lon)
 
labels = ['0-1 km', '1-2 km', '2-3 km', '3-5 km', '5+ km']
df['distance_band'] = pd.cut(df['distance'], bins=[0, 1, 2, 3, 5, np.inf], labels=labels)
df_homes = df[df['room_type'] == 'Entire home/apt'].copy()
 
# --- TABLES (printed so you can read the real numbers) ---
n_city = df['market_city'].value_counts()
median_room = df.groupby(['room_type', 'market_city'])['price'].median().unstack()
share_room = pd.crosstab(df['market_city'], df['room_type'], normalize='index') * 100
home_band_median = df_homes.groupby(['distance_band', 'market_city'], observed=False)['price'].median().unstack()
home_band_n = df_homes.groupby(['distance_band', 'market_city'], observed=False).size().unstack(fill_value=0)
band_share = pd.crosstab(df['distance_band'], df['market_city'], normalize='columns') * 100
 
print("=== LISTINGS PER CITY ===")
print(n_city.to_string())
print("\n=== MEDIAN PRICE BY ROOM TYPE (EUR) ===")
print(median_room.round(1).to_string())
ratio = median_room.loc['Entire home/apt', 'Amsterdam'] / median_room.loc['Entire home/apt', 'Copenhagen']
print(f"\nEntire-home ratio Amsterdam/Copenhagen: {ratio:.2f}x")
print("\n=== ROOM TYPE SHARE (%) ===")
print(share_room.round(1).to_string())
print("\n=== ENTIRE HOMES: MEDIAN PRICE BY DISTANCE BAND (EUR) ===")
print(home_band_median.round(1).to_string())
print("\n=== ENTIRE HOMES: N BY DISTANCE BAND ===")
print(home_band_n.to_string())
print("\n=== SHARE OF LISTINGS BY DISTANCE BAND (% of each city) ===")
print(band_share.round(1).to_string())
 
print("\n=== LINEAR FIT: entire-home price vs distance ===")
for city in ['Amsterdam', 'Copenhagen']:
    d = df_homes[df_homes['market_city'] == city].dropna(subset=['distance', 'price'])
    slope, intercept = np.polyfit(d['distance'], d['price'], 1)
    print(f"{city}: {slope:+.2f} EUR/night per km | intercept {intercept:.1f} EUR")
 
# --- CHART 1: median price by room type ---
plt.figure(figsize=(9, 6))
data1 = median_room.reset_index().melt(id_vars='room_type', var_name='market_city', value_name='price')
sns.barplot(data=data1, x='room_type', y='price', hue='market_city', palette=colors)
plt.title("Median price per night by room type")
plt.xlabel("Room type")
plt.ylabel("Median price per night (EUR)")
plt.legend(title="City")
plt.annotate(f"n: Amsterdam={n_city['Amsterdam']}, Copenhagen={n_city['Copenhagen']}",
             xy=(0.02, -0.15), xycoords='axes fraction', fontsize=8, color='#444444')
plt.tight_layout()
plt.savefig('CHART_median_price_room_type.png', dpi=300)
plt.close()
 
# --- CHART 2: room type share ---
fig, ax = plt.subplots(figsize=(8, 6))
share_room.plot(kind='bar', stacked=True, color=['#d62728', '#2ca02c', '#9467bd', '#bcbd22'][:share_room.shape[1]], ax=ax)
plt.title("Room type share by city")
plt.xlabel("City")
plt.ylabel("Share of listings (%)")
plt.xticks(rotation=0)
for p in ax.patches:
    w, h = p.get_width(), p.get_height()
    if h > 4:
        x, y = p.get_xy()
        ax.text(x + w / 2, y + h / 2, f"{h:.1f}%", ha='center', va='center', color='white', fontsize=9, weight='bold')
plt.legend(title="Room type", bbox_to_anchor=(1.02, 1), loc='upper left')
plt.annotate(f"n: Amsterdam={n_city['Amsterdam']}, Copenhagen={n_city['Copenhagen']}",
             xy=(0.02, -0.15), xycoords='axes fraction', fontsize=8, color='#444444')
plt.tight_layout()
plt.savefig('CHART_room_type_share.png', dpi=300)
plt.close()
 
# --- CHART 3: entire-home price by distance band ---
plt.figure(figsize=(10, 6))
data3 = home_band_median.reset_index().melt(id_vars='distance_band', var_name='market_city', value_name='price')
sns.lineplot(data=data3, x='distance_band', y='price', hue='market_city', marker='o',
             linewidth=2.5, palette=colors, sort=False)
plt.title("Entire homes: median price by distance from center")
plt.xlabel("Distance from city center")
plt.ylabel("Median price per night (EUR)")
plt.legend(title="City")
plt.tight_layout()
plt.savefig('CHART_price_by_distance_band.png', dpi=300)
plt.close()
 
# --- CHART 4: share of listings by distance band ---
plt.figure(figsize=(9, 6))
data4 = band_share.reset_index().melt(id_vars='distance_band', var_name='market_city', value_name='share')
sns.barplot(data=data4, x='distance_band', y='share', hue='market_city', palette=colors)
plt.title("Share of each city's listings by distance from center")
plt.xlabel("Distance from city center")
plt.ylabel("Share of city listings (%)")
plt.legend(title="City")
plt.tight_layout()
plt.savefig('CHART_listing_distribution_distance.png', dpi=300)
plt.close()
 
print("\nSaved 4 charts.")








        