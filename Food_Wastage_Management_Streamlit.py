# ====================================================
# Streamlit App — Local Food Wastage Management System
# ====================================================
# ── Import libraries ────────────────────────────────────
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine, text
import warnings
warnings.filterwarnings("ignore")

# ── MySQL Config  ─────────────────────────────────────

import os

HOST     = os.environ.get("HOST", "localhost")
PORT     = int(os.environ.get("PORT", 3306))
USER     = os.environ.get("USER", "root")
PASSWORD = os.environ.get("PASSWORD", " ")
DATABASE = os.environ.get("DATABASE", "food_wastage")

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
def get_engine():
    from urllib.parse import quote_plus
    pwd = quote_plus(PASSWORD)   # converts @ to %40 automatically
    url = f"mysql+mysqlconnector://{USER}:{pwd}@{HOST}:{PORT}/{DATABASE}"
    return create_engine(url)

def q(sql, params=None):
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})

def run(sql, params=None):
    with get_engine().connect() as conn:
        conn.execute(text(sql), params or {})
        conn.commit()

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
            "📌 Recommendations",
        ],
        label_visibility="collapsed")
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
        df = q("""SELECT f.Meal_Type, COUNT(c.Claim_ID) Claims FROM food_listings f JOIN claims c ON f.Food_ID=c.Food_ID
                  GROUP BY f.Meal_Type ORDER BY Claims DESC""")
        st.plotly_chart(px.bar(df, x="Meal_Type", y="Claims",
            title="Meal Type vs Claims",
            color="Meal_Type", color_discrete_sequence=G),
            use_container_width=True)

    df = q("""SELECT DATE(Timestamp) AS Day, COUNT(*) AS Claims FROM claims GROUP BY DATE(Timestamp) ORDER BY Day""")
    st.plotly_chart(px.bar(df, x="Day", y="Claims",
    title="Daily Claims Trend (March 2025)",
    color="Claims", color_continuous_scale="Greens"),
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
    tab1, tab2, tab3 = st.tabs(
        ["🏪 Providers","👥 Receivers","📋 Claims"])

    with tab1:
        df = q("SELECT * FROM providers")
        c1,c2 = st.columns(2)
        cf_ = c1.selectbox("City", ["All"]+sorted(df.City.unique()), key="pc")
        tf  = c2.selectbox("Type", ["All"]+sorted(df.Type.unique()), key="pt2")
        if cf_ != "All": df = df[df.City==cf_]
        if tf  != "All": df = df[df.Type==tf]
        st.caption(f"{len(df)} providers")
        st.dataframe(df, use_container_width=True, height=420)

    with tab2:
        df = q("SELECT * FROM receivers")
        rt = st.selectbox("Type", ["All"]+sorted(df.Type.unique()))
        if rt != "All": df = df[df.Type==rt]
        st.caption(f"{len(df)} receivers")
        st.dataframe(df, use_container_width=True, height=420)

    with tab3:
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

    # ── TAB 1: ADD ────────────────────────────────────────────
    with tab1:
        st.markdown("#### Add New Food Listing")
        c1, c2 = st.columns(2)
        fname = c1.text_input("Food Name", placeholder="e.g. Rice Biryani")
        qty   = c2.number_input("Quantity", min_value=1, value=10)
        exp   = c1.date_input("Expiry Date")
        pid   = c2.number_input("Provider ID", min_value=1, value=1)
        ptyp  = c1.selectbox("Provider Type", ["Restaurant","Grocery Store","Supermarket","Catering Service"])
        loc   = c2.text_input("City / Location", placeholder="e.g. Mumbai")
        ftyp  = c1.selectbox("Food Type", ["Vegetarian","Non-Vegetarian","Vegan"])
        mtyp  = c2.selectbox("Meal Type", ["Breakfast","Lunch","Dinner","Snacks"])

        if st.button("➕ Add Listing", type="primary"):
            if fname and loc:
                new_id = int(q("SELECT MAX(Food_ID) m FROM food_listings").iloc[0,0]) + 1
                run("INSERT INTO food_listings VALUES (:a,:b,:c,:d,:e,:f,:g,:h,:i)",
                    {"a":new_id,"b":fname,"c":qty,"d":str(exp),"e":pid,"f":ptyp,"g":loc,"h":ftyp,"i":mtyp})
                st.success(f"✅ Added! New Food ID: **{new_id}**")
                st.markdown("**Newly added record:**")
                st.dataframe(q("SELECT * FROM food_listings WHERE Food_ID=:id", {"id":new_id}), use_container_width=True)
            else:
                st.error("❌ Food Name and Location are required.")

        st.markdown("**Latest 10 listings:**")
        st.dataframe(q("SELECT Food_ID, Food_Name, Quantity, Expiry_Date, Location, Food_Type, Meal_Type FROM food_listings ORDER BY Food_ID DESC LIMIT 10"), use_container_width=True)

    # ── TAB 2: UPDATE ─────────────────────────────────────────
    with tab2:
        st.markdown("#### Update Claim Status")
        cid    = st.number_input("Claim ID", min_value=1, value=1)
        cur_c  = q("SELECT Claim_ID, Food_ID, Receiver_ID, Status, Timestamp FROM claims WHERE Claim_ID=:id", {"id":int(cid)})
        if len(cur_c):
            st.markdown("**Current record:**"); st.dataframe(cur_c, use_container_width=True)
            ns = st.selectbox("New Status", ["Pending","Completed","Cancelled"])
            if st.button("🔄 Update Claim", type="primary"):
                run("UPDATE claims SET Status=:s WHERE Claim_ID=:id", {"s":ns,"id":int(cid)})
                st.success(f"✅ Claim {int(cid)}: **{cur_c.iloc[0]['Status']}** → **{ns}**")
                st.markdown("**Updated record:**")
                st.dataframe(q("SELECT Claim_ID, Food_ID, Receiver_ID, Status, Timestamp FROM claims WHERE Claim_ID=:id", {"id":int(cid)}), use_container_width=True)
        else:
            st.warning(f"⚠️ Claim ID {int(cid)} not found.")

        st.markdown("---")
        st.markdown("#### Update Food Quantity")
        fid     = st.number_input("Food ID", min_value=1, value=1, key="upd_f")
        cur_f   = q("SELECT Food_ID, Food_Name, Quantity, Expiry_Date, Location FROM food_listings WHERE Food_ID=:id", {"id":int(fid)})
        if len(cur_f):
            st.markdown("**Current record:**"); st.dataframe(cur_f, use_container_width=True)
            nqty = st.number_input("New Quantity", min_value=0, value=int(cur_f.iloc[0]["Quantity"]))
            if st.button("🔄 Update Quantity", type="primary"):
                run("UPDATE food_listings SET Quantity=:q WHERE Food_ID=:id", {"q":nqty,"id":int(fid)})
                st.success(f"✅ Food ID {int(fid)}: Qty **{int(cur_f.iloc[0]['Quantity'])}** → **{nqty}**")
                st.markdown("**Updated record:**")
                st.dataframe(q("SELECT Food_ID, Food_Name, Quantity, Expiry_Date, Location FROM food_listings WHERE Food_ID=:id", {"id":int(fid)}), use_container_width=True)
        else:
            st.warning(f"⚠️ Food ID {int(fid)} not found.")

    # ── TAB 3: DELETE ─────────────────────────────────────────
    with tab3:
        st.markdown("#### Delete a Food Listing")
        st.warning("⚠️ Permanent — linked claims are also deleted (CASCADE).")
        did  = st.number_input("Food ID to Delete", min_value=1, value=1)
        prev = q("SELECT * FROM food_listings WHERE Food_ID=:id", {"id":int(did)})
        if len(prev):
            st.markdown("**Record to be deleted:**"); st.dataframe(prev, use_container_width=True)
            linked = q("SELECT Claim_ID, Receiver_ID, Status FROM claims WHERE Food_ID=:id", {"id":int(did)})
            if len(linked):
                st.markdown(f"**⚠️ {len(linked)} linked claim(s) also deleted:**")
                st.dataframe(linked, use_container_width=True)
            if st.checkbox(f"I confirm deletion of Food ID {int(did)}"):
                if st.button("🗑️ Confirm Delete", type="primary"):
                    food_name = prev.iloc[0]["Food_Name"]
                    run("DELETE FROM food_listings WHERE Food_ID=:id", {"id":int(did)})
                    st.success(f"✅ **{food_name}** (ID: {int(did)}) deleted from MySQL.")
                    st.markdown("**Latest 10 listings after deletion:**")
                    st.dataframe(q("SELECT Food_ID, Food_Name, Quantity, Location FROM food_listings ORDER BY Food_ID DESC LIMIT 10"), use_container_width=True)
        else:
            st.error(f"❌ Food ID {int(did)} not found.")
            st.dataframe(q("SELECT Food_ID, Food_Name, Location FROM food_listings ORDER BY Food_ID DESC LIMIT 10"), use_container_width=True)

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

        sql = """SELECT fl.Food_ID, fl.Food_Name, fl.Quantity, fl.Expiry_Date, fl.Food_Type, fl.Meal_Type, fl.Location, 
                fl.Provider_Type, p.Name AS Provider_Name, p.Contact AS Provider_Contact FROM food_listings fl
         LEFT JOIN providers p ON fl.Provider_ID=p.Provider_ID WHERE 1=1"""
        params = {}
        if sc != "All": sql += " AND fl.Location=:city";        params["city"] = sc
        if sf != "All": sql += " AND fl.Food_Type=:ftype";      params["ftype"] = sf
        if sm != "All": sql += " AND fl.Meal_Type=:mtype";      params["mtype"] = sm
        if sp != "All": sql += " AND fl.Provider_Type=:ptype";  params["ptype"] = sp
        sql += " ORDER BY fl.Expiry_Date ASC"

        with get_engine().connect() as conn:
            df = pd.read_sql(text(sql), conn, params=params)
        
        st.caption(f"**{len(df)}** listings found")
        st.dataframe(df, use_container_width=True, height=400)

    with tab2:
        st.markdown("#### Provider Contacts")
        c1,c2 = st.columns(2)
        scity = c1.text_input("Search City", placeholder="e.g. New Jessica")
        stype = c2.selectbox("Type",
                             ["All","Restaurant","Grocery Store","Supermarket","Catering Service"])
        sql2 = "SELECT Name, Type, Address, City, Contact FROM providers WHERE 1=1"
        p2   = {}
        if scity: sql2 += " AND LOWER(City) LIKE :city"; p2["city"] = f"%{scity.lower()}%"
        if stype != "All": sql2 += " AND Type=:ptype";   p2["ptype"] = stype
        with get_engine().connect() as conn:
            df2 = pd.read_sql(text(sql2), conn, params=p2)
        
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

    # All 6 insight queries — only run when THIS page is active
    top_city     = q("SELECT Location, COUNT(*) n FROM food_listings GROUP BY Location ORDER BY n DESC LIMIT 1")
    top_meal     = q("SELECT Meal_Type, SUM(Quantity) qty FROM food_listings GROUP BY Meal_Type ORDER BY qty DESC LIMIT 1")
    top_provider = q("""SELECT p.Name, SUM(f.Quantity) qty FROM providers p JOIN food_listings f ON 
                        p.Provider_ID=f.Provider_ID GROUP BY p.Provider_ID ORDER BY qty DESC LIMIT 1""")
    top_receiver = q("""SELECT r.Name, COUNT(c.Claim_ID) n FROM receivers r JOIN claims c ON r.Receiver_ID=c.Receiver_ID
                        GROUP BY r.Receiver_ID ORDER BY n DESC LIMIT 1""")
    comp_pct     = q("""SELECT ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM claims),1) pct
                        FROM claims WHERE Status='Completed'""")
    top_demand   = q("""SELECT f.Location, COUNT(c.Claim_ID) n FROM food_listings f JOIN claims c ON f.Food_ID=c.Food_ID
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

# ══════════════════════════════════════════════════════════════
# PAGE 7 — RECOMMENDATIONS
# ══════════════════════════════════════════════════════════════
elif page == "📌 Recommendations":
    st.markdown("## 📌 Business Recommendations")
    st.markdown("Data-driven recommendations to improve food distribution and reduce wastage.")
    st.markdown("---")
    # ── Pull supporting data ──────────────────────────────────
    hw = q("SELECT f.Location, SUM(f.Quantity) Qty, COUNT(c.Claim_ID) Claims FROM food_listings f LEFT JOIN claims c ON f.Food_ID=c.Food_ID GROUP BY f.Location ORDER BY Qty DESC LIMIT 3")
    tp = q("SELECT p.Name, SUM(f.Quantity) Donated FROM providers p JOIN food_listings f ON p.Provider_ID=f.Provider_ID GROUP BY p.Provider_ID ORDER BY Donated DESC LIMIT 3")
    hd = q("SELECT f.Location, COUNT(c.Claim_ID) Claims FROM food_listings f JOIN claims c ON f.Food_ID=c.Food_ID GROUP BY f.Location ORDER BY Claims DESC LIMIT 3")
    ex = q("SELECT Food_Name, Location FROM food_listings ORDER BY Expiry_Date ASC LIMIT 1")
    cp = q("SELECT ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM claims),1) pct FROM claims WHERE Status='Cancelled'")
    # ── Card style ────────────────────────────────────────────
    st.markdown("""<style>
    .rc{background:white;border-radius:10px;border-top:4px solid #2d7a50;
        padding:1rem 1.2rem;box-shadow:0 2px 8px rgba(0,0,0,.07);margin-bottom:.8rem}
    .rn{font-size:.7rem;font-weight:700;color:#2d7a50;text-transform:uppercase;letter-spacing:.1em}
    .rt{font-size:1rem;font-weight:700;color:#1a4731;margin:.2rem 0 .4rem}
    .rb{font-size:.85rem;color:#374151;line-height:1.5;margin-bottom:.4rem}
    .rd{background:#f0faf4;border-radius:5px;padding:.35rem .7rem;
        font-size:.8rem;color:#1a4731;font-weight:600}
    </style>""", unsafe_allow_html=True)

    def rec_card(num, icon, title, body, data):
        st.markdown(f'<div class="rc"><div class="rn">Recommendation {num}</div>'
                    f'<div class="rt">{icon} {title}</div>'
                    f'<div class="rb">{body}</div>'
                    f'<div class="rd">{data}</div></div>', unsafe_allow_html=True)
    # ── 4 Required + 3 Additional recommendations ─────────────
    c1, c2 = st.columns(2)
    cities_hw = ", ".join(hw["Location"].tolist()) if len(hw) else "N/A"
    cities_hd = ", ".join(hd["Location"].tolist()) if len(hd) else "N/A"
    top_provs  = ", ".join(tp["Name"].tolist())    if len(tp) else "N/A"
    food_exp  = f"{ex.iloc[0]['Food_Name']} in {ex.iloc[0]['Location']}" if len(ex) else "N/A"
    cancel_pct = cp.iloc[0]["pct"] if len(cp) else 0

    with c1:
        rec_card(1, "🤝", "Expand NGO Partnerships in High Wastage Cities",
                 "Cities with high food quantity but low claims have surplus going to waste. "
                 "NGO partnerships here will ensure food reaches those in need before expiry.",
                 f"📍 High wastage cities: {cities_hw}")

        rec_card(3, "🔔", "Automate Food Expiry Notifications",
                 "Food listings near expiry should trigger automatic alerts to nearby receivers "
                 "to prevent perishable items from being wasted due to missed collection.",
                 f"⏰ Earliest expiring: {food_exp}")

        rec_card(5, "❌", "Reduce Cancelled Claims",
                 f"{cancel_pct}% of claims are cancelled — a significant loss. "
                 "Reminder messages and easy rescheduling will lower the cancellation rate.",
                 f"📊 Current cancellation rate: {cancel_pct}%")

    with c2:
        rec_card(2, "🏆", "Recognise Top Contributing Providers",
                 "Providers donating the most food deserve public recognition. Certificates "
                 "and badges will motivate continued contributions and inspire others.",
                 f"🏅 Top donors: {top_provs}")

        rec_card(4, "📦", "Increase Collection in High Demand Cities",
                 "Cities with the most claims show strong need. More volunteers, vehicles, "
                 "and storage in these areas will ensure no claim goes unfulfilled.",
                 f"📍 High demand cities: {cities_hd}")

        rec_card(6, "📢", "Improve Listing Visibility for Low-Claim Providers",
                 "Some providers donate food but receive zero claims. Better listing visibility "
                 "and targeted notifications to nearby receivers will fix this gap.",
                 "🔍 Action: Notify nearest receivers when a new listing is added")

    rec_card(7, "🥗", "Promote Balanced Food Type Distribution Across Cities",
             "Food types are not equally spread across all cities. Encouraging providers to "
             "diversify donations based on local receiver preferences will improve nutritional "
             "balance and reduce selective wastage.",
             "🌱 Action: City-level campaigns to diversify food type donations")
    # ── Supporting Charts ─────────────────────────────────────
    st.markdown("---")
    st.markdown("### Supporting Data")
    c1, c2 = st.columns(2)
    with c1:
        df = q("SELECT f.Location, SUM(f.Quantity) Supply, COUNT(c.Claim_ID) Claims FROM food_listings f LEFT JOIN claims c ON f.Food_ID=c.Food_ID GROUP BY f.Location ORDER BY Supply DESC LIMIT 10")
        st.plotly_chart(px.bar(df, x="Location", y=["Supply","Claims"], barmode="group",
            color_discrete_sequence=["#2d7a50","#f59e0b"],
            title="Food Supply vs Claims per City").update_layout(
            height=300, margin=dict(t=30,b=5), xaxis_tickangle=-30),
            use_container_width=True)
    with c2:
        df2 = q("SELECT p.Name, SUM(f.Quantity) Donated FROM providers p JOIN food_listings f ON p.Provider_ID=f.Provider_ID GROUP BY p.Provider_ID ORDER BY Donated DESC LIMIT 10")
        st.plotly_chart(px.bar(df2, x="Donated", y="Name", orientation="h",
            color="Donated", color_continuous_scale="Greens",
            title="Top 10 Providers by Donation").update_layout(
            height=300, margin=dict(t=30,b=5), yaxis_title=""),
            use_container_width=True)