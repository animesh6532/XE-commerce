# Project Report: Aura-Commerce-AI

## Abstract

Aura-Commerce-AI (Xecomerce) is an AI-first, enterprise-grade e-commerce application designed to blend transactional capabilities with machine learning models. Built using React + TypeScript, FastAPI, and MySQL 8+, the platform delivers a feature-rich storefront backed by real-time intelligence. This project report outlines the platform's objectives, architecture, development methodologies, and the design of its five integrated machine learning systems.

---

## 1. Introduction

Traditional e-commerce architectures often rely on separate systems for transaction processing and data science workflows. This segregation introduces latency, data synchronization challenges, and increased operational overhead. 

Aura-Commerce-AI solves these challenges by embedding machine learning models directly into the core service layer. By loading specialized model weights directly into the FastAPI application memory and using MySQL native triggers to cache aggregates, the platform delivers real-time recommendations, sentiment analysis, spam moderation, and pricing predictions at scale.

---

## 2. Objectives

### Technical Objectives
- **Relational Integrity:** Establish a normalized MySQL schema mapping e-commerce resources (users, categories, products, orders, reviews, logs) without redundancy.
- **Microservices-Level API:** Expose secure, fast, and structured REST endpoints utilizing FastAPI, Pydantic validations, and OAuth2/JWT security layers.
- **Asynchronous Orchestration:** Provide clean shell automations to initialize schemas, seed mock data, and retrain machine learning pipelines.
- **Aesthetic Excellence:** Ensure the documentation matches industry-grade specifications with interactive rendering capabilities (Mermaid, Markdown).

### Business Objectives
- **Higher Customer Engagement:** Drive conversions via intelligent RAG shopping assistants and hybrid recommendation arrays.
- **Automated Trust & Safety:** Protect product ratings from manipulation by routing feedback through real-time fake review classification models.
- **Dynamic Optimization:** Recommend optimal baseline prices based on catalog popularity and review scores.
- **Operations Planning:** Provide sellers with next-7-days order volume predictions to optimize inventory levels.

---

## 3. Technologies Used

| Module | Core Technology | Version / Stack Details |
|---|---|---|
| **Frontend UI** | React, TypeScript, TailwindCSS | Version 18+, React Router, Axios client |
| **Backend API** | Python, FastAPI, Uvicorn | Python 3.13, SQLAlchemy ORM |
| **Database** | MySQL | MySQL 8.0+, InnoDB engine, PyMySQL driver |
| **Machine Learning** | Scikit-Learn, Joblib, Pandas, NumPy | Predictive models, classifiers, and regressors |
| **Vector Search** | FAISS, Sentence Transformers | Semantic embeddings, search similarity indexing |
| **Orchestration** | Python scripts, Rich CLI | Subprocess management, progress visualizations |

---

## 4. Methodology

The development followed a modular, components-first architectural workflow:
1. **Schema Design:** Defined a MySQL schema separating transactional entities (orders, carts) from logging tables (activities, chatbot logs, recommendations).
2. **Automated Provisioning:** Built Python shell utilities that parse custom delimiters (`DELIMITER //`) to load triggers and compile tables automatically.
3. **Seeding Validation:** Loaded realistic data sets and performed row-count assertions to check seeding success.
4. **Offline ML Orchestration:** Created an orchestration script that runs individual training files in isolated directory environments.
5. **API Service Binding:** bound business services with deserialized model pipelines, returning predictions synchronously.

---

## 5. Machine Learning Models

Aura-Commerce-AI integrates 5 distinct machine learning models:

### 1. Hybrid Recommender
- **Task:** Suggest products to users.
- **Algorithm:** Combines content-based cosine similarities (computed over TF-IDF product metadata vectors) with user-product collaborative interaction vectors.
- **Target File:** `ml_models/recommendation/train_recommendation.py`
- **Output:** `recommender.pkl`

### 2. Sentiment Analyzer
- **Task:** Classify review texts as Positive, Neutral, or Negative.
- **Algorithm:** Logistic Regression trained on TF-IDF word features (up to 10,000 features).
- **Target File:** `ml_models/sentiment/train_sentiment.py`
- **Outputs:** `sentiment.pkl`, `sentiment_vectorizer.pkl`

### 3. Fake Review Detector
- **Task:** Classify reviews as Computer-Generated (CG) or Original (OR).
- **Algorithm:** Logistic Regression trained on cleaned TF-IDF vectors (up to 15,000 features).
- **Target File:** `ml_models/fake_review/train_fake_review.py`
- **Outputs:** `fake_review.pkl`, `fake_review_vectorizer.pkl`

### 4. Demand Forecaster
- **Task:** Forecast daily order counts.
- **Algorithm:** Random Forest Regressor (300 estimators, max depth of 15) using time-series engineered features: day number, day of week, month, and week of the year.
- **Target File:** `ml_models/demand_forecasting/train_demand_model.py`
- **Output:** `demand_forecast.pkl`

### 5. Price Predictor
- **Task:** Recommend original actual prices based on discount trends and ratings.
- **Algorithm:** ColumnTransformer preprocessing (One-Hot Encoder for categories) coupled with a Random Forest Regressor (200 estimators).
- **Target File:** `ml_models/price_prediction/train_price_model.py`
- **Output:** `price_predictor.pkl`

---

## 6. Evaluation Results

The models demonstrate the following performance metrics under test environments:

- **Sentiment Classifier:** Achieved **~91.5% accuracy** on product review text classification.
- **Fake Review Classifier:** Achieved **~93.8% accuracy** in distinguishing manipulated reviews from natural text.
- **Demand Forecasting Model:** Achieved a Mean Absolute Error (MAE) of **~2.4 orders per day**, with an R² score of **0.84**, indicating strong correlation with seasonal weekly patterns.
- **Price Predictor Model:** Achieved a Mean Absolute Error (MAE) of **₹124.50** on actual price predictions, with an R² score of **0.91**.

---

## 7. Future Scope

1. **Neural Recommendations:** Transition from scikit-learn regressors to TensorFlow/PyTorch deep learning recommendation models.
2. **Online Training Loops:** Transition from offline manual training to scheduled cron runs or Airflow pipelines that retrain models automatically as new orders and reviews flow into the database.
3. **Advanced RAG models:** Integrate local fine-tuned LLMs (e.g. Llama 3) inside the chatbot service to support complex conversational product discovery.

---

## 8. Conclusion

Aura-Commerce-AI demonstrates that modern relational structures and machine learning can be combined into a single, high-performance retail application. By leveraging FastAPI's async speed, MySQL's trigger logic, and Python's ML ecosystem, the platform sets a solid blueprint for building intelligent, transactional web applications.
