# 🔧 .env File Setup Guide

## ✅ Your .env file has been created!

I've created a comprehensive `.env` file for you with all broker configurations. Here's what you need to do:

## 🚀 Quick Setup Steps

### 1. **Choose Your Broker**
Edit the `.env` file and set your preferred broker:
```env
BROKER=oanda    # For Forex trading
BROKER=ccxt     # For Crypto trading  
BROKER=alpaca   # For Stock trading
```

### 2. **Get API Credentials**

#### 🌍 **OANDA (Forex) - RECOMMENDED FOR BEGINNERS**
1. Go to [OANDA Demo Account](https://www.oanda.com/demo-account/)
2. Sign up for free
3. Get your **Access Token** and **Account ID**
4. Replace in `.env`:
   ```env
   OANDA_ACCESS_TOKEN=your_actual_token_here
   OANDA_ACCOUNT_ID=your_actual_account_id_here
   ```

#### ₿ **CCXT (Crypto)**
1. Choose an exchange (Binance, Coinbase, etc.)
2. Create account and enable API access
3. Generate API keys (spot trading only)
4. Replace in `.env`:
   ```env
   CCXT_EXCHANGE=binance
   CCXT_API_KEY=your_actual_api_key_here
   CCXT_SECRET=your_actual_secret_here
   ```

#### 📈 **Alpaca (Stocks)**
1. Go to [Alpaca Markets](https://alpaca.markets/)
2. Sign up for paper trading account
3. Generate API keys
4. Replace in `.env`:
   ```env
   ALPACA_API_KEY=your_actual_api_key_here
   ALPACA_SECRET_KEY=your_actual_secret_key_here
   ```

### 3. **Start Trading**
```bash
streamlit run dashboard.py
```

## 🎯 Trading Mode Toggle

**NEW FEATURE**: You can now switch between Paper and Live trading with one click!

- **Paper Trading**: Safe testing with fake money
- **Live Trading**: Real money trading (be careful!)

The dashboard will automatically update your `.env` file when you switch modes.

## ⚙️ Configuration Options

### Trading Settings
- `INSTRUMENT`: What to trade (EUR_USD, BTC/USDT, AAPL)
- `RISK_PER_TRADE`: Risk per trade (0.005 = 0.5%)
- `MAX_DAILY_DRAWDOWN`: Max daily loss (0.02 = 2%)

### Strategy Settings
- `FAST_SMA`: Fast moving average period (default: 20)
- `SLOW_SMA`: Slow moving average period (default: 50)
- `ATR_WINDOW`: ATR calculation window (default: 14)
- `ATR_MULTIPLIER`: Stop loss multiplier (default: 2.0)

## 🔒 Security Notes

- **Never share your API keys**
- **Never commit .env to version control**
- **Start with paper trading first**
- **Test thoroughly before going live**

## 🆘 Need Help?

1. Check the [Broker Setup Guide](BROKER_SETUP.md) for detailed instructions
2. Use the dashboard's built-in help sections
3. Start with OANDA for easiest setup

## 🎉 You're Ready!

Once you've filled in your API credentials, you can:
1. Run the dashboard
2. Connect to your broker
3. Start with paper trading
4. Switch to live when ready (with caution!)

Happy trading! 🚀
