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
import math

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

# Miro API Configuration
MIRO_API_KEY = os.getenv('MIRO_API_KEY')
MIRO_ACCESS_TOKEN = os.getenv('MIRO_ACCESS_TOKEN')
MIRO_API_URL = "https://api.miro.com/v1"

def create_miro_mind_map(mind_map_data, board_name="Training Process Mind Map"):
    """
    Create a Miro board with mind map structure and content using v1 API
    """
    if not MIRO_ACCESS_TOKEN:
        st.warning("⚠️ Miro API access token not set. Please add MIRO_ACCESS_TOKEN to your .env file")
        return None
    
    try:
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {MIRO_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Create board with v1 API payload
        board_payload = {
            "name": board_name,
            "description": "AI-generated mind map for training process visualization"
        }
        
        # Debug: Show board creation request
        st.write(f"🔍 Debug: Creating board with payload: {board_payload}")
        
        response = requests.post(f"{MIRO_API_URL}/boards", headers=headers, json=board_payload)
        
        # Debug: Show board creation response
        st.write(f"🔍 Debug: Board creation response status: {response.status_code}")
        st.write(f"🔍 Debug: Board creation response body: {response.text}")
        
        if response.status_code == 201:
            board_data = response.json()
            board_id = board_data.get('id')
            board_url = board_data.get('viewLink')
            
            st.success(f"✅ Miro board created successfully!")
            st.info(f"Board ID: {board_id}")
            st.info(f"Board URL: {board_url}")
            
            # Add content to the board
            st.info("🔄 Adding mind map content to the board...")
            
            # Create a basic mind map structure using v1 API
            mind_map_items = create_mind_map_structure(mind_map_data, board_id, headers)
            
            if mind_map_items:
                st.success("✅ Mind map content added to board!")
            
            return {
                "success": True,
                "board_id": board_id,
                "board_url": board_url,
                "embed_url": f"https://miro.com/app/board/{board_id}/"
            }
        else:
            st.error(f"❌ Failed to create Miro board: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error creating Miro board: {str(e)}")
        return None

def create_mind_map_structure(mind_map_data, board_id, headers):
    """
    Add mind map content to the Miro board using v1 REST API
    Creates a proper connected mind map with connectors using AI-generated content
    """
    try:
        # Parse the AI-generated mind map structure
        lines = mind_map_data.split('\n')
        main_topics = []
        subtopics = {}
        
        # Extract content from AI response
        current_main_topic = None
        for line in lines:
            line = line.strip()
            if line.startswith('**') and line.endswith('**'):
                # This is a main topic
                topic = line.replace('**', '').strip()
                main_topics.append(topic)
                current_main_topic = topic
                subtopics[topic] = []
            elif line.startswith('-') and len(line) > 2 and current_main_topic:
                # This is a subtopic
                subtopic = line[1:].strip()
                subtopics[current_main_topic].append(subtopic)
            elif line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.') or line.startswith('5.'):
                # This might be a numbered item that could be a subtopic
                if current_main_topic:
                    subtopic = line.split('.', 1)[1].strip() if '.' in line else line
                    subtopics[current_main_topic].append(subtopic)
        
        # If no structured content found, create a basic mind map
        if not main_topics:
            main_topics = ["Training Process", "Planning Phase", "Development Phase", "Delivery Phase", "Evaluation Phase"]
            subtopics = {
                "Training Process": [],
                "Planning Phase": ["Needs Assessment", "Goal Setting"],
                "Development Phase": ["Content Creation", "Material Design"],
                "Delivery Phase": ["Training Sessions", "Support Materials"],
                "Evaluation Phase": ["Feedback Collection", "Performance Metrics"]
            }
        
        # Ensure we have at least some content
        if not main_topics:
            main_topics = ["Training Process"]
            subtopics = {"Training Process": []}
        
        # Create mind map nodes with actual content
        mind_map_nodes = []
        
        # Add central topic (first main topic or default)
        central_topic = main_topics[0] if main_topics else "Training Process"
        mind_map_nodes.append({
            "type": "text",
            "text": f"🎯 {central_topic}",
            "x": 0,
            "y": 0,
            "width": 350,
            "height": 80
        })
        
        # Create a cleaner, more organized layout
        # Main branches positioned in a clean cross pattern
        main_branch_positions = [
            (-500, 0, "📋", "Planning Phase"),      # Left
            (500, 0, "🛠️", "Development Phase"),   # Right
            (0, -400, "📚", "Delivery Phase"),      # Top
            (0, 400, "📊", "Evaluation Phase")      # Bottom
        ]
        
        # Use default topics if we don't have enough from AI
        default_topics = ["Planning Phase", "Development Phase", "Delivery Phase", "Evaluation Phase"]
        
        for i in range(4):  # Always create 4 main branches
            if i + 1 < len(main_topics):
                topic = main_topics[i + 1]
            else:
                topic = default_topics[i] if i < len(default_topics) else f"Topic {i + 1}"
            
            x, y, emoji, default_name = main_branch_positions[i]
            mind_map_nodes.append({
                "type": "text",
                "text": f"{emoji} {topic}",
                "x": x,
                "y": y,
                "width": 250,
                "height": 60
            })
        
        # Add subtopics with better organization and spacing
        default_subtopics = {
            "Planning Phase": ["Needs Assessment", "Goal Setting", "Timeline Planning", "Resource Allocation"],
            "Development Phase": ["Content Creation", "Material Design", "Technology Setup", "Testing & Review"],
            "Delivery Phase": ["Training Sessions", "Support Materials", "Facilitation", "Q&A Support"],
            "Evaluation Phase": ["Feedback Collection", "Performance Metrics", "Continuous Improvement", "Documentation"]
        }
        
        # Create subtopics in organized clusters around each main branch
        for i in range(4):
            x, y, emoji, default_name = main_branch_positions[i]
            
            # Get topic name for this branch
            if i + 1 < len(main_topics):
                topic = main_topics[i + 1]
            else:
                topic = default_topics[i] if i < len(default_topics) else f"Topic {i + 1}"
            
            # Get subtopics for this topic
            if topic in subtopics and subtopics[topic]:
                topic_subtopics = subtopics[topic]
            elif topic in default_subtopics:
                topic_subtopics = default_subtopics[topic]
            else:
                topic_subtopics = default_subtopics[default_name]
            
            # Add subtopics in organized clusters
            for j, subtopic in enumerate(topic_subtopics[:4]):  # Show up to 4 subtopics per branch
                # Calculate positions in a clean grid around each main branch
                if i == 0:  # Left branch - arrange vertically
                    sub_x = x - 300
                    sub_y = y - 150 + (j * 100)
                elif i == 1:  # Right branch - arrange vertically
                    sub_x = x + 300
                    sub_y = y - 150 + (j * 100)
                elif i == 2:  # Top branch - arrange horizontally
                    sub_x = x - 200 + (j * 150)
                    sub_y = y - 300
                else:  # Bottom branch - arrange horizontally
                    sub_x = x - 200 + (j * 150)
                    sub_y = y + 300
                
                mind_map_nodes.append({
                    "type": "text",
                    "text": f"• {subtopic}",
                    "x": sub_x,
                    "y": sub_y,
                    "width": 180,
                    "height": 50
                })
        
        # Store created widget IDs for connectors
        created_widgets = []
        
        # Add all text widgets first
        for i, node in enumerate(mind_map_nodes):
            try:
                # Create the widget payload (only use supported properties)
                miro_widget = {
                    "type": "text",
                    "text": node["text"],
                    "x": node["x"],
                    "y": node["y"],
                    "width": node["width"]
                }
                
                # Debug: Show what we're sending to Miro
                st.write(f"🔍 Debug: Creating text widget {i+1}: {node['text']}")
                
                # Create the widget
                node_response = requests.post(
                    f"{MIRO_API_URL}/boards/{board_id}/widgets",
                    headers=headers,
                    json=miro_widget
                )
                
                if node_response.status_code == 201 or node_response.status_code == 200:
                    widget_data = node_response.json()
                    widget_id = widget_data.get('id')
                    created_widgets.append({
                        "id": widget_id,
                        "x": node["x"],
                        "y": node["y"],
                        "text": node["text"]
                    })
                    st.success(f"✅ Created widget: {node['text']} (ID: {widget_id})")
                else:
                    st.warning(f"⚠️ Could not create widget '{node['text']}': {node_response.status_code} - {node_response.text}")
                    
            except Exception as e:
                st.warning(f"⚠️ Error creating widget '{node['text']}': {str(e)}")
        
        # Now create connectors (lines) between nodes
        st.info("🔄 Creating mind map connectors...")
        
        # Create organized connections
        connections = []
        
        if len(created_widgets) > 0:
            central_widget_idx = 0
            
            # Connect central topic to main branches (widgets 1-4)
            for i in range(1, min(5, len(created_widgets))):
                connections.append((central_widget_idx, i))
            
            # Connect main branches to their subtopics
            # Each main branch should connect to its 4 subtopics
            for branch_idx in range(1, 5):  # Main branches are at indices 1-4
                if branch_idx < len(created_widgets):
                    # Calculate the starting index for subtopics of this branch
                    # Each branch has 4 subtopics, so they start at index 5 + (branch_idx-1)*4
                    subtopic_start_idx = 5 + (branch_idx - 1) * 4
                    
                    # Connect to up to 4 subtopics for this branch
                    for j in range(4):
                        subtopic_idx = subtopic_start_idx + j
                        if subtopic_idx < len(created_widgets):
                            connections.append((branch_idx, subtopic_idx))
        
        for i, (from_idx, to_idx) in enumerate(connections):
            if from_idx < len(created_widgets) and to_idx < len(created_widgets):
                try:
                    from_widget = created_widgets[from_idx]
                    to_widget = created_widgets[to_idx]
                    
                    # Create connector line using widget IDs
                    connector = {
                        "type": "line",
                        "startWidget": {
                            "id": from_widget["id"]
                        },
                        "endWidget": {
                            "id": to_widget["id"]
                        }
                    }
                    
                    st.write(f"🔍 Debug: Creating connector {i+1}: {from_widget['text']} → {to_widget['text']}")
                    
                    connector_response = requests.post(
                        f"{MIRO_API_URL}/boards/{board_id}/widgets",
                        headers=headers,
                        json=connector
                    )
                    
                    if connector_response.status_code == 201 or connector_response.status_code == 200:
                        st.success(f"✅ Created connector: {from_widget['text']} → {to_widget['text']}")
                    else:
                        st.warning(f"⚠️ Could not create connector: {connector_response.status_code} - {connector_response.text}")
                        
                except Exception as e:
                    st.warning(f"⚠️ Error creating connector: {str(e)}")
        
        return len(created_widgets)
        
    except Exception as e:
        st.error(f"Error creating mind map structure: {str(e)}")
        return 0

# Set page config
st.set_page_config(page_title='Content Generator with Vadoo AI', layout='wide')

# Title
st.title("🤖 Automated Content Generator with Vadoo AI")

# Admin Onboarding Questionnaire
with st.expander("📋 Admin Setup: Training Context Questionnaire", expanded=True):
    st.write("**Please provide context about your training/onboarding to generate more targeted content:**")
    
    # Training Context Questions
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 WHO")
        target_audience = st.selectbox(
            "Who is this training for?",
            ["New Employees", "Existing Staff", "Managers/Supervisors", "Contractors", "Students", "Clients", "Other"],
            help="Select the primary audience for this training"
        )
        
        if target_audience == "Other":
            target_audience = st.text_input("Please specify:", placeholder="e.g., Sales team, Customer service reps")
        
        audience_size = st.selectbox(
            "How many people will receive this training?",
            ["1-10 people", "11-50 people", "51-100 people", "100+ people", "Unknown"],
            help="This helps determine the scale and format of materials"
        )
    
    with col2:
        st.subheader("🎯 WHAT")
        training_type = st.selectbox(
            "What type of training is this?",
            ["Onboarding", "Skills Development", "Compliance/Safety", "Product Training", "Process Training", "Leadership Development", "Other"],
            help="Select the primary purpose of this training"
        )
        
        if training_type == "Other":
            training_type = st.text_input("Please specify training type:", placeholder="e.g., Software training, Policy updates")
        
        urgency_level = st.selectbox(
            "How urgent is this training?",
            ["Low - General knowledge building", "Medium - Important but not critical", "High - Required for job function", "Critical - Immediate compliance needed"],
            help="This affects the tone and priority of content"
        )
    
    # Additional Context
    st.subheader("⏰ WHEN & WHERE")
    col3, col4 = st.columns(2)
    
    with col3:
        timeline = st.selectbox(
            "When does this training need to be completed?",
            ["ASAP - Within 1 week", "Soon - Within 1 month", "Flexible - Within 3 months", "Ongoing - Continuous learning", "Unknown"],
            help="This helps determine content depth and format"
        )
        
        delivery_method = st.selectbox(
            "How will this training be delivered?",
            ["Self-paced online", "Instructor-led virtual", "In-person classroom", "Hybrid approach", "Mobile/App-based", "Other"],
            help="This affects the format of generated materials"
        )
    
    with col4:
        industry = st.text_input(
            "What industry/sector is this for?",
            placeholder="e.g., Healthcare, Technology, Finance, Education",
            help="This helps customize content with relevant examples"
        )
        
        company_size = st.selectbox(
            "What's the size of your organization?",
            ["Startup (1-50 employees)", "Small business (51-200)", "Medium business (201-1000)", "Large enterprise (1000+)", "Educational institution", "Government/Non-profit"],
            help="This affects the tone and complexity of content"
        )
    
    # Advanced Options
    with st.expander("🔧 Advanced Options"):
        st.write("**Additional context for more personalized content:**")
        
        col5, col6 = st.columns(2)
        with col5:
            learning_style = st.multiselect(
                "Preferred learning styles:",
                ["Visual learners", "Auditory learners", "Reading/Writing", "Kinesthetic/Hands-on", "Social learners"],
                default=["Visual learners", "Reading/Writing"],
                help="Select all that apply to your audience"
            )
            
            technical_level = st.selectbox(
                "Technical expertise level:",
                ["Beginner - No prior knowledge", "Intermediate - Some experience", "Advanced - Experienced users", "Expert - Specialists"],
                help="This affects the complexity of explanations"
            )
        
        with col6:
            compliance_requirements = st.multiselect(
                "Any compliance requirements?",
                ["None", "Safety regulations", "Data privacy", "Industry standards", "Legal requirements", "Quality standards"],
                help="Select all that apply"
            )
            
            success_metrics = st.text_area(
                "How will you measure training success?",
                placeholder="e.g., Quiz scores, practical assessments, feedback surveys, performance improvements",
                height=80,
                help="This helps focus content on measurable outcomes"
            )
    
    # Store context in session state
    if st.button("✅ Save Training Context", type="primary"):
        training_context = {
            "target_audience": target_audience,
            "audience_size": audience_size,
            "training_type": training_type,
            "urgency_level": urgency_level,
            "timeline": timeline,
            "delivery_method": delivery_method,
            "industry": industry,
            "company_size": company_size,
            "learning_style": learning_style,
            "technical_level": technical_level,
            "compliance_requirements": compliance_requirements,
            "success_metrics": success_metrics
        }
        st.session_state.training_context = training_context
        st.success("✅ Training context saved! This will be used to customize your content generation.")
        
        # Show summary
        st.subheader("📊 Training Context Summary")
        st.write(f"**Training for:** {target_audience} ({audience_size})")
        st.write(f"**Type:** {training_type} - {urgency_level}")
        st.write(f"**Timeline:** {timeline} via {delivery_method}")
        if industry:
            st.write(f"**Industry:** {industry} ({company_size})")

# File Inventory Section
with st.expander("📁 Existing Files Inventory", expanded=False):
    st.write("**Do you have any existing files related to this training topic?**")
    
    # Add file uploader here
    uploaded_files = st.file_uploader("Upload your source files", accept_multiple_files=True, type=['txt', 'pdf', 'docx'])
    
    existing_files = st.multiselect(
        "Select existing files you have:",
        ["Training Manuals", "Policy Documents", "Procedure Guides", "Video Content", "Presentations", "Handouts", "Assessment Materials", "Reference Guides", "None"],
        help="This helps us understand what materials you already have"
    )

    # Additional file details
    if existing_files and "None" not in existing_files:
        st.write("**Additional details about your existing files:**")
        
        file_quality = st.selectbox(
            "How current/up-to-date are these files?",
            ["Very current (updated within 6 months)", "Somewhat current (6-12 months old)", "Needs updating (1-2 years old)", "Outdated (2+ years old)", "Unknown"],
            help="This helps determine if files need updating"
        )
        
        file_format = st.multiselect(
            "What formats are your files in?",
            ["PDF", "Word (.docx)", "PowerPoint (.pptx)", "Excel (.xlsx)", "Video files", "Web pages", "Printed materials", "Other"],
            help="This helps with integration planning"
        )
        
        # Save file inventory to session state
        if st.button("💾 Save File Inventory", key="save_files"):
            file_inventory = {
                "existing_files": existing_files,
                "file_quality": file_quality,
                "file_format": file_format
            }
            st.session_state.file_inventory = file_inventory
            st.success("✅ File inventory saved!")
            
with st.expander("📋 Team Collaboration & Video Calls", expanded=False):
    st.write("**Would you like to connect with team members for deeper topic exploration?**")
    
    collaboration_needed = st.selectbox(
        #Prompt for team collaboration
        "Do you need team collaboration for this training?",
        ["Yes - Schedule video calls with subject matter experts", "Yes - Record team discussions for future reference", "Maybe - Depends on topic complexity", "No - Self-contained training", "Not sure yet"],
        help="This helps plan interactive sessions and knowledge sharing"
    )
    
    if collaboration_needed and "No - Self-contained training" not in collaboration_needed:
        #Prompt for additional collaboration details
        st.write("**Additional collaboration details:**")
        #Prompt for team members
        
        team_members = st.multiselect(
            "Who should be involved in these sessions?",
            ["Subject Matter Experts", "Team Members", "Other"],
            help="Select team members who can contribute to the training"
        )
        #Prompt for video call schedule
        
        session_type = st.selectbox(
            "What type of sessions do you prefer?",
            ["Zoom calls with screen sharing", "Google meet and Read.ai for AI recorded sessions", "Live Q&A sessions", "Workshop format"],
            help="Choose the most effective format for your training"
        )
        
        #Save collaboration info
        if st.button("Save Collaboration Info", key="save_collaboration"):
            collaboration_info = {
                "collaboration_needed": collaboration_needed,
                "team_members": team_members,
                "session_type": session_type
            }
            #Save collaboration info to session state
            st.session_state.collaboration_info = collaboration_info
            st.success("✅ Collaboration info saved!")
    
with st.expander("🗺️ Mind Map & Process Mapping", expanded=False):
    st.write("**Would you like to create a mind map to visualize organizational processes?**")
    
    mind_map_needed = st.selectbox(
        "Do you need process mapping for this training?",
        ["Yes - Create Miro mind map for complex processes","Yes - Identify knowledge gaps in existing processes", "Maybe - Depends on process complexity", "No - Simple processes only", "Not sure yet"],
        help="This helps visualize complex workflows and identify areas needing clarification"
    )
    #Prompt for additional mind map details
    if mind_map_needed and "No - Simple processes only" not in mind_map_needed:
        st.write("**Additional mind map details:**")
        #Prompt for process areas
        process_areas = st.multiselect(
            "Which process areas need mapping?",
            ["Organizational Structure", "Workflows & Procedures", "Decision Making", "Compliance Processes", "Customer Journey", "Other"],
            help="Select the areas that need visual mapping"
        )
        #Prompt for mind map type
        mind_map_type = st.selectbox(
            "What type of mind map do you need?",
            ["Process Flow Diagram", "Organizational Chart", "Decision Tree", "Customer Journey Map", "System Architecture", "Compliance Framework", "Other"],
            help="Choose the most appropriate visualization type"
        )
        
        # Save mind map info
        if st.button("💾 Save Mind Map Settings", key="save_mind_map"):
            mind_map_info = {
                "mind_map_needed": mind_map_needed,
                "process_areas": process_areas,
                "mind_map_type": mind_map_type
            }
            st.session_state.mind_map_info = mind_map_info
            st.success("✅ Mind map settings saved!")

# Show comprehensive summary if both training context and file inventory are saved
if st.session_state.get('training_context') and st.session_state.get('file_inventory'):
    with st.expander("📋 Complete Training Summary & Recommendations", expanded=True):
        st.subheader("🎯 Training Overview")
        tc = st.session_state.training_context
        fi = st.session_state.file_inventory
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**👥 Audience:** {tc.get('target_audience')} ({tc.get('audience_size')})")
            st.write(f"**🎯 Type:** {tc.get('training_type')} - {tc.get('urgency_level')}")
            st.write(f"**⏰ Timeline:** {tc.get('timeline')} via {tc.get('delivery_method')}")
            if tc.get('industry'):
                st.write(f"**🏢 Industry:** {tc.get('industry')} ({tc.get('company_size')})")
        
        with col2:
            st.write(f"**📁 Existing Files:** {', '.join(fi.get('existing_files', []))}")
            st.write(f"**💾 Quality:** {fi.get('file_quality', 'Unknown')}")
            st.write(f"**📄 Formats:** {', '.join(fi.get('file_format', []))}")
        
        # Add collaboration info if available
        ci = st.session_state.get('collaboration_info', None)
        if ci:
            st.subheader("📋 Team Collaboration Plan")
            col3, col4 = st.columns(2)
            with col3:
                st.write(f"**🎯 Collaboration:** {ci.get('collaboration_needed', 'None')}")
                st.write(f"**👥 Team Members:** {', '.join(ci.get('team_members', []))}")
            with col4:
                st.write(f"**🎥 Session Format:** {ci.get('session_type', 'None')}")
        mmi = st.session_state.get('mind_map_info', None)
        if mmi:
            st.subheader("🗺️ Mind Map & Process Mapping")
            col5, col6 = st.columns(2)
            with col5:
                st.write(f"**🗺️ Mapping Type:** {mmi.get('mind_map_needed', 'None')}")
                st.write(f"**🗺️ Process Areas:** {', '.join(mmi.get('process_areas', []))}")
            with col6:
                st.write(f"**🗺️ Visualization:** {mmi.get('mind_map_type', 'None')}")
            # Generate collaboration-specific recommendations
            if st.button("🤖 Get Collaboration Recommendations", key="get_collab_recommendations"):
                collab_prompt = f"""
                Based on this collaboration setup:
                - Collaboration Type: {ci.get('collaboration_needed')}
                - Team Members: {', '.join(ci.get('team_members', []))}
                - Session Format: {ci.get('session_type')}
                - Training Context: {tc.get('target_audience')} in {tc.get('industry', 'General')} industry
                
                Provide 3-5 specific recommendations for:
                1. How to structure the video call sessions
                2. What topics to cover in team discussions
                3. How to integrate recorded sessions with training materials
                4. Best practices for using Read.ai or Zoom recordings
                5. Follow-up activities after team sessions
                """
                
                try:
                    collab_recommendations = model.generate_content(collab_prompt)
                    st.subheader("🤖 Collaboration Recommendations")
                    st.write(collab_recommendations.text)
                except Exception as e:
                    st.error(f"Error generating collaboration recommendations: {str(e)}")

        # Generate AI recommendations
        if st.button("🤖 Get AI Recommendations", key="get_recommendations"):
            recommendation_prompt = f"""
            Based on this training context:
            - Target: {tc.get('target_audience')} in {tc.get('industry', 'General')} industry
            - Type: {tc.get('training_type')} with {tc.get('urgency_level')} urgency
            - Timeline: {tc.get('timeline')} via {tc.get('delivery_method')}
            - Existing files: {', '.join(fi.get('existing_files', []))} ({fi.get('file_quality', 'Unknown')})
            
            Provide 3-5 specific recommendations for:
            1. How to best use existing files
            2. What new content to prioritize
            3. Recommended delivery approach
            4. Success measurement strategies
            """
            
            try:
                recommendations = model.generate_content(recommendation_prompt)
                st.subheader("🤖 AI Recommendations")
                st.write(recommendations.text)
            except Exception as e:
                st.error(f"Error generating recommendations: {str(e)}")

        # Generate mind map and knowledge gap analysis (only if mind map info is saved)
        if mmi and st.button("🗺️ Generate Mind Map & Identify Gaps", key="generate_mind_map"):
            mind_map_prompt = f"""
            Based on this training context and mind map requirements:
            - Training Context: {tc.get('target_audience')} in {tc.get('industry', 'General')} industry
            - Process Areas: {', '.join(mmi.get('process_areas', []))}
            - Mind Map Type: {mmi.get('mind_map_type', 'None')}
            - Existing Files: {', '.join(fi.get('existing_files', []))}
            
            Create a comprehensive mind map structure and identify knowledge gaps:
            1. **Mind Map Structure**: Outline the main nodes and connections for a {mmi.get('mind_map_type', 'Process Flow')} diagram
            2. **Knowledge Gaps**: Identify 3-5 areas where information is missing or unclear
            3. **Team Collaboration Needs**: Suggest specific team members to consult for each gap
            4. **Miro Integration**: Provide step-by-step instructions for creating this in Miro
            """
            
            try:
                with st.spinner("🔄 Generating mind map structure..."):
                    mind_map_response = model.generate_content(mind_map_prompt)
                
                st.subheader("🗺️ Mind Map Structure & Knowledge Gaps")
                st.write(mind_map_response.text)
                
                # Create actual Miro board
                st.subheader("🎨 Creating Miro Board")
                board_name = f"Training Mind Map - {tc.get('target_audience', 'General')} - {mmi.get('mind_map_type', 'Process Flow')}"
                
                miro_result = create_miro_mind_map(mind_map_response.text, board_name)
                
                if miro_result and miro_result.get('success'):
                    st.success("✅ Miro board created successfully!")
                    
                    # Add helpful instructions for finding content
                    st.info("""
                    🎯 **How to find your mind map content in Miro:**
                    1. **Click the 'Open in Miro' button below** to open the board
                    2. **Zoom out** (Ctrl/Cmd + scroll wheel) to see all content
                    3. **Look for text boxes** - your mind map nodes are text widgets
                    4. **Main topic** is centered at (0,0) coordinates
                    5. **Subtopics** are arranged around the main topic
                    6. **If you don't see content**, try refreshing the page or check the board URL
                    """)
                    
                    # Display the embedded Miro board
                    st.subheader("🗺️ Your Mind Map Board")
                    board_embed_url = miro_result.get('embed_url')
                    
                    # Embed the Miro board using iframe
                    st.components.v1.iframe(
                        src=board_embed_url,
                        width=800,
                        height=600,
                        scrolling=True
                    )
                    
                    # Add board management options
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                        <a href="{miro_result.get('board_url')}" target="_blank">
                            <button style="
                                background-color: #FF5C8D;
                                border: none;
                                color: white;
                                padding: 10px 20px;
                                text-align: center;
                                text-decoration: none;
                                display: inline-block;
                                font-size: 14px;
                                margin: 4px 2px;
                                cursor: pointer;
                                border-radius: 8px;
                                width: 100%;
                            ">
                                🎨 Open in Miro
                            </button>
                        </a>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error generating mind map: {str(e)}")

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

    
def build_context_aware_prompt(base_prompt, content, training_context=None):
    # Build a prompt that incorporates training context for more targeted content generation
    """Build a prompt that incorporates training context for more targeted content generation"""
    if not training_context:
        # If no training context, return the base prompt
        return f"{base_prompt}: {content}"
    
    # Build the context information
    context_info = f"""
    Training Context:
    - Target Audience: {training_context.get('target_audience', 'General')}
    - Training Type: {training_context.get('training_type', 'General')}
    - Urgency Level: {training_context.get('urgency_level', 'Medium')}
    - Timeline: {training_context.get('timeline', 'Flexible')}
    - Delivery Method: {training_context.get('delivery_method', 'Self-paced')}
    - Industry: {training_context.get('industry', 'General')}
    - Technical Level: {training_context.get('technical_level', 'Beginner')}
    """
    
    # Add file inventory information if available
    file_inventory = st.session_state.get('file_inventory', None)
    if file_inventory:
        file_info = f"""
    Existing Files:
    - Available Files: {', '.join(file_inventory.get('existing_files', []))}
    - File Quality: {file_inventory.get('file_quality', 'Unknown')}
    - File Formats: {', '.join(file_inventory.get('file_format', []))}
    """
        context_info += file_info
    
    # Add collaboration information if available
    collaboration_info = st.session_state.get('collaboration_info', None)
    if collaboration_info:
        collab_info = f"""
    Team Collaboration:
    - Collaboration Type: {collaboration_info.get('collaboration_needed', 'None')}
    - Team Members: {', '.join(collaboration_info.get('team_members', []))}
    - Session Format: {collaboration_info.get('session_type', 'None')}
    """
        context_info += collab_info
    
    return f"{base_prompt}\n\n{context_info}\n\nContent to analyze: {content}"
    # Return the prompt with the context information

# Process uploaded files if any
extracted_content = ""  # Initialize outside the if block
if uploaded_files:
    st.subheader("📄 Processing Uploaded Files")
    # Loop through each file and extract content
    for file in uploaded_files:
        # Debug: Show file info
        st.write(f"Processing file: {file.name} (Type: {file.type})")
        
        # Check if the file is a text file
        if file.type == "text/plain":
            # Read the file content
            extracted_content += file.read().decode("utf-8") + "\n\n"
        elif file.type == "application/pdf":
            # Read the PDF file
            pdf_reader = PyPDF2.PdfReader(file)
            # Loop through each page and extract text
            for page in pdf_reader.pages:
                # Extract text from the page
                extracted_content += page.extract_text() + "\n\n"
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # Read the DOCX file
            doc = Document(file)
            # Loop through each paragraph and extract text
            for para in doc.paragraphs:
                extracted_content += para.text + "\n\n"
    
    # Debug: Show if content was extracted
    st.write(f"Content length: {len(extracted_content)} characters")
    
    if extracted_content:
        st.subheader("Extracted Content")
        # Display the extracted content
        st.text_area("Content from uploaded files", extracted_content, height=300)
        
        # Cache the processed content for better performance
        if 'cached_content' not in st.session_state:
            st.session_state.cached_content = extracted_content[:1000]
        
        # Store extracted content in session state
        st.session_state.extracted_content = extracted_content
    else:
        st.warning("No content was extracted from the uploaded files.")