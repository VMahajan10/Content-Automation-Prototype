#!/usr/bin/env python3
"""
Test file for improved pathway section handling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pathway_section_improvements():
    """Test the improved pathway section handling functionality"""
    
    # Mock uploaded file
    class MockUploadedFile:
        def __init__(self, name, content, file_type="text/plain"):
            self.name = name
            self.content = content.encode('utf-8')
            self.type = file_type
        
        def read(self):
            return self.content
    
    # Test data
    test_content = """
    Advanced Quality Control Procedures
    
    1. Statistical Process Control (SPC)
    - Monitor key process parameters
    - Track control charts for trends
    - Implement corrective actions when needed
    - Document all SPC activities
    
    2. Root Cause Analysis
    - Use 5-Why methodology
    - Fishbone diagram analysis
    - Pareto chart for prioritization
    - Action plan development
    
    3. Continuous Improvement
    - Kaizen events and workshops
    - Process optimization
    - Standard work documentation
    - Training and certification
    """
    
    mock_file = MockUploadedFile("quality_manual.txt", test_content)
    
    # Test the extract_target_from_input function
    from app import extract_target_from_input
    
    # Test pathway section extraction
    result = extract_target_from_input("Update pathway 1 section 2 with new file")
    print(f"Pathway section extraction test: {result}")
    assert result and result['type'] == 'pathway_section' and result['pathway_num'] == 1 and result['section_num'] == 2
    
    # Test pathway section extraction with higher numbers
    result = extract_target_from_input("Update pathway 3 section 1 with new file")
    print(f"Pathway section extraction test (higher numbers): {result}")
    assert result and result['type'] == 'pathway_section' and result['pathway_num'] == 3 and result['section_num'] == 1
    
    # Test module extraction
    result = extract_target_from_input("Update module 2 with new file")
    print(f"Module extraction test: {result}")
    assert result and result['type'] == 'module' and result['identifier'] == 'module_2'
    
    # Test section extraction
    result = extract_target_from_input("Add content to safety section")
    print(f"Section extraction test: {result}")
    assert result and result['type'] == 'section' and result['identifier'] == 'safety'
    
    print("✅ All pathway section extraction tests passed!")
    
    # Test the update_pathway_section function with mock session state
    from app import update_pathway_section
    
    # Mock session state for testing
    import streamlit as st
    
    # Mock current pathway data
    st.session_state['generated_pathway'] = {
        'pathways': [
            {
                'pathway_name': 'Quality Training Program',
                'sections': [
                    {
                        'title': 'Introduction to Quality',
                        'modules': []
                    },
                    {
                        'title': 'Basic Quality Procedures',
                        'modules': []
                    },
                    {
                        'title': 'Advanced Quality Techniques',
                        'modules': []
                    }
                ]
            }
        ]
    }
    
    # Mock past pathways data
    st.session_state['past_generated_pathways'] = [
        {
            'pathways': [
                {
                    'pathway_name': 'Safety Training Program',
                    'sections': [
                        {
                            'title': 'Safety Basics',
                            'modules': []
                        },
                        {
                            'title': 'PPE Requirements',
                            'modules': []
                        }
                    ]
                }
            ]
        }
    ]
    
    # Test updating current pathway section
    target_info = {
        'type': 'pathway_section',
        'pathway_num': 1,
        'section_num': 2,
        'identifier': 'pathway_1_section_2'
    }
    
    new_content_modules = [
        {
            'title': 'New Quality Module',
            'description': 'Additional quality content',
            'content': 'This is new quality content from uploaded files.',
            'source': ['quality_manual.txt'],
            'content_types': []
        }
    ]
    
    result = update_pathway_section(target_info, new_content_modules, {}, {})
    print(f"Current pathway section update test: {result}")
    assert "✅" in result, "Should successfully update current pathway section"
    
    # Test updating past pathway section
    target_info = {
        'type': 'pathway_section',
        'pathway_num': 2,
        'section_num': 1,
        'identifier': 'pathway_2_section_1'
    }
    
    result = update_pathway_section(target_info, new_content_modules, {}, {})
    print(f"Past pathway section update test: {result}")
    assert "✅" in result, "Should successfully update past pathway section"
    
    # Test error handling for non-existent pathway
    target_info = {
        'type': 'pathway_section',
        'pathway_num': 5,
        'section_num': 1,
        'identifier': 'pathway_5_section_1'
    }
    
    result = update_pathway_section(target_info, new_content_modules, {}, {})
    print(f"Non-existent pathway test: {result}")
    assert "❌" in result and "not found" in result, "Should provide helpful error message"
    
    # Test error handling for non-existent section
    target_info = {
        'type': 'pathway_section',
        'pathway_num': 1,
        'section_num': 10,
        'identifier': 'pathway_1_section_10'
    }
    
    result = update_pathway_section(target_info, new_content_modules, {}, {})
    print(f"Non-existent section test: {result}")
    assert "❌" in result and "not found" in result, "Should provide helpful error message"
    
    print("✅ All pathway section improvement tests passed!")

if __name__ == "__main__":
    test_pathway_section_improvements() 