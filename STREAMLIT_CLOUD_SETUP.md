# 🚀 Streamlit Cloud Setup Guide

## 📋 **For Your Published Streamlit App**

Since your app is published on Streamlit Cloud, you need to configure the secrets through the Streamlit Cloud interface instead of using a `.env` file.

## 🔧 **Step 1: Access Streamlit Cloud Secrets**

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in to your account
3. Find your trading bot app
4. Click on the **"Settings"** or **"Manage app"** button
5. Look for **"Secrets"** section

## 🔑 **Step 2: Add Your API Credentials**

Copy and paste this configuration into the secrets section:

```toml
[broker]
BROKER = "alpaca"

[oanda]
OANDA_ACCESS_TOKEN = "your_oanda_access_token_here"
OANDA_ACCOUNT_ID = "your_oanda_account_id_here"
OANDA_ENVIRONMENT = "practice"

[ccxt]
CCXT_EXCHANGE = "binance"
CCXT_API_KEY = "your_ccxt_api_key_here"
CCXT_SECRET = "your_ccxt_secret_here"
CCXT_SANDBOX = true

[alpaca]
ALPACA_API_KEY = "PKFXJ6MZQAJLCXZUXRJQ"
ALPACA_SECRET_KEY = "tLzA3QOUJcAGuDGdKIBcDmSQhNc37s46UryPcAFl"
ALPACA_BASE_URL = "https://paper-api.alpaca.markets"
ALPACA_PAPER = true

[trading]
INSTRUMENT = "EUR_USD"
GRANULARITY = "M1"
RISK_PER_TRADE = 0.005
MAX_DAILY_DRAWDOWN = 0.02
UNITS_CAP = 20000

[strategy]
SLOW_SMA = 50
FAST_SMA = 20
ATR_WINDOW = 14
ATR_MULTIPLIER = 2.0
```

## ⚠️ **Important Security Notes:**

- **Replace placeholder values** with your real API credentials
- **Never commit real API keys** to GitHub
- **Use paper trading credentials** for testing
- **Keep your secrets secure** - only you can see them

## 🔄 **Step 3: Update Your App Code**

I've created a new configuration system that works with both local `.env` files and Streamlit secrets:

1. **For Local Development**: Uses `.env` file (as before)
2. **For Streamlit Cloud**: Uses secrets management

## 🚀 **Step 4: Deploy the Updated App**

1. **Commit the new files** to your GitHub repository
2. **Streamlit Cloud will automatically redeploy** your app
3. **Your app will now read credentials** from the secrets you configured

## 🎯 **What This Fixes:**

- ✅ **Credentials will be recognized** in your published app
- ✅ **All 3 brokers will work** (OANDA, CCXT, Alpaca)
- ✅ **Secure credential storage** through Streamlit Cloud
- ✅ **Works both locally and in production**

## 🔍 **Testing Your Setup:**

After adding the secrets:

1. **Visit your published Streamlit app**
2. **Go to the Home tab**
3. **Select a broker** (e.g., Alpaca)
4. **You should see** "✅ [Broker] credentials configured"
5. **Click "Connect to Broker"** to test the connection

## 🆘 **Need Help?**

- Check the [Streamlit Cloud documentation](https://docs.streamlit.io/streamlit-community-cloud)
- Make sure your secrets are properly formatted (TOML format)
- Verify your API credentials are correct and active

Your trading bot will now work perfectly on Streamlit Cloud! 🎉
