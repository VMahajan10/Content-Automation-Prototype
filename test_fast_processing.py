#!/usr/bin/env python3
"""
Test file for fast processing optimization
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_fast_processing():
    """Test the fast processing optimization"""
    
    print("🧪 Testing fast processing optimization...")
    
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
    
    # Test the fast extraction function
    try:
        from app import extract_fast_modules_from_content
        
        training_context = {
            'primary_goals': 'Safety training for bridge fabrication',
            'training_type': 'Safety',
            'target_audience': 'Construction workers',
            'industry': 'Construction'
        }
        
        print("📞 Testing fast module extraction...")
        modules = extract_fast_modules_from_content(
            mock_file.name,
            test_content,
            training_context,
            'Safety training for bridge fabrication'
        )
        
        print(f"✅ Fast extraction completed: {len(modules)} modules extracted")
        for i, module in enumerate(modules):
            print(f"  Module {i+1}: {module.get('title', 'No title')}")
            print(f"    Content length: {len(module.get('content', ''))} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing fast processing: {str(e)}")
        return False

if __name__ == "__main__":
    test_fast_processing() 