#!/usr/bin/env python3
"""
Test script for goal-aligned content extraction
Demonstrates how the system now extracts training-relevant information
that directly aligns with user's training goals
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock streamlit for testing
class MockStreamlit:
    def write(self, text):
        print(f"DEBUG: {text}")
    
    def warning(self, text):
        print(f"WARNING: {text}")

# Replace streamlit with mock
import modules.utils
modules.utils.st = MockStreamlit()

from modules.utils import extract_modules_from_file_content_fallback
from modules.config import *

def test_goal_aligned_extraction():
    """Test the improved goal-aligned content extraction"""
    
    print("🎯 **Testing Goal-Aligned Content Extraction**")
    print("=" * 60)
    
    # Sample training context with specific goals
    training_context = {
        'primary_goals': 'understand factory workflow and safety procedures',
        'success_metrics': 'feedback surveys and safety compliance',
        'training_type': 'Process Training',
        'target_audience': 'fabricators',
        'industry': 'construction'
    }
    
    print(f"🎯 **Training Goals:** {training_context['primary_goals']}")
    print(f"📊 **Success Metrics:** {training_context['success_metrics']}")
    print(f"📋 **Training Type:** {training_context['training_type']}")
    print(f"👥 **Target Audience:** {training_context['target_audience']}")
    print(f"🏢 **Industry:** {training_context['industry']}")
    print()
    
    # Sample content with training-relevant information mixed with conversation
    sample_content = """
    Bruce: Yeah, so the safety procedures for handling steel materials are critical.
    Sarah: Right, what are the key steps?
    Bruce: First, you need to inspect the material for any damage or defects before handling.
    Sarah: Okay, and then what?
    Bruce: Then you use the proper lifting equipment and PPE - hard hat, safety glasses, steel-toed boots.
    Sarah: Got it. What about the workflow process?
    Bruce: The workflow starts with receiving the steel shipment and verifying it against the bill of lading.
    Sarah: And then?
    Bruce: Then you stage the materials in the designated area and begin the fabrication process.
    Sarah: What about quality control?
    Bruce: Quality control happens at multiple checkpoints - during material inspection, after cutting, and before final assembly.
    Sarah: That makes sense. Any other procedures?
    Bruce: Yes, documentation is important. You need to record all measurements, inspections, and any issues that arise.
    Sarah: Thanks for explaining that.
    Bruce: No problem. Safety first, always.
    """
    
    print("📄 **Sample Content (with training info mixed with conversation):**")
    print(sample_content)
    print()
    
    # Test the goal-aligned extraction
    print("🔍 **Extracting Goal-Aligned Training Information...**")
    modules = extract_modules_from_file_content_fallback(
        "sample_training.txt", 
        sample_content, 
        training_context
    )
    
    print(f"\n✅ **Results: {len(modules)} training modules extracted**")
    print("=" * 60)
    
    for i, module in enumerate(modules, 1):
        print(f"\n📚 **Module {i}:**")
        print(f"📝 **Title:** {module['title']}")
        print(f"📋 **Description:** {module['description']}")
        print(f"📄 **Content Preview:** {module['content'][:200]}...")
        print(f"🎯 **Key Points:** {module.get('key_points', [])}")
        print(f"📊 **Relevance Score:** {module.get('relevance_score', 'N/A')}")
        print("-" * 40)

def test_different_training_goals():
    """Test with different training goals to show adaptability"""
    
    print("\n🎯 **Testing Different Training Goals**")
    print("=" * 60)
    
    # Test 1: Safety-focused training
    safety_context = {
        'primary_goals': 'learn safety procedures and emergency response',
        'success_metrics': 'safety compliance and incident reduction',
        'training_type': 'Safety Training',
        'target_audience': 'operators',
        'industry': 'manufacturing'
    }
    
    safety_content = """
    The safety procedures for equipment operation are essential. Always wear PPE including hard hat, safety glasses, and steel-toed boots.
    Before starting any equipment, perform a pre-operation inspection to check for damage or malfunctions.
    Emergency procedures must be followed immediately if any safety issues are detected.
    All incidents must be reported and documented according to company policy.
    """
    
    print(f"🎯 **Safety Training Goals:** {safety_context['primary_goals']}")
    safety_modules = extract_modules_from_file_content_fallback(
        "safety_training.txt", 
        safety_content, 
        safety_context
    )
    
    print(f"✅ **Safety Modules:** {len(safety_modules)} extracted")
    for i, module in enumerate(safety_modules, 1):
        print(f"   {i}. {module['title']}")
    
    # Test 2: Quality-focused training
    quality_context = {
        'primary_goals': 'understand quality control and inspection procedures',
        'success_metrics': 'quality metrics and defect reduction',
        'training_type': 'Quality Training',
        'target_audience': 'inspectors',
        'industry': 'manufacturing'
    }
    
    quality_content = """
    Quality control procedures require careful attention to detail. Inspect all materials for defects before processing.
    Use calibrated measuring equipment and follow standard inspection procedures.
    Document all inspection results and report any non-conforming materials.
    Quality standards must be maintained throughout the entire production process.
    """
    
    print(f"\n🎯 **Quality Training Goals:** {quality_context['primary_goals']}")
    quality_modules = extract_modules_from_file_content_fallback(
        "quality_training.txt", 
        quality_content, 
        quality_context
    )
    
    print(f"✅ **Quality Modules:** {len(quality_modules)} extracted")
    for i, module in enumerate(quality_modules, 1):
        print(f"   {i}. {module['title']}")

def test_conversation_filtering():
    """Test how the system filters out conversation and focuses on training content"""
    
    print("\n🎯 **Testing Conversation Filtering**")
    print("=" * 60)
    
    # Content with lots of conversation but some training info
    conversational_content = """
    Yeah, so um, you know, the process is like this.
    Right, okay, so what do we do first?
    Well, first you need to check the material quality and safety standards.
    Oh right, and then what?
    Then you follow the proper workflow procedures step by step.
    Got it, thanks.
    No problem, see you later.
    """
    
    training_context = {
        'primary_goals': 'learn process procedures and workflow',
        'success_metrics': 'process efficiency',
        'training_type': 'Process Training',
        'target_audience': 'workers',
        'industry': 'general'
    }
    
    print("📄 **Conversational Content (with minimal training info):**")
    print(conversational_content)
    print()
    
    modules = extract_modules_from_file_content_fallback(
        "conversational.txt", 
        conversational_content, 
        training_context
    )
    
    print(f"✅ **Filtered Results: {len(modules)} training modules extracted**")
    for i, module in enumerate(modules, 1):
        print(f"   {i}. {module['title']} - {module['description'][:100]}...")

if __name__ == "__main__":
    print("🚀 **Goal-Aligned Content Extraction Test**")
    print("This test demonstrates how the system now extracts training-relevant")
    print("information that directly aligns with user's training goals.")
    print()
    
    # Run tests
    test_goal_aligned_extraction()
    test_different_training_goals()
    test_conversation_filtering()
    
    print("\n✅ **Test Complete!**")
    print("The system now focuses on extracting training-relevant information")
    print("that directly supports the user's specific training goals.") 