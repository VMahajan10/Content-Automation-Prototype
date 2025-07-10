#!/bin/bash

echo "🚀 Gateway Content Automation - Starting..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found in current directory"
    echo "💡 Please run this script from the Gateway Content Automation directory"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "✅ Activating virtual environment..."
    source .venv/bin/activate
else
    echo "⚠️ Virtual environment not found"
    echo "💡 Consider creating one: python -m venv .venv"
fi

# Install required packages if needed
echo "📦 Checking dependencies..."
pip install -q python-docx PyPDF2 streamlit google-generativeai python-dotenv requests fastapi uvicorn psutil

# Run the improved startup script
echo "🎯 Starting application with automatic backend management..."
python start_app.py 