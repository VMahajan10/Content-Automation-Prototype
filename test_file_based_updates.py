#!/usr/bin/env python3
"""
Test file for file-based module updates
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_file_based_updates():
    """Test the new file-based update functionality"""
    
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
    Safety Procedures for Bridge Fabrication
    
    1. Personal Protective Equipment (PPE)
    - Hard hat must be worn at all times
    - Safety glasses for eye protection
    - Steel-toed boots required
    - High-visibility vest mandatory
    
    2. Equipment Safety
    - Inspect all tools before use
    - Follow lockout/tagout procedures
    - Maintain proper tool condition
    - Report damaged equipment immediately
    
    3. Workspace Safety
    - Keep work area clean and organized
    - Proper lighting for all work areas
    - Clear access paths maintained
    - Emergency exits clearly marked
    """
    
    mock_file = MockUploadedFile("safety_manual.txt", test_content)
    
    # Test the extract_target_from_input function
    from app import extract_target_from_input
    
    # Test module extraction
    result = extract_target_from_input("Update module 2 with new file")
    print(f"Module extraction test: {result}")
    assert result and result['type'] == 'module' and result['identifier'] == 'module_2'
    
    # Test section extraction
    result = extract_target_from_input("Add content to safety section")
    print(f"Section extraction test: {result}")
    assert result and result['type'] == 'section' and result['identifier'] == 'safety'
    
    # Test pathway extraction
    result = extract_target_from_input("Update pathway with new information")
    print(f"Pathway extraction test: {result}")
    assert result and result['type'] == 'pathway' and result['identifier'] == 'entire'
    
    print("✅ All file-based update tests passed!")

if __name__ == "__main__":
    test_file_based_updates() 