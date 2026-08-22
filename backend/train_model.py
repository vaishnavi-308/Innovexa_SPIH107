import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report


# ==========================================
# 1. LOAD HISTORICAL INDUSTRIAL DATA
# ==========================================

data_path = "data/industrial_data.csv"

data = pd.read_csv(data_path)

print("Industrial data loaded successfully!")
print("Number of records:", len(data))


# ==========================================
# 2. FEATURES USED BY THE ML MODEL
# ==========================================

features = [
    "Age_Years",
    "Operating_Hours",
    "Failures_Last_Year",
    "Maintenance_Due",
    "Temperature",
    "Vibration",
    "Pressure",
    "Inspection_Score",
    "Previous_Incidents"
]

X = data[features]

y = data["Risk_Level"]


# ==========================================
# 3. CONVERT LOW/MEDIUM/HIGH TO NUMBERS
# ==========================================

encoder = LabelEncoder()

y_encoded = encoder.fit_transform(y)

print("\nRisk classes:")
print(list(encoder.classes_))


# ==========================================
# 4. SPLIT DATA
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.20,
    random_state=42,
    stratify=y_encoded
)

print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))


# ==========================================
# 5. CREATE RANDOM FOREST MODEL
# ==========================================

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42,
    class_weight="balanced"
)


# ==========================================
# 6. TRAIN THE ML MODEL
# ==========================================

print("\nTraining PredictSafe ML model...")

model.fit(X_train, y_train)

print("Training completed!")


# ==========================================
# 7. TEST THE MODEL
# ==========================================

predictions = model.predict(X_test)

accuracy = accuracy_score(
    y_test,
    predictions
)

print("\n--------------------------------")
print("MODEL PERFORMANCE")
print("--------------------------------")

print(
    "Accuracy:",
    round(accuracy * 100, 2),
    "%"
)

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions,
        target_names=encoder.classes_,
        zero_division=0
    )
)


# ==========================================
# 8. CREATE MODEL FOLDER
# ==========================================

model_folder = "model"

os.makedirs(
    model_folder,
    exist_ok=True
)


# ==========================================
# 9. SAVE TRAINED MODEL
# ==========================================

model_path = os.path.join(
    model_folder,
    "risk_model.pkl"
)

encoder_path = os.path.join(
    model_folder,
    "risk_encoder.pkl"
)


joblib.dump(
    model,
    model_path
)

joblib.dump(
    encoder,
    encoder_path
)


# ==========================================
# 10. FINISHED
# ==========================================

print("\n--------------------------------")
print("PREDICTSAFE MODEL READY")
print("--------------------------------")

print("ML model saved to:")
print(model_path)

print("Risk encoder saved to:")
print(encoder_path)

print("\nYou can now use the trained model")
print("to predict risks from a new CSV file.")