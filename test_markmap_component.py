#!/usr/bin/env python3
"""
Test script for the markmap component
"""

import streamlit as st
from markmap_component import markmap

def test_markmap_component():
    """Test the markmap component with sample data"""
    
    st.title("🧠 Markmap Component Test")
    
    # Sample markdown data for testing
    sample_markdown = """# Project Overview
## Frontend
- React Components
  - Navigation
  - Forms
  - Charts
- Styling
  - CSS Modules
  - Tailwind CSS
## Backend
- API Endpoints
  - Authentication
  - Data CRUD
- Database
  - PostgreSQL
  - Redis Cache
## DevOps
- CI/CD Pipeline
- Docker Containers
- Cloud Deployment"""

    st.subheader("📝 Sample Markdown Data")
    st.code(sample_markdown, language="markdown")
    
    st.subheader("🗺️ Rendered Mind Map")
    
    # Test the markmap component
    markmap(sample_markdown, height=600)
    
    st.success("✅ Markmap component test completed!")

if __name__ == "__main__":
    test_markmap_component() 