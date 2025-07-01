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

# Import from our modules
from modules.config import *
from modules.utils import extract_key_topics_from_content, calculate_text_dimensions
from modules.mindmeister import (
    create_mindmeister_mind_map,
    create_mindmeister_ai_mind_map,
    create_enhanced_mindmeister_mind_map,
    display_mind_map_from_session,
    create_simple_mind_map
)
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
    steps = ["Training Context", "File Inventory", "Collaboration Planning", "Mind Map Creation", "Review & Refine"]
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
        
        uploaded_files = st.file_uploader(
            "Upload existing training materials",
            type=['pdf', 'docx', 'txt', 'pptx', 'xlsx', 'csv'],
            accept_multiple_files=True,
            help="Supported formats: PDF, Word, PowerPoint, Excel, CSV, Text"
        )
        
        # File categorization
        if uploaded_files:
            st.markdown("#### 📂 Categorize Your Files")
            
            file_categories = {}
            for uploaded_file in uploaded_files:
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
            
            st.session_state.file_inventory = {
                'uploaded_files': [f.name for f in uploaded_files],
                'file_categories': file_categories
            }
        
        st.markdown("#### 🔍 Manual File Inventory")
        st.markdown("If you have files that can't be uploaded, list them here:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            process_docs = st.text_area(
                "Process Documentation",
                placeholder="List any process documents, SOPs, workflows..."
            )
            
            training_materials = st.text_area(
                "Existing Training Materials",
                placeholder="List any existing training videos, presentations, guides..."
            )
        
        with col2:
            policies = st.text_area(
                "Policies & Procedures",
                placeholder="List any relevant policies, procedures, guidelines..."
            )
            
            technical_docs = st.text_area(
                "Technical Documentation",
                placeholder="List any technical guides, user manuals, system docs..."
            )
        
        # Save manual inventory
        st.session_state.file_inventory.update({
            'process_docs': process_docs,
            'training_materials': training_materials,
            'policies': policies,
            'technical_docs': technical_docs
        })
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Training Context"):
                st.session_state.discovery_step = 1
                st.rerun()
        
        with col2:
            if st.button("Next: Collaboration Planning →", type="primary"):
                st.session_state.discovery_step = 3
                st.rerun()
    
    # Step 3: Collaboration Planning
    elif st.session_state.discovery_step == 3:
        st.subheader("👥 Step 3: Team Collaboration & Video Calls")
        st.markdown("### Plan video calls with team members to dive deeper into topics")
        
        st.markdown("#### 🎥 Video Call Planning")
        st.info("Schedule video calls (Zoom, Read.ai, etc.) with team members to gather detailed information")
        
        # Team member input
        st.markdown("#### 👤 Team Members to Interview")
        
        team_members = st.session_state.collaboration_plan.get('team_members', [])
        
        if st.button("➕ Add Team Member"):
            team_members.append({
                'name': '',
                'role': '',
                'expertise': '',
                'availability': '',
                'topics_to_cover': ''
            })
            st.session_state.collaboration_plan['team_members'] = team_members
            st.rerun()
        
        for i, member in enumerate(team_members):
            with st.expander(f"Team Member {i+1}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    member['name'] = st.text_input(f"Name", value=member.get('name', ''), key=f"name_{i}")
                    member['role'] = st.text_input(f"Role/Position", value=member.get('role', ''), key=f"role_{i}")
                    member['expertise'] = st.text_input(f"Areas of Expertise", value=member.get('expertise', ''), key=f"expertise_{i}")
                
                with col2:
                    member['availability'] = st.text_input(f"Availability", value=member.get('availability', ''), key=f"avail_{i}")
                    member['topics_to_cover'] = st.text_area(f"Topics to Cover", value=member.get('topics_to_cover', ''), key=f"topics_{i}")
                
                if st.button(f"Remove Member {i+1}", key=f"remove_{i}"):
                    team_members.pop(i)
                    st.session_state.collaboration_plan['team_members'] = team_members
                    st.rerun()
        
        st.session_state.collaboration_plan['team_members'] = team_members
        
        # Video call preferences
        st.markdown("#### 🎬 Video Call Preferences")
        col1, col2 = st.columns(2)
        
        with col1:
            preferred_platform = st.selectbox(
                "Preferred video platform",
                ["Zoom", "Microsoft Teams", "Google Meet", "Read.ai", "Other"],
                index=["Zoom", "Microsoft Teams", "Google Meet", "Read.ai", "Other"].index(
                    st.session_state.collaboration_plan.get('preferred_platform', 'Zoom')
                )
            )
            
            call_duration = st.selectbox(
                "Preferred call duration",
                ["30 minutes", "45 minutes", "1 hour", "1.5 hours", "2 hours"],
                index=["30 minutes", "45 minutes", "1 hour", "1.5 hours", "2 hours"].index(
                    st.session_state.collaboration_plan.get('call_duration', '1 hour')
                )
            )
        
        with col2:
            recording_preference = st.selectbox(
                "Recording preference",
                ["Record all calls", "Record key calls only", "No recording", "Ask participants"],
                index=["Record all calls", "Record key calls only", "No recording", "Ask participants"].index(
                    st.session_state.collaboration_plan.get('recording_preference', 'Record key calls only')
                )
            )
            
            follow_up_plan = st.text_area(
                "Follow-up plan",
                value=st.session_state.collaboration_plan.get('follow_up_plan', ''),
                placeholder="How will you follow up after calls? Email summaries, action items, etc."
            )
        
        st.session_state.collaboration_plan.update({
            'preferred_platform': preferred_platform,
            'call_duration': call_duration,
            'recording_preference': recording_preference,
            'follow_up_plan': follow_up_plan
        })
        
        # Knowledge gaps identification
        st.markdown("#### ❓ Potential Knowledge Gaps")
        st.info("Based on your training context and existing files, what areas might need clarification?")
        
        knowledge_gaps = st.text_area(
            "Areas that need clarification or more information",
            value=st.session_state.collaboration_plan.get('knowledge_gaps', ''),
            placeholder="List specific topics, processes, or areas where you need more information from team members"
        )
        
        st.session_state.collaboration_plan['knowledge_gaps'] = knowledge_gaps
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to File Inventory"):
                st.session_state.discovery_step = 2
                st.rerun()
        
        with col2:
            if st.button("Next: Mind Map Creation →", type="primary"):
                st.session_state.discovery_step = 4
                st.rerun()
    
    # Step 4: Mind Map Creation
    elif st.session_state.discovery_step == 4:
        st.subheader("🧠 Step 4: Mind Map Creation")
        st.markdown("### Create a mind map to visualize the process/flow")
        
        # Check MindMeister configuration
        if not MINDMEISTER_CLIENT_ID:
            st.error("⚠️ MindMeister Client ID not configured. Please set MINDMEISTER_CLIENT_ID in your .env file")
            st.info("You can still proceed with the discovery process and create the mind map later.")
        else:
            st.success("✅ MindMeister integration ready")
        
        st.markdown("#### 🎯 Mind Map Configuration")
        
        mind_map_type = st.selectbox(
            "Type of mind map to create",
            ["Process Flow", "Training Structure", "Knowledge Map", "Decision Tree", "Organizational Chart"],
            index=["Process Flow", "Training Structure", "Knowledge Map", "Decision Tree", "Organizational Chart"].index(
                st.session_state.mind_map_data.get('mind_map_type', 'Process Flow')
            )
        )
        
        mind_map_focus = st.text_area(
            "Focus area for the mind map",
            value=st.session_state.mind_map_data.get('mind_map_focus', ''),
            placeholder="What specific process, topic, or area should the mind map focus on?"
        )
        
        complexity_level = st.selectbox(
            "Desired complexity level",
            ["Simple (High-level overview)", "Moderate (Key details)", "Detailed (Comprehensive)"],
            index=["Simple (High-level overview)", "Moderate (Key details)", "Detailed (Comprehensive)"].index(
                st.session_state.mind_map_data.get('complexity_level', 'Moderate (Key details)')
            )
        )
        
        st.session_state.mind_map_data.update({
            'mind_map_type': mind_map_type,
            'mind_map_focus': mind_map_focus,
            'complexity_level': complexity_level
        })
        
        # Generate mind map
        if st.button("🧠 Generate Mind Map", type="primary"):
            if not mind_map_focus:
                st.error("Please specify a focus area for the mind map")
                return
            
            with st.spinner("🤖 Creating mind map..."):
                # Prepare data for mind map creation
                training_context = st.session_state.training_context
                file_inventory = st.session_state.file_inventory
                collaboration_info = st.session_state.collaboration_plan
                mind_map_info = st.session_state.mind_map_data
                
                # Extract content from uploaded files if any
                extracted_content = ""
                if 'uploaded_files' in file_inventory and file_inventory['uploaded_files']:
                    # This would be implemented to extract content from the uploaded files
                    extracted_content = "Content from uploaded files would be extracted here"
                
                if MINDMEISTER_CLIENT_ID:
                    result = create_mindmeister_ai_mind_map(
                        training_context,
                        file_inventory,
                        collaboration_info,
                        mind_map_info,
                        extracted_content
                    )
                    
                    if result and result.get('success'):
                        st.success("✅ Mind map created successfully!")
                        st.info(f"Message: {result.get('message', 'Mind map ready')}")
                        
                        # Display the mind map that was just created
                        st.markdown("---")
                        st.markdown("### 🧠 Your Generated Mind Map")
                        display_mind_map_from_session()
                    else:
                        st.error("❌ Failed to create mind map")
                        st.info("You can still proceed with the discovery process")
                else:
                    st.info("Mind map creation skipped - MindMeister not configured")
                    
                    # Create a basic mind map without MindMeister
                    st.markdown("---")
                    st.markdown("### 🧠 Basic Mind Map Preview")
                    
                    # Create and display basic mind map
                    basic_result = create_simple_mind_map(training_context, file_inventory, collaboration_info, mind_map_info, f"Basic {mind_map_type}")
                    
                    if basic_result and basic_result.get('success'):
                        st.success("✅ Basic mind map created successfully!")
                        st.info("💡 Upgrade to MindMeister integration for professional mind maps with AI enhancement")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Collaboration Planning"):
                st.session_state.discovery_step = 3
                st.rerun()
        
        with col2:
            if st.button("Next: Review & Refine →", type="primary"):
                st.session_state.discovery_step = 5
                st.rerun()
    
    # Step 5: Review & Refine
    elif st.session_state.discovery_step == 5:
        st.subheader("✅ Step 5: Review & Refine")
        st.markdown("### Review your discovery findings and plan next steps")
        
        # Summary of all collected information
        st.markdown("#### 📋 Discovery Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Training Context:**")
            context = st.session_state.training_context
            st.write(f"- **Audience:** {context.get('target_audience', 'Not specified')}")
            st.write(f"- **Type:** {context.get('training_type', 'Not specified')}")
            st.write(f"- **Timeline:** {context.get('timeline', 'Not specified')}")
            st.write(f"- **Urgency:** {context.get('urgency_level', 'Not specified')}")
            
            st.markdown("**File Inventory:**")
            inventory = st.session_state.file_inventory
            if 'uploaded_files' in inventory and inventory['uploaded_files']:
                st.write(f"- **Files uploaded:** {len(inventory['uploaded_files'])}")
            else:
                st.write("- No files uploaded")
        
        with col2:
            st.markdown("**Collaboration Plan:**")
            collab = st.session_state.collaboration_plan
            if 'team_members' in collab and collab['team_members']:
                st.write(f"- **Team members:** {len(collab['team_members'])}")
            else:
                st.write("- No team members added")
            
            st.markdown("**Mind Map:**")
            mind_map = st.session_state.mind_map_data
            st.write(f"- **Type:** {mind_map.get('mind_map_type', 'Not specified')}")
            st.write(f"- **Focus:** {mind_map.get('mind_map_focus', 'Not specified')}")
        
        # Display the mind map if it exists
        if 'mind_map_display_data' in st.session_state and st.session_state.mind_map_display_data:
            st.markdown("---")
            st.markdown("#### 🧠 Your Created Mind Map")
            display_mind_map_from_session()
            
            # Add regenerate option
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Regenerate Mind Map"):
                    st.session_state.discovery_step = 4
                    st.rerun()
            with col2:
                if st.button("📄 Export Mind Map"):
                    mind_map_data = st.session_state.mind_map_display_data
                    import io
                    buffer = io.StringIO()
                    buffer.write(f"Mind Map: {mind_map_data['map_name']}\n")
                    buffer.write("=" * 50 + "\n\n")
                    buffer.write(mind_map_data['raw_data'])
                    
                    st.download_button(
                        label="Download Mind Map",
                        data=buffer.getvalue(),
                        file_name=f"mind_map_{mind_map_data['map_name'].replace(' ', '_')}.txt",
                        mime="text/plain"
                    )
        
        # Next steps recommendations
        st.markdown("#### 🎯 Recommended Next Steps")
        
        recommendations = []
        
        # Check for missing information
        if not st.session_state.training_context.get('target_audience'):
            recommendations.append("🔍 **Define target audience** - Specify who needs the training")
        
        if not st.session_state.file_inventory.get('uploaded_files') and not any([
            st.session_state.file_inventory.get('process_docs'),
            st.session_state.file_inventory.get('training_materials'),
            st.session_state.file_inventory.get('policies'),
            st.session_state.file_inventory.get('technical_docs')
        ]):
            recommendations.append("📁 **Gather existing materials** - Upload or list existing training materials")
        
        if not st.session_state.collaboration_plan.get('team_members'):
            recommendations.append("👥 **Identify team members** - Add team members for video call interviews")
        
        if not st.session_state.mind_map_data.get('mind_map_focus'):
            recommendations.append("🧠 **Define mind map focus** - Specify what the mind map should cover")
        
        if recommendations:
            st.warning("**Areas that need attention:**")
            for rec in recommendations:
                st.write(rec)
        else:
            st.success("✅ All discovery areas have been addressed!")
        
        # Action items
        st.markdown("#### 📝 Action Items")
        
        action_items = []
        
        # Based on collaboration plan
        if st.session_state.collaboration_plan.get('team_members'):
            action_items.append(f"📞 Schedule video calls with {len(st.session_state.collaboration_plan['team_members'])} team member(s)")
        
        # Based on file inventory
        if st.session_state.file_inventory.get('uploaded_files'):
            action_items.append("📄 Review and analyze uploaded training materials")
        
        # Based on mind map
        if st.session_state.mind_map_data.get('mind_map_focus'):
            action_items.append("🧠 Review and refine the created mind map")
        
        if action_items:
            for item in action_items:
                st.write(f"- {item}")
        else:
            st.info("No specific action items identified yet")
        
        # Export/Share options
        st.markdown("#### 💾 Export Discovery Report")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Export as PDF"):
                st.info("PDF export functionality coming soon...")
        
        with col2:
            if st.button("📊 Export as JSON"):
                # Create a comprehensive report
                report = {
                    'training_context': st.session_state.training_context,
                    'file_inventory': st.session_state.file_inventory,
                    'collaboration_plan': st.session_state.collaboration_plan,
                    'mind_map_data': st.session_state.mind_map_data,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Convert to JSON string
                import json
                json_str = json.dumps(report, indent=2)
                
                # Create download button
                st.download_button(
                    label="Download JSON Report",
                    data=json_str,
                    file_name=f"training_discovery_report_{time.strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col3:
            if st.button("📧 Share Report"):
                st.info("Email sharing functionality coming soon...")
        
        # Navigation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Mind Map Creation"):
                st.session_state.discovery_step = 4
                st.rerun()
        
        with col2:
            if st.button("🏠 Back to Home", type="primary"):
                st.session_state.discovery_step = 1
                st.rerun()

def mindmeister_embed(api_key, user_name="User"):
    import streamlit.components.v1 as components
    html = f"""
    <html>
    <body onload=\"document.forms[0].submit()\">
      <form action=\"https://www.mindmeister.com/external/show\"
            target=\"mindmeister_editor\"
            method=\"POST\"
            enctype=\"multipart/form-data\">
        <input type=\"hidden\" name=\"file[id]\" value=\"-1\"/>
        <input type=\"hidden\" name=\"file[name]\" value=\"Embedded Map.mind\"/>
        <input type=\"hidden\" name=\"api_key\" value=\"{api_key}\"/>
        <input type=\"hidden\" name=\"external_user_name\" value=\"{user_name}\"/>
        <input type=\"hidden\" name=\"file[allow_export]\" value=\"1\"/>
        <input type=\"submit\" value=\"Open MindMeister Editor\"/>
      </form>
      <iframe name=\"mindmeister_editor\" width=\"100%\" height=\"700px\" style=\"border:none;\"></iframe>
    </body>
    </html>
    """
    components.html(html, height=750)

def mindmeister_embed_flexible(
    api_key,
    file_id="-1",
    file_name="Embedded Map.mind",
    allow_export=True,
    view_only=False,
    hide_close_button=False,
    hide_sidebar=False,
    use_url_params=False,
    indexable_text=False,
    save_action="o",
    newcopy_url="",
    overwrite_url="",
    success_url="",
    external_user_name="User",
    file_content=None,  # Should be bytes or None
    file_content_name=None,  # e.g. "map.mind"
    download_url=""
):
    import streamlit.components.v1 as components
    def bool_to_str(val):
        return "true" if val else "false"
    fields = f"""
        <input type=\"hidden\" name=\"file[id]\" value=\"{file_id}\"/>
        <input type=\"hidden\" name=\"file[name]\" value=\"{file_name}\"/>
        <input type=\"hidden\" name=\"api_key\" value=\"{api_key}\"/>
        <input type=\"hidden\" name=\"external_user_name\" value=\"{external_user_name}\"/>
        {'<input type=\\"hidden\\" name=\\"file[allow_export]\\" value=\\"1\\"/>' if allow_export else ''}
        {'<input type=\\"hidden\\" name=\\"file[view_only]\\" value=\\"true\\"/>' if view_only else ''}
        {'<input type=\\"hidden\\" name=\\"file[hide_close_button]\\" value=\\"true\\"/>' if hide_close_button else ''}
        {'<input type=\\"hidden\\" name=\\"file[hide_sidebar]\\" value=\\"true\\"/>' if hide_sidebar else ''}
        {'<input type=\\"hidden\\" name=\\"file[use_url_params]\\" value=\\"true\\"/>' if use_url_params else ''}
        {'<input type=\\"hidden\\" name=\\"file[indexable_text]\\" value=\\"true\\"/>' if indexable_text else ''}
        <input type=\"hidden\" name=\"file[save_action]\" value=\"{save_action}\"/>
        {f'<input type=\\"hidden\\" name=\\"file[newcopy_url]\\" value=\\"{newcopy_url}\\"/>' if newcopy_url else ''}
        {f'<input type=\\"hidden\\" name=\\"file[overwrite_url]\\" value=\\"{overwrite_url}\\"/>' if overwrite_url else ''}
        {f'<input type=\\"hidden\\" name=\\"file[success_url]\\" value=\\"{success_url}\\"/>' if success_url else ''}
        {f'<input type=\\"hidden\\" name=\\"file[download_url]\\" value=\\"{download_url}\\"/>' if download_url else ''}
    """
    file_input = ""
    if file_content and file_content_name:
        file_input = f'<input type="file" name="file[content]" value="{file_content_name}"/>'
    html = f"""
    <html>
    <body onload=\"document.forms[0].submit()\">
      <form action=\"https://www.mindmeister.com/external/show\"
            target=\"mindmeister_editor\"
            method=\"POST\"
            enctype=\"multipart/form-data\">
        {fields}
        {file_input}
        <input type=\"submit\" value=\"Open MindMeister Editor\"/>
      </form>
      <iframe name=\"mindmeister_editor\" width=\"100%\" height=\"700px\" style=\"border:none;\"></iframe>
    </body>
    </html>
    """
    components.html(html, height=750)

def show_mind_maps_page():
    """Mind maps page with MindMeister integration"""
    st.header("🧠 AI Mind Map Generation")
    st.markdown("Create professional mind maps using MindMeister integration")
    
    # Add tabs for different mind map types
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌐 MindMeister Flexible Embed", 
        "🌐 MindMeister Editor", 
        "🗺️ Markmap Component", 
        "🧠 MindMeister AI"
    ])
    
    with tab1:
        st.subheader("🌐 MindMeister Flexible Embed API")
        st.info("Set your options and open the MindMeister editor with full API flexibility. The map will always be editable.")
        api_key = st.secrets["MINDMEISTER_API_KEY"] if "MINDMEISTER_API_KEY" in st.secrets else "YOUR_API_KEY"
        user_name = st.text_input("User Name", "User", key="mme_user_name")
        file_id = st.text_input("Map ID (-1 for new)", "-1", key="mme_file_id")
        file_name = st.text_input("Map Name", "Embedded Map.mind", key="mme_file_name")
        allow_export = st.checkbox("Allow export and print", True, key="mme_allow_export")
        hide_close_button = st.checkbox("Hide close button", False, key="mme_hide_close_button")
        hide_sidebar = st.checkbox("Hide sidebar", False, key="mme_hide_sidebar")
        use_url_params = st.checkbox("Use URL params", False, key="mme_use_url_params")
        indexable_text = st.checkbox("Indexable text", False, key="mme_indexable_text")
        save_action = st.selectbox("Save action", ["o", "s"], index=0, format_func=lambda x: "Overwrite" if x=="o" else "Save as new copy", key="mme_save_action")
        newcopy_url = st.text_input("Newcopy URL", "", key="mme_newcopy_url")
        overwrite_url = st.text_input("Overwrite URL", "", key="mme_overwrite_url")
        success_url = st.text_input("Success URL", "", key="mme_success_url")
        download_url = st.text_input("Download URL", "", key="mme_download_url")
        # File upload (optional, for advanced use)
        file_content = None
        file_content_name = None
        uploaded_file = st.file_uploader("Upload MindMeister file (.mind, .mm, .xmind, .mmap)", type=["mind", "mm", "xmind", "mmap"], key="mme_file_upload")
        if uploaded_file:
            file_content = uploaded_file.getvalue()
            file_content_name = uploaded_file.name
        if st.button("Open MindMeister Editor", key="mme_open_btn"):
            mindmeister_embed_flexible(
                api_key=api_key,
                file_id=file_id,
                file_name=file_name,
                allow_export=allow_export,
                view_only=False,
                hide_close_button=hide_close_button,
                hide_sidebar=hide_sidebar,
                use_url_params=use_url_params,
                indexable_text=indexable_text,
                save_action=save_action,
                newcopy_url=newcopy_url,
                overwrite_url=overwrite_url,
                success_url=success_url,
                external_user_name=user_name,
                file_content=file_content,
                file_content_name=file_content_name,
                download_url=download_url
            )
    
    with tab2:
        st.subheader("🌐 MindMeister Embedded Editor")
        st.info("A new, editable MindMeister map will open below. Each visit creates a new map.")
        api_key = st.secrets["MINDMEISTER_API_KEY"] if "MINDMEISTER_API_KEY" in st.secrets else "YOUR_API_KEY"
        user_name = st.session_state.get("user_name", "User")
        mindmeister_embed(api_key=api_key, user_name=user_name)
    
    with tab3:
        st.subheader("🗺️ Test Markmap Component")
        st.markdown("Test the local markmap component with sample data")
        
        # Sample markdown for testing
        sample_markdown = """# Training Program Overview\n## Frontend Development\n- React Components\n  - Navigation\n  - Forms\n  - Charts\n- Styling\n  - CSS Modules\n  - Tailwind CSS\n## Backend Development\n- API Endpoints\n  - Authentication\n  - Data CRUD\n- Database\n  - PostgreSQL\n  - Redis Cache\n## DevOps & Deployment\n- CI/CD Pipeline\n- Docker Containers\n- Cloud Deployment"""
        
        st.markdown("**Sample Markdown Data:**")
        st.code(sample_markdown, language="markdown")
        
        if st.button("🎯 Test Markmap Component", type="primary"):
            st.markdown("**Rendered Mind Map:**")
            markmap(sample_markdown, height=600)
            st.success("✅ Markmap component test completed!")
    
    with tab4:
        st.subheader("🧠 MindMeister AI Mind Maps")
        
        # Quick test button
        st.markdown("### 🧪 Quick Test")
        if st.button("🎯 Test Mind Map with Sample Data", type="secondary"):
            # Create sample data for testing
            sample_training_context = {
                'target_audience': 'New Employees',
                'training_type': 'Onboarding',
                'industry': 'Technology',
                'company_size': 'Medium Business',
                'urgency_level': 'Medium',
                'timeline': '1 month'
            }
            
            sample_file_inventory = {
                'existing_files': ['employee_handbook.pdf', 'onboarding_checklist.docx']
            }
            
            sample_collaboration_info = {
                'collaboration_needed': 'HR Team'
            }
            
            sample_mind_map_info = {
                'mind_map_type': 'Process Flow'
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

    st.markdown("---")
    
    # Check MindMeister configuration
    if not MINDMEISTER_CLIENT_ID:
        st.error("⚠️ MindMeister Client ID not configured. Please set MINDMEISTER_CLIENT_ID in your .env file")
        return
    
    # Training context input
    st.subheader("📋 Training Context")
    col1, col2 = st.columns(2)
    
    with col1:
        target_audience = st.text_input("Target Audience", placeholder="e.g., New employees, Managers, Technical staff")
        training_type = st.selectbox("Training Type", ["Onboarding", "Skills Development", "Compliance", "Process Training", "Other"])
        industry = st.text_input("Industry", placeholder="e.g., Healthcare, Technology, Finance")
    
    with col2:
        company_size = st.selectbox("Company Size", ["Startup", "Small Business", "Medium Business", "Large Enterprise"])
        urgency_level = st.selectbox("Urgency Level", ["Low", "Medium", "High", "Critical"])
        timeline = st.selectbox("Timeline", ["Immediate", "1-2 weeks", "1 month", "Flexible"])
    
    # File upload
    st.subheader("📁 Upload Training Materials")
    uploaded_files = st.file_uploader(
        "Upload PDFs, Word documents, or text files",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True
    )
    
    # Extract content from uploaded files
    extracted_content = ""
    if uploaded_files:
        st.info("📄 Processing uploaded files...")
        for uploaded_file in uploaded_files:
            try:
                if uploaded_file.type == "application/pdf":
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    for page in pdf_reader.pages:
                        extracted_content += page.extract_text() + "\n"
                elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                    doc = Document(uploaded_file)
                    for paragraph in doc.paragraphs:
                        extracted_content += paragraph.text + "\n"
                elif uploaded_file.type == "text/plain":
                    extracted_content += uploaded_file.getvalue().decode() + "\n"
            except Exception as e:
                st.warning(f"Could not process {uploaded_file.name}: {str(e)}")
        
        if extracted_content:
            st.success(f"✅ Extracted {len(extracted_content)} characters from {len(uploaded_files)} file(s)")
            st.session_state.extracted_content = extracted_content
    
    # Mind map generation
    st.subheader("🎨 Generate Mind Map")
    
    if st.button("🧠 Create AI Mind Map", type="primary"):
        if not target_audience:
            st.error("Please provide a target audience")
            return
        
        # Prepare training context
        training_context = {
            "target_audience": target_audience,
            "training_type": training_type,
            "industry": industry,
            "company_size": company_size,
            "urgency_level": urgency_level,
            "timeline": timeline
        }
        
        # Placeholder for file inventory and collaboration info
        file_inventory = {"existing_files": [f.name for f in uploaded_files] if uploaded_files else []}
        collaboration_info = {"collaboration_needed": "None"}
        mind_map_info = {"mind_map_type": "Process Flow"}
        
        with st.spinner("🤖 Generating AI mind map..."):
            result = create_mindmeister_ai_mind_map(
                training_context, 
                file_inventory, 
                collaboration_info, 
                mind_map_info, 
                extracted_content
            )
        
        if result and result.get('success'):
            st.success("✅ Mind map created successfully!")
            st.info(f"Message: {result.get('message', 'Mind map ready')}")
        else:
            st.error("❌ Failed to create mind map")

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