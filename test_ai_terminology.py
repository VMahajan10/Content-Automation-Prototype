#!/usr/bin/env python3
"""
Test script for AI-driven terminology extraction
Demonstrates how the new approach replaces hardcoded lists with dynamic AI analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.utils import extract_ai_driven_terminology, extract_basic_terminology
from modules.config import api_key

def test_ai_terminology_extraction():
    """Test the new AI-driven terminology extraction"""
    
    print("🧠 Testing AI-Driven Terminology Extraction")
    print("=" * 60)
    
    # Sample content for testing
    sample_content = """
    The truss assembly process involves several critical steps. First, fabricators must 
    verify the steel shipment against the bill of lading and inspect for any damage. 
    Material handling procedures require proper staging and storage of steel components. 
    During assembly, welders follow specific welding procedures and quality control 
    checkpoints. Safety protocols must be followed throughout, including proper PPE usage. 
    Equipment maintenance and calibration are essential for accurate fabrication. 
    Documentation requirements include recording all quality inspections and process steps.
    """
    
    # Sample training context
    training_context = {
        'primary_goals': 'understand truss assembly and steel fabrication processes',
        'training_type': 'Process Training',
        'target_audience': 'fabricators',
        'industry': 'manufacturing',
        'success_metrics': 'feedback surveys and quality assessments'
    }
    
    print(f"📄 Sample Content: {sample_content[:100]}...")
    print(f"🎯 Training Goals: {training_context['primary_goals']}")
    print(f"🏭 Industry: {training_context['industry']}")
    print()
    
    # Test different terminology types
    terminology_types = ["technical", "action", "industry", "all"]
    
    for term_type in terminology_types:
        print(f"🔍 Testing '{term_type}' terminology extraction:")
        
        try:
            # Test AI-driven extraction
            ai_terms = extract_ai_driven_terminology(sample_content, training_context, term_type)
            print(f"   🤖 AI-extracted terms ({len(ai_terms)}): {ai_terms}")
            
            # Test basic fallback extraction
            basic_terms = extract_basic_terminology(sample_content, training_context, term_type)
            print(f"   📝 Basic fallback terms ({len(basic_terms)}): {basic_terms}")
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        print()
    
    # Test with different content types
    print("🔄 Testing with different content types:")
    
    # Technical content
    technical_content = """
    The calibration process requires precise measurement using calibrated instruments.
    Verification procedures must be followed to ensure accuracy within ±0.001 inches.
    Quality control checkpoints are established at each stage of production.
    """
    
    print(f"🔧 Technical content: {technical_content[:80]}...")
    tech_terms = extract_ai_driven_terminology(technical_content, training_context, "technical")
    print(f"   Technical terms: {tech_terms}")
    print()
    
    # Action-oriented content
    action_content = """
    Inspect the material for defects before processing. Verify dimensions against 
    specifications. Assemble components according to the assembly diagram. 
    Document all measurements and observations in the quality log.
    """
    
    print(f"⚡ Action content: {action_content[:80]}...")
    action_terms = extract_ai_driven_terminology(action_content, training_context, "action")
    print(f"   Action terms: {action_terms}")
    print()
    
    # Industry-specific content
    industry_content = """
    Steel fabrication involves cutting, bending, and welding steel components.
    Truss assembly requires precise alignment and proper joint preparation.
    Beam construction follows structural engineering specifications.
    """
    
    print(f"🏭 Industry content: {industry_content[:80]}...")
    industry_terms = extract_ai_driven_terminology(industry_content, training_context, "industry")
    print(f"   Industry terms: {industry_terms}")
    print()
    
    # Test API key availability
    print("🔑 API Key Status:")
    if api_key and api_key != "your_gemini_api_key_here":
        print("   ✅ Gemini API key is configured")
        print("   🚀 AI-driven extraction will be used")
    else:
        print("   ⚠️ No Gemini API key found")
        print("   📝 Basic fallback extraction will be used")
    
    print()
    print("✅ AI-driven terminology extraction test completed!")
    print()
    print("💡 Benefits of this approach:")
    print("   • No more hardcoded lists to maintain")
    print("   • Context-aware terminology extraction")
    print("   • Adapts to any industry or domain")
    print("   • Graceful fallback when AI is unavailable")
    print("   • More relevant and specific terms")

if __name__ == "__main__":
    test_ai_terminology_extraction() 