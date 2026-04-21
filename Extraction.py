import streamlit as st
import pandas as pd
import re
from rapidfuzz import fuzz

# =====================================================
# 1. BANK DICTIONARY (CANONICAL OUTPUT)
# =====================================================
BANK_KEYWORDS = {
    "sbi": "State Bank of India",
    "state bank": "State Bank of India",

    "hdfc": "HDFC",
    "icici": "ICICI",
    "axis": "Axis",

    "pnb": "Punjab National Bank",
    "punjab national": "Punjab National Bank",

    "canara": "Canara",
    "baroda": "Bank of Baroda",

    "kotak": "Kotak Mahindra",
    "indusind": "IndusInd",
    "federal": "Federal",
    "yes": "Yes",
    "rbl": "RBL",

    "karnataka": "Karnataka",
    "city union": "City Union Bank",
    "union bank": "Union Bank of India",
    "unionbank": "Union Bank of India",

    "bank of india": "Bank of India"
}

# =====================================================
# 2. OCR + CLEANING FUNCTION (ROBUST)
# =====================================================
def clean_text(text):
    text = str(text).lower()

    # OCR corrections (very important)
    ocr_map = {
        "0": "o",
        "1": "i",
        "5": "s",
        "8": "b"
    }

    for k, v in ocr_map.items():
        text = text.replace(k, v)

    # remove symbols
    text = re.sub(r'[^a-z0-9]', ' ', text)

    # normalize spaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# =====================================================
# 3. FDR EXTRACTION (SYMBOL ROBUST)
# =====================================================
def extract_fdr(text):
    text = str(text)

    # convert everything except digits into space
    text = re.sub(r'[^0-9]', ' ', text)

    # extract long digit groups
    matches = re.findall(r'\d{6,16}', text)

    return matches[0] if matches else None

# =====================================================
# 4. BANK DETECTION (EXACT + FUZZY MATCH)
# =====================================================
def extract_bank(text):
    text_clean = clean_text(text)

    best_match = None
    best_score = 0

    for key, value in BANK_KEYWORDS.items():

        # 1. direct match (fast path)
        if key in text_clean:
            return value

        # 2. fuzzy match (OCR + typo handling)
        score = fuzz.partial_ratio(key, text_clean)

        if score > best_score and score > 80:
            best_score = score
            best_match = value

    return best_match

# =====================================================
# 5. STREAMLIT UI
# =====================================================
st.set_page_config(page_title="FDR Extraction System", layout="wide")

st.title("🏦 FDR + Bank OCR Extraction System")

st.write("Upload multiple Excel files and get cleaned structured output instantly.")

# =====================================================
# 6. MULTI FILE UPLOAD
# =====================================================
uploaded_files = st.file_uploader(
    "Upload Excel Files",
    type=["xlsx"],
    accept_multiple_files=True
)

# =====================================================
# 7. PROCESSING LOGIC
# =====================================================
if uploaded_files:

    all_data = []

    for file in uploaded_files:

        df = pd.read_excel(file)

        # clean column names
        df.columns = df.columns.str.strip().str.lower()

        # assume first column is input text
        col = df.columns[0]

        # extraction
        df["fdr_number"] = df[col].apply(extract_fdr)
        df["bank_name"] = df[col].apply(extract_bank)

        df["source_file"] = file.name

        # keep only required columns
        df = df[["fdr_number", "bank_name", "source_file"]]

        all_data.append(df)

    # merge all files properly
    final_df = pd.concat(all_data, ignore_index=True)

    st.success("Processing completed successfully!")

    # =====================================================
    # 8. SHOW OUTPUT
    # =====================================================
    st.subheader("📊 Extracted Data Preview")
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
    st.info("Upload one or more Excel files to start processing.")