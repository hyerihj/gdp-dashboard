# streamlit_app.py — visual polish to match mock‑up
"""
Minimalist IG Post Processor – Streamlit app
===========================================
This version keeps **all of your existing logic** but tweaks the _look‑and‑feel_ so it
resembles the screenshots you shared:

*   ✨  **Centred, oversized title**
*   🧭  Collapsible **“How to Use”** section in the main column
*   Clean sidebar with numeric step headers
*   Tight top padding for a neater hero block

Save this as **`streamlit_app.py`** and run:

```bash
pip install streamlit pandas
streamlit run streamlit_app.py
```
"""

from io import StringIO
import json
import re

import pandas as pd
import streamlit as st

# ──────────────────────────────  Page set‑up  ──────────────────────────────
st.set_page_config(
    page_title="Minimalist IG Post Processor",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject a sprinkle of CSS to centre the hero title & tighten vertical spacing
st.markdown(
    """
    <style>
        /* ─── Main title ─── */
        .block-container h1:first-child {
            text-align: center;
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 1.25rem;
        }
        /* ─── Compact top padding ─── */
        .block-container {
            padding-top: 1.2rem;
        }
        /* ─── Sidebar header size ─── */
        section[data-testid="stSidebar"] h2 {
            font-size: 1.05rem;
            margin-bottom: .3rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Minimalist IG Post Processor")

# ──────────────────────────────  Default dictionary  ──────────────────────────────
DEFAULT_DICT = {
    "Fashion": ["style", "fashion", "wardrobe", "clothing", "outfit"],
    "Food": ["delicious", "food", "dinner", "lunch", "restaurant"],
    "Travel": ["travel", "trip", "vacation", "explore", "journey"],
    "Fitness": ["workout", "fitness", "exercise", "gym", "training"],
}

# ──────────────────────────────  Sidebar  ──────────────────────────────
## 1️⃣  Upload
st.sidebar.header("1️⃣  Upload your CSV")
uploaded_file = st.sidebar.file_uploader(
    "Choose an Instagram CSV file (≤200 MB)", type=["csv"], accept_multiple_files=False
)

st.sidebar.markdown("---")

## 2️⃣  Dictionary
st.sidebar.header("2️⃣  Modify keyword dictionary")

dict_input = st.sidebar.text_area(
    "Dictionary (JSON)",
    value=json.dumps(DEFAULT_DICT, indent=2),
    height=280,
)

try:
    keyword_dict = json.loads(dict_input)
    if not isinstance(keyword_dict, dict):
        raise ValueError("Dictionary root must be a JSON object (key → list).")
except (json.JSONDecodeError, ValueError) as e:
    st.sidebar.error(f"❌ {e}\nUsing default dictionary instead.")
    keyword_dict = DEFAULT_DICT

st.sidebar.markdown(
    """<small>🔧 Edit the JSON above to add/delete categories & keywords.</small>""",
    unsafe_allow_html=True,
)

# ──────────────────────────────  Helper functions  ──────────────────────────────

def classify_sentence(text: str, kw_dict: dict) -> str:
    """Return first category whose keywords appear in *text* (case‑insensitive)."""
    text_lower = text.lower()
    for cat, kws in kw_dict.items():
        if any(k.lower() in text_lower for k in kws):
            return cat
    return "Uncategorized"


def process_dataframe(df: pd.DataFrame, kw_dict: dict) -> pd.DataFrame:
    """Split captions into sentences/hashtags ➜ classify ➜ tidy DataFrame."""
    df = df.rename(columns={"shortcode": "ID", "caption": "Context"})
    rows = []
    for _, row in df.iterrows():
        # split on sentence terminators **or** look‑ahead for a hashtag
        sentences = re.split(r"(?<=[.!?])\s+|(?=#[^\s]+)", str(row["Context"]))
        for i, s in enumerate(sentences, start=1):
            clean = re.sub(r"\s+", " ", s.strip())
            if clean and not re.fullmatch(r"[.!?]+", clean):
                rows.append(
                    {
                        "ID": row["ID"],
                        "Context": row["Context"],
                        "Sentence ID": i,
                        "Statement": clean,
                        "Category": classify_sentence(clean, kw_dict),
                    }
                )
    return pd.DataFrame(rows)

# ──────────────────────────────  How‑to expander  ──────────────────────────────
with st.expander("ℹ️  How to Use", expanded=False):
    st.markdown(
        """
1. **Upload your CSV** in the sidebar. File must contain `shortcode` & `caption` columns.
2. **Edit the dictionary** (optional) – JSON keys → category names.
3. **Click _Run processor_** to explode captions into sentence‑level rows.
4. **Download the CSV** of the transformed data.

**Output columns**  
• `ID`  • `Sentence ID`  • `Context`  • `Statement`  • `Category`
        """
    )

# ──────────────────────────────  Main logic  ──────────────────────────────
if uploaded_file is None:
    st.info("👈  Start by uploading a CSV file from the sidebar.")
    st.stop()

raw_df = pd.read_csv(uploaded_file)

if not {"shortcode", "caption"}.issubset(raw_df.columns):
    st.error("CSV must contain `shortcode` and `caption` columns.")
    st.stop()

if st.sidebar.button("▶️  Run processor"):
    with st.spinner("Processing …"):
        final_df = process_dataframe(raw_df, keyword_dict)

    st.success("Processing complete!")
    st.subheader("Preview of processed data")
    st.dataframe(final_df, use_container_width=True)

    buff = StringIO()
    final_df.to_csv(buff, index=False)
    st.download_button(
        "💾  Download CSV", data=buff.getvalue(), mime="text/csv", file_name="ig_posts_classified.csv"
    )
