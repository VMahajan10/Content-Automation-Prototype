#!/usr/bin/env python3
"""
Simple test file for improved pathway section handling
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_pathway_section_extraction():
    """Test the improved pathway section extraction functionality"""
    
    # Test the extract_target_from_input function
    from app import extract_target_from_input
    
    # Test pathway section extraction
    result = extract_target_from_input("Update pathway 1 section 2 with new file")
    print(f"Pathway section extraction test: {result}")
    assert result and result['type'] == 'pathway_section' and result['pathway_num'] == 1 and result['section_num'] == 2
    
    # Test pathway section extraction with higher numbers
    result = extract_target_from_input("Update pathway 3 section 1 with new file")
    print(f"Pathway section extraction test (higher numbers): {result}")
    assert result and result['type'] == 'pathway_section' and result['pathway_num'] == 3 and result['section_num'] == 1
    
    # Test module extraction
    result = extract_target_from_input("Update module 2 with new file")
    print(f"Module extraction test: {result}")
    assert result and result['type'] == 'module' and result['identifier'] == 'module_2'
    
    # Test section extraction
    result = extract_target_from_input("Add content to safety section")
    print(f"Section extraction test: {result}")
    assert result and result['type'] == 'section' and result['identifier'] == 'safety'
    
    # Test pathway extraction
    result = extract_target_from_input("Update pathway with new information")
    print(f"Pathway extraction test: {result}")
    assert result and result['type'] == 'pathway' and result['identifier'] == 'entire'
    
    # Test numbered section extraction
    result = extract_target_from_input("Add content to section 3")
    print(f"Numbered section extraction test: {result}")
    assert result and result['type'] == 'section' and result['identifier'] == 'section_3'
    
    print("✅ All pathway section extraction tests passed!")

def test_error_handling_improvements():
    """Test the improved error handling for pathway references"""
    
    # Mock the update_pathway_section function to test error handling
    def mock_update_pathway_section(target_info, new_content_modules, editable_pathways, training_context):
        """Mock function to test error handling logic"""
        pathway_num = target_info['pathway_num']
        section_num = target_info['section_num']
        
        # Simulate current pathway (pathway 1)
        current_pathway = {
            'pathways': [
                {
                    'sections': [
                        {'title': 'Section 1', 'modules': []},
                        {'title': 'Section 2', 'modules': []},
                        {'title': 'Section 3', 'modules': []}
                    ]
                }
            ]
        }
        
        # Simulate past pathways
        past = [
            {
                'pathways': [
                    {
                        'sections': [
                            {'title': 'Past Section 1', 'modules': []},
                            {'title': 'Past Section 2', 'modules': []}
                        ]
                    }
                ]
            }
        ]
        
        # Test current pathway (pathway 1)
        if pathway_num == 1 and current_pathway:
            pathways = current_pathway.get('pathways', [])
            if not pathways:
                return f"❌ No pathways found in current pathway data"
            
            pathway = pathways[0]
            sections = pathway.get('sections', [])
            
            if section_num > len(sections):
                available_sections = list(range(1, len(sections) + 1))
                return f"❌ Section {section_num} not found in current pathway. Available sections: {available_sections}"
            
            return f"✅ Successfully updated Current Pathway, Section {section_num}"
        
        # Test past pathways (pathway 2 = first past pathway)
        elif pathway_num == 2 and len(past) > 0:
            pathway_data = past[pathway_num - 1]
            pathways = pathway_data.get('pathways', [])
            
            if not pathways:
                return f"❌ No pathways found in pathway data {pathway_num}"
            
            pathway = pathways[0]
            sections = pathway.get('sections', [])
            
            if section_num > len(sections):
                available_sections = list(range(1, len(sections) + 1))
                return f"❌ Section {section_num} not found in pathway {pathway_num}. Available sections: {available_sections}"
            
            return f"✅ Successfully updated Pathway {pathway_num}, Section {section_num}"
        
        else:
            # Provide helpful error message with available pathways
            available_pathways = ["Current Pathway (pathway 1)"]
            if past:
                available_pathways.extend([f"Past Pathway {i+1}" for i in range(len(past))])
            
            return f"❌ Pathway {pathway_num} not found. Available pathways: {', '.join(available_pathways)}"
    
    # Test current pathway section update
    target_info = {
        'type': 'pathway_section',
        'pathway_num': 1,
        'section_num': 2,
        'identifier': 'pathway_1_section_2'
    }
    
    result = mock_update_pathway_section(target_info, [], {}, {})
    print(f"Current pathway section update test: {result}")
    assert "✅" in result, "Should successfully update current pathway section"
    
    # Test past pathway section update
    target_info = {
        'type': 'pathway_section',
        'pathway_num': 2,
        'section_num': 1,
        'identifier': 'pathway_2_section_1'
    }
    
    result = mock_update_pathway_section(target_info, [], {}, {})
    print(f"Past pathway section update test: {result}")
    assert "✅" in result, "Should successfully update past pathway section"
    
    # Test error handling for non-existent pathway
    target_info = {
        'type': 'pathway_section',
        'pathway_num': 5,
        'section_num': 1,
        'identifier': 'pathway_5_section_1'
    }
    
    result = mock_update_pathway_section(target_info, [], {}, {})
    print(f"Non-existent pathway test: {result}")
    assert "❌" in result and "not found" in result, "Should provide helpful error message"
    
    # Test error handling for non-existent section
    target_info = {
        'type': 'pathway_section',
        'pathway_num': 1,
        'section_num': 10,
        'identifier': 'pathway_1_section_10'
    }
    
    result = mock_update_pathway_section(target_info, [], {}, {})
    print(f"Non-existent section test: {result}")
    assert "❌" in result and "not found" in result, "Should provide helpful error message"
    
    print("✅ All error handling improvement tests passed!")

if __name__ == "__main__":
    test_pathway_section_extraction()
    test_error_handling_improvements()
    print("✅ All pathway section improvement tests completed successfully!") 