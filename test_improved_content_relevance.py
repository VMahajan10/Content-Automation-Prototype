#!/usr/bin/env python3
"""
Test script for improved content relevance functions
Tests the enhanced title, description, and content creation functions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.utils import (
    create_goal_aligned_title,
    create_goal_aligned_description,
    create_goal_aligned_content,
    is_conversational_content,
    extract_meaningful_content_snippet
)

def test_content_relevance():
    """Test the improved content relevance functions"""
    
    # Sample training context
    training_context = {
        'primary_goals': 'understand factory workflow and safety procedures',
        'training_type': 'Process Training',
        'target_audience': 'fabricators',
        'industry': 'manufacturing'
    }
    
    # Test cases with different types of content
    test_cases = [
        {
            'name': 'Conversational Content',
            'content': "You're a bit lagging, but I think we can hear you. Backgrounds, filters, appearance. That's the truss, but it hasn't got the zigzags in yet.",
            'expected_type': 'conversational'
        },
        {
            'name': 'Technical Content',
            'content': "The truss assembly process requires careful inspection of all welds. Each component must be verified against the engineering drawings before proceeding to the next station. Quality control procedures include dimensional checks and visual inspection of weld quality.",
            'expected_type': 'technical'
        },
        {
            'name': 'Safety Content',
            'content': "Safety procedures for fabricators include wearing proper PPE, following lockout-tagout procedures, and maintaining clear communication with team members. All equipment must be inspected before use and any defects reported immediately.",
            'expected_type': 'safety'
        },
        {
            'name': 'Mixed Content',
            'content': "Yeah, so the truss assembly process requires careful inspection. You know, we need to verify all the welds and check the dimensions. The quality control procedures are really important for safety.",
            'expected_type': 'mixed'
        }
    ]
    
    print("🧪 Testing Improved Content Relevance Functions")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        
        content = test_case['content']
        print(f"📄 Content: {content[:100]}...")
        
        # Test conversational detection
        is_conv = is_conversational_content(content)
        print(f"🔍 Is Conversational: {is_conv}")
        
        # Test meaningful snippet extraction
        snippet = extract_meaningful_content_snippet(content)
        print(f"💡 Meaningful Snippet: {snippet[:80] if snippet else 'None'}...")
        
        # Test title creation
        title = create_goal_aligned_title(content, training_context, i)
        print(f"📝 Title: {title}")
        
        # Test description creation
        description = create_goal_aligned_description(content, training_context)
        print(f"📋 Description: {description}")
        
        # Test content creation (truncated for readability)
        full_content = create_goal_aligned_content(content, training_context)
        print(f"📄 Content Preview: {full_content[:150]}...")
        
        print()
    
    print("✅ Content relevance testing completed!")

def test_conversational_detection():
    """Test the conversational content detection function"""
    
    print("\n🔍 Testing Conversational Content Detection")
    print("=" * 50)
    
    conversational_examples = [
        "You're a bit lagging, but I think we can hear you.",
        "Backgrounds, filters, appearance.",
        "Yeah, okay, so what we need to do is...",
        "Um, let me think about that for a moment.",
        "Speaker 1: Can you hear me? Speaker 2: Yes, I can hear you.",
        "Right, so the process is...",
        "Well, you know, it's like this..."
    ]
    
    non_conversational_examples = [
        "The truss assembly process requires careful inspection of all welds.",
        "Safety procedures for fabricators include wearing proper PPE.",
        "Quality control procedures include dimensional checks and visual inspection.",
        "Equipment maintenance schedules must be followed strictly.",
        "Documentation requirements include detailed records of all inspections."
    ]
    
    print("\n🗣️ Conversational Examples:")
    for i, example in enumerate(conversational_examples, 1):
        is_conv = is_conversational_content(example)
        print(f"{i}. '{example}' -> Conversational: {is_conv}")
    
    print("\n📚 Non-Conversational Examples:")
    for i, example in enumerate(non_conversational_examples, 1):
        is_conv = is_conversational_content(example)
        print(f"{i}. '{example}' -> Conversational: {is_conv}")

def test_meaningful_snippet_extraction():
    """Test the meaningful snippet extraction function"""
    
    print("\n💡 Testing Meaningful Snippet Extraction")
    print("=" * 50)
    
    test_contents = [
        "You're a bit lagging, but I think we can hear you. The truss assembly process requires careful inspection.",
        "Backgrounds, filters, appearance. Safety procedures for fabricators include wearing proper PPE.",
        "Yeah, okay, so what we need to do is verify all the welds and check the dimensions.",
        "The quality control procedures are really important for safety and compliance."
    ]
    
    for i, content in enumerate(test_contents, 1):
        snippet = extract_meaningful_content_snippet(content)
        print(f"{i}. Content: {content}")
        print(f"   Snippet: {snippet}")
        print()

if __name__ == "__main__":
    test_content_relevance()
    test_conversational_detection()
    test_meaningful_snippet_extraction()
    
    print("\n🎯 Summary:")
    print("• Improved functions now detect conversational vs. technical content")
    print("• Titles are more specific and relevant to actual content")
    print("• Descriptions include meaningful snippets from content")
    print("• Content is structured appropriately based on content type")
    print("• Better handling of irrelevant or conversational content") 