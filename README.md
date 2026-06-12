# Aura-Commerce-AI (Xecomerce)

**AI-Powered Intelligent Commerce Platform**

Aura-Commerce-AI is an enterprise-grade, AI-first e-commerce platform designed to showcase full-stack retail engineering integrated with machine learning models. It combines a React + TypeScript storefront, a FastAPI backend microservice, a fully normalized MySQL 8+ database, and five custom machine learning pipelines for predictive pricing, demand forecasting, customer sentiment analysis, review moderation, and personalized recommendations.

---

## 1. Project Overview

Aura-Commerce-AI solves major retail engineering pain points by unifying transactional processing and artificial intelligence:
- **Low Conversions:** Solved using a hybrid recommendation system (combining content-based filtering with collaborative filtering).
- **Manual Pricing:** Solved using an automated price prediction regressor that forecasts optimal values based on ratings and discounts.
- **Review Spams:** Solved with a fake review classification pipeline that detects computer-generated or disingenuous feedback.
- **Inaccurate Forecasting:** Solved using a Random Forest time-series demand forecasting model.
- **Search Friction:** Solved using semantic keyword, voice, and image-based search matching.

---

## 2. Key Features

- **Core E-Commerce:** Category navigation, product catalogs, shopping carts, wishlists, and order lifecycle management.
- **AI Chatbot & RAG:** RAG-powered shopping assistant utilizing Ollama/template fallbacks with interactive comparison routing (e.g. brand comparison).
- **Hybrid Recommender:** Suggests relevant products using content similarity and user clickstream feedback logs.
- **NLP Sentiment & Moderation:** Real-time sentiment prediction (Positive/Neutral/Negative) and machine-learning-based spam reviews checking.
- **Predictive Analytics:** Real-time demand forecast for next-7-days sales counts and automated base price recommender.
- **Search Capabilities:** Full keyword matching, voice search (speech-to-text), and visual search (image encoding similarity).
- **Observability:** Custom dashboard serving Plotly analytics, data drift monitors, and performance logging.

---

## 3. Folder Structure

```
Aura-Commerce-AI/
├── backend/                  # FastAPI Web Server Application
│   ├── app/
│   │   ├── api/              # Route controllers (Auth, Products, Cart, Orders, Reviews, Chatbot, etc.)
│   │   ├── database/         # Connection engine, SQLAlchemy models, Pydantic schemas
│   │   ├── services/         # Business logic modules (Auth, Cart, Recommendation services)
│   │   └── utils/            # JWT helpers, password hashing libraries
├── database/                 # MySQL 8+ Database Schema and Seeds
│   ├── ecommerce.sql         # Target schema including foreign keys, indexes, and triggers
│   ├── seed_data.sql         # Enterprise mock seed records for all tables
│   └── migrations/           # Database migration files
├── ml_models/                # ML Pipeline and Saved Artifacts (Must not be modified)
│   ├── datasets/             # Source CSV datasets for training
│   ├── saved_models/         # Persisted joblib model weights
│   ├── recommendation/       # Content-based and collaborative filters
│   ├── sentiment/            # TF-IDF review sentiment analyzers
│   ├── fake_review/          # Fake review detector model
│   ├── demand_forecasting/   # Random Forest orders count demand forecaster
│   ├── price_prediction/     # Product actual price predictor
│   └── chatbot/              # LLM assistant and comparisons engine
├── scripts/                  # Automated Orchestration Scripts
│   ├── create_database.py    # Database auto-creation and schema initializations
│   ├── seed_database.py      # Database populator and count verification
│   └── train_all_models.py   # Multi-pipeline model training orchestrator
└── docs/                     # System Design and Architectural Reports
    ├── architecture.md       # High-Level Architecture, Recommendation & Chatbot flows
    ├── api_documentation.md  # Detailed backend route parameters and payloads
    ├── er_diagram.md         # Mermaid entity relations diagram
    ├── system_design.md      # Low-level layout, scalability, and security implementations
    └── project_report.md     # Production project summary and evaluation metrics
```

---

## 4. Installation & Setup

### Prerequisites
- Python 3.13+
- Node.js 18+
- MySQL 8.0+

