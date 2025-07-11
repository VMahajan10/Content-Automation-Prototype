#!/usr/bin/env python3
"""
Test file for chatbot file processing functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_chatbot_file_processing():
    """Test the chatbot file processing functionality"""
    
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
    
    # Mock Streamlit session state
    class MockSessionState:
        def __init__(self):
            self._data = {
                'editable_pathways': {
                    'Safety Training': [
                        {
                            'title': 'Basic Safety',
                            'description': 'Introduction to safety procedures',
                            'content': 'Basic safety information',
                            'source': ['Existing content']
                        }
                    ]
                },
                'training_context': {
                    'primary_goals': 'Safety training for new employees',
                    'training_type': 'Safety'
                }
            }
        
        def __getitem__(self, key):
            return self._data[key]
        
        def __setitem__(self, key, value):
            self._data[key] = value
        
        def __contains__(self, key):
            return key in self._data
        
        def get(self, key, default=None):
            return self._data.get(key, default)
    
    # Mock Streamlit functions
    class MockStreamlit:
        def __init__(self):
            self.session_state = MockSessionState()
        
        def info(self, message):
            print(f"ℹ️ INFO: {message}")
        
        def error(self, message):
            print(f"❌ ERROR: {message}")
        
        def success(self, message):
            print(f"✅ SUCCESS: {message}")
    
    # Replace streamlit with our mock
    import sys
    sys.modules['streamlit'] = MockStreamlit()
    
    # Test the function
    from app import process_new_files
    
    print("🧪 Testing chatbot file processing...")
    print(f"📁 Mock file: {mock_file.name}")
    print(f"📄 Content length: {len(test_content)} characters")
    
    # Test the function
    result = process_new_files([mock_file])
    
    print(f"✅ File processing test completed!")
    print(f"Result: {result}")
    
    if result:
        print("✅ File processing successful!")
        print(f"Updated pathways: {sys.modules['streamlit'].session_state._data['editable_pathways']}")
    else:
        print("❌ File processing failed!")
        print("💡 Check the error messages above to see what went wrong")

if __name__ == "__main__":
    test_chatbot_file_processing() 