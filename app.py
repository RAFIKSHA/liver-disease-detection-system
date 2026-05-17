# from flask import Flask, render_template, request, redirect, session
# import requests
# import pickle
# import numpy as np
# import os
# from dotenv import load_dotenv
# from groq import Groq

# load_dotenv()

# # ──────────────────────────────
# # GROQ CLIENT (SAFE INIT)
# # ──────────────────────────────
# client = None
# if os.getenv("GROQ_API_KEY"):
#     client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# # ──────────────────────────────
# # FLASK APP
# # ──────────────────────────────
# app = Flask(__name__)
# app.secret_key = os.environ.get("SECRET_KEY", "any-long-random-string")

# # ──────────────────────────────
# # SUPABASE CONFIG
# # ──────────────────────────────
# SUPABASE_URL = os.environ.get("SUPABASE_URL")
# SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# HEADERS = {
#     "apikey": SUPABASE_KEY,
#     "Authorization": f"Bearer {SUPABASE_KEY}",
#     "Content-Type": "application/json",
#     "Prefer": "return=representation"
# }

# # ──────────────────────────────
# # SUPABASE FUNCTIONS
# # ──────────────────────────────
# def sb_get(table, params=None):
#     response = requests.get(
#         f"{SUPABASE_URL}/rest/v1/{table}",
#         headers=HEADERS,
#         params=params
#     )
#     return response.json()


# def sb_post(table, data):
#     response = requests.post(
#         f"{SUPABASE_URL}/rest/v1/{table}",
#         headers=HEADERS,
#         json=data
#     )
#     return response


# # ──────────────────────────────
# # EXPLAINABLE AI (SAFE + FALLBACK)
# # ──────────────────────────────
# def generate_ai_explanation(results, form_data):

#     disease_count = sum(1 for r in results.values() if r == "Disease Detected")
#     total_models = len(results)

#     # ── RULE BASED EXPLANATION (ALWAYS WORKS)
#     if disease_count >= 3:
#         risk_level = "HIGH RISK"
#         base_explanation = "Multiple AI models strongly indicate liver disease. Immediate medical consultation is recommended."
#     elif disease_count == 2:
#         risk_level = "MODERATE RISK"
#         base_explanation = "Some models indicate possible liver abnormality. Further clinical tests are advised."
#     else:
#         risk_level = "LOW RISK"
#         base_explanation = "Most AI models indicate normal liver condition. Maintain healthy lifestyle."

#     # ── OPTIONAL GROQ ENHANCEMENT
#     if client:
#         try:
#             prompt = f"""
# You are a medical assistant.

# Patient age: {form_data['age']}
# Gender: {form_data['gender']}

# Model results:
# {results}

# Give short clinical explanation.
# """

#             response = client.chat.completions.create(
#                 model="llama3-70b-8192",
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.4,
#                 max_tokens=300
#             )

#             ai_text = response.choices[0].message.content

#         except Exception:
#             ai_text = base_explanation

#     else:
#         ai_text = base_explanation

#     return f"""
# MODEL CONSENSUS REPORT
# ----------------------
# Total Models: {total_models}
# Positive Predictions: {disease_count}

# Risk Level: {risk_level}

# Clinical Explanation:
# {ai_text}

# NOTE:
# - Based on machine learning consensus
# - Not a final medical diagnosis
# - Consult doctor for confirmation
# """


# # ──────────────────────────────
# # LOAD MODELS
# # ──────────────────────────────
# scaler = pickle.load(open("scaler.pkl", "rb"))

# models = {
#     "Logistic Regression": (pickle.load(open("Logistic_Regression.pkl", "rb")), True),
#     "Decision Tree": (pickle.load(open("Decision_Tree.pkl", "rb")), False),
#     "Random Forest": (pickle.load(open("Random_Forest.pkl", "rb")), False),
#     "SVM": (pickle.load(open("SVM.pkl", "rb")), True),
#     "KNN": (pickle.load(open("KNN.pkl", "rb")), True),
# }


# # ──────────────────────────────
# # ROUTES (UNCHANGED LOGIC)
# # ──────────────────────────────

# @app.route("/")
# def home():
#     return render_template("start.html")


# @app.route("/patient_signup", methods=["GET", "POST"])
# def patient_signup():

#     if request.method == "POST":

#         name = request.form["name"].strip()
#         email = request.form["email"].strip().lower()
#         password = request.form["password"]

#         existing = sb_get("patients", {
#             "email": f"eq.{email}",
#             "select": "id"
#         })

#         if existing:
#             return render_template("patient_signup.html", error="Email already registered")

#         response = sb_post("patients", {
#             "name": name,
#             "email": email,
#             "password": password
#         })

#         if response.status_code in [200, 201]:
#             session["user"] = email
#             session["uname"] = name
#             return redirect("/predict_page")

#         return render_template("patient_signup.html", error="Signup Failed")

#     return render_template("patient_signup.html")


# @app.route("/patient_login", methods=["GET", "POST"])
# def patient_login():

#     if request.method == "POST":

#         email = request.form["email"].strip().lower()
#         password = request.form["password"]

