import streamlit as st
# Load environment variables and configure AI

import google.generativeai as genai
# Load environment variables and configure AI

# Configure Veo2 for video generation
try:
    import google.cloud.aiplatform as aiplatform
    from google.cloud.aiplatform import generative_models
    VEO2_AVAILABLE = True
except ImportError:
    VEO2_AVAILABLE = False
    st.warning("⚠️ Google Cloud AI Platform not available. Veo2 video generation will be disabled.")

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

load_dotenv()
# Configure Google Gemini API
api_key = os.getenv('GEMINI_API_KEY')
if not api_key or api_key == "your_gemini_api_key_here":
    st.error("⚠️ Please set your Gemini API key in the .env file")
    st.stop()

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro')

# Configure Veo2 for video generation
project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')

# Initialize the Veo2 model
if project_id and VEO2_AVAILABLE:
    try:
        aiplatform.init(project=project_id, location=location)
        veo_model = generative_models.VideoGeneratorModel.from_pretrained("veo2")
    except Exception as e:
        veo_model = None
        st.warning(f"⚠️ Veo2 initialization failed: {str(e)}")
else:
    veo_model = None
    if not project_id:
        st.warning("⚠️ Google Cloud Project ID not set. Veo2 video generation will not be available.")
    elif not VEO2_AVAILABLE:
        st.warning("⚠️ Google Cloud AI Platform not available. Veo2 video generation will not be available.")

# Set page config
def generate_video_with_gemini(prompt, duration_minutes=2):
    """
    Generate video content using Gemini's capabilities
    Note: Gemini doesn't have direct video generation, so we provide enhanced script generation
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
        1. Detailed scene-by-scene breakdown
        2. Visual descriptions and camera angles
        3. Narration script with timing
        4. Graphics and text overlay suggestions
        5. Background music recommendations
        6. Production checklist
        7. Estimated production time
        """
        
        progress_bar.progress(50)
        status_text.text("🔄 Generating content with Gemini...")
        
        response = model.generate_content(enhanced_prompt)
        
        progress_bar.progress(100)
        status_text.text("✅ Enhanced video content generated successfully!")
        
        return response
    except Exception as e:
        st.error(f"Video content generation error: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")
        st.write(f"🔍 Debug: Full error details: {e}")
        return None
    
def generate_video_with_veo2(prompt, duration_minutes=2):
    """
    Generate a video using Google's Veo2 model 
    """
    try:
        if not veo_model:
            st.error("❌ Veo2 model not available. Please set up Google Cloud Project ID.")
            return None
        
        st.write(f"🔍 Debug: Duration in minutes: {duration_minutes}")
        st.write(f"🔍 Debug: Prompt length: {len(prompt)} characters")
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        status.text_text("🔄 Initializing Veo2 video generation...")
        
        # Convert minutes to seconds (Veo2 accepts seconds)
        duration_seconds = duration_minutes * 60
        # Convert minutes to seconds (Veo2 accepts seconds)
        progress_bar.progress(25)
        status_text.text("🔄 Generating video with Veo2...")
        
        # Generate video using Veo2
        response = veo_model.generate_video(
            prompt=prompt,
            video_length=duration_seconds
        )
        # Update progress bar to 100%
        progress_bar.progress(100)
        status_text.text("✅ Video generated successfully!")
        
        return response 
    # If there is an error, return None
    except Exception as e:
        st.error(f"Veo2 video generation error: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")
        st.write(f"🔍 Debug: Full error details: {e}")
        return None

st.set_page_config(page_title='Content Generator', layout='wide')
# Title

st.title("🤖 Automated Content Generator")

# Test API connection
if st.button("🔍 Test API Connection"):
    try:
        st.info("Testing Gemini API connection...")
        test_response = model.generate_content("Hello, this is a test.")
        st.success("✅ API connection successful!")
        st.write(f"Response: {test_response.text}")
    except Exception as e:
        st.error(f"❌ API connection failed: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")

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
            
            #Initializing the OpenAI Model 
            # Generate training content
            prompt = f"Based on this content: {extracted_content[:10000]}... Create a comprehensive onboarding training module with the following sections: 1) Welcome Overview, 2) Key Learning Objectives 3)Important Policies 4)Contact Information. Format it as structured content suitable for new employees. "
            # Generate content using the model
            
            # Display the generated content
            st.subheader("🤖 AI-Generated Onboarding Content")
            # Display the generated content
            
            # Create tabs for different content sections
            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                "🤖 Content Overview", 
                "🎯 Key Points", 
                "📚 Detailed Analysis", 
                "💡 Practical Applications",
                "🃏 Interactive Flashcards",
                "🎥 Veo2 Video Generation",
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
                key_points_prompt = f"Extract the main key points and import concepts from this content: {extracted_content[:5000]}"
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
                st.header("🎥 AI-Generated Videos")
                
                # Add video generation controls with better layout
                st.write("**Video Settings:**")
                
                # Use columns for better layout
                col1, col2, col3 = st.columns(3)
                with col1:
                    video_duration = st.slider("Duration (minutes)", 1, 20, 5)
                with col2:
                    st.write(f"**Estimated cost:** ${video_duration * 0.02:.2f}")
                with col3:
                    generate_button = st.button("🎬 Generate Video", key="generate_video", type="primary")
                
                # Show video generation area only when button is clicked
                if generate_button:
                    with st.spinner("🔄 Preparing video generation..."):
                        st.write("🔍 Debug: Generate button was clicked!")
                        st.write(f"🔍 Debug: Content length: {len(extracted_content)}")
                        st.write(f"🔍 Debug: Duration: {video_duration} minutes")
                        
                        if extracted_content:
                            st.info("🔄 Generating video with AI...")
                            
                            # Use cached prompt for better performance
                            cached_prompt = st.session_state.get('video_prompt', video_generation_prompt)
                            
                            # Generate video using Veo2
                            video_response = generate_video_with_veo2(cached_prompt, video_duration)
                            
                            if video_response:
                                st.success("✅ Video generated sucessfully with Veo2!")
                                
                                # Display enhanced video content
                                st.subheader("🎬 Your Generated Video")
                                
                                try:
                                    st.video(video_response)
                                    
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if st.button("📥 Download Video", key="download_video"):
                                            st.info("Video download feature coming soon!")
                                    with col2:
                                        st.write(f"**Duration:** {video_duration} minutes")
                                        st.write("**Model:** Google Veo2")
                                except Exception as e:
                                    st.error(f"❌ Error displaying video: {str(e)}")
                                    st.write("Video was generated but couldn't be displayed.")
                            else:
                                st.error("❌ Failed to generate video. Please try again.")
                                
                                # Provide alternative content generation
                                st.subheader("🎬 Alternative: Video Script Generation")
                                st.info("Since Veo2 video generation failed, here's a detailed video script you can use:")
                                
                                # Generate a video script using the available text API
                                try:
                                    script_prompt = f"Create a detailed video script for a {video_duration}-minute educational video about: {cached_prompt}. Include scene descriptions, narration, and timing."
                                    
                                    script_response = model.generate_content(script_prompt)
                                    
                                    st.success("✅ Video script generated!")
                                    st.text_area("📝 Video Script", script_response.text, height=400)
                                    
                                    # Add download option for script
                                    if st.button("📥 Download Script", key="download_script"):
                                        st.info("Script download feature coming soon!")
                                        
                                except Exception as e:
                                    st.error(f"❌ Failed to generate script: {str(e)}")
                        else:
                            st.warning("⚠️ Please upload content first to generate videos.")
                else:
                    st.info("💡 Click 'Generate Video' to create an AI-generated video based on your content.")
            with tab7:
                st.header("🖼️ Visual Learning Resources")
                st.write("Visual learning resources for effective learning and memorization.")
    else:
        st.warning("No content was extracted from the uploaded files.")
        # Show button even if no content
        if st.button("Generate Training Materials"):
            st.write("No content to process. Please upload valid files.")