#!/usr/bin/env python3
"""
Test script for AI-powered conversational pattern filtering
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the modules directory to the path
sys.path.append('modules')

from modules.utils import (
    ai_filter_conversational_patterns,
    ai_identify_conversational_elements,
    ai_enhanced_content_cleaning,
    ai_content_quality_assessment,
    ai_extract_process_elements,
    ai_extract_process_steps,
    ai_extract_meaningful_content,
    ai_extract_learning_objectives
)

def test_ai_filtering():
    """Test the AI-powered conversational pattern filtering"""
    
    # Sample conversational content
    conversational_content = """
    Um, so yeah, I think we can hear you now. Okay, so what we're going to do today is, 
    you know, talk about the truss assembly process. Right? So, um, if you go to the 
    fabrication area, you'll see that, uh, that's the truss, but it hasn't got the 
    zigzags in yet. And what they do is they make, you know, these components. 
    This is the biggest bridge we make, and the advantage of this is that, um, 
    it's really strong. Can you hear me? Is that working? You're a bit lagging. 
    Anyway, so yeah, that's basically it. Thanks for listening, bye!
    """
    
    training_context = {
        'training_type': 'Process Training',
        'target_audience': 'fabricators',
        'industry': 'manufacturing',
        'primary_goals': 'Understand truss assembly procedures'
    }
    
    print("🧪 Testing AI-Powered Conversational Pattern Filtering")
    print("=" * 60)
    
    print("\n📝 Original Conversational Content:")
    print("-" * 40)
    print(conversational_content)
    
    print("\n🔍 Step 1: Identifying Conversational Elements")
    print("-" * 40)
    try:
        conversational_elements = ai_identify_conversational_elements(conversational_content)
        print(f"Identified {len(conversational_elements)} conversational elements:")
        for element in conversational_elements:
            print(f"  - '{element}'")
    except Exception as e:
        print(f"Error identifying elements: {e}")
    
    print("\n🧹 Step 2: AI-Enhanced Content Cleaning")
    print("-" * 40)
    try:
        cleaned_content = ai_enhanced_content_cleaning(conversational_content, training_context)
        print("Cleaned content:")
        print(cleaned_content)
    except Exception as e:
        print(f"Error cleaning content: {e}")
    
    print("\n📊 Step 3: Content Quality Assessment")
    print("-" * 40)
    try:
        assessment = ai_content_quality_assessment(conversational_content)
        print("Quality Assessment:")
        for key, value in assessment.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error assessing quality: {e}")
    
    print("\n✨ Step 4: Direct AI Filtering")
    print("-" * 40)
    try:
        filtered_content = ai_filter_conversational_patterns(conversational_content, training_context)
        print("AI-filtered content:")
        print(filtered_content)
    except Exception as e:
        print(f"Error filtering content: {e}")
    
    print("\n" + "=" * 60)
    print("✅ AI-Powered Filtering Test Complete!")
    
    print("\n🔧 Testing AI-Powered Process Extraction (Industry-Agnostic)")
    print("=" * 60)
    
    # Generic test content that could be from any industry
    generic_content = """
    The process involves several key steps. First, we begin with initial preparation 
    and setup. Then we proceed with the main execution phase where we carefully 
    follow established procedures. The verification phase follows, where we conduct 
    thorough testing and quality checks. Finally, we complete the process and 
    document all results. The workflow includes proper documentation and safety 
    protocols throughout.
    """
    
    print("\n📝 Generic Content (Any Industry):")
    print(generic_content)
    
    print("\n🔍 AI Process Elements Extraction:")
    print("-" * 40)
    try:
        process_elements = ai_extract_process_elements(generic_content, training_context)
        print(f"Identified {len(process_elements)} process elements:")
        for element in process_elements:
            print(f"  - {element}")
    except Exception as e:
        print(f"Error extracting process elements: {e}")
    
    print("\n📋 AI Process Steps Extraction:")
    print("-" * 40)
    try:
        process_steps = ai_extract_process_steps(generic_content, training_context)
        print("Extracted process steps:")
        for step_type, step_description in process_steps.items():
            print(f"  {step_type}: {step_description}")
    except Exception as e:
        print(f"Error extracting process steps: {e}")
    
    print("\n📖 AI Meaningful Content Extraction:")
    print("-" * 40)
    try:
        meaningful_content = ai_extract_meaningful_content(generic_content, training_context)
        print("Most meaningful content:")
        print(meaningful_content)
    except Exception as e:
        print(f"Error extracting meaningful content: {e}")
    
    print("\n🎯 AI Learning Objectives Extraction:")
    print("-" * 40)
    try:
        learning_objectives = ai_extract_learning_objectives(generic_content, training_context)
        print(f"Extracted {len(learning_objectives)} learning objectives:")
        for i, objective in enumerate(learning_objectives, 1):
            print(f"  {i}. {objective}")
    except Exception as e:
        print(f"Error extracting learning objectives: {e}")
    
    print("\n" + "=" * 60)
    print("✅ AI-Powered Process Extraction Test Complete!")
    print("💡 The AI functions work with any industry content without assumptions!")

def test_comparison():
    """Compare AI filtering with traditional regex filtering"""
    
    print("\n🔄 Comparison: AI vs Traditional Regex Filtering")
    print("=" * 60)
    
    # Test content with various conversational patterns
    test_content = """
    Um, hello everyone! So yeah, today we're going to talk about, you know, 
    the welding process. Right? So if you go to the workshop, um, you'll see 
    that we have these, uh, welding machines. And what they do is they make, 
    you know, really strong joints. Can you hear me? Is that working? 
    You're a bit lagging. Anyway, so yeah, that's basically how it works. 
    Thanks for listening, bye!
    """
    
    print("\n📝 Test Content:")
    print(test_content)
    
    # Traditional regex approach (simplified)
    import re
    traditional_patterns = [
        r'\b(um|uh|oh|yeah|okay|right|so|well|you know)\b',
        r'\b(hello|goodbye|thank you|thanks|bye)\b',
        r'\b(can you hear me|is that working|you\'re a bit lagging)\b'
    ]
    
    traditional_cleaned = test_content
    for pattern in traditional_patterns:
        traditional_cleaned = re.sub(pattern, '', traditional_cleaned, flags=re.IGNORECASE)
    
    print("\n🔧 Traditional Regex Cleaning:")
    print(traditional_cleaned)
    
    # AI approach
    training_context = {'training_type': 'Welding Training', 'target_audience': 'welders', 'industry': 'manufacturing'}
    
    try:
        ai_cleaned = ai_filter_conversational_patterns(test_content, training_context)
        print("\n🤖 AI-Powered Cleaning:")
        print(ai_cleaned)
        
        print(f"\n📊 Comparison Results:")
        print(f"Original length: {len(test_content)} characters")
        print(f"Traditional cleaned: {len(traditional_cleaned)} characters")
        print(f"AI cleaned: {len(ai_cleaned)} characters")
        print(f"Traditional removed: {len(test_content) - len(traditional_cleaned)} characters")
        print(f"AI removed: {len(test_content) - len(ai_cleaned)} characters")
        
    except Exception as e:
        print(f"AI cleaning failed: {e}")

if __name__ == "__main__":
    # Check if API key is available
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == "your_gemini_api_key_here":
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("💡 Please set your Gemini API key in the .env file")
        sys.exit(1)
    
    # Run tests
    test_ai_filtering()
    test_comparison() 