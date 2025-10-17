import streamlit as st
import pandas as pd
import time


st.title("📊 Strategy Risk Reduction Report (2015–2024)")

st.markdown("""
This report demonstrates the effectiveness of our two investment strategies over time:

- **Minimum Risk Strategy**: Aims for the lowest volatility possible.
- **Target Return Strategy**: Seeks stable returns within a specific risk profile.

The following table shows how risk improved when these strategies were tested on future market conditions.
""")

data = {
    "Period": [
        "2015–2018 → 2019", "2015–2018 → 2019",
        "2015–2020 → 2021", "2015–2020 → 2021",
        "2015–2022 → 2023", "2015–2022 → 2023",
        "2015–2023 → 2024", "2015–2023 → 2024"
    ],
    "Strategy": [
        "Minimum Risk", "Target Return",
        "Minimum Risk", "Target Return",
        "Minimum Risk", "Target Return",
        "Minimum Risk", "Target Return"
    ],
    "Risk Improvement (%)": [
        round((0.0142 / 0.0136 - 1) * 100, 2),
        round((0.0035 / 0.0023 - 1) * 100, 2),
        round((0.0261 / 0.0120 - 1) * 100, 2),
        round((0.0026 / 0.0013 - 1) * 100, 2),
        round((0.0247 / 0.0117 - 1) * 100, 2),
        round((0.0117 / 0.0064 - 1) * 100, 2),
        round((0.0232 / 0.0085 - 1) * 100, 2),
        round((0.0084 / 0.0044 - 1) * 100, 2)
    ],
    "Interpretation": [
        "Slight improvement in stability", "Strong improvement in steady returns",
        "Notable improvement in risk management", "Significant increase in stability",
        "Strong improvement in performance volatility", "Good level of stability",
        "Highest improvement in portfolio stability", "Clear and effective risk reduction"
    ]
}

df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True)

st.markdown("---")
st.success("✅ These consistent improvements demonstrate the reliability and robustness of our strategies over time.")


# Effect when switching between pages
with st.spinner('Loading...'):
    time.sleep(1)  # Wait before switching

# Creating columns for buttons
col1, col2, col3 = st.columns([3, 6, 3])

# Back to Welcome Page
with col1:
    if st.button("⬅️ Back to Welcome"):
        st.switch_page("pages/wel.py")
        st.experimental_rerun()

# Go to Portfolio Page
with col3:
    if st.button("➡️ Go to About"):
        st.switch_page("pages/about.py")
        st.experimental_rerun()

# Here you can add the actual content for performance analysis.
st.title("📊 Portfolio Performance Analysis")
st.markdown("""
    ## 📉 Performance Metrics
    
    Here you can display portfolio performance, including:
    - Expected Return
    - Portfolio Risk
    - Allocation Weights with Charts

    
""")