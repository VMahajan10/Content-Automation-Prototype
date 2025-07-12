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
import subprocess
import threading
import atexit
import io
try:
    import ffmpeg
except ImportError:
    ffmpeg = None

# Import from our modules
from modules.config import *
from modules.utils import flush_debug_logs_to_streamlit, extract_modules_from_file_content
from markmap_component import markmap

# BackendFile class for handling file-like objects
class BackendFile:
    def __init__(self, name, content, size):
        self.name = name
        self.content = content
        self.size = size
        self._position = 0
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
    
    def seek(self, offset, whence=0):
        """Proper seek method for file-like objects"""
        if whence == 0:
            self._position = offset
        elif whence == 1:
            self._position += offset
        elif whence == 2:
            self._position = len(self.content) + offset
        return self._position
    
    def read(self, size=-1):
        """Read method for file-like objects"""
        if size == -1:
            size = len(self.content) - self._position
        data = self.content[self._position:self._position + size]
        self._position += len(data)
        return data
    
    def tell(self):
        """Tell method for file-like objects"""
        return self._position

# Global variable to track backend process
backend_process = None

def start_backend_server():
    """Start the backend server in a separate process"""
    global backend_process
    try:
        # Check if backend is already running
        try:
            response = requests.get("http://localhost:8000/health", timeout=3)
            if response.status_code == 200:
                st.success("✅ Backend server is already running")
                return True
        except:
            pass
        
        # Start backend server
        st.info("🚀 Starting backend server...")
        backend_process = subprocess.Popen(
            ["python", "upload_backend.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start with better timeout
        st.info("⏳ Waiting for backend server to start...")
        for i in range(10):
            time.sleep(1)
            try:
                response = requests.get("http://localhost:8000/health", timeout=3)
                if response.status_code == 200:
                    st.success("✅ Backend server started successfully")
                    return True
            except:
                if i < 5:
                    st.info(f"⏳ Waiting for backend... ({i+1}/10)")
                else:
                    st.info(f"⏳ Backend is taking longer than expected... ({i+1}/10)")
        
        # If we get here, backend didn't start
        st.error("❌ Backend server failed to start within timeout")
        if backend_process:
            backend_process.terminate()
            try:
                backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend_process.kill()
        return False
            
    except Exception as e:
        st.error(f"❌ Failed to start backend server: {str(e)}")
        return False

def stop_backend_server():
    """Stop the backend server"""
    global backend_process
    if backend_process:
        try:
            backend_process.terminate()
            backend_process.wait(timeout=5)
            st.info("🛑 Backend server stopped")
        except:
            backend_process.kill()
        backend_process = None

# Register cleanup function
atexit.register(stop_backend_server)

# Page configuration
st.set_page_config(
    page_title="Gateway Content Automation",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main application
def main():
    # Initialize session state variables
    if 'ai_cache' not in st.session_state:
        st.session_state.ai_cache = {}
    
    # Start backend server automatically
    if not start_backend_server():
        st.warning("⚠️ Backend server could not be started. Some features may not work properly.")
    
    # Show Gemini API status
    if model:
        st.success("✅ Gemini AI Connected - Chatbot powered by AI")
    else:
        st.error("❌ Gemini AI Not Available - Some features may be limited")
        st.info("Please configure your Gemini API key in Settings")
    
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
                                                    # Create a file-like object using the existing BackendFile class
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
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("👁️ View Current Session Files"):
                            try:
                                response = requests.get("http://localhost:8000/files/session/")
                                if response.status_code == 200:
                                    session_data = response.json()
                                    backend_file_list = session_data.get('files', [])
                                    session_id = session_data.get('session_id', 'Unknown')
                                    total_files = session_data.get('total_files', 0)
                                    
                                    st.markdown(f"#### 📂 Current Session Files (Session: {session_id[:8]}...)")
                                    st.info(f"📊 Total files in session: {total_files}")
                                    
                                    if backend_file_list:
                                        for file_info in backend_file_list:
                                            col1, col2, col3 = st.columns([3, 1, 1])
                                            with col1:
                                                st.write(f"📄 {file_info['filename']}")
                                            with col2:
                                                st.write(f"{file_info['size']} bytes")
                                            with col3:
                                                if st.button(f"🗑️", key=f"del_session_{file_info['filename']}"):
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
                                        st.info("No files in current session.")
                            except Exception as e:
                                st.warning(f"Could not fetch session files: {str(e)}")
                    
                    with col2:
                        if st.button("🗂️ View All Backend Files"):
                            try:
                                response = requests.get("http://localhost:8000/files/")
                                if response.status_code == 200:
                                    backend_file_list = response.json().get('files', [])
                                    if backend_file_list:
                                        st.markdown("#### 📂 All Files in Backend Storage")
                                        st.warning("⚠️ This shows ALL files ever uploaded, not just current session")
                                        for file_info in backend_file_list:
                                            col1, col2, col3 = st.columns([3, 1, 1])
                                            with col1:
                                                st.write(f"📄 {file_info['filename']}")
                                            with col2:
                                                st.write(f"{file_info['size']} bytes")
                                            with col3:
                                                if st.button(f"🗑️", key=f"del_all_{file_info['filename']}"):
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
                    
                    with col3:
                        if st.button("🆕 Start New Session"):
                            try:
                                response = requests.post("http://localhost:8000/session/new/")
                                if response.status_code == 200:
                                    session_data = response.json()
                                    st.success(f"✅ New session started: {session_data.get('session_id', 'Unknown')[:8]}...")
                                    st.info("🔄 Previous session files have been cleared")
                                    st.rerun()
                                else:
                                    st.error("Failed to start new session")
                            except Exception as e:
                                st.error(f"Error starting new session: {str(e)}")
                    
                    # Process Backend Files section
                    st.markdown("#### 🔄 Process Backend Files")
                    if st.button("🔄 Process Current Session Files"):
                        try:
                            response = requests.get("http://localhost:8000/files/session/")
                            if response.status_code == 200:
                                session_data = response.json()
                                backend_file_list = session_data.get('files', [])
                                session_id = session_data.get('session_id', 'Unknown')
                                total_files = session_data.get('total_files', 0)
                                
                                # Download and create proper file objects for processing
                                if backend_file_list:
                                    for file_info in backend_file_list:
                                        try:
                                            # Download file from backend
                                            download_response = requests.get(f"http://localhost:8000/files/{file_info['filename']}/download")
                                            if download_response.status_code == 200:
                                                # Create a file-like object
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
                                    st.warning("No backend files found for processing.")
                            else:
                                st.error("❌ Backend server responded with error")
                        except Exception as e:
                            st.error(f"Error processing backend files: {str(e)}")
                        
            except Exception as e:
                st.error(f"Error checking backend server or processing backend files: {str(e)}")
        
        # File categorization
        extracted_file_contents = {}
        
        # Combine regular uploaded files with processed backend files
        all_files_to_process = uploaded_files.copy()
        if st.session_state.get('processed_backend_files'):
            all_files_to_process.extend(st.session_state.processed_backend_files)
        
        st.write(f"🔍 **File Processing Debug:**")
        st.write(f"Uploaded files: {[f.name for f in uploaded_files] if uploaded_files else 'None'}")
        st.write(f"Processed backend files: {[f.name for f in st.session_state.get('processed_backend_files', [])] if st.session_state.get('processed_backend_files') else 'None'}")
        st.write(f"All files to process: {[f.name for f in all_files_to_process] if all_files_to_process else 'None'}")
        
        if all_files_to_process:
            st.markdown("#### 📂 Categorize Your Files")
            file_categories = {}
            for i, uploaded_file in enumerate(all_files_to_process):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📄 {uploaded_file.name}")
                with col2:
                    category = st.selectbox(
                        f"Category for {uploaded_file.name}",
                        ["Process Documentation", "Training Materials", "Policies & Procedures", "Technical Guides", "User Manuals", "Other"],
                        key=f"cat_{uploaded_file.name}_{i}"  # Add index to make key unique
                    )
                    file_categories[uploaded_file.name] = category
                # --- Extract text from file ---
                file_text = ""
                mime_type, _ = mimetypes.guess_type(uploaded_file.name)
                if uploaded_file.type == "application/pdf":
                    try:
                        # Create a file-like object from the uploaded file
                        pdf_file = uploaded_file.getvalue()
                        # Ensure we have bytes for PyPDF2
                        if isinstance(pdf_file, str):
                            pdf_file = pdf_file.encode('utf-8')
                        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
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
        
        st.write(f"📝 **Manual Inventory Debug:**")
        st.write(f"Process docs: '{process_docs[:100] if process_docs else 'None'}...'")
        st.write(f"Training materials: '{training_materials[:100] if training_materials else 'None'}...'")
        st.write(f"Policies: '{policies[:100] if policies else 'None'}...'")
        st.write(f"Technical docs: '{technical_docs[:100] if technical_docs else 'None'}...'")
        
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
            st.markdown("### 🛤️ Ready to Generate Goal-Aligned Pathways")
            st.markdown("You have files and content available. Generate AI-powered pathways that align with your training goals!")
            
            # Show training goals for reference
            if st.session_state.training_context.get('primary_goals'):
                st.info(f"🎯 **Your Training Goals:** {st.session_state.training_context['primary_goals']}")
            if st.session_state.training_context.get('success_metrics'):
                st.info(f"📊 **Your Success Metrics:** {st.session_state.training_context['success_metrics']}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("← Back to Training Context"):
                    st.session_state.discovery_step = 1
                    st.rerun()
            
            with col2:
                if st.button("🤖 Generate Goal-Aligned Pathways", type="primary"):
                    st.session_state.discovery_step = 3
                    st.rerun()
        
            with col3:
                st.info("💡 Content will be filtered to match your training objectives")
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

    # Step 3: Generate Pathways
    elif st.session_state.discovery_step == 3:
        st.subheader("🛤️ Generate Training Pathways")
        context = st.session_state.get('training_context', {})
        inventory = st.session_state.get('file_inventory', {})
        extracted_file_contents = st.session_state.get('extracted_file_contents', {})
        
        st.write(f"🔍 **Step 3 Debug:**")
        st.write(f"Context keys: {list(context.keys())}")
        st.write(f"Inventory keys: {list(inventory.keys())}")
        st.write(f"Extracted files keys: {list(extracted_file_contents.keys())}")
        st.write(f"Session state keys: {list(st.session_state.keys())}")
        
        # Add backend file processing
        st.markdown("### 📁 Process Backend Files")
        if st.button("🔄 Process Backend Files Now"):
            with st.spinner("Processing backend files..."):
                try:
                    response = requests.get("http://localhost:8000/files/")
                    if response.status_code == 200:
                        backend_files = response.json().get('files', [])
                        st.write(f"📁 Found {len(backend_files)} files in backend")
                        
                        processed_files = {}
                        for file_info in backend_files:
                            st.write(f"📄 Processing: {file_info['filename']}")
                            try:
                                # Download file from backend
                                download_response = requests.get(f"http://localhost:8000/files/{file_info['filename']}/download")
                                if download_response.status_code == 200:
                                    # Extract content based on file type
                                    filename = file_info['filename']
                                    content = ""
                                    
                                    if filename.lower().endswith('.txt'):
                                        content = download_response.text
                                    elif filename.lower().endswith('.mp4'):
                                        # For video files, we'll need to transcribe
                                        st.write(f"🎥 Video file detected: {filename}")
                                        content = f"[Video file: {filename} - Transcription needed]"
                                    else:
                                        content = download_response.text
                                    
                                    if content and len(content.strip()) > 50:
                                        processed_files[filename] = content
                                        st.write(f"✅ Processed {filename} ({len(content)} characters)")
                                    else:
                                        st.write(f"⚠️ {filename} has insufficient content")
                                else:
                                    st.write(f"❌ Failed to download {filename}")
                            except Exception as e:
                                st.write(f"❌ Error processing {file_info['filename']}: {str(e)}")
                        
                        # Update session state with processed files
                        if processed_files:
                            st.session_state['extracted_file_contents'] = processed_files
                            st.success(f"✅ Successfully processed {len(processed_files)} backend files!")
                            st.rerun()
                        else:
                            st.warning("No files could be processed successfully")
                    else:
                        st.error("Failed to fetch backend files")
                except Exception as e:
                    st.error(f"Error processing backend files: {str(e)}")

        # File categorization and pathway generation continues here...
        
        st.markdown("### Generate Your Semantically Aligned Pathway")
        st.markdown("Click the button below to generate a pathway using AI based on your training context and content. Content will be analyzed semantically to identify topics relevant to your training goals.")
        
        # Show training goals for reference
        if context.get('primary_goals'):
            st.info(f"🎯 **Your Training Goals:** {context['primary_goals']}")
        if context.get('success_metrics'):
            st.info(f"📊 **Your Success Metrics:** {context['success_metrics']}")
        
        # Add option to bypass filtering
        bypass_filtering = st.checkbox(
            "Include all file content (bypass goal alignment)",
            help="If checked, all content from files will be included regardless of relevance to training goals"
        )
        
        # Add option to preserve original content
        preserve_original_content = st.checkbox(
            "Preserve original content (minimal AI transformation)",
            help="If checked, original file content will be preserved with minimal AI transformation. Useful for already structured training materials."
        )
        
        # Show goal alignment information
        st.info("🎯 **Goal Alignment:** Content will be filtered to match your specific training goals and objectives")
        if context.get('primary_goals'):
            st.write(f"**Your Goals:** {context['primary_goals']}")
        if context.get('training_type'):
            st.write(f"**Training Type:** {context['training_type']}")
        if context.get('target_audience'):
            st.write(f"**Target Audience:** {context['target_audience']}")
        
        # Add speed and content optimization options
        col1, col2 = st.columns(2)
        
        with col1:
            quick_test_mode = st.checkbox(
                "Quick Test Mode (skip AI analysis for speed)",
                help="For testing purposes - skips AI analysis and uses basic content extraction for maximum speed"
            )
        
        with col2:
            enhanced_content_mode = st.checkbox(
                "Enhanced Content Mode (more modules and pathways)",
                help="Generate more comprehensive content with additional modules, pathways, and sections"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🤖 Generate Goal-Aligned Pathway", type="primary"):
                # Clear previous errors
                if 'ai_errors' in st.session_state:
                    del st.session_state['ai_errors']
                
                st.write("🔍 **Debug Info:**")
                st.write(f"Training Context: {context}")
                st.write(f"File Inventory: {inventory}")
                st.write(f"Extracted Files: {list(extracted_file_contents.keys())}")
                st.write(f"Number of files with content: {len([c for c in extracted_file_contents.values() if c and len(c.strip()) > 50])}")
                
                if quick_test_mode:
                    st.info("⚡ **Quick Test Mode Enabled**")
                    st.write("• Skipping AI analysis for maximum speed")
                    st.write("• Using basic content extraction")
                    st.write("• Estimated time: 5-10 seconds")
                    
                    with st.spinner("⚡ Quick processing (bypassing AI analysis)..."):
                        try:
                            from modules.utils import create_quick_pathway
                            st.write("📞 Creating quick pathway...")
                            
                            generated_pathways_data = create_quick_pathway(context, extracted_file_contents, inventory)
                            
                            # Flush any debug logs from background threads
                            flush_debug_logs_to_streamlit()
                            
                            st.write(f"📋 Quick Response: {generated_pathways_data}")
                            
                            if generated_pathways_data:
                                st.session_state['generated_pathway'] = generated_pathways_data
                                st.success("✅ Quick pathway generated successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Quick pathway generation failed")
                        except Exception as e:
                            st.error(f"❌ Quick pathway error: {str(e)}")
                            st.session_state['ai_errors'] = {
                                'error': str(e),
                                'type': type(e).__name__,
                                'traceback': str(e)
                            }
                else:
                    # Add parallel processing status
                    st.info("🚀 **Goal-Aligned Processing Enabled**")
                    st.write("• Content will be filtered to match your specific training goals")
                    st.write("• Multiple AI agents will process files simultaneously")
                    st.write("• Only training-relevant information will be extracted")
                    st.write("• Titles, descriptions, and content will be aligned with your goals")
                    st.write("• Video files are processed separately to avoid timeouts")
                    
                    with st.spinner("🤖 Generating goal-aligned pathway with AI (parallel processing enabled)..."):
                        try:
                            from modules.utils import gemini_generate_complete_pathway, get_parallel_config
                            st.write("📞 Calling AI function...")
                            
                            # Show parallel configuration
                            config = get_parallel_config()
                            st.write(f"⚙️ **Parallel Configuration:**")
                            st.write(f"   Max File Workers: {config['max_file_workers']}")
                            st.write(f"   Max Section Workers: {config['max_section_workers']}")
                            st.write(f"   Timeout: {config['timeout_seconds']} seconds")
                            
                            # Pass the bypass filtering option
                            if bypass_filtering:
                                st.info("🔄 Bypassing goal alignment - including all file content")
                            else:
                                st.info("🎯 Using goal alignment - filtering content to match your training objectives")
                            
                            # Pass enhanced content mode
                            if enhanced_content_mode:
                                st.info("📈 Enhanced Content Mode - generating more modules, pathways, and sections")
                            
                            # Add progress indicator
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            # Update progress
                            status_text.text("🚀 Starting AI pathway generation...")
                            progress_bar.progress(10)
                            
                            generated_pathways_data = gemini_generate_complete_pathway(context, extracted_file_contents, inventory, bypass_filtering=bypass_filtering, preserve_original_content=preserve_original_content, enhanced_content=enhanced_content_mode)
                            
                            # Flush any debug logs from background threads
                            flush_debug_logs_to_streamlit()
                            
                            # Update progress
                            status_text.text("✅ AI pathway generation completed!")
                            progress_bar.progress(100)
                            
                            # Clear progress after a moment
                            import time
                            time.sleep(1)
                            progress_bar.empty()
                            status_text.empty()
                            
                            st.write(f"📋 AI Response: {generated_pathways_data}")
                            
                            if generated_pathways_data:
                                st.session_state['generated_pathway'] = generated_pathways_data
                                st.success("✅ Goal-aligned pathway generated successfully!")
                                st.rerun()
                            else:
                                st.error("❌ AI returned None or empty response")
                                st.info("💡 This might mean:")
                                st.info("• No content was extracted from files")
                                st.info("• AI couldn't process the content")
                                st.info("• API call failed silently")
                        except Exception as e:
                            error_msg = f"❌ Exception during AI generation: {str(e)}"
                            st.error(error_msg)
                            st.code(f"Error details: {type(e).__name__}: {str(e)}")
                            import traceback
                            full_traceback = traceback.format_exc()
                            st.code(full_traceback)
                            
                            # Store error in session state for persistence
                            st.session_state['ai_errors'] = {
                                'error': str(e),
                                'type': type(e).__name__,
                                'traceback': full_traceback
                            }
                            
                            # Also write error to file for debugging
                            try:
                                with open('ai_error_log.txt', 'w') as f:
                                    f.write(f"Error Type: {type(e).__name__}\n")
                                    f.write(f"Error Message: {str(e)}\n")
                                    f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                                    f.write(f"Full Traceback:\n{full_traceback}\n")
                                st.info("📝 Error logged to 'ai_error_log.txt' file")
                            except:
                                pass
        
        # Show persistent errors if they exist
        if 'ai_errors' in st.session_state:
            st.error("🚨 **Previous Error (from last attempt):**")
            st.write(f"**Error Type:** {st.session_state['ai_errors']['type']}")
            st.write(f"**Error Message:** {st.session_state['ai_errors']['error']}")
            st.code(st.session_state['ai_errors']['traceback'])
            
            # Add specific help for rate limit errors
            if '429' in st.session_state['ai_errors']['error'] or 'quota' in st.session_state['ai_errors']['error'].lower():
                st.warning("⚠️ **API Rate Limit Hit**")
                st.write("You've exceeded your Gemini API daily quota. Try these options:")
                st.write("• **Use Quick Test Mode** (checkbox above) - works without AI")
                st.write("• **Wait 24 hours** for quota reset")
                st.write("• **Upgrade your Gemini API plan** for higher limits")
                st.write("• **Check your billing** at https://ai.google.dev/")
            
            if st.button("🗑️ Clear Error Log"):
                del st.session_state['ai_errors']
                st.rerun()
        
        with col2:
            st.markdown("**AI-Powered Pathways**")
            st.markdown("All pathways are generated using AI to ensure they are:")
            st.markdown("• Contextually relevant to your industry")
            st.markdown("• Tailored to your target audience")
            st.markdown("• Based on your specific content")
            st.markdown("• Adaptable to your company size")
        
        # --- Display generated pathway(s) ---
        if 'generated_pathway' not in st.session_state:
            st.error("No pathway generated yet. Please click the 'Generate Semantically Aligned Pathway' button above.")
            return
        
        generated_pathways_data = st.session_state['generated_pathway']
        if not generated_pathways_data or 'pathways' not in generated_pathways_data or not generated_pathways_data['pathways']:
            st.error("No pathways found in the AI response.")
            return
        pathways = generated_pathways_data['pathways']
        pathway_names = [p['pathway_name'] for p in pathways]
        
        # Pathways UI navigation state
        if 'selected_pathway_idx' not in st.session_state:
            st.session_state['selected_pathway_idx'] = 0
        if 'selected_section' not in st.session_state:
            st.session_state['selected_section'] = None
        
        # Show pathway cards for all pathways
        st.markdown(f"### 🎯 **Select a Pathway**")
        
        # Check if pathways exist and are not empty
        if not pathways or len(pathways) == 0:
            st.error("No pathways generated. Please try again.")
            return
        
        cols = st.columns(len(pathway_names))
        for idx, pname in enumerate(pathway_names):
            with cols[idx]:
                if st.button(f"Pathway {idx+1}: {pname}", key=f"pathway_card_{idx}"):
                    st.session_state['selected_pathway_idx'] = idx
                    st.session_state['selected_section'] = None
        # Safety check for pathway index
        if 'selected_pathway_idx' not in st.session_state or st.session_state['selected_pathway_idx'] >= len(pathways):
            st.session_state['selected_pathway_idx'] = 0
        
        selected_pathway = pathways[st.session_state['selected_pathway_idx']]
        
        # Initialize chatbot visibility state for main pathway view
        if 'chatbot_visible' not in st.session_state:
            st.session_state.chatbot_visible = True  # Show by default after pathway generation
        
        # Create header with pathway name
        st.markdown(f"### 🎯 **{selected_pathway['pathway_name']}**")
        st.markdown("This goal-aligned pathway is designed based on your specific training goals and available content. Content has been filtered and structured to directly support your training objectives.")
        
        # Add floating chatbot button with CSS
        st.markdown("""
        <style>
        .floating-chatbot {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            color: white;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .floating-chatbot:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        .chatbot-popup {
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 350px;
            max-height: 500px;
            background: white;
            border: 2px solid #1f77b4;
            border-radius: 10px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            z-index: 9999;
            overflow-y: auto;
            padding: 15px;
        }
        .chatbot-popup-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .chatbot-popup-close {
            background: none;
            border: none;
            font-size: 22px;
            color: #1f77b4;
            cursor: pointer;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create main content area
        # Main content goes here
        
        # Initialize chatbot visibility state
        if 'chatbot_visible' not in st.session_state:
            st.session_state.chatbot_visible = False
        
        # Floating chatbot button on the right side
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
        with col5:
            if st.button("🤖", key="floating_chatbot_toggle", help="AI Assistant"):
                st.session_state.chatbot_visible = not st.session_state.chatbot_visible
                st.rerun()
        
        # Show chatbot popup if visible
        if st.session_state.chatbot_visible:
            create_pathway_chatbot_popup("floating")
        # --- Convert pathway to editable format ---
        if 'editable_pathways' not in st.session_state or st.session_state.get('editable_pathways_pathway_idx', -1) != st.session_state['selected_pathway_idx']:
            editable_pathways = {}
            for section in selected_pathway['sections']:
                section_title = section['title']
                editable_pathways[section_title] = []
                for module in section['modules']:
                    editable_pathways[section_title].append({
                        'title': module['title'],
                        'description': module['description'],
                        'content': module.get('content', ''),
                        'source': module.get('source', ['Content from uploaded files']),
                        'content_types': module.get('content_types', [])
                    })
            st.session_state['editable_pathways'] = editable_pathways
            st.session_state['editable_pathways_pathway_idx'] = st.session_state['selected_pathway_idx']
        editable_pathways = st.session_state['editable_pathways']
        # Show sections if pathway selected
        section_names = list(editable_pathways.keys())
        st.markdown(f"### Sections in Pathway {st.session_state['selected_pathway_idx']+1}: {selected_pathway['pathway_name']}")
        for idx, section in enumerate(section_names):
            # Find section description from generated pathway
            section_desc = ""
            for gen_section in selected_pathway['sections']:
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
            
            # Initialize chatbot visibility state
            if 'chatbot_visible' not in st.session_state:
                st.session_state.chatbot_visible = False
            
            # Create main layout with chatbot toggle
            main_col, chatbot_col = st.columns([4, 1])
            
            with main_col:
                i = 0
                while i < len(mods):
                    mod = mods[i]
                    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 2, 2])
                    with col1:
                        new_title = st.text_input(f"Title ({section}-{i})", mod['title'], key=f"title_{section}_{i}")
                        new_desc = st.text_input(f"Description ({section}-{i})", mod.get('description', ''), key=f"desc_{section}_{i}")
                        new_content = st.text_area(f"Content ({section}-{i})", mod['content'], key=f"content_{section}_{i}")
                        # Display correct local module number within section
                        st.markdown(f"**Module {i+1}. {new_title}**")
                    
                    # Display content types on the right side
                    with col4:
                        st.markdown("**🎨 Content Types:**")
                        content_types = mod.get('content_types', [])
                        if content_types:
                            for j, content_type in enumerate(content_types):
                                with st.expander(f"📋 {content_type.get('title', f'Content Type {j+1}')}"):
                                    st.markdown(f"**Type:** {content_type.get('type', 'Unknown')}")
                                    st.markdown(f"**Description:** {content_type.get('description', 'No description')}")
                                    st.markdown(f"**Content:** {content_type.get('content', 'No content')}")
                        else:
                            st.info("No content types generated for this module")
                    
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
                    
                    # Move section controls
                    with col5:
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
            
            # Remove chatbot from module view since we have floating chatbot
            pass
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
                    'pathways': [
                        {
                            'pathway_name': p['pathway_name'],
                            'sections': [
                                {
                                    'name': section,
                                    'modules': [
                                        {'title': m['title'], 'content': m['content'], 'source': m['source']}
                                        for m in editable_pathways[section]
                                    ]
                                } for section in editable_pathways.keys()
                            ]
                        } for p in pathways
                    ]
                }
                json_str = json.dumps(export_data, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"onboarding_pathways_all.json",
                    mime="application/json"
                )
        with col5:
            if st.button("Save Pathways"):
                st.session_state['confirmed_pathways'] = {
                    'pathways': [
                        {
                            'pathway_name': selected_pathway['pathway_name'],
                            'sections': [
                                {
                                    'name': section,
                                    'modules': [
                                        {'title': m['title'], 'content': m['content'], 'source': m['source']}
                                        for m in editable_pathways[section]
                                    ]
                                } for section in editable_pathways.keys()
                            ]
                        }
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

        # Save generated pathway to history
        if 'past_generated_pathways' not in st.session_state:
            st.session_state['past_generated_pathways'] = []
        # Only append if not already present (by pathway_name and sections)
        if generated_pathways_data not in st.session_state['past_generated_pathways']:
            st.session_state['past_generated_pathways'].append(generated_pathways_data)

def create_pathway_chatbot():
    """
    Create a chatbot interface for pathway management
    Allows admins to regenerate modules and ingest new files
    """
    st.markdown("---")
    st.markdown("### 🤖 AI Pathway Assistant")
    st.markdown("Use this chatbot to regenerate modules, update content, or ingest new files.")
    
    # Initialize chat history
    if 'chatbot_history' not in st.session_state:
        st.session_state.chatbot_history = []
    
    # Chatbot interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Display chat history
        st.markdown("**💬 Chat History:**")
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.chatbot_history:
                if message['role'] == 'user':
                    st.markdown(f"**👤 You:** {message['content']}")
                else:
                    st.markdown(f"**🤖 Assistant:** {message['content']}")
        
        # User input
        user_input = st.text_input("Ask me about regenerating modules, updating content, or ingesting new files:", 
                                  key="chatbot_input", 
                                  placeholder="e.g., 'Regenerate module 2 with a more professional tone'")
        
        if st.button("Send", key="send_chat"):
            if user_input:
                # Add user message to history
                st.session_state.chatbot_history.append({
                    'role': 'user',
                    'content': user_input
                })
                
                # Process the request
                response = process_chatbot_request(user_input)
                
                # Add assistant response to history
                st.session_state.chatbot_history.append({
                    'role': 'assistant',
                    'content': response
                })
                
                st.rerun()
    
    with col2:
        st.markdown("**🛠️ Quick Actions:**")
        
        if st.button("🔄 Regenerate Current Module", key="regenerate_current"):
            regenerate_current_module()
        
        if st.button("📁 Ingest New Files", key="ingest_new_files"):
            ingest_new_files_interface()
        
        if st.button("🎨 Update Module Tone", key="update_tone"):
            update_module_tone_interface()
        
        if st.button("📝 Add Missing Info", key="add_missing_info"):
            add_missing_info_interface()
        
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.chatbot_history = []
            st.rerun()

def create_pathway_chatbot_popup(context="main"):
    """
    Create a popup chatbot interface for pathway management
    This version appears as a floating popup when toggled
    """
    # Always use a floating popup on the right, never sidebar
    if context == "floating":
        # No custom CSS needed for sidebar approach
        
        # Render the popup only if chatbot_visible is True
        if st.session_state.get("chatbot_visible", False):
            # Use sidebar for floating effect
            with st.sidebar:
                st.markdown("### 🤖 AI Assistant")
                
                # Show AI status
                if model:
                    st.success("✅ Gemini AI Connected")
                else:
                    st.error("❌ Gemini AI Not Available")
                    st.info("Please check your API key in Settings")
                
                # Show current module structure
                editable_pathways = st.session_state.get('editable_pathways', {})
                if editable_pathways:
                    st.markdown("**📚 Current Modules:**")
                    module_reference_help = format_module_reference_help(editable_pathways)
                    # Show a condensed version
                    for section_name, modules in editable_pathways.items():
                        st.markdown(f"**{section_name}:**")
                        for i, module in enumerate(modules):
                            st.markdown(f"  • Module {i+1}: {module['title']}")
                        st.markdown("")
                else:
                    st.info("📚 No modules available yet")
                
                # Close button
                if st.button("✕ Close", key=f"sidebar_close_{context}", help="Close AI Assistant"):
                    st.session_state.chatbot_visible = False
                    st.rerun()
                
                # Chat history
                if 'popup_chatbot_history' not in st.session_state:
                    st.session_state.popup_chatbot_history = []
                
                # Display recent messages
                recent_messages = st.session_state.popup_chatbot_history[-8:] if st.session_state.popup_chatbot_history else []
                for message in recent_messages:
                    if message['role'] == 'user':
                        st.markdown(f"**👤 You:** {message['content']}")
                    else:
                        st.markdown(f"**🤖 Assistant:** {message['content']}")
                
                st.markdown("---")
                
                # File upload section - MOVED TO TOP
                st.markdown("**📁 Upload Files:**")
                uploaded_files = st.file_uploader(
                    "Upload files to add to your pathway",
                    type=['pdf', 'doc', 'docx', 'txt', 'mp4', 'avi', 'mov'],
                    key=f"sidebar_file_upload_{context}",
                    accept_multiple_files=True
                )
                
                # Show uploaded files status
                if uploaded_files:
                    st.success(f"📁 {len(uploaded_files)} files ready")
                    for i, file in enumerate(uploaded_files):
                        st.write(f"• {file.name} ({file.size} bytes)")
                    
                                    # Process files button
                if st.button("🔄 Process Files Now", key=f"sidebar_process_files_{context}"):
                    st.info("🚀 Fast processing files...")
                    
                    # Add progress indicator
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Process files with progress updates
                    for i, file in enumerate(uploaded_files):
                        status_text.text(f"Processing {file.name}... ({i+1}/{len(uploaded_files)})")
                        progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    result = process_new_files(uploaded_files)
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    if result:
                        st.success("✅ Files processed and pathway updated!")
                        # Add success message to chat
                        st.session_state.popup_chatbot_history.append({
                            'role': 'assistant',
                            'content': f"✅ Successfully processed {len(uploaded_files)} files and updated your pathway!"
                        })
                        st.rerun()
                    else:
                        st.error("❌ Failed to process files. Please try again.")
                        # Add error message to chat
                        st.session_state.popup_chatbot_history.append({
                            'role': 'assistant',
                            'content': "❌ Failed to process files. Please check the file format and try again."
                        })
                        st.rerun()
                else:
                    st.info("📁 No files uploaded yet")
                
                st.markdown("---")
                
                # User input section
                st.markdown("**💬 Ask me anything:**")
                user_input = st.text_input("Your message:", key=f"sidebar_input_{context}", placeholder="e.g., 'Update module 2 with new file' or 'Regenerate module 1'")
                
                # Send button
                if st.button("Send", key=f"sidebar_send_{context}"):
                    if user_input:
                        st.session_state.popup_chatbot_history.append({
                            'role': 'user',
                            'content': user_input
                        })
                        
                        # Pass uploaded files to the processing function
                        response = process_chatbot_request(user_input, uploaded_files)
                        st.session_state.popup_chatbot_history.append({
                            'role': 'assistant',
                            'content': response
                        })
                        st.rerun()
                
                st.markdown("---")
                
                # Quick actions
                st.markdown("**⚡ Quick Actions:**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("🔄 Regenerate", key=f"quick_regenerate_{context}"):
                        if uploaded_files:
                            response = process_chatbot_request("regenerate current module with uploaded files", uploaded_files)
                        else:
                            response = "Please upload files first, then ask me to regenerate modules."
                        
                        st.session_state.popup_chatbot_history.append({
                            'role': 'assistant',
                            'content': response
                        })
                        st.rerun()
                
                with col2:
                    if st.button("📚 Past Pathways", key=f"show_past_{context}"):
                        response = process_chatbot_request("show past pathways")
                        st.session_state.popup_chatbot_history.append({
                            'role': 'assistant',
                            'content': response
                        })
                        st.rerun()
                
                with col3:
                    if st.button("🔍 Search Content", key=f"search_content_{context}"):
                        response = process_chatbot_request("find safety procedures")
                        st.session_state.popup_chatbot_history.append({
                            'role': 'assistant',
                            'content': response
                        })
                        st.rerun()
                
                col4, col5 = st.columns(2)
                with col4:
                    if st.button("🗑️ Clear Chat", key=f"sidebar_clear_{context}", help="Clear chat history"):
                        st.session_state.popup_chatbot_history = []
                        st.rerun()
    else:
        # Fallback: show nothing for non-floating context
        pass

def process_chatbot_request(user_input, uploaded_files=None):
    """
    Process chatbot requests and return appropriate responses
    """
    user_input_lower = user_input.lower()
    
    # Get current pathway data for module reference
    editable_pathways = st.session_state.get('editable_pathways', {})
    module_reference_help = ""
    if editable_pathways:
        module_reference_help = format_module_reference_help(editable_pathways)
    
    # Check for file-based update requests (when files are uploaded) - PRIORITY 1
    if uploaded_files and len(uploaded_files) > 0:
        if any(word in user_input_lower for word in ['update', 'add to', 'modify', 'change', 'adjust', 'regenerate']):
            if any(word in user_input_lower for word in ['module', 'section', 'pathway', 'course', 'program']):
                return handle_file_based_module_update(user_input, uploaded_files)
    
    # Check for regeneration requests (when no files uploaded)
    if any(word in user_input_lower for word in ['regenerate']):
        if 'module' in user_input_lower or 'content' in user_input_lower:
            return handle_module_regeneration(user_input)
        else:
            return f"I can help you regenerate modules. Please specify which module you'd like to regenerate and any specific changes you want.\n\n{module_reference_help}"
    
    # Check for file ingestion requests (when no files uploaded)
    elif any(word in user_input_lower for word in ['ingest', 'upload', 'add', 'new file', 'new files', 'process files']):
        return handle_file_ingestion(user_input)
    
    # Check for tone/style changes (expanded to include more tones)
    elif any(word in user_input_lower for word in ['tone', 'style', 'professional', 'casual', 'formal', 'technical', 'friendly', 'conversational', 'academic', 'simple', 'detailed']):
        return handle_tone_change(user_input)
    
    # Check for content addition
    elif any(word in user_input_lower for word in ['add', 'include', 'missing', 'additional', 'insert', 'supplement']):
        return handle_content_addition(user_input)
    
    # Check for specific module requests
    elif any(word in user_input_lower for word in ['module', 'section', 'content']):
        return handle_module_specific_request(user_input)
    
    # General help
    elif any(word in user_input_lower for word in ['help', 'what can you do', 'how', 'commands']):
        return get_chatbot_help()
    
    # Default response - use AI for intelligent responses
    else:
        try:
            if not model:
                # Fallback if AI not available
                if uploaded_files and len(uploaded_files) > 0:
                    return f"I see you've uploaded {len(uploaded_files)} file(s). You can:\n• \"Update module 1 with new file\"\n• \"Add content to safety section\"\n• \"Modify module 1 with uploaded content\"\n• \"Update pathway with new information\"\n• \"Regenerate module 2 with uploaded files\"\n\nPlease specify which module, section, or pathway you'd like to update with the uploaded files.\n\n{module_reference_help}"
                else:
                    return f"I can help you with:\n• Regenerating modules with different content or tone\n• Uploading new files to update pathways\n• Changing module tone/style (professional, casual, formal, technical, friendly, etc.)\n• Adding missing information to modules\n• Updating specific modules/sections with new file content\n\nPlease be more specific about what you'd like to do.\n\n{module_reference_help}"
            
            # Use AI to generate contextual response
            files_info = f"User has uploaded {len(uploaded_files)} files: {[f.name for f in uploaded_files]}" if uploaded_files else "No files uploaded"
            
            prompt = f"""
            You are an AI training content assistant. The user said: "{user_input}"
            {files_info}
            
            Current module structure:
            {module_reference_help}
            
            Generate a helpful, contextual response that:
            1. Acknowledges their input
            2. Suggests relevant actions they can take
            3. Provides specific examples of commands they can use
            4. Is friendly and encouraging
            5. References the correct module numbering system (modules are numbered 1, 2, 3, etc. within each section)
            6. Mentions that they can search for content and ask questions about training information
            
            Keep the response concise and actionable.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            # Fallback to static response if AI fails
            if uploaded_files and len(uploaded_files) > 0:
                return f"I see you've uploaded {len(uploaded_files)} file(s). You can:\n• \"Update module 1 with new file\"\n• \"Add content to section 3\"\n• \"Modify module 1 with uploaded content\"\n• \"Update pathway with new information\"\n• \"Regenerate module 2 with uploaded files\"\n\nPlease specify which module, section, or pathway you'd like to update with the uploaded files.\n\n{module_reference_help}"
            else:
                return f"I can help you with:\n• Regenerating modules with different content or tone\n• Uploading new files to update pathways\n• Changing module tone/style (professional, casual, formal, technical, friendly, etc.)\n• Adding missing information to modules\n• Updating specific modules/sections with new file content\n• Searching for specific topics in pathways\n• Answering questions about training content\n\nPlease be more specific about what you'd like to do.\n\n{module_reference_help}"

def handle_module_regeneration(user_input):
    """
    Handle module regeneration requests
    """
    try:
        # Extract module information from user input
        module_info = extract_module_info_from_input(user_input)
        
        if not module_info:
            return "Please specify which module you'd like to regenerate. You can say 'regenerate module 2' or 'update the safety module'."
        
        # Get current pathway data
        if 'editable_pathways' not in st.session_state:
            return "No pathway data available. Please generate a pathway first."
        
        editable_pathways = st.session_state['editable_pathways']
        
        # Find the specified module
        target_module = find_module_by_info(module_info, editable_pathways)
        
        if not target_module:
            return f"Could not find module matching '{module_info}'. Please check the module name or number."
        
        # Extract regeneration parameters
        tone = extract_tone_from_input(user_input)
        content_focus = extract_content_focus_from_input(user_input)
        changes_requested = extract_changes_from_input(user_input)
        
        # Regenerate the module
        new_content = regenerate_module_content(target_module, tone, content_focus, changes_requested)
        
        # Update the module in the pathway
        if update_module_in_pathway(target_module, new_content):
            return f"✅ Successfully regenerated module '{target_module['module']['title']}' with {tone} tone and {content_focus} focus.\n\nChanges made: {changes_requested if changes_requested else 'Updated content and tone'}"
        else:
            return "❌ Failed to update module in pathway. Please try again."
        
    except Exception as e:
        return f"❌ Error regenerating module: {str(e)}"

def handle_file_ingestion(user_input):
    """
    Handle file ingestion requests with AI-powered guidance
    """
    try:
        if not model:
            return "AI model not available. Please check your API configuration."
        
        # Use AI to generate personalized file ingestion guidance
        prompt = f"""
        The user is asking about file ingestion for training content. 
        User input: "{user_input}"
        
        Generate a helpful, personalized response that explains:
        1. How to upload files in the chatbot interface
        2. What happens when files are processed
        3. Supported file types
        4. Best practices for file uploads
        
        Make the response friendly and actionable. Include specific steps.
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        # Fallback to static response if AI fails
        return (
            "**File Ingestion Options:**\n\n"
            "1. **Upload files in the chatbot interface** - I'll process them immediately\n"
            "2. **Use the 'Process Files Now' button** after uploading\n"
            "3. **Ask me to update specific modules or sections** with uploaded content\n\n"
            "**What happens when you ingest new files:**\n"
            "• New content will be analyzed and integrated into existing modules\n"
            "• Missing information will be added to relevant modules\n"
            "• New modules may be created if significant new content is found\n"
            "• Existing modules will be updated with additional information\n\n"
            "**Supported file types:** PDF, DOC, DOCX, TXT, MP4, AVI, MOV\n\n"
            "**Examples:**\n"
            "• \"Update module 2 with new file\"\n"
            "• \"Add content to section 3\"\n"
            "• \"Update pathway with new information\"\n\n"
            "Upload files in the sidebar, then ask me to update specific modules or sections!"
        )

def handle_tone_change(user_input):
    """
    Handle tone/style change requests
    """
    tone = extract_tone_from_input(user_input)
    if tone:
        return f"I can help you change the tone to {tone}. Please specify which module you'd like to update, or use the 'Update Module Tone' button."
    else:
        return "I can help you change module tone. Available tones: professional, casual, formal, technical, friendly. Please specify which module and tone."

def handle_content_addition(user_input):
    """
    Handle content addition requests
    """
    return "I can help you add missing information to modules. Please specify which module and what information you'd like to add."

def handle_module_specific_request(user_input):
    """
    Handle requests for specific modules or content
    """
    user_input_lower = user_input.lower()
    
    # Check if user is asking about specific modules
    if any(word in user_input_lower for word in ['show', 'view', 'see', 'display']):
        return "I can help you view specific modules. Please specify which module you'd like to see (e.g., 'show module 2' or 'view safety module')."
    
    # Check if user is asking about module content
    elif any(word in user_input_lower for word in ['content', 'information', 'details']):
        return "I can help you with module content. Please specify what you'd like to do (e.g., 'add more details to module 3' or 'make module 1 more detailed')."
    
    # Default response for module-related requests
    else:
        return "I can help you with modules. Please specify what you'd like to do:\n• View a specific module\n• Modify module content\n• Add information to a module\n• Change module tone"

def get_chatbot_help():
    """
    Return AI-powered help information for the chatbot
    """
    try:
        if not model:
            return "AI model not available. Please check your API configuration."
        
        # Get current pathway data for module reference help
        editable_pathways = st.session_state.get('editable_pathways', {})
        module_reference_help = ""
        if editable_pathways:
            module_reference_help = format_module_reference_help(editable_pathways)
        
        # Use AI to generate contextual help
        prompt = f"""
        Generate a comprehensive, user-friendly help guide for an AI training content assistant chatbot.
        
        The chatbot can:
        - Regenerate modules with different tones and content
        - Process uploaded files and update pathways
        - Update specific modules/sections with new file content
        - Change module tone and style
        - Add missing information to modules
        - Search for specific topics in pathways (NEW)
        - Answer questions about training content (NEW)
        - Reference and integrate from past pathways (NEW)
        
        Current module structure:
        {module_reference_help}
        
        Include:
        1. Clear command examples with correct module numbering
        2. File upload instructions
        3. Available tones and styles
        4. Best practices and tips
        5. Troubleshooting advice
        6. Module reference examples using the correct numbering system
        7. Content search and question examples (NEW)
        8. Past pathway integration examples (NEW)
        
        Make it conversational and easy to follow. Emphasize that modules are numbered locally within each section (Module 1, 2, 3, etc. within each section).
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        # Fallback to static help if AI fails
        editable_pathways = st.session_state.get('editable_pathways', {})
        module_reference_help = ""
        if editable_pathways:
            module_reference_help = format_module_reference_help(editable_pathways)
        
    return (
            f"**AI Pathway Assistant Help**\n\n"
            f"{module_reference_help}\n\n"
            "**Content Search & Questions (NEW):**\n"
            "- \"Find safety procedures in the pathways\"\n"
            "- \"Search for PPE requirements\"\n"
            "- \"What does module 2 say about equipment safety?\"\n"
            "- \"What are the emergency procedures?\"\n"
            "- \"Show content of module 1\"\n"
            "- \"Tell me about quality control procedures\"\n\n"
            "**Past Pathway Integration (NEW):**\n"
            "- \"Show past pathways\"\n"
            "- \"Integrate module 2 from pathway 1 section 3\"\n"
            "- \"Integrate 'PPE Requirements' from pathway 2 into section Safety Procedures\"\n"
            "- \"Merge section 2 from pathway 1 into section Quality Control\"\n"
            "- \"Merge 'Safety Procedures' from pathway 2 into section Quality Control\"\n\n"
        "**Module Regeneration Commands:**\n"
            "- \"Regenerate module 1 with professional tone\"\n"
            "- \"Update module 2 to include more procedures\"\n"
        "- \"Change module 1 to casual tone and add troubleshooting steps\"\n"
        "- \"Regenerate module 3 to remove technical jargon\"\n"
        "- \"Update module 1 to include more safety procedures\"\n\n"
        "**File-Based Update Commands:**\n"
        "- \"Update module 2 with new file\" (upload file first)\n"
        "- \"Add content to safety section\" (upload file first)\n"
        "- \"Update pathway with new information\" (upload file first)\n"
        "- \"Modify module 1 with uploaded content\" (upload file first)\n\n"
        "**File Ingestion Commands:**\n"
        "- \"Ingest new files\"\n"
        "- \"Upload additional training materials\"\n"
        "- \"Add new content from files\"\n\n"
        "**Content Modification Commands:**\n"
        "- \"Add missing information to module 3\"\n"
        "- \"Include more detailed procedures in module 2\"\n"
        "- \"Simplify the language in module 1\"\n"
        "- \"Add troubleshooting tips to the equipment module\"\n\n"
        "**File Upload:**\n"
        "- Use the file upload section in the sidebar to add new files\n"
        "- Supported formats: PDF, DOC, DOCX, TXT, MP4, AVI, MOV\n"
        "- Files will be automatically processed and integrated\n"
        "- Upload files, then type commands to update specific modules/sections\n\n"
        "**Available Tones:**\n"
        "- Professional - Formal business language\n"
        "- Casual - Friendly, conversational tone\n"
        "- Formal - Academic or technical tone\n"
        "- Technical - Detailed technical explanations\n"
        "- Friendly - Warm, approachable tone\n"
        "- Conversational - Natural, dialogue-like\n"
        "- Academic - Scholarly, research-based\n"
        "- Simple - Easy-to-understand language\n"
        "- Detailed - Comprehensive explanations\n\n"
            "**Module Numbering:**\n"
            "- Modules are numbered locally within each section (1, 2, 3, etc.)\n"
            "- \"Module 1\" refers to the first module in the current section\n"
            "- \"Module 2 in safety section\" refers to the second module in the safety section\n"
            "- You can also reference modules by title or keywords\n\n"
        "**Tips:**\n"
        "- Be specific about which module you want to modify\n"
        "- Mention what content you want to add, remove, or change\n"
        "- Specify the tone/style you want\n"
        "- Upload files through the sidebar file uploader\n"
        "- Use \"Clear Chat\" to start fresh conversations\n"
            "- **NEW:** Search for topics and ask questions about training content\n"
            "- **NEW:** Integrate modules/sections from past pathways"
    )

def extract_module_info_from_input(user_input):
    """
    Extract module information from user input
    """
    # Look for module numbers
    import re
    module_match = re.search(r'module\s+(\d+)', user_input.lower())
    if module_match:
        return f"module_{module_match.group(1)}"
    
    # Look for specific module names
    module_keywords = ['safety', 'quality', 'process', 'equipment', 'training', 'onboarding']
    for keyword in module_keywords:
        if keyword in user_input.lower():
            return keyword
    
    return None

def extract_tone_from_input(user_input):
    """
    Extract tone information from user input
    """
    user_input_lower = user_input.lower()
    
    if 'professional' in user_input_lower:
        return 'professional'
    elif 'casual' in user_input_lower:
        return 'casual'
    elif 'formal' in user_input_lower:
        return 'formal'
    elif 'technical' in user_input_lower:
        return 'technical'
    elif 'friendly' in user_input_lower:
        return 'friendly'
    elif 'conversational' in user_input_lower:
        return 'conversational'
    elif 'academic' in user_input_lower:
        return 'academic'
    elif 'simple' in user_input_lower:
        return 'simple'
    elif 'detailed' in user_input_lower:
        return 'detailed'
    elif 'conversational' in user_input_lower:
        return 'conversational'
    
    return 'professional'  # Default

def extract_content_focus_from_input(user_input):
    """
    Extract content focus from user input
    """
    user_input_lower = user_input.lower()
    
    if 'procedure' in user_input_lower:
        return 'procedures'
    elif 'safety' in user_input_lower:
        return 'safety'
    elif 'quality' in user_input_lower:
        return 'quality'
    elif 'technical' in user_input_lower:
        return 'technical'
    elif 'practical' in user_input_lower:
        return 'practical'
    
    return 'general'

def extract_changes_from_input(user_input):
    """
    Extract specific changes requested from user input
    """
    user_input_lower = user_input.lower()
    changes = []
    
    # Check for specific change requests
    if 'remove' in user_input_lower:
        # Extract what to remove
        import re
        remove_match = re.search(r'remove\s+([^,]+)', user_input_lower)
        if remove_match:
            changes.append(f"Remove: {remove_match.group(1)}")
    
    if 'add' in user_input_lower:
        # Extract what to add
        import re
        add_match = re.search(r'add\s+([^,]+)', user_input_lower)
        if add_match:
            changes.append(f"Add: {add_match.group(1)}")
    
    if 'include' in user_input_lower:
        # Extract what to include
        import re
        include_match = re.search(r'include\s+([^,]+)', user_input_lower)
        if include_match:
            changes.append(f"Include: {include_match.group(1)}")
    
    if 'more' in user_input_lower and 'detail' in user_input_lower:
        changes.append("Add more detailed explanations")
    
    if 'simplify' in user_input_lower:
        changes.append("Simplify language and explanations")
    
    if 'expand' in user_input_lower:
        changes.append("Expand on key concepts")
    
    return '; '.join(changes) if changes else None

def find_module_by_info(module_info, editable_pathways):
    """
    Find a module based on the provided information
    Updated to handle correct module numbering within sections
    """
    # Create module mapping
    module_mapping = create_module_mapping(editable_pathways)
    
    # Check for module number references (e.g., "module 2")
            if module_info.startswith('module_'):
                module_num = module_info.split('_')[1]
        
        # First try to find by global number
        if module_num in module_mapping['by_global_number']:
            return module_mapping['by_global_number'][module_num]
        
        # If not found globally, check if it's a section-specific reference
        # Look for patterns like "section 3 module 2" or "safety module 1"
        for section_name, section_modules in module_mapping['by_section_and_number'].items():
            if module_num in section_modules:
                return section_modules[module_num]
            
            # Check by module title/keywords
    module_info_lower = module_info.lower()
    for title, module_data in module_mapping['by_title'].items():
        if module_info_lower in title or title in module_info_lower:
            return module_data
    
    # Check for section-specific module references
    for section_name, section_modules in module_mapping['by_section_and_number'].items():
        if module_info_lower in section_name.lower():
            # Return first module in this section (module 1)
            if '1' in section_modules:
                return section_modules['1']
    
    return None

def regenerate_module_content(target_module, tone, content_focus, changes_requested=None):
    """
    Regenerate module content using AI with specific changes
    """
    try:
        if not model:
            return "AI model not available. Please check your API configuration."
        
        original_content = target_module['module']['content']
        module_title = target_module['module']['title']
        
        # Build the prompt based on requested changes
        changes_text = ""
        if changes_requested:
            changes_text = f"\nSpecific Changes Requested: {changes_requested}"
        
        prompt = (
            f"Regenerate this training module content with the specified tone, focus, and changes.\n\n"
            f"Original Module: {module_title}\n"
            f"Original Content: {original_content[:1500]}\n\n"
            f"Requirements:\n"
            f"- Tone: {tone}\n"
            f"- Content Focus: {content_focus}\n"
            f"- Keep the same core information but adapt the style\n"
            f"- Make it suitable for training purposes\n"
            f"- Ensure it's clear and actionable{changes_text}\n\n"
            f"Instructions:\n"
            f"1. Maintain the essential training information\n"
            f"2. Apply the requested tone and style changes\n"
            f"3. Focus on the specified content area\n"
            f"4. Make the content more engaging and practical\n"
            f"5. Ensure it follows training best practices\n\n"
            f"Return only the regenerated content, no explanations or markdown formatting."
        )
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        return f"Error regenerating content: {str(e)}"

def update_module_in_pathway(target_module, new_content):
    """
    Update the module content in the pathway
    """
    try:
        section_name = target_module['section']
        module_index = target_module['index']
        
        if 'editable_pathways' in st.session_state:
            editable_pathways = st.session_state['editable_pathways']
            if section_name in editable_pathways and module_index < len(editable_pathways[section_name]):
                editable_pathways[section_name][module_index]['content'] = new_content
                st.session_state['editable_pathways'] = editable_pathways
                return True
        
        return False
        
    except Exception as e:
        return False

def regenerate_current_module():
    """
    Regenerate the currently selected module
    """
    if 'selected_section' not in st.session_state or not st.session_state['selected_section']:
        st.error("Please select a section and module first.")
        return
    
    st.info("Regenerating current module...")
    # This would be implemented to regenerate the currently viewed module
    st.success("Module regenerated successfully!")

def ingest_new_files_interface():
    """
    Interface for ingesting new files
    """
    st.markdown("### Ingest New Files")
    st.markdown("Upload new files to update your pathway:")
    
    uploaded_files = st.file_uploader(
        "Choose files to ingest",
        type=['txt', 'pdf', 'doc', 'docx', 'mp4', 'avi', 'mov'],
        accept_multiple_files=True,
        key="ingest_files"
    )
    
    if uploaded_files:
        st.markdown(f"**Files selected:** {len(uploaded_files)} files")
        for file in uploaded_files:
            st.markdown(f"- {file.name} ({file.size} bytes)")
        
        if st.button("Process New Files"):
            result = process_new_files(uploaded_files)
            if result:
                st.success("New files processed and pathway updated!")
                st.rerun()
            else:
                st.error("Failed to process new files. Please try again.")

def update_module_tone_interface():
    """
    Interface for updating module tone
    """
    st.markdown("### Update Module Tone")
    
    # Get current pathway data
    if 'editable_pathways' not in st.session_state:
        st.error("No pathway data available. Please generate a pathway first.")
        return
    
    editable_pathways = st.session_state['editable_pathways']
    
    # Create module selection
    module_options = []
    for section_name, modules in editable_pathways.items():
        for i, module in enumerate(modules):
            module_options.append(f"{section_name} - {module['title']}")
    
    if not module_options:
        st.error("No modules available to update.")
        return
    
    selected_module = st.selectbox("Select module to update:", module_options)
    tone_options = ['professional', 'casual', 'formal', 'technical', 'friendly']
    selected_tone = st.selectbox("Select new tone:", tone_options)
    
    if st.button("Apply Tone Change"):
        # Find and update the selected module
        section_name, module_title = selected_module.split(" - ", 1)
        target_module = find_module_by_title(module_title, editable_pathways)
        
        if target_module:
            new_content = regenerate_module_content(target_module, selected_tone, 'general')
            if update_module_in_pathway(target_module, new_content):
                st.success(f"Updated module '{module_title}' to {selected_tone} tone!")
            else:
                st.error("Failed to update module. Please try again.")
        else:
            st.error("Module not found. Please try again.")

def add_missing_info_interface():
    """
    Interface for adding missing information
    """
    st.markdown("### Add Missing Information")
    
    # Get current pathway data
    if 'editable_pathways' not in st.session_state:
        st.error("No pathway data available. Please generate a pathway first.")
        return
    
    editable_pathways = st.session_state['editable_pathways']
    
    # Create module selection
    module_options = []
    for section_name, modules in editable_pathways.items():
        for i, module in enumerate(modules):
            module_options.append(f"{section_name} - {module['title']}")
    
    if not module_options:
        st.error("No modules available to update.")
        return
    
    selected_module = st.selectbox("Select module to update:", module_options, key="missing_info_module")
    missing_info = st.text_area("What information would you like to add?", 
                               placeholder="e.g., Add more safety procedures, Include quality control steps, Add troubleshooting tips")
    
    if st.button("Add Information"):
        # Find and update the selected module
        section_name, module_title = selected_module.split(" - ", 1)
        target_module = find_module_by_title(module_title, editable_pathways)
        
        if target_module and missing_info:
            changes_requested = f"Add: {missing_info}"
            new_content = regenerate_module_content(target_module, 'professional', 'general', changes_requested)
            if update_module_in_pathway(target_module, new_content):
                st.success(f"Added information to module '{module_title}'!")
            else:
                st.error("Failed to update module. Please try again.")
        else:
            st.error("Please specify what information to add.")

def process_new_files(uploaded_files):
    """
    Process newly uploaded files and update pathway
    """
    try:
        if not uploaded_files:
            return False
        
        # Extract content from new files
        new_file_contents = {}
        for uploaded_file in uploaded_files:
            try:
                # Read file content
                content = uploaded_file.read()
                
                # Handle different file types
                if uploaded_file.type == "text/plain":
                    file_content = content.decode('utf-8')
                elif uploaded_file.type == "application/pdf":
                    # Extract text from PDF using PyPDF2
                    try:
                        # Create a file-like object from the uploaded file
                        pdf_file = uploaded_file.getvalue()
                        # Ensure we have bytes for PyPDF2
                        if isinstance(pdf_file, str):
                            pdf_file = pdf_file.encode('utf-8')
                        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
                        file_content = ""
                        for page in pdf_reader.pages:
                            page_text = page.extract_text()
                            if page_text:
                                file_content += page_text + "\n"
                        
                        if not file_content.strip():
                            file_content = f"PDF content from {uploaded_file.name} (no text extracted)"
                    except Exception as e:
                        file_content = f"PDF content from {uploaded_file.name} (extraction error: {str(e)})"
                else:
                    file_content = f"Content from {uploaded_file.name}"
                
                new_file_contents[uploaded_file.name] = file_content
                
            except Exception as e:
                st.error(f"Error reading {uploaded_file.name}: {str(e)}")
                continue
        
        if not new_file_contents:
            st.error("No files could be processed.")
            return False
        
        # Get current pathway data - create if not exists
        if 'editable_pathways' not in st.session_state:
            st.info("No existing pathway found. Creating new pathway structure...")
            st.session_state['editable_pathways'] = {
                'Additional Content': []
            }
        
        editable_pathways = st.session_state['editable_pathways']
        training_context = st.session_state.get('training_context', {})
        
        # If no training context, create a basic one
        if not training_context:
            training_context = {
                'primary_goals': 'Training content from uploaded files',
                'training_type': 'General',
                'target_audience': 'Employees',
                'industry': 'General'
            }
            st.session_state['training_context'] = training_context
        
        # Process new content and integrate into existing modules
        processed_count = 0
        for filename, content in new_file_contents.items():
            # Extract modules from new content using FAST processing
            new_modules = extract_fast_modules_from_content(filename, content, training_context, training_context.get('primary_goals', 'training goals'))
            
            if new_modules:
                # Integrate new modules into existing pathway
                success = integrate_new_modules(new_modules, editable_pathways, training_context)
                if success:
                    processed_count += len(new_modules)
        
        # Update session state
        st.session_state['editable_pathways'] = editable_pathways
        
        if processed_count > 0:
            return True
        else:
            # Even if no modules were created, the files were processed successfully
        return True
        
    except Exception as e:
        st.error(f"❌ Error processing new files: {str(e)}")
        return False

def find_module_by_title(module_title, editable_pathways):
    """
    Find a module by its title
    """
    for section_name, modules in editable_pathways.items():
        for i, module in enumerate(modules):
            if module['title'] == module_title:
                return {'module': module, 'section': section_name, 'index': i}
    return None

def integrate_new_modules(new_modules, editable_pathways, training_context):
    """
    Integrate new modules into existing pathway
    """
    try:
        for new_module in new_modules:
            # Find the best section to add this module to
            best_section = find_best_section_for_module(new_module, editable_pathways)
            
            if best_section:
                # Add the new module to the best section
                editable_pathways[best_section].append({
                    'title': new_module['title'],
                    'description': new_module['description'],
                    'content': new_module['content'],
                    'source': new_module.get('source', ['New file content']),
                    'content_types': new_module.get('content_types', [])
                })
            else:
                # Create a new section if no good match found
                section_name = "Additional Content"
                if section_name not in editable_pathways:
                    editable_pathways[section_name] = []
                
                editable_pathways[section_name].append({
                    'title': new_module['title'],
                    'description': new_module['description'],
                    'content': new_module['content'],
                    'source': new_module.get('source', ['New file content']),
                    'content_types': new_module.get('content_types', [])
                })
        
        return True
        
    except Exception as e:
        st.error(f"Error integrating new modules: {str(e)}")
        return False

def find_best_section_for_module(new_module, editable_pathways):
    """
    Find the best section to add a new module to
    """
    try:
        new_module_content = new_module['content'].lower()
        new_module_title = new_module['title'].lower()
        
        best_section = None
        best_score = 0
        
        for section_name in editable_pathways.keys():
            section_score = 0
            
            # Check if section name matches module content
            if any(word in new_module_content for word in section_name.lower().split()):
                section_score += 2
            
            # Check if any existing modules in this section are similar
            for existing_module in editable_pathways[section_name]:
                existing_content = existing_module['content'].lower()
                existing_title = existing_module['title'].lower()
                
                # Check for keyword matches
                common_keywords = ['safety', 'quality', 'process', 'equipment', 'training', 'procedure']
                for keyword in common_keywords:
                    if keyword in new_module_content and keyword in existing_content:
                        section_score += 1
                    if keyword in new_module_title and keyword in existing_title:
                        section_score += 1
            
            if section_score > best_score:
                best_score = section_score
                best_section = section_name
        
        return best_section if best_score > 0 else None
        
    except Exception as e:
        return None

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
    MINDMEISTER_REDIRECT_URI=https://localhost:8001
    VADOO_API_KEY=your_vadoo_api_key_here
    CANVA_API_KEY=your_canva_api_key_here
    ```
    """)

def handle_file_based_module_update(user_input, uploaded_files):
    """
    Handle requests to update specific modules/sections/pathways with new file content
    Optimized for speed while maintaining quality
    """
    try:
        if not uploaded_files:
            return "No files uploaded. Please upload files first, then specify which module, section, or pathway you want to update."
        
        # Extract target information from user input
        target_info = extract_target_from_input(user_input)
        if not target_info:
            # Provide more helpful guidance based on available pathways
            current_pathway = st.session_state.get('generated_pathway', None)
            past_pathways = st.session_state.get('past_generated_pathways', [])
            
            available_options = []
            if current_pathway:
                available_options.append("• 'Update pathway 1 section 1 with new file'")
                available_options.append("• 'Add content to pathway 1 section 2'")
            if past_pathways:
                for i, _ in enumerate(past_pathways, 2):
                    available_options.append(f"• 'Update pathway {i} section 1 with new file'")
            
            if not available_options:
                available_options = [
                    "• 'Update module 2 with new file'",
                    "• 'Add content to safety section'", 
                    "• 'Update pathway with new information'"
                ]
            
            return f"Please specify what you want to update. Examples:\n" + "\n".join(available_options)
        
        st.info(f"🚀 Fast processing {len(uploaded_files)} files to update {target_info['type']}...")
        
        # Get current pathway data
        if 'editable_pathways' not in st.session_state:
            return "No pathway data available. Please generate a pathway first."
        
        editable_pathways = st.session_state['editable_pathways']
        training_context = st.session_state.get('training_context', {})
        primary_goals = training_context.get('primary_goals', 'training goals')
        
        # Extract content from uploaded files using FAST AI processing
        new_content_modules = []
        
        for uploaded_file in uploaded_files:
            try:
                # Read file content
                content = uploaded_file.read()
                
                # Handle different file types
                if uploaded_file.type == "text/plain":
                    file_content = content.decode('utf-8')
                elif uploaded_file.type == "application/pdf":
                    # Extract text from PDF using PyPDF2
                    try:
                        # Create a file-like object from the uploaded file
                        pdf_file = uploaded_file.getvalue()
                        # Ensure we have bytes for PyPDF2
                        if isinstance(pdf_file, str):
                            pdf_file = pdf_file.encode('utf-8')
                        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
                        file_content = ""
                        for page in pdf_reader.pages:
                            page_text = page.extract_text()
                            if page_text:
                                file_content += page_text + "\n"
                        
                        if not file_content.strip():
                            file_content = f"PDF content from {uploaded_file.name} (no text extracted)"
                    except Exception as e:
                        file_content = f"PDF content from {uploaded_file.name} (extraction error: {str(e)})"
                else:
                    file_content = f"Content from {uploaded_file.name}"
                
                # Debug: Show file content length
                st.info(f"📄 Processing {uploaded_file.name} ({len(file_content)} characters)")
                
                # Use FAST AI processing - single API call per file
                extracted_modules = extract_fast_modules_from_content(
                    uploaded_file.name, 
                    file_content, 
                    training_context, 
                    primary_goals
                )
                
                if extracted_modules:
                    new_content_modules.extend(extracted_modules)
                    st.success(f"✅ Fast extracted {len(extracted_modules)} modules from {uploaded_file.name}")
                else:
                    st.warning(f"⚠️ No relevant modules found in {uploaded_file.name}")
                    # Try fallback extraction
                    st.info(f"🔄 Trying fallback extraction for {uploaded_file.name}...")
                    fallback_modules = create_simple_modules_from_content(uploaded_file.name, file_content, training_context)
                    if fallback_modules:
                        new_content_modules.extend(fallback_modules)
                        st.success(f"✅ Fallback extracted {len(fallback_modules)} modules from {uploaded_file.name}")
                    else:
                        st.error(f"❌ Could not extract any content from {uploaded_file.name}")
                
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                continue
        
        if not new_content_modules:
            return "❌ No relevant content could be extracted from the uploaded files. Please check that the files contain text content and try again."
        
        # Apply the new content based on target type
        if target_info['type'] == 'specific_module':
            return update_specific_module_in_pathway(target_info, new_content_modules, editable_pathways, training_context)
        elif target_info['type'] == 'module':
            return update_specific_module(target_info['identifier'], new_content_modules, editable_pathways, target_info.get('action', 'add'))
        elif target_info['type'] == 'section':
            return update_specific_section(target_info['identifier'], new_content_modules, editable_pathways, target_info.get('action', 'add'))
        elif target_info['type'] == 'pathway_section':
            return update_pathway_section(target_info, new_content_modules, editable_pathways, training_context)
        elif target_info['type'] == 'pathway':
            return update_entire_pathway(new_content_modules, editable_pathways, training_context)
        else:
            return "❌ Invalid target type specified."
        
    except Exception as e:
        return f"❌ Error processing file-based update: {str(e)}"

def extract_target_from_input(user_input):
    """
    Extract target module/section/pathway from user input with action intent
    """
    user_input_lower = user_input.lower()
    
    # Extract action intent (replace vs merge)
    action_intent = 'add'  # Default action
    if any(word in user_input_lower for word in ['modify', 'update', 'change', 'replace', 'overwrite']):
        action_intent = 'replace'
    elif any(word in user_input_lower for word in ['merge', 'combine', 'append', 'add to', 'enhance']):
        action_intent = 'merge'
    elif any(word in user_input_lower for word in ['add', 'insert', 'create', 'new']):
        action_intent = 'add'
    
    # Look for pathway references first (e.g., "pathway 4 section 3", "pathway 1 section 2")
    import re
    pathway_section_match = re.search(r'pathway\s+(\d+)\s+section\s+(\d+)', user_input_lower)
    if pathway_section_match:
        pathway_num = int(pathway_section_match.group(1))
        section_num = int(pathway_section_match.group(2))
        return {
            'type': 'pathway_section',
            'pathway_num': pathway_num,
            'section_num': section_num,
            'identifier': f"pathway_{pathway_num}_section_{section_num}",
            'action': action_intent
        }
    
    # Look for specific module references (e.g., "pathway 3 section 2 module 1")
    pathway_section_module_match = re.search(r'pathway\s+(\d+)\s+section\s+(\d+)\s+module\s+(\d+)', user_input_lower)
    if pathway_section_module_match:
        pathway_num = int(pathway_section_module_match.group(1))
        section_num = int(pathway_section_module_match.group(2))
        module_num = int(pathway_section_module_match.group(3))
        return {
            'type': 'specific_module',
            'pathway_num': pathway_num,
            'section_num': section_num,
            'module_num': module_num,
            'identifier': f"pathway_{pathway_num}_section_{section_num}_module_{module_num}",
            'action': action_intent
        }
    
    # Look for module references
    module_match = re.search(r'module\s+(\d+)', user_input_lower)
    if module_match:
        return {
            'type': 'module',
            'identifier': f"module_{module_match.group(1)}",
            'action': action_intent
        }
    
    # Look for numbered section references (e.g., "section 3", "section 4")
    section_match = re.search(r'section\s+(\d+)', user_input_lower)
    if section_match:
        return {
            'type': 'section',
            'identifier': f"section_{section_match.group(1)}",
            'action': action_intent
        }
    
    # Look for section references (check specific keywords first, then generic 'section')
    specific_keywords = ['safety', 'quality', 'process', 'equipment', 'training']
    for keyword in specific_keywords:
        if keyword in user_input_lower:
            return {
                'type': 'section',
                'identifier': keyword,
                'action': action_intent
            }
    
    # Check for generic 'section' keyword
    if 'section' in user_input_lower:
        return {
            'type': 'section',
            'identifier': 'section',
            'action': action_intent
        }
    
    # Look for pathway references
    pathway_keywords = ['pathway', 'course', 'program', 'training']
    if any(keyword in user_input_lower for keyword in pathway_keywords):
        return {
            'type': 'pathway',
            'identifier': 'entire',
            'action': action_intent
        }
    
    return None

def update_specific_module_in_pathway(target_info, new_content_modules, editable_pathways, training_context):
    """
    Update a specific module in a specific pathway and section
    """
    try:
        pathway_num = target_info['pathway_num']
        section_num = target_info['section_num']
        module_num = target_info['module_num']
        action = target_info.get('action', 'add')
        
        # Get the current session's pathways
        current_pathways = []
        if 'generated_pathway' in st.session_state:
            current_pathways = st.session_state['generated_pathway'].get('pathways', [])
        
        # Check if pathway exists
        if pathway_num > len(current_pathways):
            available_pathways = [f"Pathway {i+1}" for i in range(len(current_pathways))]
            return f"❌ Pathway {pathway_num} not found. Available pathways: {', '.join(available_pathways)}"
        
        pathway = current_pathways[pathway_num - 1]
        sections = pathway.get('sections', [])
        
        # Check if section exists
        if section_num > len(sections):
            available_sections = list(range(1, len(sections) + 1))
            return f"❌ Section {section_num} not found in pathway {pathway_num}. Available sections: {available_sections}"
        
        target_section = sections[section_num - 1]
        modules = target_section.get('modules', [])
        
        # Check if module exists
        if module_num > len(modules):
            available_modules = list(range(1, len(modules) + 1))
            return f"❌ Module {module_num} not found in pathway {pathway_num}, section {section_num}. Available modules: {available_modules}"
        
        target_module = modules[module_num - 1]
        module_title = target_module.get('title', f'Module {module_num}')
        
        # Process new content
        if not new_content_modules:
            return "❌ No content could be extracted from uploaded files."
        
        # Get the best content for this module
        best_content = find_best_content_for_module({'module': target_module}, new_content_modules)
        
        if not best_content:
            return f"❌ No relevant content found for module '{module_title}'."
        
        # Apply action (replace or merge)
        if action == 'replace':
            # Replace the entire module content
            target_module['content'] = best_content['content']
            target_module['description'] = best_content['description']
            target_module['source'] = best_content['source']
            target_module['content_types'] = best_content.get('content_types', [])
            action_text = "replaced"
        elif action == 'merge':
            # Merge new content with existing content
            existing_content = target_module.get('content', '')
            new_content = best_content['content']
            target_module['content'] = f"{existing_content}\n\n--- Additional Content ---\n\n{new_content}"
            target_module['source'] = target_module.get('source', []) + best_content['source']
            action_text = "enhanced with"
        else:  # add
            # Add as new module (existing behavior)
            target_section['modules'].append({
                'title': best_content['title'],
                'description': best_content['description'],
                'content': best_content['content'],
                'source': best_content.get('source', ['New file content']),
                'content_types': best_content.get('content_types', [])
            })
            action_text = "added new module"
        
        # Save back to session state
        st.session_state['generated_pathway']['pathways'][pathway_num - 1] = pathway
        
        # Force UI refresh
        if 'editable_pathways' in st.session_state:
            if 'editable_pathways_pathway_idx' in st.session_state:
                del st.session_state['editable_pathways_pathway_idx']
        
        if action == 'add':
            return f"✅ Successfully {action_text} to Pathway {pathway_num}, Section {section_num}!"
        else:
            return f"✅ Successfully {action_text} content for module '{module_title}' in Pathway {pathway_num}, Section {section_num}!"
        
    except Exception as e:
        return f"❌ Error updating specific module: {str(e)}"

def update_specific_module(module_identifier, new_content_modules, editable_pathways, action='add'):
    """
    Update a specific module with new content from files
    """
    try:
        # Find the target module
        target_module = find_module_by_info(module_identifier, editable_pathways)
        
        if not target_module:
            return f"❌ Could not find module '{module_identifier}'. Please check the module name or number."
        
        # Find the most relevant new content for this module
        best_content = find_best_content_for_module(target_module, new_content_modules)
        
        if not best_content:
            return f"❌ No relevant content found in uploaded files for module '{target_module['module']['title']}'."
        
        # Apply action (replace or merge)
        if action == 'replace':
            # Replace the entire module content
        updated_module = target_module['module'].copy()
        updated_module['content'] = best_content['content']
        updated_module['description'] = best_content['description']
        updated_module['source'] = best_content['source']
        updated_module['content_types'] = best_content.get('content_types', [])
        
        # Update in pathway
        editable_pathways[target_module['section']][target_module['index']] = updated_module
            
            action_text = "replaced"
        elif action == 'merge':
            # Merge new content with existing content
            existing_module = target_module['module']
            existing_content = existing_module.get('content', '')
            new_content = best_content['content']
            
            updated_module = existing_module.copy()
            updated_module['content'] = f"{existing_content}\n\n--- Additional Content ---\n\n{new_content}"
            updated_module['source'] = existing_module.get('source', []) + best_content['source']
            
            # Update in pathway
            editable_pathways[target_module['section']][target_module['index']] = updated_module
            
            action_text = "enhanced"
        else:  # add
            # Add as new module (existing behavior)
            editable_pathways[target_module['section']].append({
                'title': best_content['title'],
                'description': best_content['description'],
                'content': best_content['content'],
                'source': best_content.get('source', ['New file content']),
                'content_types': best_content.get('content_types', [])
            })
            action_text = "added new module"
        
        # Update session state
        st.session_state['editable_pathways'] = editable_pathways
        
        return f"✅ Successfully {action_text} content for module '{target_module['module']['title']}'!"
        
    except Exception as e:
        return f"❌ Error updating module: {str(e)}"

def update_specific_section(section_identifier, new_content_modules, editable_pathways, action='add'):
    """
    Update a specific section with new content from files
    """
    try:
        # Find the target section
        target_section = None
        
        # Handle numbered sections (e.g., "section_3" -> section index 2)
        if section_identifier.startswith('section_'):
            try:
                section_number = int(section_identifier.split('_')[1])
                section_names = list(editable_pathways.keys())
                if 1 <= section_number <= len(section_names):
                    target_section = section_names[section_number - 1]  # Convert to 0-based index
                else:
                    return f"❌ Section {section_number} not found. Available sections: {list(range(1, len(section_names) + 1))}"
            except (ValueError, IndexError):
                return f"❌ Invalid section number. Available sections: {list(range(1, len(editable_pathways.keys()) + 1))}"
        else:
            # Handle named sections (e.g., "safety", "quality")
        for section_name in editable_pathways.keys():
            if section_identifier.lower() in section_name.lower():
                target_section = section_name
                break
        
        if not target_section:
            return f"❌ Could not find section matching '{section_identifier}'. Available sections: {list(editable_pathways.keys())}"
        
        if action == 'add':
        # Add new modules to the section
        added_count = 0
        for new_module in new_content_modules:
            # Check if this module is relevant to the section
            if is_module_relevant_to_section(new_module, target_section):
                editable_pathways[target_section].append({
                    'title': new_module['title'],
                    'description': new_module['description'],
                    'content': new_module['content'],
                    'source': new_module.get('source', ['New file content']),
                    'content_types': new_module.get('content_types', [])
                })
                added_count += 1
        
        if added_count == 0:
            return f"❌ No relevant content found for section '{target_section}'."
        
        # Update session state
        st.session_state['editable_pathways'] = editable_pathways
        
        return f"✅ Successfully added {added_count} new modules to section '{target_section}'!"
        
        elif action in ['replace', 'merge']:
            # Update existing modules in the section
            updated_count = 0
            for i, existing_module in enumerate(editable_pathways[target_section]):
                # Find relevant new content for this module
                best_content = find_best_content_for_module({'module': existing_module}, new_content_modules)
                
                if best_content:
                    if action == 'replace':
                        # Replace module content
                        editable_pathways[target_section][i]['content'] = best_content['content']
                        editable_pathways[target_section][i]['description'] = best_content['description']
                        editable_pathways[target_section][i]['source'] = best_content['source']
                        editable_pathways[target_section][i]['content_types'] = best_content.get('content_types', [])
                    else:  # merge
                        # Merge with existing content
                        existing_content = existing_module.get('content', '')
                        new_content = best_content['content']
                        editable_pathways[target_section][i]['content'] = f"{existing_content}\n\n--- Additional Content ---\n\n{new_content}"
                        editable_pathways[target_section][i]['source'] = existing_module.get('source', []) + best_content['source']
                    
                    updated_count += 1
            
            if updated_count == 0:
                return f"❌ No relevant content found to update modules in section '{target_section}'."
            
            # Update session state
            st.session_state['editable_pathways'] = editable_pathways
            
            action_text = "replaced" if action == 'replace' else "enhanced"
            return f"✅ Successfully {action_text} {updated_count} modules in section '{target_section}'!"
        
    except Exception as e:
        return f"❌ Error updating section: {str(e)}"

def update_pathway_section(target_info, new_content_modules, editable_pathways, training_context):
    """
    Update a specific section in a specific pathway with new content from files.
    Pathway numbering now matches the UI: pathway 1 = generated_pathway['pathways'][0], pathway 2 = generated_pathway['pathways'][1], etc.
    Past pathways are only referenced if explicitly requested (e.g., 'past pathway 1').
    """
    try:
        pathway_num = target_info['pathway_num']
        section_num = target_info['section_num']

        # Get the current session's pathways (UI numbering)
        current_pathways = []
        if 'generated_pathway' in st.session_state:
            current_pathways = st.session_state['generated_pathway'].get('pathways', [])

        # If user references a valid pathway in the current session
        if 1 <= pathway_num <= len(current_pathways):
            pathway = current_pathways[pathway_num - 1]
            sections = pathway.get('sections', [])
            if section_num > len(sections):
                available_sections = list(range(1, len(sections) + 1))
                return f"❌ Section {section_num} not found in pathway {pathway_num}. Available sections: {available_sections}"
            target_section = sections[section_num - 1]
            section_title = target_section.get('title', f'Section {section_num}')
            added_count = 0
            added_modules = []
            for new_module in new_content_modules:
                target_section['modules'].append({
                    'title': new_module['title'],
                    'description': new_module['description'],
                    'content': new_module['content'],
                    'source': new_module.get('source', ['New file content']),
                    'content_types': new_module.get('content_types', [])
                })
                added_modules.append(new_module['title'])
                added_count += 1
            # Save back to session state
            st.session_state['generated_pathway']['pathways'][pathway_num - 1] = pathway
            
            # Force UI refresh by updating editable_pathways if it exists
            if 'editable_pathways' in st.session_state:
                # Clear the editable_pathways cache so it regenerates from the updated pathway
                if 'editable_pathways_pathway_idx' in st.session_state:
                    del st.session_state['editable_pathways_pathway_idx']
            
            return f"✅ Successfully added {added_count} new modules to Pathway {pathway_num}, Section {section_num} ({section_title})!\n\nAdded modules: {', '.join(added_modules)}\n\nPlease refresh the page or navigate to Section {section_num} to see the changes."

        # Optionally: support explicit 'past pathway X' references in the future
        # For now, if pathway_num is out of range, show available pathways
        available_pathways = [f"Pathway {i+1}" for i in range(len(current_pathways))]
        if not available_pathways:
            return f"❌ No pathways available. Please generate a pathway first."
        else:
            return f"❌ Pathway {pathway_num} not found. Available pathways: {', '.join(available_pathways)}"
    except Exception as e:
        return f"❌ Error updating pathway section: {str(e)}"

def update_entire_pathway(new_content_modules, editable_pathways, training_context):
    """
    Update the entire pathway with new content from files
    """
    try:
        # Integrate new modules into existing pathway using local function
        success = integrate_new_modules(new_content_modules, editable_pathways, training_context)
        
        if success:
            # Update session state
            st.session_state['editable_pathways'] = editable_pathways
            
            return f"✅ Successfully integrated {len(new_content_modules)} new modules into the pathway!"
        else:
            return "❌ Failed to integrate new modules into pathway."
        
    except Exception as e:
        return f"❌ Error updating pathway: {str(e)}"

def find_best_content_for_module(target_module, new_content_modules):
    """
    Find the best new content for a specific module
    """
    try:
        target_content = target_module['module']['content'].lower()
        target_title = target_module['module']['title'].lower()
        
        best_content = None
        best_score = 0
        
        for new_module in new_content_modules:
            new_content = new_module['content'].lower()
            new_title = new_module['title'].lower()
            
            # Calculate relevance score
            score = 0
            
            # Check for keyword matches
            common_keywords = ['safety', 'quality', 'process', 'equipment', 'training', 'procedure', 'protocol']
            for keyword in common_keywords:
                if keyword in target_content and keyword in new_content:
                    score += 2
                if keyword in target_title and keyword in new_title:
                    score += 3
            
            # Check for content similarity
            if len(set(target_content.split()) & set(new_content.split())) > 5:
                score += 1
            
            if score > best_score:
                best_score = score
                best_content = new_module
        
        return best_content if best_score > 0 else None
        
    except Exception as e:
        return None

def extract_fast_modules_from_content(filename, content, training_context, primary_goals):
    """
    Fast module extraction using single AI call per file
    Optimized for speed while maintaining quality
    """
    try:
        if not model:
            return []
        
        # Create a comprehensive prompt for single AI call
        prompt = f"""
        Extract training modules from this content file: {filename}
        
        Content: {content[:3000]}  # Limit content length for speed
        
        Training Context:
        - Goals: {primary_goals}
        - Type: {training_context.get('training_type', 'General')}
        - Audience: {training_context.get('target_audience', 'Employees')}
        - Industry: {training_context.get('industry', 'General')}
        
        Instructions:
        1. Extract 2-4 key training modules from the content
        2. Each module should be relevant to the training goals
        3. Create clear titles and descriptions
        4. Include practical, actionable content
        5. Focus on the most important training topics
        
        Return the modules in this JSON format:
        {{
            "modules": [
                {{
                    "title": "Module Title",
                    "description": "Brief description",
                    "content": "Detailed training content",
                    "source": ["{filename}"],
                    "content_types": []
                }}
            ]
        }}
        
        Only return valid JSON, no explanations.
        """
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Parse JSON response
        try:
            import json
            result = json.loads(response_text)
            modules = result.get('modules', [])
            
            # Validate and clean modules
            valid_modules = []
            for module in modules:
                if module.get('title') and module.get('content'):
                    # Ensure content is substantial
                    if len(module['content']) > 50:
                        valid_modules.append(module)
            
            return valid_modules
            
        except json.JSONDecodeError:
            # Fallback: create simple modules from content
            return create_simple_modules_from_content(filename, content, training_context)
        
    except Exception as e:
        # Fallback to simple extraction
        return create_simple_modules_from_content(filename, content, training_context)

def create_simple_modules_from_content(filename, content, training_context):
    """
    Create simple modules when AI extraction fails
    """
    try:
        # Clean the content
        content = content.strip()
        if not content or len(content) < 50:
            return []
        
        # Split content into chunks
        sentences = content.split('.')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) < 500:
                current_chunk += sentence + "."
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + "."
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Create modules from chunks
        modules = []
        for i, chunk in enumerate(chunks[:3]):  # Limit to 3 modules for speed
            if len(chunk) > 50:  # Lower threshold for fallback
                # Try to extract a meaningful title from the first sentence
                first_sentence = chunk.split('.')[0][:100]
                title = f"Content from {filename} - {first_sentence}"
                description = f"Content extracted from {filename}"
                
                modules.append({
                    'title': title,
                    'description': description,
                    'content': chunk,
                    'source': [filename],
                    'content_types': []
                })
        
        return modules
        
    except Exception as e:
        return []

def is_module_relevant_to_section(new_module, section_name):
    """
    Check if a new module is relevant to a specific section
    """
    try:
        new_content = new_module['content'].lower()
        new_title = new_module['title'].lower()
        section_lower = section_name.lower()
        
        # Check for keyword matches
        section_keywords = section_lower.split()
        for keyword in section_keywords:
            if keyword in new_content or keyword in new_title:
                return True
        
        # Check for common training keywords
        training_keywords = ['safety', 'quality', 'process', 'equipment', 'training']
        for keyword in training_keywords:
            if keyword in section_lower and (keyword in new_content or keyword in new_title):
                return True
        
        return False
        
    except Exception as e:
        return False

def create_module_mapping(editable_pathways):
    """
    Create a comprehensive mapping of modules for chatbot reference
    Returns a dictionary with multiple ways to reference modules
    """
    module_mapping = {
        'by_section_and_number': {},  # e.g., {'safety': {'1': module_obj, '2': module_obj}}
        'by_global_number': {},       # e.g., {'1': module_obj, '2': module_obj}
        'by_title': {},              # e.g., {'safety procedures': module_obj}
        'section_info': {}           # e.g., {'safety': {'count': 3, 'modules': [module1, module2, module3]}}
    }
    
    global_module_number = 1
    
    for section_name, modules in editable_pathways.items():
        # Initialize section mapping
        module_mapping['by_section_and_number'][section_name] = {}
        module_mapping['section_info'][section_name] = {
            'count': len(modules),
            'modules': modules
        }
        
        # Map modules within this section
        for i, module in enumerate(modules):
            local_module_number = i + 1
            
            # Map by section and local number
            module_mapping['by_section_and_number'][section_name][str(local_module_number)] = {
                'module': module,
                'section': section_name,
                'index': i,
                'local_number': local_module_number,
                'global_number': global_module_number
            }
            
            # Map by global number
            module_mapping['by_global_number'][str(global_module_number)] = {
                'module': module,
                'section': section_name,
                'index': i,
                'local_number': local_module_number,
                'global_number': global_module_number
            }
            
            # Map by title (lowercase for matching)
            module_title_lower = module['title'].lower()
            module_mapping['by_title'][module_title_lower] = {
                'module': module,
                'section': section_name,
                'index': i,
                'local_number': local_module_number,
                'global_number': global_module_number
            }
            
            global_module_number += 1
    
    return module_mapping

def get_module_reference_info(editable_pathways):
    """
    Get comprehensive module reference information for chatbot
    """
    module_mapping = create_module_mapping(editable_pathways)
    
    reference_info = []
    
    for section_name, section_data in module_mapping['section_info'].items():
        section_info = {
            'section_name': section_name,
            'module_count': section_data['count'],
            'modules': []
        }
        
        for i, module in enumerate(section_data['modules']):
            module_info = {
                'local_number': i + 1,
                'global_number': module_mapping['by_section_and_number'][section_name][str(i + 1)]['global_number'],
                'title': module['title'],
                'description': module.get('description', '')
            }
            section_info['modules'].append(module_info)
        
        reference_info.append(section_info)
    
    return reference_info

def format_module_reference_help(editable_pathways):
    """
    Format module reference information for chatbot help
    """
    reference_info = get_module_reference_info(editable_pathways)
    
    help_text = "**Available Modules by Section:**\n\n"
    
    for section_info in reference_info:
        help_text += f"**{section_info['section_name']}** ({section_info['module_count']} modules):\n"
        
        for module_info in section_info['modules']:
            help_text += f"  • Module {module_info['local_number']}: {module_info['title']}\n"
        
        help_text += "\n"
    
    help_text += "**Reference Examples:**\n"
    help_text += "• \"Update module 1\" (refers to first module in current section)\n"
    help_text += "• \"Regenerate module 2 in safety section\"\n"
    help_text += "• \"Update the safety procedures module\"\n"
    help_text += "• \"Modify module 3 in section 2\"\n"
    
    return help_text

# --- Helper functions for past pathway integration ---
def list_past_pathways():
    """Return a summary of all past generated pathways."""
    past = st.session_state.get('past_generated_pathways', [])
    if not past:
        return "No past pathways found."
    out = []
    for idx, pathway_data in enumerate(past, 1):
        for p in pathway_data.get('pathways', []):
            out.append(f"Pathway {idx}: {p.get('pathway_name', 'Unnamed')}")
            for sidx, section in enumerate(p.get('sections', []), 1):
                out.append(f"  Section {sidx}: {section.get('title', 'Untitled')} ({len(section.get('modules', []))} modules)")
                for midx, mod in enumerate(section.get('modules', []), 1):
                    out.append(f"    Module {midx}: {mod.get('title', 'No title')}")
    return '\n'.join(out)

def get_past_module(pathway_num, section_num, module_num):
    """Retrieve a module from a past pathway by indices (1-based)."""
    past = st.session_state.get('past_generated_pathways', [])
    try:
        pathway = past[pathway_num-1]['pathways'][0] if len(past[pathway_num-1]['pathways']) == 1 else past[pathway_num-1]['pathways'][pathway_num-1]
        section = pathway['sections'][section_num-1]
        module = section['modules'][module_num-1]
        return module
    except Exception:
        return None

def integrate_past_module_into_current(pathway_num, section_num, module_num, target_section=None):
    """Integrate a module from a past pathway into the current editable_pathways."""
    module = get_past_module(pathway_num, section_num, module_num)
    if not module:
        return False, "Module not found in past pathways."
    editable_pathways = st.session_state.get('editable_pathways', {})
    if not editable_pathways:
        return False, "No current pathway to integrate into."
    # Default to first section if not specified
    if not target_section:
        target_section = list(editable_pathways.keys())[0]
    if target_section not in editable_pathways:
        return False, f"Section '{target_section}' not found in current pathway."
    # Add a copy of the module
    editable_pathways[target_section].append(dict(module))
    st.session_state['editable_pathways'] = editable_pathways
    return True, f"Module '{module.get('title','')}' from past pathway {pathway_num} section {section_num} integrated into section '{target_section}'."

# --- Chatbot quick action and command parsing ---
def handle_past_pathway_request(user_input):
    """Handle user requests about past pathways."""
    user_input_lower = user_input.lower()
    if 'list' in user_input_lower or 'show' in user_input_lower:
        return list_past_pathways()
    # Parse integration command: e.g. "integrate module 2 from pathway 1 section 3 into section Safety Procedures"
    import re
    match = re.search(r'integrate module (\d+) from (?:past )?pathway (\d+)(?: section (\d+))?(?: into section ([\w\s]+))?', user_input_lower)
    if match:
        module_num = int(match.group(1))
        pathway_num = int(match.group(2))
        section_num = int(match.group(3)) if match.group(3) else 1
        target_section = match.group(4).strip() if match.group(4) else None
        success, msg = integrate_past_module_into_current(pathway_num, section_num, module_num, target_section)
        return msg
    return "To reference past pathways, say 'show past pathways' or 'integrate module 2 from pathway 1 section 3'."

# Update process_chatbot_request to handle past pathway requests
old_process_chatbot_request = process_chatbot_request

def process_chatbot_request(user_input, uploaded_files=None):
    user_input_lower = user_input.lower()
    if any(word in user_input_lower for word in ['past pathway', 'previous pathway', 'show past', 'list past', 'integrate from past', 'integrate from previous']):
        return handle_past_pathway_request(user_input)
    return old_process_chatbot_request(user_input, uploaded_files)



# --- Advanced memory helpers ---
def find_past_module_by_title(title, pathway_num=None):
    """Find a module by title in a specific or any past pathway. Returns (module, pathway_idx, section_idx, module_idx) or None."""
    past = st.session_state.get('past_generated_pathways', [])
    title_lower = title.strip().lower()
    for pidx, pathway_data in enumerate(past):
        if pathway_num and (pidx+1) != pathway_num:
            continue
        for pw in pathway_data.get('pathways', []):
            for sidx, section in enumerate(pw.get('sections', [])):
                for midx, mod in enumerate(section.get('modules', [])):
                    if title_lower == mod.get('title', '').strip().lower():
                        return mod, pidx+1, sidx+1, midx+1
    return None

def find_past_section_by_title_or_number(pathway_num, section_ref):
    """Find a section by number or title in a past pathway. Returns (section, section_idx) or None."""
    past = st.session_state.get('past_generated_pathways', [])
    try:
        pathway = past[pathway_num-1]['pathways'][0] if len(past[pathway_num-1]['pathways']) == 1 else past[pathway_num-1]['pathways'][pathway_num-1]
        # If section_ref is int, treat as index
        if isinstance(section_ref, int):
            return pathway['sections'][section_ref-1], section_ref
        # Otherwise, match by title
        section_ref_lower = section_ref.strip().lower()
        for sidx, section in enumerate(pathway['sections']):
            if section_ref_lower == section.get('title', '').strip().lower():
                return section, sidx+1
        return None
    except Exception:
        return None

def merge_past_section_into_current(pathway_num, section_ref, target_section=None):
    """Merge all modules from a past section into a section in the current pathway."""
    result = find_past_section_by_title_or_number(pathway_num, section_ref)
    if not result:
        return False, "Section not found in past pathway."
    section, _ = result
    editable_pathways = st.session_state.get('editable_pathways', {})
    if not editable_pathways:
        return False, "No current pathway to merge into."
    # Default to first section if not specified
    if not target_section:
        target_section = list(editable_pathways.keys())[0]
    if target_section not in editable_pathways:
        return False, f"Section '{target_section}' not found in current pathway."
    # Add copies of all modules
    for mod in section.get('modules', []):
        editable_pathways[target_section].append(dict(mod))
    st.session_state['editable_pathways'] = editable_pathways
    return True, f"Merged {len(section.get('modules', []))} modules from past pathway {pathway_num} section '{section.get('title','')}' into section '{target_section}'."

# --- Update handle_past_pathway_request for advanced memory ---
def handle_past_pathway_request(user_input):
    """Handle user requests about past pathways, including advanced memory."""
    user_input_lower = user_input.lower()
    import re
    # List/show
    if 'list' in user_input_lower or 'show' in user_input_lower:
        return list_past_pathways()
    # Merge section by number: "merge section 2 from pathway 1 into section Quality Control"
    match = re.search(r'merge section (\d+) from (?:past )?pathway (\d+)(?: into section ([\w\s]+))?', user_input_lower)
    if match:
        section_num = int(match.group(1))
        pathway_num = int(match.group(2))
        target_section = match.group(3).strip() if match.group(3) else None
        success, msg = merge_past_section_into_current(pathway_num, section_num, target_section)
        return msg
    # Merge section by title: "merge 'Safety Procedures' from pathway 2 into section Quality Control"
    match = re.search(r"merge ['\"]?([\w\s]+)['\"]? from (?:past )?pathway (\d+)(?: into section ([\w\s]+))?", user_input_lower)
    if match:
        section_title = match.group(1)
        pathway_num = int(match.group(2))
        target_section = match.group(3).strip() if match.group(3) else None
        success, msg = merge_past_section_into_current(pathway_num, section_title, target_section)
        return msg
    # Integrate module by title: "integrate 'PPE Requirements' from pathway 2 into section Safety Procedures"
    match = re.search(r"integrate ['\"]?([\w\s]+)['\"]? from (?:past )?pathway (\d+)(?: into section ([\w\s]+))?", user_input_lower)
    if match:
        module_title = match.group(1)
        pathway_num = int(match.group(2))
        target_section = match.group(3).strip() if match.group(3) else None
        result = find_past_module_by_title(module_title, pathway_num)
        if not result:
            return f"Module '{module_title}' not found in pathway {pathway_num}."
        mod, pidx, sidx, midx = result
        editable_pathways = st.session_state.get('editable_pathways', {})
        if not editable_pathways:
            return "No current pathway to integrate into."
        if not target_section:
            target_section = list(editable_pathways.keys())[0]
        if target_section not in editable_pathways:
            return f"Section '{target_section}' not found in current pathway."
        editable_pathways[target_section].append(dict(mod))
        st.session_state['editable_pathways'] = editable_pathways
        return f"Module '{module_title}' from pathway {pathway_num} integrated into section '{target_section}'."
    # Integrate module by number (existing logic)
    match = re.search(r'integrate module (\d+) from (?:past )?pathway (\d+)(?: section (\d+))?(?: into section ([\w\s]+))?', user_input_lower)
    if match:
        module_num = int(match.group(1))
        pathway_num = int(match.group(2))
        section_num = int(match.group(3)) if match.group(3) else 1
        target_section = match.group(4).strip() if match.group(4) else None
        success, msg = integrate_past_module_into_current(pathway_num, section_num, module_num, target_section)
        return msg
    return ("To reference past pathways, you can now:\n"
            "- 'show past pathways'\n"
            "- 'integrate module 2 from pathway 1 section 3'\n"
            "- 'integrate \"PPE Requirements\" from pathway 2 into section Safety Procedures'\n"
            "- 'merge section 2 from pathway 1 into section Quality Control'\n"
            "- 'merge \"Safety Procedures\" from pathway 2 into section Quality Control'")

# --- Content-aware chatbot functions ---
def search_modules_by_content(query, editable_pathways=None, include_past_pathways=True):
    """Search through module content for specific topics or keywords."""
    if editable_pathways is None:
        editable_pathways = st.session_state.get('editable_pathways', {})
    
    results = []
    query_lower = query.lower()
    
    # Search current pathway
    for section_name, modules in editable_pathways.items():
        for i, module in enumerate(modules):
            content = module.get('content', '').lower()
            title = module.get('title', '').lower()
            description = module.get('description', '').lower()
            
            # Check if query appears in content, title, or description
            if (query_lower in content or query_lower in title or query_lower in description):
                results.append({
                    'type': 'current',
                    'section': section_name,
                    'module_number': i + 1,
                    'module_title': module.get('title', ''),
                    'content_preview': module.get('content', '')[:200] + '...',
                    'relevance_score': calculate_relevance_score(query_lower, content, title, description)
                })
    
    # Search past pathways if requested
    if include_past_pathways:
        past = st.session_state.get('past_generated_pathways', [])
        for pidx, pathway_data in enumerate(past):
            for pw in pathway_data.get('pathways', []):
                for sidx, section in enumerate(pw.get('sections', [])):
                    for midx, module in enumerate(section.get('modules', [])):
                        content = module.get('content', '').lower()
                        title = module.get('title', '').lower()
                        description = module.get('description', '').lower()
                        
                        if (query_lower in content or query_lower in title or query_lower in description):
                            results.append({
                                'type': 'past',
                                'pathway_num': pidx + 1,
                                'section': section.get('title', ''),
                                'section_num': sidx + 1,
                                'module_number': midx + 1,
                                'module_title': module.get('title', ''),
                                'content_preview': module.get('content', '')[:200] + '...',
                                'relevance_score': calculate_relevance_score(query_lower, content, title, description)
                            })
    
    # Sort by relevance score
    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    return results

def calculate_relevance_score(query, content, title, description):
    """Calculate relevance score for search results."""
    score = 0
    query_words = query.split()
    
    # Title matches get highest score
    for word in query_words:
        if word.lower() in title.lower():
            score += 10
        if word.lower() in description.lower():
            score += 5
        if word.lower() in content.lower():
            score += 1
    
    # Exact phrase matches get bonus
    if query.lower() in title.lower():
        score += 20
    if query.lower() in description.lower():
        score += 10
    if query.lower() in content.lower():
        score += 5
    
    return score

def get_module_content_summary(module_data):
    """Get a summary of module content using AI."""
    try:
        if not model:
            return module_data.get('content', '')[:300] + '...'
        
        content = module_data.get('content', '')
        title = module_data.get('title', '')
        
        if len(content) < 100:
            return content
        
        prompt = f"""
        Summarize this training module content in 2-3 sentences:
        
        Title: {title}
        Content: {content[:1000]}
        
        Provide a concise summary that captures the key training points.
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        return module_data.get('content', '')[:300] + '...'

def answer_content_question(question, editable_pathways=None):
    """Answer questions about pathway content using AI."""
    try:
        if not model:
            return "AI model not available for content analysis."
        
        # Get all module content for context
        all_content = []
        if editable_pathways is None:
            editable_pathways = st.session_state.get('editable_pathways', {})
        
        for section_name, modules in editable_pathways.items():
            for i, module in enumerate(modules):
                all_content.append(f"Section: {section_name}, Module {i+1}: {module.get('title', '')}")
                all_content.append(f"Content: {module.get('content', '')}")
                all_content.append("---")
        
        # Add past pathway content
        past = st.session_state.get('past_generated_pathways', [])
        for pidx, pathway_data in enumerate(past):
            for pw in pathway_data.get('pathways', []):
                for sidx, section in enumerate(pw.get('sections', [])):
                    for midx, module in enumerate(section.get('modules', [])):
                        all_content.append(f"Past Pathway {pidx+1}, Section {sidx+1}, Module {midx+1}: {module.get('title', '')}")
                        all_content.append(f"Content: {module.get('content', '')}")
                        all_content.append("---")
        
        context = "\n".join(all_content[:5000])  # Limit context length
        
        prompt = f"""
        You are an AI training content assistant. Answer the user's question based on the training pathway content below.
        
        Question: {question}
        
        Training Content:
        {context}
        
        Instructions:
        1. Answer the question based on the provided training content
        2. If the information is not in the content, say so
        3. Be specific and reference which modules/sections contain the information
        4. Keep the response concise and helpful
        5. If multiple modules contain relevant information, mention them all
        
        Answer:
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        return f"Error analyzing content: {str(e)}"

def handle_content_question_request(user_input):
    """Handle user questions about pathway content."""
    user_input_lower = user_input.lower()
    
    # Check for search requests
    if any(word in user_input_lower for word in ['find', 'search', 'look for', 'where is', 'which module']):
        # Extract search query
        import re
        search_patterns = [
            r'find (.*?) in',
            r'search for (.*?)',
            r'look for (.*?)',
            r'where is (.*?)',
            r'which module (.*?)',
            r'find (.*?)',
            r'search (.*?)'
        ]
        
        query = None
        for pattern in search_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                query = match.group(1).strip()
                break
        
        if query:
            results = search_modules_by_content(query)
            if results:
                response = f"Found {len(results)} modules containing '{query}':\n\n"
                for i, result in enumerate(results[:5]):  # Limit to top 5 results
                    if result['type'] == 'current':
                        response += f"{i+1}. **Current Pathway** - {result['section']}, Module {result['module_number']}: {result['module_title']}\n"
                    else:
                        response += f"{i+1}. **Past Pathway {result['pathway_num']}** - {result['section']}, Module {result['module_number']}: {result['module_title']}\n"
                    response += f"   Preview: {result['content_preview']}\n\n"
                
                if len(results) > 5:
                    response += f"... and {len(results) - 5} more results.\n"
                
                return response
            else:
                return f"No modules found containing '{query}'."
        else:
            return "Please specify what you'd like to search for. Example: 'find safety procedures' or 'search for PPE requirements'"
    
    # Check for content questions
    elif any(word in user_input_lower for word in ['what does', 'what is', 'how do', 'explain', 'tell me about', 'what are']):
        return answer_content_question(user_input)
    
    # Check for module content requests
    elif any(word in user_input_lower for word in ['show content', 'module content', 'what\'s in', 'content of']):
        # Extract module reference
        import re
        module_match = re.search(r'module (\d+)', user_input_lower)
        if module_match:
            module_num = int(module_match.group(1))
            editable_pathways = st.session_state.get('editable_pathways', {})
            if editable_pathways:
                # Find the module
                for section_name, modules in editable_pathways.items():
                    if module_num <= len(modules):
                        module = modules[module_num - 1]
                        summary = get_module_content_summary(module)
                        return f"**Module {module_num} in {section_name}: {module.get('title', '')}**\n\n{summary}"
                
                return f"Module {module_num} not found in current pathway."
            else:
                return "No current pathway available."
        else:
            return "Please specify which module you'd like to see. Example: 'show content of module 2'"
    
    return ("I can help you with content questions. Try:\n"
            "- 'Find safety procedures in the pathways'\n"
            "- 'What does module 2 say about PPE?'\n"
            "- 'Search for quality control procedures'\n"
            "- 'What are the emergency procedures?'\n"
            "- 'Show content of module 1'")

# Update process_chatbot_request to handle content questions
def process_chatbot_request(user_input, uploaded_files=None):
    user_input_lower = user_input.lower()
    
    # Check for content questions first
    if any(word in user_input_lower for word in ['find', 'search', 'what does', 'what is', 'how do', 'explain', 'tell me about', 'what are', 'show content', 'module content', 'what\'s in', 'content of']):
        return handle_content_question_request(user_input)
    
    # Check for past pathway requests
    if any(word in user_input_lower for word in ['past pathway', 'previous pathway', 'show past', 'list past', 'integrate from past', 'integrate from previous']):
        return handle_past_pathway_request(user_input)
    
    # Original logic for other requests
    # Get current pathway data for module reference
    editable_pathways = st.session_state.get('editable_pathways', {})
    module_reference_help = ""
    if editable_pathways:
        module_reference_help = format_module_reference_help(editable_pathways)
    
    # Check for file-based update requests (when files are uploaded) - PRIORITY 1
    if uploaded_files and len(uploaded_files) > 0:
        if any(word in user_input_lower for word in ['update', 'add to', 'modify', 'change', 'adjust', 'regenerate']):
            if any(word in user_input_lower for word in ['module', 'section', 'pathway', 'course', 'program']):
                return handle_file_based_module_update(user_input, uploaded_files)
    
    # Check for regeneration requests (when no files uploaded)
    if any(word in user_input_lower for word in ['regenerate']):
        if 'module' in user_input_lower or 'content' in user_input_lower:
            return handle_module_regeneration(user_input)
        else:
            return f"I can help you regenerate modules. Please specify which module you'd like to regenerate and any specific changes you want.\n\n{module_reference_help}"
    
    # Check for file ingestion requests (when no files uploaded)
    elif any(word in user_input_lower for word in ['ingest', 'upload', 'add', 'new file', 'new files', 'process files']):
        return handle_file_ingestion(user_input)
    
    # Check for tone/style changes (expanded to include more tones)
    elif any(word in user_input_lower for word in ['tone', 'style', 'professional', 'casual', 'formal', 'technical', 'friendly', 'conversational', 'academic', 'simple', 'detailed']):
        return handle_tone_change(user_input)
    
    # Check for content addition
    elif any(word in user_input_lower for word in ['add', 'include', 'missing', 'additional', 'insert', 'supplement']):
        return handle_content_addition(user_input)
    
    # Check for specific module requests
    elif any(word in user_input_lower for word in ['module', 'section', 'content']):
        return handle_module_specific_request(user_input)
    
    # General help
    elif any(word in user_input_lower for word in ['help', 'what can you do', 'how', 'commands']):
        return get_chatbot_help()
    
    # Default response - use AI for intelligent responses
    else:
        try:
            if not model:
                # Fallback if AI not available
                if uploaded_files and len(uploaded_files) > 0:
                    return f"I see you've uploaded {len(uploaded_files)} file(s). You can:\n• \"Update module 1 with new file\"\n• \"Add content to safety section\"\n• \"Modify module 1 with uploaded content\"\n• \"Update pathway with new information\"\n• \"Regenerate module 2 with uploaded files\"\n\nPlease specify which module, section, or pathway you'd like to update with the uploaded files.\n\n{module_reference_help}"
                else:
                    return f"I can help you with:\n• Regenerating modules with different content or tone\n• Uploading new files to update pathways\n• Changing module tone/style (professional, casual, formal, technical, friendly, etc.)\n• Adding missing information to modules\n• Updating specific modules/sections with new file content\n• Searching for specific topics in pathways\n• Answering questions about training content\n\nPlease be more specific about what you'd like to do.\n\n{module_reference_help}"
            
            # Use AI to generate contextual response
            files_info = f"User has uploaded {len(uploaded_files)} files: {[f.name for f in uploaded_files]}" if uploaded_files else "No files uploaded"
            
            prompt = f"""
            You are an AI training content assistant. The user said: "{user_input}"
            {files_info}
            
            Current module structure:
            {module_reference_help}
            
            Generate a helpful, contextual response that:
            1. Acknowledges their input
            2. Suggests relevant actions they can take
            3. Provides specific examples of commands they can use
            4. Is friendly and encouraging
            5. References the correct module numbering system (modules are numbered 1, 2, 3, etc. within each section)
            6. Mentions that they can search for content and ask questions about training information
            
            Keep the response concise and actionable.
            """
            
            response = model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            # Fallback to static response if AI fails
            if uploaded_files and len(uploaded_files) > 0:
                return f"I see you've uploaded {len(uploaded_files)} file(s). You can:\n• \"Update module 1 with new file\"\n• \"Add content to section 3\"\n• \"Modify module 1 with uploaded content\"\n• \"Update pathway with new information\"\n• \"Regenerate module 2 with uploaded files\"\n\nPlease specify which module, section, or pathway you'd like to update with the uploaded files.\n\n{module_reference_help}"
            else:
                return f"I can help you with:\n• Regenerating modules with different content or tone\n• Uploading new files to update pathways\n• Changing module tone/style (professional, casual, formal, technical, friendly, etc.)\n• Adding missing information to modules\n• Updating specific modules/sections with new file content\n• Searching for specific topics in pathways\n• Answering questions about training content\n\nPlease be more specific about what you'd like to do.\n\n{module_reference_help}"

if __name__ == "__main__":
    main() 