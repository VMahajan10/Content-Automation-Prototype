#!/usr/bin/env python3
"""
Test clean pathway generation functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_clean_pathway_generation():
    """
    Test pathway generation with clean, simple logic
    """
    
    # Sample training context
    context = {
        'primary_goals': 'Employee onboarding and safety training',
        'training_type': 'Onboarding',
        'target_audience': 'New Employees',
        'industry': 'Manufacturing',
        'company_size': 'Medium'
    }
    
    # Sample file contents
    extracted_file_contents = {
        'safety_manual.txt': """
        Safety Manual for Manufacturing Facility
        
        Section 1: Personal Protective Equipment
        All employees must wear appropriate PPE including hard hats, safety glasses, and steel-toed boots when working in the manufacturing area. PPE must be inspected before each use and replaced if damaged.
        
        Section 2: Safety
        Before operating any machinery, employees must complete safety training and receive proper authorization. Always follow lockout/tagout procedures when performing maintenance.
        
        Section 3: Emergency Procedures
        In case of emergency, immediately notify your supervisor and follow evacuation procedures. Know the location of emergency exits and first aid stations.
        """,
        
        'onboarding_checklist.txt': """
        New Employee Onboarding Checklist
        
        Day 1: Orientation
        - Complete new hire paperwork
        - Receive company ID and access cards
        - Attend safety orientation session
        - Meet with immediate supervisor
        
        Day 2-3: Training
        - Complete required safety training modules
        - Learn company policies and procedures
        - Receive job-specific training
        - Practice emergency procedures
        
        Week 1: Integration
        - Shadow experienced employees
        - Complete initial performance review
        - Set up work station and tools
        - Establish communication channels
        """
    }
    
    print("🔍 Testing clean pathway generation...")
    print(f"📋 Context: {context}")
    print(f"📄 Files: {list(extracted_file_contents.keys())}")
    
    # Simple pathway generation logic
    def generate_clean_pathway(context, extracted_file_contents):
        """
        Generate pathways using simple, clean logic
        """
        import time
        start_time = time.time()
        
        print(f"🚀 [Clean Pathway] Starting pathway generation for {len(extracted_file_contents)} files")
        
        primary_goals = context.get('primary_goals', '')
        training_type = context.get('training_type', 'Training')
        target_audience = context.get('target_audience', 'employees')
        industry = context.get('industry', 'general')
        
        all_modules = []
        file_debug = []
        
        for filename, content in extracted_file_contents.items():
            if not content or len(content.strip()) < 50:
                print(f"⚠️ Skipping {filename}: no content or too short")
                continue
            
            print(f"🔍 Processing file: {filename} (length: {len(content)})")
            
            # Simple content processing
            import re
            chunks = [c.strip() for c in re.split(r'\n\s*\n', content) if len(c.strip()) > 100]
            modules = []
            for i, chunk in enumerate(chunks):
                # Clean up the chunk
                cleaned_chunk = re.sub(r'\s+', ' ', chunk).strip()
                
                # Generate simple title
                title = f"Module {i+1}: {filename.replace('.txt', '').replace('_', ' ')}"
                
                modules.append({
                    'title': title,
                    'description': f"Content extracted from {filename}",
                    'content': cleaned_chunk,
                    'source': filename
                })
            
            print(f"✅ {filename}: {len(modules)} modules extracted")
            all_modules.extend(modules)
            file_debug.append(f"{filename}: {len(modules)} modules")
        
        if not all_modules:
            print("⚠️ No modules extracted, creating basic pathway")
            return {
                'pathways': [{
                    'pathway_name': 'Basic Training Pathway',
                    'sections': [{
                        'title': 'Modules from Uploaded Files',
                        'modules': []
                    }]
                }]
            }
            
        # Create pathway
        pathway = {
            'pathway_name': f"{training_type} Pathway for {target_audience} ({industry})",
            'sections': [{
                'title': 'Modules from Uploaded Files',
                'modules': all_modules
            }]
        }
        
        print(f"🎯 Pathway generated with {len(all_modules)} modules from {len(extracted_file_contents)} files")
        print(f"⏱️ Total time: {round(time.time()-start_time, 1)}s")
        print(f"Files processed: {', '.join(file_debug)}")
        
        return {'pathways': [pathway]}
    
    # Generate pathway
    result = generate_clean_pathway(context, extracted_file_contents)
    
    # Display results
    print("\n" + "="*50)
    print("📊 PATHWAY GENERATION RESULTS")
    print("="*50)
    
    if result and 'pathways' in result:
        for i, pathway in enumerate(result['pathways']):
            print(f"🎯 Pathway {i+1}: {pathway['pathway_name']}")
            
            for j, section in enumerate(pathway['sections']):
                print(f"📑 Section {j+1}: {section['title']}")
                print(f"     Modules: {len(section['modules'])}")
                
                for k, module in enumerate(section['modules'][:3]):  # Show first 3 modules
                    print(f"       📝 Module {k+1}: {module['title']}")
                    print(f"         Source: {module['source']}")
                    print(f"   Content preview: {module['content'][:100]}...")
                
                if len(section['modules']) > 3:
                    print(f"       ... and {len(section['modules']) - 3} more modules")
    else:
        print("❌ No pathways generated")
    
    print("\n✅ Test completed successfully!")
    return result

if __name__ == "__main__":
    test_clean_pathway_generation() 