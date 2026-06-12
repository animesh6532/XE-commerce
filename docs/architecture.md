# System Architecture Documentation

This document describes the architectural layout, machine learning components, recommendation pipelines, and conversational data flows of the Aura-Commerce-AI (Xecomerce) platform.

---

## 1. System Architecture Overview

Aura-Commerce-AI is designed as an N-tier distributed application combining transactional e-commerce workflows with analytical intelligence pipelines.

```mermaid
graph TD
    User([User Client])
    
    subgraph Frontend_Layer [Frontend Layer - React & TS]
        UI[Storefront SPA]
        Svc[API Client Service]
        UI --> Svc
    end
    
    subgraph Gateway_Proxy [Reverse Proxy - Nginx]
        Proxy[Nginx Load Balancer]
    end
    
    subgraph Application_Layer [Application Layer - FastAPI]
        API[FastAPI Web Engine]
        Sec[JWT Auth Middleware]
        Srv[Business Logic Services]
        API --> Sec
        Sec --> Srv
    end
    
    subgraph Data_Layer [Persistence Layer - MySQL 8]
        DB[(MySQL Database)]
        Trig[Rating Auto-Triggers]
        DB --> Trig
    end
    
    subgraph ML_Inference_Layer [ML Engine Layer]
        Rec[Hybrid Recommender]
        Sent[Review Sentiment Model]
        Fake[Fake Review Detector]
        Forecast[Demand Forecaster]
        Price[Price Predictor]
        Chat[RAG Chatbot Engine]
    end

    User -->|HTTPS| Proxy
    Proxy -->|API Proxy| API
    Svc -->|REST Requests| Proxy
    Srv -->|SQLAlchemy ORM| DB
    Srv -->|In-Memory Inference| ML_Inference_Layer
    DB -.->|Feature Extraction| ML_Inference_Layer
```

---

## 2. Machine Learning Architecture

The Machine Learning layer is divided into discrete service modules located in the `ml_models/` package. Model training is executed offline via the automated training orchestrator, outputting serialized joblib weights to `saved_models/` which are loaded into RAM by the FastAPI application during worker startup.

### Models and Frameworks
- **Sentence Transformers & FAISS:** Used for semantic keyword search, voice query matching, and image vector similarity search.
- **Scikit-Learn (Logistic Regression & RF):** Powers review sentiment scoring, fake review classification, demand forecasting, and pricing models.
- **Ollama / Templates:** Powers the RAG chatbot and product comparison engines.

---

## 3. Recommendation Pipeline

The recommendation engine implements a **Hybrid Recommendation Strategy** combining Content-Based Filtering with Collaborative Filtering hooks to mitigate the cold-start problem and deliver personalized lists.

```mermaid
flowchart TD
    Req[Get Recommendations Request] --> Auth{User Identified?}
    
    Auth -->|No / Cold Start| Content[Content-Based Filter]
    Auth -->|Yes| Hybrid[Hybrid Recommender]
    
    Content -->|Extract Features| Similarity[Cosine Similarity on Product TF-IDF]
    Similarity --> TopCold[Retrieve Top Similar Products]
    
    Hybrid -->|Collaborative Hook| Collab[User-Item Interactions Matrix]
    Hybrid -->|Content Hook| Similarity
    Collab --> Combine[Compute Weighted Score Matrix]
    Similarity --> Combine
    
    Combine --> TopWarm[Rank Candidates]
    
    TopCold --> Log[Write to recommendations_logs]
    TopWarm --> Log
    Log --> Response[Return Ranked Candidates]
```

---

## 4. Chatbot Pipeline

The conversational shopper assistant contains a RAG (Retrieval-Augmented Generation) pipeline that routes user queries depending on their intent.

```mermaid
flowchart TD
    UserQuery[User types query] --> Router{Query Intent Router}
    
    Router -->|Comparison Query: 'Brand A vs Brand B'| Compare[Comparison Engine]
    Router -->|Discovery Query: 'gaming keyboard'| RAG[RAG Retrieval Engine]
    Router -->|General chit-chat| LLM[LLM General Response]
    
    Compare --> Match[Extract Entity Names & Query Categories]
    Match --> SQLCompare[Fetch prices, reviews, pros/cons from MySQL]
    SQLCompare --> CompTemplate[Format Comparison Grid Response]
    
    RAG --> Embed[Create Query Embedding via SentenceTransformer]
    Embed --> FAISS[Semantic Search in FAISS index]
    FAISS --> FetchProducts[Fetch Product Cards from MySQL]
    FetchProducts --> PromptAssemble[Assemble RAG context prompt]
    PromptAssemble --> Ollama[Generate Answer via Ollama / Template fallback]
    
    CompTemplate --> AddHist[Append to chatbot_logs]
    Ollama --> AddHist
    LLM --> AddHist
    AddHist --> Send[Send Response to Frontend]
```

---

## 5. End-to-End Data Flow

### 1. Product Review Lifecycle & Automated Moderation
1. **Submit:** The user submits a review text and rating through the storefront UI.
2. **REST API:** The UI fires a `POST /api/reviews` request.
3. **ML Check (Fake Review):** The `review_service.py` intercepts the request and sends the text to the `FakeReviewModel` (Logistic Regression).
4. **ML Check (Sentiment):** The text is passed to the `SentimentModel` (TF-IDF vectorizer + Logistic Regression) to compute sentiment labels (Positive, Neutral, Negative).
5. **Database Commit:** The review record is saved in MySQL with flags: `is_fake`, `fake_probability`, and `sentiment`.
6. **Trigger Recalculation:** The MySQL trigger `after_review_insert` fires automatically. It updates the product's aggregated ratings in the `ratings` table and syncs the average score to the main `products` table.
7. **Response:** The frontend receives the created review object, immediately reflecting updated star averages.
