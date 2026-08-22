def predict_risk(data):

    results = []

    for index, row in data.iterrows():

        # Get equipment ID
        equipment = row.get(
            "Equipment_ID",
            f"Equipment-{index + 1}"
        )

        # Get values from CSV
        failures = get_number(row, "Failures")
        maintenance = get_number(row, "Maintenance_Due")
        temperature = get_number(row, "Temperature")
        vibration = get_number(row, "Vibration")


        # Calculate risk score
        score = 0
        reasons = []


        # Failure condition
        if failures >= 3:

            score += 40

            reasons.append(
                "Frequent equipment failures"
            )


        # Maintenance condition
        if maintenance == 1:

            score += 25

            reasons.append(
                "Maintenance is due"
            )


        # Temperature condition
        if temperature > 80:

            score += 20

            reasons.append(
                "High operating temperature"
            )


        # Vibration condition
        if vibration > 7:

            score += 15

            reasons.append(
                "High vibration level"
            )


        # Determine risk level
        if score >= 60:

            level = "HIGH"

            action = (
                "Immediate inspection and maintenance recommended"
            )

        elif score >= 30:

            level = "MEDIUM"

            action = (
                "Schedule inspection and monitor equipment"
            )

        else:

            level = "LOW"

            action = (
                "Continue regular monitoring"
            )


        results.append({

            "equipment_id": equipment,

            "risk_score": score,

            "risk_level": level,

            "reasons": reasons,

            "recommended_action": action

        })


    # Highest risk first
    results.sort(
        key=lambda x: x["risk_score"],
        reverse=True
    )

    return results



def get_number(row, column):

    value = row.get(column, 0)

    try:

        return float(value)

    except:

        return 0