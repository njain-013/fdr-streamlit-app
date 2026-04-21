import streamlit as st
import pandas as pd
import re

# =====================================================
# 1. BANK DICTIONARY (ROBUST + OCR SAFE + VARIATIONS)
# =====================================================
BANK_KEYWORDS = {
    "state bank": "State Bank of India",
    "sbi": "State Bank of India",

    "hdfc": "HDFC",
    "hdfcbank": "HDFC",

    "icici": "ICICI",
    "icicibank": "ICICI",

    "axis": "Axis",
    "axisbank": "Axis",

    "punjab national": "Punjab National Bank",
    "pnb": "Punjab National Bank",

    "canara": "Canara",

    "baroda": "Bank of Baroda",

    "kotak": "Kotak Mahindra",
    "kotakmahindra": "Kotak Mahindra",

    "indusind": "IndusInd",

    "federal": "Federal",

    "yes": "Yes",

    "rbl": "RBL",

    "karnataka": "Karnataka",

    "city union": "City Union Bank",
    "cityunion": "City Union Bank",

    "union bank": "Union Bank of India",
    "unionbank": "Union Bank of India",

    "bank of india": "Bank of India"
}

# =====================================================
# 2. TEXT CLEANING (HANDLES OCR + SYMBOLS)
# =====================================================
def clean_text(text):
    text = str(text).lower()

    # remove everything except letters & numbers
    text = re.sub(r'[^a-z0-9]', ' ', text)

    # normalize spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# =====================================================
# 3. FDR EXTRACTION (SYMBOL-ROBUST)
# =====================================================
def extract_fdr(text):
    text = str(text)

    # replace all non-numeric with space
    text = re.sub(r'[^0-9]', ' ', text)

    # find digit groups (6–16 digits)
    matches = re.findall(r'\d{6,16}', text)

    return matches[0] if matches else None

# =====================================================
# 4. BANK EXTRACTION (SMART MATCH)
# =====================================================
def extract_bank(text):
    text_clean = clean_text(text)

    best_match = None
    best_score = 0

    for key, value in BANK_KEYWORDS.items():

        if key in text_clean:
            score = len(key)  # longer match preferred

            if score > best_score:
                best_score = score
                best_match = value

    return best_match

# =====================================================
# 5. STREAMLIT UI
# =====================================================
st.set_page_config(page_title="FDR Extractor", layout="wide")

st.title("🏦 FDR & Bank Extraction System")
st.write("Upload one or multiple Excel files to extract FDR numbers and bank names automatically.")

# =====================================================
# 6. MULTI FILE UPLOAD
# =====================================================
uploaded_files = st.file_uploader(
    "Upload Excel Files",
    type=["xlsx"],
    accept_multiple_files=True
)

# =====================================================
# 7. PROCESS FILES
# =====================================================
if uploaded_files:

    all_data = []

    for file in uploaded_files:

        df = pd.read_excel(file)
        col = df.columns[0]

        # apply extraction
        df["FDR_Number"] = df[col].apply(extract_fdr)
        df["Bank_Name"] = df[col].apply(extract_bank)

        df["Source_File"] = file.name  # track file origin

        all_data.append(df)

    final_df = pd.concat(all_data, ignore_index=True)

    st.success("Processing completed successfully!")

    # =====================================================
    # 8. SHOW OUTPUT
    # =====================================================
    st.subheader("Extracted Data Preview")
    st.dataframe(final_df)

    # =====================================================
    # 9. DOWNLOAD OUTPUT
    # =====================================================
    output_file = "cleaned_fdr_output.xlsx"
    final_df.to_excel(output_file, index=False)

    with open(output_file, "rb") as f:
        st.download_button(
            label="⬇ Download Cleaned File",
            data=f,
            file_name="cleaned_fdr_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.info("Please upload one or more Excel files to start processing.")