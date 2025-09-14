#!/usr/bin/env python3
"""
Debug script to check what API key is being used
"""

import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== API Key Debug ===")
print(f"Environment variable: {os.getenv('GEMINI_API_KEY')}")
print(f"Environment variable length: {len(os.getenv('GEMINI_API_KEY', ''))}")

# Check if we can access Streamlit secrets
try:
    secrets_key = st.secrets.get('GEMINI_API_KEY')
    print(f"Streamlit secrets: {secrets_key}")
    print(f"Streamlit secrets length: {len(secrets_key) if secrets_key else 0}")
except Exception as e:
    print(f"Streamlit secrets error: {e}")

# Check .env file directly
try:
    with open('.env', 'r') as f:
        env_content = f.read()
        print(f".env file content: {env_content.strip()}")
except Exception as e:
    print(f".env file error: {e}")

print("=== End Debug ===")
