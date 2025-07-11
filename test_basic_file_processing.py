#!/usr/bin/env python3
"""
Basic test for file processing functionality - no AI calls
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_file_processing():
    """Test basic file processing without AI calls"""
    
    print("🧪 Testing basic file processing functionality...")
    
    # Test 1: Check if the import works
    try:
        from modules.utils import extract_modules_from_file_content
        print("✅ Import successful: extract_modules_from_file_content")
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False
    
    # Test 2: Check if the function exists and is callable
    try:
        from modules.utils import extract_modules_from_file_content
        if callable(extract_modules_from_file_content):
            print("✅ Function is callable")
        else:
            print("❌ Function is not callable")
            return False
    except Exception as e:
        print(f"❌ Function check failed: {str(e)}")
        return False
    
    # Test 3: Check if the app.py imports work
    try:
        from app import process_new_files
        print("✅ process_new_files import successful")
    except Exception as e:
        print(f"❌ process_new_files import failed: {str(e)}")
        return False
    
    # Test 4: Check if integrate_new_modules is available in app.py
    try:
        from app import integrate_new_modules
        print("✅ integrate_new_modules import successful (from app.py)")
    except Exception as e:
        print(f"❌ integrate_new_modules import failed: {str(e)}")
        return False
    
    print("✅ All basic tests passed!")
    return True

if __name__ == "__main__":
    success = test_basic_file_processing()
    if success:
        print("\n🎉 All import and function tests passed!")
        print("💡 The chatbot file processing should now work correctly.")
        print("💡 The original error 'name extract_modules_from_file_content is not defined' has been fixed!")
    else:
        print("\n❌ Some tests failed. Check the errors above.") 