# ====================================================
# EDA — LOCAL FOOD WASTAGE MANAGEMENT SYSTEM
# ====================================================
# ── Install libraries ────────────────────────────────────
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
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

# ====================================================
# Streamlit App — Local Food Wastage Management System
# ====================================================

# ── MySQL Config ──────────────────────────────────────────────
DB_CONFIG = dict(host="localhost", port=3306,
                 user="root", password=" ",
                 database="food_wastage")

# ── Page Setup ────────────────────────────────────────────────
st.set_page_config(page_title="Food Wastage MS", page_icon="🌿", layout="wide")
st.markdown("""
<style>
[data-testid="stSidebar"]{background:#1a4731}
[data-testid="stSidebar"] *{color:#e0f0e8 !important}
.metric-box{background:white;border-left:4px solid #2d7a50;
            border-radius:10px;padding:1rem 1.2rem;
            box-shadow:0 2px 8px rgba(0,0,0,.07);margin-bottom:.5rem}
.metric-box .num{font-size:1.8rem;font-weight:700;color:#1a4731}
.metric-box .lbl{font-size:.72rem;color:#6b7280;text-transform:uppercase;letter-spacing:.07em}
.sql{background:#1e2a22;color:#7ee8a2;font-family:monospace;font-size:.8rem;
     padding:.9rem 1.1rem;border-radius:8px;white-space:pre-wrap;margin-bottom:.6rem}
.insight-box{background:#f0faf4;border-left:4px solid #2d7a50;
             border-radius:8px;padding:.8rem 1.1rem;margin-bottom:.5rem}
.insight-box .ititle{font-weight:700;color:#1a4731;font-size:.95rem}
.insight-box .iq{color:#6b7280;font-size:.82rem;margin:.2rem 0}
.insight-box .ival{font-size:1.1rem;color:#2d7a50;font-weight:600;margin-top:.2rem}
</style>""", unsafe_allow_html=True)

# ── DB Helpers ────────────────────────────────────────────────
@st.cache_resource
def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

def q(sql, params=None):
    conn = get_conn()
    try:
        return pd.read_sql(sql, conn, params=params)
    except Exception:
        conn.reconnect()
        return pd.read_sql(sql, conn, params=params)

def run(sql, params=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params or ())
    conn.commit(); cur.close()

G = px.colors.sequential.Greens

with st.sidebar:
    st.markdown("### 🌿 FoodShare Hub")
    st.markdown("---")
    page = st.radio(
        label="Navigation",                        
        options=[
            "🏠 Dashboard",
            "📊 SQL Queries (15)",
            "🗂️ Browse Data",
            "✏️ CRUD",
            "🔍 Search & Filter",
            "💡 Business Insights",                
        ],
        label_visibility="collapsed"               
    )
    st.markdown("---")
    st.markdown(f"🥗 **{int(q('SELECT SUM(Quantity) t FROM food_listings').iloc[0,0]):,}** food units")
    st.markdown(f"📋 **{q('SELECT COUNT(*) t FROM claims').iloc[0,0]:,}** claims")
    st.markdown(f"🏪 **{q('SELECT COUNT(*) t FROM providers').iloc[0,0]:,}** providers")
    st.markdown(f"👥 **{q('SELECT COUNT(*) t FROM receivers').iloc[0,0]:,}** receivers")

