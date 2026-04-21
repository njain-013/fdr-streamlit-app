import streamlit as st
import pandas as pd
import re
from rapidfuzz import fuzz
import matplotlib.pyplot as plt

# =====================================================
# BANK MAP
# =====================================================
BANK_KEYWORDS = {
    "sbi": "State Bank of India",
    "hdfc": "HDFC",
    "icici": "ICICI",
    "axis": "Axis Bank",
    "pnb": "Punjab National Bank",
    "union bank": "Union Bank of India",
    "unionbank": "Union Bank of India",
    "kotak": "Kotak Mahindra"
}

# =====================================================
# CLEAN TEXT (OCR FIX)
# =====================================================
def clean_text(text):
    text = str(text).lower()

    ocr_map = {"0": "o", "1": "i", "5": "s", "8": "b"}
    for k, v in ocr_map.items():
        text = text.replace(k, v)

    text = re.sub(r'[^a-z0-9]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# =====================================================
# FDR EXTRACTION
# =====================================================
def extract_fdr(text):
    text = str(text)
    text = re.sub(r'[^0-9]', ' ', text)
    matches = re.findall(r'\d{6,16}', text)
    return matches[0] if matches else None

# =====================================================
# BANK EXTRACTION (FUZZY)
# =====================================================
def extract_bank(text):
    text_clean = clean_text(text)

    best = None
    best_score = 0

    for k, v in BANK_KEYWORDS.items():
        if k in text_clean:
            return v

        score = fuzz.partial_ratio(k, text_clean)
        if score > 80 and score > best_score:
            best_score = score
            best = v

    return best

# =====================================================
# UI
# =====================================================
st.set_page_config(layout="wide")
st.title("🏦 FDR Extraction Dashboard")

uploaded_files = st.file_uploader(
    "Upload Excel Files",
    type=["xlsx"],
    accept_multiple_files=True
)

if uploaded_files:

    all_data = []

    for file in uploaded_files:
        df = pd.read_excel(file)
        df.columns = df.columns.str.strip().str.lower()

        col = df.columns[0]

        df["source_file"] = file.name
        df["fdr_number"] = df[col].apply(extract_fdr)
        df["bank_name"] = df[col].apply(extract_bank)

        all_data.append(df)

    final_df = pd.concat(all_data, ignore_index=True)

    # =================================================
    # KPIs
    # =================================================
    total_records = len(final_df)
    missing_fdr = final_df["fdr_number"].isna().sum()
    missing_bank = final_df["bank_name"].isna().sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Records", total_records)
    col2.metric("Missing FDR", missing_fdr)
    col3.metric("Missing Bank", missing_bank)

    # =================================================
    # FULL DATA
    # =================================================
    st.subheader("📊 Full Dataset")
    st.dataframe(final_df)

    # =================================================
    # BANK WISE CHART
    # =================================================
    st.subheader("🏦 Bank Distribution")

    bank_counts = final_df["bank_name"].value_counts()

    fig, ax = plt.subplots()
    bank_counts.plot(kind="bar", ax=ax)
    st.pyplot(fig)

    # =================================================
    # FILE WISE SUMMARY
    # =================================================
    st.subheader("📁 File-wise Summary")

    file_summary = final_df.groupby("source_file").size()
    st.bar_chart(file_summary)

    # =================================================
    # DOWNLOAD
    # =================================================
    output_file = "dashboard_output.xlsx"
    final_df.to_excel(output_file, index=False)

    with open(output_file, "rb") as f:
        st.download_button("⬇ Download Report", f, file_name="report.xlsx")

else:
    st.info("Upload Excel files to generate dashboard")
