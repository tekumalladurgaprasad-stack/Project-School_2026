# CrediGuard - Credit Risk Monitoring & Decision Support Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5%2B-F7931E.svg)](https://scikit-learn.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0%2B-47A248.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**CrediGuard** is a full-stack, machine learning-driven credit risk assessment and monitoring platform. It enables credit risk analysts, financial institutions, and underwriters to evaluate the likelihood of credit card client default, record client repayment history, and maintain an audit trail of risk assessments in real-time.

---

## Table of Contents

- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Machine Learning Model](#machine-learning-model)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [API Reference](#api-reference)
- [Sample Data](#sample-data)
- [Project Directory Structure](#project-directory-structure)

---

## Key Features

1. **Executive Risk Dashboard**
   - Live metrics: Total Customers, Average Credit Limit, Delayed Payers, and On-Time Customers.
   - Live **Recent Risk Assessments** table showing the latest automated evaluations and risk tiers.

2. **Customer Onboarding & Management**
   - **Manual Entry:** Form with validation against demographic, repayment, and bill parameters.
   - **Bulk Upload:** Batch ingestion of customer records via CSV or JSON files with error handling.

3. **Machine Learning Risk Assessment Engine**
   - **Random Forest Classifier** trained on 30,000 credit records.
   - **Cost-Sensitive Decision Threshold ($0.1779$):** Optimized to minimize asymmetric financial losses (where false negatives / undetected defaults are 5x more costly than false positives).
   - Instant risk classification: **Low Risk**, **Moderate Risk**, or **High Risk**.

4. **Prediction History & Auditing**
   - Every risk evaluation is recorded in MongoDB with timestamp, customer summary, predicted default probability, decision cutoff, and classification.
   - Filterable and refreshable audit table.

5. **Direct In-Table Assessment**
   - Dedicated `⚡ Assess Risk` button beside each customer in the records list for on-demand evaluation.

---

## System Architecture

```
[ Frontend: HTML5 / Modern CSS / Vanilla JS ]
          │                           │
          │ (HTTP / REST)             │ (Static Assets)
          ▼                           ▼
[ FastAPI Server (Port 8000) ]  [ Python HTTP Server (Port 3000) ]
   ├── Endpoints: /customers, /predict, /predictions
   ├── Validation: Pydantic schemas (schemas.py)
   ├── Preprocessing: Feature encoder (preprocessing.py)
   └── Model Engine: Random Forest Pipeline (.pkl)
          │
          ▼
   [ MongoDB (localhost:27017) ]
      └── Database: CrediGuard
          ├── Collection: customers
          └── Collection: predictions
```

---

## Machine Learning Model

- **Dataset:** UCI *Default of Credit Card Clients Dataset* (30,000 records).
- **Features Used (28 features):**
  - Demographic: `LIMIT_BAL`, `SEX`, `AGE`, `EDUCATION` (one-hot), `MARRIAGE` (one-hot).
  - Repayment Status: `PAY_0` to `PAY_6` (history over 6 months).
  - Billing History: `BILL_AMT1` to `BILL_AMT6`.
  - Payment History: `PAY_AMT1` to `PAY_AMT6`.
- **Model Parameters:**
  - Algorithm: Random Forest Classifier
  - Estimators: 150
  - Optimal Cutoff Threshold: `0.1779`
  - Cost Matrix: False Negative Cost = 5, False Positive Cost = 1

---

## Prerequisites

Before starting, ensure you have the following installed:

1. **Python 3.10+** (Python 3.12 recommended)
   - Verify: `python --version`
2. **MongoDB Community Server** (running locally on port `27017`)
   - Verify (Windows PowerShell): `Get-Service MongoDB`
   - Start if stopped: `net start MongoDB`
3. **Git**
   - Verify: `git --version`

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/tekumalladurgaprasad-stack/Project-School_2026.git
   cd Project-School_2026
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify / Generate the trained model artifact:**
   The pre-trained model file `random_forest_credit_default.pkl` is located in `App/backend/`. If you wish to retrain or regenerate it:
   ```bash
   python App/backend/train_model.py
   ```

---

## Running the Application

### Step 1: Start the Backend (FastAPI)

```bash
cd App/backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
- **Backend URL:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Step 2: Start the Frontend

In a **second terminal** window:
```bash
cd App/frontend
python -m http.server 3000
```
- **Frontend URL:** [http://127.0.0.1:3000](http://127.0.0.1:3000)

*(Alternatively, you can open `App/frontend/index.html` directly in any web browser.)*

---

## API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/customers` | Fetch all registered customers from MongoDB |
| `POST` | `/customers` | Register a new customer and automatically compute & log risk assessment |
| `POST` | `/predict` | Evaluate default risk for customer parameters without saving to client registry |
| `GET` | `/predictions` | Fetch chronological risk assessment history |
| `GET` | `/docs` | Interactive Swagger API documentation |

---

## Sample Data

### Low-Risk Profile (Pays on Time)
```json
{
  "LIMIT_BAL": 200000,
  "SEX": 2,
  "EDUCATION": 2,
  "MARRIAGE": 2,
  "AGE": 32,
  "PAY_0": -1, "PAY_2": -1, "PAY_3": -1, "PAY_4": -1, "PAY_5": -1, "PAY_6": -1,
  "BILL_AMT1": 15000, "BILL_AMT2": 14200, "BILL_AMT3": 12800, "BILL_AMT4": 16000, "BILL_AMT5": 11000, "BILL_AMT6": 9500,
  "PAY_AMT1": 15000, "PAY_AMT2": 14200, "PAY_AMT3": 12800, "PAY_AMT4": 16000, "PAY_AMT5": 11000, "PAY_AMT6": 9500
}
```

### High-Risk Profile (Repeated Delays)
```json
{
  "LIMIT_BAL": 30000,
  "SEX": 1,
  "EDUCATION": 3,
  "MARRIAGE": 2,
  "AGE": 24,
  "PAY_0": 2, "PAY_2": 2, "PAY_3": 2, "PAY_4": 0, "PAY_5": 0, "PAY_6": -1,
  "BILL_AMT1": 29500, "BILL_AMT2": 28800, "BILL_AMT3": 27000, "BILL_AMT4": 25000, "BILL_AMT5": 18000, "BILL_AMT6": 5000,
  "PAY_AMT1": 0, "PAY_AMT2": 500, "PAY_AMT3": 0, "PAY_AMT4": 1000, "PAY_AMT5": 1500, "PAY_AMT6": 5000
}
```

---

## Project Directory Structure

```
Project-School_2026/
├── App/
│   ├── backend/
│   │   ├── database.py                     # MongoDB connection & CRUD operations
│   │   ├── main.py                         # FastAPI server routes & endpoints
│   │   ├── preprocessing.py                # Feature encoding & inference pipeline
│   │   ├── random_forest_credit_default.pkl# Trained ML model artifact
│   │   ├── Random_Forest.ipynb             # Research & exploration notebook
│   │   ├── requirements.txt                # Backend dependencies
│   │   ├── schemas.py                      # Pydantic data schemas & validation
│   │   └── train_model.py                  # Standalone model training script
│   └── frontend/
│       ├── index.html                      # Single page application markup
│       ├── script.js                       # Frontend state & API integration logic
│       └── style.css                       # Modern UI styling & responsive layout
├── default_of_credit_card_clients.xls      # Benchmark dataset
├── Model.ipynb                             # Model comparison notebook
├── requirements.txt                        # Global project dependencies
├── .gitignore                              # Git exclusion rules
└── README.md                               # Project documentation
```

---

## License

This project is licensed under the MIT License.
