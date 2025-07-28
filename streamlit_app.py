# streamlit_app.py — drop expander, always visible instructions
"""
📝 Text Transformation App – Streamlit
-------------------------------------
"""

import streamlit as st
import pandas as pd
import re
from io import StringIO

# ──────────────────────────────  Page set‑up  ──────────────────────────────
st.set_page_config(
    page_title="Text Transformation App",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    /* ─── Hero title ─── */
    .block-container h1:first-child {
        text-align: center;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 1.25rem;
    }
    /* ─── Compact top padding ─── */
    .block-container { padding-top: 1.2rem; }
    /* ─── Sidebar header size ─── */
    section[data-testid="stSidebar"] h2 {
        font-size: 1.05rem; margin-bottom: .3rem;
    }
</style>
    """,
    unsafe_allow_html=True,
)

st.title("📝 Text Transformation App")

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
    st.success(f"File uploaded successfully! Found {raw_df.shape[0]} rows and {raw_df.shape[1]} columns.")

    st.markdown("### 🔍 Data Preview")
    st.dataframe(raw_df)

    st.markdown("### 📊 Column Information")
    column_info = pd.DataFrame({
        "Column": raw_df.columns,
        "Type": [raw_df[col].dtype for col in raw_df.columns],
        "Non-null Count": [raw_df[col].count() for col in raw_df.columns],
        "Sample Value": [raw_df[col].dropna().iloc[0] if not raw_df[col].dropna().empty else "" for col in raw_df.columns],
    })
    st.dataframe(column_info)

    id_col = st.selectbox("Select the ID column (e.g., shortcode)", raw_df.columns)
    context_col = st.selectbox("Select the Context column (e.g., caption)", raw_df.columns)
    include_hashtags = st.checkbox("Include hashtags as separate sentences", value=True)

    raw_df = raw_df.rename(columns={id_col: "ID", context_col: "Context"})

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

    st.header("📊 Preview & Download")
    st.markdown("### Preview of Processed Data")
    st.dataframe(final_df.head())

    csv = final_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Processed CSV",
        data=csv,
        file_name="ig_posts_transformed_output.csv",
        mime='text/csv'
    )
