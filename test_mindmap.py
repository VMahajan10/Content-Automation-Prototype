#!/usr/bin/env python3
"""
Test script for mind map functionality
"""

import streamlit as st
from modules.mindmeister import create_mindmeister_mind_map, display_mind_map_from_session, generate_mind_map_content, parse_mind_map_data

def test_parsing():
    """Test the parsing function with sample data"""
    st.subheader("🧪 Testing Parsing Function")
    
    # Test content
    test_content = """**Onboarding**
- **Target Audience: New employees**
  - Audience Size: 10
  - Experience Level: Beginner
- **Training Goals**
  - Understand the material
- **Existing Resources**
  - Uploaded Files: 1
- **Timeline & Urgency**
  - Timeline: Soon (1 month)
  - Urgency: Medium
- **Success Metrics**
  - Through personal evaluations
- **Next Steps**
  - Review Training Context
  - Schedule Team Meetings
  - Develop Training Materials
  - Implement Training Program"""
    
    st.write("Test content:")
    st.code(test_content)
    
    # Parse the content
    branches = parse_mind_map_data(test_content.split('\n'))
    
    st.write("Parsed branches:")
    for branch, items in branches.items():
        st.write(f"**{branch}** ({len(items)} items):")
        for item in items:
            st.write(f"  - {item}")
    
    st.success("✅ Parsing test completed!")

def test_mind_map():
    """Test the mind map creation and display"""
    
    st.title("🧠 Mind Map Test")
    
    # Test parsing first
    test_parsing()
    
    st.markdown("---")
    
    # Test data
    training_context = {
        'target_audience': 'New Employees',
        'training_type': 'Onboarding',
        'timeline': '1 month',
        'urgency_level': 'Medium',
        'audience_size': '10',
        'audience_level': 'Beginner',
        'primary_goals': 'Understand the material\nImprove performance\nComplete training'
    }
    
    file_inventory = {
        'uploaded_files': ['handbook.pdf', 'checklist.docx']
    }
    
    collaboration_info = {
        'team_members': ['John Doe', 'Jane Smith']
    }
    
    mind_map_info = {
        'mind_map_type': 'Process Flow',
        'mind_map_focus': 'Employee Onboarding Process',
        'complexity_level': 'Moderate (Key details)'
    }
    
    if st.button("🧪 Test Mind Map Creation"):
        st.info("Testing mind map creation...")
        
        # Generate content
        content = generate_mind_map_content(training_context, file_inventory, collaboration_info, mind_map_info)
        st.write("Generated content:")
        st.code(content)
        
        # Create mind map
        result = create_mindmeister_mind_map(content, "Test Mind Map")
        
        if result and result.get('success'):
            st.success("✅ Mind map created successfully!")
            
            # Display the mind map
            st.markdown("---")
            st.markdown("### Displaying Mind Map:")
            display_mind_map_from_session()
        else:
            st.error("❌ Mind map creation failed")
    
    # Show session state info
    if st.button("🔍 Show Session State"):
        st.write("Session state keys:")
        for key in st.session_state.keys():
            st.write(f"- {key}")
        
        if 'mind_map_display_data' in st.session_state:
            st.write("Mind map data:")
            st.json(st.session_state.mind_map_display_data)

if __name__ == "__main__":
    test_mind_map() 