from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import pandas as pd
import numpy as np
import joblib
import os
import json
from datetime import datetime


# ============================================================
# FLASK SETUP
# ============================================================

app = Flask(__name__)

CORS(app)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

FRONTEND_DIR = os.path.join(
    BASE_DIR,
    "frontend"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "model"
)

FEEDBACK_FILE = os.path.join(
    BASE_DIR,
    "data",
    "inspector_feedback.json"
)


# ============================================================
# LOAD TRAINED ML MODEL
# ============================================================

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "risk_model.pkl"
)

ENCODER_PATH = os.path.join(
    MODEL_DIR,
    "risk_encoder.pkl"
)


try:

    model = joblib.load(MODEL_PATH)

    encoder = joblib.load(ENCODER_PATH)

    print("ML model loaded successfully!")

    print(
        "Risk classes:",
        list(encoder.classes_)
    )

except Exception as e:

    print(
        "ERROR loading ML model:",
        e
    )

    model = None
    encoder = None


# ============================================================
# MODEL FEATURES
# ============================================================

FEATURES = [

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


# ============================================================
# STORE LAST ANALYSIS
# ============================================================

latest_results = []


# ============================================================
# RISK EXPLANATION
# ============================================================

def generate_explanation(row, risk):

    reasons = []


    # Temperature
    if row["Temperature"] >= 90:

        reasons.append(
            "High operating temperature"
        )

    elif row["Temperature"] >= 80:

        reasons.append(
            "Elevated operating temperature"
        )


    # Vibration
    if row["Vibration"] >= 8:

        reasons.append(
            "High vibration level"
        )

    elif row["Vibration"] >= 5:

        reasons.append(
            "Elevated vibration level"
        )


    # Pressure
    if row["Pressure"] >= 10:

        reasons.append(
            "High pressure"
        )

    elif row["Pressure"] >= 8:

        reasons.append(
            "Elevated pressure"
        )


    # Failures
    if row["Failures_Last_Year"] >= 4:

        reasons.append(
            "Multiple failures recorded in the last year"
        )

    elif row["Failures_Last_Year"] >= 2:

        reasons.append(
            "Previous equipment failures detected"
        )


    # Maintenance
    if row["Maintenance_Due"] == 1:

        reasons.append(
            "Maintenance is currently due"
        )


    # Inspection
    if row["Inspection_Score"] < 50:

        reasons.append(
            "Low inspection score"
        )

    elif row["Inspection_Score"] < 70:

        reasons.append(
            "Inspection score requires attention"
        )


    # Incidents
    if row["Previous_Incidents"] >= 3:

        reasons.append(
            "Multiple previous safety incidents"
        )

    elif row["Previous_Incidents"] >= 1:

        reasons.append(
            "Previous safety incident recorded"
        )


    # Age
    if row["Age_Years"] >= 10:

        reasons.append(
            "Equipment has high operating age"
        )


    # If no specific reason
    if len(reasons) == 0:

        if risk == "LOW":

            reasons.append(
                "No major risk indicators detected"
            )

        else:

            reasons.append(
                "Several equipment parameters require monitoring"
            )


    return reasons


# ============================================================
# RECOMMENDED ACTION
# ============================================================

def generate_recommendation(row, risk):


    if risk == "HIGH":

        return (
            "Immediate inspection recommended. "
            "Check equipment condition, perform preventive "
            "maintenance and investigate abnormal sensor readings."
        )


    elif risk == "MEDIUM":

        return (
            "Schedule an inspection soon. "
            "Monitor sensor readings and perform required "
            "maintenance before the risk increases."
        )


    else:

        return (
            "Continue routine monitoring and scheduled maintenance. "
            "No immediate intervention is required."
        )


# ============================================================
# INSPECTION PRIORITY
# ============================================================

def get_priority(risk):

    if risk == "HIGH":

        return "Priority 1"

    elif risk == "MEDIUM":

        return "Priority 2"

    else:

        return "Priority 3"


# ============================================================
# RISK SCORE
# ============================================================

def get_risk_score(risk):

    if risk == "HIGH":

        return 3

    elif risk == "MEDIUM":

        return 2

    else:

        return 1


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_DIR,
        "index.html"
    )


