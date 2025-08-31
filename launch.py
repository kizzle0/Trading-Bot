#!/usr/bin/env python3
"""
Easy launcher for the Universal Trading Bot Dashboard
Double-click this file to start the dashboard!
"""
import subprocess
import sys
import os
import webbrowser
import time
import threading

def open_browser():
    """Open browser after a short delay"""
    time.sleep(3)
    webbrowser.open('http://localhost:8501')

def main():
    print("🚀 Universal Trading Bot Dashboard Launcher")
    print("=" * 50)
    print("Starting the dashboard...")
    print("The dashboard will open in your browser at http://localhost:8501")
    print("Press Ctrl+C to stop the dashboard")
    print("=" * 50)
    
    # Open browser in background
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # Run streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py"])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped. Thanks for using the trading bot!")
    except Exception as e:
        print(f"\n❌ Error starting dashboard: {e}")
        print("Make sure you're in the correct directory and have installed all dependencies.")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
