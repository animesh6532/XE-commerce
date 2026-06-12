# API Documentation

This document describes all backend REST API endpoints exposed by the FastAPI web service of the Aura-Commerce-AI (Xecomerce) platform.

---

## 1. Authentication Router (`/api/auth`)

### Register User
* **Endpoint:** `POST /api/auth/register`
* **Description:** Creates a new customer or seller account.
* **Request Payload (JSON):**
  ```json
  {
    "email": "customer1@gmail.com",
    "password": "Password123",
    "first_name": "Manav",
    "last_name": "Sharma",
    "role": "customer"
  }
  ```
* **Success Response (201 Created):**
  ```json
  {
    "success": true,
    "message": "User registered successfully",
    "user_id": 3
  }
  ```

### Login User
* **Endpoint:** `POST /api/auth/login`
* **Description:** Validates credentials and returns a JWT access token.
* **Request Payload (JSON):**
  ```json
  {
    "email": "customer1@gmail.com",
    "password": "Password123"
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "email": "customer1@gmail.com",
      "role": "customer",
      "first_name": "Manav"
    }
  }
  ```

---

## 2. Product Catalog Router (`/api/products`)

### Retrieve All Products
* **Endpoint:** `GET /api/products`
* **Description:** Retrieves list of products with optional category filtering.
* **Success Response (200 OK):**
  ```json
  {
    "products": [
      {
        "id": 1,
        "product_code": "B07JW9H4J1",
        "name": "Wayona Nylon Braided USB to Lightning Fast Charging Cable",
        "category": "Cables",
        "discounted_price": 399.00,
        "actual_price": 1399.00,
        "rating": 4.33,
        "rating_count": 3,
        "in_stock": true
      }
    ]
  }
  ```

---

## 3. Shopping Cart Router (`/api/cart`)

### Retrieve User Cart
* **Endpoint:** `GET /api/cart`
* **Description:** Fetches active cart items for the authenticated user.
* **Headers:** `Authorization: Bearer <token>`
* **Success Response (200 OK):**
  ```json
  {
    "cart_id": 1,
    "items": [
      {
        "product_id": 2,
        "name": "Ambrane Unbreakable Braided Type C Cable",
        "quantity": 2,
        "price": 349.00
      }
    ]
  }
  ```

### Add Item to Cart
* **Endpoint:** `POST /api/cart/items`
* **Headers:** `Authorization: Bearer <token>`
* **Request Payload:**
  ```json
  {
    "product_id": 3,
    "quantity": 1
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "success": true,
    "message": "Product added to cart"
  }
  ```

---

## 4. Orders Router (`/api/orders`)

### Create Order
* **Endpoint:** `POST /api/orders`
* **Headers:** `Authorization: Bearer <token>`
* **Request Payload:**
  ```json
  {
    "shipping_address": "Flat 102, Shanti Vihar, New Delhi - 110001",
    "payment_method": "Credit Card"
  }
  ```
* **Success Response (201 Created):**
  ```json
  {
    "success": true,
    "order_id": 1,
    "order_uuid": "ORD_001_846283",
    "total_amount": 8298.00,
    "message": "Order created and payment settled successfully"
  }
  ```

---

## 5. Product Reviews Router (`/api/reviews`)

### Submit Product Review
* **Endpoint:** `POST /api/reviews`
* **Headers:** `Authorization: Bearer <token>`
* **Request Payload:**
  ```json
  {
    "product_id": 1,
    "review_title": "Excellent Cable",
    "review_text": "Highly durable and charges extremely fast.",
    "rating": 5
  }
  ```
* **Success Response (201 Created):**
  ```json
  {
    "review_id": 9,
    "product_id": 1,
    "sentiment": "Positive",
    "is_fake": false,
    "fake_probability": 0.012,
    "message": "Review added. Moderation checks passed."
  }
  ```

---

## 6. AI Chatbot Assistant Router (`/api/chatbot`)

### Send Shopper Query
* **Endpoint:** `POST /api/chatbot/query` (also supports `/api/chatbot/chat/query`)
* **Request Payload:**
  ```json
  {
    "query": "mechanical gaming keyboard under 5000",
    "budget": 5000.00,
    "min_rating": 4.0
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "status": "success",
    "response": "Based on your criteria, I recommend the Keychron K2 Wireless Keyboard. It features Gateron G Pro switches and has an average rating of 5.0.",
    "source": "ollama",
    "rag_data": {
      "routed_dataset": "Keyboards",
      "matches": [
        {
          "id": 3,
          "name": "Keychron K2 Mechanical Keyboard",
          "price": 7499.00
        }
      ]
    }
  }
  ```

### Compare Products
* **Endpoint:** `POST /api/chatbot/compare`
* **Request Payload:**
  ```json
  {
    "query": "Keychron vs Razer"
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "status": "success",
    "entities": ["Keychron", "Razer"],
    "comparison": {
      "Keychron": {"average_price": 7499.00, "rating": 5.0},
      "Razer": {"average_price": 6200.00, "rating": 4.2}
    },
    "verdict": "Keychron is recommended for professional typing, while Razer excels at pure gaming response speeds."
  }
  ```

---

## 7. Search & Discovery Routers

### Semantic Search (`/api/search`)
* **Endpoint:** `GET /api/search?q=lightning+cable`
* **Success Response (200 OK):**
  ```json
  {
    "results": [
      {
        "id": 1,
        "name": "Wayona Nylon Braided USB to Lightning Cable",
        "relevance_score": 0.895
      }
    ]
  }
  ```

### Voice Search (`/api/voice-search`)
* **Endpoint:** `POST /api/voice-search`
* **Request Payload:** (Binary audio stream or multipart form data containing wav audio)
* **Success Response (200 OK):**
  ```json
  {
    "transcription": "usb charging cable",
    "results": [
      {
        "id": 1,
        "name": "Wayona Fast Charging Cable"
      }
    ]
  }
  ```

### Image Search (`/api/image-search`)
* **Endpoint:** `POST /api/image-search`
* **Request Payload:** (Multipart form containing image file)
* **Success Response (200 OK):**
  ```json
  {
    "matched_product_id": 2,
    "confidence": 0.9430,
    "matches": [
      {
        "id": 2,
        "name": "Ambrane Unbreakable Braided Cable"
      }
    ]
  }
  ```

---

## 8. Pricing Intelligence Router (`/api/price-prediction`)

### Predict Base Price
* **Endpoint:** `POST /api/price-prediction`
* **Request Payload:**
  ```json
  {
    "category": "Keyboards",
    "discounted_price": 7499.00,
    "discount_percentage": 25.0,
    "rating": 5.0,
    "rating_count": 1
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "status": "success",
    "predicted_actual_price": 9850.50,
    "original_actual_price_listed": 9999.00
  }
  ```

---

## 9. Error Codes and Status Payloads

The API uses standardized HTTP status codes to communicate client and server-side exceptions.

### 1. HTTP 400 Bad Request
Occurs when request payloads are missing required fields or validation checks fail.
```json
{
  "detail": [
    {
      "loc": ["body", "query"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 2. HTTP 401 Unauthorized
Occurs when the JWT authentication token is missing, expired, or invalid.
```json
{
  "detail": "Could not validate credentials"
}
```

### 3. HTTP 403 Forbidden
Occurs when the authenticated user attempts to access routes restricted to other roles (e.g. customer accessing admin dashboards).
```json
{
  "detail": "Insufficient permissions to access this resource"
}
```

### 4. HTTP 500 Internal Server Error
Occurs when database queries fail, ML models fail to load, or runtime code triggers exceptions.
```json
{
  "detail": "Database connection timeout. Please try again later."
}
```