### Setup Environment
1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/Xecomerce.git
   cd Xecomerce
   ```
2. Copy the environment variables:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` to configure your local MySQL credentials (`MYSQL_USER`, `MYSQL_PASSWORD`, etc.).*

3. Set up the Python virtual environment and install backend dependencies:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Install root dependencies (data processing, ML libraries):
   ```bash
   cd ..
   pip install -r requirements.txt
   ```

5. Install frontend packages:
   ```bash
   cd frontend
   npm install
   ```

---

## 5. Automated Database Initialization

Aura-Commerce-AI contains automation scripts to bootstrap your database in seconds.

### Step 1: Create Database & Schema
Run the database creation script which connects to MySQL, creates the target database, compiles the `ecommerce.sql` file, executes it (creating all 15 tables with indexes), and defines triggers to calculate review average ratings automatically.
```bash
python scripts/create_database.py
```

### Step 2: Seed the Database
Seed the tables with high-fidelity test records and print a verification report:
```bash
python scripts/seed_database.py
```

---

## 6. Training Machine Learning Models

Orchestrate training of all five machine learning models sequentially using the automated runner. This script executes training processes in their relative folder contexts, outputs real-time progress bars using `rich`, and logs the training outputs.

```bash
python scripts/train_all_models.py
```
**Saved Artifacts Generated:**
- `recommender.pkl` -> Hybrid candidate generator
- `sentiment.pkl` & `sentiment_vectorizer.pkl` -> Review classifier
- `fake_review.pkl` & `fake_review_vectorizer.pkl` -> Moderation checker
- `demand_forecast.pkl` -> Order trend predictor
- `price_predictor.pkl` -> Price optimization weights

*Artifacts are saved directly to `ml_models/saved_models/`.*

---

## 7. Running the Application

### Running the Backend API
Start the FastAPI server on port 8000:
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Access the interactive OpenAPI spec documentation at: `http://localhost:8000/docs`.

### Running the Frontend Storefront
Start the React web client:
```bash
cd frontend
npm start
```
The storefront runs locally at `http://localhost:3000`.

---

## 8. API Documentation Summary

| Method | Endpoint | Description | Request Example (JSON) |
|---|---|---|---|
| `POST` | `/api/auth/register` | User signup | `{"email": "user@test.com", "password": "Password123"}` |
| `POST` | `/api/auth/login` | User signin | `{"email": "user@test.com", "password": "Password123"}` |
| `GET` | `/api/products` | Retrieve catalog | *None* |
| `POST` | `/api/chatbot/query` | Run RAG pipeline | `{"query": "gaming keyboard under 5000"}` |
| `POST` | `/api/chatbot/compare` | Compare products | `{"query": "Samsung vs OnePlus"}` |
| `POST` | `/api/price-prediction` | Calculate optimal base price | `{"category": "Keyboards", "discounted_price": 4500.0}` |

*For the complete endpoints guide, parameters, and payloads, see [docs/api_documentation.md](file:///D:/PROJECTS/Xecomerce/docs/api_documentation.md).*

---

## 9. Screenshots Section

Below are placeholders for the interface modules. Replace these images with your UI deployment details:

### User Storefront & AI Chatbot
![Storefront & Chatbot Panel](file:///D:/PROJECTS/Xecomerce/docs/screenshots/storefront.png)

### Seller Analytics & Price Forecaster
![Seller Dashboard](file:///D:/PROJECTS/Xecomerce/docs/screenshots/dashboard.png)

### ML Performance Dashboard (Plotly)
![ML Performance Dashboard](file:///D:/PROJECTS/Xecomerce/docs/screenshots/ml_metrics.png)

---

## 10. Future Improvements

1. **Auto-tuning ML models:** Incorporate MLflow pipelines to detect model drift and trigger automatic retrain cycles via Airflow.
2. **Deep Recommender:** Shift from traditional content-based matrix models to deep-learning-based recommendation architectures (e.g., Two-Tower Neural Models).
3. **Multi-turn LLMs:** Implement session-aware memory inside the chat API for fluid, long-form conversational recommendations.
4. **GraphQL Gateway:** Introduce a GraphQL aggregation layer to reduce network payloads between the React UI client and backend endpoints.

---

## 11. License

This project is licensed under the MIT License - see the [LICENSE](file:///D:/PROJECTS/Xecomerce/LICENSE) file for details.
