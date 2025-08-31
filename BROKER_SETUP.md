# Broker Setup Guide

This guide will help you connect to all three supported brokers: OANDA (Forex), CCXT (Crypto), and Alpaca (Stocks).

## 🌍 OANDA (Forex Trading)

### 1. Create OANDA Account
1. Go to [OANDA Demo Account](https://www.oanda.com/demo-account/)
2. Sign up for a free demo account
3. Verify your email address

### 2. Get API Credentials
1. Log into your OANDA account
2. Go to **Manage API Access** in your account settings
3. Click **Generate API Token**
4. Copy your **Access Token** and **Account ID**

### 3. Configure .env File
Add these lines to your `.env` file:
```env
BROKER=oanda
OANDA_ACCESS_TOKEN=your_access_token_here
OANDA_ACCOUNT_ID=your_account_id_here
OANDA_ENVIRONMENT=practice
```

### 4. Test Connection
- Launch the dashboard: `streamlit run dashboard.py`
- Go to Home tab
- Select "OANDA (Forex)" from broker dropdown
- Choose your currency pair (e.g., EUR_USD, GBP_USD)
- Click "Connect to Broker"

---

## ₿ CCXT (Crypto Trading)

### 1. Choose Exchange
Popular exchanges supported by CCXT:
- **Binance** (recommended for beginners)
- **Coinbase Pro**
- **Kraken**
- **KuCoin**

### 2. Create Exchange Account
1. Go to your chosen exchange website
2. Sign up and complete KYC verification
3. Enable API access in account settings

### 3. Create API Keys
1. Go to **API Management** in your exchange account
2. Create new API key
3. **Important**: Enable only "Spot Trading" permissions
4. **Never** enable "Withdraw" permissions for security
5. Copy your **API Key** and **Secret Key**

### 4. Configure .env File
Add these lines to your `.env` file:
```env
BROKER=ccxt
CCXT_EXCHANGE=binance
CCXT_API_KEY=your_api_key_here
CCXT_SECRET=your_secret_key_here
CCXT_SANDBOX=true
```

### 5. Test Connection
- Launch the dashboard: `streamlit run dashboard.py`
- Go to Home tab
- Select "CCXT (Crypto)" from broker dropdown
- Choose your crypto pair (e.g., BTC/USDT, ETH/USDT)
- Click "Connect to Broker"

---

## 📈 Alpaca (Stock Trading)

### 1. Create Alpaca Account
1. Go to [Alpaca Markets](https://alpaca.markets/)
2. Sign up for a free account
3. Complete account verification

### 2. Get API Credentials
1. Log into your Alpaca account
2. Go to **Paper Trading** section
3. Click **Generate API Key**
4. Copy your **API Key** and **Secret Key**

### 3. Configure .env File
Add these lines to your `.env` file:
```env
BROKER=alpaca
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
ALPACA_PAPER=true
```

### 4. Test Connection
- Launch the dashboard: `streamlit run dashboard.py`
- Go to Home tab
- Select "Alpaca (Stocks)" from broker dropdown
- Choose your stock symbol (e.g., AAPL, MSFT, TSLA)
- Click "Connect to Broker"

---

## 🔧 Complete .env Example

Here's a complete `.env` file example with all brokers configured:

```env
# Broker Selection (choose one)
BROKER=oanda

# OANDA Settings
OANDA_API_URL=https://api-fxpractice.oanda.com
OANDA_STREAM_URL=https://stream-fxpractice.oanda.com
OANDA_ACCESS_TOKEN=your_oanda_token_here
OANDA_ACCOUNT_ID=your_oanda_account_id_here
OANDA_ENVIRONMENT=practice

# CCXT Settings
CCXT_EXCHANGE=binance
CCXT_API_KEY=your_binance_api_key_here
CCXT_SECRET=your_binance_secret_here
CCXT_SANDBOX=true

# Alpaca Settings
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets
ALPACA_PAPER=true

# Trading Settings
INSTRUMENT=EUR_USD
GRANULARITY=M1
RISK_PER_TRADE=0.005
MAX_DAILY_DRAWDOWN=0.02
UNITS_CAP=20000

# Strategy Parameters
SLOW_SMA=50
FAST_SMA=20
ATR_WINDOW=14
ATR_MULTIPLIER=2.0
```

---

## 🚀 Quick Start Checklist

### For Forex (OANDA):
- [ ] Create OANDA demo account
- [ ] Get API token and account ID
- [ ] Add credentials to `.env`
- [ ] Set `BROKER=oanda`
- [ ] Test connection in dashboard

### For Crypto (CCXT):
- [ ] Create exchange account (e.g., Binance)
- [ ] Generate API keys (spot trading only)
- [ ] Add credentials to `.env`
- [ ] Set `BROKER=ccxt`
- [ ] Test connection in dashboard

### For Stocks (Alpaca):
- [ ] Create Alpaca account
- [ ] Generate paper trading API keys
- [ ] Add credentials to `.env`
- [ ] Set `BROKER=alpaca`
- [ ] Test connection in dashboard

---

## 🔒 Security Best Practices

1. **Never share your API keys**
2. **Use paper trading/sandbox first**
3. **Limit API permissions** (trading only, no withdrawals)
4. **Use environment variables** (never hardcode keys)
5. **Regularly rotate API keys**
6. **Monitor your accounts** for unusual activity

---

## 🆘 Troubleshooting

### Connection Issues:
- Check your internet connection
- Verify API credentials are correct
- Ensure API keys have proper permissions
- Check if exchange is under maintenance

### Common Errors:
- **"Invalid API key"**: Check your credentials
- **"Insufficient permissions"**: Enable trading permissions
- **"Rate limit exceeded"**: Wait a few minutes and try again
- **"Account not found"**: Verify account ID/credentials

### Getting Help:
- Check the dashboard logs tab for detailed error messages
- Review broker-specific documentation
- Test with paper trading first
- Start with small amounts

---

## 📞 Support Links

- **OANDA**: [Support Center](https://www.oanda.com/support/)
- **Binance**: [Support Center](https://www.binance.com/en/support)
- **Alpaca**: [Support Center](https://alpaca.markets/support/)

Happy Trading! 🚀
