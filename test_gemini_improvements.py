#!/usr/bin/env python3
"""
Test script to verify Gemini API improvements for conversational content transformation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.utils import (
    transform_conversational_to_professional,
    ai_enhanced_content_cleaning,
    apply_comprehensive_transformation,
    create_cohesive_module_content_optimized,
    detect_content_type
)

def test_gemini_improvements():
    """Test that Gemini API improvements work correctly"""
    
    print("🚀 Testing Gemini API Improvements")
    print("=" * 50)
    
    # Sample conversational content
    conversational_content = """
    Teams Meeting
    Mon, Dec 9, 2024
    0:00 - Mike Wright
    in too Bruce, all good?
    0:02 - Bruce Mullaney
    Yeah, thank you. I've got to stop and use the restroom in about five minutes. There was a car accident...
    0:05 - Mike Wright
    Oh no, are you okay?
    0:07 - Bruce Mullaney
    Yeah, I'm fine. Just traffic. So about the bridge fabrication process, we need to make sure we follow the safety protocols.
    0:10 - Mike Wright
    Right, absolutely. The welding procedures are critical for structural integrity.
    0:12 - Bruce Mullaney
    Exactly. And we need to check the quality control standards before moving to the next phase.
    """
    
    # Sample training context
    training_context = {
        'training_type': 'Process Training',
        'target_audience': 'fabricators',
        'industry': 'manufacturing',
        'primary_goals': 'understand how to fabricate bridges safely',
        'success_metrics': 'feedback surveys'
    }
    
    print("📝 **Test 1: Content Type Detection**")
    content_type = detect_content_type(conversational_content)
    print(f"   Detected type: {content_type}")
    
    print("\n📝 **Test 2: Conversational to Professional Transformation**")
    try:
        professional_content = transform_conversational_to_professional(
            conversational_content, 'safety', training_context
        )
        if professional_content:
            print(f"✅ Transformation successful")
            print(f"   Original length: {len(conversational_content)}")
            print(f"   Transformed length: {len(professional_content)}")
            print(f"   Preview: {professional_content[:200]}...")
        else:
            print("⚠️ Transformation failed")
    except Exception as e:
        print(f"❌ Transformation error: {str(e)}")
    
    print("\n📝 **Test 3: AI-Enhanced Content Cleaning**")
    try:
        cleaned_content = ai_enhanced_content_cleaning(conversational_content, training_context)
        if cleaned_content:
            print(f"✅ Cleaning successful")
            print(f"   Original length: {len(conversational_content)}")
            print(f"   Cleaned length: {len(cleaned_content)}")
            print(f"   Preview: {cleaned_content[:200]}...")
        else:
            print("⚠️ Cleaning failed")
    except Exception as e:
        print(f"❌ Cleaning error: {str(e)}")
    
    print("\n📝 **Test 4: Comprehensive Transformation**")
    try:
        transformed_content = apply_comprehensive_transformation(conversational_content, training_context)
        if transformed_content:
            print(f"✅ Comprehensive transformation successful")
            print(f"   Original length: {len(conversational_content)}")
            print(f"   Transformed length: {len(transformed_content)}")
            print(f"   Preview: {transformed_content[:200]}...")
        else:
            print("⚠️ Comprehensive transformation failed")
    except Exception as e:
        print(f"❌ Comprehensive transformation error: {str(e)}")
    
    print("\n📝 **Test 5: Module Creation**")
    try:
        module = create_cohesive_module_content_optimized(
            conversational_content, training_context, 1
        )
        if module:
            print(f"✅ Module creation successful")
            print(f"   Title: {module.get('title', 'No title')}")
            print(f"   Description: {module.get('description', 'No description')}")
            print(f"   Content length: {len(module.get('content', ''))}")
        else:
            print("⚠️ Module creation failed")
    except Exception as e:
        print(f"❌ Module creation error: {str(e)}")
    
    print("\n✅ Gemini API improvements test completed!")

if __name__ == "__main__":
    test_gemini_improvements() 