#         result = sb_get("patients", {
#             "email": f"eq.{email}",
#             "password": f"eq.{password}",
#             "select": "*"
#         })

#         if result:
#             session["user"] = email
#             session["uname"] = result[0]["name"]
#             return redirect("/predict_page")

#         return render_template("patient_login.html", error="Invalid Credentials")

#     return render_template("patient_login.html")


# @app.route("/predict_page")
# def predict_page():
#     if "user" not in session:
#         return redirect("/patient_login")
#     return render_template("predict.html")


# # ──────────────────────────────
# # PREDICTION
# # ──────────────────────────────
# @app.route("/predict", methods=["POST"])
# def predict():

#     if "user" not in session:
#         return redirect("/patient_login")

#     try:

#         age = float(request.form["age"])
#         gender = float(request.form["gender"])
#         tb = float(request.form["tb"])
#         db_ = float(request.form["db"])
#         alk = float(request.form["alk"])
#         sgpt = float(request.form["sgpt"])
#         sgot = float(request.form["sgot"])
#         tp = float(request.form["tp"])
#         alb = float(request.form["alb"])
#         agr = float(request.form["agr"])

#         raw_data = np.array([[age, gender, tb, db_, alk, sgpt, sgot, tp, alb, agr]])
#         scaled_data = scaler.transform(raw_data)

#         results = {}

#         for name, (model, use_scaled) in models.items():
#             inp = scaled_data if use_scaled else raw_data
#             pred = model.predict(inp)[0]
#             results[name] = "Disease Detected" if pred == 1 else "No Disease"

#         rf_result = results["Random Forest"]

#         sb_post("history", {
#             "email": session["user"],
#             "age": age,
#             "gender": int(gender),
#             "total_bilirubin": tb,
#             "sgpt": sgpt,
#             "sgot": sgot,
#             "result": rf_result
#         })

#         # 🔥 SAFE EXPLAINABLE AI
#         ai_explanation = generate_ai_explanation(results, request.form)

#         return render_template(
#             "predict.html",
#             results=results,
#             ai_explanation=ai_explanation
#         )

#     except Exception as e:
#         return render_template("predict.html", error=str(e))


# # ──────────────────────────────
# # HISTORY + DOCTOR + LOGOUT (SAME)
# # ──────────────────────────────
# @app.route("/history")
# def history():
#     if "user" not in session:
#         return redirect("/patient_login")

#     data = sb_get("history", {
#         "email": f"eq.{session['user']}",
#         "order": "id.desc",
#         "select": "*"
#     })

#     return render_template("history.html", data=data)


# @app.route("/doctor_login", methods=["GET", "POST"])
# def doctor_login():

#     if request.method == "POST":

#         email = request.form["email"].strip().lower()
#         password = request.form["password"]

#         doctor_email = os.environ.get("DOCTOR_EMAIL", "doctor@gmail.com").lower()
#         doctor_password = os.environ.get("DOCTOR_PASSWORD", "admin123")

#         if email == doctor_email and password == doctor_password:
#             session["doctor"] = email
#             return redirect("/doctor_dashboard")

#         return render_template("doctor_login.html", error="Invalid Doctor Credentials")

#     return render_template("doctor_login.html")


# @app.route("/doctor_dashboard")
# def doctor_dashboard():

#     if "doctor" not in session:
#         return redirect("/doctor_login")

#     data = sb_get("history", {
#         "order": "id.desc",
#         "select": "*"
#     })

#     return render_template("doctor_dashboard.html", data=data)


# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect("/")


# if __name__ == "__main__":
#     app.run(debug=True)
from flask import Flask, render_template, request, redirect, session
import requests
import pickle
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────
# GROQ CLIENT (SAFE INIT)
# ──────────────────────────────
client = None
try:
    from groq import Groq
    if os.getenv("GROQ_API_KEY"):
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except ImportError:
    pass

# ──────────────────────────────
# FLASK APP
# ──────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "any-long-random-string")

# ──────────────────────────────
# SUPABASE CONFIG
# ──────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ──────────────────────────────
# SUPABASE FUNCTIONS
# ──────────────────────────────
def sb_get(table, params=None):
    response = requests.get(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        params=params
    )
    return response.json()


def sb_post(table, data):
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS,
        json=data
    )
    return response


# ──────────────────────────────
# EXPLAINABLE AI (SAFE + FALLBACK)
# ──────────────────────────────
def generate_ai_explanation(results, form_data):

    disease_count = sum(1 for r in results.values() if r == "Disease Detected")
    total_models = len(results)

    # ── RULE BASED EXPLANATION (ALWAYS WORKS)
    if disease_count >= 3:
        risk_level = "HIGH RISK"
        base_explanation = "Multiple AI models strongly indicate liver disease. Immediate medical consultation is recommended."
    elif disease_count == 2:
        risk_level = "MODERATE RISK"
        base_explanation = "Some models indicate possible liver abnormality. Further clinical tests are advised."
    else:
        risk_level = "LOW RISK"
        base_explanation = "Most AI models indicate normal liver condition. Maintain healthy lifestyle."

    # ── OPTIONAL GROQ ENHANCEMENT
    if client:
        try:
            prompt = f"""
You are a medical assistant.

Patient age: {form_data['age']}
Gender: {form_data['gender']}

Model results:
{results}

Give short clinical explanation.
"""
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=300
            )
            ai_text = response.choices[0].message.content

        except Exception:
            ai_text = base_explanation

    else:
        ai_text = base_explanation

    return f"""
MODEL CONSENSUS REPORT
----------------------
Total Models: {total_models}
Positive Predictions: {disease_count}

Risk Level: {risk_level}

Clinical Explanation:
{ai_text}

NOTE:
- Based on machine learning consensus
- Not a final medical diagnosis
- Consult doctor for confirmation
"""


