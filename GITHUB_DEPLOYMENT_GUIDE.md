# 🚀 GitHub Deployment Guide

This guide will walk you through deploying your trading bot to the cloud using GitHub and Streamlit Cloud.

## 📋 **Step-by-Step Process**

### **Step 1: Create GitHub Repository**

1. **Go to:** https://github.com
2. **Sign in** to your GitHub account (create one if needed)
3. **Click "New repository"** (green button)
4. **Repository name:** `trading-bot` (or any name you prefer)
5. **Description:** `Universal Trading Bot with Streamlit Dashboard`
6. **Make it Public** (required for free Streamlit Cloud)
7. **Don't initialize** with README (we already have files)
8. **Click "Create repository"**

### **Step 2: Connect Local Repository to GitHub**

Run these commands in your terminal:

```bash
# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/trading-bot.git

# Push your code to GitHub
git branch -M main
git push -u origin main
```

### **Step 3: Deploy to Streamlit Cloud**

1. **Go to:** https://share.streamlit.io/
2. **Sign in** with your GitHub account
3. **Click "New app"**
4. **Repository:** Select your `trading-bot` repository
5. **Branch:** `main`
6. **Main file path:** `dashboard.py`
7. **App URL:** Choose a custom name (e.g., `your-trading-bot`)
8. **Click "Deploy!"**

### **Step 4: Set Environment Variables**

1. **In Streamlit Cloud dashboard**
2. **Click on your app**
3. **Go to "Settings"**
4. **Click "Secrets"**
5. **Add your API keys:**

```toml
# OANDA
OANDA_ACCESS_TOKEN = "your_oanda_token"
OANDA_ACCOUNT_ID = "your_account_id"
OANDA_ENVIRONMENT = "practice"

# Binance (CCXT)
CCXT_EXCHANGE = "binance"
CCXT_API_KEY = "your_binance_key"
CCXT_SECRET = "your_binance_secret"
CCXT_SANDBOX = "true"

# Alpaca
ALPACA_API_KEY = "your_alpaca_key"
ALPACA_SECRET_KEY = "your_alpaca_secret"
ALPACA_PAPER = "true"

# Trading Settings
BROKER = "oanda"
RISK_PER_TRADE = "0.01"
MAX_DAILY_DRAWDOWN = "0.03"
```

6. **Click "Save"**

### **Step 5: Access Your Trading Bot**

Your bot will be available at:
`https://your-trading-bot.streamlit.app`

## 🎯 **Quick Commands**

### **If you don't have GitHub CLI:**
```bash
# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/trading-bot.git

# Push to GitHub
git push -u origin main
```

### **If you have GitHub CLI:**
```bash
# Create repository and push
gh repo create trading-bot --public --source=. --remote=origin --push
```

## 📱 **Mobile Access**

Once deployed, you can:
- **Access from your phone** at the Streamlit URL
- **Start/stop trading** with one tap
- **Monitor P&L** in real-time
- **Check positions** anywhere
- **Adjust settings** on the go

## 🔄 **Updating Your Bot**

To update your bot:
```bash
# Make changes to your code
git add .
git commit -m "Update trading bot"
git push origin main
```

Streamlit Cloud will automatically redeploy your app!

## 🛡️ **Security Notes**

- **Never commit** `.env` files to GitHub
- **Use environment variables** for API keys
- **Start with paper trading** accounts
- **Test thoroughly** before going live

## 🆘 **Troubleshooting**

### **Common Issues:**

1. **"Repository not found"**
   - Check your GitHub username
   - Make sure repository is public

2. **"Deployment failed"**
   - Check `requirements.txt` exists
   - Verify `dashboard.py` is in root directory

3. **"Module not found"**
   - Add missing packages to `requirements.txt`
   - Redeploy the app

### **Getting Help:**
- Check Streamlit Cloud logs
- Review GitHub repository
- Test locally first

## 🎉 **You're Ready!**

Once deployed, your trading bot will be:
- ✅ **Accessible from anywhere**
- ✅ **Running 24/7**
- ✅ **Mobile-friendly**
- ✅ **Automatically updated**

**Your trading bot URL will be:** `https://your-trading-bot.streamlit.app`
