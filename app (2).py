import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from main import main

st.set_page_config(page_title="3D Print Prototype", layout="wide")

page = st.sidebar.selectbox(
    "Choose a page",
    ["Home", "Carlos Prototype", "Ammar Prototype"]
)

if page == "Home":
    st.title("3D Printing Prototype Dashboard")
    st.write("Use the sidebar to switch between prototype pages.")
    st.write("Carlos Prototype contains the 3D Print Risk Checker.")
    st.write("Ammar Prototype is a separate page for other team work.")

elif page == "Carlos Prototype":
    st.title("3D Print Risk Checker")
    st.write("Upload a G-code or BGCODE file to analyze print details and possible risks.")

    uploaded_file = st.file_uploader(
        "Upload your G-code file",
        type=["gcode", "txt", "bgcode"],
        key="carlos_upload"
    )

    if uploaded_file is not None:
        results = main(uploaded_file)

        if results is None:
            st.error("Could not parse the uploaded file.")
        elif "error" in results:
            st.error(results["error"])
        else:
            features = results["features"]
            warnings = results["warnings"]
            risk_score = results.get("risk_score", 0)

            tab1, tab2, tab3, tab4 = st.tabs(
                ["Overview", "Charts", "Warnings", "Raw Data"]
            )

            with tab1:
                st.subheader("Overview")

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("File Type", features.get("file_type", "Unknown"))

                with col2:
                    st.metric("Warnings", len(warnings))

                with col3:
                    st.metric("Risk Score", f"{risk_score}%")

                with col4:
                    if features.get("file_type") == "bgcode":
                        st.metric("Printer Model", features.get("printer_model", "Unknown"))
                    else:
                        st.metric("Layers", features.get("layers", 0))

                st.divider()

                if features.get("file_type") == "bgcode":
                    left, right = st.columns(2)

                    with left:
                        st.write(f"**Filename:** {features.get('filename', 'Unknown')}")
                        st.write(f"**Producer:** {features.get('producer', 'Unknown')}")
                        st.write(f"**Produced On:** {features.get('produced_on', 'Unknown')}")

                    with right:
                        st.write(f"**Printer Model:** {features.get('printer_model', 'Unknown')}")
                        st.write(f"**Filament Type:** {features.get('filament_type', 'Unknown')}")
                        st.write(f"**Support Level:** {features.get('format_supported', 'Unknown')}")

                    st.info(features.get("note", ""))
                else:
                    left, right = st.columns(2)

                    with left:
                        st.write(f"**Filename:** {features.get('filename', 'Unknown')}")
                        st.write(f"**Print Moves:** {features.get('print_moves', 0)}")
                        st.write(f"**Travel Moves:** {features.get('travel_moves', 0)}")
                        st.write(f"**Retractions:** {features.get('retractions', 0)}")

                    with right:
                        st.write(f"**Total Lines:** {features.get('total_lines', 0)}")
                        st.write(f"**Max Nozzle Temp:** {features.get('max_nozzle_temp', 0)} °C")
                        st.write(f"**Max Bed Temp:** {features.get('max_bed_temp', 0)} °C")
                        st.write(f"**Layers:** {features.get('layers', 0)}")

            with tab2:
                st.subheader("Charts")

                if features.get("file_type") == "bgcode":
                    meta_df = pd.DataFrame({
                        "Category": ["Warnings"],
                        "Value": [len(warnings)]
                    })

                    st.write("BGCODE files currently support metadata-only analysis.")
                    st.bar_chart(meta_df.set_index("Category"))

                else:
                    stats_df = pd.DataFrame({
                        "Category": ["Print Moves", "Travel Moves", "Retractions", "Layers"],
                        "Value": [
                            features.get("print_moves", 0),
                            features.get("travel_moves", 0),
                            features.get("retractions", 0),
                            features.get("layers", 0),
                        ]
                    })

                    temp_df = pd.DataFrame({
                        "Temperature Type": ["Nozzle Temp", "Bed Temp"],
                        "Temperature": [
                            features.get("max_nozzle_temp", 0),
                            features.get("max_bed_temp", 0),
                        ]
                    })

                    chart_col1, chart_col2 = st.columns(2)

                    with chart_col1:
                        st.write("### Print Statistics")
                        st.bar_chart(stats_df.set_index("Category"))

                    with chart_col2:
                        st.write("### Temperature Comparison")
                        st.bar_chart(temp_df.set_index("Temperature Type"))

                    st.write("### Movement Breakdown")

                    move_counts = [
                        features.get("print_moves", 0),
                        features.get("travel_moves", 0)
                    ]
                    move_labels = ["Print Moves", "Travel Moves"]

                    fig, ax = plt.subplots()
                    ax.pie(move_counts, labels=move_labels, autopct="%1.1f%%", startangle=90)
                    ax.axis("equal")
                    st.pyplot(fig)

            with tab3:
                st.subheader("Warnings")

                if risk_score >= 60:
                    st.error(f"High Risk: {risk_score}%")
                elif risk_score >= 30:
                    st.warning(f"Medium Risk: {risk_score}%")
                else:
                    st.success(f"Low Risk: {risk_score}%")

                if warnings:
                    for warning in warnings:
                        st.warning(warning)
                else:
                    st.success("No warnings detected")

            with tab4:
                st.subheader("Raw Parsed Data")
                st.json(results)

elif page == "Ammar Prototype":
    st.title("Ammar Prototype")
    st.write("This page shows the Print Risk + Cost Estimator prototype.")

    st.subheader("4. Print Risk + Cost Estimator")

    teammate_file = st.file_uploader(
        "Upload gcode, bgcode prototype file",
        type=["gcode", "txt", "bgcode"],
        key="ammar_upload"
    )

    filament_cost_per_gram = st.number_input(
        "Filament cost per gram ($)",
        min_value=0.01,
        value=0.05,
        step=0.01
    )

    estimated_weight = st.number_input(
        "Estimated print weight (grams)",
        min_value=1.0,
        value=68.0,
        step=1.0
    )

    failure_percent = st.slider(
        "Estimated chance of failure (%)",
        min_value=0,
        max_value=100,
        value=50
    )

    if teammate_file is not None:
        st.success(f"Uploaded: {teammate_file.name}")

        estimated_filament_loss = estimated_weight * filament_cost_per_gram
        estimated_cost_loss = estimated_filament_loss * (failure_percent / 100)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Failure Chance", f"{failure_percent}%")

        with col2:
            st.metric("Filament Cost if Full Print Fails", f"${estimated_filament_loss:.2f}")

        with col3:
            st.metric("Expected Cost Loss", f"${estimated_cost_loss:.2f}")

        if failure_percent >= 60:
            st.error(
                f"This print has a HIGH failure risk — you could waste about ${estimated_cost_loss:.2f} of filament."
            )
        elif failure_percent >= 30:
            st.warning(
                f"This print has a MEDIUM failure risk — you could waste about ${estimated_cost_loss:.2f} of filament."
            )
        else:
            st.success(
                f"This print has a LOW failure risk — estimated loss is about ${estimated_cost_loss:.2f}."
            )

        st.markdown("### What it tests")
        st.write("This prototype tests whether users react more when money is shown instead of only warnings.")