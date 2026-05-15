import pandas as pd
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

# ──────────────────────────────────────────────
#  LOAD DATASET
# ──────────────────────────────────────────────

data = pd.read_csv("dataset.csv")
print(f"Dataset shape: {data.shape}")
print(f"Result distribution:\n{data['Result'].value_counts()}\n")

X = data.drop("Result", axis=1)
y = data["Result"]

# ──────────────────────────────────────────────
#  TRAIN/TEST SPLIT
# ──────────────────────────────────────────────

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ──────────────────────────────────────────────
#  SCALER (needed for LR, SVM, KNN)
# ──────────────────────────────────────────────

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)
pickle.dump(scaler, open("scaler.pkl", "wb"))
print("scaler.pkl saved\n")

# ──────────────────────────────────────────────
#  MODEL DEFINITIONS
#  (name, model, use_scaled_input)
# ──────────────────────────────────────────────

model_configs = {
    "Logistic_Regression": (LogisticRegression(max_iter=1000), True),
    "Decision_Tree":       (DecisionTreeClassifier(random_state=42), False),
    "Random_Forest":       (RandomForestClassifier(n_estimators=100, random_state=42), False),
    "SVM":                 (SVC(probability=True, random_state=42), True),
    "KNN":                 (KNeighborsClassifier(n_neighbors=5), True),
}

# ──────────────────────────────────────────────
#  TRAIN ALL MODELS
# ──────────────────────────────────────────────

best_model      = None
best_model_name = ""
best_accuracy   = 0

for name, (model, use_scaled) in model_configs.items():
    print(f"Training: {name}")
    Xtr = X_train_sc if use_scaled else X_train
    Xte = X_test_sc  if use_scaled else X_test

    model.fit(Xtr, y_train)
    preds    = model.predict(Xte)
    accuracy = accuracy_score(y_test, preds)

    print(f"  Accuracy : {accuracy * 100:.2f}%")
    print(f"  Report   :\n{classification_report(y_test, preds, zero_division=0)}")

    filename = f"{name}.pkl"
    pickle.dump(model, open(filename, "wb"))
    print(f"  Saved as : {filename}\n")

    if accuracy > best_accuracy:
        best_accuracy   = accuracy
        best_model_name = name
        best_model      = model

# ──────────────────────────────────────────────
#  SAVE BEST MODEL
# ──────────────────────────────────────────────

pickle.dump(best_model, open("best_model.pkl", "wb"))
print(f"Best Model  : {best_model_name}")
print(f"Best Accuracy: {best_accuracy * 100:.2f}%")
print("Saved as best_model.pkl")
print("\nAll models trained and saved successfully!")