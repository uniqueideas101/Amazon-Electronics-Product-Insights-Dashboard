import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    url = "https://drive.google.com/uc?id=1WeD2MS13KBD_VmKUjv9NwX4le3oeGh6d" 
    return pd.read_csv(url)


df = load_data()

# Title
st.title("Amazon Electronics Product Insights Dashboard")

# Sidebar filters
st.sidebar.header("Filter Options")
categories = st.sidebar.multiselect(
    "Select Categories", options=df["product_category"].unique(),
    default=df["product_category"].unique()[:5]
)

filtered_df = df[df["product_category"].isin(categories)]

avg_rating = round(filtered_df["product_rating"].mean(), 2)
avg_discount = round(filtered_df["discount_percentage"].mean(), 2)
avg_purchase = round(filtered_df["purchased_last_month"].mean(), 2)

col1, col2, col3 = st.columns(3)
col1.metric("⭐ Avg Rating", avg_rating)
col2.metric("💰 Avg Discount (%)", avg_discount)
col3.metric("🛒 Avg Monthly Purchases", avg_purchase)

# category

st.subheader("Top Performing Categories")
cat_perf = (filtered_df.groupby("product_category")["purchased_last_month"]
            .mean().sort_values(ascending=False).head(10))
fig1 = px.bar(cat_perf, x=cat_perf.index, y=cat_perf.values,
              labels={"x":"Category", "y":"Avg Purchases"},
              color=cat_perf.values, color_continuous_scale="Blues")
st.plotly_chart(fig1)

# dicsount
st.subheader("Discount Impact on Purchases")
fig2 = px.scatter(filtered_df, x="discount_percentage", y="purchased_last_month",
                  color="product_category", opacity=0.6,
                  labels={"discount_percentage":"Discount (%)",
                          "purchased_last_month":"Units Purchased"})
st.plotly_chart(fig2)

# ratings vs review

st.subheader("Ratings vs Reviews")
fig3 = px.scatter(filtered_df, x="product_rating", y="total_reviews",
                  size="purchased_last_month", color="product_category",
                  hover_name="product_title", opacity=0.6)
st.plotly_chart(fig3)

# Promotional Analysis

import itertools

st.subheader("Promotion Impact")

# Calculate actual means
promo_df = filtered_df.groupby(["has_coupon", "is_best_seller", "is_sponsored"])["purchased_last_month"].mean().reset_index()

# Create all possible combinations of True/False
combos = pd.DataFrame(list(itertools.product([True, False], repeat=3)), columns=["has_coupon", "is_best_seller", "is_sponsored"])

# Merge to include missing combinations (fill missing with 0 or NaN)
promo_df = combos.merge(promo_df, on=["has_coupon", "is_best_seller", "is_sponsored"], how="left").fillna(0)

st.dataframe(promo_df)



# Compute summaries
coupon_summary = (
    filtered_df.groupby("has_coupon")["purchased_last_month"].mean().reset_index()
)
coupon_summary["promotion_type"] = "Has Coupon"

best_seller_summary = (
    filtered_df.groupby("is_best_seller")["purchased_last_month"].mean().reset_index()
)
best_seller_summary["promotion_type"] = "Best Seller"

sponsored_summary = (
    filtered_df.groupby("is_sponsored")["purchased_last_month"].mean().reset_index()
)
sponsored_summary["promotion_type"] = "Sponsored"

# Combine all
combined = pd.concat([
    coupon_summary.rename(columns={"has_coupon": "status"}),
    best_seller_summary.rename(columns={"is_best_seller": "status"}),
    sponsored_summary.rename(columns={"is_sponsored": "status"})
])

# Plot in one figure
fig = px.bar(
    combined,
    x="promotion_type",
    y="purchased_last_month",
    color="status",
    barmode="group",
    title="Impact of Promotions on Monthly Purchases",
    labels={"purchased_last_month": "Avg Purchases", "promotion_type": "Promotion Type"},
    color_discrete_sequence=["#7219C0", "#4CAF50"]
)

st.plotly_chart(fig)

st.markdown("""
<div style="background-color:#F0F2F6; padding:15px; border-radius:10px; border:1px solid #ddd">
    <h3 style="color:#333;">Product Insights Summary</h3>
    <ul>
        <li>Phones & Laptops dominate purchases despite minimal discounts (brand-driven demand).</li>
        <li>Accessories respond strongly to discounts (price-sensitive segment).</li>
        <li>Laptops have highest reviews (4.7) → strong satisfaction & retention potential.</li>
        <li>Most devices rated 4–5 stars, but low review volume (underused trust signal).</li>
        <li>Coupons, Best Seller & Sponsorship tags perform best.</li>
    </ul>
    <hr>
    <h4 style="color:#444;">Strategic Recommendations</h4>
    <ul>
        <li>Incentivize reviews to boost social proof.</li>
        <li>Use differentiated promotion: visibility for premium, discounts for accessories.</li>
        <li>Experiment with cross-sells (e.g., headphones with laptops).</li>
    </ul>
</div>
""", unsafe_allow_html=True)



