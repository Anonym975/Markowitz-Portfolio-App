
import streamlit as st
import plotly.express as px
import pandas as pd
import streamlit_shadcn_ui as ui
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize

import time 
import warnings

from PIL import Image
from portfolio_optimizer import PortfolioOptimizer


def main():
    st.markdown("""
    <style>
    @keyframes wave {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-10px); }
    }
    .wave-text {
        text-align: center;
        font-size: 34px;
        font-weight: bold;
        color: #0072ff;
        animation: wave 2s infinite;
    }
    </style>
    <div class="wave-text">📈 Smart Investing Starts Here</div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### Input Parameters")
        with st.form("portfolio_form"):
            money = st.number_input(
                "💰 Enter how much you will invest ($)", 
                min_value=100.0, 
                step=100.0, 
                value=10000.0, 
                format="%.2f",
                help="Total capital you want to allocate"
            )

            UserReturn = st.number_input(
                "📊 Target Annual Return (%)",
                min_value=0.1,
                max_value=30.0,
                step=0.5,
                value=7.0,
                format="%.2f",
                help="Annual return you aim to achieve"
            )

            calculate = st.form_submit_button("🚀 Calculate")

    if calculate:
        with st.spinner("Buckle Up! Financial Wizardry in Progress...."):
            try:
                optimizer = PortfolioOptimizer(
                    ['AAPL', 'JNJ', 'PG', 'JPM', 'XOM', 'AMZN', 'KO', 'MSFT', 'GOLD', 'CVX'],
                    '2015-01-01',
                    '2023-12-30',
                    "stock_data.xlsx",
                    UserReturn,
                    0.044,
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")
                return

        with st.container(border=True):
            main_tab1, main_tab2 = st.tabs(["Strategy: Minimum Risk", "Strategy: Target Return"])

            # ---- Minimum Risk ----
            with main_tab1:
                sub_tab1, sub_tab2 = st.tabs(["Summary", "Distribution"])
                with sub_tab1:
                    st.markdown("#### Optimization Portfolio with Minimum Risk")
                    w_opt_min = optimizer.singleEquationSolver()
                    risk_min = optimizer.riskFunction(w_opt_min)
                    return_min = optimizer.portfolioReturn(w_opt_min)

                    st.markdown(f"**Expected Annual Return**: {return_min:.2%}")
                    st.markdown(f"**Portfolio Risk**: {risk_min:.2%}")
                    st.caption("Note: This strategy does not require a target return. The portfolio is optimized to minimize risk, and the resulting return is a byproduct of this optimization.")

                with sub_tab2:
                    allocations = optimizer.allocation()
                    allocations["Tickers"] = allocations.index

                    # لا نحتاج لتحويل هنا إذا كان "Allocation (%)" بالفعل بنسبته الصحيحة من الأصل
                    # allocations["Allocation (%)"] = (
                    # allocations["Allocation (%)"]
                    # .astype(str)
                    # .str.replace('%', '', regex=False)
                    # .astype(float)
                    # )

                    st.table(allocations)

                    # --- تعديل Pie Chart إلى Bar Chart للـ Minimum Risk ---
                    bar_data = allocations[allocations["Allocation (%)"] != "0.00%"].copy() # استخدم copy() لتجنب SettingWithCopyWarning
                    bar_data["Allocation (%) Numeric"] = bar_data["Allocation (%)"].astype(str).str.replace('%', '', regex=False).astype(float)

                    fig_bar_min_risk = px.bar(
                        bar_data, 
                        x="Tickers", 
                        y="Allocation (%) Numeric", 
                        title="Asset Allocation (Minimum Risk)",
                        labels={"Allocation (%) Numeric": "Allocation (%)"}
                    )
                    fig_bar_min_risk.update_layout(height=400, margin=dict(t=50, b=0, l=0, r=0))
                    st.plotly_chart(fig_bar_min_risk, use_container_width=True)
                    
                    

            # ---- Target Return ----
            with main_tab2:
                sub_tab3, sub_tab4 = st.tabs(["Summary", "Distribution"])
                with sub_tab3:
                    st.markdown("#### Optimization Portfolio with Target Return")
                    daily_target_return = (1 + UserReturn / 100) ** (1/252) - 1
                    w_opt_target = optimizer.markowitz_optimal_weights_specific_return(daily_target_return)
                    risk_target = optimizer.riskFunction(w_opt_target)
                    return_target = optimizer.portfolioReturn(w_opt_target)

                    st.markdown(f"**Expected Annual Return**: {return_target:.2%}")
                    st.markdown(f"**Portfolio Risk**: {risk_target:.4%}")
                    st.markdown(f"**Sum of Weights**: {np.sum(w_opt_target):.4f}")

                    investment_required = np.sum(w_opt_target) * money
                    st.markdown(f"**To achieve your target return of {UserReturn:.2f}%, you need to invest:** ${investment_required:.2f}")
                    st.caption("Note: The sum of weights exceeds 1 because the optimizer adjusts allocations to meet your return target.")

                with sub_tab4:
                    allocations_target = optimizer.allocation(
                        method=optimizer.markowitz_optimal_weights_specific_return,
                        U=daily_target_return,
                        money=investment_required
                    )
                    allocations_target["Tickers"] = allocations_target.index
                    st.table(allocations_target)

                    # --- تعديل Pie Chart إلى Bar Chart للـ Target Return ---
                    # تأكد أنك بتستخدم عمود Investment ($) أو Original Weight هنا
                    bar_data_target = allocations_target[allocations_target["Allocation (%)"] != "0.00%"].copy()
                    bar_data_target["Investment ($) Numeric"] = bar_data_target["Investment ($)"] # Assuming it's already numeric or will be

                    fig_bar_target_return = px.bar(
                        bar_data_target, 
                        x="Tickers", 
                        y="Investment ($) Numeric", # أو "Original Weight" لو عايز تعرضها كنسبة
                        title="Asset Allocation (Target Return) by Investment",
                        labels={"Investment ($) Numeric": "Investment ($)"}
                    )
                    fig_bar_target_return.update_layout(height=400, margin=dict(t=50, b=0, l=0, r=0))
                    st.plotly_chart(fig_bar_target_return, use_container_width=True)

    # Navigation Buttons
    time.sleep(1)
    col1, col2, col3 = st.columns([3, 4, 2])
    with col1:
        if st.button("⬅️ Back to Welcome"):
            st.switch_page("pages/wel.py")
    with col3:
        if st.button("➡️ Go to Performance"):
            st.switch_page("pages/performance.py")

main()


