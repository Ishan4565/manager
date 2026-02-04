import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


API_URL = "https://booking-dzz2.onrender.com"
MANAGER_PASSWORD = "manager_booking12"  

st.set_page_config(page_title="Manager Analytics Dashboard", page_icon="📊", layout="wide")


st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)


st.sidebar.title("🔐 Manager Access")
access_password = st.sidebar.text_input("Enter Password", type="password")

if access_password != MANAGER_PASSWORD:
    st.title("📊 Manager Analytics Dashboard")
    st.info("Please enter the manager password in the sidebar to access real-time business insights.")
    st.stop()  # Stops execution here if password is wrong



st.title("📊 Manager Analytics Dashboard")
st.write("Real-time insights into your booking business performance")

if st.button("🔄 Refresh Data"):
    st.rerun()

try:
    # Fetching data from your FastAPI backend
    analytics_response = requests.get(f"{API_URL}/analytics")
    reviews_response = requests.get(f"{API_URL}/reviews")
    seats_response = requests.get(f"{API_URL}/seats")
    
    if analytics_response.status_code == 200 and reviews_response.status_code == 200:
        analytics = analytics_response.json()
        reviews_data = reviews_response.json()
        seats_data = seats_response.json()
        
        stats = analytics["overall_statistics"]
        category_scores = analytics["category_scores"]
        sentiment_breakdown = analytics["sentiment_breakdown"]
        
        st.divider()
        
        # Row 1: Key Performance Indicators (KPIs)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Reviews", stats["total_reviews"])
        
        with col2:
            happiness_pct = ((stats["overall_avg_score"] or 0) + 1) * 50
            st.metric("Customer Satisfaction", f"{round(happiness_pct, 1)}%")
        
        with col3:
            st.metric("Available Seats", seats_data["available"], f"-{seats_data['booked']} booked")
        
       with col4:
            # Added a check to ensure total_reviews is not None or Zero
            total = stats.get("total_reviews", 0)
            excellent = stats.get("excellent_ratings", 0)
            
            excellence_rate = (excellent / total * 100) if total > 0 else 0
            
            st.metric(
                "Excellence Rate", 
                f"{round(excellence_rate, 1)}%",
                help="Percentage of 'Excellent' ratings"
            )
