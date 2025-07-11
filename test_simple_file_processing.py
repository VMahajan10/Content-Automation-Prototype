#!/usr/bin/env python3
"""
Simple test for file processing functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_extract_modules_function():
    """Test the extract_modules_from_file_content function directly"""
    
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
    
    # Mock training context
    training_context = {
        'primary_goals': 'Safety training for new employees',
        'training_type': 'Safety',
        'target_audience': 'New employees',
        'industry': 'Construction'
    }
    
    print("🧪 Testing extract_modules_from_file_content function...")
    print(f"📄 Content length: {len(test_content)} characters")
    print(f"🎯 Training context: {training_context}")
    
    try:
        # Import the function directly
        from modules.utils import extract_modules_from_file_content
        
        # Test the function
        modules = extract_modules_from_file_content("safety_manual.txt", test_content, training_context)
        
        print(f"✅ Function executed successfully!")
        print(f"📊 Number of modules extracted: {len(modules) if modules else 0}")
        
        if modules:
            print("📋 Extracted modules:")
            for i, module in enumerate(modules, 1):
                print(f"  {i}. {module.get('title', 'No title')}")
                print(f"     Description: {module.get('description', 'No description')[:100]}...")
                print(f"     Content length: {len(module.get('content', ''))} characters")
        else:
            print("⚠️ No modules were extracted")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing function: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_extract_modules_function()
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!") 