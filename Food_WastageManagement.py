# ====================================================
# EDA — LOCAL FOOD WASTAGE MANAGEMENT SYSTEM
# ====================================================
# ── Install libraries ────────────────────────────────────
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import mysql.connector
import warnings
warnings.filterwarnings("ignore")

# ── Path ────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
CHART_DIR = os.path.join(BASE_DIR, "eda_charts")
os.makedirs(CHART_DIR, exist_ok=True)

def csv_path(filename):
    return os.path.join(BASE_DIR, filename)

# ── Load Data ────────────────────────────────────────────────
providers = pd.read_csv(os.path.join(BASE_DIR, "providers.csv"))
receivers = pd.read_csv(os.path.join(BASE_DIR, "receivers.csv"))
food      = pd.read_csv(os.path.join(BASE_DIR, "food_listings.csv"))
claims    = pd.read_csv(os.path.join(BASE_DIR, "claims.csv"))
claims["Timestamp"] = pd.to_datetime(claims["Timestamp"])

# ── Merged tables ────────────────────────────────────────────────
cf  = claims.merge(food, on="Food_ID").merge(providers, on="Provider_ID", suffixes=("","_p"))
cfr = cf.merge(receivers, on="Receiver_ID", suffixes=("","_r"))

# print(f"Loaded: {len(providers)} providers | {len(receivers)} receivers | "
#      f"{len(food)} food listings | {len(claims)} claims")

GREEN = ["#1a4731","#2d7a50","#4caf7a","#a7f3c8"]
STATUS_CLR = {"Completed":"#2d7a50","Pending":"#f59e0b","Cancelled":"#ef4444"}

def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(CHART_DIR, f"{name}.png"), bbox_inches="tight", dpi=130)
    plt.close(fig)
    #print(f"  Saved: {name}.png")

def bar_pie(series, title, fname):
    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4))
    series.plot.bar(ax=a, color=GREEN[:len(series)], edgecolor="white", legend=False)
    a.set_title(f"{title} — Count"); a.set_xlabel(""); a.set_ylabel("Count")
    for i, v in enumerate(series): a.text(i, v+1, str(v), ha="center", fontsize=9, fontweight="bold")
    b.pie(series.values, labels=series.index, autopct="%1.1f%%",
          colors=GREEN[:len(series)], wedgeprops={"edgecolor":"white"})
    b.set_title(f"{title} — Share")
    fig.suptitle(title, fontweight="bold", color="#1a4731")
    save(fig, fname)

# ════════════════════════════════════════════════════════════
# SECTION 1 — UNIVARIATE (4 charts)
# ════════════════════════════════════════════════════════════
# print("\n--- Univariate ---")

bar_pie(providers["Type"].value_counts(),  "Provider Type Distribution",  "01_provider_type")
bar_pie(receivers["Type"].value_counts(),  "Receiver Type Distribution",  "02_receiver_type")
bar_pie(food["Food_Type"].value_counts(),  "Food Type Distribution",      "03_food_type")
bar_pie(food["Meal_Type"].value_counts(),  "Meal Type Distribution",      "04_meal_type")

# ════════════════════════════════════════════════════════════
# SECTION 2 — BIVARIATE (4 charts)
# ════════════════════════════════════════════════════════════
# print("\n--- Bivariate ---")

# Chart 5 — City vs Listings
fig, ax = plt.subplots(figsize=(12, 5))
d = food["Location"].value_counts().head(15)
d[::-1].plot.barh(ax=ax, color="#2d7a50", edgecolor="white")
ax.set_title("Top 15 Cities by Food Listings", fontweight="bold")
ax.set_xlabel("Listings"); ax.set_ylabel("City")
save(fig, "05_city_vs_listings")