# ──────────────────────────────
# LOAD MODELS — Safe loading with BASE_DIR
# ──────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_pkl(filename):
    return pickle.load(open(os.path.join(BASE_DIR, filename), "rb"))

scaler = load_pkl("scaler.pkl")

models = {
    "Logistic Regression": (load_pkl("Logistic_Regression.pkl"), True),
    "Decision Tree":       (load_pkl("Decision_Tree.pkl"), False),
    "Random Forest":       (load_pkl("Random_Forest.pkl"), False),
    "SVM":                 (load_pkl("SVM.pkl"), True),
    "KNN":                 (load_pkl("KNN.pkl"), True),
}


# ──────────────────────────────
# ROUTES
# ──────────────────────────────

@app.route("/")
def home():
    return render_template("start.html")


@app.route("/patient_signup", methods=["GET", "POST"])
def patient_signup():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        existing = sb_get("patients", {
            "email": f"eq.{email}",
            "select": "id"
        })

        if existing:
            return render_template("patient_signup.html", error="Email already registered")

        response = sb_post("patients", {
            "name": name,
            "email": email,
            "password": password
        })

        if response.status_code in [200, 201]:
            session["user"] = email
            session["uname"] = name
            return redirect("/predict_page")

        return render_template("patient_signup.html", error="Signup Failed")

    return render_template("patient_signup.html")


@app.route("/patient_login", methods=["GET", "POST"])
def patient_login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        result = sb_get("patients", {
            "email": f"eq.{email}",
            "password": f"eq.{password}",
            "select": "*"
        })

        if result:
            session["user"] = email
            session["uname"] = result[0]["name"]
            return redirect("/predict_page")

        return render_template("patient_login.html", error="Invalid Credentials")

    return render_template("patient_login.html")


@app.route("/predict_page")
def predict_page():
    if "user" not in session:
        return redirect("/patient_login")
    return render_template("predict.html")


# ──────────────────────────────
# PREDICTION
# ──────────────────────────────
@app.route("/predict", methods=["POST"])
def predict():

    if "user" not in session:
        return redirect("/patient_login")

    try:

        age = float(request.form["age"])
        gender = float(request.form["gender"])
        tb = float(request.form["tb"])
        db_ = float(request.form["db"])
        alk = float(request.form["alk"])
        sgpt = float(request.form["sgpt"])
        sgot = float(request.form["sgot"])
        tp = float(request.form["tp"])
        alb = float(request.form["alb"])
        agr = float(request.form["agr"])

        raw_data = np.array([[age, gender, tb, db_, alk, sgpt, sgot, tp, alb, agr]])
        scaled_data = scaler.transform(raw_data)

        results = {}

        for name, (model, use_scaled) in models.items():
            inp = scaled_data if use_scaled else raw_data
            pred = model.predict(inp)[0]
            results[name] = "Disease Detected" if pred == 1 else "No Disease"

        rf_result = results["Random Forest"]

        sb_post("history", {
            "email": session["user"],
            "age": age,
            "gender": int(gender),
            "total_bilirubin": tb,
            "sgpt": sgpt,
            "sgot": sgot,
            "result": rf_result
        })

        ai_explanation = generate_ai_explanation(results, request.form)

        return render_template(
            "predict.html",
            results=results,
            ai_explanation=ai_explanation
        )

    except Exception as e:
        return render_template("predict.html", error=str(e))


# ──────────────────────────────
# HISTORY + DOCTOR + LOGOUT
# ──────────────────────────────
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/patient_login")

    data = sb_get("history", {
        "email": f"eq.{session['user']}",
        "order": "id.desc",
        "select": "*"
    })

    return render_template("history.html", data=data)


@app.route("/doctor_login", methods=["GET", "POST"])
def doctor_login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        doctor_email = os.environ.get("DOCTOR_EMAIL", "doctor@gmail.com").lower()
        doctor_password = os.environ.get("DOCTOR_PASSWORD", "admin123")

        if email == doctor_email and password == doctor_password:
            session["doctor"] = email
            return redirect("/doctor_dashboard")

        return render_template("doctor_login.html", error="Invalid Doctor Credentials")

    return render_template("doctor_login.html")


@app.route("/doctor_dashboard")
def doctor_dashboard():

    if "doctor" not in session:
        return redirect("/doctor_login")

    data = sb_get("history", {
        "order": "id.desc",
        "select": "*"
    })

    return render_template("doctor_dashboard.html", data=data)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)