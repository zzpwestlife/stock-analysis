import yfinance as yf
import pandas as pd

# Define tickers and date range
tickers = ["NVDY", "NVDA"]
start_date = "2024-05-31"
end_date = "2025-02-28"

# Fetch adjusted close prices
data = yf.download(tickers, start=start_date, end=end_date, interval="1mo")["Adj Close"]

# Calculate monthly returns
monthly_returns = data.pct_change().dropna()

# Calculate cumulative returns
cumulative_returns = (1 + monthly_returns).prod() - 1

print("Monthly Returns:\n", monthly_returns)
print("\nCumulative Returns:\n", cumulative_returns)