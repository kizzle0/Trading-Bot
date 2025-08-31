#!/usr/bin/env python3
"""
Deploy your trading bot to Streamlit Cloud for 24/7 access
"""
import os
import subprocess
import sys

def create_requirements_file():
    """Create a requirements.txt file for cloud deployment"""
    requirements = """streamlit>=1.28.0
pandas>=2.2.0
numpy>=1.26.0
yfinance>=0.2.40
ccxt>=4.0.0
oandapyV20>=0.7.2
alpaca-trade-api>=3.0.0
python-dotenv>=1.0.1
loguru>=0.7.2
pydantic>=2.7.0
matplotlib>=3.7.0
plotly>=5.17.0
backtesting>=0.3.3
websockets>=13.0
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    
    print("✅ Created requirements.txt for cloud deployment")

def create_streamlit_config():
    """Create Streamlit config for cloud deployment"""
    config = """[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
"""
    
    os.makedirs('.streamlit', exist_ok=True)
    with open('.streamlit/config.toml', 'w') as f:
        f.write(config)
    
    print("✅ Created Streamlit config for cloud deployment")

def main():
    print("🚀 Trading Bot Cloud Deployment Setup")
    print("=" * 50)
    
    print("This will prepare your trading bot for cloud deployment.")
    print("You'll be able to access it from anywhere in the world!")
    print()
    
    # Create necessary files
    create_requirements_file()
    create_streamlit_config()
    
    print("\n📋 Next Steps:")
    print("1. Go to https://share.streamlit.io/")
    print("2. Sign in with your GitHub account")
    print("3. Create a new repository with your trading bot code")
    print("4. Deploy from GitHub repository")
    print("5. Set environment variables for your API keys")
    print()
    
    print("🌐 Benefits of Cloud Deployment:")
    print("• Access from anywhere (phone, tablet, computer)")
    print("• Runs 24/7 automatically")
    print("• No need to keep your computer on")
    print("• Professional web app URL")
    print("• Automatic updates when you push to GitHub")
    print()
    
    print("💰 Cost: FREE for public repositories!")
    print("🔒 Security: Use environment variables for API keys")

if __name__ == "__main__":
    main()
