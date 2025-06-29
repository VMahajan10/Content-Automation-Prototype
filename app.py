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

def extract_key_topics_from_content(content, max_topics=5):
    """
    Extract key topics from uploaded content using AI
    """
    try:
        if not content or len(content.strip()) < 50:
            return []
        
        # Use Gemini to extract key topics
        prompt = f"""
        Extract the top {max_topics} most important topics or concepts from this training content:
        
        {content[:2000]}
        
        Return only the topic names, separated by commas. Keep them short and relevant.
        """
        
        response = model.generate_content(prompt)
        topics = [topic.strip() for topic in response.text.split(',') if topic.strip()]
        return topics[:max_topics]
    except Exception as e:
        st.warning(f"Could not extract topics from content: {str(e)}")
        return []

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

def create_miro_ai_mind_map(training_context, file_inventory, collaboration_info, mind_map_info, extracted_content=""):
    """
    Create a professional mind map using Miro's AI chatbot
    This integrates with Miro's AI assistant to generate high-quality mind maps
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
        
        # Create board first
        board_name = f"AI-Generated Training Mind Map - {training_context.get('target_audience', 'General')}"
        board_payload = {
            "name": board_name,
            "description": "Professional mind map generated by AI assistant"
        }
        
        st.info("🔄 Creating Miro board for AI mind map generation...")
        
        response = requests.post(f"{MIRO_API_URL}/boards", headers=headers, json=board_payload)
        
        if response.status_code != 201:
            st.error(f"❌ Failed to create Miro board: {response.status_code} - {response.text}")
            return None
            
        board_data = response.json()
        board_id = board_data.get('id')
        board_url = board_data.get('viewLink')
        
        st.success(f"✅ Miro board created successfully!")
        st.info(f"Board ID: {board_id}")
        
        # Enhanced content extraction from uploaded files
        enhanced_content = ""
        if extracted_content:
            # Process the extracted content to identify key topics and concepts
            enhanced_content = f"""
            **Extracted Content Analysis:**
            {extracted_content[:3000]}
            
            **Key Topics Identified:**
            - Training requirements and objectives
            - Process workflows and procedures
            - Compliance and safety guidelines
            - Performance metrics and KPIs
            - Best practices and standards
            - Common challenges and solutions
            """
        
        # Prepare comprehensive prompt for AI mind map generation
        ai_prompt = f"""
        Create a comprehensive, professional mind map for training and onboarding purposes based on the following information:

        **Training Context:**
        - Target Audience: {training_context.get('target_audience', 'General')}
        - Training Type: {training_context.get('training_type', 'General')}
        - Industry: {training_context.get('industry', 'General')}
        - Company Size: {training_context.get('company_size', 'General')}
        - Urgency Level: {training_context.get('urgency_level', 'Medium')}
        - Timeline: {training_context.get('timeline', 'Flexible')}
        - Delivery Method: {training_context.get('delivery_method', 'Self-paced')}
        - Technical Level: {training_context.get('technical_level', 'Beginner')}

        **Existing Files & Resources:**
        - Available Files: {', '.join(file_inventory.get('existing_files', []))}
        - File Quality: {file_inventory.get('file_quality', 'Unknown')}
        - File Formats: {', '.join(file_inventory.get('file_format', []))}

        **Team Collaboration:**
        - Collaboration Type: {collaboration_info.get('collaboration_needed', 'None') if collaboration_info else 'None'}
        - Team Members: {', '.join(collaboration_info.get('team_members', [])) if collaboration_info else 'None'}
        - Session Format: {collaboration_info.get('session_type', 'None') if collaboration_info else 'None'}

        **Mind Map Requirements:**
        - Process Areas: {', '.join(mind_map_info.get('process_areas', [])) if mind_map_info else 'General'}
        - Mind Map Type: {mind_map_info.get('mind_map_type', 'Process Flow') if mind_map_info else 'Process Flow'}

        **Uploaded Content Analysis:**
        {enhanced_content}

        **Instructions for AI Mind Map:**
        1. Create a comprehensive, professional mind map that visualizes the training process
        2. Include main branches for planning, development, delivery, and evaluation phases
        3. Add relevant subtopics based on the training context and industry
        4. Use appropriate colors, icons, and visual hierarchy
        5. Include knowledge gaps and areas that need team collaboration
        6. Make it visually appealing and easy to understand
        7. Focus on practical, actionable training steps
        8. Consider the target audience and technical level
        9. Include best practices and industry-specific considerations
        10. Add notes or callouts for important points
        11. Integrate content from uploaded files into relevant sections
        12. Create specific sections for documents, visual assets, sticky notes, tables, and interactive elements

        **Specific Content Integration:**
        - **Documents**: Create detailed specs, playbooks, and actionable steps
        - **Visual Assets**: Generate diagrams, charts, infographics, and mockups
        - **Sticky Notes**: Include brainstorming insights, key takeaways, and workshop activities
        - **Tables**: Add planning tools, tracking metrics, and performance analysis
        - **Interactive Elements**: Create clickable interfaces and navigation flows

        Please create a professional, well-structured mind map that can be used for training planning and execution.
        """
        
        st.info("🤖 Generating professional mind map with AI...")
        
        # Use our enhanced AI approach since Miro AI assistant endpoint doesn't exist
        return create_enhanced_miro_mind_map(ai_prompt, board_id, headers, board_url)
            
    except Exception as e:
        st.error(f"Error creating Miro AI mind map: {str(e)}")
        return None

def create_enhanced_miro_mind_map(ai_prompt, board_id, headers, board_url):
    """
    Create an enhanced mind map with better spacing and professional layout
    """
    try:
        # Use our existing Gemini AI to generate mind map structure
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        enhanced_prompt = f"""
        Based on this comprehensive training information, create a detailed mind map structure:

        {ai_prompt}

        Please provide the mind map structure in this format:
        **Main Topic 1**
        - Subtopic 1.1
        - Subtopic 1.2
        - Subtopic 1.3

        **Main Topic 2**
        - Subtopic 2.1
        - Subtopic 2.2
        - Subtopic 2.3

        And so on for 4-5 main topics with 3-4 subtopics each.
        Make sure the topics are relevant to the training context provided.
        """
        
        with st.spinner("🔄 Generating enhanced mind map structure with AI..."):
            mind_map_response = model.generate_content(enhanced_prompt)
        
        # Create the mind map using our enhanced spacing function
        mind_map_items = create_enhanced_mind_map_structure(
            mind_map_response.text, 
            board_id, 
            headers,
            training_context=st.session_state.get('training_context'),
            file_inventory=st.session_state.get('file_inventory'),
            collaboration_info=st.session_state.get('collaboration_info'),
            extracted_content=st.session_state.get('extracted_content', '')
        )
        
        if mind_map_items:
            st.success("✅ Enhanced professional mind map created successfully!")
            return {
                "success": True,
                "board_id": board_id,
                "board_url": board_url,
                "embed_url": f"https://miro.com/app/board/{board_id}/",
                "method": "enhanced_ai"
            }
        else:
            st.error("❌ Failed to create enhanced mind map")
            return None
            
    except Exception as e:
        st.error(f"Error in enhanced mind map creation: {str(e)}")
        return None

def create_enhanced_mind_map_structure(mind_map_data, board_id, headers, training_context=None, file_inventory=None, collaboration_info=None, extracted_content=""):
    """
    Create mind map with smart spacing algorithm to prevent text overlap
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
        
        # SMART SPACING ALGORITHM - Calculate dynamic spacing based on text length
        def calculate_text_dimensions(text, base_width=200, base_height=60):
            """Calculate dynamic width and height based on text length"""
            # Estimate characters per line (assuming average 12px font)
            chars_per_line = 25
            
            # Calculate how many lines this text will need
            lines_needed = max(1, len(text) // chars_per_line + (1 if len(text) % chars_per_line > 0 else 0))
            
            # Calculate dynamic width (minimum 200, maximum 400)
            dynamic_width = min(400, max(base_width, len(text) * 8))
            
            # Calculate dynamic height based on lines needed
            dynamic_height = max(base_height, lines_needed * 30 + 20)
            
            return dynamic_width, dynamic_height
        
        def calculate_safe_position(base_x, base_y, index, total_items, direction, min_distance=300):
            """Calculate safe position that doesn't overlap with existing items"""
            if direction == "vertical":
                # Vertical arrangement with dynamic spacing
                spacing = max(min_distance, 150)  # Minimum 150px between items
                y_offset = (index - (total_items - 1) / 2) * spacing
                return base_x, base_y + y_offset
            elif direction == "horizontal":
                # Horizontal arrangement with dynamic spacing
                spacing = max(min_distance, 200)  # Minimum 200px between items
                x_offset = (index - (total_items - 1) / 2) * spacing
                return base_x + x_offset, base_y
            else:
                # Radial arrangement
                angle = (index / total_items) * 2 * 3.14159
                radius = min_distance
                x_offset = radius * math.cos(angle)
                y_offset = radius * math.sin(angle)
                return base_x + x_offset, base_y + y_offset
        
        # Create comprehensive mind map nodes with ALL features
        all_widgets = []
        
        # Add central topic with dynamic sizing
        central_topic = main_topics[0] if main_topics else "Training Process"
        central_text = f"🎯 {central_topic}"
        central_width, central_height = calculate_text_dimensions(central_text, 400, 100)
        
        all_widgets.append({
            "type": "text",
            "text": central_text,
            "x": 0,
            "y": 0,
            "width": central_width,
            "height": central_height,
            "widget_type": "central_topic"
        })
        
        # Create SPACED OUT layout with smart positioning
        # Main branches positioned in a clean cross pattern with MORE SPACING
        main_branch_positions = [
            (-1000, 0, "📋", "Planning Phase"),      # Left - EVEN MORE SPACING
            (1000, 0, "🛠️", "Development Phase"),   # Right - EVEN MORE SPACING
            (0, -800, "📚", "Delivery Phase"),       # Top - EVEN MORE SPACING
            (0, 800, "📊", "Evaluation Phase")       # Bottom - EVEN MORE SPACING
        ]
        
        # Use default topics if we don't have enough from AI
        default_topics = ["Planning Phase", "Development Phase", "Delivery Phase", "Evaluation Phase"]
        
        for i in range(4):  # Always create 4 main branches
            if i + 1 < len(main_topics):
                topic = main_topics[i + 1]
            else:
                topic = default_topics[i] if i < len(default_topics) else f"Topic {i + 1}"
            
            x, y, emoji, default_name = main_branch_positions[i]
            branch_text = f"{emoji} {topic}"
            branch_width, branch_height = calculate_text_dimensions(branch_text, 300, 80)
            
            all_widgets.append({
                "type": "text",
                "text": branch_text,
                "x": x,
                "y": y,
                "width": branch_width,
                "height": branch_height,
                "widget_type": "main_branch"
            })
            
            # Add comprehensive content for this branch
            branch_topic = topic
            
            # Add subtopics with SMART SPACING
            topic_subtopics = subtopics.get(branch_topic, [])
            for j, subtopic in enumerate(topic_subtopics[:4]):
                subtopic_text = f"• {subtopic}"
                subtopic_width, subtopic_height = calculate_text_dimensions(subtopic_text, 220, 60)
                
                # Calculate SMART POSITION based on branch direction
                if i == 0:  # Left branch
                    sub_x = x - 800
                    sub_y = y - 400 + (j * 250)
                elif i == 1:  # Right branch
                    sub_x = x + 800
                    sub_y = y - 400 + (j * 250)
                elif i == 2:  # Top branch
                    sub_x = x - 500 + (j * 300)
                    sub_y = y - 800
                else:  # Bottom branch
                    sub_x = x - 500 + (j * 300)
                    sub_y = y + 800
                
                # Apply final position adjustment to prevent overlap
                final_x, final_y = calculate_safe_position(sub_x, sub_y, j, len(topic_subtopics[:4]), "vertical" if i < 2 else "horizontal")
                
                all_widgets.append({
                    "type": "text",
                    "text": subtopic_text,
                    "x": final_x,
                    "y": final_y,
                    "width": subtopic_width,
                    "height": subtopic_height,
                    "widget_type": "subtopic"
                })
            
            # Add DOCUMENT widgets (detailed specs and playbooks)
            # Generate dynamic content based on training context and extracted content
            doc_content = []
            
            # Add training specifications document with actual context
            if training_context:
                doc_content.append(f"📄 Training Specifications\n• Target: {training_context.get('target_audience', 'General')}\n• Type: {training_context.get('training_type', 'General')}\n• Level: {training_context.get('technical_level', 'Beginner')}")
                
                # Add implementation playbook with timeline and delivery info
                doc_content.append(f"📄 Implementation Playbook\n• Timeline: {training_context.get('timeline', 'Flexible')}\n• Delivery: {training_context.get('delivery_method', 'Self-paced')}\n• Industry: {training_context.get('industry', 'General')}")
                
                # Add content from uploaded files if available
                if extracted_content:
                    # Extract key topics from uploaded content
                    key_topics = extract_key_topics_from_content(extracted_content)
                    if key_topics:
                        doc_content.append(f"📄 Content Analysis\n• Key Topics: {', '.join(key_topics[:3])}\n• File Quality: {file_inventory.get('file_quality', 'Unknown') if file_inventory else 'Unknown'}\n• Formats: {', '.join(file_inventory.get('file_format', [])[:2]) if file_inventory else 'Unknown'}")
                    else:
                        doc_content.append(f"📄 Content Analysis\n• {len(extracted_content)} characters analyzed\n• File Quality: {file_inventory.get('file_quality', 'Unknown') if file_inventory else 'Unknown'}\n• Ready for integration")
            else:
                # Fallback content
                doc_content = [
                    f"📄 Training Specifications\n• Detailed requirements\n• Learning objectives\n• Success criteria",
                    f"📄 Implementation Playbook\n• Step-by-step guide\n• Best practices\n• Common pitfalls"
                ]
            
            for j, doc in enumerate(doc_content[:2]):
                doc_width, doc_height = calculate_text_dimensions(doc, 280, 120)
                
                # Position documents to the side of subtopics
                if i == 0:  # Left branch
                    doc_x = x - 1200
                    doc_y = y - 200 + (j * 350)
                elif i == 1:  # Right branch
                    doc_x = x + 1200
                    doc_y = y - 200 + (j * 350)
                elif i == 2:  # Top branch
                    doc_x = x - 800 + (j * 450)
                    doc_y = y - 1200
                else:  # Bottom branch
                    doc_x = x - 800 + (j * 450)
                    doc_y = y + 1200
                
                all_widgets.append({
                    "type": "text",
                    "text": doc,
                    "x": doc_x,
                    "y": doc_y,
                    "width": doc_width,
                    "height": doc_height,
                    "widget_type": "document"
                })
            
            # Add VISUAL ASSETS widgets (diagrams, charts, infographics)
            # Generate dynamic visual content based on training context
            visual_content = []
            
            if training_context:
                # Add process flow diagram with actual training type
                training_type = training_context.get('training_type', 'Training')
                visual_content.append(f"🖼️ {training_type} Process Flow\n• Planning → Development → Delivery → Evaluation\n• Key milestones and decision points\n• Success indicators")
                
                # Add performance metrics chart with actual metrics
                success_metrics = training_context.get('success_metrics', 'Standard metrics')
                visual_content.append(f"📊 Performance Metrics Dashboard\n• KPIs: Completion rates, assessment scores\n• Progress tracking: Weekly milestones\n• Success metrics: {success_metrics}")
                
                # Add industry-specific visuals
                industry = training_context.get('industry')
                if industry and industry.strip():
                    visual_content.append(f"🖼️ {industry} Industry Diagram\n• Industry-specific workflows\n• Compliance requirements\n• Best practices visualization")
            else:
                # Fallback content
                visual_content = [
                    f"🖼️ Process Flow Diagram\n• Visual workflow\n• Decision points\n• Key milestones",
                    f"📊 Performance Metrics Chart\n• KPIs and targets\n• Progress tracking\n• Success indicators"
                ]
            
            for j, visual in enumerate(visual_content[:2]):
                visual_width, visual_height = calculate_text_dimensions(visual, 250, 100)
                
                # Position visuals near documents
                if i == 0:  # Left branch
                    vis_x = x - 1400
                    vis_y = y + 200 + (j * 250)
                elif i == 1:  # Right branch
                    vis_x = x + 1400
                    vis_y = y + 200 + (j * 250)
                elif i == 2:  # Top branch
                    vis_x = x + 800 + (j * 350)
                    vis_y = y - 1200
                else:  # Bottom branch
                    vis_x = x + 800 + (j * 350)
                    vis_y = y + 1200
                
                all_widgets.append({
                    "type": "text",
                    "text": visual,
                    "x": vis_x,
                    "y": vis_y,
                    "width": visual_width,
                    "height": visual_height,
                    "widget_type": "visual_asset"
                })
            
            # Add STICKY NOTES widgets (insights, takeaways, brainstorming)
            sticky_content = [
                f"📝 Key Insight\n• Important learning\n• Critical success factor",
                f"📝 Workshop Activity\n• Interactive exercise\n• Group discussion",
                f"📝 Best Practice\n• Proven approach\n• Industry standard"
            ]
            for j, sticky in enumerate(sticky_content[:3]):
                sticky_width, sticky_height = calculate_text_dimensions(sticky, 200, 80)
                
                # Position sticky notes in clusters
                if i == 0:  # Left branch
                    sticky_x = x - 1600
                    sticky_y = y - 100 + (j * 180)
                elif i == 1:  # Right branch
                    sticky_x = x + 1600
                    sticky_y = y - 100 + (j * 180)
                elif i == 2:  # Top branch
                    sticky_x = x - 200 + (j * 280)
                    sticky_y = y - 1400
                else:  # Bottom branch
                    sticky_x = x - 200 + (j * 280)
                    sticky_y = y + 1400
                
                all_widgets.append({
                    "type": "text",
                    "text": sticky,
                    "x": sticky_x,
                    "y": sticky_y,
                    "width": sticky_width,
                    "height": sticky_height,
                    "widget_type": "sticky_note"
                })
            
            # Add TABLE widgets (planning tools, tracking metrics)
            table_content = [
                f"📊 Training Timeline\n• Week 1: Planning\n• Week 2: Development\n• Week 3: Delivery\n• Week 4: Evaluation",
                f"📊 Resource Allocation\n• Budget: $10,000\n• Time: 40 hours\n• Team: 5 members\n• Tools: LMS, Video"
            ]
            for j, table in enumerate(table_content[:2]):
                table_width, table_height = calculate_text_dimensions(table, 240, 120)
                
                # Position tables near sticky notes
                if i == 0:  # Left branch
                    table_x = x - 1800
                    table_y = y + 300 + (j * 250)
                elif i == 1:  # Right branch
                    table_x = x + 1800
                    table_y = y + 300 + (j * 250)
                elif i == 2:  # Top branch
                    table_x = x + 400 + (j * 400)
                    table_y = y - 1400
                else:  # Bottom branch
                    table_x = x + 400 + (j * 400)
                    table_y = y + 1400
                
                all_widgets.append({
                    "type": "text",
                    "text": table,
                    "x": table_x,
                    "y": table_y,
                    "width": table_width,
                    "height": table_height,
                    "widget_type": "table"
                })
            
            # Add INTERACTIVE ELEMENTS widgets (clickable interfaces, prototypes)
            interactive_content = [
                f"🖱️ Training Platform\n• Clickable modules\n• Interactive quizzes\n• Progress tracking",
                f"🖱️ Assessment Tool\n• Online evaluations\n• Skill assessments\n• Certification system"
            ]
            for j, interactive in enumerate(interactive_content[:2]):
                interactive_width, interactive_height = calculate_text_dimensions(interactive, 220, 90)
                
                # Position interactive elements near tables
                if i == 0:  # Left branch
                    int_x = x - 2000
                    int_y = y + 100 + (j * 200)
                elif i == 1:  # Right branch
                    int_x = x + 2000
                    int_y = y + 100 + (j * 200)
                elif i == 2:  # Top branch
                    int_x = x + 600 + (j * 350)
                    int_y = y - 1600
                else:  # Bottom branch
                    int_x = x + 600 + (j * 350)
                    int_y = y + 1600
                
                all_widgets.append({
                    "type": "text",
                    "text": interactive,
                    "x": int_x,
                    "y": int_y,
                    "width": interactive_width,
                    "height": interactive_height,
                    "widget_type": "interactive_element"
                })
        
        # Store created widget IDs for connectors
        created_widgets = []
        
        # Add all widgets first with different styling based on widget type
        for i, widget in enumerate(all_widgets):
            try:
                # Create the widget payload with different styling based on type
                miro_widget = {
                    "type": "text",
                    "text": widget["text"],
                    "x": widget["x"],
                    "y": widget["y"],
                    "width": widget["width"]
                }
                
                # Add different styling based on widget type
                widget_type = widget.get("widget_type", "text")
                if widget_type == "central_topic":
                    miro_widget["style"] = {
                        "backgroundColor": "#FF6B6B",
                        "borderColor": "#FF5252",
                        "borderWidth": 4,  # Changed from "3" to 4 (valid enum value)
                        "fontSize": 18,    # Changed from "18" to 18 (integer)
                        "fontFamily": "Arial"
                    }
                elif widget_type == "main_branch":
                    miro_widget["style"] = {
                        "backgroundColor": "#4ECDC4",
                        "borderColor": "#26A69A",
                        "borderWidth": 2,  # Changed from "2" to 2 (integer)
                        "fontSize": 16,    # Changed from "16" to 16 (integer)
                        "fontFamily": "Arial"
                    }
                elif widget_type == "subtopic":
                    miro_widget["style"] = {
                        "backgroundColor": "#45B7D1",
                        "borderColor": "#1976D2",
                        "borderWidth": 2,  # Changed from "1" to 2 (valid enum value)
                        "fontSize": 14,    # Changed from "14" to 14 (integer)
                        "fontFamily": "Arial"
                    }
                elif widget_type == "document":
                    miro_widget["style"] = {
                        "backgroundColor": "#FFEAA7",
                        "borderColor": "#FDCB6E",
                        "borderWidth": 2,  # Changed from "2" to 2 (integer)
                        "fontSize": 12,    # Changed from "12" to 12 (integer)
                        "fontFamily": "Arial"
                    }
                elif widget_type == "visual_asset":
                    miro_widget["style"] = {
                        "backgroundColor": "#A8E6CF",
                        "borderColor": "#66BB6A",
                        "borderWidth": 2,  # Changed from "2" to 2 (integer)
                        "fontSize": 12,    # Changed from "12" to 12 (integer)
                        "fontFamily": "Arial"
                    }
                elif widget_type == "sticky_note":
                    miro_widget["style"] = {
                        "backgroundColor": "#FFB3BA",
                        "borderColor": "#FF8A80",
                        "borderWidth": 2,  # Changed from "1" to 2 (valid enum value)
                        "fontSize": 11,    # Changed from "11" to 11 (integer)
                        "fontFamily": "Arial"
                    }
                elif widget_type == "table":
                    miro_widget["style"] = {
                        "backgroundColor": "#DDA0DD",
                        "borderColor": "#AB47BC",
                        "borderWidth": 2,  # Changed from "2" to 2 (integer)
                        "fontSize": 12,    # Changed from "12" to 12 (integer)
                        "fontFamily": "Arial"
                    }
                elif widget_type == "interactive_element":
                    miro_widget["style"] = {
                        "backgroundColor": "#FFD93D",
                        "borderColor": "#FFC107",
                        "borderWidth": 2,  # Changed from "2" to 2 (integer)
                        "fontSize": 12,    # Changed from "12" to 12 (integer)
                        "fontFamily": "Arial"
                    }
                
                # Debug: Show what we're sending to Miro
                st.write(f"🔍 Debug: Creating {widget_type} widget {i+1}: {widget['text']} at ({widget['x']}, {widget['y']}) with size {widget['width']}x{widget['height']}")
                
                # Create the widget
                widget_response = requests.post(
                    f"{MIRO_API_URL}/boards/{board_id}/widgets",
                    headers=headers,
                    json=miro_widget
                )
                
                if widget_response.status_code == 201 or widget_response.status_code == 200:
                    widget_data = widget_response.json()
                    widget_id = widget_data.get('id')
                    created_widgets.append({
                        "id": widget_id,
                        "x": widget["x"],
                        "y": widget["y"],
                        "text": widget["text"],
                        "type": widget_type
                    })
                    st.success(f"✅ Created {widget_type} widget: {widget['text']} (ID: {widget_id})")
                else:
                    st.warning(f"⚠️ Could not create {widget_type} widget '{widget['text']}': {widget_response.status_code} - {widget_response.text}")
                    
            except Exception as e:
                st.warning(f"⚠️ Error creating {widget.get('widget_type', 'text')} widget '{widget['text']}': {str(e)}")
        
        # Now create connectors (lines) between nodes
        st.info("🔄 Creating mind map connectors...")
        
        # Create organized connections
        connections = []
        
        if len(created_widgets) > 0:
            central_widget_idx = 0
            
            # Connect central topic to main branches (widgets 1-4)
            for i in range(1, min(5, len(created_widgets))):
                connections.append((central_widget_idx, i))
            
            # Connect main branches to their subtopics and other elements
            # This is a simplified connection strategy - in a real implementation,
            # you'd want more sophisticated connection logic
            for branch_idx in range(1, 5):  # Main branches are at indices 1-4
                if branch_idx < len(created_widgets):
                    # Connect to nearby elements (simplified approach)
                    for j in range(5, min(len(created_widgets), 20)):  # Connect to first 15 additional elements
                        connections.append((branch_idx, j))
        
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
        st.error(f"Error creating enhanced mind map structure: {str(e)}")
        return 0

def create_miro_ai_content(training_context, file_inventory, collaboration_info, mind_map_info, extracted_content="", content_type="mindmap"):
    """
    Create different types of Miro AI content based on the specified type
    Supports: doc, image, sticky_notes, table, mindmap, prototype
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
        
        # Create board first
        content_type_names = {
            "doc": "Document",
            "image": "Visual Assets", 
            "sticky_notes": "Sticky Notes",
            "table": "Table",
            "mindmap": "Mind Map",
            "prototype": "Prototype"
        }
        
        board_name = f"AI-Generated {content_type_names.get(content_type, 'Content')} - {training_context.get('target_audience', 'General')}"
        board_payload = {
            "name": board_name,
            "description": f"Professional {content_type} generated by AI assistant"
        }
        
        st.info(f"🔄 Creating Miro board for {content_type} generation...")
        
        response = requests.post(f"{MIRO_API_URL}/boards", headers=headers, json=board_payload)
        
        if response.status_code != 201:
            st.error(f"❌ Failed to create Miro board: {response.status_code} - {response.text}")
            return None
            
        board_data = response.json()
        board_id = board_data.get('id')
        board_url = board_data.get('viewLink')
        
        st.success(f"✅ Miro board created successfully!")
        st.info(f"Board ID: {board_id}")
        
        # Prepare comprehensive prompt for AI content generation
        ai_prompt = f"""
        Create a professional {content_type} for training and onboarding purposes based on the following information:

        **Training Context:**
        - Target Audience: {training_context.get('target_audience', 'General')}
        - Training Type: {training_context.get('training_type', 'General')}
        - Industry: {training_context.get('industry', 'General')}
        - Company Size: {training_context.get('company_size', 'General')}
        - Urgency Level: {training_context.get('urgency_level', 'Medium')}
        - Timeline: {training_context.get('timeline', 'Flexible')}
        - Delivery Method: {training_context.get('delivery_method', 'Self-paced')}
        - Technical Level: {training_context.get('technical_level', 'Beginner')}

        **Existing Files & Resources:**
        - Available Files: {', '.join(file_inventory.get('existing_files', []))}
        - File Quality: {file_inventory.get('file_quality', 'Unknown')}
        - File Formats: {', '.join(file_inventory.get('file_format', []))}

        **Team Collaboration:**
        - Collaboration Type: {collaboration_info.get('collaboration_needed', 'None') if collaboration_info else 'None'}
        - Team Members: {', '.join(collaboration_info.get('team_members', [])) if collaboration_info else 'None'}
        - Session Format: {collaboration_info.get('session_type', 'None') if collaboration_info else 'None'}

        **Content Requirements:**
        - Process Areas: {', '.join(mind_map_info.get('process_areas', [])) if mind_map_info else 'General'}
        - Content Type: {content_type_names.get(content_type, 'General')}

        **Uploaded Content:**
        {extracted_content[:2000] if extracted_content else 'No additional content provided'}

        **Instructions for {content_type.upper()} Generation:**
        """
        
        # Add specific instructions based on content type
        if content_type == "doc":
            ai_prompt += """
        1. Create a comprehensive training document (specs, playbook, notes, or report)
        2. Include clear sections with headings and subheadings
        3. Add actionable steps and best practices
        4. Include industry-specific examples and case studies
        5. Make it easy to follow and implement
        6. Add checklists and templates where appropriate
        """
        elif content_type == "image":
            ai_prompt += """
        1. Generate visual assets for training presentations
        2. Create mockups, diagrams, and infographics
        3. Design campaign materials and creative elements
        4. Include charts, graphs, and visual data representation
        5. Make visuals engaging and informative
        6. Use appropriate colors and branding elements
        """
        elif content_type == "sticky_notes":
            ai_prompt += """
        1. Generate ideas for brainstorming sessions
        2. Create insights and key takeaways
        3. Design workshop activities and exercises
        4. Plan roadmaps and strategic initiatives
        5. Organize thoughts and concepts clearly
        6. Use color coding for different categories
        """
        elif content_type == "table":
            ai_prompt += """
        1. Create tables for planning and tracking
        2. Include research data and analysis
        3. Design backlogs and project management tools
        4. Add performance metrics and KPIs
        5. Organize information in logical categories
        6. Make data easy to read and understand
        """
        elif content_type == "mindmap":
            ai_prompt += """
        1. Create a comprehensive mind map with proper spacing
        2. Include main branches for planning, development, delivery, and evaluation
        3. Add relevant subtopics based on the training context and industry
        4. Use appropriate colors, icons, and visual hierarchy
        5. Include knowledge gaps and collaboration needs
        6. Make it visually appealing and easy to understand
        7. Focus on practical, actionable training steps
        8. Consider the target audience and technical level
        9. Include best practices and industry-specific considerations
        10. Add notes or callouts for important points
        """
        elif content_type == "prototype":
            ai_prompt += """
        1. Create clickable interfaces for training platforms
        2. Design app mockups and website layouts
        3. Include user flows and navigation paths
        4. Add interactive elements and user experience features
        5. Make interfaces intuitive and user-friendly
        6. Include responsive design considerations
        """
        
        ai_prompt += f"\n\nPlease create a professional, well-structured {content_type} that can be used for training planning and execution."
        
        st.info(f"🤖 Generating professional {content_type} with AI...")
        
        # Use our enhanced AI approach for different content types
        if content_type == "mindmap":
            return create_enhanced_miro_mind_map(ai_prompt, board_id, headers, board_url)
        else:
            # For other content types, create a basic structure
            return create_basic_miro_content(ai_prompt, board_id, headers, board_url, content_type)
            
    except Exception as e:
        st.error(f"Error creating Miro AI {content_type}: {str(e)}")
        return None

def create_basic_miro_content(ai_prompt, board_id, headers, board_url, content_type):
    """
    Create basic Miro content for non-mindmap types
    """
    try:
        # Use our existing Gemini AI to generate content structure
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        enhanced_prompt = f"""
        Based on this comprehensive training information, create a detailed {content_type} structure:

        {ai_prompt}

        Please provide the {content_type} structure in a format that can be implemented in Miro.
        """
        
        with st.spinner(f"🔄 Generating {content_type} structure with AI..."):
            content_response = model.generate_content(enhanced_prompt)
        
        # For now, create a simple text widget with the generated content
        # In the future, this could be expanded to create specific widget types
        try:
            content_widget = {
                "type": "text",
                "text": f"AI-Generated {content_type.upper()} Content:\n\n{content_response.text[:1000]}...",
                "x": 0,
                "y": 0,
                "width": 600,
                "height": 400
            }
            
            response = requests.post(
                f"{MIRO_API_URL}/boards/{board_id}/widgets",
                headers=headers,
                json=content_widget
            )
            
            if response.status_code == 201 or response.status_code == 200:
                st.success(f"✅ {content_type.title()} content created successfully!")
                return {
                    "success": True,
                    "board_id": board_id,
                    "board_url": board_url,
                    "embed_url": f"https://miro.com/app/board/{board_id}/",
                    "method": f"enhanced_ai_{content_type}"
                }
            else:
                st.error(f"❌ Failed to create {content_type} content")
                return None
                
        except Exception as e:
            st.error(f"Error creating {content_type} widget: {str(e)}")
            return None
            
    except Exception as e:
        st.error(f"Error in {content_type} creation: {str(e)}")
        return None

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
    
    # Process uploaded files if any
    if uploaded_files:
        st.subheader("📄 Processing Uploaded Files")
        extracted_content = ""  # Initialize content variable
        
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

        # Single comprehensive mind map generation button that uses all AI features
        if mmi and st.button("🚀 Create Professional Mind Map with AI", key="generate_comprehensive_mind_map", type="primary"):
            st.subheader("🚀 Professional AI Mind Map Generation")
            st.info("""
            **🎯 What this professional system does:**
            - **🗺️ Smart Mind Map**: Creates well-spaced, professional mind maps with proper visual hierarchy
            - **📄 Document Integration**: Adds detailed specs, playbooks, and actionable steps as notes
            - **🖼️ Visual Assets**: Generates diagrams, charts, infographics, and mockups
            - **📝 Sticky Notes**: Includes brainstorming insights, key takeaways, and workshop activities
            - **📊 Tables**: Adds planning tools, tracking metrics, and performance analysis
            - **🖱️ Interactive Elements**: Creates clickable prototypes and navigation flows where relevant
            - **✨ All features work together** to create the ultimate training visualization
            - **🎨 Smart Spacing**: Dynamic text sizing and overlap prevention for better readability
            """)
            
            # Get extracted content from uploaded files
            extracted_content = st.session_state.get('extracted_content', '')
            
            try:
                with st.spinner("🚀 AI is creating your professional mind map..."):
                    mind_map_result = create_miro_ai_mind_map(
                        training_context=tc,
                        file_inventory=fi,
                        collaboration_info=ci,
                        mind_map_info=mmi,
                        extracted_content=extracted_content
                    )
                
                if mind_map_result and mind_map_result.get('success'):
                    st.success("✅ Professional AI Mind Map created successfully!")
                    
                    # Show enhanced features used
                    st.success("🎉 Used enhanced AI system for professional mind map!")
                    st.info("""
                    ✨ **Professional Features Used:**
                    - **Smart Spacing**: Dynamic text sizing and overlap prevention
                    - **Document Integration**: Detailed specs and playbooks
                    - **Visual Assets**: Charts, diagrams, and infographics
                    - **Sticky Notes**: Brainstorming insights and takeaways
                    - **Tables**: Planning tools and metrics
                    - **Interactive Elements**: Clickable prototypes
                    - **Professional Layout**: All elements work together cohesively
                    """)
                    
                    # Add helpful instructions
                    st.info("""
                    🎯 **Your Professional AI Mind Map is Ready!**
                    1. **Click 'Open in Miro'** to explore your AI-enhanced mind map
                    2. **Multiple content types** integrated into one comprehensive view
                    3. **Smart spacing** ensures everything is readable and well-organized
                    4. **Interactive elements** for better engagement
                    5. **Professional visuals** with charts, diagrams, and tables
                    6. **Complete training overview** with all your context and requirements
                    7. **Industry-specific content** based on your input
                    8. **Actionable insights** for your training planning
                    """)
                    
                    # Display the embedded Miro board
                    st.subheader("🚀 Your Professional AI-Enhanced Mind Map")
                    board_embed_url = mind_map_result.get('embed_url')
                    
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
                        <a href="{mind_map_result.get('board_url')}" target="_blank">
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
                    
                    with col2:
                        st.markdown(f"""
                        <a href="{mind_map_result.get('board_url')}" target="_blank">
                            <button style="
                                background-color: #4CAF50;
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
                                ✏️ Edit Mind Map
                            </button>
                        </a>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <button onclick="window.print()" style="
                            background-color: #2196F3;
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
                            📄 Export PDF
                        </button>
                        """, unsafe_allow_html=True)
                        
            except Exception as e:
                st.error(f"Error generating professional mind map: {str(e)}")

        # Generate different types of Miro AI content
        if mmi and st.button("🎨 Create Other AI Content Types", key="generate_miro_ai_content", type="secondary"):
            st.subheader("🎨 Miro AI Content Generation")
            st.info("""
            **🎯 Choose from different Miro AI content types:**
            - **📄 Document**: Create specs, playbooks, notes, or reports
            - **🖼️ Image**: Generate visuals, mockups, diagrams, infographics
            - **📝 Sticky Notes**: Create brainstorming ideas, insights, workshops
            - **📊 Table**: Build planning tables, tracking tools, analysis
            - **🖱️ Prototype**: Design clickable interfaces, apps, websites
            """)
            
            # Content type selector
            content_type = st.selectbox(
                "Choose content type:",
                [
                    ("doc", "📄 Document - Create specs, playbooks, reports"),
                    ("image", "🖼️ Image - Generate visuals and mockups"),
                    ("sticky_notes", "📝 Sticky Notes - Brainstorming and insights"),
                    ("table", "📊 Table - Planning and analysis tools"),
                    ("prototype", "🖱️ Prototype - Clickable interfaces")
                ],
                format_func=lambda x: x[1],
                help="Select the type of content you want to generate"
            )
            
            selected_type = content_type[0]
            
            # Get extracted content from uploaded files
            extracted_content = st.session_state.get('extracted_content', '')
            
            try:
                with st.spinner(f"🤖 Miro AI is creating your {selected_type}..."):
                    miro_content_result = create_miro_ai_content(
                        training_context=tc,
                        file_inventory=fi,
                        collaboration_info=ci,
                        mind_map_info=mmi,
                        extracted_content=extracted_content,
                        content_type=selected_type
                    )
                
                if miro_content_result and miro_content_result.get('success'):
                    content_type_names = {
                        "doc": "Document",
                        "image": "Visual Assets", 
                        "sticky_notes": "Sticky Notes",
                        "table": "Table",
                        "prototype": "Prototype"
                    }
                    
                    content_name = content_type_names.get(selected_type, selected_type.title())
                    st.success(f"✅ Professional {content_name} created by Miro AI!")
                    
                    # Show method used
                    method = miro_content_result.get('method', 'unknown')
                    if 'enhanced_ai' in method:
                        st.success("🎉 Used enhanced AI system for professional generation!")
                        st.info("✨ **Enhanced Features:** AI-generated content with professional structure")
                    
                    # Add helpful instructions
                    st.info(f"""
                    🎯 **Your Professional {content_name} is Ready!**
                    1. **Click 'Open in Miro'** to view your AI-generated content
                    2. **The content includes** all your training context and requirements
                    3. **Professional structure** tailored to your needs
                    4. **Industry-specific content** based on your input
                    5. **Actionable insights** for your training planning
                    """)
                    
                    # Display the embedded Miro board
                    st.subheader(f"🎨 Your Professional AI-Generated {content_name}")
                    board_embed_url = miro_content_result.get('embed_url')
                    
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
                        <a href="{miro_content_result.get('board_url')}" target="_blank">
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
                    
                    with col2:
                        st.markdown(f"""
                        <a href="{miro_content_result.get('board_url')}" target="_blank">
                            <button style="
                                background-color: #4CAF50;
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
                                ✏️ Edit Content
                            </button>
                        </a>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                        <button onclick="window.print()" style="
                            background-color: #2196F3;
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
                            📄 Export PDF
                        </button>
                        """, unsafe_allow_html=True)
                        
            except Exception as e:
                st.error(f"Error generating Miro AI {selected_type}: {str(e)}")

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

# Information about Miro AI Integration
with st.expander("ℹ️ About Miro AI Mind Map Generation"):
    st.write("""
    **🚀 Comprehensive Enhanced Mind Map Generation**
    
    This app now integrates ALL Miro AI capabilities into comprehensive mind maps! Here's what you can achieve:
    
    **✨ Integrated Features:**
    - **🗺️ Smart Mind Map**: Creates well-spaced, professional mind maps with proper visual hierarchy
    - **📄 Document Integration**: Adds detailed specs, playbooks, and actionable steps as notes
    - **🖼️ Visual Assets**: Generates diagrams, charts, infographics, and mockups
    - **📝 Sticky Notes**: Includes brainstorming insights, key takeaways, and workshop activities
    - **📊 Tables**: Adds planning tools, tracking metrics, and performance analysis
    - **🖱️ Interactive Elements**: Creates clickable prototypes and navigation flows where relevant
    - **✨ All features work together** to create the ultimate training visualization
    
    **🎯 What the AI Considers:**
    - **Training Context**: Audience, type, urgency, timeline, delivery method
    - **Industry & Company**: Size, sector, technical level, compliance needs
    - **Existing Resources**: File inventory, quality, formats
    - **Team Collaboration**: Session types, team members, recording needs
    - **Process Areas**: Organizational structure, workflows, decision making
    - **Uploaded Content**: Extracted text from PDFs, Word docs, etc.
    
    **🤖 Comprehensive AI Capabilities:**
    - **Smart Organization**: Logical grouping of related concepts with all content types
    - **Visual Hierarchy**: Clear main topics, subtopics, and supporting elements
    - **Content Integration**: Documents, visuals, sticky notes, tables, and interactive elements
    - **Color Coding**: Industry-appropriate color schemes for different content types
    - **Icon Selection**: Relevant icons for documents, visuals, notes, tables, and prototypes
    - **Knowledge Gaps**: Identifies areas needing more information
    - **Best Practices**: Industry-specific recommendations
    - **Enhanced Layout**: Smart spacing and positioning for all content types
    
    **🔄 Comprehensive System:**
    - **Primary**: Enhanced AI with ALL Miro features integrated
    - **Smart Spacing**: Dynamic text sizing and overlap prevention
    - **Content Variety**: Documents, visuals, sticky notes, tables, and interactive elements
    - **Professional Layout**: All elements work together cohesively
    - **Better Readability**: Larger text boxes and more spacing between elements
    
    **🔧 Requirements:**
    - Valid Miro API access token in your .env file
    - Miro account with appropriate permissions
    - Internet connection for API calls
    
    **💡 Best Results:**
    - Fill out all training context sections
    - Upload relevant documents
    - Specify collaboration needs
    - Choose appropriate process areas
    - Provide detailed industry information
    
    **🎨 Comprehensive Layout:**
    - **Larger Central Topic**: 400x100 pixels for better visibility
    - **Spaced Main Branches**: 1200 pixels from center for clear separation
    - **Organized Subtopics**: 800 pixels from main branches with 250-300 pixel spacing
    - **Document Integration**: Positioned near relevant branches with 250-300 pixel width
    - **Visual Assets**: Charts and diagrams positioned for maximum impact
    - **Sticky Notes**: Clustered insights with 180-200 pixel width
    - **Tables**: Planning tools with 220-250 pixel width
    - **Interactive Elements**: Prototypes positioned for engagement
    - **Clean Cross Pattern**: Professional layout with all content types integrated
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

def create_enhanced_comprehensive_mind_map(training_context, file_inventory, collaboration_info, mind_map_info, extracted_content=""):
    """
    Create a comprehensive mind map that integrates ALL Miro AI capabilities
    - Smart mind map with proper spacing
    - Document integration (specs, playbooks)
    - Visual assets (diagrams, charts)
    - Sticky notes (insights, takeaways)
    - Tables (planning tools, metrics)
    - Interactive elements (prototypes)
    """
    # For now, use the existing create_miro_ai_mind_map function
    return create_miro_ai_mind_map(training_context, file_inventory, collaboration_info, mind_map_info, extracted_content)

def create_comprehensive_mind_map_with_features(comprehensive_prompt, board_id, headers, board_url):
    """
    Create comprehensive mind map with integrated Miro AI features
    """
    # For now, use the existing create_enhanced_miro_mind_map function
    return create_enhanced_miro_mind_map(comprehensive_prompt, board_id, headers, board_url)

def create_comprehensive_mind_map_structure(comprehensive_data, board_id, headers):
    """
    Create comprehensive mind map with integrated Miro AI features
    """
    # For now, use the existing create_enhanced_mind_map_structure function
    return create_enhanced_mind_map_structure(comprehensive_data, board_id, headers)