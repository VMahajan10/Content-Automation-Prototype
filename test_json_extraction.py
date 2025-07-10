#!/usr/bin/env python3
"""
Test script to verify improved JSON extraction for meeting transcripts
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock streamlit for testing
class MockStreamlit:
    def info(self, msg):
        print(f"INFO: {msg}")
    def error(self, msg):
        print(f"ERROR: {msg}")

# Mock the streamlit module
sys.modules['streamlit'] = MockStreamlit()

from modules.utils import extract_json_from_ai_response

def test_json_extraction():
    """Test the improved JSON extraction function"""
    
    # Test cases for different AI response formats
    test_cases = [
        {
            "name": "Valid JSON Array",
            "input": '[{"title": "Safety Procedures", "description": "PPE requirements", "content": "Training content"}]',
            "expected": "list"
        },
        {
            "name": "JSON with Markdown",
            "input": '```json\n[{"title": "Quality Control", "description": "Inspection procedures", "content": "Training content"}]\n```',
            "expected": "list"
        },
        {
            "name": "Structured Text Response",
            "input": 'Title: Safety Procedures\nDescription: PPE requirements\nContent: Training content\n\nTitle: Quality Control\nDescription: Inspection procedures\nContent: Training content',
            "expected": "list"
        },
        {
            "name": "Invalid JSON with Text",
            "input": 'I cannot extract training modules from this content as it does not align with the training goals.',
            "expected": "None"
        },
        {
            "name": "Empty Response",
            "input": '',
            "expected": "None"
        }
    ]
    
    print("🧪 Testing improved JSON extraction...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"📄 Input: {test_case['input'][:100]}...")
        
        result = extract_json_from_ai_response(test_case['input'])
        
        if result is None:
            print(f"✅ Result: None (as expected)")
        elif isinstance(result, list):
            print(f"✅ Result: List with {len(result)} items")
            for j, item in enumerate(result):
                print(f"   Item {j+1}: {item}")
        else:
            print(f"✅ Result: {type(result).__name__} - {result}")
        
        # Check if result matches expected type
        if test_case['expected'] == "None" and result is None:
            print(f"✅ Test {i} PASSED")
        elif test_case['expected'] == "list" and isinstance(result, list):
            print(f"✅ Test {i} PASSED")
        else:
            print(f"❌ Test {i} FAILED - Expected {test_case['expected']}, got {type(result).__name__}")
    
    print(f"\n🎯 JSON extraction test completed!")

if __name__ == "__main__":
    test_json_extraction() 