# 🏥 Liver Disease Prediction System

A Flask web application that predicts liver disease using 5 machine learning models — Logistic Regression, Decision Tree, Random Forest, SVM, and KNN — with patient login, history tracking, and a doctor dashboard.

---

## 📁 Project Structure

```
liver_disease/
├── app.py                    ← Flask routes (fixed)
├── train_model.py            ← Retrain all models (fixed)
├── dataset.csv               ← Training data (300 records, 10 features)
├── requirements.txt          ← Python dependencies (pinned versions)
├── scaler.pkl                ← StandardScaler (REQUIRED — generate by running train_model.py)
├── Logistic_Regression.pkl
├── Decision_Tree.pkl
├── Random_Forest.pkl
├── SVM.pkl
├── KNN.pkl
├── best_model.pkl
└── templates/
    ├── start.html
    ├── patient_signup.html
    ├── patient_login.html
    ├── predict.html
    ├── history.html
    ├── doctor_login.html
    └── doctor_dashboard.html
```

---

## ⚠️ Why Old .pkl Files Were Broken

The original `.pkl` files were trained with **scikit-learn 0.22** and are **not compatible** with scikit-learn 1.x. You must retrain models using `train_model.py` before running the app.

---

## 🚀 Setup Guide

### Step 1 — Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Setup Supabase Database

Go to [supabase.com](https://supabase.com) → SQL Editor → Run this:

```sql
CREATE TABLE IF NOT EXISTS patients (
    id       SERIAL PRIMARY KEY,
    name     VARCHAR(100) NOT NULL,
    email    VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS history (
    id               SERIAL PRIMARY KEY,
    email            VARCHAR(100),
    age              FLOAT,
    gender           INTEGER,
    total_bilirubin  FLOAT,
    sgpt             FLOAT,
    sgot             FLOAT,
    result           VARCHAR(50),
    created_at       TIMESTAMP DEFAULT NOW()
);
```

### Step 4 — Retrain Models (REQUIRED)

```bash
python train_model.py
```

This generates fresh `.pkl` files compatible with the installed scikit-learn version. Also creates `scaler.pkl` which is required by the app.

### Step 5 — Set Environment Variables

Create a `.env` file (or set in system):

```env
DATABASE_URL=postgresql://postgres:yourpassword@db.xxxx.supabase.co:5432/postgres
SECRET_KEY=any-long-random-string
DOCTOR_EMAIL=doctor@gmail.com
DOCTOR_PASSWORD=admin123

```
<!-- VluNtLPGVo0EqDZI -->
### Step 6 — Run the App

```bash
python app.py
```

Open: http://localhost:5000

---

## 🐛 Bugs Fixed

| Bug | Fix |
|-----|-----|
| Old `.pkl` files crash on scikit-learn 1.x | Retrain with `train_model.py` — generates compatible files |
| `scaler.pkl` missing — LR/SVM/KNN predict wrong | Added `StandardScaler`, saved as `scaler.pkl`, loaded in app |
| Single global DB connection crashes after idle/timeout | `get_db()` now creates a fresh connection per request |
| Login/Signup errors showed blank page | Proper error messages rendered in templates |
| `db` variable name clashed with Flask's `db` | Renamed to `db_` in predict route |
| No `ORDER BY` in history queries | Added `ORDER BY id DESC` |
| Doctor credentials hardcoded only | Now reads from environment variables |
| `psycopg2.fetchone()` returned tuple, not dict | Added `RealDictCursor` for dict-style row access |

---

## 🧠 Input Features

| Field | Description |
|-------|-------------|
| Age | Patient age in years |
| Gender | 1 = Male, 0 = Female |
| Total Bilirubin (TB) | mg/dL |
| Direct Bilirubin (DB) | mg/dL |
| Alkaline Phosphotase (ALK) | IU/L |
| SGPT | IU/L (Alanine Aminotransferase) |
| SGOT | IU/L (Aspartate Aminotransferase) |
| Total Proteins (TP) | g/dL |
| Albumin (ALB) | g/dL |
| A/G Ratio (AGR) | Albumin / Globulin ratio |

---

## 🔑 Default Doctor Login

```
Email:    doctor@gmail.com
Password: admin123
```

Change via environment variables before deploying.

---

## ☁️ Deploy on Render

1. Push to GitHub (add `.env` to `.gitignore`)
2. New Web Service → connect repo
3. Build Command: `pip install -r requirements.txt && python train_model.py`
4. Start Command: `gunicorn app:app`
5. Add environment variables in Render dashboard