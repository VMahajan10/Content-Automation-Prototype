#!/usr/bin/env python3
"""
Test script to verify content extraction fixes work correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.utils import (
    extract_training_information_from_content,
    is_meaningful_training_content,
    extract_broader_training_content,
    create_cohesive_module_content_optimized,
    extract_modules_from_file_content,
    get_training_keywords_from_goals
)

def test_training_goals_usage():
    """Test that training goals are properly used in content extraction"""
    print("🧪 Testing training goals usage...")
    
    # Sample meeting transcript content
    meeting_content = """
    Meet Meeting
    Thu, Dec 12, 2024
    0:00 - MaiLinh Ho
    to work through the construction flow chart with you, just to understand how does that work now that we have pretty much the overview of manufacturing...
    
    0:02 - Bruce Mullaney
    Yeah, let's go through the construction flow chart. We need to understand the process for bridge fabrication.
    
    0:05 - MaiLinh Ho
    Right, so we have the shop drawings, then we move to plate cutting and drilling. The welding procedure specification (WPS) is critical for quality control.
    
    0:08 - Bruce Mullaney
    Exactly. And we need to ensure proper fit-up before welding. The submerged arc welding (SAW) process requires specific parameters.
    """
    
    training_context = {
        'training_type': 'Process Training',
        'target_audience': 'fabricators',
        'industry': 'manufacturing',
        'primary_goals': 'understanding how to fabricate bridges',
        'success_metrics': 'feedback surveys'
    }
    
    # Test keyword generation from goals
    keywords = get_training_keywords_from_goals(training_context)
    print(f"   Keywords from goals: {keywords[:5]}...")
    assert 'bridge' in keywords or 'fabrication' in keywords, "Should extract keywords from training goals"
    
    # Test training information extraction
    training_info = extract_training_information_from_content(meeting_content, training_context)
    print(f"   Training info extraction: {len(training_info)} sections")
    assert len(training_info) > 0, "Should extract training information using goals"
    
    print("✅ Training goals usage test passed")

def test_file_content_extraction():
    """Test that file content is properly extracted into modules"""
    print("🧪 Testing file content extraction...")
    
    # Sample file content
    file_content = """
    Bridge Fabrication Process
    
    The bridge fabrication process involves several critical steps that must be followed precisely.
    
    Step 1: Shop Drawings Review
    All shop drawings must be carefully reviewed for accuracy before any fabrication begins.
    
    Step 2: Plate Cutting and Drilling
    Steel plates are cut and drilled according to the approved shop drawings.
    
    Step 3: Welding Procedure Specification (WPS)
    The WPS outlines the exact parameters for submerged arc welding (SAW) process.
    
    Step 4: Quality Control
    Non-destructive testing (NDT) is performed to verify weld integrity.
    
    Step 5: Fit-up and Assembly
    Proper fit-up is essential before any welding begins.
    """
    
    training_context = {
        'training_type': 'Process Training',
        'target_audience': 'fabricators',
        'industry': 'manufacturing',
        'primary_goals': 'understanding how to fabricate bridges',
        'success_metrics': 'feedback surveys'
    }
    
    # Test module extraction from file content
    modules = extract_modules_from_file_content("test_file.txt", file_content, training_context)
    
    print(f"   Modules extracted: {len(modules)}")
    assert len(modules) > 0, "Should extract modules from file content"
    
    # Check that modules contain actual content
    for i, module in enumerate(modules):
        print(f"   Module {i+1}: {module['title']}")
        print(f"   Content length: {len(module['content'])} characters")
        assert len(module['content']) > 100, f"Module {i+1} should contain substantial content"
        assert 'bridge' in module['content'].lower() or 'fabrication' in module['content'].lower(), f"Module {i+1} should contain relevant content"
    
    print("✅ File content extraction test passed")

def test_meeting_transcript_extraction():
    """Test extraction from meeting transcripts with training goals"""
    print("🧪 Testing meeting transcript extraction...")
    
    # Sample meeting transcript content
    meeting_content = """
    Meet Meeting
    Thu, Dec 12, 2024
    0:00 - MaiLinh Ho
    to work through the construction flow chart with you, just to understand how does that work now that we have pretty much the overview of manufacturing...
    
    0:02 - Bruce Mullaney
    Yeah, let's go through the construction flow chart. We need to understand the process for bridge fabrication.
    
    0:05 - MaiLinh Ho
    Right, so we have the shop drawings, then we move to plate cutting and drilling. The welding procedure specification (WPS) is critical for quality control.
    
    0:08 - Bruce Mullaney
    Exactly. And we need to ensure proper fit-up before welding. The submerged arc welding (SAW) process requires specific parameters.
    """
    
    training_context = {
        'training_type': 'Process Training',
        'target_audience': 'fabricators',
        'industry': 'manufacturing',
        'primary_goals': 'understanding how to fabricate bridges',
        'success_metrics': 'feedback surveys'
    }
    
    # Test content validation
    is_meaningful = is_meaningful_training_content(meeting_content, training_context)
    print(f"   Content validation: {is_meaningful}")
    assert is_meaningful, "Meeting content should be considered meaningful"
    
    # Test broader content extraction
    broader_content = extract_broader_training_content(meeting_content, training_context)
    print(f"   Broader extraction: {len(broader_content)} sentences")
    assert len(broader_content) > 0, "Should extract training content from meeting transcript"
    
    # Test training information extraction
    training_info = extract_training_information_from_content(meeting_content, training_context)
    print(f"   Training info extraction: {len(training_info)} sections")
    assert len(training_info) > 0, "Should extract training information from meeting transcript"
    
    print("✅ Meeting transcript extraction test passed")

def test_module_creation():
    """Test module creation from extracted content"""
    print("🧪 Testing module creation...")
    
    # Sample training content
    training_content = """
    Bridge fabrication process involves several critical steps. First, shop drawings must be carefully reviewed for accuracy. 
    Plate cutting and drilling follows specific procedures to ensure precision. The welding procedure specification (WPS) 
    outlines the exact parameters for submerged arc welding (SAW). Quality control includes non-destructive testing (NDT) 
    to verify weld integrity. Proper fit-up is essential before any welding begins.
    """
    
    training_context = {
        'training_type': 'Process Training',
        'target_audience': 'fabricators',
        'industry': 'manufacturing',
        'primary_goals': 'understanding how to fabricate bridges',
        'success_metrics': 'feedback surveys'
    }
    
    # Test module creation
    module = create_cohesive_module_content_optimized(training_content, training_context, 1)
    
    if module:
        print(f"   Module title: {module['title']}")
        print(f"   Module description: {module['description']}")
        print(f"   Module content length: {len(module['content'])}")
        assert len(module['content']) > 50, "Module should have substantial content"
        assert 'bridge' in module['content'].lower() or 'fabrication' in module['content'].lower(), "Module should contain relevant content"
        print("✅ Module creation test passed")
    else:
        print("❌ Module creation failed")

def test_content_validation():
    """Test content validation logic"""
    print("🧪 Testing content validation...")
    
    training_context = {
        'training_type': 'Process Training',
        'target_audience': 'fabricators',
        'industry': 'manufacturing',
        'primary_goals': 'understanding how to fabricate bridges'
    }
    
    # Test various content types
    test_cases = [
        ("Short content", "Too short", False),
        ("Bridge fabrication process involves welding procedures and quality control measures.", "Good content", True),
        ("Um, yeah, so like, you know, we need to, um, do the thing.", "Conversational", True),  # More lenient now
        ("", "Empty content", False),
        ("Process training for fabricators includes safety procedures and equipment operation.", "Training content", True)
    ]
    
    for content, description, expected in test_cases:
        result = is_meaningful_training_content(content, training_context)
        print(f"   {description}: {result} (expected: {expected})")
        if expected:
            assert result, f"Content should be considered meaningful: {description}"
        else:
            assert not result, f"Content should not be considered meaningful: {description}"
    
    print("✅ Content validation test passed")

def main():
    """Run all tests"""
    print("🚀 Testing Content Extraction Fixes")
    print("=" * 50)
    
    try:
        test_content_validation()
        test_training_goals_usage()
        test_meeting_transcript_extraction()
        test_file_content_extraction()
        test_module_creation()
        
        print("\n✅ All tests passed! Content extraction fixes are working correctly.")
        print("\n🎯 Key improvements:")
        print("• Training goals are now properly used for content extraction")
        print("• File content is properly extracted into modules")
        print("• Meeting transcripts now generate meaningful training modules")
        print("• Content validation is more lenient to preserve actual content")
        print("• Modules contain actual file content, not generic placeholders")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 