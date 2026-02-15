import streamlit as st
import pandas as pd
import requests
import io
import os
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Set page title
st.set_page_config(page_title="Batch Prediction Service", layout="wide")

st.title("Batch Prediction Service")
st.sidebar.info(f"App Version: 1.0.0\nStreamlit: {st.__version__}")

# File uploader
uploaded_file = st.file_uploader("Upload CSV file for prediction", type=["csv"])

if uploaded_file is not None:
    # Display the uploaded file
    st.subheader("Uploaded Data")
    try:
        df = pd.read_csv(uploaded_file)
        
        # --- FIX: Ensure numeric types for critical columns ---
        cols_to_numeric = ['total_area', 'build_year', 'living_area', 'kitchen_area', 'rooms']
        for col in cols_to_numeric:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        st.dataframe(df.head())
        
        # Reset file pointer for request
        uploaded_file.seek(0)
        
        # --- Data Quality Check / Drift Detection (Run Immediately) ---
        st.markdown("### 🔍 Data Quality Check")

        # 1. Define Baseline
        AVG_AREA = 55.0
        MAX_AREA = 120.0
        MIN_YEAR = 1950

        # 2. Calculate Drift Metrics
        total_rows = len(df)
        outliers = df[df['total_area'] > MAX_AREA]
        outlier_ratio = len(outliers) / total_rows
        
        strange_years = df[df['build_year'] < MIN_YEAR]
        strange_year_ratio = len(strange_years) / total_rows
        
        # --- Critical Logic Checks ---
        negative_areas = df[ (df['total_area'] <= 0) | (df['living_area'] <= 0) | (df['kitchen_area'] <= 0) ]
        future_years = df[df['build_year'] > 2030]
        negative_rooms = df[df['rooms'] < 0]
        
        critical_errors = len(negative_areas) + len(future_years) + len(negative_rooms)

        # 3. Traffic Light UI
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Rows Processed", total_rows)
            st.metric("Outlier Ratio (>120m²)", f"{outlier_ratio:.1%}")

        with col2:
            if critical_errors > 0:
                    st.error(f"⛔ CRITICAL METADATA ERRORS: Found {critical_errors} rows with impossible values (negative area, future year, etc.).")
            elif outlier_ratio > 0.10:
                st.error("⚠️ High Data Drift Detected! This batch contains unusually large apartments. Predictions may be unreliable.")
            elif outlier_ratio > 0:
                st.warning("⚠️ Some outliers detected.")
            else:
                st.success("✅ Data looks consistent with training distribution.")

        if len(negative_areas) > 0:
            st.write("❌ **Negative Areas detected:**", negative_areas.index.tolist())
        if len(future_years) > 0:
                st.write("❌ **Future Building Years detected:**", future_years.index.tolist())
        
        if strange_year_ratio > 0:
            st.warning(f"⚠️ Found {len(strange_years)} rows with build_year < 1950. Please verify data.")

        # 4. Visual Proof (Simple Distribution)
        st.markdown("### 📊 Data Distribution (Total Area 0-200m²)")
        
        try:
            # Simple Streamlit Native Chart (Robust)
            # Create a histogram using numpy
            plot_vals = df['total_area'].dropna()
            # Filter for sane visualization range
            plot_vals = plot_vals[plot_vals <= 200]
            
            if not plot_vals.empty:
                hist_values, bin_edges = np.histogram(plot_vals, bins=20, range=(0, 200))
                
                # Create a dataframe for the chart
                chart_data = pd.DataFrame({
                    "Apartment Count": hist_values,
                    "Area Range (m²)": [f"{int(e)}-{int(bin_edges[i+1])}" for i, e in enumerate(bin_edges[:-1])]
                }).set_index("Area Range (m²)")
                
                st.bar_chart(chart_data)
            else:
                st.warning("No data points found in range 0-200m²")
                
        except Exception as e:
            st.warning(f"Could not render chart: {e}")

        if st.button("Predict"):

            # --- End Data Quality Check ---

            with st.spinner("Processing..."):
                try:
                    # Prepare the file for the request
                    files = {"file": (uploaded_file.name, uploaded_file, "text/csv")}
                    
                    # Get backend URL from environment (default to localhost)
                    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8081")
                    response = requests.post(f"{BACKEND_URL}/predict_batch", files=files)
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        
                        # Check if backend returned an error dict despite 200 OK
                        if isinstance(response_data, dict) and "error" in response_data:
                            st.error(f"Backend Error: {response_data['error']}")
                        else:
                            try:
                                result_df = pd.DataFrame(response_data)
                                
                                st.success("Prediction successful!")
                                st.subheader("Results")
                                st.dataframe(result_df)
                                
                                # Convert DataFrame to CSV for download
                                csv = result_df.to_csv(index=False).encode('utf-8')
                                
                                st.download_button(
                                    label="Download Predictions as CSV",
                                    data=csv,
                                    file_name="predictions.csv",
                                    mime="text/csv",
                                )
                            except ValueError as e:
                                st.error(f"Failed to parse response into DataFrame. Error: {e}")
                                with st.expander("Debug Raw Response"):
                                    st.write(response_data)
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                     st.error(f"Connection error: {e}")
            
    except Exception as e:
        st.error(f"Error reading file: {e}")