# Chart 6 — Provider Type vs Quantity
fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4))
pt = food.groupby("Provider_Type")["Quantity"].agg(["sum","mean"])
pt["sum"].plot.bar(ax=a, color=GREEN, edgecolor="white", legend=False)
a.set_title("Total Quantity by Provider Type"); a.set_xlabel("")
pt["mean"].plot.bar(ax=b, color=GREEN, edgecolor="white", legend=False)
b.set_title("Avg Quantity by Provider Type"); b.set_xlabel("")
fig.suptitle("Provider Type vs Quantity", fontweight="bold", color="#1a4731")
save(fig, "06_provider_vs_quantity")

# Chart 7 — Food Type vs Quantity
fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4))
ft = food.groupby("Food_Type")["Quantity"].agg(["sum","mean"])
ft["sum"].plot.bar(ax=a, color=GREEN[:3], edgecolor="white", legend=False)
a.set_title("Total Quantity by Food Type"); a.set_xlabel("")
ft["mean"].plot.bar(ax=b, color=GREEN[:3], edgecolor="white", legend=False)
b.set_title("Avg Quantity by Food Type"); b.set_xlabel("")
fig.suptitle("Food Type vs Quantity", fontweight="bold", color="#1a4731")
save(fig, "07_foodtype_vs_quantity")

# Chart 8 — Meal Type vs Quantity
fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4))
mt = food.groupby("Meal_Type")["Quantity"].agg(["sum","mean"])
mt["sum"].plot.bar(ax=a, color=GREEN, edgecolor="white", legend=False)
a.set_title("Total Quantity by Meal Type"); a.set_xlabel("")
mt["mean"].plot.bar(ax=b, color=GREEN, edgecolor="white", legend=False)
b.set_title("Avg Quantity by Meal Type"); b.set_xlabel("")
fig.suptitle("Meal Type vs Quantity", fontweight="bold", color="#1a4731")
save(fig, "08_mealtype_vs_quantity")

# ════════════════════════════════════════════════════════════
# SECTION 3 — MULTIVARIATE (4 charts)
# ════════════════════════════════════════════════════════════
#print("\n--- Multivariate ---")

# Chart 9 — City + Provider Type + Quantity
fig, ax = plt.subplots(figsize=(13, 5))
top8 = food.groupby("Location")["Quantity"].sum().nlargest(8).index
(food[food["Location"].isin(top8)]
 .groupby(["Location","Provider_Type"])["Quantity"].sum()
 .unstack(fill_value=0)
 .plot.bar(ax=ax, color=GREEN, edgecolor="white", width=0.75))
ax.set_title("City + Provider Type + Quantity", fontweight="bold")
ax.set_xlabel("City"); ax.tick_params(axis="x", rotation=30)
ax.legend(title="Provider Type", bbox_to_anchor=(1,1))
save(fig, "09_city_provider_quantity")

# Chart 10 — Food Type + Meal Type heatmap
fig, ax = plt.subplots(figsize=(9, 4))
pivot = food.groupby(["Food_Type","Meal_Type"])["Quantity"].sum().unstack(fill_value=0)
sns.heatmap(pivot, annot=True, fmt=",d", cmap="Greens",
            linewidths=0.5, linecolor="white", ax=ax)
ax.set_title("Food Type × Meal Type × Quantity", fontweight="bold")
save(fig, "10_foodtype_mealtype_heatmap")

# Chart 11 — Provider + Claims + Quantity (bubble)
fig, ax = plt.subplots(figsize=(12, 5))
ps = (cf.groupby("Name").agg(Claims=("Claim_ID","count"), Qty=("Quantity","sum"))
        .reset_index().nlargest(15,"Claims"))
sc = ax.scatter(ps["Claims"], ps["Qty"], s=ps["Qty"]/5,
                c=ps["Claims"], cmap="Greens", alpha=0.8, edgecolors="#1a4731")
for _, row in ps.iterrows():
    ax.annotate(row["Name"][:10], (row["Claims"], row["Qty"]),
                xytext=(4,3), textcoords="offset points", fontsize=7)
