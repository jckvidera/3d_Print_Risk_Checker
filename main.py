from gcode_parser import parse_gcode_file
from risk_checks import analyze_risks, calculate_risk_score


def main(uploaded_file):
    try:
        if uploaded_file is None:
            return {"error": "No file uploaded"}

        features = parse_gcode_file(uploaded_file)

        if features is None:
            return {"error": "parse_gcode_file returned None"}

        warnings = analyze_risks(features)
        risk_score = calculate_risk_score(warnings)

        return {
            "features": features,
            "warnings": warnings,
            "risk_score": risk_score,
        }

    except Exception as e:
        return {"error": str(e)}
