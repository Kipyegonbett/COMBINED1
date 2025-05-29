import streamlit as st
import pandas as pd
from io import BytesIO

# Define diagnosis categories and their ranges
diagnosis_ranges = {
    "Certain infectious or parasitic diseases": ("1A00", "1H0Z"),
    "Neoplasms": ("2A00", "2F9Z"),
    "Diseases of the blood or blood-forming organs": ("3A00", "3C0Z"),
    "Diseases of the immune system": ("4A00", "4B4Z"),
    "Endocrine, nutritional or metabolic diseases": ("5A00", "5D46"),
    "Mental, behavioral and neurodevelopmental disorders": ("6A00", "6E8Z"),
    "Sleep-wake disorders": ("7A00", "7B2Z"),
    "Diseases of the nervous system": ("8A00", "8E7Z"),
    "Diseases of the visual system": ("9A00", "9E1Z"),
    "Diseases of the ear or mastoid process": ("AA00", "AC0Z"),
    "Diseases of the circulatory system": ("BA00", "BE2Z"),
    "Diseases of the respiratory system": ("CA00", "CB7Z"),
    "Diseases of the digestive system": ("DA00", "DE2Z"),
    "Diseases of the skin and subcutaneous tissue": ("EA00", "EM0Z"),
    "Diseases of the musculoskeletal system or connective tissue": ("FA00", "FC0Z"),
    "Diseases of genitourinary system": ("GA00", "GC8Z"),
    "Conditions related to sexual health": ("HA00", "HA8Z"),
    "Pregnancy, childbirth or puerperium": ("JA00", "JB6Z"),
    "Certain conditions originating in perinatal period": ("KA00", "KD5Z"),
    "Developmental anomalies": ("LA00", "LD9Z"),
    "Symptoms, signs or clinical findings not elsewhere classified": ("MA00", "MH2Y"),
    "Injury, poisoning or certain consequences of external causes": ("NA00", "NF2Z"),
    "External causes of morbidity or mortality": ("PA00", "PL2Z"),
    "Factors influencing health status or contact with health services": ("QA00", "QF4Z"),
    "Codes for special purposes": ("RA00", "RA26"),
    "Supplementary chapter: Traditional medicine conditions (Module 1)": ("SA00", "ST2Z"),
    "Supplementary section for functioning assessment": ("VA00", "VC50"),
    "Extension codes": ("XA0060", "XY9U"),
}

def filter_by_diagnosis(df, start_code, end_code):
    """Filter dataset based on alphanumeric diagnosis code range."""
    df["Diagnosis"] = df["Diagnosis"].astype(str).str.strip().str.upper()
    return df[df["Diagnosis"].apply(lambda x: start_code <= x <= end_code)]

# Streamlit UI
st.title("Diagnosis Code Analysis Tool")

uploaded_file = st.file_uploader("Upload your dataset (.xlsx, .csv, .txt)", type=["xlsx", "csv", "txt"])
mode = st.radio("Select mode:", ["Filter by code range", "Analyze specific code"])

if mode == "Filter by code range":
    start_code = st.text_input("Start code (e.g., 1A00)")
    end_code = st.text_input("End code (e.g., 1H0Z)")
else:
    diagnosis_code = st.text_input("Diagnosis code (e.g., 8A68.Z)")

if st.button("Analyze"):
    if not uploaded_file:
        st.warning("Please upload a file first.")
    else:
        try:
            file_name = uploaded_file.name
            file_bytes = uploaded_file.read()

            # Read file based on extension
            if file_name.endswith(".xlsx"):
                df = pd.read_excel(BytesIO(file_bytes), dtype=str)
            elif file_name.endswith(".csv"):
                df = pd.read_csv(BytesIO(file_bytes), dtype=str)
            else:  # Assume text file
                text_content = file_bytes.decode("utf-8")
                diagnoses = [line.strip() for line in text_content.split("\n") if line.strip()]
                df = pd.DataFrame(diagnoses, columns=["Diagnosis"])

            if "Diagnosis" not in df.columns:
                st.error("No column named 'Diagnosis' found in the uploaded file.")
            else:
                df["Diagnosis"] = df["Diagnosis"].str.strip().str.upper()

                if mode == "Filter by code range":
                    if not start_code or not end_code:
                        st.warning("Please enter both start and end codes.")
                    else:
                        category_name = next((name for name, (start, end) in diagnosis_ranges.items() if start_code >= start and end_code <= end), None)
                        filtered_df = filter_by_diagnosis(df, start_code.strip().upper(), end_code.strip().upper())

                        st.write(f"📊 **Number of diagnoses in range {start_code} to {end_code}:** {len(filtered_df)}")
                        
                        if category_name:
                            st.write(f"🩺 **Category:** {category_name}")
                        else:
                            st.warning("Diagnosis code range does not match any predefined category.")

                        if not filtered_df.empty:
                            csv = filtered_df.to_csv(index=False).encode('utf-8')
                            st.download_button("Download Filtered Data", csv, f"filtered_diagnosis_{start_code}_to_{end_code}.csv", "text/csv")
                            st.dataframe(filtered_df.head())

                else:  # Analyze specific code
                    if not diagnosis_code:
                        st.warning("Please enter a diagnosis code.")
                    else:
                        code_value = diagnosis_code.strip().upper()
                        count = len(df[df["Diagnosis"].str.startswith(code_value)])
                        exact_count = len(df[df["Diagnosis"] == code_value])
                        matches = df[df["Diagnosis"].str.startswith(code_value)]

                        st.write(f"🩺 **Diagnosis Code:** {code_value}")
                        st.write(f"📊 **Total records in dataset:** {len(df)}")
                        st.write(f"🔍 **Count of diagnoses starting with '{code_value}':** {count}")
                        st.write(f"✅ **Exact matches for '{code_value}':** {exact_count}")

                        if count > 0:
                            st.write("📌 **Matching diagnoses found:**")
                            st.dataframe(matches["Diagnosis"].value_counts().reset_index().rename(columns={"index": "Diagnosis", "Diagnosis": "Count"}))

                        st.write("📊 **Top 10 most frequent diagnoses in dataset:**")
                        st.dataframe(df["Diagnosis"].value_counts().head(10).reset_index().rename(columns={"index": "Diagnosis", "Diagnosis": "Count"}))

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Ensure your file meets these requirements:\n- Contains a column named 'Diagnosis'\n- Supported formats: Excel (.xlsx), CSV (.csv), or text (.txt)\n- For text files, each line should contain one diagnosis code.")

