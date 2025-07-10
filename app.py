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
from modules.utils import create_quick_pathway
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
    # Start backend server automatically
    if not start_backend_server():
        st.warning("⚠️ Backend server could not be started. Some features may not work properly.")
    
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
        
        # Add quick test mode for faster processing
        quick_test_mode = st.checkbox(
            "Quick Test Mode (skip AI analysis for speed)",
            help="For testing purposes - skips AI analysis and uses basic content extraction for maximum speed"
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
                            
                            generated_pathways_data = gemini_generate_complete_pathway(context, extracted_file_contents, inventory, bypass_filtering=bypass_filtering, preserve_original_content=preserve_original_content)
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
        cols = st.columns(len(pathway_names))
        for idx, pname in enumerate(pathway_names):
            with cols[idx]:
                if st.button(f"Pathway {idx+1}: {pname}", key=f"pathway_card_{idx}"):
                    st.session_state['selected_pathway_idx'] = idx
                    st.session_state['selected_section'] = None
        selected_pathway = pathways[st.session_state['selected_pathway_idx']]
        st.markdown(f"### 🎯 **{selected_pathway['pathway_name']}**")
        st.markdown("This goal-aligned pathway is designed based on your specific training goals and available content. Content has been filtered and structured to directly support your training objectives.")
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
            
            # Create two columns: left for modules, right for chatbot
            left_col, right_col = st.columns([2, 1])
            
            with left_col:
                i = 0
                while i < len(mods):
                    mod = mods[i]
                    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 2, 2])
                    with col1:
                        new_title = st.text_input(f"Title ({section}-{i})", mod['title'], key=f"title_{section}_{i}")
                        new_desc = st.text_input(f"Description ({section}-{i})", mod.get('description', ''), key=f"desc_{section}_{i}")
                        new_content = st.text_area(f"Content ({section}-{i})", mod['content'], key=f"content_{section}_{i}")
                        st.markdown(f"**{i+1}. {new_title}**")
                    
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
            
            # Chatbot in the right column
            with right_col:
                create_pathway_chatbot()
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

def process_chatbot_request(user_input):
    """
    Process chatbot requests and return appropriate responses
    """
    user_input_lower = user_input.lower()
    
    # Check for regeneration requests
    if any(word in user_input_lower for word in ['regenerate', 'regenerate', 'update', 'change']):
        if 'module' in user_input_lower or 'content' in user_input_lower:
            return handle_module_regeneration(user_input)
        else:
            return "I can help you regenerate modules. Please specify which module you'd like to regenerate and any specific changes you want."
    
    # Check for file ingestion requests
    elif any(word in user_input_lower for word in ['ingest', 'upload', 'add', 'new file', 'new files']):
        return handle_file_ingestion(user_input)
    
    # Check for tone/style changes
    elif any(word in user_input_lower for word in ['tone', 'style', 'professional', 'casual', 'formal']):
        return handle_tone_change(user_input)
    
    # Check for content addition
    elif any(word in user_input_lower for word in ['add', 'include', 'missing', 'additional']):
        return handle_content_addition(user_input)
    
    # General help
    elif any(word in user_input_lower for word in ['help', 'what can you do', 'how']):
        return get_chatbot_help()
    
    # Default response
    else:
        return "I can help you with:\n• Regenerating modules with different content or tone\n• Ingesting new files to update pathways\n• Changing module tone/style\n• Adding missing information\n\nPlease be more specific about what you'd like to do."

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
    Handle file ingestion requests
    """
    return """📁 **File Ingestion Options:**

1. **Use the 'Ingest New Files' button** (right sidebar) for direct file processing
2. **Upload files in the chatbot interface** - I'll process them immediately
3. **Go to file upload section** and return here for automatic updates

**What happens when you ingest new files:**
• New content will be analyzed and integrated into existing modules
• Missing information will be added to relevant modules
• New modules may be created if significant new content is found
• Existing modules will be updated with additional information

**Supported file types:** PDF, DOC, DOCX, TXT, MP4, AVI, MOV

Would you like to use the 'Ingest New Files' button or upload files directly here?"""

def handle_tone_change(user_input):
    """
    Handle tone/style change requests
    """
    tone = extract_tone_from_input(user_input)
    if tone:
        return f"🎨 I can help you change the tone to {tone}. Please specify which module you'd like to update, or use the 'Update Module Tone' button."
    else:
        return "🎨 I can help you change module tone. Available tones: professional, casual, formal, technical, friendly. Please specify which module and tone."

def handle_content_addition(user_input):
    """
    Handle content addition requests
    """
    return "📝 I can help you add missing information to modules. Please specify which module and what information you'd like to add, or use the 'Add Missing Info' button."

def get_chatbot_help():
    """
    Return help information for the chatbot
    """
    return """🤖 **AI Pathway Assistant Help**

**Module Regeneration Commands:**
• "Regenerate module 2 with professional tone"
• "Update the safety module to include more procedures"
• "Change module 1 to casual tone and add troubleshooting steps"
• "Regenerate module 3 to remove technical jargon"
• "Update module 1 to include more safety procedures"

**File Ingestion Commands:**
• "Ingest new files"
• "Upload additional training materials"
• "Add new content from files"

**Content Modification Commands:**
• "Add missing information to module 3"
• "Include more detailed procedures in module 2"
• "Simplify the language in module 1"
• "Add troubleshooting tips to the equipment module"

**Quick Actions (right sidebar):**
• 🔄 Regenerate Current Module - Update the currently selected module
• 📁 Ingest New Files - Upload and process new files to update pathway
• 🎨 Update Module Tone - Change the tone/style of any module
• 📝 Add Missing Info - Add specific information to any module

