#!/usr/bin/env python3
"""
Test file for section extraction and module numbering
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_section_extraction():
    """Test the section extraction functionality"""
    
    # Mock editable pathways data
    editable_pathways = {
        'Safety Procedures': [
            {'title': 'PPE Requirements', 'description': 'Personal protective equipment', 'content': 'Safety content 1'},
            {'title': 'Equipment Safety', 'description': 'Equipment safety procedures', 'content': 'Safety content 2'},
            {'title': 'Emergency Procedures', 'description': 'Emergency response', 'content': 'Safety content 3'}
        ],
        'Quality Control': [
            {'title': 'Inspection Procedures', 'description': 'Quality inspection steps', 'content': 'Quality content 1'},
            {'title': 'Documentation', 'description': 'Quality documentation', 'content': 'Quality content 2'}
        ],
        'Process Training': [
            {'title': 'Standard Operating Procedures', 'description': 'SOP training', 'content': 'Process content 1'},
            {'title': 'Workflow Management', 'description': 'Workflow procedures', 'content': 'Process content 2'},
            {'title': 'Team Coordination', 'description': 'Team coordination', 'content': 'Process content 3'},
            {'title': 'Communication Protocols', 'description': 'Communication procedures', 'content': 'Process content 4'}
        ]
    }
    
    # Test the extract_target_from_input function
    from app import extract_target_from_input, create_module_mapping, get_module_reference_info, format_module_reference_help
    
    print("🔍 Testing section extraction...")
    
    # Test numbered section extraction
    result = extract_target_from_input("Update pathway 4 section 3 with uploaded information")
    print(f"Section extraction test: {result}")
    assert result and result['type'] == 'section' and result['identifier'] == 'section_3'
    
    # Test named section extraction
    result = extract_target_from_input("Add content to safety section")
    print(f"Named section extraction test: {result}")
    assert result and result['type'] == 'section' and result['identifier'] == 'safety'
    
    # Test pathway extraction
    result = extract_target_from_input("Update pathway with new information")
    print(f"Pathway extraction test: {result}")
    assert result and result['type'] == 'pathway' and result['identifier'] == 'entire'
    
    print("✅ All section extraction tests passed!")
    
    print("\n🔍 Testing module mapping system...")
    
    # Test module mapping creation
    module_mapping = create_module_mapping(editable_pathways)
    print(f"Module mapping created with {len(module_mapping['by_global_number'])} global modules")
    
    # Test section-specific module references
    safety_module_1 = module_mapping['by_section_and_number']['Safety Procedures']['1']
    print(f"Safety Module 1: {safety_module_1['module']['title']}")
    assert safety_module_1['local_number'] == 1
    assert safety_module_1['global_number'] == 1
    
    quality_module_1 = module_mapping['by_section_and_number']['Quality Control']['1']
    print(f"Quality Module 1: {quality_module_1['module']['title']}")
    assert quality_module_1['local_number'] == 1
    assert quality_module_1['global_number'] == 4  # After safety modules
    
    process_module_2 = module_mapping['by_section_and_number']['Process Training']['2']
    print(f"Process Module 2: {process_module_2['module']['title']}")
    assert process_module_2['local_number'] == 2
    assert process_module_2['global_number'] == 7  # After safety and quality modules
    
    # Test global module references
    global_module_3 = module_mapping['by_global_number']['3']
    print(f"Global Module 3: {global_module_3['module']['title']}")
    assert global_module_3['section'] == 'Safety Procedures'
    assert global_module_3['local_number'] == 3
    
    # Test title-based references
    ppe_module = module_mapping['by_title']['ppe requirements']
    print(f"PPE Module by title: {ppe_module['module']['title']}")
    assert ppe_module['section'] == 'Safety Procedures'
    assert ppe_module['local_number'] == 1
    
    print("✅ All module mapping tests passed!")
    
    print("\n🔍 Testing module reference info...")
    
    # Test module reference info
    reference_info = get_module_reference_info(editable_pathways)
    print(f"Reference info created for {len(reference_info)} sections")
    
    for section_info in reference_info:
        print(f"Section: {section_info['section_name']} ({section_info['module_count']} modules)")
        for module_info in section_info['modules']:
            print(f"  Module {module_info['local_number']}: {module_info['title']}")
    
    # Test help formatting
    help_text = format_module_reference_help(editable_pathways)
    print(f"\nHelp text length: {len(help_text)} characters")
    print("Help text preview:")
    print(help_text[:500] + "..." if len(help_text) > 500 else help_text)
    
    print("✅ All module reference tests passed!")
    
    print("\n🎯 Testing find_module_by_info with new mapping...")
    
    from app import find_module_by_info
    
    # Test finding module by local number
    result = find_module_by_info("module_1", editable_pathways)
    print(f"Module 1 result: {result['module']['title'] if result else 'Not found'}")
    assert result and result['module']['title'] == 'PPE Requirements'
    
    # Test finding module by title
    result = find_module_by_info("equipment safety", editable_pathways)
    print(f"Equipment safety result: {result['module']['title'] if result else 'Not found'}")
    assert result and result['module']['title'] == 'Equipment Safety'
    
    # Test finding module by section keyword
    result = find_module_by_info("safety", editable_pathways)
    print(f"Safety section result: {result['module']['title'] if result else 'Not found'}")
    assert result and result['section'] == 'Safety Procedures'
    
    print("✅ All find_module_by_info tests passed!")
    
    print("\n🎉 All tests completed successfully!")

if __name__ == "__main__":
    test_section_extraction() 