# ============================================================
# UPLOAD PAGE
# ============================================================

@app.route("/upload")
def upload_page():

    return send_from_directory(
        FRONTEND_DIR,
        "upload.html"
    )


# ============================================================
# DASHBOARD PAGE
# ============================================================

@app.route("/dashboard")
def dashboard_page():

    return send_from_directory(
        FRONTEND_DIR,
        "dashboard.html"
    )


# ============================================================
# FRONTEND FILES
# ============================================================

@app.route("/<path:filename>")
def frontend_files(filename):

    return send_from_directory(
        FRONTEND_DIR,
        filename
    )


# ============================================================
# CSV ANALYSIS API
# ============================================================

@app.route(
    "/api/analyze",
    methods=["POST"]
)
def analyze_csv():

    global latest_results


    # --------------------------------------------------------
    # CHECK FILE
    # --------------------------------------------------------

    if "file" not in request.files:

        return jsonify({

            "success": False,

            "error":
            "No CSV file uploaded."

        }), 400


    file = request.files["file"]


    if file.filename == "":

        return jsonify({

            "success": False,

            "error":
            "No file selected."

        }), 400


    # --------------------------------------------------------
    # CHECK MODEL
    # --------------------------------------------------------

    if model is None or encoder is None:

        return jsonify({

            "success": False,

            "error":
            "ML model is not loaded. "
            "Please train the model first."

        }), 500


    try:

        # ----------------------------------------------------
        # READ CSV
        # ----------------------------------------------------

        data = pd.read_csv(file)


        print(
            "Uploaded records:",
            len(data)
        )


        # ----------------------------------------------------
        # CHECK REQUIRED COLUMNS
        # ----------------------------------------------------

        missing_columns = [

            column

            for column in FEATURES

            if column not in data.columns

        ]


        if len(missing_columns) > 0:

            return jsonify({

                "success": False,

                "error":
                "Missing required columns: "
                + ", ".join(missing_columns)

            }), 400


        # ----------------------------------------------------
        # CLEAN NUMERIC DATA
        # ----------------------------------------------------

        for column in FEATURES:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            )


        # ----------------------------------------------------
        # CHECK INVALID DATA
        # ----------------------------------------------------

        if data[FEATURES].isnull().any().any():

            return jsonify({

                "success": False,

                "error":
                "CSV contains missing or invalid "
                "values in required columns."

            }), 400


        # ----------------------------------------------------
        # CREATE MODEL INPUT
        # ----------------------------------------------------

        X = data[FEATURES]


        # ----------------------------------------------------
        # ML PREDICTION
        # ----------------------------------------------------

        predictions = model.predict(X)


        # ----------------------------------------------------
        # PREDICTION PROBABILITY
        # ----------------------------------------------------

        probabilities = None


        try:

            probabilities = model.predict_proba(X)

        except Exception:

            probabilities = None


        results = []


        # ----------------------------------------------------
        # PROCESS EACH MACHINE
        # ----------------------------------------------------

        for index, prediction in enumerate(predictions):


            # Convert number back to HIGH/MEDIUM/LOW

            risk = encoder.inverse_transform(
                [prediction]
            )[0]


            risk = str(
                risk
            ).upper()


            row = data.iloc[index]


            # ------------------------------------------------
            # CONFIDENCE
            # ------------------------------------------------

            confidence = 0


            if probabilities is not None:

                confidence = float(
                    max(
                        probabilities[index]
                    ) * 100
                )


            # ------------------------------------------------
            # EXPLANATION
            # ------------------------------------------------

            explanation_list = generate_explanation(
                row,
                risk
            )


            explanation = "; ".join(
                explanation_list
            )


            # ------------------------------------------------
            # RECOMMENDATION
            # ------------------------------------------------

            recommendation = generate_recommendation(
                row,
                risk
            )


            # ------------------------------------------------
            # PRIORITY
            # ------------------------------------------------

            priority = get_priority(
                risk
            )


            # ------------------------------------------------
            # RESULT OBJECT
            # ------------------------------------------------

            result = {

                "Equipment_ID":
                str(
                    row["Equipment_ID"]
                    if "Equipment_ID" in data.columns
                    else f"Equipment-{index + 1}"
                ),

                "Equipment_Type":
                str(
                    row["Equipment_Type"]
                    if "Equipment_Type" in data.columns
                    else "Unknown"
                ),

                "Risk_Level":
                risk,

                "Risk_Score":
                get_risk_score(risk),

                "Priority":
                priority,

                "Confidence":
                round(
                    confidence,
                    2
                ),

                "Explanation":
                explanation,

                "Recommendation":
                recommendation,

                "Temperature":
                float(
                    row["Temperature"]
                ),

                "Vibration":
                float(
                    row["Vibration"]
                ),

                "Pressure":
                float(
                    row["Pressure"]
                ),

                "Inspection_Score":
                float(
                    row["Inspection_Score"]
                ),

                "Failures_Last_Year":
                int(
                    row["Failures_Last_Year"]
                ),

                "Maintenance_Due":
                int(
                    row["Maintenance_Due"]
                ),

                "Previous_Incidents":
                int(
                    row["Previous_Incidents"]
                ),

                "Age_Years":
                float(
                    row["Age_Years"]
                ),

                "Operating_Hours":
                float(
                    row["Operating_Hours"]
                )

            }


            results.append(
                result
            )


        # ----------------------------------------------------
        # SORT EQUIPMENT
        # HIGH → MEDIUM → LOW
        # ----------------------------------------------------

        results.sort(

            key=lambda x:
            x["Risk_Score"],

            reverse=True

        )


        # ----------------------------------------------------
        # SAVE RESULTS
        # ----------------------------------------------------

        latest_results = results


        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        high_count = sum(

            1

            for item in results

            if item["Risk_Level"] == "HIGH"

        )


        medium_count = sum(

            1

            for item in results

            if item["Risk_Level"] == "MEDIUM"

        )


        low_count = sum(

            1

            for item in results

            if item["Risk_Level"] == "LOW"

        )


        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return jsonify({

            "success": True,

            "total_equipment":
            len(results),

            "high_risk":
            high_count,

            "medium_risk":
            medium_count,

            "low_risk":
            low_count,

            "results":
            results

        })


    except Exception as e:

        print(
            "ERROR:",
            str(e)
        )


        return jsonify({

            "success": False,

            "error":
            str(e)

        }), 500


