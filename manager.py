import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuration
API_URL = "https://booking-dzz2.onrender.com"
MANAGER_PASSWORD = "manager_booking12"

st.set_page_config(page_title="Manager Analytics", page_icon="📊", layout="wide")

# --- Security Section ---
st.sidebar.title("🔐 Manager Access")
access_password = st.sidebar.text_input("Enter Password", type="password")

if access_password != MANAGER_PASSWORD:
    st.title("📊 Manager Analytics Dashboard")
    st.info("Please enter the manager password in the sidebar to access insights.")
    st.stop()

# --- Main Dashboard ---
st.title("📊 Manager Analytics Dashboard")

if st.button("🔄 Refresh Data"):
    st.rerun()

try:
    # API Calls
    analytics_res = requests.get(f"{API_URL}/analytics")
    reviews_res = requests.get(f"{API_URL}/reviews")
    seats_res = requests.get(f"{API_URL}/seats")

    if analytics_res.status_code == 200 and reviews_res.status_code == 200:
        analytics = analytics_res.json()
        reviews_data = reviews_res.json()
        seats_data = seats_res.json()

        stats = analytics["overall_statistics"]
        cat_scores = analytics["category_scores"]
        sentiment_breakdown = analytics["sentiment_breakdown"]

        st.divider()

        # Row 1: Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Reviews", stats.get("total_reviews", 0))
        
        with col2:
            avg_score = stats.get("overall_avg_score", 0) or 0
            happiness = (avg_score + 1) * 50
            st.metric("Customer Satisfaction", f"{round(happiness, 1)}%")
        
        with col3:
            st.metric("Available Seats", seats_data.get("available", 0))
        
        with col4:
            total = stats.get("total_reviews", 0)
            excellent = stats.get("excellent_ratings", 0)
            rate = (excellent / total * 100) if total > 0 else 0
            st.metric("Excellence Rate", f"{round(rate, 1)}%")

        # Row 2: Charts
        st.divider()
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("🎯 Rating Distribution")
            r_labels = ['Excellent', 'Good', 'Average', 'Poor', 'Very Poor']
            r_values = [stats.get(f"{r.lower().replace(' ', '_')}_ratings", 0) for r in r_labels]
            if sum(r_values) > 0:
                fig_pie = px.pie(names=r_labels, values=r_values, hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No ratings yet.")

        with c2:
            st.subheader("💭 Sentiment Analysis")
            s_labels = [s['category'].title() for s in sentiment_breakdown]
            s_counts = [s['count'] for s in sentiment_breakdown]
            if s_labels:
                fig_bar = px.bar(x=s_labels, y=s_counts, color=s_labels)
                st.plotly_chart(fig_bar, use_container_width=True)

        # Row 3: Reviews
        st.divider()
        st.subheader("📝 Recent Reviews")
        for rev in reviews_data.get("reviews", [])[:5]:
            with st.expander(f"{rev['user_name']} - Seat {rev['seat_number']}"):
                st.write(f"**Experience:** {rev['overall_experience']}")
                st.write(f"**AI Score:** {rev['average_score']:.3f}")

    else:
        st.error("Could not fetch data from API.")

except Exception as e:
    st.error(f"Error: {e}")
