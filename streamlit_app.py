# ig_post_preprocessor.py — polished Streamlit layout with visible instructions
"""
📸 IG Post Preprocessor – Streamlit
----------------------------------
This version features:

* **Always visible** step-by-step instructions
* Cleaner layout with emojis and markdown formatting
* No hidden UI elements for a smoother experience
"""

import streamlit as st
import pandas as pd
import re
from io import StringIO

# ──────────────────────────────  Page Set-up  ──────────────────────────────
st.set_page_config(
    page_title="IG Post Preprocessor",
    page_icon="📸",
    layout="centered",
)

st.markdown(
    """
<style>
    .block-container h1:first-child {
        text-align: center;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 1.25rem;
    }
    .block-container { padding-top: 1.2rem; }
</style>
    """,
    unsafe_allow_html=True,
)

st.title("📸 IG Post Preprocessor")

# ──────────────────────────────  How to Use  ──────────────────────────────
st.markdown(
    """
### How to Use
1. **Upload your CSV file** containing Instagram post data  
2. **Select ID Column** – the unique identifier for each post (e.g., shortcode)  
3. **Select Context Column** – the text/caption content to process  
4. **Configure Options** – Choose whether to include hashtags as separate sentences  
5. **Click to Process** – The app will split text accordingly  
6. **Preview and Download** the processed result as a new CSV file
    """
)

# ──────────────────────────────  Step 1: Upload CSV File  ──────────────────────────────
st.header("Step 1: 📂 Upload Your Dataset")
uploaded_file = st.file_uploader("Upload a CSV file with IG post data", type="csv")

if uploaded_file:
    raw_df = pd.read_csv(uploaded_file)
    st.success("File uploaded successfully!")

    st.markdown("### 🔍 Available Columns")
    st.write(raw_df.columns.tolist())

    # ──────────────────────────────  Step 2: Select Columns  ──────────────────────────────
    st.header("Step 2: 🔧 Select Relevant Columns")
    id_col = st.selectbox("Select the ID column (e.g., shortcode)", raw_df.columns)
    context_col = st.selectbox("Select the Context column (e.g., caption)", raw_df.columns)

    raw_df = raw_df.rename(columns={id_col: "ID", context_col: "Context"})

    # ──────────────────────────────  Step 3: Configure Options  ──────────────────────────────
    st.header("Step 3: 🛠️ Configure Processing Options")
    include_hashtags = st.checkbox("Include hashtags as separate sentences", value=True)

    # ──────────────────────────────  Step 4: Process Data  ──────────────────────────────
    st.header("Step 4: ⚙️ Process Captions")
    data = []
    for _, row in raw_df.iterrows():
        pattern = r'(?<=[.!?])\s+'
        if include_hashtags:
            pattern += r'|(?=#[^\s]+)'
        sentences = re.split(pattern, str(row["Context"]))
        for i, sentence in enumerate(sentences):
            cleaned = re.sub(r'\s+', ' ', sentence.strip())
            if cleaned and not re.fullmatch(r'[.!?]+', cleaned):
                data.append({
                    "ID": row["ID"],
                    "Statement": cleaned,
                    "Sentence ID": i
                })

    final_df = pd.DataFrame(data)

    # ──────────────────────────────  Step 5: Preview and Download  ──────────────────────────────
    st.header("Step 5: 📊 Preview & Download")
    st.markdown("### Preview of Processed Data")
    st.dataframe(final_df.head())

    csv = final_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Processed CSV",
        data=csv,
        file_name="ig_posts_transformed_output.csv",
        mime='text/csv'
    )
