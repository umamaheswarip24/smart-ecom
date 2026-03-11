# 🛒 Smart E-Commerce Checkout Workflow

## Overview
A cloud-native, microservices-based e-commerce checkout system that demonstrates 
end-to-end order processing using REST APIs, asynchronous messaging, and persistent 
database storage — without a UI.

The system mimics real-world platforms like Amazon/Flipkart where Cart, Payment, 
Inventory, and Discount are **independent but coordinated services**.

## Objective
Connect individual microservices (Cart, Payment, Inventory, Discount) into a 
complete checkout pipeline demonstrated entirely through API calls using Postman.

---

## Architecture

```
+------------------+        +-------------------+
|   Cart Service   |        | Discount Function |
|   (Node.js:3001) |        | (Serverless:3000) |
+--------+---------+        +---------+---------+
         |                            |
         |  POST /pay (with items)    |
         +------------+---------------+
                      |
             +--------v---------+
             |  Payment Service |
             |  (Python:3002)   |
             +--------+---------+
                      |
          +-----------+-----------+
          |                       |
   [REST Response]        [RabbitMQ Publish]
          |                       |
   Client gets            +-------v--------+
   final amount           |   RabbitMQ     |
                          |  events queue  |
                          +-------+--------+
                                  |
                         +--------v----------+
                         | Inventory Service |
                         | (Java/Spring:3003)|
                         +--------+----------+
                                  |
                          +-------v-------+
                          |     MySQL     |
                          |   Database    |
                          +---------------+
```

### Flow Explanation
1. **Cart** — Items are added to cart via POST /add
2. **Discount** — Discount code is validated via Serverless function
3. **Payment** — Payment is processed with or without discount
4. **RabbitMQ** — Payment publishes `payment_processed` event asynchronously
5. **Inventory** — Consumes the event and updates stock in MySQL

---

## Tech Stack

| Service | Technology | Purpose |
|---|---|---|
| Cart Service | Node.js, Express | Manages cart items in memory |
| Payment Service | Python, Flask | Processes payments and applies discounts |
| Inventory Service | Java, Spring Boot | Manages stock with MySQL persistence |
| Discount Function | Node.js, Serverless Offline | Simulates AWS Lambda discount logic |
| Message Broker | RabbitMQ | Async communication between Payment and Inventory |
| Database | MySQL 8 | Persists inventory, cart and payment records |
| Containerization | Docker, Docker Compose | Runs all services together |
| Orchestration | Kubernetes (k8s) | Scales and manages cart service deployment |

---

## Project Structure

```
smart-ecom/
├── cart-service/
│   ├── index.js          # Express server with POST /add and GET /view
│   ├── package.json      # Node dependencies
│   └── Dockerfile        # Container definition
│
├── payment-service/
│   ├── app.py            # Flask server with discount logic and RabbitMQ publish
│   ├── notify.py         # Standalone RabbitMQ publisher (testing)
│   └── Dockerfile        # Container definition
│
├── inventory-service/
│   ├── src/
│   │   └── main/java/com/example/inventory/
│   │       ├── InventoryController.java  # REST API endpoints
│   │       ├── Stock.java                # Entity/Model
│   │       └── StockRepository.java      # JPA MySQL operations
│   ├── consumer.py       # RabbitMQ event listener
│   ├── pom.xml           # Java dependencies
│   └── Dockerfile        # Container definition
│
├── discount-function/
│   ├── handler.js        # Serverless Lambda function
│   ├── serverless.yml    # Serverless framework config
│   └── package.json      # Node dependencies
│
├── deploy/
│   ├── docker-compose.yml  # Runs all services together
│   ├── init.sql            # Creates MySQL tables on startup
│   ├── k8s-cart.yaml       # Kubernetes deployment for cart
│   └── nginx.conf          # Reverse proxy config
│
└── README.md
```

---

## How to Run

### Prerequisites
- Docker Desktop installed and running
- Node.js 18+ installed
- Postman installed

### Step 1 — Clone the Repository
```bash
git clone <your-github-url>
cd smart-ecom
```

### Step 2 — Start All Services
```bash
cd deploy
docker-compose up --build
```

This will start all 6 services:
- Cart Service on http://localhost:3001
- Payment Service on http://localhost:3002
- Inventory Service on http://localhost:3003
- Discount Function on http://localhost:3000
- RabbitMQ Dashboard on http://localhost:15672
- MySQL on port 3307

### Step 3 — Verify All Services Are Running
Open browser and check:
- RabbitMQ Dashboard → http://localhost:15672
  - Username: `guest`
  - Password: `guest`

### Step 4 — Run Inventory Consumer
Open a new terminal and run:
```bash
cd inventory-service
pip install pika requests
python consumer.py
```

### Step 5 — Test APIs Using Postman
Follow the API Endpoints section below to test the full checkout flow.

---

## API Endpoints

### 1. Inventory Service (http://localhost:3003)

