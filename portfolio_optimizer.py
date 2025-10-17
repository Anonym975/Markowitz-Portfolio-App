import yfinance as yf
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from scipy.optimize import minimize
import time
import os

# Functional Paradigm: Data downloading with retry mechanism
def download_data(tickers, start_date, end_date, retries=3, delay=5):
    for _ in range(retries):
        try:
            data = yf.download(tickers=tickers, start=start_date, end=end_date)
            if not data['Adj Close'].empty:
                return data['Adj Close']
        except Exception as e:
            print(f"Download failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    print("Failed to download data. Switching to Excel backup...")
    return None

class PortfolioOptimizer:
    def __init__(self, stocks, start, end, excel_file, target_return, riskFreeRate=0.044):
        self.stocks = stocks
        self.start = start
        self.end = end
        self.excel_file = excel_file
        self.target_return = target_return
        self.riskFreeRate = riskFreeRate

        self.prices = self.basicMetrics()
        if self.prices is not None and not self.prices.empty:
            n_assets = len(self.prices.columns)
            self.weights = np.array([1.0 / n_assets] * n_assets)
        else:
            raise ValueError("Price data is empty. Cannot initialize weights.")

        self.returns = np.log(self.prices / self.prices.shift(1)).dropna()
        self.pBar = self.returns.mean()
        self.Sigma = self.returns.cov()
        self.meanReturns, self.covMatrix = self.pBar, self.Sigma

        # Optional: initialize optimized allocation with minimum risk
        self.optimized_allocation = self.allocation()

    def basicMetrics(self):
        prices = download_data(self.stocks, self.start, self.end)
        if prices is None:
            try:
                prices = pd.read_excel(self.excel_file, index_col=0, parse_dates=True)
            except FileNotFoundError:
                st.error(f"❌ Excel file '{self.excel_file}' not found. Please upload it.")
                raise
        return prices

    def getData(self):
        meanReturns = self.returns.mean()
        covMatrix = self.returns.cov()
        return meanReturns, covMatrix

    def calculate_metrics(self):
        port_variance = self.portfolio_variance(self.weights, self.Sigma)
        port_annual_ret = np.sum(self.pBar * self.weights) * 252
        port_volatility = np.sqrt(port_variance)
        sharpe_ratio = (port_annual_ret - self.riskFreeRate) / port_volatility
        return port_annual_ret, port_volatility, port_variance, sharpe_ratio

    def portfolio_variance(self, weights, Sigma):
        return np.dot(weights.T, np.dot(Sigma, weights)) * 252

    def portfolioReturn(self, weights):  
        return np.sum(self.pBar * weights) * 252

    def portfolioPerformance(self, weights):
        port_annual_ret = np.sum(self.meanReturns * weights) * 252
        port_variance = self.portfolio_variance(weights, self.Sigma)
        port_volatility = np.sqrt(port_variance)
        return port_annual_ret, port_volatility

    def riskFunction(self, w):
        return self.portfolio_variance(w, self.Sigma)

    def singleEquationSolver(self):
        # Minimize portfolio risk without target return
        Sigma_inv = np.linalg.inv(self.Sigma)
        sum_all_elements = np.sum(Sigma_inv)
        w_opt = np.sum(Sigma_inv, axis=1) / sum_all_elements
        w_opt = np.maximum(w_opt, 0)
        w_opt = w_opt / np.sum(w_opt)
        return w_opt

    def markowitz_optimal_weights_specific_return(self, U):
        # Optimize weights for specific target daily return U
        Sigma_inv = np.linalg.inv(self.Sigma)
        M = np.dot(np.dot(self.pBar.T, Sigma_inv), self.pBar)
        w_opt = np.dot(Sigma_inv, self.pBar) * (U / M)
        w_opt = np.maximum(w_opt, 0)
        return w_opt
    



    def allocation(self, method=None, U=None, money=None):
        if method is None:
            method = self.singleEquationSolver

        weights = method() if U is None else method(U)
        total_original_weight = np.sum(weights) # Calculate total of original weights

        # Note: We are no longer normalizing weights to sum to 1 here.
        # The 'Allocation (%)' will be directly based on the original weights.

        allocation_df = pd.DataFrame({
            "Original Weight": weights,
            # "Normalized Weight": normalized_weights, # <-- إلغاء هذا العمود
            "Allocation (%)": weights * 100, # <-- استخدام Original Weight مباشرةً
        }, index=self.meanReturns.index)

        # Calculate investment if money and target return are provided
        if money is not None and U is not None:
            # When sum of weights is not 1, 'money' should be distributed based on the
            # proportions of the 'Original Weight' relative to their sum.
            # However, based on your previous output, 'Investment ($)' was calculated
            # as normalized_weights * money, where normalized_weights already summed to 1.
            # If you want to use the *original* sum of weights, you need to rethink the money allocation logic.
            # For simplicity, if U is provided and money is the *total required investment*,
            # then the current calculation (normalized_weights * money) still makes sense for distribution.
            # If money is the *initial budget* and you want to proportionally allocate, it's different.

            # Let's assume 'money' passed here is the total amount that *should be* invested
            # based on the sum of original weights (e.g., investment_required from main.py)
            # In this case, Investment ($) would be Original Weight / Total Original Weight * Money
            # Or, if we keep the previous logic that 'money' passed is what *was* calculated as required,
            # then we should use the `normalized_weights` to distribute it.
            
            # Given your previous output for 'Investment ($)' which summed to '3,301.0927',
            # it implies 'money' here is the `investment_required` which is `sum(original_weights) * initial_budget_money`.
            # So, to get the correct proportion for each, we still need normalization.
            # Let's clarify this part if needed.

            # For now, if the user wants `Investment ($)` to reflect the *total money available*
            # and distribute it by these (possibly non-sum-to-1) weights, then:
            # allocated_money = (weights / total_original_weight) * money
            # But this would change the meaning of 'Investment ($)' from the previous output.

            # Let's stick to the simpler interpretation: you want to show the 'Original Weight'
            # as a percentage, and if money is provided, it's about how much of that money
            # each original weight represents, relative to the sum of original weights.

            allocated_money = (weights / total_original_weight) * money
            allocation_df["Investment ($)"] = allocated_money
        
        # Format Allocation % to show 2 decimals + "%"
        allocation_df["Allocation (%)"] = allocation_df["Allocation (%)"].map("{:.2f}%".format)

        # Add Total row
        total_data = {
            "Original Weight": weights.sum(),
            # "Normalized Weight": normalized_weights.sum(), # <-- إلغاء هذا
            "Allocation (%)": "{:.2f}%".format(total_original_weight * 100) # <-- استخدام total_original_weight
        }
        if "Investment ($)" in allocation_df.columns:
            total_data["Investment ($)"] = allocation_df["Investment ($)"].sum()
            # total_data["Investment ($)"] = total_original_weight * money # If money is the initial budget.
            # Based on your previous output, it was `3301.0927` which is `sum(normalized_weights) * original_money_budget`
            # or `sum(original_weights) * original_money_budget`.
            # If `money` passed to `allocation` is the `investment_required` then `allocation_df["Investment ($)"].sum()` is correct.

        total_df = pd.DataFrame(total_data, index=["Total"])
        allocation_df = pd.concat([allocation_df, total_df])

        return allocation_df















    # def allocation(self, method=None, U=None, money=None):
    #     if method is None:
    #         method = self.singleEquationSolver

    #     weights = method() if U is None else method(U)
    #     total_weight = np.sum(weights)

    #     # Normalize weights if using target return (to display allocation percentages)
    #     normalized_weights = weights / total_weight if U is not None  else weights

    #     allocation_df = pd.DataFrame({
    #         "Original Weight": weights,
    #         "Normalized Weight": normalized_weights,
    #         "Allocation (%)": normalized_weights * 100,
    #     }, index=self.meanReturns.index)

    #     # Calculate investment if money and target return are provided
    #     if money is not None and U is not None:
    #         allocated_money = normalized_weights * money
    #         allocation_df["Investment ($)"] = allocated_money

        
    #     # Format Allocation % to show 2 decimals + "%"
    #     allocation_df["Allocation (%)"] = allocation_df["Allocation (%)"].map("{:.2f}%".format)

    #     # Add Total row
    #     total_data = {
    #         "Original Weight": weights.sum(),
    #         "Normalized Weight": normalized_weights.sum(),
    #         "Allocation (%)": "{:.2f}%".format(normalized_weights.sum() * 100)
    #     }
    #     if "Investment ($)" in allocation_df.columns:
    #         total_data["Investment ($)"] = allocation_df["Investment ($)"].sum()
    #         # total_data["Investment ($)"] = normalized_weights.sum() * money

    #     total_df = pd.DataFrame(total_data, index=["Total"])
    #     allocation_df = pd.concat([allocation_df, total_df])

    #     return allocation_df




    