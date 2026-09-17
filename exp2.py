#EXPERIMENT 2 - ANALYSIS (predicted vs. given rating, combined across participants)

import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

def predicted_rating_from_filename(filename):
    # "syn_img_5_2.03.jpg" -> 2.03 (the duplicate number, "5", doesn't matter)
    stem = filename.rsplit(".", 1)[0]
    return float(stem.rsplit("_", 1)[1])

exp2_files = sorted(glob.glob("exp2_*.csv"))
print("Found participant files:", exp2_files)

all_long = []

for file in exp2_files:
    participant = file.replace("exp2_", "").replace(".csv", "")

    df = pd.read_csv(file)
    df["Predicted"] = df["Image"].apply(predicted_rating_from_filename)
    df["Participant"] = participant

    long_df = df.melt(
        id_vars=["Image", "Predicted", "Participant"],
        value_vars=["Rating 1", "Rating 2"],
        var_name="Presentation",
        value_name="Given"
    )
    all_long.append(long_df)

long_df = pd.concat(all_long, ignore_index=True)

rho, p_value = spearmanr(long_df["Predicted"], long_df["Given"])
print(f"\nCombined: Spearman rho = {rho:.3f} (p = {p_value:.4f}), n = {len(long_df)}")

predicted_levels = sorted(long_df["Predicted"].unique())
grouped_ratings = [
    long_df.loc[long_df["Predicted"] == level, "Given"]
    for level in predicted_levels
]

# Size boxes to the tightest gap between neighbouring levels so they don't overlap
if len(predicted_levels) > 1:
    min_gap = np.diff(predicted_levels).min()
    box_width = min(min_gap * 0.6, 0.3)
else:
    box_width = 0.3

fig, ax = plt.subplots(figsize=(10, 5))
ax.boxplot(grouped_ratings, positions=predicted_levels, widths=box_width)
lims = [min(predicted_levels), max(predicted_levels)]
ax.plot(lims, lims, "r--", alpha=0.5, label="Perfect agreement")
ax.set_xlabel("Predicted rating (from linear model)")
ax.set_ylabel("Given rating")
ax.set_title(f"Experiment 2 — combined (Spearman ρ = {rho:.3f})")
ax.set_xticks(predicted_levels)
ax.set_xticklabels([f"{v:.2f}" for v in predicted_levels], rotation=45, ha="right", fontsize=8)
ax.legend()
plt.tight_layout()
plt.show()