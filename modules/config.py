"""
Configuration module for Gateway Content Automation
Handles all environment variables and API configurations
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st

# Load environment variables
load_dotenv()

# Configure Google Gemini API
api_key = os.getenv('GEMINI_API_KEY')
if not api_key or api_key == "your_gemini_api_key_here":
    st.error("⚠️ Please set your Gemini API key in the .env file")
    st.stop()

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro')

# Vadoo AI Configuration
VADOO_API_KEY = os.getenv('VADOO_API_KEY')
VADOO_API_URL = "https://viralapi.vadoo.tv/api"

# Canva API Configuration
CANVA_API_KEY = os.getenv('CANVA_API_KEY')
CANVA_CLIENT_ID = os.getenv('CANVA_CLIENT_ID')
CANVA_CLIENT_SECRET = os.getenv('CANVA_CLIENT_SECRET')

# MindMeister OAuth Configuration
MINDMEISTER_CLIENT_ID = os.getenv('MINDMEISTER_CLIENT_ID')
MINDMEISTER_CLIENT_SECRET = os.getenv('MINDMEISTER_CLIENT_SECRET')
MINDMEISTER_REDIRECT_URI = os.getenv('MINDMEISTER_REDIRECT_URI', 'http://localhost:8501')
MINDMEISTER_API_URL = "https://www.mindmeister.com/services/rest/oauth2"

# Database Encryption Key
DATABASE_ENCRYPTION_KEY = os.getenv('DATABASE_ENCRYPTION_KEY') 