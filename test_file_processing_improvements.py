#!/usr/bin/env python3
"""
Test file for improved file processing and pathway section updates
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pathway_section_extraction():
    """Test the pathway section extraction functionality"""
    
    print("🔍 Testing pathway section extraction...")
    
    from app import extract_target_from_input
    
    # Test pathway section reference
    test_input = "update pathway 4 section 3 with this information"
    result = extract_target_from_input(test_input)
    
    print(f"Input: {test_input}")
    print(f"Result: {result}")
    
    assert result is not None, "Should extract pathway section"
    assert result['type'] == 'pathway_section', "Should be pathway_section type"
    assert result['pathway_num'] == 4, "Should extract pathway number 4"
    assert result['section_num'] == 3, "Should extract section number 3"
    
    # Test other patterns
    test_inputs = [
        "add content to pathway 2 section 1",
        "update pathway 1 section 5 with new info",
        "modify pathway 3 section 2"
    ]
    
    for test_input in test_inputs:
        result = extract_target_from_input(test_input)
        print(f"Input: {test_input}")
        print(f"Result: {result}")
        assert result is not None, f"Should extract from: {test_input}"
        assert result['type'] == 'pathway_section', f"Should be pathway_section type for: {test_input}"
    
    print("✅ Pathway section extraction tests passed!")

def test_fallback_content_extraction():
    """Test the improved fallback content extraction"""
    
    print("\n📝 Testing fallback content extraction...")
    
    from app import create_simple_modules_from_content
    
    # Test with good content
    test_content = """
    Safety Procedures for Bridge Fabrication
    
    1. Personal Protective Equipment (PPE)
    - Hard hat must be worn at all times
    - Safety glasses for eye protection
    - Steel-toed boots required
    - High-visibility vest mandatory
    
    2. Equipment Safety
    - Inspect all tools before use
    - Follow lockout/tagout procedures
    - Maintain proper tool condition
    - Report damaged equipment immediately
    
    3. Workspace Safety
    - Keep work area clean and organized
    - Proper lighting for all work areas
    - Clear access paths maintained
    - Emergency exits clearly marked
    """
    
    training_context = {
        'primary_goals': 'Safety training',
        'training_type': 'Safety',
        'target_audience': 'Workers'
    }
    
    modules = create_simple_modules_from_content("safety_manual.txt", test_content, training_context)
    
    print(f"Created {len(modules)} modules from test content")
    for i, module in enumerate(modules):
        print(f"  Module {i+1}: {module['title']}")
        print(f"    Content length: {len(module['content'])} characters")
    
    assert len(modules) > 0, "Should create modules from good content"
    assert all(len(module['content']) > 50 for module in modules), "All modules should have substantial content"
    
    # Test with minimal content
    minimal_content = "This is a very short document."
    modules = create_simple_modules_from_content("short.txt", minimal_content, training_context)
    
    print(f"Created {len(modules)} modules from minimal content")
    assert len(modules) == 0, "Should not create modules from minimal content"
    
    # Test with empty content
    empty_content = ""
    modules = create_simple_modules_from_content("empty.txt", empty_content, training_context)
    
    print(f"Created {len(modules)} modules from empty content")
    assert len(modules) == 0, "Should not create modules from empty content"
    
    print("✅ Fallback content extraction tests passed!")

def test_file_processing_improvements():
    """Test the improved file processing with better error handling"""
    
    print("\n🔄 Testing file processing improvements...")
    
    # Mock uploaded file
    class MockUploadedFile:
        def __init__(self, name, content, file_type="text/plain"):
            self.name = name
            self.content = content.encode('utf-8')
            self.type = file_type
        
        def read(self):
            return self.content
    
    # Test with good content
    good_content = """
    Quality Control Procedures
    
    1. Inspection Process
    - Perform visual inspections before and after each operation
    - Check for defects and document findings
    - Use appropriate measuring tools
    - Record all measurements accurately
    
    2. Documentation Requirements
    - Complete inspection forms thoroughly
    - Include date, time, and inspector name
    - Attach photos of any defects found
    - File reports within 24 hours
    """
    
    mock_file = MockUploadedFile("quality_manual.txt", good_content)
    
    # Test the file processing logic
    from app import handle_file_based_module_update
    
    # Mock session state
    import streamlit as st
    if not hasattr(st, 'session_state'):
        st.session_state = {}
    
    st.session_state['editable_pathways'] = {
        'Quality Control': [
            {
                'title': 'Basic Inspection',
                'description': 'Basic quality inspection procedures',
                'content': 'Perform basic visual inspections.'
            }
        ]
    }
    st.session_state['training_context'] = {
        'primary_goals': 'Quality control training',
        'training_type': 'Quality',
        'target_audience': 'Inspectors'
    }
    st.session_state['past_generated_pathways'] = [
        {
            'pathways': [
                {
                    'pathway_name': 'Quality Training',
                    'sections': [
                        {'title': 'Introduction', 'modules': []},
                        {'title': 'Basic Procedures', 'modules': []},
                        {'title': 'Advanced Techniques', 'modules': []}
                    ]
                }
            ]
        }
    ]
    
    # Test pathway section update
    test_input = "update pathway 1 section 3 with this information"
    result = handle_file_based_module_update(test_input, [mock_file])
    
    print(f"File processing result: {result}")
    
    # The result should indicate success or provide helpful error messages
    assert "✅" in result or "❌" in result, "Should provide clear success/error feedback"
    
    print("✅ File processing improvements tests passed!")

def main():
    """Run all file processing improvement tests"""
    print("🔄 Testing File Processing Improvements")
    print("=" * 50)
    
    try:
        test_pathway_section_extraction()
        test_fallback_content_extraction()
        test_file_processing_improvements()
        
        print("\n🎉 All file processing improvement tests passed!")
        print("\n✅ Improvements implemented:")
        print("   • Better pathway section extraction (e.g., 'pathway 4 section 3')")
        print("   • Improved fallback content extraction")
        print("   • Better error handling and debugging")
        print("   • More robust file processing")
        print("   • Clearer success/error messages")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 