# ============================================================
# GET LAST ANALYSIS
# ============================================================

@app.route(
    "/api/results",
    methods=["GET"]
)
def get_results():

    return jsonify({

        "success": True,

        "results":
        latest_results

    })


# ============================================================
# INSPECTOR FEEDBACK
# ============================================================

@app.route(
    "/api/feedback",
    methods=["POST"]
)
def save_feedback():


    try:

        feedback = request.get_json()


        if not feedback:

            return jsonify({

                "success": False,

                "error":
                "No feedback received."

            }), 400


        # ----------------------------------------------------
        # CREATE DATA FOLDER IF REQUIRED
        # ----------------------------------------------------

        os.makedirs(

            os.path.dirname(
                FEEDBACK_FILE
            ),

            exist_ok=True

        )


        # ----------------------------------------------------
        # LOAD EXISTING FEEDBACK
        # ----------------------------------------------------

        if os.path.exists(
            FEEDBACK_FILE
        ):

            try:

                with open(
                    FEEDBACK_FILE,
                    "r",
                    encoding="utf-8"
                ) as f:

                    feedback_data = json.load(f)

            except Exception:

                feedback_data = []

        else:

            feedback_data = []


        # ----------------------------------------------------
        # ADD DATE/TIME
        # ----------------------------------------------------

        feedback["timestamp"] = (
            datetime.now()
            .strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )


        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        feedback_data.append(
            feedback
        )


        with open(
            FEEDBACK_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(

                feedback_data,

                f,

                indent=4

            )


        return jsonify({

            "success": True,

            "message":
            "Inspector feedback saved successfully."

        })


    except Exception as e:

        return jsonify({

            "success": False,

            "error":
            str(e)

        }), 500


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print(
        "\n===================================="
    )

    print(
        "       PREDICTSAFE AI"
    )

    print(
        "===================================="
    )

    print(
        "Server running at:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print(
        "====================================\n"
    )


    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )