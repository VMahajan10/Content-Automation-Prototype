import streamlit as st
# Load environment variables and configure AI

import openai
# Load environment variables and configure AI

from dotenv import load_dotenv
# Load environment variables and configure AI

import os 

import PyPDF2
import time

load_dotenv()
# Configure OpenAI API
api_key = os.getenv('OPENAI_API_KEY')
if not api_key or api_key == "your_openai_api_key_here":
    st.error("⚠️ Please set your OpenAI API key in the .env file")
    st.stop()

client = openai.OpenAI(api_key=api_key)
# Set page config
st.set_page_config(page_title='Content Generator', layout='wide')
# Title

st.title("🤖 Automated Content Generator")

# Test API connection
if st.button("🔍 Test API Connection"):
    try:
        st.info("Testing OpenAI API connection...")
        test_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, this is a test."}],
            max_tokens=10
        )
        st.success("✅ API connection successful!")
        st.write(f"Response: {test_response.choices[0].message.content}")
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
        # Generate training content button
        if st.button("Generate Training Materials"):
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
                "🎥 Video Learning Resources",
                "🖼️ Visual Learning Resources"
            ])

            with tab1:
                st.header("Content Overview")
                # AI will generate overview based on uploaded files
                overview_prompt = f"Create a brief overview of this content: {extracted_content[:5000]}"
                try:
                    st.info("🔄 Connecting to OpenAI API...")
                    overview_response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that creates clear content summaries."},
                            {"role": "user", "content": overview_prompt}
                        ],
                        max_tokens=500,
                        temperature=0.7
                    )
                    st.success("✅ API call successful!")
                    st.write(overview_response.choices[0].message.content)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.error(f"Error type: {type(e).__name__}")
                    st.write("Content overview will be generated here based on your uploaded files.")
            with tab2:
                st.header("Key Points")
                key_points_prompt = f"Extract the main key points and import concepts from this content: {extracted_content[:5000]}"
                try:
                    key_points_response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            #System prompt
                            {"role": "system", "content": "You are a helpful assistant that extracts key points and creates bullet points "},
                            {"role": "user", "content": key_points_prompt}
                            #Displaying the key points in a bullet point format
                        ],
                        #Max tokens
                        max_tokens=800,
                        #Temperature
                        temperature=0.7,
                    )
                    st.write(key_points_response.choices[0].message.content)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.write("Key points will be extracted from your uploaded files.")
            with tab3:
                st.header("Detailed Analysis")
                analysis_prompt = f"Provide a detailed analysis of this content: {extracted_content[:5000]}"
                try:
                    analysis_response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that provides detailed analysis of content."},
                            {"role": "user", "content": analysis_prompt}
                        ],
                        max_tokens= 800,
                        temperature=0.7,
                    )
                    st.write(analysis_response.choices[0].message.content)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.write("Detailed analysis will be generated here based on your uploaded files.")
            with tab4:
                st.header("Practical Applications")
                practical_prompt = f"Apply the key points and analysis to create practical applications for new employees: {extracted_content[:5000]}"
                try:
                    practical_response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                         {"role": "system", "content": "You are a helpful assistant that creates practical applications for new employees."},
                         {"role": "user", "content": practical_prompt}
                        ],
                        max_tokens=800,
                        temperature=0.7,
                    )
                    st.write(practical_response.choices[0].message.content)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.write("Practical applications will be generated here based on your uploaded files.")
            with tab5:
                st.header("🃏 Interactive Flashcards")
                
                # Generate flashcards using AI
                flashcards_prompt = f"Create 5 interactive flashcards based on this content: {extracted_content[:5000]}. Format each flashcard as: 'Question: [question]' followed by 'Answer: [answer]' on the next line. Make them engaging and educational."
                
                try:
                    st.info("🔄 Generating flashcards...")
                    flashcards_response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that creates engaging educational flashcards."},
                            {"role": "user", "content": flashcards_prompt}
                        ],
                        max_tokens=1000,
                        temperature=0.7,
                    )
                    
                    flashcards_content = flashcards_response.choices[0].message.content
                    
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
                st.header("🎥 Video Learning Resources")
                
                # Generate video suggestions using AI
                video_prompt = f"Based on this content: {extracted_content[:5000]}, suggest 5 educational videos that would help learners understand these concepts. For each video, provide: 1) A descriptive title, 2) A brief explanation of why it's relevant, 3) Estimated duration, 4) Suggested platform (YouTube, Coursera, etc.). Format as: 'Title: [title]' followed by 'Description: [description]' followed by 'Duration: [duration]' followed by 'Platform: [platform]' on separate lines."
                
                try:
                    st.info("🔄 Generating video suggestions...")
                    video_response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that suggests relevant educational videos."},
                            {"role": "user", "content": video_prompt}
                        ],
                        max_tokens=1000,
                        temperature=0.7,
                    )
                    
                    video_content = video_response.choices[0].message.content
                    
                    # Parse video suggestions
                    video_suggestions = []
                    lines = video_content.split('\n')
                    current_video = {}
                    
                    for line in lines:
                    # Strip the line of whitespace
                        line = line.strip()
                        if line.startswith('Title:'):
                            if current_video:
                                #If the line starts with Title: and the current video is not empty then add the current video to the video suggestions
                                video_suggestions.append(current_video)
                            current_video = {'title': line.replace('Title:', '').strip()}
                            #If the line starts with Title: and the current video is empty then the title is the line after Title:
                        elif line.startswith('Description:'):
                            current_video['description'] = line.replace('Description:', '').strip()
                            #If the line starts with Description: and the current video is not empty then the description is the line after Description:
                        elif line.startswith('Duration:'):
                            current_video['duration'] = line.replace('Duration:', '').strip()
                            #If the line starts with Duration: and the current video is not empty then the duration is the line after Duration:
                        elif line.startswith('Platform:'):
                            current_video['platform'] = line.replace('Platform:', '').strip()

                    if current_video:
                        #If the line starts with Platform: and the current video is not empty then the platform is the line after Platform:
                        video_suggestions.append(current_video)
                    
                    # Display video suggestions
                    if video_suggestions:
                        st.success(f"✅ Generated {len(video_suggestions)} video suggestions!")
                        
                        for i, video in enumerate(video_suggestions, 1):
                            #Display the video suggestions in an expander
                            with st.expander(f"🎬 Video {i}: {video.get('title', 'Untitled')}"):
                                st.write(f"**Title:** {video.get('title', 'N/A')}")
                                st.write(f"**Description:** {video.get('description', 'N/A')}")
                                st.write(f"**Duration:** {video.get('duration', 'N/A')}")
                                st.write(f"**Platform:** {video.get('platform', 'N/A')}")
                                
                                # Add interactive elements
                                col1, col2 = st.columns(2)
                                with col1:
                                    #If the button is clicked then the video is added to the watchlist
                                    if st.button(f"📺 Watch Later", key=f"watch_{i}"):
                                        st.success("Added to watchlist!")
                                with col2:
                                    #If the button is clicked then the video is marked as helpful
                                    if st.button(f"⭐ Rate Helpful", key=f"rate_{i}"):
                                        st.info("⭐ Marked as helpful!")
                    else:
                        st.write("Video suggestions will be generated here based on your content.")
                    #If the video suggestions are not generated then the user is informed that the video suggestions will be generated here based on your content.
                except Exception as e:
                    st.error(f"❌ Error generating video suggestions: {str(e)}")
                    st.write("Video suggestions will be generated here based on your uploaded files.")
            with tab7:
                st.header("🖼️ Visual Learning Resources")
                st.write("Visual learning resources for effective learning and memorization.")
    else:
        st.warning("No content was extracted from the uploaded files.")
        # Show button even if no content
        if st.button("Generate Training Materials"):
            st.write("No content to process. Please upload valid files.")