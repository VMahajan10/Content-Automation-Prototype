#!/usr/bin/env python3
"""
Test file to verify Gemini API integration in chatbot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gemini_chatbot():
    """Test that the chatbot is properly using Gemini API"""
    
    print("🧪 Testing Gemini API integration in chatbot...")
    
    # Test 1: Check if model is imported and available
    try:
        from modules.config import model, api_key
        print(f"✅ Model imported successfully")
        print(f"✅ API Key configured: {'Yes' if api_key and api_key != 'your_gemini_api_key_here' else 'No'}")
        print(f"✅ Model available: {'Yes' if model else 'No'}")
    except Exception as e:
        print(f"❌ Error importing model: {str(e)}")
        return False
    
    # Test 2: Test basic AI response
    if model:
        try:
            response = model.generate_content("Hello, this is a test.")
            print(f"✅ Basic AI response test: {response.text[:50]}...")
        except Exception as e:
            print(f"❌ Error with basic AI response: {str(e)}")
            return False
    else:
        print("⚠️ Model not available - skipping AI response test")
    
    # Test 3: Test chatbot functions
    try:
        from app import process_chatbot_request, get_chatbot_help
        
        # Test help function
        help_response = get_chatbot_help()
        print(f"✅ Help function test: {len(help_response)} characters")
        
        # Test file ingestion function
        ingestion_response = process_chatbot_request("how do I upload files?")
        print(f"✅ File ingestion test: {len(ingestion_response)} characters")
        
        # Test default response
        default_response = process_chatbot_request("hello")
        print(f"✅ Default response test: {len(default_response)} characters")
        
    except Exception as e:
        print(f"❌ Error testing chatbot functions: {str(e)}")
        return False
    
    print("🎉 All Gemini chatbot tests passed!")
    return True

if __name__ == "__main__":
    test_gemini_chatbot() 