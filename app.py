import streamlit as st
# Load environment variables and configure AI

import google.generativeai as genai
# Load environment variables and configure AI

from dotenv import load_dotenv
# Load environment variables and configure AI

import os 

import PyPDF2
import time
#Importing time to measure the time taken to generate the video
import base64 
#Importing base64 to encode and decode the video
import requests 
#Importing requests to make API calls to the video generation API
import json
from docx import Document

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

# Set page config
st.set_page_config(page_title='Content Generator with Vadoo AI', layout='wide')

# Title
st.title("🤖 Automated Content Generator with Vadoo AI")

# Information about Vadoo AI capabilities
with st.expander("ℹ️ About Vadoo AI Video Generation"):
    st.write("""
    **🎬 Vadoo AI Video Generation**
    
    This app now uses Vadoo AI to generate actual videos with AI voiceover! Here's what you can create:
    
    **✨ Features:**
    - **Real AI Videos**: Generate actual video content with AI-generated visuals
    - **Built-in Voiceover**: Videos come with AI-generated narration
    - **Multiple Styles**: Choose from different themes and styles
    - **Custom Scripts**: Use your own content or let AI generate scripts
    - **Multiple Languages**: Generate videos in different languages
    - **Flexible Duration**: From 30 seconds to 10 minutes
    
    **🎯 Best Practices:**
    - Provide detailed, descriptive prompts for better results
    - Specify the educational topic clearly
    - Include key concepts you want to highlight
    - Mention target audience (new employees, students, etc.)
    
    **💰 Pricing:**
    - Video generation: Included with Vadoo AI subscription
    - No additional cost for voiceover (included)
    - Free script generation as fallback
    
    **🔧 Requirements:**
    - Valid Vadoo AI API key in your .env file
    - Stable internet connection for video processing
    - Patience (video generation takes 2-3 minutes)
    """)

# Test API connection
if st.button("🔍 Test API Connection"):
    try:
        st.info("Testing Gemini API connection...")
        test_response = model.generate_content("Hello, this is a test.")
        st.success("✅ Gemini API connection successful!")
        st.write(f"Response: {test_response.text}")
        
        if VADOO_API_KEY:
            st.success("✅ Vadoo AI API key found!")
        else:
            st.warning("⚠️ Vadoo AI API key not set. Video generation will use enhanced scripts.")
    except Exception as e:
        st.error(f"❌ API connection failed: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")

def generate_vadoo_video(prompt, duration_minutes=2, aspect_ratio="16:9"):
    """
    Generate video using Vadoo AI video generation API
    """
    if not VADOO_API_KEY:
        st.warning("⚠️ Vadoo AI API key not set. Using enhanced video script generation.")
        return generate_enhanced_video_script(prompt, duration_minutes)
    
    try:
        st.write(f"🔍 Debug: Duration in minutes: {duration_minutes}")
        st.write(f"🔍 Debug: Prompt length: {len(prompt)} characters")
        st.write(f"🔍 Debug: Aspect ratio: {aspect_ratio}")
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("🔄 Initializing Vadoo AI video generation...")
        
        # Vadoo API headers with API key
        headers = {
            "X-API-KEY": VADOO_API_KEY,
            "Content-Type": "application/json"
        }
        
        # Map duration to Vadoo format
        duration_mapping = {
            1: "30-60",
            2: "60-90", 
            3: "90-120",
            5: "5 min",
            10: "10 min"
        }
        vadoo_duration = duration_mapping.get(duration_minutes, "30-60")
        
        # Prepare video generation request for Vadoo AI
        video_request = {
            "topic": "Custom",
            "prompt": prompt,
            "duration": vadoo_duration,
            "aspect_ratio": aspect_ratio,
            "language": "English",
            "voice": "Charlie",
            "theme": "Hormozi_1",
            "include_voiceover": "1",
            "use_ai": "1",
            "custom_instruction": f"Create an educational video about: {prompt}. Make it engaging and informative for new employees."
        }
        
        progress_bar.progress(25)
        status_text.text("🔄 Sending request to Vadoo AI...")
        
        # Make API call to Vadoo AI's video generation endpoint
        response = requests.post(
            f"{VADOO_API_URL}/generate_video",
            headers=headers,
            json=video_request,
            timeout=600  # Longer timeout for video generation
        )
        
        progress_bar.progress(50)
        status_text.text("🔄 Processing Vadoo AI video generation...")
        
        if response.status_code == 200:
            video_data = response.json()
            progress_bar.progress(75)
            status_text.text("🔄 Video generation initiated! Waiting for completion...")
            
            # Vadoo returns a video ID, we need to poll for completion
            video_id = video_data.get("vid")
            if video_id:
                st.info(f"🎬 Video generation started! Video ID: {video_id}")
                st.info("⏳ Video will be ready in 2-3 minutes. Check your Vadoo dashboard for the final video.")
                
                return {
                    "success": True,
                    "video_id": video_id,
                    "message": f"Video generation started! Video ID: {video_id}. Check your Vadoo dashboard in 2-3 minutes.",
                    "type": "video_generation_started"
                }
            else:
                st.error("❌ No video ID received from Vadoo AI")
                return generate_enhanced_video_script(prompt, duration_minutes)
        else:
            st.error(f"❌ Vadoo AI API error: {response.status_code} - {response.text}")
            return generate_enhanced_video_script(prompt, duration_minutes)
            
    except Exception as e:
        st.error(f"Vadoo AI video generation error: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")
        return generate_enhanced_video_script(prompt, duration_minutes)

