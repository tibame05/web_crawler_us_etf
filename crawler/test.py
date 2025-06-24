import os
import pandas as pd
import yfinance as yf
import re

# Output directory
output_dir = "Output"
os.makedirs(output_dir, exist_ok=True)

# Sanitize function for ticker codes
def clean_ticker(code):
    return re.sub(r'[^A-Za-z0-9.-]', '', code)

# Use the original `etf_codes` from your scraper
tickers = [clean_ticker(code) for code in etf_codes]
start_date = '2015-05-01'
end_date = pd.Timestamp.today().strftime('%Y-%m-%d')

for r in tickers:
    try:
        df = yf.download(r, start=start_date, end=end_date)
        if not df.empty and len(df) > 1:
            df = df.reset_index()
            df = df.drop(df.index[0])
            csv_name = os.path.join(output_dir, f"{r}.csv")
            df.to_csv(csv_name, encoding="utf-8", index=False)
            print(f"✅ Saved: {csv_name}")
        else:
            print(f"⚠️ Skipping {r}: No data or insufficient data.")
    except Exception as e:
        print(f"❌ Error downloading {r}: {e}")


if not df.empty and len(df) > 1:
    df = df.reset_index()
    df = df.drop(df.index[0])
    df.to_csv(csv_name, encoding="utf-8", index=False)
    print(f"✅ Saved: {csv_name}")
elif df.empty:
    print(f"⚠️ Skipping {r}: No data available (possibly delisted).")
else:
    print(f"⚠️ Skipping {r}: Not enough data to process.")