"""
Gateway Content Automation - Main Application
Clean, modular version using separate modules for better maintainability
"""

import streamlit as st
import PyPDF2
import time
import base64
import requests
import json
from docx import Document
import math
import re
import tempfile
import os
import mimetypes
import google.generativeai as genai
try:
    import ffmpeg
except ImportError:
    ffmpeg = None

# Import from our modules
from modules.config import *
from modules.utils import extract_key_topics_from_content, calculate_text_dimensions, gemini_generate_module_description, gemini_group_modules_into_sections
from markmap_component import markmap

# Page configuration
st.set_page_config(
    page_title="Gateway Content Automation",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main application
def main():
    st.title("🚀 Gateway Content Automation")
    st.markdown("### AI-Powered Training Content Generation & Mind Mapping")
    
    # Sidebar navigation
    st.sidebar.title("🎯 Navigation")
    page = st.sidebar.selectbox(
        "Choose a section:",
        ["🏠 Home", "🔍 Training Discovery", "🧠 Mind Maps", "📹 Video Generation", "📄 Document Processing", "⚙️ Settings"]
    )
    
    if page == "🏠 Home":
        show_home_page()
    elif page == "🔍 Training Discovery":
        show_training_discovery_page()
    elif page == "🧠 Mind Maps":
        show_mind_maps_page()
    elif page == "📹 Video Generation":
        show_video_generation_page()
    elif page == "📄 Document Processing":
        show_document_processing_page()
    elif page == "⚙️ Settings":
        show_settings_page()

def show_home_page():
    """Home page with overview and quick actions"""
    st.header("🏠 Welcome to Gateway Content Automation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 What You Can Do")
        st.markdown("""
        - **🔍 Training Discovery** - Comprehensive needs analysis and planning
        - **🧠 Create AI Mind Maps** - Generate professional mind maps with MindMeister
        - **📹 Generate Training Videos** - Create engaging video content with AI
        - **📄 Process Documents** - Extract and analyze training materials
        - **🎨 Design Content** - Create visual assets and presentations
        """)
    
    with col2:
        st.subheader("🚀 Quick Start")
        st.markdown("""
        1. **Start with Training Discovery** - Analyze your training needs
        2. **Upload your training materials** (PDFs, Word docs, etc.)
        3. **Configure your settings** with API keys
        4. **Generate content** using AI-powered tools
        5. **Export and share** your professional training content
        """)
    
    # Quick action buttons
    st.subheader("⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔍 Training Discovery", type="primary"):
            st.session_state.page = "🔍 Training Discovery"
            st.rerun()
    
    with col2:
        if st.button("🧠 Create Mind Map"):
            st.session_state.page = "🧠 Mind Maps"
            st.rerun()
    
    with col3:
        if st.button("📹 Generate Video"):
            st.session_state.page = "📹 Video Generation"
            st.rerun()
    
    with col4:
        if st.button("📄 Process Documents"):
            st.session_state.page = "📄 Document Processing"
            st.rerun()
    
    # Quick test mind map
    st.markdown("### 🧪 Quick Mind Map Test")
    if st.button("🎯 Test Mind Map Generation", type="secondary"):
        # Create sample data for testing
        sample_training_context = {
            'target_audience': 'New Employees',
            'training_type': 'Onboarding',
            'industry': 'Technology',
            'company_size': 'Medium Business (200-1000)',
            'urgency_level': 'Medium',
            'timeline': 'Soon (1 month)'
        }
        
        sample_file_inventory = {
            'uploaded_files': ['employee_handbook.pdf', 'onboarding_checklist.docx'],
            'process_docs': 'HR onboarding procedures',
            'training_materials': 'Welcome video, company policies'
        }
        
        sample_collaboration_info = {
            'team_members': ['HR Manager', 'Department Head'],
            'preferred_platform': 'Zoom'
        }
        
        sample_mind_map_info = {
            'mind_map_type': 'Process Flow',
            'mind_map_focus': 'Employee Onboarding Process',
            'complexity_level': 'Moderate (Key details)'
        }
        
        # Generate the mind map
        result = create_mindmeister_ai_mind_map(
            sample_training_context,
            sample_file_inventory,
            sample_collaboration_info,
            sample_mind_map_info,
            "Sample onboarding content and procedures"
        )
        
        if result and result.get('success'):
            st.success("✅ Test mind map created successfully!")
        else:
            st.error("❌ Test mind map creation failed")

def show_training_discovery_page():
    """Training discovery page for onboarding and training needs analysis"""
    st.header("🔍 Training Discovery & Needs Analysis")
    st.markdown("### Comprehensive training assessment and planning tool")
    
    # Initialize session state for tracking progress
    if 'discovery_step' not in st.session_state:
        st.session_state.discovery_step = 1
    if 'training_context' not in st.session_state:
        st.session_state.training_context = {}
    if 'file_inventory' not in st.session_state:
        st.session_state.file_inventory = {}
    if 'collaboration_plan' not in st.session_state:
        st.session_state.collaboration_plan = {}
    if 'mind_map_data' not in st.session_state:
        st.session_state.mind_map_data = {}
    
    # Progress indicator
    steps = ["Training Context", "File Inventory", "Suggested Pathways", "Review & Refine"]
    progress = st.progress((st.session_state.discovery_step - 1) / (len(steps) - 1))
    
    col1, col2, col3, col4, col5 = st.columns(5)
    for i, step in enumerate(steps, 1):
        with [col1, col2, col3, col4, col5][i-1]:
            if i <= st.session_state.discovery_step:
                st.markdown(f"**{i}. {step}** ✅")
            else:
                st.markdown(f"{i}. {step}")
    
    st.markdown("---")
    
    # Step 1: Training Context
    if st.session_state.discovery_step == 1:
        st.subheader("📋 Step 1: Training Context & Requirements")
        st.markdown("### Who, What, When - Training Assessment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👥 **Who** - Target Audience")
            target_audience = st.text_input(
                "Who is the training for?",
                value=st.session_state.training_context.get('target_audience', ''),
                placeholder="e.g., New employees, Department managers, Technical staff"
            )
            
            audience_size = st.number_input(
                "How many people need this training?",
                min_value=1,
                value=st.session_state.training_context.get('audience_size', 10)
            )
            
            audience_level = st.selectbox(
                "Experience level of audience",
                ["Beginner", "Intermediate", "Advanced", "Mixed"],
                index=["Beginner", "Intermediate", "Advanced", "Mixed"].index(
                    st.session_state.training_context.get('audience_level', 'Beginner')
                )
            )
        
        with col2:
            st.markdown("#### 🎯 **What** - Training Objectives")
            training_type = st.selectbox(
                "Type of training needed",
                ["Onboarding", "Skills Development", "Compliance", "Process Training", "Leadership", "Technical", "Other"],
                index=["Onboarding", "Skills Development", "Compliance", "Process Training", "Leadership", "Technical", "Other"].index(
                    st.session_state.training_context.get('training_type', 'Onboarding')
                )
            )
            
            primary_goals = st.text_area(
                "Primary training goals",
                value=st.session_state.training_context.get('primary_goals', ''),
                placeholder="What should learners be able to do after training?"
            )
            
            success_metrics = st.text_area(
                "How will you measure success?",
                value=st.session_state.training_context.get('success_metrics', ''),
                placeholder="e.g., Quiz scores, practical assessments, feedback surveys"
            )
        
        st.markdown("#### ⏰ **When** - Timeline & Urgency")
        col1, col2 = st.columns(2)
        
        with col1:
            timeline = st.selectbox(
                "When is training needed?",
                ["Immediate (1-2 weeks)", "Soon (1 month)", "Flexible (2-3 months)", "Long-term (3+ months)"],
                index=["Immediate (1-2 weeks)", "Soon (1 month)", "Flexible (2-3 months)", "Long-term (3+ months)"].index(
                    st.session_state.training_context.get('timeline', 'Soon (1 month)')
                )
            )
            
            urgency_level = st.selectbox(
                "Urgency level",
                ["Low", "Medium", "High", "Critical"],
                index=["Low", "Medium", "High", "Critical"].index(
                    st.session_state.training_context.get('urgency_level', 'Medium')
                )
            )
        
        with col2:
            industry = st.text_input(
                "Industry/Department",
                value=st.session_state.training_context.get('industry', ''),
                placeholder="e.g., Healthcare, Technology, Finance, HR"
            )
            
            company_size = st.selectbox(
                "Organization size",
                ["Startup (<50)", "Small Business (50-200)", "Medium Business (200-1000)", "Large Enterprise (1000+)"],
                index=["Startup (<50)", "Small Business (50-200)", "Medium Business (200-1000)", "Large Enterprise (1000+)"].index(
                    st.session_state.training_context.get('company_size', 'Small Business (50-200)')
                )
            )
        
        # Save training context
        st.session_state.training_context = {
            'target_audience': target_audience,
            'audience_size': audience_size,
            'audience_level': audience_level,
            'training_type': training_type,
            'primary_goals': primary_goals,
            'success_metrics': success_metrics,
            'timeline': timeline,
            'urgency_level': urgency_level,
            'industry': industry,
            'company_size': company_size
        }
        
        if st.button("Next: File Inventory →", type="primary"):
            st.session_state.discovery_step = 2
            st.rerun()
    
    # Step 2: File Inventory
    elif st.session_state.discovery_step == 2:
        st.subheader("📁 Step 2: Existing Files & Resources")
        st.markdown("### What training materials do you already have?")
        
        st.markdown("#### 📄 Upload Existing Files")
        st.info("Upload any existing training materials, process documents, or related files")
        
        # File upload method selection
        upload_method = st.radio(
            "Choose upload method:",
            ["Standard Upload (≤200MB)", "Backend Upload (Large Files)"],
            help="Use backend upload for files larger than 200MB"
        )
        
        uploaded_files = []
        
        if upload_method == "Standard Upload (≤200MB)":
            uploaded_files = st.file_uploader(
                "Upload existing training materials",
                type=['pdf', 'docx', 'txt', 'pptx', 'xlsx', 'csv', 'mp3', 'wav', 'aac', 'ogg', 'flac', 'mp4', 'mov', 'avi', 'mkv'],
                accept_multiple_files=True,
                help="Supported formats: PDF, Word, PowerPoint, Excel, CSV, Text, Audio, Video"
            )
        else:
            # Backend upload option
            st.info("🔧 Backend upload for large files (requires upload_backend.py to be running)")
            
            # Check if backend is running
            try:
                response = requests.get("http://localhost:8000/", timeout=2)
                if response.status_code == 200:
                    st.success("✅ Backend server is running")
                    
                    # File upload for backend
                    backend_files = st.file_uploader(
                        "Upload large files via backend",
                        type=['pdf', 'docx', 'txt', 'pptx', 'xlsx', 'csv', 'mp3', 'wav', 'aac', 'ogg', 'flac', 'mp4', 'mov', 'avi', 'mkv'],
                        accept_multiple_files=True,
                        help="Large files will be uploaded to backend server"
                    )
                    
                    if backend_files:
                        with st.spinner("Uploading files to backend..."):
                            for file in backend_files:
                                try:
                                    files = {'file': (file.name, file.getvalue(), file.type)}
                                    response = requests.post("http://localhost:8000/upload/", files=files)
                                    if response.status_code == 200:
                                        result = response.json()
                                        st.success(f"✅ {file.name} uploaded successfully ({result['size']} bytes)")
                                        # Don't add to uploaded_files yet - wait for processing
                                    else:
                                        st.error(f"❌ Failed to upload {file.name}: {response.text}")
                                except Exception as e:
                                    st.error(f"❌ Error uploading {file.name}: {str(e)}")
                        
                        # Track backend uploaded files for processing
                        if backend_files:
                            st.success("✅ Files uploaded successfully! They will be processed when you click 'Process Backend Files Now'.")
                            # Store uploaded files in session state for processing
                            if 'backend_uploaded_files' not in st.session_state:
                                st.session_state.backend_uploaded_files = []
                            st.session_state.backend_uploaded_files.extend([f.name for f in backend_files])
                    
                    # Note: Backend storage is available for large file uploads
                    st.info("💡 Backend storage is ready for large file uploads. Files will be processed after upload.")
                    
                    # Show backend files status
                    if st.session_state.get('backend_uploaded_files'):
                        st.success(f"📁 {len(st.session_state.backend_uploaded_files)} files uploaded via backend and ready for processing!")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🔄 Process Backend Files Now"):
                                st.session_state.process_backend_files = True
                                st.rerun()
                        with col2:
                            st.info("💡 After processing, you can generate pathways with your content!")
                    
                    # Process backend files if requested
                    if st.session_state.get('process_backend_files', False):
                        # Check if backend is running first
                        try:
                            response = requests.get("http://localhost:8000/", timeout=2)
                            if response.status_code != 200:
                                st.error("❌ Backend server is not responding properly")
                                st.session_state.process_backend_files = False
                                return
                        except requests.exceptions.ConnectionError:
                            st.error("❌ Backend server is not running. Please start it with: `python upload_backend.py`")
                            st.session_state.process_backend_files = False
                            return
                        
                        with st.spinner("🔄 Downloading and processing backend files..."):
                            try:
                                response = requests.get("http://localhost:8000/files/")
                                if response.status_code == 200:
                                    backend_file_list = response.json().get('files', [])
                                    processed_count = 0
                                    
                                    for i, file_info in enumerate(backend_file_list):
                                        if file_info['filename'] in st.session_state.get('backend_uploaded_files', []):
                                            st.write(f"Processing {i+1}/{len(backend_file_list)}: {file_info['filename']}")
                                            try:
                                                # Download file from backend
                                                download_response = requests.get(f"http://localhost:8000/files/{file_info['filename']}/download")
                                                if download_response.status_code == 200:
                                                    # Create a file-like object
                                                    class BackendFile:
                                                        def __init__(self, name, content, size):
                                                            self.name = name
                                                            self.content = content
                                                            self.size = size
                                                            # Determine file type from extension
                                                            ext = os.path.splitext(name)[1].lower()
                                                            if ext in ['.mp4', '.mov', '.avi', '.mkv']:
                                                                self.type = 'video/mp4'
                                                            elif ext in ['.mp3', '.wav', '.aac', '.ogg', '.flac']:
                                                                self.type = 'audio/mp3'
                                                            elif ext == '.pdf':
                                                                self.type = 'application/pdf'
                                                            elif ext == '.docx':
                                                                self.type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                                                            elif ext == '.txt':
                                                                self.type = 'text/plain'
                                                            else:
                                                                self.type = 'application/octet-stream'
                                                        
                                                        def getvalue(self):
                                                            return self.content
                                                    
                                                    backend_file = BackendFile(
                                                        file_info['filename'], 
                                                        download_response.content,
                                                        file_info['size']
                                                    )
                                                    uploaded_files.append(backend_file)
                                                    processed_count += 1
                                                else:
                                                    st.warning(f"Failed to download {file_info['filename']}")
                                            except Exception as e:
                                                st.warning(f"Error downloading {file_info['filename']}: {str(e)}")
                                    
                                    if processed_count > 0:
                                        st.success(f"✅ Successfully processed {processed_count} backend files!")
                                        # Store processed backend files separately
                                        if 'processed_backend_files' not in st.session_state:
                                            st.session_state.processed_backend_files = []
                                        st.session_state.processed_backend_files.extend(uploaded_files)
                                        # Clear the processing flag and backend files list
                                        st.session_state.process_backend_files = False
                                        st.session_state.backend_uploaded_files = []
                                        st.info("🔄 Backend files have been processed and are ready for pathway generation!")
                                        st.rerun()
                                    else:
                                        st.warning("No files could be processed.")
                                        st.session_state.process_backend_files = False
                                else:
                                    st.error("Failed to fetch backend files.")
                                    st.session_state.process_backend_files = False
                            except Exception as e:
                                st.error(f"Error processing backend files: {str(e)}")
                                st.session_state.process_backend_files = False
                    
                    # Optional: View and process existing backend files
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("👁️ View Files in Backend Storage"):
                            try:
                                response = requests.get("http://localhost:8000/files/")
                                if response.status_code == 200:
                                    backend_file_list = response.json().get('files', [])
                                    if backend_file_list:
                                        st.markdown("#### 📂 Files in Backend Storage")
                                        for file_info in backend_file_list:
                                            col1, col2, col3 = st.columns([3, 1, 1])
                                            with col1:
                                                st.write(f"📄 {file_info['filename']}")
                                            with col2:
                                                st.write(f"{file_info['size']} bytes")
                                            with col3:
                                                if st.button(f"🗑️", key=f"del_{file_info['filename']}"):
                                                    try:
                                                        response = requests.delete(f"http://localhost:8000/files/{file_info['filename']}")
                                                        if response.status_code == 200:
                                                            st.success(f"Deleted {file_info['filename']}")
                                                            st.rerun()
                                                        else:
                                                            st.error(f"Failed to delete {file_info['filename']}")
                                                    except Exception as e:
                                                        st.error(f"Error deleting {file_info['filename']}: {str(e)}")
                                    else:
                                        st.info("No files currently in backend storage.")
                            except Exception as e:
                                st.warning(f"Could not fetch backend files: {str(e)}")
                    
                    with col2:
                        if st.button("🔄 Process Backend Files"):
                            try:
                                response = requests.get("http://localhost:8000/files/")
                                if response.status_code == 200:
                                    backend_file_list = response.json().get('files', [])
                                    if backend_file_list:
                                        st.info(f"Processing {len(backend_file_list)} files from backend...")
                                        
                                        # Download and create proper file objects for processing
                                        for file_info in backend_file_list:
                                            try:
                                                # Download file from backend
                                                download_response = requests.get(f"http://localhost:8000/files/{file_info['filename']}/download")
                                                if download_response.status_code == 200:
                                                    # Create a file-like object
                                                    class BackendFile:
                                                        def __init__(self, name, content, size):
                                                            self.name = name
                                                            self.content = content
                                                            self.size = size
                                                            # Determine file type from extension
                                                            ext = os.path.splitext(name)[1].lower()
                                                            if ext in ['.mp4', '.mov', '.avi', '.mkv']:
                                                                self.type = 'video/mp4'
                                                            elif ext in ['.mp3', '.wav', '.aac', '.ogg', '.flac']:
                                                                self.type = 'audio/mp3'
                                                            elif ext == '.pdf':
                                                                self.type = 'application/pdf'
                                                            elif ext == '.docx':
                                                                self.type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                                                            elif ext == '.txt':
                                                                self.type = 'text/plain'
                                                            else:
                                                                self.type = 'application/octet-stream'
                                                        
                                                        def getvalue(self):
                                                            return self.content
                                                    
                                                    backend_file = BackendFile(
                                                        file_info['filename'], 
                                                        download_response.content,
                                                        file_info['size']
                                                    )
                                                    uploaded_files.append(backend_file)
                                                else:
                                                    st.warning(f"Failed to download {file_info['filename']}")
                                            except Exception as e:
                                                st.warning(f"Error downloading {file_info['filename']}: {str(e)}")
                                        
                                        if uploaded_files:
                                            st.success(f"Added {len(uploaded_files)} files for processing!")
                                            st.rerun()
                                        else:
                                            st.warning("No files could be downloaded for processing.")
                                    else:
                                        st.info("No files in backend storage to process.")
                                else:
                                    st.error("Failed to fetch backend files.")
                            except Exception as e:
                                st.error(f"Error processing backend files: {str(e)}")
                        
                else:
                    st.error("❌ Backend server responded with error")
            except requests.exceptions.ConnectionError:
                st.error("❌ Backend server not running. Start it with: `python upload_backend.py`")
                st.code("python upload_backend.py")
            except Exception as e:
                st.error(f"❌ Error connecting to backend: {str(e)}")
        
        # File categorization
        extracted_file_contents = {}
        
        # Combine regular uploaded files with processed backend files
        all_files_to_process = uploaded_files.copy()
        if st.session_state.get('processed_backend_files'):
            all_files_to_process.extend(st.session_state.processed_backend_files)
        
        if all_files_to_process:
            st.markdown("#### 📂 Categorize Your Files")
            file_categories = {}
            for uploaded_file in all_files_to_process:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📄 {uploaded_file.name}")
                with col2:
                    category = st.selectbox(
                        f"Category for {uploaded_file.name}",
                        ["Process Documentation", "Training Materials", "Policies & Procedures", "Technical Guides", "User Manuals", "Other"],
                        key=f"cat_{uploaded_file.name}"
                    )
                    file_categories[uploaded_file.name] = category
                # --- Extract text from file ---
                file_text = ""
                mime_type, _ = mimetypes.guess_type(uploaded_file.name)
                if uploaded_file.type == "application/pdf":
                    try:
                        pdf_reader = PyPDF2.PdfReader(uploaded_file)
                        for page in pdf_reader.pages:
                            file_text += page.extract_text() or ""
                    except Exception as e:
                        file_text = f"[Error extracting PDF: {e}]"
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    try:
                        doc = Document(uploaded_file)
                        for paragraph in doc.paragraphs:
                            file_text += paragraph.text + "\n"
                    except Exception as e:
                        file_text = f"[Error extracting DOCX: {e}]"
                elif uploaded_file.type == "text/plain":
                    try:
                        file_text = uploaded_file.getvalue().decode(errors="ignore")
                    except Exception as e:
                        file_text = f"[Error extracting TXT: {e}]"
                elif uploaded_file.type.startswith("audio/"):
                    try:
                        # Save audio to temp file
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[-1]) as tmp_audio:
                            tmp_audio.write(uploaded_file.getvalue())
                            tmp_audio_path = tmp_audio.name
                        # Transcribe with Gemini
                        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                        model = genai.GenerativeModel('gemini-2.0-flash-exp')
                        with open(tmp_audio_path, 'rb') as audio_file:
                            response = model.generate_content([
                                "Generate a transcript of the speech.",
                                {"mime_type": "audio/wav", "data": audio_file.read()}
                            ])
                        file_text = response.text
                        os.unlink(tmp_audio_path)
                    except Exception as e:
                        file_text = f"[Error transcribing audio: {e}]"
                elif uploaded_file.type.startswith("video/") or (mime_type and mime_type.startswith("video/")):
                    if ffmpeg is None:
                        file_text = "[ffmpeg-python not installed. Cannot extract audio from video.]"
                    else:
                        try:
                            # Save video to temp file
                            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[-1]) as tmp_video:
                                tmp_video.write(uploaded_file.getvalue())
                                tmp_video_path = tmp_video.name
                            # Extract audio to temp file
                            tmp_audio_path = tmp_video_path + ".audio.wav"
                            (
                                ffmpeg
                                .input(tmp_video_path)
                                .output(tmp_audio_path, format='wav', acodec='pcm_s16le', ac=1, ar='16k')
                                .overwrite_output()
                                .run(quiet=True)
                            )
                            # Transcribe with Gemini
                            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                            model = genai.GenerativeModel('gemini-2.0-flash-exp')
                            with open(tmp_audio_path, 'rb') as audio_file:
                                response = model.generate_content([
                                    "Generate a transcript of the speech.",
                                    {"mime_type": "audio/wav", "data": audio_file.read()}
                                ])
                            file_text = response.text
                            os.unlink(tmp_video_path)
                            os.unlink(tmp_audio_path)
                        except Exception as e:
                            file_text = f"[Error extracting/transcribing video: {e}]"
                else:
                    file_text = "[Unsupported file type for extraction]"
                extracted_file_contents[uploaded_file.name] = file_text
            
            # Update session state with file information
            if 'file_inventory' not in st.session_state:
                st.session_state.file_inventory = {}
            st.session_state.file_inventory.update({
                'uploaded_files': [f.name for f in all_files_to_process],
                'file_categories': file_categories
            })
            # Store extracted text for pathway generation
            st.session_state['extracted_file_contents'] = extracted_file_contents
        
        # Always show manual file inventory section
        st.markdown("#### 🔍 Manual File Inventory")
        st.markdown("If you have files that can't be uploaded, list them here:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            process_docs = st.text_area(
                "Process Documentation",
                value=st.session_state.get('file_inventory', {}).get('process_docs', ''),
                placeholder="List any process documents, SOPs, workflows..."
            )
            
            training_materials = st.text_area(
                "Existing Training Materials",
                value=st.session_state.get('file_inventory', {}).get('training_materials', ''),
                placeholder="List any existing training videos, presentations, guides..."
            )
        
        with col2:
            policies = st.text_area(
                "Policies & Procedures",
                value=st.session_state.get('file_inventory', {}).get('policies', ''),
                placeholder="List any relevant policies, procedures, guidelines..."
            )
            
            technical_docs = st.text_area(
                "Technical Documentation",
                value=st.session_state.get('file_inventory', {}).get('technical_docs', ''),
                placeholder="List any technical guides, user manuals, system docs..."
            )
        
        # Save manual inventory
        if 'file_inventory' not in st.session_state:
            st.session_state.file_inventory = {}
        st.session_state.file_inventory.update({
            'process_docs': process_docs,
            'training_materials': training_materials,
            'policies': policies,
            'technical_docs': technical_docs
        })
        
        # Show current inventory summary
        st.markdown("#### 📋 Current Inventory Summary")
        inventory_summary = []
        if st.session_state.file_inventory.get('uploaded_files'):
            inventory_summary.append(f"**Uploaded Files:** {len(st.session_state.file_inventory['uploaded_files'])} files")
        if st.session_state.file_inventory.get('process_docs'):
            inventory_summary.append("**Process Docs:** ✓ Added")
        if st.session_state.file_inventory.get('training_materials'):
            inventory_summary.append("**Training Materials:** ✓ Added")
        if st.session_state.file_inventory.get('policies'):
            inventory_summary.append("**Policies:** ✓ Added")
        if st.session_state.file_inventory.get('technical_docs'):
            inventory_summary.append("**Technical Docs:** ✓ Added")
        
        if inventory_summary:
            for item in inventory_summary:
                st.markdown(f"• {item}")
        else:
            st.info("No inventory items added yet. Please upload files or add manual inventory.")
        
        # Show pathway generation button if files are available
        if all_files_to_process or any([
            st.session_state.file_inventory.get('process_docs'),
            st.session_state.file_inventory.get('training_materials'),
            st.session_state.file_inventory.get('policies'),
            st.session_state.file_inventory.get('technical_docs')
        ]):
            st.markdown("---")
            st.markdown("### 🛤️ Ready to Generate Pathways")
            st.markdown("You have files and content available. Generate AI-powered pathways based on your content!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("← Back to Training Context"):
                    st.session_state.discovery_step = 1
                    st.rerun()
            
            with col2:
                if st.button("🤖 Generate Pathways Now", type="primary"):
                    st.session_state.discovery_step = 3
                    st.rerun()
        
            with col3:
                st.info("💡 Your files will be processed and used to generate contextual pathways")
        else:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back to Training Context"):
                    st.session_state.discovery_step = 1
                    st.rerun()
            
            with col2:
                if st.button("Next: Suggested Pathways →", type="primary"):
                    st.session_state.discovery_step = 3
                    st.rerun()
        
        # --- SUGGESTED PATHWAYS SECTION (moved to its own step) ---

    # Step 3: Suggested Pathways (new step, replaces Collaboration Planning and Mind Map)
    elif st.session_state.discovery_step == 3:
        st.subheader("🛤️ Suggested Pathways")
        context = st.session_state.get('training_context', {})
        inventory = st.session_state.get('file_inventory', {})
        extracted_file_contents = st.session_state.get('extracted_file_contents', {})
        
        # Debug information
        st.markdown("**Debug Info:**")
        st.write(f"Training Context: {context}")
        st.write(f"File Inventory: {inventory}")
        st.write(f"Extracted Files: {list(extracted_file_contents.keys())}")
        
        # Show extracted content from files
        if extracted_file_contents:
            with st.expander("📄 View Extracted Content from Files"):
                st.markdown("**Content that will be used to generate modules:**")
                for filename, content in extracted_file_contents.items():
                    if content and len(content.strip()) > 50:
                        st.markdown(f"### {filename}")
                        st.markdown(f"**Content Preview:** {content[:500]}...")
                        st.markdown("---")
        
        # Check if we need to regenerate pathway due to new files
        # Include both regular uploaded files and processed backend files
        all_files = list(extracted_file_contents.keys())
        if st.session_state.get('processed_backend_files'):
            all_files.extend([f.name for f in st.session_state.processed_backend_files])
        
        current_file_count = len(set(all_files))  # Remove duplicates
        if 'last_file_count' not in st.session_state:
            st.session_state['last_file_count'] = 0
        
        # If new files were added, clear the generated pathway to force regeneration
        if current_file_count > st.session_state['last_file_count'] and 'generated_pathway' in st.session_state:
            st.info("🔄 New files detected! You may want to regenerate your pathway to include the new content.")
            if st.button("🔄 Regenerate Pathway with New Files"):
                del st.session_state['generated_pathway']
                del st.session_state['editable_pathways']
                st.session_state['last_file_count'] = current_file_count
                st.rerun()
        
        # Update file count
        st.session_state['last_file_count'] = current_file_count
        
        # --- Always show pathway generation section ---
        st.markdown("### Generate Your Pathway")
        st.markdown("Click the button below to generate a pathway using AI based on your training context and content.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🤖 Generate Pathway with AI", type="primary"):
                with st.spinner("🤖 Generating pathway with AI..."):
                    from modules.utils import gemini_generate_complete_pathway
                    try:
                        generated_pathway = gemini_generate_complete_pathway(context, extracted_file_contents, inventory)
                        if generated_pathway:
                            st.session_state['generated_pathway'] = generated_pathway
                            
                            # Count modules extracted from files
                            total_modules = sum(len(section.get('modules', [])) for section in generated_pathway.get('sections', []))
                            st.success(f"✅ Pathway generated successfully! Created {total_modules} modules from your uploaded content.")
                            
                            # Show which files contributed to the pathway
                            if extracted_file_contents:
                                st.info(f"📁 Modules were generated from {len(extracted_file_contents)} files including video transcriptions and document content.")
                            
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error during AI pathway generation: {str(e)}")
                        st.markdown("**Troubleshooting:**")
                        st.markdown("- Make sure you've filled out the training context")
                        st.markdown("- Ensure you have uploaded files or provided manual inventory")
                        st.markdown("- Check that your Gemini API key is valid")
                        if st.button("Retry AI Generation"):
                            st.rerun()
        
        with col2:
            st.markdown("**AI-Powered Pathways**")
            st.markdown("All pathways are generated using AI to ensure they are:")
            st.markdown("• Contextually relevant to your industry")
            st.markdown("• Tailored to your target audience")
            st.markdown("• Based on your specific content")
            st.markdown("• Adaptable to your company size")
        
        # If no pathway generated yet, show message and return
        if 'generated_pathway' not in st.session_state:
            st.info("👆 Click the 'Generate Pathway with AI' button above to create your pathway.")
            return
        
        # --- Display generated pathway ---
        if 'generated_pathway' not in st.session_state:
            st.error("No pathway generated yet. Please click the 'Generate Pathway with AI' button above.")
            return
        
        generated_pathway = st.session_state['generated_pathway']
        pathway_name = generated_pathway['pathway_name']
        
        # --- Convert Gemini pathway to editable format ---
        if 'editable_pathways' not in st.session_state:
            editable_pathways = {}
            for section in generated_pathway['sections']:
                section_title = section['title']
                editable_pathways[section_title] = []
                for module in section['modules']:
                    editable_pathways[section_title].append({
                        'title': module['title'],
                        'description': module['description'],
                        'content': module.get('content', ''),
                        'source': ['AI Generated']
                    })
            st.session_state['editable_pathways'] = editable_pathways
        
        editable_pathways = st.session_state['editable_pathways']
        
        # Display pathway information
        st.markdown(f"### 🎯 **{pathway_name}**")
        st.markdown("This AI-generated pathway is designed based on your training context and available content.")
        
        # Pathways UI navigation state
        if 'selected_pathway' not in st.session_state:
            st.session_state['selected_pathway'] = None
        if 'selected_section' not in st.session_state:
            st.session_state['selected_section'] = None
        
        # Show pathway card (for now, only one pathway)
        pathway_names = [pathway_name]  # For future: support multiple pathways
        cols = st.columns(len(pathway_names))
        for idx, pname in enumerate(pathway_names):
            with cols[idx]:
                if st.button(f"Pathway {idx+1}: {pname}", key=f"pathway_card_{idx}"):
                    st.session_state['selected_pathway'] = pname
                    st.session_state['selected_section'] = None
        
        # Show sections if pathway selected
        if st.session_state['selected_pathway']:
            st.markdown(f"### Sections in Pathway {pathway_names.index(st.session_state['selected_pathway'])+1}: {st.session_state['selected_pathway']}")
            section_names = list(editable_pathways.keys())
            
            # Display sections with descriptions
            for idx, section in enumerate(section_names):
                # Find section description from generated pathway
                section_desc = ""
                for gen_section in generated_pathway['sections']:
                    if gen_section['title'] == section:
                        section_desc = gen_section.get('description', '')
                        break
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Section {idx+1}: {section}**")
                    if section_desc:
                        st.markdown(f"*{section_desc}*")
                with col2:
                    if st.button(f"View Modules", key=f"section_card_{section}"):
                        st.session_state['selected_section'] = section
                st.markdown("---")
        
        # Show modules if section selected
        if st.session_state['selected_section']:
            section = st.session_state['selected_section']
            mods = editable_pathways[section]
            section_idx = list(editable_pathways.keys()).index(section) + 1
            st.markdown(f"### Modules in Section {section_idx}: {section}")
            i = 0
            while i < len(mods):
                mod = mods[i]
                col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
                with col1:
                    new_title = st.text_input(f"Title ({section}-{i})", mod['title'], key=f"title_{section}_{i}")
                    new_desc = st.text_input(f"Description ({section}-{i})", mod.get('description', ''), key=f"desc_{section}_{i}")
                    new_content = st.text_area(f"Content ({section}-{i})", mod['content'], key=f"content_{section}_{i}")
                    st.markdown(f"**{i+1}. {new_title}**")
                with col2:
                    if st.button("⬆️", key=f"up_{section}_{i}") and i > 0:
                        mods[i-1], mods[i] = mods[i], mods[i-1]
                        st.session_state['editable_pathways'] = editable_pathways
                        st.experimental_rerun()
                    if st.button("⬇️", key=f"down_{section}_{i}") and i < len(mods)-1:
                        mods[i+1], mods[i] = mods[i], mods[i+1]
                        st.session_state['editable_pathways'] = editable_pathways
                        st.experimental_rerun()
                with col3:
                    if st.button("🗑️ Delete", key=f"del_{section}_{i}"):
                        mods.pop(i)
                        st.session_state['editable_pathways'] = editable_pathways
                        st.experimental_rerun()
                with col4:
                    move_to_section = st.selectbox(
                        "Move to section",
                        section_names,
                        index=section_names.index(section),
                        key=f"move_{section}_{i}"
                    )
                    if move_to_section != section:
                        editable_pathways[move_to_section].append(mod)
                        mods.pop(i)
                        st.session_state['editable_pathways'] = editable_pathways
                        st.experimental_rerun()
                mod['title'] = new_title
                mod['description'] = new_desc
                mod['content'] = new_content
                st.markdown(f"_Description: {mod['description']}_")
                st.markdown(f"_Source: {', '.join(mod['source'])}_")
                            st.markdown("---")
                i += 1
            
        # --- Export and Save Buttons ---
        st.markdown("---")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button("← Back to File Upload"):
                st.session_state.discovery_step = 2
                st.rerun()
        
        with col2:
            if st.button("🔄 Regenerate Pathway"):
                del st.session_state['generated_pathway']
                del st.session_state['editable_pathways']
                st.rerun()
        
        with col3:
            if st.button("🤖 Generate New Pathway"):
                del st.session_state['generated_pathway']
                del st.session_state['editable_pathways']
                st.rerun()
        
        with col4:
            if st.button("Export Pathways as JSON"):
                import json
                export_data = {
                    'pathway': pathway_name,
                    'sections': [
                        {
                            'name': section,
                            'modules': [
                                {'title': m['title'], 'content': m['content'], 'source': m['source']}
                                for m in mods
                            ]
                        } for section, mods in editable_pathways.items()
                    ]
                }
                json_str = json.dumps(export_data, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"onboarding_pathways_{pathway_name.replace(' ', '_')}.json",
                    mime="application/json"
                )
        with col5:
            if st.button("Save Pathways"):
                st.session_state['confirmed_pathways'] = {
                    'pathway': pathway_name,
                    'sections': [
                        {
                            'name': section,
                            'modules': [
                                {'title': m['title'], 'content': m['content'], 'source': m['source']}
                                for m in mods
                            ]
                        } for section, mods in editable_pathways.items()
                    ]
                }
                st.success("Pathways saved! You can now generate multimedia content.")
                st.session_state['show_generate_multimedia'] = True
        
        if st.session_state.get('show_generate_multimedia') and st.session_state.get('confirmed_pathways'):
            if st.button("Generate Multimedia Content for Modules"):
                st.session_state['generate_multimedia_triggered'] = True
        
        if st.session_state.get('generate_multimedia_triggered'):
            st.markdown("---")
            st.subheader("🎬 Multimedia Content Generation (Coming Soon)")
            st.info("The app will generate multimedia content for each module in your confirmed pathways. Stay tuned!")

def show_mind_maps_page():
    """Mind maps page with Markmap only (MindMeister removed)"""
    st.header("🧠 Pathways & Markmap Visualization")
    st.markdown("Suggested pathways and module visualization.")
    
    # Only Markmap tab remains
    st.subheader("🗺️ Markmap Component")
    st.markdown("Test the local markmap component with sample data")
    
    # Sample markdown for testing
    sample_markdown = """# Training Program Overview\n## Frontend Development\n- React Components\n  - Navigation\n  - Forms\n  - Charts\n- Styling\n  - CSS Modules\n  - Tailwind CSS\n## Backend Development\n- API Endpoints\n  - Authentication\n  - Data CRUD\n- Database\n  - PostgreSQL\n  - Redis Cache\n## DevOps & Deployment\n- CI/CD Pipeline\n- Docker Containers\n- Cloud Deployment"""
    
    st.markdown("**Sample Markdown Data:**")
    st.code(sample_markdown, language="markdown")
    
    if st.button("🎯 Test Markmap Component", type="primary"):
        st.markdown("**Rendered Mind Map:**")
        markmap(sample_markdown, height=600)
        st.success("✅ Markmap component test completed!")

def show_video_generation_page():
    """Video generation page"""
    st.header("📹 AI Video Generation")
    st.info("Video generation features coming soon...")
    
    # Placeholder for video generation functionality
    st.markdown("""
    This section will include:
    - **Vadoo AI Integration** - Generate training videos
    - **Canva Veo3 Integration** - Create professional video content
    - **Custom video templates** - Industry-specific video styles
    - **Voice-over generation** - AI-powered narration
    """)

def show_document_processing_page():
    """Document processing page"""
    st.header("📄 Document Processing")
    st.info("Document processing features coming soon...")
    
    # Placeholder for document processing functionality
    st.markdown("""
    This section will include:
    - **PDF processing** - Extract and analyze content
    - **Word document processing** - Parse training materials
    - **Content analysis** - AI-powered insights
    - **Document summarization** - Key points extraction
    """)

def show_settings_page():
    """Settings page for configuration"""
    st.header("⚙️ Settings & Configuration")
    
    st.subheader("🔑 API Configuration")
    
    # Check current configuration
    config_status = {
        "Gemini API": "✅ Configured" if api_key and api_key != "your_gemini_api_key_here" else "❌ Not configured",
        "MindMeister": "✅ Configured" if MINDMEISTER_CLIENT_ID else "❌ Not configured",
        "Vadoo AI": "✅ Configured" if VADOO_API_KEY else "❌ Not configured",
        "Canva": "✅ Configured" if CANVA_API_KEY else "❌ Not configured"
    }
    
    for service, status in config_status.items():
        st.write(f"{service}: {status}")
    
    st.subheader("📝 Environment Variables")
    st.info("""
    Configure your API keys in the `.env` file:
    
    ```
    GEMINI_API_KEY=your_gemini_api_key_here
    MINDMEISTER_CLIENT_ID=your_mindmeister_client_id_here
    MINDMEISTER_CLIENT_SECRET=your_mindmeister_client_secret_here
    MINDMEISTER_REDIRECT_URI=https://localhost:8501
    VADOO_API_KEY=your_vadoo_api_key_here
    CANVA_API_KEY=your_canva_api_key_here
    ```
    """)

if __name__ == "__main__":
    main() 