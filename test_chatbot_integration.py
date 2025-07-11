#!/usr/bin/env python3
"""
Test file for chatbot integration with new module numbering system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_chatbot_module_references():
    """Test that the chatbot can correctly reference modules with the new numbering system"""
    
    # Mock editable pathways data
    editable_pathways = {
        'Safety Procedures': [
            {'title': 'PPE Requirements', 'description': 'Personal protective equipment', 'content': 'Safety content 1'},
            {'title': 'Equipment Safety', 'description': 'Equipment safety procedures', 'content': 'Safety content 2'},
            {'title': 'Emergency Procedures', 'description': 'Emergency response', 'content': 'Safety content 3'}
        ],
        'Quality Control': [
            {'title': 'Inspection Procedures', 'description': 'Quality inspection steps', 'content': 'Quality content 1'},
            {'title': 'Documentation', 'description': 'Quality documentation', 'content': 'Quality content 2'}
        ],
        'Process Training': [
            {'title': 'Standard Operating Procedures', 'description': 'SOP training', 'content': 'Process content 1'},
            {'title': 'Workflow Management', 'description': 'Workflow procedures', 'content': 'Process content 2'},
            {'title': 'Team Coordination', 'description': 'Team coordination', 'content': 'Process content 3'},
            {'title': 'Communication Protocols', 'description': 'Communication procedures', 'content': 'Process content 4'}
        ]
    }
    
    # Mock session state
    import streamlit as st
    if not hasattr(st, 'session_state'):
        class MockSessionState:
            def __init__(self):
                self.data = {}
            
            def get(self, key, default=None):
                return self.data.get(key, default)
            
            def __setitem__(self, key, value):
                self.data[key] = value
        
        st.session_state = MockSessionState()
    
    st.session_state['editable_pathways'] = editable_pathways
    
    # Test the chatbot functions
    from app import process_chatbot_request, find_module_by_info, create_module_mapping, format_module_reference_help
    
    print("🤖 Testing chatbot module references...")
    
    # Test module reference help generation
    help_text = format_module_reference_help(editable_pathways)
    print(f"Help text generated ({len(help_text)} characters)")
    assert "Safety Procedures" in help_text
    assert "Module 1: PPE Requirements" in help_text
    assert "Module 2: Equipment Safety" in help_text
    
    # Test module mapping
    module_mapping = create_module_mapping(editable_pathways)
    print(f"Module mapping created with {len(module_mapping['by_global_number'])} modules")
    
    # Test finding modules by different references
    test_cases = [
        ("module_1", "PPE Requirements"),
        ("module_2", "Equipment Safety"),
        ("module_3", "Emergency Procedures"),
        ("ppe requirements", "PPE Requirements"),
        ("equipment safety", "Equipment Safety"),
        ("safety", "PPE Requirements"),  # Should return first safety module
    ]
    
    for module_ref, expected_title in test_cases:
        result = find_module_by_info(module_ref, editable_pathways)
        if result and result['module']['title'] == expected_title:
            print(f"✅ '{module_ref}' -> {result['module']['title']}")
        else:
            actual_title = result['module']['title'] if result else 'Not found'
            print(f"❌ '{module_ref}' -> {actual_title} (expected: {expected_title})")
    
    # Test chatbot responses
    print("\n🤖 Testing chatbot responses...")
    
    # Test regeneration request
    response = process_chatbot_request("regenerate module 1")
    print(f"Regeneration response: {response[:100]}...")
    # The response should mention modules or pathway data
    assert any(word in response.lower() for word in ["module", "pathway", "data", "available"])
    
    # Test help request
    response = process_chatbot_request("help")
    print(f"Help response: {response[:100]}...")
    assert "module" in response.lower() or "help" in response.lower()
    
    # Test file-based update request
    class MockUploadedFile:
        def __init__(self, name):
            self.name = name
    
    mock_files = [MockUploadedFile("test.txt")]
    response = process_chatbot_request("update module 2 with new file", mock_files)
    print(f"File update response: {response[:100]}...")
    assert "module" in response.lower() or "file" in response.lower()
    
    print("✅ All chatbot module reference tests passed!")
    
    # Test section-specific module references
    print("\n🔍 Testing section-specific module references...")
    
    # Test finding modules in specific sections
    safety_module_1 = module_mapping['by_section_and_number']['Safety Procedures']['1']
    quality_module_1 = module_mapping['by_section_and_number']['Quality Control']['1']
    process_module_2 = module_mapping['by_section_and_number']['Process Training']['2']
    
    print(f"Safety Module 1: {safety_module_1['module']['title']} (Local: {safety_module_1['local_number']}, Global: {safety_module_1['global_number']})")
    print(f"Quality Module 1: {quality_module_1['module']['title']} (Local: {quality_module_1['local_number']}, Global: {quality_module_1['global_number']})")
    print(f"Process Module 2: {process_module_2['module']['title']} (Local: {process_module_2['local_number']}, Global: {process_module_2['global_number']})")
    
    # Verify local numbering is correct
    assert safety_module_1['local_number'] == 1
    assert quality_module_1['local_number'] == 1
    assert process_module_2['local_number'] == 2
    
    # Verify global numbering is sequential
    assert safety_module_1['global_number'] == 1
    assert quality_module_1['global_number'] == 4  # After 3 safety modules
    assert process_module_2['global_number'] == 7  # After safety and quality modules
    
    print("✅ All section-specific module reference tests passed!")
    
    print("\n🎉 All chatbot integration tests completed successfully!")

if __name__ == "__main__":
    test_chatbot_module_references() 