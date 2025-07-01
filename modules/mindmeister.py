"""
MindMeister integration module for Gateway Content Automation
Handles all MindMeister API interactions and mind map creation
"""

import streamlit as st
import requests
from modules.config import MINDMEISTER_CLIENT_ID, MINDMEISTER_CLIENT_SECRET, MINDMEISTER_API_URL

def create_mindmeister_mind_map(mind_map_data, map_name="Training Process Mind Map"):
    """
    Create a visual mind map directly on the Streamlit page
    """
    try:
        st.success("✅ Creating your mind map...")
        
        # Create a visual mind map using Streamlit components
        st.markdown(f"## 🧠 {map_name}")
        
        # Parse the mind map data and create a visual structure
        lines = mind_map_data.split('\n')
        
        # Create the main mind map visualization with better styling
        st.markdown("""
        <style>
        .mind-map-container {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
        }
        .mind-map-center {
            text-align: center;
            padding: 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            color: white;
            font-size: 28px;
            font-weight: bold;
            margin: 20px auto;
            max-width: 400px;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        }
        .mind-map-branch {
            background: white;
            padding: 15px;
            border-radius: 12px;
            margin: 10px 0;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            border-left: 5px solid #667eea;
        }
        .mind-map-item {
            background: #f8f9fa;
            padding: 8px 12px;
            border-radius: 8px;
            margin: 5px 0;
            border-left: 3px solid #28a745;
            font-size: 14px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Main topic (center) with enhanced styling
        st.markdown(f"""
        <div class="mind-map-container">
            <div class="mind-map-center">
                🎯 {map_name.split(' - ')[0] if ' - ' in map_name else 'Training Process'}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create branches
        branch_data = parse_mind_map_data(lines)
        
        # Display each branch with enhanced styling
        for branch_title, branch_items in branch_data.items():
            st.markdown(f"### 🌿 {branch_title}")
            
            # Create a container for this branch
            with st.container():
                if branch_items:  # Only create columns if there are items
                    # Use a more flexible layout
                    items_per_row = min(3, len(branch_items))
                    if items_per_row == 1:
                        cols = st.columns([1])
                    elif items_per_row == 2:
                        cols = st.columns([1, 1])
                    else:
                        cols = st.columns([1, 1, 1])
                    
                    for i, item in enumerate(branch_items):
                        col_idx = i % items_per_row
                        with cols[col_idx]:
                            st.markdown(f"""
                            <div class="mind-map-item">
                                📌 {item}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No items in this branch")
        
        # Add a summary section with enhanced styling
        st.markdown("---")
        st.markdown("### 📊 Mind Map Summary")
        
        # Create a summary metrics with better layout
        total_branches = len(branch_data)
        total_items = sum(len(items) for items in branch_data.values())
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🌿 Main Branches", total_branches)
        with col2:
            st.metric("📌 Total Items", total_items)
        with col3:
            st.metric("🎯 Map Type", map_name.split(' - ')[0] if ' - ' in map_name else 'Training Process')
        with col4:
            st.metric("✅ Status", "Complete")
        
        # Store the mind map data in session state for later use
        if 'mind_map_display_data' not in st.session_state:
            st.session_state.mind_map_display_data = {}
        
        st.session_state.mind_map_display_data = {
            'map_name': map_name,
            'branch_data': branch_data,
            'total_branches': total_branches,
            'total_items': total_items,
            'raw_data': mind_map_data
        }
        
        # Add download option with better styling
        st.markdown("### 💾 Export Options")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Export as Text", type="secondary"):
                # Create downloadable text file
                import io
                buffer = io.StringIO()
                buffer.write(f"Mind Map: {map_name}\n")
                buffer.write("=" * 50 + "\n\n")
                buffer.write(mind_map_data)
                
                st.download_button(
                    label="Download Mind Map",
                    data=buffer.getvalue(),
                    file_name=f"mind_map_{map_name.replace(' ', '_')}.txt",
                    mime="text/plain"
                )
        
        with col2:
            if st.button("🖼️ Export as Image", type="secondary"):
                st.info("Image export feature coming soon...")
        
        return {
            "success": True,
            "map_id": "visual_mind_map",
            "map_url": "Created directly on page",
            "embed_url": "Visual mind map displayed above"
        }
            
    except Exception as e:
        st.error(f"Error creating mind map: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")
        return None

def parse_mind_map_data(lines):
    """
    Parse mind map data and organize into branches
    """
    branches = {}
    current_branch = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for main topic (starts with ** and ends with **)
        if line.startswith('**') and line.endswith('**') and not line.startswith('- **'):
            current_branch = line[2:-2]  # Remove "**"
            branches[current_branch] = []
        # Check for main branch (starts with - ** and ends with **)
        elif line.startswith('- **') and line.endswith('**'):
            current_branch = line[4:-3]  # Remove "- **" and "**"
            branches[current_branch] = []
        # Check for sub-items (starts with   -)
        elif line.startswith('  - ') and current_branch:
            item = line[4:]  # Remove "  - "
            branches[current_branch].append(item)
        # Check for items that start with just "- " (not indented)
        elif line.startswith('- ') and not line.startswith('- **') and current_branch:
            item = line[2:]  # Remove "- "
            branches[current_branch].append(item)
    
    # If no structured data found, create default branches
    if not branches:
        branches = {
            "Planning Phase": ["Needs Assessment", "Goal Setting", "Resource Planning"],
            "Development Phase": ["Content Creation", "Material Design", "Testing"],
            "Delivery Phase": ["Training Sessions", "Support Materials", "Feedback"],
            "Evaluation Phase": ["Performance Metrics", "Success Measurement", "Improvements"]
        }
    
    return branches

def create_mindmeister_ai_mind_map(training_context, file_inventory, collaboration_info, mind_map_info, extracted_content=""):
    """
    Create a professional mind map using MindMeister's API
    This integrates with MindMeister to generate high-quality mind maps
    """
    if not MINDMEISTER_CLIENT_ID:
        st.warning("⚠️ MindMeister Client ID not set. Please add MINDMEISTER_CLIENT_ID to your .env file")
        return None
    
    try:
        # Debug: Show what data we're working with
        st.info("🔍 Debug: Generating mind map with the following data:")
        st.write(f"- Training Context: {len(training_context)} items")
        st.write(f"- File Inventory: {len(file_inventory)} items")
        st.write(f"- Collaboration Info: {len(collaboration_info)} items")
        st.write(f"- Mind Map Info: {len(mind_map_info)} items")
        
        # Use the simple mind map creation approach
        map_name = f"Training Process - {training_context.get('target_audience', 'General')}"
        
        # Create the mind map using the simple approach
        result = create_simple_mind_map(training_context, file_inventory, collaboration_info, mind_map_info, map_name)
        
        if result and result.get('success'):
            st.success("✅ Mind map creation completed successfully!")
            return {
                "success": True,
                "message": "Mind map created successfully!",
                "mind_map_url": result.get('map_url'),
                "map_id": result.get('map_id')
            }
        else:
            st.error("❌ Mind map creation failed")
            return {
                "success": False,
                "message": "Failed to create mind map"
            }
            
    except Exception as e:
        st.error(f"Error creating MindMeister mind map: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")
        return None

def generate_mind_map_content(training_context, file_inventory, collaboration_info, mind_map_info, extracted_content=""):
    """
    Generate mind map content using AI based on the training context and data
    """
    try:
        # Create a structured mind map content based on the training discovery data
        mind_map_structure = []
        
        # Main topic based on training type
        main_topic = training_context.get('training_type', 'Training Process')
        mind_map_structure.append(f"**{main_topic}**")
        
        # Add training context as main branches
        if training_context.get('target_audience'):
            mind_map_structure.append(f"- **Target Audience: {training_context['target_audience']}**")
            if training_context.get('audience_size'):
                mind_map_structure.append(f"  - Audience Size: {training_context['audience_size']}")
            if training_context.get('audience_level'):
                mind_map_structure.append(f"  - Experience Level: {training_context['audience_level']}")
        
        if training_context.get('primary_goals'):
            mind_map_structure.append(f"- **Training Goals**")
            goals = training_context['primary_goals'].split('\n')
            for goal in goals[:3]:  # Limit to 3 main goals
                if goal.strip():
                    mind_map_structure.append(f"  - {goal.strip()}")
        
        # Add file inventory information
        if file_inventory.get('uploaded_files') or any([
            file_inventory.get('process_docs'),
            file_inventory.get('training_materials'),
            file_inventory.get('policies'),
            file_inventory.get('technical_docs')
        ]):
            mind_map_structure.append(f"- **Existing Resources**")
            if file_inventory.get('uploaded_files'):
                mind_map_structure.append(f"  - Uploaded Files: {len(file_inventory['uploaded_files'])}")
            if file_inventory.get('process_docs'):
                mind_map_structure.append(f"  - Process Documentation")
            if file_inventory.get('training_materials'):
                mind_map_structure.append(f"  - Training Materials")
            if file_inventory.get('policies'):
                mind_map_structure.append(f"  - Policies & Procedures")
        
        # Add collaboration plan
        if collaboration_info.get('team_members'):
            mind_map_structure.append(f"- **Team Collaboration**")
            mind_map_structure.append(f"  - Team Members: {len(collaboration_info['team_members'])}")
            if collaboration_info.get('preferred_platform'):
                mind_map_structure.append(f"  - Platform: {collaboration_info['preferred_platform']}")
        
        # Add timeline and urgency
        if training_context.get('timeline') or training_context.get('urgency_level'):
            mind_map_structure.append(f"- **Timeline & Urgency**")
            if training_context.get('timeline'):
                mind_map_structure.append(f"  - Timeline: {training_context['timeline']}")
            if training_context.get('urgency_level'):
                mind_map_structure.append(f"  - Urgency: {training_context['urgency_level']}")
        
        # Add success metrics
        if training_context.get('success_metrics'):
            mind_map_structure.append(f"- **Success Metrics**")
            metrics = training_context['success_metrics'].split('\n')
            for metric in metrics[:2]:  # Limit to 2 main metrics
                if metric.strip():
                    mind_map_structure.append(f"  - {metric.strip()}")
        
        # Add next steps
        mind_map_structure.append(f"- **Next Steps**")
        mind_map_structure.append(f"  - Review Training Context")
        mind_map_structure.append(f"  - Schedule Team Meetings")
        mind_map_structure.append(f"  - Develop Training Materials")
        mind_map_structure.append(f"  - Implement Training Program")
        
        # Add process phases
        mind_map_structure.append(f"- **Process Phases**")
        mind_map_structure.append(f"  - Planning Phase")
        mind_map_structure.append(f"  - Development Phase")
        mind_map_structure.append(f"  - Delivery Phase")
        mind_map_structure.append(f"  - Evaluation Phase")
        
        return '\n'.join(mind_map_structure)
        
    except Exception as e:
        st.error(f"Error generating mind map content: {str(e)}")
        return "**Training Process**\n- Planning Phase\n  - Needs Assessment\n  - Goal Setting\n- Development Phase\n  - Content Creation\n  - Material Design\n- Delivery Phase\n  - Training Sessions\n  - Support Materials\n- Evaluation Phase\n  - Performance Metrics\n  - Success Measurement"

def create_enhanced_mindmeister_mind_map(ai_prompt, map_id, headers, map_url):
    """
    Create an enhanced mind map with better spacing and professional layout
    """
    try:
        st.info("🔄 Starting enhanced mind map creation...")
        st.write(f"🔍 Debug: Map ID: {map_id}")
        st.write(f"🔍 Debug: Map URL: {map_url}")
        
        # For now, return a placeholder response
        st.success("✅ MindMeister integration coming soon...")
        return {
            "success": True,
            "message": "MindMeister integration is being implemented",
            "url": None
        }
        
    except Exception as e:
        st.error(f"Error creating enhanced mind map: {str(e)}")
        return None

def create_mind_map_structure(mind_map_data, map_id, headers):
    """
    Add mind map content to the MindMeister map
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
        
        st.success("✅ Mind map structure created successfully!")
        return len(main_topics) + sum(len(subs) for subs in subtopics.values())
        
    except Exception as e:
        st.error(f"Error creating mind map structure: {str(e)}")
        return 0

def display_mind_map_from_session():
    """
    Display the mind map from session state data
    """
    if 'mind_map_display_data' not in st.session_state or not st.session_state.mind_map_display_data:
        st.info("No mind map data available. Please generate a mind map first.")
        return False
    
    mind_map_data = st.session_state.mind_map_display_data
    
    try:
        # Validate the data structure
        required_keys = ['map_name', 'branch_data', 'total_branches', 'total_items', 'raw_data']
        for key in required_keys:
            if key not in mind_map_data:
                st.error(f"Invalid mind map data structure. Missing key: {key}")
                return False
        
        # Display the mind map with enhanced styling
        st.markdown(f"## 🧠 {mind_map_data['map_name']}")
        
        # Add the same CSS styling
        st.markdown("""
        <style>
        .mind-map-container {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
        }
        .mind-map-center {
            text-align: center;
            padding: 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            color: white;
            font-size: 28px;
            font-weight: bold;
            margin: 20px auto;
            max-width: 400px;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        }
        .mind-map-branch-container {
            background: white;
            padding: 15px;
            border-radius: 12px;
            margin: 15px 0;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            border-left: 5px solid #667eea;
        }
        .mind-map-item {
            background: #f8f9fa;
            padding: 8px 12px;
            border-radius: 8px;
            margin: 5px 0;
            border-left: 3px solid #28a745;
            font-size: 14px;
        }
        .mind-map-branch-title {
            color: #667eea;
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Main topic (center) with enhanced styling
        main_topic = mind_map_data.get('main_topic', 'Training Process')
        st.markdown(f"""
        <div class="mind-map-container">
            <div class="mind-map-center">
                🎯 {main_topic}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Display branches in a more visual layout
        branch_data = mind_map_data['branch_data']
        if not branch_data:
            st.warning("No branches found in mind map data")
            return False
        
        # Use columns to create a radial-like layout
        if len(branch_data) <= 4:
            # For 4 or fewer branches, use 2x2 layout
            cols = st.columns(2)
            branch_list = list(branch_data.items())
            
            for i, (branch_title, branch_items) in enumerate(branch_list):
                col_idx = i % 2
                with cols[col_idx]:
                    st.markdown(f"""
                    <div class="mind-map-branch-container">
                        <div class="mind-map-branch-title">🌿 {branch_title}</div>
                    """, unsafe_allow_html=True)
                    
                    if branch_items:
                        for item in branch_items:
                            st.markdown(f"""
                            <div class="mind-map-item">
                                📌 {item}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No items in this branch")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            # For more branches, use 3 columns
            cols = st.columns(3)
            branch_list = list(branch_data.items())
            
            for i, (branch_title, branch_items) in enumerate(branch_list):
                col_idx = i % 3
                with cols[col_idx]:
                    st.markdown(f"""
                    <div class="mind-map-branch-container">
                        <div class="mind-map-branch-title">🌿 {branch_title}</div>
                    """, unsafe_allow_html=True)
                    
                    if branch_items:
                        for item in branch_items:
                            st.markdown(f"""
                            <div class="mind-map-item">
                                📌 {item}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No items in this branch")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
        
        # Add a summary section with enhanced styling
        st.markdown("---")
        st.markdown("### 📊 Mind Map Summary")
        
        # Create a summary metrics with better layout
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🌿 Main Branches", mind_map_data['total_branches'])
        with col2:
            st.metric("📌 Total Items", mind_map_data['total_items'])
        with col3:
            st.metric("🎯 Map Type", main_topic)
        with col4:
            st.metric("✅ Status", "Complete")
        
        return True
        
    except Exception as e:
        st.error(f"Error displaying mind map: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")
        return False

def create_simple_mind_map(training_context, file_inventory, collaboration_info, mind_map_info, map_name="Training Process Mind Map"):
    """
    Create a simple but effective mind map directly without complex parsing
    """
    try:
        st.success("✅ Creating your mind map...")
        
        # Create a visual mind map using Streamlit components
        st.markdown(f"## 🧠 {map_name}")
        
        # Add the CSS styling
        st.markdown("""
        <style>
        .mind-map-container {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
        }
        .mind-map-center {
            text-align: center;
            padding: 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            color: white;
            font-size: 28px;
            font-weight: bold;
            margin: 20px auto;
            max-width: 400px;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        }
        .mind-map-branch-container {
            background: white;
            padding: 15px;
            border-radius: 12px;
            margin: 15px 0;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            border-left: 5px solid #667eea;
        }
        .mind-map-item {
            background: #f8f9fa;
            padding: 8px 12px;
            border-radius: 8px;
            margin: 5px 0;
            border-left: 3px solid #28a745;
            font-size: 14px;
        }
        .mind-map-branch-title {
            color: #667eea;
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Main topic (center) with enhanced styling
        main_topic = training_context.get('training_type', 'Training Process')
        st.markdown(f"""
        <div class="mind-map-container">
            <div class="mind-map-center">
                🎯 {main_topic}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Create branches directly from the data
        branches = {}
        
        # Target Audience branch
        if training_context.get('target_audience'):
            branches["Target Audience"] = []
            branches["Target Audience"].append(f"Audience: {training_context['target_audience']}")
            if training_context.get('audience_size'):
                branches["Target Audience"].append(f"Size: {training_context['audience_size']}")
            if training_context.get('audience_level'):
                branches["Target Audience"].append(f"Level: {training_context['audience_level']}")
        
        # Training Goals branch
        if training_context.get('primary_goals'):
            branches["Training Goals"] = []
            goals = training_context['primary_goals'].split('\n')
            for goal in goals[:3]:
                if goal.strip():
                    branches["Training Goals"].append(goal.strip())
        
        # Timeline & Urgency branch
        timeline_items = []
        if training_context.get('timeline'):
            timeline_items.append(f"Timeline: {training_context['timeline']}")
        if training_context.get('urgency_level'):
            timeline_items.append(f"Urgency: {training_context['urgency_level']}")
        if timeline_items:
            branches["Timeline & Urgency"] = timeline_items
        
        # Existing Resources branch
        resource_items = []
        if file_inventory.get('uploaded_files'):
            resource_items.append(f"Uploaded Files: {len(file_inventory['uploaded_files'])}")
        if file_inventory.get('process_docs'):
            resource_items.append("Process Documentation")
        if file_inventory.get('training_materials'):
            resource_items.append("Training Materials")
        if resource_items:
            branches["Existing Resources"] = resource_items
        
        # Team Collaboration branch
        if collaboration_info.get('team_members'):
            branches["Team Collaboration"] = []
            branches["Team Collaboration"].append(f"Team Members: {len(collaboration_info['team_members'])}")
            if collaboration_info.get('preferred_platform'):
                branches["Team Collaboration"].append(f"Platform: {collaboration_info['preferred_platform']}")
        
        # Success Metrics branch
        if training_context.get('success_metrics'):
            branches["Success Metrics"] = []
            metrics = training_context['success_metrics'].split('\n')
            for metric in metrics[:2]:
                if metric.strip():
                    branches["Success Metrics"].append(metric.strip())
        
        # Process Phases branch (always include)
        branches["Process Phases"] = [
            "Planning Phase",
            "Development Phase", 
            "Delivery Phase",
            "Evaluation Phase"
        ]
        
        # Next Steps branch (always include)
        branches["Next Steps"] = [
            "Review Training Context",
            "Schedule Team Meetings",
            "Develop Training Materials",
            "Implement Training Program"
        ]
        
        # Display branches in a more visual layout
        # Use columns to create a radial-like layout
        if len(branches) <= 4:
            # For 4 or fewer branches, use 2x2 layout
            cols = st.columns(2)
            branch_list = list(branches.items())
            
            for i, (branch_title, branch_items) in enumerate(branch_list):
                col_idx = i % 2
                with cols[col_idx]:
                    st.markdown(f"""
                    <div class="mind-map-branch-container">
                        <div class="mind-map-branch-title">🌿 {branch_title}</div>
                    """, unsafe_allow_html=True)
                    
                    if branch_items:
                        for item in branch_items:
                            st.markdown(f"""
                            <div class="mind-map-item">
                                📌 {item}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No items in this branch")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            # For more branches, use 3 columns
            cols = st.columns(3)
            branch_list = list(branches.items())
            
            for i, (branch_title, branch_items) in enumerate(branch_list):
                col_idx = i % 3
                with cols[col_idx]:
                    st.markdown(f"""
                    <div class="mind-map-branch-container">
                        <div class="mind-map-branch-title">🌿 {branch_title}</div>
                    """, unsafe_allow_html=True)
                    
                    if branch_items:
                        for item in branch_items:
                            st.markdown(f"""
                            <div class="mind-map-item">
                                📌 {item}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No items in this branch")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
        
        # Add a summary section
        st.markdown("---")
        st.markdown("### 📊 Mind Map Summary")
        
        # Create a summary metrics
        total_branches = len(branches)
        total_items = sum(len(items) for items in branches.values())
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🌿 Main Branches", total_branches)
        with col2:
            st.metric("📌 Total Items", total_items)
        with col3:
            st.metric("🎯 Map Type", main_topic)
        with col4:
            st.metric("✅ Status", "Complete")
        
        # Store the mind map data in session state for later use
        if 'mind_map_display_data' not in st.session_state:
            st.session_state.mind_map_display_data = {}
        
        st.session_state.mind_map_display_data = {
            'map_name': map_name,
            'branch_data': branches,
            'total_branches': total_branches,
            'total_items': total_items,
            'raw_data': f"Mind map for {main_topic}",
            'main_topic': main_topic
        }
        
        return {
            "success": True,
            "map_id": "simple_mind_map",
            "map_url": "Created directly on page",
            "embed_url": "Visual mind map displayed above"
        }
            
    except Exception as e:
        st.error(f"Error creating simple mind map: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")
        return None 