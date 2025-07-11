#!/usr/bin/env python3
"""
Test file for professional content cleaning functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_professional_content_cleaning():
    """Test the professional content cleaning functionality"""
    
    # Import the functions
    from modules.utils import clean_conversational_content, make_content_professional
    
    # Test conversational content
    conversational_content = """
    1:03:04 - Mike Wright
    If you just have a look at it today or tomorrow morning, Think your way through it.
    
    1:03:14 - MaiLinh Ho
    Just look straight into me tomorrow and we'll just sort them out So it's getting clear in your head happy to do that Perfect.
    
    So yeah, basically we need to um, you know, sort of work on this process and make sure everything is, like, you know, properly set up.
    """
    
    print("=== Testing Professional Content Cleaning ===")
    print(f"Original content:\n{conversational_content}")
    
    # Test conversational cleaning
    cleaned_content = clean_conversational_content(conversational_content)
    print(f"\nAfter conversational cleaning:\n{cleaned_content}")
    
    # Test professional transformation
    professional_content = make_content_professional(conversational_content)
    print(f"\nAfter professional transformation:\n{professional_content}")
    
    # Test with more casual language
    casual_content = """
    So we need to get this done, you know? Just check it out and make sure it's all good.
    We'll work on it tomorrow and figure out what needs to be done.
    Basically, we just need to set it up properly and handle any issues that come up.
    """
    
    print(f"\n=== Testing Casual Language Transformation ===")
    print(f"Original casual content:\n{casual_content}")
    
    professional_casual = make_content_professional(casual_content)
    print(f"\nAfter professional transformation:\n{professional_casual}")
    
    # Test with incomplete sentences
    incomplete_content = """
    We need to review the process and ensure proper implementation.
    So
    If you just
    """
    
    print(f"\n=== Testing Incomplete Sentence Cleaning ===")
    print(f"Original incomplete content:\n{incomplete_content}")
    
    cleaned_incomplete = make_content_professional(incomplete_content)
    print(f"\nAfter professional transformation:\n{cleaned_incomplete}")
    
    print("\n✅ Professional content cleaning tests completed!")

if __name__ == "__main__":
    test_professional_content_cleaning() 