# ══════════════════════════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":
    st.markdown("## 🌿 Local Food Wastage Management System")
    st.markdown("Connecting surplus food with those in need.")
    st.markdown("---")

    total   = int(q("SELECT SUM(Quantity) t FROM food_listings").iloc[0,0])
    comp    = q("SELECT COUNT(*) t FROM claims WHERE Status='Completed'").iloc[0,0]
    pend    = q("SELECT COUNT(*) t FROM claims WHERE Status='Pending'").iloc[0,0]
    cities  = q("SELECT COUNT(DISTINCT Location) t FROM food_listings").iloc[0,0]
    total_c = q("SELECT COUNT(*) t FROM claims").iloc[0,0]

    cols = st.columns(5)
    for col, num, lbl in zip(cols,
        [f"{total:,}", total_c, comp, pend, cities],
        ["Food Units","Total Claims","Completed","Pending","Cities"]):
        col.markdown(f'<div class="metric-box"><div class="num">{num}</div>'
                     f'<div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        df = q("SELECT Status, COUNT(*) n FROM claims GROUP BY Status")
        st.plotly_chart(px.pie(df, names="Status", values="n", hole=.4,
            title="Claim Status",
            color_discrete_sequence=["#2d7a50","#f59e0b","#ef4444"]),
            use_container_width=True)
    with c2:
        df = q("SELECT Food_Type, SUM(Quantity) Qty FROM food_listings GROUP BY Food_Type")
        st.plotly_chart(px.bar(df, x="Food_Type", y="Qty",
            title="Food Type vs Quantity",
            color="Food_Type", color_discrete_sequence=G),
            use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        df = q("SELECT Location City, COUNT(*) n FROM food_listings GROUP BY Location ORDER BY n DESC LIMIT 10")
        st.plotly_chart(px.bar(df, x="n", y="City", orientation="h",
            title="Top 10 Cities by Listings",
            color="n", color_continuous_scale="Greens"),
            use_container_width=True)
    with c4:
        df = q("""SELECT f.Meal_Type, COUNT(c.Claim_ID) Claims
                  FROM food_listings f JOIN claims c ON f.Food_ID=c.Food_ID
                  GROUP BY f.Meal_Type ORDER BY Claims DESC""")
        st.plotly_chart(px.bar(df, x="Meal_Type", y="Claims",
            title="Meal Type vs Claims",
            color="Meal_Type", color_discrete_sequence=G),
            use_container_width=True)

    df = q("SELECT DATE_FORMAT(Timestamp,'%Y-%m') Month, COUNT(*) Claims FROM claims GROUP BY Month ORDER BY Month")
    st.plotly_chart(px.line(df, x="Month", y="Claims", markers=True,
        title="Monthly Claims Trend", color_discrete_sequence=["#2d7a50"]),
        use_container_width=True)

# ══════════════════════════════════════════════════════════════
# PAGE 2 — SQL QUERIES
# ══════════════════════════════════════════════════════════════
elif page == "📊 SQL Queries (15)":
    st.markdown("## 📊 All 15 SQL Queries")

    QUERIES = {
        "Q1 · Providers & Receivers per City": {
            "desc": "How many food providers and receivers are there in each city?",
            "sql":  "SELECT p.City, COUNT(DISTINCT p.Provider_ID) AS Total_Providers, COUNT(DISTINCT r.Receiver_ID) AS Total_Receivers FROM providers p LEFT JOIN receivers r ON p.City=r.City GROUP BY p.City ORDER BY Total_Providers DESC LIMIT 10",
            "chart": ("bar","City","Total_Providers")},
        "Q2A · Provider Type Contribution": {
            "desc": "Which type of food provider contributes the most food?",
            "sql":  "SELECT Provider_Type, COUNT(*) AS Total_Listings, SUM(Quantity) AS Total_Quantity FROM food_listings GROUP BY Provider_Type ORDER BY Total_Quantity DESC",
            "chart": ("pie","Provider_Type","Total_Quantity")},
        "Q2B · Receivers by City": {
            "desc": "How many receivers are there in each city?",
            "sql":  "SELECT City, COUNT(Receiver_ID) AS Total_Receivers, COUNT(DISTINCT Type) AS Receiver_Types FROM receivers GROUP BY City ORDER BY Total_Receivers DESC LIMIT 10",
            "chart": ("bar","City","Total_Receivers")},
        "Q3 · Provider Contacts by City": {
            "desc": "Contact information of food providers in a specific city.",
            "sql":  "SELECT Name, Type, Address, City, Contact FROM providers WHERE City='New Jessica' ORDER BY Name",
            "chart": None},
        "Q4 · Top Receivers by Claims": {
            "desc": "Which receivers have claimed the most food?",
            "sql":  "SELECT r.Name, r.Type, r.City, COUNT(c.Claim_ID) AS Total_Claims FROM receivers r JOIN claims c ON r.Receiver_ID=c.Receiver_ID GROUP BY r.Receiver_ID, r.Name, r.Type, r.City ORDER BY Total_Claims DESC LIMIT 10",
            "chart": ("bar","Name","Total_Claims")},
        "Q5 · Total Food Available": {
            "desc": "What is the total quantity of food available?",
            "sql":  "SELECT SUM(Quantity) AS Total_Quantity, COUNT(*) AS Total_Listings, ROUND(AVG(Quantity),1) AS Avg_Per_Listing FROM food_listings",
            "chart": None},
        "Q6 · Top Cities by Listings": {
            "desc": "Which city has the highest number of food listings?",
            "sql":  "SELECT Location AS City, COUNT(*) AS Listings, SUM(Quantity) AS Total_Qty FROM food_listings GROUP BY Location ORDER BY Listings DESC LIMIT 10",
            "chart": ("bar","City","Listings")},
        "Q7 · Most Common Food Types": {
            "desc": "What are the most commonly available food types?",
            "sql":  "SELECT Food_Type, COUNT(*) AS Listings, SUM(Quantity) AS Total_Qty, ROUND(AVG(Quantity),1) AS Avg_Qty FROM food_listings GROUP BY Food_Type ORDER BY Listings DESC",
            "chart": ("bar","Food_Type","Total_Qty")},
        "Q8 · Claims per Food Item": {
            "desc": "How many claims have been made for each food item?",
            "sql":  "SELECT f.Food_Name, COUNT(c.Claim_ID) AS Total_Claims FROM food_listings f JOIN claims c ON f.Food_ID=c.Food_ID GROUP BY f.Food_ID, f.Food_Name ORDER BY Total_Claims DESC LIMIT 10",
            "chart": ("bar","Food_Name","Total_Claims")},
        "Q9 · Providers with Most Successful Claims": {
            "desc": "Which provider has the highest number of completed claims?",
            "sql":  "SELECT p.Name, p.Type, p.City, COUNT(c.Claim_ID) AS Completed_Claims FROM providers p JOIN food_listings f ON p.Provider_ID=f.Provider_ID JOIN claims c ON f.Food_ID=c.Food_ID WHERE c.Status='Completed' GROUP BY p.Provider_ID, p.Name, p.Type, p.City ORDER BY Completed_Claims DESC LIMIT 10",
            "chart": ("bar","Name","Completed_Claims")},
        "Q10 · Claim Status %": {
            "desc": "What percentage of claims are completed vs pending vs cancelled?",
            "sql":  "SELECT Status, COUNT(*) AS Count, ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM claims),2) AS Percentage FROM claims GROUP BY Status",
            "chart": ("pie","Status","Count")},
        "Q11 · Avg Quantity per Receiver": {
            "desc": "What is the average quantity of food claimed per receiver?",
            "sql":  "SELECT r.Name, r.Type, COUNT(c.Claim_ID) AS Claims, ROUND(AVG(f.Quantity),1) AS Avg_Qty FROM receivers r JOIN claims c ON r.Receiver_ID=c.Receiver_ID JOIN food_listings f ON c.Food_ID=f.Food_ID GROUP BY r.Receiver_ID, r.Name, r.Type ORDER BY Avg_Qty DESC LIMIT 10",
            "chart": ("bar","Name","Avg_Qty")},
        "Q12 · Most Claimed Meal Type": {
            "desc": "Which meal type is claimed the most?",
            "sql":  "SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims, SUM(f.Quantity) AS Total_Qty FROM food_listings f JOIN claims c ON f.Food_ID=c.Food_ID GROUP BY f.Meal_Type ORDER BY Total_Claims DESC",
            "chart": ("bar","Meal_Type","Total_Claims")},
        "Q13 · Total Donated per Provider": {
            "desc": "What is the total quantity donated by each provider?",
            "sql":  "SELECT p.Name, p.Type, p.City, SUM(f.Quantity) AS Total_Donated FROM providers p JOIN food_listings f ON p.Provider_ID=f.Provider_ID GROUP BY p.Provider_ID, p.Name, p.Type, p.City ORDER BY Total_Donated DESC LIMIT 10",
            "chart": ("bar","Name","Total_Donated")},
        "Q14 · Monthly Claims Trend": {
            "desc": "How have claims changed over time?",
            "sql":  "SELECT DATE_FORMAT(Timestamp,'%Y-%m') AS Month, COUNT(*) AS Total_Claims, SUM(CASE WHEN Status='Completed' THEN 1 ELSE 0 END) AS Completed, SUM(CASE WHEN Status='Pending' THEN 1 ELSE 0 END) AS Pending, SUM(CASE WHEN Status='Cancelled' THEN 1 ELSE 0 END) AS Cancelled FROM claims GROUP BY DATE_FORMAT(Timestamp,'%Y-%m') ORDER BY Month",
            "chart": ("line","Month","Total_Claims")},
        "Q15 · Provider Type x Food Type": {
            "desc": "Which provider types donate which food types?",
            "sql":  "SELECT Provider_Type, Food_Type, COUNT(*) AS Listings, SUM(Quantity) AS Total_Qty FROM food_listings GROUP BY Provider_Type, Food_Type ORDER BY Provider_Type, Total_Qty DESC",
            "chart": ("bar","Provider_Type","Total_Qty")},
    }

    sel  = st.selectbox("Select Query", list(QUERIES.keys()))
    info = QUERIES[sel]
    st.markdown(f"**Question:** {info['desc']}")
    st.markdown(f'<div class="sql">{info["sql"]}</div>', unsafe_allow_html=True)

    df = q(info["sql"])
    if info["chart"]:
        c1, c2 = st.columns(2)
        c1.dataframe(df, use_container_width=True, height=260)
        ctype, cx, cy = info["chart"]
        with c2:
            if ctype == "pie":
                fig = px.pie(df, names=cx, values=cy, hole=.4,
                             color_discrete_sequence=G)
            elif ctype == "line":
                fig = px.line(df, x=cx, y=cy, markers=True,
                              color_discrete_sequence=["#2d7a50"])
            else:
                fig = px.bar(df, x=cx, y=cy,
                             color_discrete_sequence=["#2d7a50"])
            fig.update_layout(height=260, margin=dict(t=10,b=5))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.markdown("### All 15 Query Results")
    for name, info in QUERIES.items():
        with st.expander(f"✅ {name}"):
            st.caption(info["desc"])
            st.dataframe(q(info["sql"]), use_container_width=True)

# ══════════════════════════════════════════════════════════════
# PAGE 3 — BROWSE DATA
# ══════════════════════════════════════════════════════════════
elif page == "🗂️ Browse Data":
    st.markdown("## 🗂️ Browse All Data")
    tab1, tab2, tab3, tab4 = st.tabs(
        ["🥗 Food Listings","🏪 Providers","👥 Receivers","📋 Claims"])

    with tab1:
        df = q("SELECT * FROM food_listings")
        c1,c2,c3,c4 = st.columns(4)
        city = c1.selectbox("City",          ["All"]+sorted(df.Location.unique()))
        ft   = c2.selectbox("Food Type",     ["All"]+sorted(df.Food_Type.unique()))
        mt   = c3.selectbox("Meal Type",     ["All"]+sorted(df.Meal_Type.unique()))
        pt   = c4.selectbox("Provider Type", ["All"]+sorted(df.Provider_Type.unique()))
        if city != "All": df = df[df.Location==city]
        if ft   != "All": df = df[df.Food_Type==ft]
        if mt   != "All": df = df[df.Meal_Type==mt]
        if pt   != "All": df = df[df.Provider_Type==pt]
        st.caption(f"{len(df)} records")
        st.dataframe(df, use_container_width=True, height=420)

    with tab2:
        df = q("SELECT * FROM providers")
        c1,c2 = st.columns(2)
        cf_ = c1.selectbox("City", ["All"]+sorted(df.City.unique()), key="pc")
        tf  = c2.selectbox("Type", ["All"]+sorted(df.Type.unique()), key="pt2")
        if cf_ != "All": df = df[df.City==cf_]
        if tf  != "All": df = df[df.Type==tf]
        st.caption(f"{len(df)} providers")
        st.dataframe(df, use_container_width=True, height=420)

    with tab3:
        df = q("SELECT * FROM receivers")
        rt = st.selectbox("Type", ["All"]+sorted(df.Type.unique()))
        if rt != "All": df = df[df.Type==rt]
        st.caption(f"{len(df)} receivers")
        st.dataframe(df, use_container_width=True, height=420)

    with tab4:
        df = q("SELECT * FROM claims")
        sf = st.selectbox("Status", ["All"]+sorted(df.Status.unique()))
        if sf != "All": df = df[df.Status==sf]
        st.caption(f"{len(df)} claims")
        st.dataframe(df, use_container_width=True, height=420)

# ══════════════════════════════════════════════════════════════
# PAGE 4 — CRUD
# ══════════════════════════════════════════════════════════════
elif page == "✏️ CRUD":
    st.markdown("## ✏️ CRUD Operations")
    tab1, tab2, tab3 = st.tabs(["➕ Add Listing","🔄 Update","🗑️ Delete"])

    with tab1:
        st.markdown("#### Add New Food Listing")
        c1,c2 = st.columns(2)
        fname = c1.text_input("Food Name")
        qty   = c2.number_input("Quantity", min_value=1, value=10)
        exp   = c1.date_input("Expiry Date")
        pid   = c2.number_input("Provider ID", min_value=1, value=1)
        ptyp  = c1.selectbox("Provider Type",
                             ["Restaurant","Grocery Store","Supermarket","Catering Service"])
        loc   = c2.text_input("City / Location")
        ftyp  = c1.selectbox("Food Type", ["Vegetarian","Non-Vegetarian","Vegan"])
        mtyp  = c2.selectbox("Meal Type", ["Breakfast","Lunch","Dinner","Snacks"])
        if st.button("➕ Add", type="primary"):
            if fname and loc:
                new_id = int(q("SELECT MAX(Food_ID) m FROM food_listings").iloc[0,0]) + 1
                run("INSERT INTO food_listings VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (new_id, fname, qty, str(exp), pid, ptyp, loc, ftyp, mtyp))
                st.success(f"✅ Added! Food ID: {new_id}")
            else:
                st.error("Food Name and Location are required.")

    with tab2:
        st.markdown("#### Update Claim Status")
        cid    = st.number_input("Claim ID", min_value=1, value=1)
        cur_df = q(f"SELECT Status FROM claims WHERE Claim_ID={int(cid)}")
        if len(cur_df): st.info(f"Current Status: **{cur_df.iloc[0,0]}**")
        ns = st.selectbox("New Status", ["Pending","Completed","Cancelled"])
        if st.button("🔄 Update Claim", type="primary"):
            run("UPDATE claims SET Status=%s WHERE Claim_ID=%s", (ns, int(cid)))
            st.success(f"✅ Claim {int(cid)} updated to {ns}")

        st.markdown("#### Update Food Quantity")
        fid  = st.number_input("Food ID", min_value=1, value=1, key="upd_f")
        nqty = st.number_input("New Quantity", min_value=0, value=10)
        if st.button("🔄 Update Quantity", type="primary"):
            run("UPDATE food_listings SET Quantity=%s WHERE Food_ID=%s", (nqty, int(fid)))
            st.success(f"✅ Food ID {int(fid)} quantity updated to {nqty}")

    with tab3:
        st.markdown("#### Delete a Food Listing")
        st.warning("⚠️ This is permanent.")
        did  = st.number_input("Food ID to Delete", min_value=1, value=1)
        prev = q(f"SELECT * FROM food_listings WHERE Food_ID={int(did)}")
        if len(prev):
            st.dataframe(prev, use_container_width=True)
            if st.button("🗑️ Confirm Delete", type="primary"):
                run("DELETE FROM food_listings WHERE Food_ID=%s", (int(did),))
                st.success(f"✅ Food ID {int(did)} deleted.")
        else:
            st.error("Food ID not found.")

# ══════════════════════════════════════════════════════════════
# PAGE 5 — SEARCH & FILTER
# ══════════════════════════════════════════════════════════════
elif page == "🔍 Search & Filter":
    st.markdown("## 🔍 Search & Filter")
    tab1, tab2 = st.tabs(["🍽️ Find Food","📞 Contacts"])

    with tab1:
        st.markdown("#### Search Available Food")
        c1,c2,c3,c4 = st.columns(4)
        cities = ["All"]+sorted(
            q("SELECT DISTINCT Location FROM food_listings ORDER BY Location")["Location"])
        sc = c1.selectbox("City",          cities)
        sf = c2.selectbox("Food Type",     ["All","Vegetarian","Non-Vegetarian","Vegan"])
        sm = c3.selectbox("Meal Type",     ["All","Breakfast","Lunch","Dinner","Snacks"])
        sp = c4.selectbox("Provider Type",
                          ["All","Restaurant","Grocery Store","Supermarket","Catering Service"])

        sql = """SELECT fl.Food_ID, fl.Food_Name, fl.Quantity, fl.Expiry_Date,
                        fl.Food_Type, fl.Meal_Type, fl.Location, fl.Provider_Type,
                        p.Name AS Provider_Name, p.Contact AS Provider_Contact
                 FROM food_listings fl
                 LEFT JOIN providers p ON fl.Provider_ID=p.Provider_ID WHERE 1=1"""
        params = []
        if sc != "All": sql += " AND fl.Location=%s";      params.append(sc)
        if sf != "All": sql += " AND fl.Food_Type=%s";     params.append(sf)
        if sm != "All": sql += " AND fl.Meal_Type=%s";     params.append(sm)
        if sp != "All": sql += " AND fl.Provider_Type=%s"; params.append(sp)
        sql += " ORDER BY fl.Expiry_Date ASC"

        df = pd.read_sql(sql, get_conn(), params=params if params else None)
        st.caption(f"**{len(df)}** listings found")
        st.dataframe(df, use_container_width=True, height=400)

    with tab2:
        st.markdown("#### Provider Contacts")
        c1,c2 = st.columns(2)
        scity = c1.text_input("Search City", placeholder="e.g. New Jessica")
        stype = c2.selectbox("Type",
                             ["All","Restaurant","Grocery Store","Supermarket","Catering Service"])
        sql2 = "SELECT Name, Type, Address, City, Contact FROM providers WHERE 1=1"
        p2   = []
        if scity: sql2 += " AND LOWER(City) LIKE %s"; p2.append(f"%{scity.lower()}%")
        if stype != "All": sql2 += " AND Type=%s";    p2.append(stype)
        df2 = pd.read_sql(sql2, get_conn(), params=p2 if p2 else None)
        st.caption(f"{len(df2)} providers found")
        st.dataframe(df2, use_container_width=True, height=350)

        st.markdown("#### Receiver Contacts")
        df3 = q("SELECT Name, Type, City, Contact FROM receivers ORDER BY City, Name")
        rt  = st.selectbox("Filter by Type", ["All"]+sorted(df3.Type.unique()))
        if rt != "All": df3 = df3[df3.Type==rt]
        st.dataframe(df3, use_container_width=True, height=280)

# ══════════════════════════════════════════════════════════════
# PAGE 6 — BUSINESS INSIGHTS
# ══════════════════════════════════════════════════════════════
elif page == "💡 Business Insights":
    st.markdown("## 💡 Business Insights")
    st.markdown("Key findings from SQL analysis of the food wastage dataset.")
    st.markdown("---")

    top_city     = q("SELECT Location, COUNT(*) n FROM food_listings GROUP BY Location ORDER BY n DESC LIMIT 1")
    top_meal     = q("SELECT Meal_Type, SUM(Quantity) qty FROM food_listings GROUP BY Meal_Type ORDER BY qty DESC LIMIT 1")
    top_provider = q("""SELECT p.Name, SUM(f.Quantity) qty
                        FROM providers p JOIN food_listings f ON p.Provider_ID=f.Provider_ID
                        GROUP BY p.Provider_ID ORDER BY qty DESC LIMIT 1""")
    top_receiver = q("""SELECT r.Name, COUNT(c.Claim_ID) n
                        FROM receivers r JOIN claims c ON r.Receiver_ID=c.Receiver_ID
                        GROUP BY r.Receiver_ID ORDER BY n DESC LIMIT 1""")
    comp_pct     = q("""SELECT ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM claims),1) pct
                        FROM claims WHERE Status='Completed'""")
    top_demand   = q("""SELECT f.Location, COUNT(c.Claim_ID) n
                        FROM food_listings f JOIN claims c ON f.Food_ID=c.Food_ID
                        GROUP BY f.Location ORDER BY n DESC LIMIT 1""")

    # 6 insight cards — displayed in Streamlit
    insights = [
        ("🏙️ Food Availability",
         "Which city has the most food?",
         f"{top_city.iloc[0]['Location']}  ({top_city.iloc[0]['n']} listings)"),
        ("🍽️ Food Waste",
         "Which meal gets wasted the most?",
         f"{top_meal.iloc[0]['Meal_Type']}  (Total Qty: {int(top_meal.iloc[0]['qty']):,})"),
        ("🏪 Provider Analysis",
         "Which provider contributes the most?",
         f"{top_provider.iloc[0]['Name']}  (Total Qty: {int(top_provider.iloc[0]['qty']):,})"),
        ("👥 Receiver Analysis",
         "Which receiver claims the most food?",
         f"{top_receiver.iloc[0]['Name']}  ({top_receiver.iloc[0]['n']} claims)"),
        ("📋 Claims Analysis",
         "What percentage of claims are completed?",
         f"{comp_pct.iloc[0]['pct']}% of all claims completed"),
        ("📍 Demand Analysis",
         "Which city has the highest food demand?",
         f"{top_demand.iloc[0]['Location']}  ({top_demand.iloc[0]['n']} claims)"),
    ]

    # Display 2 cards per row
    for i in range(0, len(insights), 2):
        c1, c2 = st.columns(2)
        for col, (title, question, answer) in zip([c1, c2], insights[i:i+2]):
            col.markdown(
                f'<div class="insight-box">'
                f'<div class="ititle">{title}</div>'
                f'<div class="iq">{question}</div>'
                f'<div class="ival">{answer}</div>'
                f'</div>',
                unsafe_allow_html=True)

    # Supporting charts
    st.markdown("---")
    st.markdown("### Supporting Charts")
    c1, c2 = st.columns(2)
    with c1:
        df = q("SELECT Status, COUNT(*) n FROM claims GROUP BY Status")
        st.plotly_chart(px.pie(df, names="Status", values="n", hole=.4,
            title="Claim Status Distribution",
            color_discrete_sequence=["#2d7a50","#f59e0b","#ef4444"]),
            use_container_width=True)
    with c2:
        df = q("""SELECT f.Location, COUNT(c.Claim_ID) Claims
                  FROM food_listings f JOIN claims c ON f.Food_ID=c.Food_ID
                  GROUP BY f.Location ORDER BY Claims DESC LIMIT 10""")
        st.plotly_chart(px.bar(df, x="Claims", y="Location", orientation="h",
            title="Top 10 Cities by Food Demand",
            color="Claims", color_continuous_scale="Greens"),
            use_container_width=True)

    df2 = q("SELECT Meal_Type, SUM(Quantity) Qty FROM food_listings GROUP BY Meal_Type ORDER BY Qty DESC")
    st.plotly_chart(px.bar(df2, x="Meal_Type", y="Qty",
        title="Total Quantity by Meal Type (Waste Risk)",
        color="Meal_Type", color_discrete_sequence=G),
        use_container_width=True)
    
    
    
    
    
    
    



