def analyze_risks(features):
    warnings = []

    if features is None:
        return warnings

    file_type = features.get("file_type", "")

    if file_type == "bgcode":
        warnings.append("Binary G-code: only metadata is being analyzed right now")
        return warnings

    if features.get("max_bed_temp", 0) == 0:
        warnings.append("No bed temperature detected")

    if features.get("max_nozzle_temp", 0) > 260:
        warnings.append("Nozzle temperature is very high")

    if features.get("retractions", 0) > 3000:
        warnings.append("High number of retractions")

    if features.get("layers", 0) < 5:
        warnings.append("Very low layer count")

    if features.get("print_moves", 0) < 100:
        warnings.append("Very few print moves")

    return warnings


def calculate_risk_score(warnings):
    score = len(warnings) * 20
    if score > 100:
        score = 100
    return score