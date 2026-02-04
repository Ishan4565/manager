import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

API_URL = "https://booking-dzz2.onrender.com"

st.set_page_config(page_title="Manager Analytics Dashboard", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Manager Analytics Dashboard")
st.write("Real-time insights into your booking business performance")

if st.button("🔄 Refresh Data"):
    st.rerun()

try:
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
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Reviews",
                stats["total_reviews"],
                help="Total number of customer reviews received"
            )
        
        with col2:
            happiness_pct = ((stats["overall_avg_score"] or 0) + 1) * 50
            st.metric(
                "Customer Satisfaction",
                f"{round(happiness_pct, 1)}%",
                help="Overall customer happiness score"
            )
        
        with col3:
            st.metric(
                "Available Seats",
                seats_data["available"],
                f"-{seats_data['booked']} booked",
                help="Current seat availability"
            )
        
        with col4:
            excellence_rate = (stats["excellent_ratings"] / stats["total_reviews"] * 100) if stats["total_reviews"] > 0 else 0
            st.metric(
                "Excellence Rate",
                f"{round(excellence_rate, 1)}%",
                help="Percentage of 'Excellent' ratings"
            )
        
        st.divider()
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("🎯 Rating Distribution")
            
            rating_labels = []
            rating_counts = []
            colors_map = {
                'excellent': '#10b981',
                'good': '#3b82f6',
                'average': '#f59e0b',
                'poor': '#ef4444',
                'very_poor': '#7f1d1d'
            }
            
            for rating in ['excellent', 'good', 'average', 'poor', 'very_poor']:
                count = stats.get(f"{rating}_ratings", 0)
                if count > 0:
                    rating_labels.append(rating.replace('_', ' ').title())
                    rating_counts.append(count)
            
            if rating_labels:
                fig_ratings = go.Figure(data=[go.Pie(
                    labels=rating_labels,
                    values=rating_counts,
                    hole=0.4,
                    marker_colors=['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#7f1d1d'][:len(rating_labels)]
                )])
                fig_ratings.update_layout(height=400)
                st.plotly_chart(fig_ratings, use_container_width=True)
            else:
                st.info("No ratings data available yet")
        
        with col_right:
            st.subheader("💭 Sentiment Analysis")
            
            sentiment_labels = [s['category'].title() for s in sentiment_breakdown]
            sentiment_counts = [s['count'] for s in sentiment_breakdown]
            
            if sentiment_labels:
                fig_sentiment = go.Figure(data=[go.Bar(
                    x=sentiment_labels,
                    y=sentiment_counts,
                    marker_color=['#10b981', '#ef4444', '#6b7280'],
                    text=sentiment_counts,
                    textposition='auto'
                )])
                fig_sentiment.update_layout(
                    height=400,
                    xaxis_title="Sentiment",
                    yaxis_title="Number of Reviews"
                )
                st.plotly_chart(fig_sentiment, use_container_width=True)
            else:
                st.info("No sentiment data available yet")
        
        st.divider()
        
        st.subheader("📈 Category Performance Analysis")
        
        categories_df = pd.DataFrame({
            'Category': [
                '🔊 Sound Quality',
                '💺 Seat Comfort',
                '📏 Seat Height',
                '👀 View Quality',
                '🎫 Booking Service',
                '👥 Staff Behavior',
                '✨ Cleanliness',
                '💰 Value for Money'
            ],
            'Score': [
                category_scores['sound_quality'],
                category_scores['seat_comfort'],
                category_scores['seat_height'],
                category_scores['view_quality'],
                category_scores['booking_service'],
                category_scores['staff_behavior'],
                category_scores['cleanliness'],
                category_scores['value_for_money']
            ]
        })
        
        categories_df = categories_df.sort_values('Score', ascending=True)
        
        fig_categories = go.Figure(data=[go.Bar(
            y=categories_df['Category'],
            x=categories_df['Score'],
            orientation='h',
            marker_color=['#ef4444' if score < 0 else '#f59e0b' if score < 0.3 else '#10b981' 
                         for score in categories_df['Score']],
            text=[f"{score:.3f}" for score in categories_df['Score']],
            textposition='auto'
        )])
        
        fig_categories.update_layout(
            height=500,
            xaxis_title="Average Sentiment Score",
            yaxis_title="Category",
            xaxis=dict(range=[-1, 1])
        )
        
        st.plotly_chart(fig_categories, use_container_width=True)
        
        lowest_category = categories_df.iloc[0]
        st.warning(f"⚠️ **Manager Alert:** '{lowest_category['Category']}' has the lowest score ({lowest_category['Score']:.3f}). Consider prioritizing improvements in this area.")
        
        st.divider()
        
        st.subheader("📝 Recent Customer Reviews")
        
        reviews = reviews_data["reviews"]
        
        if reviews:
            for review in reviews[:5]:
                with st.expander(f"Review by {review['user_name']} - Seat {review['seat_number']} - Rating: {review['overall_rating'].upper()}"):
                    
                    col_a, col_b = st.columns([2, 1])
                    
                    with col_a:
                        st.write(f"**Overall Experience:**")
                        st.write(f"_{review['overall_experience']}_")
                        
                        if review.get('sound_quality_review'):
                            st.write(f"**Sound Quality:** {review['sound_quality_review']}")
                        if review.get('seat_comfort_review'):
                            st.write(f"**Seat Comfort:** {review['seat_comfort_review']}")
                    
                    with col_b:
                        st.metric("Overall Score", f"{review['average_score']:.3f}")
                        st.metric("Sentiment", review['overall_sentiment_label'].title())
                        st.write(f"**Date:** {review['created_at'][:10]}")
        else:
            st.info("No reviews yet. Start collecting customer feedback!")
        
        st.divider()
        
        col_best, col_worst = st.columns(2)
        
        if reviews:
            best_review = max(reviews, key=lambda x: x['average_score'])
            worst_review = min(reviews, key=lambda x: x['average_score'])
            
            with col_best:
                st.success("🌟 **Best Review**")
                st.write(f"**Customer:** {best_review['user_name']}")
                st.write(f"**Seat:** {best_review['seat_number']}")
                st.write(f"**Score:** {best_review['average_score']:.3f}")
                st.write(f"**Comment:** _{best_review['overall_experience'][:150]}..._" if len(best_review['overall_experience']) > 150 else f"**Comment:** _{best_review['overall_experience']}_")
            
            with col_worst:
                st.error("⚠️ **Needs Attention**")
                st.write(f"**Customer:** {worst_review['user_name']}")
                st.write(f"**Seat:** {worst_review['seat_number']}")
                st.write(f"**Score:** {worst_review['average_score']:.3f}")
                st.write(f"**Comment:** _{worst_review['overall_experience'][:150]}..._" if len(worst_review['overall_experience']) > 150 else f"**Comment:** _{worst_review['overall_experience']}_")
    
    else:
        st.error("Unable to fetch analytics data. Please check your backend service.")

except Exception as e:
    st.error(f"Connection Error: {e}")
    st.info("Make sure your Render backend is running at: " + API_URL)

st.divider()
st.caption("Dashboard automatically pulls data from your booking system API")