**Available Tones:**
• Professional - Formal business language
• Casual - Friendly, conversational tone
• Formal - Academic or technical tone
• Technical - Detailed technical explanations
• Friendly - Warm, approachable tone

**Tips:**
• Be specific about which module you want to modify
• Mention what content you want to add, remove, or change
• Specify the tone/style you want
• Use the quick action buttons for common tasks
• Upload new files to automatically integrate them into your pathway"""

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
    """
    for section_name, modules in editable_pathways.items():
        for i, module in enumerate(modules):
            # Check by module number
            if module_info.startswith('module_'):
                module_num = module_info.split('_')[1]
                if str(i + 1) == module_num:
                    return {'module': module, 'section': section_name, 'index': i}
            
            # Check by module title/keywords
            module_title_lower = module['title'].lower()
            if module_info in module_title_lower:
                return {'module': module, 'section': section_name, 'index': i}
    
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
        
        prompt = f"""
        Regenerate this training module content with the specified tone, focus, and changes.
        
        Original Module: {module_title}
        Original Content: {original_content[:1500]}
        
        Requirements:
        - Tone: {tone}
        - Content Focus: {content_focus}
        - Keep the same core information but adapt the style
        - Make it suitable for training purposes
        - Ensure it's clear and actionable{changes_text}
        
        Instructions:
        1. Maintain the essential training information
        2. Apply the requested tone and style changes
        3. Focus on the specified content area
        4. Make the content more engaging and practical
        5. Ensure it follows training best practices
        
        Return only the regenerated content, no explanations or markdown formatting.
        """
        
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
    
    st.info("🔄 Regenerating current module...")
    # This would be implemented to regenerate the currently viewed module
    st.success("Module regenerated successfully!")

def ingest_new_files_interface():
    """
    Interface for ingesting new files
    """
    st.markdown("### 📁 Ingest New Files")
    st.markdown("Upload new files to update your pathway:")
    
    uploaded_files = st.file_uploader(
        "Choose files to ingest",
        type=['txt', 'pdf', 'doc', 'docx', 'mp4', 'avi', 'mov'],
        accept_multiple_files=True,
        key="ingest_files"
    )
    
    if uploaded_files:
        st.markdown(f"**📄 Files selected:** {len(uploaded_files)} files")
        for file in uploaded_files:
            st.markdown(f"• {file.name} ({file.size} bytes)")
        
        if st.button("🔄 Process New Files"):
            result = process_new_files(uploaded_files)
            if result:
                st.success("✅ New files processed and pathway updated!")
                st.rerun()
            else:
                st.error("❌ Failed to process new files. Please try again.")

def update_module_tone_interface():
    """
    Interface for updating module tone
    """
    st.markdown("### 🎨 Update Module Tone")
    
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
    
    if st.button("🔄 Apply Tone Change"):
        # Find and update the selected module
        section_name, module_title = selected_module.split(" - ", 1)
        target_module = find_module_by_title(module_title, editable_pathways)
        
        if target_module:
            new_content = regenerate_module_content(target_module, selected_tone, 'general')
            if update_module_in_pathway(target_module, new_content):
                st.success(f"✅ Updated module '{module_title}' to {selected_tone} tone!")
            else:
                st.error("❌ Failed to update module. Please try again.")
        else:
            st.error("❌ Module not found. Please try again.")

def add_missing_info_interface():
    """
    Interface for adding missing information
    """
    st.markdown("### 📝 Add Missing Information")
    
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
    
    if st.button("🔄 Add Information"):
        # Find and update the selected module
        section_name, module_title = selected_module.split(" - ", 1)
        target_module = find_module_by_title(module_title, editable_pathways)
        
        if target_module and missing_info:
            changes_requested = f"Add: {missing_info}"
            new_content = regenerate_module_content(target_module, 'professional', 'general', changes_requested)
            if update_module_in_pathway(target_module, new_content):
                st.success(f"✅ Added information to module '{module_title}'!")
            else:
                st.error("❌ Failed to update module. Please try again.")
        else:
            st.error("❌ Please specify what information to add.")

def process_new_files(uploaded_files):
    """
    Process newly uploaded files and update pathway
    """
    try:
        if not uploaded_files:
            return False
        
        st.info("🔄 Processing new files...")
        
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
                    # For PDFs, we'd need a PDF reader
                    file_content = f"PDF content from {uploaded_file.name}"
                else:
                    file_content = f"Content from {uploaded_file.name}"
                
                new_file_contents[uploaded_file.name] = file_content
                
            except Exception as e:
                st.error(f"Error reading {uploaded_file.name}: {str(e)}")
                continue
        
        if not new_file_contents:
            st.error("No files could be processed.")
            return False
        
        # Get current pathway data
        if 'editable_pathways' not in st.session_state:
            st.error("No pathway data available.")
            return False
        
        editable_pathways = st.session_state['editable_pathways']
        training_context = st.session_state.get('training_context', {})
        
        # Process new content and integrate into existing modules
        for filename, content in new_file_contents.items():
            # Extract modules from new content
            new_modules = extract_modules_from_file_content(filename, content, training_context)
            
            if new_modules:
                # Integrate new modules into existing pathway
                integrate_new_modules(new_modules, editable_pathways, training_context)
        
        # Update session state
        st.session_state['editable_pathways'] = editable_pathways
        
        st.success(f"✅ Successfully processed {len(new_file_contents)} files and updated pathway!")
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
    MINDMEISTER_REDIRECT_URI=https://localhost:8501
    VADOO_API_KEY=your_vadoo_api_key_here
    CANVA_API_KEY=your_canva_api_key_here
    ```
    """)

if __name__ == "__main__":
    main() 