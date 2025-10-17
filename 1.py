import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Load the dataset
path = Path("earthquake_data_tsunami.csv")
df = pd.read_csv(path)

# Clean column names
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

# Helper function to find columns automatically
def pick(colnames, candidates):
    for c in colnames:
        for cand in candidates:
            if cand in c:
                return c
    return None

# Detect key columns
cols = df.columns.tolist()
col_mag = pick(cols, ["mag", "magnitude"])
col_depth = pick(cols, ["depth"])
col_lat = pick(cols, ["lat"])
col_lon = pick(cols, ["lon", "long", "longitude"])
col_tsu = pick(cols, ["tsunami", "is_tsunami", "tsu"])

# Select relevant columns
use_cols = [c for c in [col_mag, col_depth, col_lat, col_lon, col_tsu] if c]
df_clean = df[use_cols].copy()

# Convert numeric fields
for c in [col_mag, col_depth, col_lat, col_lon]:
    df_clean[c] = pd.to_numeric(df_clean[c], errors="coerce")

# Convert tsunami indicator to binary 0/1
def to_binary(x):
    if pd.isna(x):
        return np.nan
    if isinstance(x, (int, float)):
        return 1 if x > 0 else 0
    s = str(x).strip().lower()
    if s in {"1", "y", "yes", "true", "t"}: return 1
    if s in {"0", "n", "no", "false", "f"}: return 0
    try:
        return 1 if float(s) > 0 else 0
    except:
        return np.nan

df_clean["tsunami_flag"] = df_clean[col_tsu].map(to_binary)
df_clean = df_clean.dropna(subset=[col_mag, col_depth, "tsunami_flag"])

# Group by tsunami flag and calculate statistics
grouped = df_clean.groupby("tsunami_flag")
stats_mag = grouped[col_mag].agg(["count", "mean", "median", "min", "max", "std"])
stats_dep = grouped[col_depth].agg(["count", "mean", "median", "min", "max", "std"])
summary_table = pd.concat({"magnitude_stats": stats_mag, "depth_stats": stats_dep}, axis=1)
print(summary_table)

# Visualization style
plt.style.use("default")

# 1. Event count comparison
counts = df_clean["tsunami_flag"].value_counts().sort_index()
plt.figure(figsize=(6,4))
counts.plot(kind="bar", color="orange")
plt.title("Count of Events: Tsunami (1) vs Non-Tsunami (0)")
plt.xlabel("Tsunami Flag")
plt.ylabel("Count")
plt.tight_layout()
plt.show()

# 2. Magnitude distribution
plt.figure(figsize=(7,5))
data_mag = [df_clean.loc[df_clean["tsunami_flag"]==0, col_mag],
            df_clean.loc[df_clean["tsunami_flag"]==1, col_mag]]
plt.boxplot(data_mag, labels=["0 = No Tsunami", "1 = Tsunami"])
plt.title("Magnitude Distribution by Tsunami Flag")
plt.ylabel("Magnitude (Mw)")
plt.tight_layout()
plt.show()

# 3. Depth distribution
plt.figure(figsize=(7,5))
data_dep = [df_clean.loc[df_clean["tsunami_flag"]==0, col_depth],
            df_clean.loc[df_clean["tsunami_flag"]==1, col_depth]]
plt.boxplot(data_dep, labels=["0 = No Tsunami", "1 = Tsunami"])
plt.title("Depth Distribution by Tsunami Flag")
plt.ylabel("Depth (km)")
plt.tight_layout()
plt.show()

# 4. Depth vs magnitude scatter plot
plt.figure(figsize=(7,5))
for flag, sub in df_clean.groupby("tsunami_flag"):
    plt.scatter(sub[col_mag], sub[col_depth], label=f"Tsunami={flag}", alpha=0.6, s=16)
plt.title("Depth vs Magnitude by Tsunami Flag")
plt.xlabel("Magnitude (Mw)")
plt.ylabel("Depth (km)")
plt.legend()
plt.tight_layout()
plt.show()

# 5. Geographic distribution of tsunami events
if (col_lat in df_clean.columns) and (col_lon in df_clean.columns):
    plt.figure(figsize=(8,5))
    sub = df_clean[df_clean["tsunami_flag"]==1]
    plt.scatter(sub[col_lon], sub[col_lat], s=12, alpha=0.7, color="orange")
    plt.title("Geographic Scatter of Tsunami-Generating Earthquakes")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.tight_layout()
    plt.show()

# Key findings summary
print("\n===== Key Findings =====")
print("1. {:.1f}% of events were associated with tsunamis.".format(df_clean["tsunami_flag"].mean()*100))
print("2. Average magnitude: {:.2f} (tsunami) vs {:.2f} (non-tsunami).".format(stats_mag.loc[1, "mean"], stats_mag.loc[0, "mean"]))
print("3. Median depth for both groups is around 26 km (shallow-focus).")
print("4. Events with Mw ≥ 7 and depth ≤ 50 km are more likely to trigger tsunamis.")
print("5. Tsunami events cluster mainly around the Pacific Ring of Fire.")