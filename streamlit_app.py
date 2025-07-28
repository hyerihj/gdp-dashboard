import streamlit as st
import pandas as pd
import re
import json
from io import StringIO

st.set_page_config(page_title="IG Post Processor", layout="wide")
st.title("Minimalist IG Post Processor")

# --- Default keyword dictionary ------------------------------------------------
DEFAULT_DICT = {
    "Fashion": ["style", "fashion", "wardrobe", "clothing", "outfit"],
    "Food": ["delicious", "food", "dinner", "lunch", "restaurant"],
    "Travel": ["travel", "trip", "vacation", "explore", "journey"],
    "Fitness": ["workout", "fitness", "exercise", "gym", "training"],
}

# --- Sidebar: File upload -------------------------------------------------------
st.sidebar.header("1️⃣  Upload your CSV")
uploaded_file = st.sidebar.file_uploader("Choose an Instagram CSV file", type=["csv"])

# --- Sidebar: Dictionary editing ----------------------------------------------
st.sidebar.header("2️⃣  Modify keyword dictionary")

dict_input = st.sidebar.text_area(
    "Dictionary (JSON)",
    value=json.dumps(DEFAULT_DICT, indent=2),
    height=300,
)

# Attempt to parse the user‑supplied dictionary
try:
    keyword_dict = json.loads(dict_input)
    if not isinstance(keyword_dict, dict):
        st.sidebar.error("Dictionary must be a JSON object with category keys; using default.")
        keyword_dict = DEFAULT_DICT
except json.JSONDecodeError as e:
    st.sidebar.error(f"JSON decode error ➜ {e}. Using default dictionary.")
    keyword_dict = DEFAULT_DICT

# --- Helper functions ----------------------------------------------------------

def classify_sentence(text: str, kw_dict: dict) -> str:
    """Classify a sentence into a category based on keyword presence."""
    text_lower = text.lower()
    for category, keywords in kw_dict.items():
        if any(k.lower() in text_lower for k in keywords):
            return category
    return "Uncategorized"


def process_dataframe(df: pd.DataFrame, kw_dict: dict) -> pd.DataFrame:
    """Split captions into sentences, classify, and return result DataFrame."""
    df = df.rename(columns={"shortcode": "ID", "caption": "Context"})
    data = []
    for _, row in df.iterrows():
        sentences = re.split(r"(?<=[.!?])\s+|(?=#[^\s]+)", str(row["Context"]))
        for i, sentence in enumerate(sentences, start=1):
            cleaned = re.sub(r"\s+", " ", sentence.strip())
            if cleaned and not re.fullmatch(r"[.!?]+", cleaned):
                data.append(
                    {
                        "ID": row["ID"],
                        "Context": row["Context"],
                        "Sentence ID": i,
                        "Statement": cleaned,
                        "Category": classify_sentence(cleaned, kw_dict),
                    }
                )
    return pd.DataFrame(data)

# --- Main processing -----------------------------------------------------------
if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)

    # Quick sanity check
    if {"shortcode", "caption"}.issubset(raw_df.columns):
        if st.sidebar.button("▶️  Run processor"):
            with st.spinner("Processing …"):
                final_df = process_dataframe(raw_df, keyword_dict)

            st.success("Processing complete!")
            st.subheader("Preview of processed data")
            st.dataframe(final_df, use_container_width=True)

            # Download button
            csv_buffer = StringIO()
            final_df.to_csv(csv_buffer, index=False)
            st.download_button(
                "💾 Download CSV",
                data=csv_buffer.getvalue(),
                mime="text/csv",
                file_name="ig_posts_classified.csv",
            )
    else:
        st.error("CSV must contain 'shortcode' and 'caption' columns.")

# --- Footer --------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.info(
    "Edit the JSON to add or remove categories and keywords.\n"
    "Each key is a category and its value is a list of keywords."
)

