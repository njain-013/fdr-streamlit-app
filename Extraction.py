import streamlit as st
import pandas as pd
import re

# -------------------------------
# BANK MAP (CLEAN OUTPUT)
# -------------------------------
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
    "city union": "City Union",
    "union bank": "Union Bank of India",
    "bank of india": "Bank of India"
}

# -------------------------------
# CLEAN TEXT
# -------------------------------
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'[=|/_\-]', ' ', text)
    text = text.replace("0", "o")
    text = text.replace("1", "i")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# -------------------------------
# FDR EXTRACTION
# -------------------------------
def extract_fdr(text):
    match = re.findall(r'\d{6,12}', str(text))
    return match[0] if match else None

# -------------------------------
# BANK EXTRACTION
# -------------------------------
def extract_bank(text):
    text_clean = clean_text(text)

    best_match = None
    best_score = 0

    for key, value in BANK_KEYWORDS.items():
        pattern = r'\b' + re.escape(key) + r'\b'

        if re.search(pattern, text_clean):
            score = len(key)

            if score > best_score:
                best_score = score
                best_match = value

    return best_match

# -------------------------------
# STREAMLIT UI
# -------------------------------
st.title("🏦 FDR & Bank Extraction Automation Tool")

st.write("Upload Excel file and get cleaned output instantly.")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:

    df = pd.read_excel(uploaded_file)
    col = df.columns[0]

    st.write("Preview of uploaded data:")
    st.dataframe(df.head())

    # -------------------------------
    # PROCESSING
    # -------------------------------
    df["FDR_Number"] = df[col].apply(extract_fdr)
    df["Bank_Name"] = df[col].apply(extract_bank)

    st.success("Processing completed!")

    st.write("Preview of extracted data:")
    st.dataframe(df.head())

    # -------------------------------
    # DOWNLOAD OUTPUT
    # -------------------------------
    output_file = "cleaned_fdr_output.xlsx"
    df.to_excel(output_file, index=False)

    with open(output_file, "rb") as f:
        st.download_button(
            label="⬇ Download Output File",
            data=f,
            file_name="cleaned_fdr_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )