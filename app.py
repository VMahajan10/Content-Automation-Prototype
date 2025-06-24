import streamlit as st
# Load environment variables and configure AI

import google.generativeai as genai
# Load environment variables and configure AI

from dotenv import load_dotenv
# Load environment variables and configure AI

import os 

import PyPDF2

load_dotenv()
# Configure Google AI
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
# Set page config
st.set_page_config(page_title='Content Generator', layout='wide')
# Title

st.title("🤖 Automated Content Generator")
uploaded_files = st.file_uploader("Upload your source files", accept_multiple_files=True, type=['txt', 'pdf', 'docx'])

if uploaded_files:
    # Extract content from uploaded files
    extracted_content = ""
    # Loop through each file and extract content
    for file in uploaded_files:
        # Debug: Show file info
        st.write(f"Processing file: {file.name} (Type: {file.type})")
        
        # Check if the file is a text file
        if file.type == "text/plain":
            # Read the file content
            extracted_content += file.read().decode("utf-8") + "\n\n"
            # Display the file name and content
        elif file.type == "application/pdf":
            # Read the PDF file
            pdf_reader = PyPDF2.PdfReader(file)
            # Loop through each page and extract text
            for page in pdf_reader.pages:
                # Extract text from the page
                extracted_content += page.extract_text() + "\n\n"
                # Display the file name and content
    
    # Debug: Show if content was extracted
    st.write(f"Content length: {len(extracted_content)} characters")
    
    if extracted_content:
        st.subheader("Extracted Content")
        # Display the extracted content
        st.text_area("Content from uploaded files", extracted_content, height=300)
        # Generate training content button
        if st.button("Generate Training Materials"):
            st.write("Generating AI-powered training materials...")
    else:
        st.warning("No content was extracted from the uploaded files.")
        # Show button even if no content
        if st.button("Generate Training Materials"):
            st.write("No content to process. Please upload valid files.")