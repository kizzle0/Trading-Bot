#!/usr/bin/env python3
"""
Main Streamlit app file for cloud deployment
This is a simple wrapper that imports and runs the main dashboard
"""
import streamlit as st
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the main dashboard
try:
    from dashboard import main
    main()
except ImportError as e:
    st.error(f"Error importing dashboard: {e}")
    st.info("Please make sure all required files are in the repository.")
except Exception as e:
    st.error(f"Error running dashboard: {e}")
    st.info("Please check the logs for more details.")
