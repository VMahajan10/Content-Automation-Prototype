#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Install required packages if needed
pip install python-docx PyPDF2 streamlit google-generativeai python-dotenv requests

# Run the Streamlit app
python -m streamlit run app.py 