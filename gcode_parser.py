def parse_gcode_file(uploaded_file):
    filename = uploaded_file.name.lower()

    if filename.endswith(".bgcode"):
        return parse_bgcode_file(uploaded_file)
    else:
        return parse_text_gcode_file(uploaded_file)


def parse_text_gcode_file(uploaded_file):
    lines = uploaded_file.read().decode("utf-8", errors="ignore").splitlines()

    features = {
        "file_type": "text_gcode",
        "filename": uploaded_file.name,
        "total_lines": 0,
        "layers": 0,
        "print_moves": 0,
        "travel_moves": 0,
        "retractions": 0,
        "max_nozzle_temp": 0,
        "max_bed_temp": 0,
    }

    for line in lines:
        line = line.strip()
        features["total_lines"] += 1

        if line.startswith(";LAYER:"):
            features["layers"] += 1

        if line.startswith("G0"):
            features["travel_moves"] += 1

        if line.startswith("G1") and "E" in line:
            features["print_moves"] += 1

        if "E-" in line:
            features["retractions"] += 1

        if line.startswith("M104") or line.startswith("M109"):
            temp = extract_temperature(line)
            if temp is not None and temp > features["max_nozzle_temp"]:
                features["max_nozzle_temp"] = temp

        if line.startswith("M140") or line.startswith("M190"):
            temp = extract_temperature(line)
            if temp is not None and temp > features["max_bed_temp"]:
                features["max_bed_temp"] = temp

    return features

def parse_bgcode_file(uploaded_file):
    raw = uploaded_file.read()
    text = raw.decode("utf-8", errors="ignore")

    features = {
        "file_type": "bgcode",
        "filename": uploaded_file.name,
        "format_supported": "metadata_only",
        "producer": "Unknown",
        "produced_on": "Unknown",
        "printer_model": "Unknown",
        "filament_type": "Unknown",
        "note": "Binary G-code detected. Full motion parsing is not enabled yet.",
        "all_metadata": {}
    }

    metadata = {}

    for line in text.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            metadata[key.strip()] = value.strip()

    features["all_metadata"] = metadata

    features["producer"] = (
        metadata.get("Producer")
        or metadata.get("producer")
        or "Unknown"
    )

    features["produced_on"] = (
        metadata.get("Produced on")
        or metadata.get("produced_on")
        or "Unknown"
    )

    features["printer_model"] = (
        metadata.get("printer_model")
        or metadata.get("Printer Model")
        or metadata.get("printer")
        or "Unknown"
    )

    features["filament_type"] = (
        metadata.get("filament_type")
        or metadata.get("Filament Type")
        or "Unknown"
    )

    return features


def extract_temperature(line):
    for part in line.split():
        if part.startswith("S"):
            try:
                return float(part[1:])
            except ValueError:
                return None
    return None