plt.colorbar(sc, label="Claims")
ax.set_title("Top 15 Providers — Claims vs Quantity", fontweight="bold")
ax.set_xlabel("Claims"); ax.set_ylabel("Total Quantity")
save(fig, "11_provider_bubble")

# Chart 12 — Receiver + Claims + Quantity
fig, (a, b) = plt.subplots(1, 2, figsize=(13, 5))
rs = (cfr.groupby("Name_r").agg(Claims=("Claim_ID","count"), Qty=("Quantity","sum"))
         .reset_index().nlargest(12,"Claims"))
rs.columns = ["Receiver","Claims","Qty"]
rs[::-1].plot.barh(x="Receiver", y="Claims", ax=a, color="#2d7a50",
                   edgecolor="white", legend=False)
a.set_title("Top 12 Receivers — Claims"); a.set_xlabel("Claims")
rs[::-1].plot.barh(x="Receiver", y="Qty", ax=b, color="#4caf7a",
                   edgecolor="white", legend=False)
b.set_title("Top 12 Receivers — Quantity"); b.set_xlabel("Total Qty")
fig.suptitle("Receiver Analysis", fontweight="bold", color="#1a4731")
save(fig, "12_receiver_claims_quantity")

# ════════════════════════════════════════════════════════════
# SECTION 4 — CLAIM ANALYSIS (3 charts)
# ════════════════════════════════════════════════════════════
#print("\n--- Claim Analysis ---")

# Chart 13 — Claim Status
bar_pie(claims["Status"].value_counts(), "Claim Status Distribution", "13_claim_status")

# Chart 14 — Top Receivers
fig, (a, b) = plt.subplots(1, 2, figsize=(13, 5))
(cfr.groupby("Name_r")["Claim_ID"].count()
    .nlargest(10)[::-1].plot.barh(ax=a, color="#2d7a50", edgecolor="white"))
a.set_title("Top 10 Receivers by Claims"); a.set_xlabel("Claims")
(cfr.groupby(["Type_r","Status"])["Claim_ID"].count().unstack(fill_value=0)
    .plot.bar(ax=b, color=STATUS_CLR, edgecolor="white"))
b.set_title("Receiver Type × Status"); b.set_xlabel("")
b.tick_params(axis="x", rotation=0); b.legend(title="Status")
fig.suptitle("Top Receivers Analysis", fontweight="bold", color="#1a4731")
save(fig, "14_top_receivers")

# Chart 15 — Top Providers
fig, (a, b) = plt.subplots(1, 2, figsize=(13, 5))
(cf[cf["Status"]=="Completed"].groupby("Name")["Claim_ID"].count()
   .nlargest(10)[::-1].plot.barh(ax=a, color="#1a4731", edgecolor="white"))
a.set_title("Top 10 Providers — Completed Claims"); a.set_xlabel("Claims")
(cf.groupby(["Provider_Type","Status"])["Claim_ID"].count().unstack(fill_value=0)
   .plot.bar(ax=b, color=STATUS_CLR, edgecolor="white"))
b.set_title("Provider Type × Status"); b.set_xlabel("")
b.tick_params(axis="x", rotation=15); b.legend(title="Status")
fig.suptitle("Top Providers Analysis", fontweight="bold", color="#1a4731")
save(fig, "15_top_providers")

# Bonus — Monthly Trend
claims["Month"] = claims["Timestamp"].dt.to_period("M").astype(str)
fig, ax = plt.subplots(figsize=(12, 4))
(claims.groupby(["Month","Status"])["Claim_ID"].count().unstack(fill_value=0)
       .plot(ax=ax, marker="o", color=STATUS_CLR))
ax.set_title("Monthly Claims Trend", fontweight="bold")
ax.set_xlabel("Month"); ax.set_ylabel("Claims")
ax.tick_params(axis="x", rotation=30); ax.legend(title="Status")
save(fig, "16_monthly_trend")