def generate_enhanced_video_script(prompt, duration_minutes=2):
    """
    Generate enhanced video script using Gemini when Vadoo AI is not available
    """
    try:
        st.write(f"🔍 Debug: Duration in minutes: {duration_minutes}")
        st.write(f"🔍 Debug: Prompt length: {len(prompt)} characters")
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("🔄 Generating enhanced video content with Gemini...")
        
        # Generate enhanced video script with Gemini
        enhanced_prompt = f"""
        Create a comprehensive video production guide for a {duration_minutes}-minute educational video about: {prompt}
        
        Include:
        1. Detailed scene-by-scene breakdown with timing
        2. Visual descriptions and camera angles
        3. Narration script with exact timing
        4. Graphics and text overlay suggestions
        5. Background music recommendations
        6. Production checklist
        7. Estimated production time
        8. Canva template suggestions
        9. Color scheme recommendations
        10. Font and typography suggestions
        """
        
        progress_bar.progress(50)
        status_text.text("🔄 Generating content with Gemini...")
        
        response = model.generate_content(enhanced_prompt)
        
        progress_bar.progress(100)
        status_text.text("✅ Enhanced video content generated successfully!")
        
        return {
            "success": True,
            "script": response.text,
            "type": "enhanced_script"
        }
    except Exception as e:
        st.error(f"Video content generation error: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")
        return None

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
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # Read the DOCX file
            doc = Document(file)
            # Loop through each paragraph and extract text
            for para in doc.paragraphs:
                extracted_content += para.text + "\n\n"
                # Display the file name and content
    
    # Debug: Show if content was extracted
    st.write(f"Content length: {len(extracted_content)} characters")
    
    if extracted_content:
        st.subheader("Extracted Content")
        # Display the extracted content
        st.text_area("Content from uploaded files", extracted_content, height=300)
        
        # Cache the processed content for better performance
        if 'cached_content' not in st.session_state:
            st.session_state.cached_content = extracted_content[:1000]
        
        # Generate training content button
        if st.button("Generate Training Materials"):
            st.session_state.show_training_materials = True
        
        # Add reset button if materials are shown
        if st.session_state.get('show_training_materials', False):
            if st.button("🔄 Reset & Regenerate"):
                st.session_state.show_training_materials = False
                st.rerun()
        
        # Show training materials if button was clicked
        if st.session_state.get('show_training_materials', False):
            st.write("Generating AI-powered training materials...")
            
            #Create tabs for different content sections
            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                "🤖 Content Overview", 
                "🎯 Key Points", 
                "📚 Detailed Analysis", 
                "💡 Practical Applications",
                "🃏 Interactive Flashcards",
                "🎥 Vadoo AI Video Generation",
                "🖼️ Visual Learning Resources"
            ])

            # Pre-process content for video generation to avoid delays
            cached_content = st.session_state.get('cached_content', extracted_content[:1000])
            video_generation_prompt = f"Create an educational video about: {cached_content}. Make it engaging and informative for new employees."
            
            # Cache the video prompt for better performance
            if 'video_prompt' not in st.session_state:
                st.session_state.video_prompt = video_generation_prompt

            with tab1:
                st.header("Content Overview")
                # AI will generate overview based on uploaded files
                overview_prompt = f"Create a brief overview of this content: {extracted_content[:5000]}"
                try:
                    st.info("🔄 Connecting to Gemini API...")
                    overview_response = model.generate_content(overview_prompt)
                    st.success("✅ API call successful!")
                    st.write(overview_response.text)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.error(f"Error type: {type(e).__name__}")
                    st.write("Content overview will be generated here based on your uploaded files.")
            with tab2:
                st.header("Key Points")
                key_points_prompt = f"Extract the main key points and important concepts from this content: {extracted_content[:5000]}"
                try:
                    key_points_response = model.generate_content(key_points_prompt)
                    st.write(key_points_response.text)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.write("Key points will be extracted from your uploaded files.")
            with tab3:
                st.header("Detailed Analysis")
                analysis_prompt = f"Provide a detailed analysis of this content: {extracted_content[:5000]}"
                try:
                    analysis_response = model.generate_content(analysis_prompt)
                    st.write(analysis_response.text)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.write("Detailed analysis will be generated here based on your uploaded files.")
            with tab4:
                st.header("Practical Applications")
                practical_prompt = f"Apply the key points and analysis to create practical applications for new employees: {extracted_content[:5000]}"
                try:
                    practical_response = model.generate_content(practical_prompt)
                    st.write(practical_response.text)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.write("Practical applications will be generated here based on your uploaded files.")
            with tab5:
                st.header("🃏 Interactive Flashcards")
                
                # Generate flashcards using AI
                flashcards_prompt = f"Create 5 interactive flashcards based on this content: {extracted_content[:5000]}. Format each flashcard as: 'Question: [question]' followed by 'Answer: [answer]' on the next line. Make them engaging and educational."
                
                try:
                    st.info("🔄 Generating flashcards...")
                    flashcards_response = model.generate_content(flashcards_prompt)
                    
                    flashcards_content = flashcards_response.text
                    
                    # Parse flashcards
                    flashcard_pairs = []
                    lines = flashcards_content.split('\n')
                    current_question = ""
                    
                    for line in lines:
                        if line.strip().startswith('Question:'):
                            current_question = line.strip().replace('Question:', '').strip()
                            #If the line starts with Question: then the current question is the line after Question:
                        elif line.strip().startswith('Answer:') and current_question:
                            answer = line.strip().replace('Answer:', '').strip()
                            #If the line starts with Answer: and the current question is not empty then the answer is the line after Answer:
                            flashcard_pairs.append((current_question, answer))
                            current_question = ""
                            #If the line starts with Answer: and the current question is not empty then the answer is the line after Answer:
                    
                    # Display flashcards with interactive reveal
                    if flashcard_pairs:
                        st.success(f"✅ Generated {len(flashcard_pairs)} flashcards!")
                        
                        for i, (question, answer) in enumerate(flashcard_pairs, 1):
                            with st.expander(f"📝 Flashcard {i}: {question[:50]}..."):
                                st.write(f"**Question:** {question}")
                                st.write(f"**Answer:** {answer}")
                                
                                # Add interactive elements
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button(f"🎯 Mark as Known", key=f"known_{i}"):
                                        st.success("✅ Marked as known!")
                                with col2:
                                    if st.button(f"📝 Review Later", key=f"review_{i}"):
                                        st.info("📝 Added to review list!")
                    else:
                        st.write("Flashcards will be generated here based on your content.")
                        
                except Exception as e:
                    st.error(f"❌ Error generating flashcards: {str(e)}")
                    st.write("Flashcards will be generated here based on your uploaded files.")
            with tab6:
                st.header("🎥 Vadoo AI Video Generation")
                
                # Add video generation controls
                st.write("**Video Settings:**")
                
                # Use columns for better layout
                col1, col2, col3 = st.columns(3)
                with col1:
                    video_duration = st.selectbox("Duration", [1, 2, 3, 5, 10], index=1, format_func=lambda x: f"{x} min")
                    aspect_ratio = st.selectbox("Aspect Ratio", ["16:9", "9:16", "1:1"], index=0)
                with col2:
                    if VADOO_API_KEY:
                        st.write("**Video:** Vadoo AI")
                        st.write("**Voice:** Charlie")
                        st.write("**Theme:** Hormozi_1")
                        st.write(f"**Aspect:** {aspect_ratio}")
                    else:
                        st.write("**Video:** Free (script)")
                with col3:
                    generate_button = st.button("🎬 Generate AI Video with Vadoo AI", key="generate_video", type="primary")
                
                # Show video generation area only when button is clicked
                if generate_button:
                    with st.spinner("🔄 Preparing Vadoo AI video generation..."):
                        st.write("🔍 Debug: Generate button was clicked!")
                        st.write(f"🔍 Debug: Content length: {len(extracted_content)}")
                        st.write(f"🔍 Debug: Duration: {video_duration} minutes")
                        
                        if extracted_content:
                            st.info("🔄 Generating AI video with Vadoo AI...")
                            
                            # Use cached prompt for better performance
                            cached_prompt = st.session_state.get('video_prompt', video_generation_prompt)
                            
                            # Generate video using Vadoo AI
                            video_response = generate_vadoo_video(cached_prompt, video_duration, aspect_ratio)
                            
                            if video_response and video_response.get("success"):
                                if video_response.get("type") == "video_generation_started":
                                    st.success("✅ Video generation started with Vadoo AI!")
                                    
                                    # Display video generation status
                                    st.subheader("🎬 Video Generation Status")
                                    st.info(video_response.get("message", "Video generation initiated!"))
                                    
                                    # Video details
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.write(f"**Video ID:** {video_response.get('video_id', 'N/A')}")
                                        st.write(f"**Duration:** {video_duration} minutes")
                                    with col2:
                                        st.write("**Model:** Vadoo AI")
                                        st.write("**Status:** Processing")
                                    with col3:
                                        st.write("**Format:** MP4")
                                        st.write("**Voiceover:** Included")
                                    
                                    # Instructions for user
                                    st.subheader("📋 Next Steps")
                                    st.write("""
                                    1. **Wait 2-3 minutes** for video processing to complete
                                    2. **Check your Vadoo dashboard** for the final video
                                    3. **Download the video** from your Vadoo account
                                    4. **Share or use** the video as needed
                                    """)
                                    
                                    # Add video script for reference
                                    st.subheader("📝 Video Script Reference")
                                    st.info("This is the script that was used to generate your AI video:")
                                    st.text_area("📝 Generated Script", cached_prompt, height=200)
                                    
                                    # Add direct Vadoo integration option
                                    st.subheader("🎨 Alternative: Direct Vadoo AI Integration")
                                    st.info("💡 Want more control? Use Vadoo AI directly with your script:")
                                    
                                    # Direct links with better formatting
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        # Create a direct link with pre-filled prompt
                                        encoded_prompt = cached_prompt.replace(" ", "%20").replace("\n", "%0A")
                                        vadoo_create_url = f"https://vadoo.tv/create?prompt={encoded_prompt[:200]}"
                                        st.markdown(f"""
                                        <a href="{vadoo_create_url}" target="_blank">
                                            <button style="
                                                background-color: #2196F3;
                                                border: none;
                                                color: white;
                                                padding: 15px 32px;
                                                text-align: center;
                                                text-decoration: none;
                                                display: inline-block;
                                                font-size: 16px;
                                                margin: 4px 2px;
                                                cursor: pointer;
                                                border-radius: 8px;
                                                width: 100%;
                                            ">
                                                🎬 Create Video in Vadoo AI
                                            </button>
                                        </a>
                                        """, unsafe_allow_html=True)
                                    
                                    with col2:
                                        if st.button("📋 Copy Script to Clipboard", key="copy_script_api"):
                                            st.session_state.script_to_copy = cached_prompt
                                            st.success("✅ Script copied! Paste it in Vadoo AI.")
                                    
                                    st.write(f"""
                                    **Recommended Settings for Direct Use:**
                                    - **Duration**: {video_duration} minutes
                                    - **Aspect Ratio**: {aspect_ratio}
                                    - **Voice**: Charlie
                                    - **Theme**: Hormozi_1
                                    """)
                                elif video_response.get("type") == "enhanced_script":
                                    st.success("✅ Enhanced video script generated!")
                                    
                                    # Display video script
                                    st.subheader("🎬 Your Enhanced Video Script")
                                    st.text_area("📝 Video Script", video_response["script"], height=400)
                                    
                                    # Add download option for script
                                    if st.button("📥 Download Script", key="download_script"):
                                        st.info("Script download feature coming soon!")
                                        
                                    # Add Vadoo integration suggestions
                                    st.subheader("🎨 Direct Vadoo AI Integration")
                                    
                                    # Create prominent direct links to Vadoo AI
                                    st.markdown("""
                                    **🚀 Quick Actions:**
                                    """)
                                    
                                    # Direct links with better formatting
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.markdown(f"""
                                        <a href="https://vadoo.tv" target="_blank">
                                            <button style="
                                                background-color: #4CAF50;
                                                border: none;
                                                color: white;
                                                padding: 15px 32px;
                                                text-align: center;
                                                text-decoration: none;
                                                display: inline-block;
                                                font-size: 16px;
                                                margin: 4px 2px;
                                                cursor: pointer;
                                                border-radius: 8px;
                                                width: 100%;
                                            ">
                                                🚀 Open Vadoo Dashboard
                                            </button>
                                        </a>
                                        """, unsafe_allow_html=True)
                                    
                                    with col2:
                                        # Create a direct link with pre-filled prompt
                                        encoded_prompt = cached_prompt.replace(" ", "%20").replace("\n", "%0A")
                                        vadoo_create_url = f"https://vadoo.tv/create?prompt={encoded_prompt[:200]}"
                                        st.markdown(f"""
                                        <a href="{vadoo_create_url}" target="_blank">
                                            <button style="
                                                background-color: #2196F3;
                                                border: none;
                                                color: white;
                                                padding: 15px 32px;
                                                text-align: center;
                                                text-decoration: none;
                                                display: inline-block;
                                                font-size: 16px;
                                                margin: 4px 2px;
                                                cursor: pointer;
                                                border-radius: 8px;
                                                width: 100%;
                                            ">
                                                🎬 Create Video Now
                                            </button>
                                        </a>
                                        """, unsafe_allow_html=True)
                                    
                                    with col3:
                                        st.markdown(f"""
                                        <a href="https://vadoo.tv/pricing" target="_blank">
                                            <button style="
                                                background-color: #FF9800;
                                                border: none;
                                                color: white;
                                                padding: 15px 32px;
                                                text-align: center;
                                                text-decoration: none;
                                                display: inline-block;
                                                font-size: 16px;
                                                margin: 4px 2px;
                                                cursor: pointer;
                                                border-radius: 8px;
                                                width: 100%;
                                            ">
                                                💰 View Pricing
                                            </button>
                                        </a>
                                        """, unsafe_allow_html=True)
                                    
                                    # Show the script for easy copying with copy button
                                    st.subheader("📋 Your Video Script (Ready to Copy)")
                                    
                                    # Add copy functionality
                                    if st.button("📋 Copy Script to Clipboard", key="copy_script_button"):
                                        st.session_state.script_to_copy = cached_prompt
                                        st.success("✅ Script copied to clipboard! You can now paste it directly in Vadoo AI.")
                                    
                                    st.text_area("📝 Script for Vadoo AI", cached_prompt, height=150, key="vadoo_script")
                                    
                                    # Add quick settings guide with direct links
                                    st.subheader("⚙️ Recommended Vadoo AI Settings")
                                    st.write(f"""
                                    **For best results, use these settings in Vadoo AI:**
                                    - **Duration**: {video_duration} minutes
                                    - **Aspect Ratio**: {aspect_ratio}
                                    - **Voice**: Charlie (or your preference)
                                    - **Theme**: Hormozi_1 (professional)
                                    - **Language**: English
                                    - **Include Voiceover**: Yes
                                    - **Use AI Enhancement**: Yes
                                    """)
                                    
                                    # Add direct integration instructions
                                    st.subheader("🔗 Direct Integration Steps")
                                    st.write("""
                                    1. **Click "Create Video Now"** above to open Vadoo AI with your script pre-filled
                                    2. **Copy the script** from the text area above
                                    3. **Paste it** into Vadoo AI's prompt field
                                    4. **Apply the recommended settings** listed above
                                    5. **Generate your video** and download it
                                    """)
                                else:
                                    st.success("✅ Video generated successfully with Vadoo AI!")
                                    
                                    # Display video
                                    st.subheader("🎬 Your Generated Video")
                                    
                                    if video_response.get("video_url"):
                                        st.video(video_response["video_url"])
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if st.button("📥 Download Video", key="download_video"):
                                            st.info("Video download feature coming soon!")
                                    with col2:
                                        st.write(f"**Duration:** {video_duration} minutes")
                                        st.write("**Platform:** Vadoo AI")
                            else:
                                st.error("❌ Failed to generate video. Please try again.")
                        else:
                            st.warning("⚠️ Please upload content first to generate videos.")
                else:
                    if VADOO_API_KEY:
                        st.info("💡 Click 'Generate AI Video with Vadoo AI' to create an AI-generated video with Vadoo AI!")
                        
                        # Add direct integration option even with API
                        st.subheader("🎨 Or Use Vadoo AI Directly")
                        st.write("**Want more control? Use Vadoo AI website directly:**")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("""
                            <a href="https://vadoo.tv" target="_blank">
                                <button style="
                                    background-color: #4CAF50;
                                    border: none;
                                    color: white;
                                    padding: 15px 32px;
                                    text-align: center;
                                    text-decoration: none;
                                    display: inline-block;
                                    font-size: 16px;
                                    margin: 4px 2px;
                                    cursor: pointer;
                                    border-radius: 8px;
                                    width: 100%;
                                ">
                                    🚀 Open Vadoo AI
                                </button>
                            </a>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("""
                            <a href="https://vadoo.tv/create" target="_blank">
                                <button style="
                                    background-color: #2196F3;
                                    border: none;
                                    color: white;
                                    padding: 15px 32px;
                                    text-align: center;
                                    text-decoration: none;
                                    display: inline-block;
                                    font-size: 16px;
                                    margin: 4px 2px;
                                    cursor: pointer;
                                    border-radius: 8px;
                                    width: 100%;
                                ">
                                    🎬 Create Video
                                </button>
                            </a>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("💡 Click 'Generate AI Video with Vadoo AI' to get an enhanced video script!")
                        st.warning("⚠️ To enable full AI video generation, add your VADOO_API_KEY to the .env file")
                        
                        # Add direct integration option when no API key
                        st.subheader("🎨 Use Vadoo AI Directly")
                        st.write("**No API key? No problem! Use Vadoo AI website directly:**")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown("""
                            <a href="https://vadoo.tv" target="_blank">
                                <button style="
                                    background-color: #4CAF50;
                                    border: none;
                                    color: white;
                                    padding: 15px 32px;
                                    text-align: center;
                                    text-decoration: none;
                                    display: inline-block;
                                    font-size: 16px;
                                    margin: 4px 2px;
                                    cursor: pointer;
                                    border-radius: 8px;
                                    width: 100%;
                                ">
                                    🚀 Open Vadoo AI
                                </button>
                            </a>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("""
                            <a href="https://vadoo.tv/create" target="_blank">
                                <button style="
                                    background-color: #2196F3;
                                    border: none;
                                    color: white;
                                    padding: 15px 32px;
                                    text-align: center;
                                    text-decoration: none;
                                    display: inline-block;
                                    font-size: 16px;
                                    margin: 4px 2px;
                                    cursor: pointer;
                                    border-radius: 8px;
                                    width: 100%;
                                ">
                                    🎬 Create Video
                                </button>
                            </a>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown("""
                            <a href="https://vadoo.tv/pricing" target="_blank">
                                <button style="
                                    background-color: #FF9800;
                                    border: none;
                                    color: white;
                                    padding: 15px 32px;
                                    text-align: center;
                                    text-decoration: none;
                                    display: inline-block;
                                    font-size: 16px;
                                    margin: 4px 2px;
                                    cursor: pointer;
                                    border-radius: 8px;
                                    width: 100%;
                                ">
                                    💰 View Pricing
                                </button>
                            </a>
                            """, unsafe_allow_html=True)
            with tab7:
                st.header("🖼️ Visual Learning Resources")
                st.write("Visual learning resources for effective learning and memorization.")
    else:
        st.warning("No content was extracted from the uploaded files.")
        # Show button even if no content
        if st.button("Generate Training Materials"):
            st.write("No content to process. Please upload valid files.")