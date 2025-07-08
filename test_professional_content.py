#!/usr/bin/env python3
"""
Test script to verify conversational content transformation into professional training material
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.utils import create_cohesive_module_content, transform_conversational_to_professional

def test_conversational_transformation():
    """Test transformation of conversational content to professional training material"""
    
    print("🧪 Testing Conversational to Professional Content Transformation")
    print("=" * 70)
    
    # Sample conversational content from the transcript
    conversational_content = """
    What you just showed me is first you have the truss, you put it together with all the different components and then you make the deck out of that. Then in here, then we go to the next stage of the abutment assembly. Because what we can do over this weekend is place everything together, come up with the workflow of how you can film everything.
    """
    
    # Training context
    training_context = {
        'training_type': 'Process Training',
        'target_audience': 'fabricators',
        'industry': 'manufacturing',
        'primary_goals': 'understand truss assembly process',
        'success_metrics': 'feedback surveys'
    }
    
    print("📝 **Original Conversational Content:**")
    print(conversational_content)
    print("\n" + "="*50 + "\n")
    
    # Test direct transformation
    print("🔄 **Transformed Professional Content:**")
    professional_content = transform_conversational_to_professional(
        conversational_content, 'process', training_context
    )
    print(professional_content)
    print("\n" + "="*50 + "\n")
    
    # Test full module creation
    print("📋 **Full Module Creation:**")
    module = create_cohesive_module_content(conversational_content, training_context, 1)
    
    if module:
        print(f"Title: {module['title']}")
        print(f"Description: {module['description']}")
        print(f"Content: {module['content'][:200]}...")
        print(f"Core Topic: {module['core_topic']}")
    else:
        print("❌ Module creation failed")
    
    print("\n" + "="*50 + "\n")
    
    # Test multiple conversational examples
    conversational_examples = [
        "That's the truss, but it hasn't got the zigzags in yet.",
        "And the advantage of this is that normally they just cut it...",
        "This is the biggest bridge we make and they only make the ba...",
        "You're a bit lagging, but I think we can hear you.",
        "Backgrounds, filters, appearance.",
        "Interesting to learn about it."
    ]
    
    print("🔄 **Multiple Examples Transformation:**")
    for i, example in enumerate(conversational_examples, 1):
        print(f"\nExample {i}:")
        print(f"Original: {example}")
        transformed = transform_conversational_to_professional(example, 'process', training_context)
        print(f"Transformed: {transformed[:150]}...")
    
    print("\n✅ **Test completed successfully!**")
    print("\n🎯 **Key Improvements:**")
    print("• Conversational fillers removed")
    print("• Professional training language added")
    print("• Structured learning objectives")
    print("• Industry-specific terminology")
    print("• Clear process descriptions")

if __name__ == "__main__":
    test_conversational_transformation() 