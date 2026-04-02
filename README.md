# 🏨 AI-Powered Booking & Business Intelligence Ecosystem

## 🎯 Problem Statement

Small hospitality businesses (hotels, hostels, event spaces) struggle with:
- **Manual booking management** (spreadsheets, phone calls)
- **No data insights** (don't know customer satisfaction)
- **Operational blind spots** (which rooms are problematic?)
- **Scaling challenges** (can't handle many concurrent bookings)

**The Technical Challenge:**
- Handle concurrent booking requests without race conditions
- Provide real-time insights to managers
- Integrate customer feedback with operational metrics
- Scale from 10 bookings/day to 1000 bookings/day

## ✅ Solution

Built a **production-grade ecosystem** with:
1. **FastAPI REST Backend** — Handles bookings, manages data, provides APIs
2. **Customer Portal** (Streamlit) — Browse rooms, make bookings, leave reviews
3. **Manager Dashboard** (Streamlit) — View bookings, customer feedback, analytics, insights
4. **NLP Sentiment Engine** — Analyzes customer reviews across 8 dimensions

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│         CUSTOMER PORTAL (Streamlit App)                 │
│  - Browse available rooms                              │
│  - Check prices                                         │
│  - Make reservations                                    │
│  - Leave reviews & ratings                             │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ REST API Calls
                   ↓
┌─────────────────────────────────────────────────────────┐
│          FASTAPI BACKEND (REST API)                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Core Operations:                                │   │
│  │ - GET /rooms (available rooms)                 │   │
│  │ - POST /bookings (create booking)              │   │
│  │ - GET /bookings (list bookings)                │   │
│  │ - POST /reviews (submit review)                │   │
│  │ - GET /analytics (booking analytics)           │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ PostgreSQL Database with Row-Level Locking       │   │
│  │ (prevents double-booking race conditions)       │   │
│  └─────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    ↓              ↓              ↓
┌─────────────┐ ┌──────────┐ ┌────────────────┐
│  NLP Engine │ │ Analytics│ │ Booking Engine │
│(Sentiment)  │ │(Plotly)  │ │(Validation)    │
└─────────────┘ └──────────┘ └────────────────┘
    │
    ↓
┌─────────────────────────────────────────────────────────┐
│        MANAGER DASHBOARD (Streamlit App)                │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Authentication:                                 │   │
│  │ - Login required (password protected)          │   │
│  │ - Only managers can access                     │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
│  Features:                                             │
│  - Real-time booking dashboard                        │
│  - Customer reviews + sentiment analysis              │
│  - Occupancy rates                                    │
│  - Revenue insights                                   │
│  - Alerts (low reviews, high cancellations)          │
└─────────────────────────────────────────────────────────┘
```

## 🛠 Tech Stack

### Backend
- **Framework:** FastAPI (async, high-performance)
- **Database:** PostgreSQL (ACID, row-level locking)
- **ORM:** SQLAlchemy (database abstraction)
- **API Docs:** Swagger UI (auto-generated)
- **Hosting:** Render (cloud deployment)
- **Port:** 5000

### Frontend (Customer Portal)
- **Framework:** Streamlit
- **Deployment:** Streamlit Cloud
- **Analytics:** Plotly (interactive charts)
- **HTTP Client:** Requests (API calls)
- **State Management:** Streamlit session state

### Manager Dashboard
- **Framework:** Streamlit
- **Authentication:** Simple password (expandable to OAuth)
- **NLP:** TextBlob, NLTK
- **Analytics:** Pandas, Plotly
- **Sentiment Analysis:** Custom NLP engine

## 📊 Key Features

### 1. Booking Management
```
Customer Flow:
1. Browse rooms (with pictures, prices, availability)
2. Select dates
3. Confirm booking
4. Receive confirmation email/SMS
5. Later: Leave review
```

### 2. Concurrency Handling (The Hard Part)
**Problem:** Two users try to book the last available room simultaneously.

**Solution:** PostgreSQL Row-Level Locking
```python
# In FastAPI endpoint
with db.begin():
    # Lock the room row until transaction completes
    room = db.query(Room).with_for_update().filter(
        Room.id == room_id
    ).first()
    
    if room.available_count > 0:
        room.available_count -= 1
        booking = Booking(room_id=room_id, user_id=user_id, ...)
        db.add(booking)
        db.commit()  # Lock released
        return {"success": True}
    else:
        db.rollback()
        return {"error": "Room fully booked"}
```

**Result:** Only one booking succeeds, other gets error. No double-booking.

### 3. NLP Sentiment Analysis
Analyzes customer reviews across 8 dimensions:

| Dimension | Example |
|-----------|---------|
| **Sound/Noise** | "Room was quiet" vs. "Too much noise" |
| **Comfort** | "Bed was comfortable" vs. "Hard mattress" |
| **Cleanliness** | "Very clean" vs. "Found dirt" |
| **Staff Service** | "Great staff" vs. "Rude staff" |
| **Food Quality** | "Breakfast was delicious" vs. "Bad food" |
| **Value for Money** | "Worth the price" vs. "Too expensive" |
| **Amenities** | "WiFi was fast" vs. "No hot water" |
| **Overall Experience** | "Would come back" vs. "Won't recommend" |

**Implementation:**
```python
from textblob import TextBlob
from nltk.tokenize import sent_tokenize

def analyze_sentiment(review_text):
    sentences = sent_tokenize(review_text)
    sentiments = {}
    
    for sentence in sentences:
        blob = TextBlob(sentence)
        polarity = blob.sentiment.polarity  # -1 (negative) to 1 (positive)
        
        # Categorize by dimension
        dimension = classify_dimension(sentence)
        sentiments[dimension] = polarity
    
    return sentiments  # Returns score for each dimension

# Manager sees:
# Sound: ⭐⭐⭐⭐⭐ (5/5)
# Comfort: ⭐⭐⭐ (3/5)
# Cleanliness: ⭐⭐⭐⭐⭐ (5/5)
```

**Auto-Alerts:**
- If any dimension scores < 3: Alert manager
- Highlight problematic areas for improvement

### 4. Real-Time Analytics Dashboard
- **Occupancy Rate:** % of rooms booked per day
- **Revenue Trends:** Income over time
- **Customer Ratings:** Average satisfaction
- **Booking Patterns:** Peak seasons, slow periods
- **Top Rooms:** Which rooms get booked most?
- **Top Issues:** What complaints are most common?

## 📂 Project Structure

```
booking_ecosystem/
├── backend/                          # FastAPI server
│   ├── main.py                      # FastAPI app
│   ├── models.py                    # SQLAlchemy models
│   ├── schemas.py                   # Pydantic schemas
│   ├── database.py                  # DB connection
│   ├── routes/
│   │   ├── bookings.py             # Booking endpoints
│   │   ├── rooms.py                # Room endpoints
│   │   └── reviews.py              # Review endpoints
│   ├── utils/
│   │   ├── sentiment.py            # NLP sentiment analysis
│   │   └── validation.py           # Data validation
│   └── requirements.txt
│
├── frontend_booking/                 # Customer Portal
│   ├── app.py                       # Streamlit main
│   ├── pages/
│   │   ├── home.py                 # Browse rooms
│   │   ├── booking.py              # Make booking
│   │   └── review.py               # Leave review
│   ├── utils/
│   │   └── api_client.py           # Backend API calls
│   └── requirements.txt
│
├── manager/                          # Manager Dashboard
│   ├── app.py                       # Streamlit main (with auth)
│   ├── pages/
│   │   ├── dashboard.py            # Overview
│   │   ├── bookings.py             # Booking list
│   │   ├── reviews.py              # Customer feedback
│   │   ├── analytics.py            # Charts & insights
│   │   └── alerts.py               # Problem areas
│   ├── utils/
│   │   ├── auth.py                 # Password protection
│   │   ├── api_client.py           # Backend calls
│   │   └── sentiment.py            # Review analysis
│   └── requirements.txt
│
├── docker-compose.yml               # Local dev setup
└── README.md
```

## 🚀 Live Demos

### Customer Portal
**URL:** https://booking-hfyo5lv5au5yqjgvjpsgdf.streamlit.app

**What you can do:**
- Browse available rooms
- Check prices and availability
- Make a booking
- View booking confirmation
- Leave reviews

### Manager Dashboard
**URL:** https://manager-wbpn8qsgvnxg3fkupycr8x.streamlit.app/

**Login:** 
- Username: manager
- Password: manager_booking12

**What you see:**
- Real-time bookings
- Customer reviews with sentiment
- Occupancy dashboard
- Revenue charts
- Alerts for problems

### FastAPI Documentation
**URL:** https://booking-dzz2.onrender.com/docs

**What it shows:**
- All API endpoints
- Request/response schemas
- Try-it-out interface
- Swagger UI

## 💻 How to Run Locally

### 1. Install Dependencies
```bash
git clone [repo-link]
cd booking_ecosystem

# Backend
cd backend && pip install -r requirements.txt
cd ..

# Frontend
cd frontend_booking && pip install -r requirements.txt
cd ..

# Manager
cd manager && pip install -r requirements.txt
cd ..
```

### 2. Setup Database
```bash
# Using Docker (easiest)
docker-compose up -d postgres

# Or manually:
# Create PostgreSQL database
createdb booking_system
```

### 3. Setup Environment Variables
```bash
# Create .env file in backend/
echo "DATABASE_URL=postgresql://user:password@localhost/booking_system" > backend/.env
```

### 4. Run Backend
```bash
cd backend
uvicorn main:app --reload --port 5000
```

**Check:** http://localhost:5000/docs (Swagger UI)

### 5. Run Customer Portal
```bash
cd frontend_booking
streamlit run app.py
```

**Opens:** http://localhost:8501

### 6. Run Manager Dashboard
```bash
cd manager
streamlit run app.py
```

**Opens:** http://localhost:8502

## 📈 API Endpoints

### Rooms
```
GET /api/rooms                    # List all rooms
GET /api/rooms/{room_id}         # Get room details
GET /api/rooms/available?from=...&to=...  # Check availability
```

### Bookings
```
POST /api/bookings               # Create new booking
GET /api/bookings                # List all bookings
GET /api/bookings/{booking_id}   # Get booking details
PUT /api/bookings/{booking_id}   # Update booking
DELETE /api/bookings/{booking_id} # Cancel booking
```

### Reviews
```
POST /api/reviews                # Submit review
GET /api/reviews/{room_id}       # Get room reviews
GET /api/reviews/sentiment/{room_id}  # Get sentiment analysis
```

### Analytics
```
GET /api/analytics/occupancy     # Occupancy rate
GET /api/analytics/revenue       # Revenue data
GET /api/analytics/ratings       # Average ratings
GET /api/analytics/bookings      # Booking trends
```

## 🎓 Key Learnings

### 1. Concurrency is Hard
**What I learned:**
- Without row-level locking, double-booking is possible
- Race conditions are subtle (tests don't always catch them)
- Need to understand ACID properties and isolation levels
- Production systems MUST prevent double-booking

### 2. API Design Matters
**What I learned:**
- RESTful design makes frontend development faster
- Swagger docs are essential (frontend engineer needs to understand API)
- Versioning APIs early prevents problems later
- Error handling (what status codes for what errors?)

### 3. NLP is Powerful but Limited
**What I learned:**
- TextBlob is simple but works for basic sentiment
- Need domain-specific tuning for hospitality feedback
- "Staff was cold" = negative feedback (NLP might miss nuance)
- Can't replace human review, but great for alerts

### 4. Real-Time Analytics Drive Action
**What I learned:**
- Dashboards only help if insights are actionable
- "Cleanliness rating: 2/5" → Manager fixes cleanliness immediately
- Data without action = waste
- Alerts (visual + email) are critical

### 5. Authentication is Essential
**What I learned:**
- Manager dashboard MUST be password protected
- Customers seeing manager view would violate privacy
- Can't use session cookies alone (token-based better)
- Rate limiting prevents abuse

## 🔄 Production Workflow

**Customer makes booking:**
```
1. Customer fills form (Streamlit)
2. POST /api/bookings (FastAPI)
3. Backend locks room row (PostgreSQL)
4. Check availability + decrement count
5. Create booking record
6. Release lock
7. Return confirmation to customer
8. Email confirmation sent
```

**Manager reviews feedback:**
```
1. Manager logs in (password check)
2. Manager visits "Reviews" page
3. App fetches all reviews (GET /api/reviews)
4. NLP analyzes each review (sentiment scores)
5. Dashboard displays: dimension-wise scores + alerts
6. Manager sees "Cleanliness: 2/5" → Takes action
```

## 💡 Future Improvements

- [ ] **Payment integration:** Stripe/Razorpay for payments
- [ ] **Email notifications:** Send confirmation emails
- [ ] **SMS alerts:** Notify managers of new bookings
- [ ] **OAuth:** Google/Facebook login for customers
- [ ] **Cancellation policy:** Refunds based on policy
- [ ] **Multi-language:** Support Hindi, Nepali, etc.
- [ ] **Mobile app:** React Native or Flutter version
- [ ] **Admin panel:** Add/edit rooms, configure settings
- [ ] **Inventory management:** Track supplies, expenses
- [ ] **Staff scheduling:** Schedule staff per occupancy

## 🔗 Related Projects

- [Fraud Detection](https://github.com/Ishan4565/fraud_detection) — Classif. + real-time inference
- [ML Drift Monitor](https://github.com/Ishan4565/inventory-drift-monitor) — Production monitoring

## 🏆 What This Project Demonstrates

✅ **Full-Stack Development** (backend + 2 frontends)  
✅ **Production Challenges** (concurrency, authentication)  
✅ **Real-World Requirements** (multi-user, data integrity)  
✅ **NLP Application** (sentiment analysis)  
✅ **API Design** (REST, Swagger docs)  
✅ **Database Design** (relationships, locking)  
✅ **Deployment** (multiple services, cloud hosting)  

## 📧 Contact

- **Email:** ishandh454@gmail.com
- **GitHub:** Ishan4565
- **LinkedIn:** https://www.linkedin.com/in/ishan-dhakal-2b1933376/

---

**This project demonstrates end-to-end ML + full-stack engineering: not just ML models, but complete systems with real-world constraints.**
