#!/usr/bin/env python3
"""
Test script to verify AI-powered conversational content transformation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.utils import transform_conversational_to_professional

def test_ai_transformation():
    """Test AI-powered transformation of conversational content"""
    
    print("🧪 Testing AI-Powered Conversational Content Transformation")
    print("=" * 70)
    
    # Sample conversational content from the transcript
    conversational_content = """
    While they've got these decks and things in there, then you can go in there and you can have a look and you can actually eyeball it. the steel to our specification and deliver it, and then we put it together. normally they just cut it off, like through here, on the front, but then the concrete will fall out.
    """
    
    # Training context
    training_context = {
        'training_type': 'Process Training',
        'target_audience': 'fabricators',
        'industry': 'manufacturing',
        'primary_goals': 'understand quality control in fabrication',
        'success_metrics': 'quiz scores'
    }
    
    print("📝 **Original Conversational Content:**")
    print(conversational_content)
    print("\n" + "="*50 + "\n")
    
    # Test AI transformation
    print("🤖 **AI-Powered Professional Transformation:**")
    try:
        professional_content = transform_conversational_to_professional(
            conversational_content, 'quality', training_context
        )
        print(professional_content)
    except Exception as e:
        print(f"❌ AI transformation failed: {str(e)}")
        print("💡 This might be due to:")
        print("• API rate limits")
        print("• Network connectivity issues")
        print("• Invalid API key")
    
    print("\n" + "="*50 + "\n")
    
    # Test multiple examples
    conversational_examples = [
        "What you just showed me is first you have the truss, you put it together with all the different components and then you make the deck out of that.",
        "That's the truss, but it hasn't got the zigzags in yet.",
        "And the advantage of this is that normally they just cut it off, like through here, on the front, but then the concrete will fall out.",
        "You can go in there and you can have a look and you can actually eyeball it."
    ]
    
    print("🔄 **Multiple Examples AI Transformation:**")
    for i, example in enumerate(conversational_examples, 1):
        print(f"\nExample {i}:")
        print(f"Original: {example}")
        try:
            transformed = transform_conversational_to_professional(example, 'process', training_context)
            print(f"AI Transformed: {transformed[:200]}...")
        except Exception as e:
            print(f"❌ Transformation failed: {str(e)}")
    
    print("\n✅ **Test completed!**")
    print("\n🎯 **Expected Improvements:**")
    print("• Professional 'Module Overview' sections")
    print("• Clear instructional language")
    print("• Learning objectives included")
    print("• Technical information preserved")
    print("• Engaging and educational content")

if __name__ == "__main__":
    test_ai_transformation() 