#### POST /inventory/add — Add new inventory item
```json
Request Body:
{
  "name": "Laptop",
  "qty": 50
}

Response:
{
  "id": 1,
  "name": "Laptop",
  "qty": 50
}
```

#### GET /inventory/{id} — Get specific item
```
GET http://localhost:3003/inventory/1

Response:
{
  "id": 1,
  "name": "Laptop",
  "qty": 50
}
```

#### GET /inventory/view — Get all items
```
GET http://localhost:3003/inventory/view

Response:
[
  { "id": 1, "name": "Laptop", "qty": 50 }
]
```

#### PUT /inventory/update/{id} — Update quantity
```json
Request Body:
{
  "qty": 45
}

Response:
{
  "id": 1,
  "name": "Laptop",
  "qty": 45
}
```

---

### 2. Cart Service (http://localhost:3001)

#### POST /add — Add item to cart
```json
Request Body:
{
  "item": "Laptop"
}

Response:
{
  "cart": ["Laptop"]
}
```

#### GET /view — View cart contents
```
GET http://localhost:3001/view

Response:
{
  "cart": ["Laptop"]
}
```

---

### 3. Payment Service (http://localhost:3002)

#### POST /pay — Payment WITHOUT discount
```json
Request Body:
{
  "amount": 1000,
  "method": "card"
}

Response:
{
  "status": "success",
  "original_amount": 1000,
  "discount": "0%",
  "final_amount": 1000.0,
  "method": "card",
  "event_published": true
}
```

#### POST /pay — Payment WITH discount
```json
Request Body:
{
  "amount": 1000,
  "method": "card",
  "discount_code": "NEWYEAR"
}

Response:
{
  "status": "success",
  "original_amount": 1000,
  "discount": "20%",
  "final_amount": 800.0,
  "method": "card",
  "event_published": true
}
```

---

### 4. Discount Function (http://localhost:3000)

#### POST /dev/apply-discount — Apply discount code
```json
Request Body:
{
  "code": "NEWYEAR"
}

Response:
{
  "discount": 0.2
}
```

#### POST /dev/apply-discount — Invalid code
```json
Request Body:
{
  "code": "INVALID"
}

Response:
{
  "discount": 0
}
```

---

## End-to-End Checkout Flow

This section demonstrates the complete checkout choreography using Postman.
The flow follows: Cart → Discount → Payment → RabbitMQ → Inventory

### Step 1 — Add Item to Inventory
```
POST http://localhost:3003/inventory/add
Body: { "name": "Laptop", "qty": 50 }
```
✅ Confirms inventory exists in MySQL before purchase

### Step 2 — Add Item to Cart
```
POST http://localhost:3001/add
Body: { "item": "Laptop" }
```
✅ Confirms item is in cart before checkout

### Step 3 — View Cart
```
GET http://localhost:3001/view
```
✅ Confirms cart contents before payment

### Step 4 — Apply Discount Code
```
POST http://localhost:3000/dev/apply-discount
Body: { "code": "NEWYEAR" }
```
✅ Confirms 20% discount is applied to cart total

### Step 5 — Process Payment WITH Discount
```
POST http://localhost:3002/pay
Body: {
  "amount": 1000,
  "method": "card",
  "discount_code": "NEWYEAR"
}
```
✅ Confirms final amount is 800 after 20% discount
✅ Confirms payment_processed event published to RabbitMQ

### Step 6 — Process Payment WITHOUT Discount
```
POST http://localhost:3002/pay
Body: {
  "amount": 1000,
  "method": "card"
}
```
✅ Confirms full amount 1000 is charged with no discount

### Step 7 — Verify RabbitMQ Event
```
Open http://localhost:15672
Login: guest / guest
Check events queue for payment_processed message
```
✅ Confirms asynchronous messaging is working

### Step 8 — Verify Inventory Updated in MySQL
```
GET http://localhost:3003/inventory/view
```
✅ Confirms inventory persists in MySQL after purchase

## System Resilience
- **Inventory updates persist in MySQL** — data survives service restarts
- **RabbitMQ events confirm async communication** — payment and inventory are decoupled
- **Independent services** — each service can be scaled or updated without affecting others
- **Real-world workflow** — mimics Amazon/Flipkart checkout pipeline

---

## Screenshots

### 1. All Services Running

### 2. Consumer Waiting for Events

### 3. Inventory Service — Add Item

### 4. Inventory Service — View All Items

### 5. Inventory Service — Get By ID

### 6. Cart Service — Add Item

### 7. Cart Service — View Cart

### 8. Discount Function — Apply NEWYEAR Code

### 9. Payment — Without Discount

### 10. Consumer — Event Received

### 11. Payment — With Discount

### 12. Consumer — Second Event Received

### 13. RabbitMQ Dashboard — Events Queue

### 14. MySQL — Inventory Persisted

### 15. MySQL — Payments Table
