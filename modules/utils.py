"""
Utilities module for Gateway Content Automation
Common helper functions used across the application
"""

import streamlit as st
from modules.config import model
import json, re
import concurrent.futures
import threading
from queue import Queue
import time
import hashlib
import re
import google.generativeai as genai
from modules.config import api_key

# Global queue for managing AI requests
ai_request_queue = Queue()
ai_response_queue = Queue()

def get_parallel_config():
    """
    Get configuration for parallel processing based on system capabilities
    (Tuned for best speed: increase workers and timeout for faster processing)
    """
    return {
        'max_file_workers': 6,      # Higher parallelism for multiple files
        'max_section_workers': 8,   # More agents for section analysis
        'max_topic_workers': 2,     # Multiple topic analysis
        'timeout_seconds': 120      # Longer timeout for large/slow sections
    }

def extract_key_topics_from_content(content, max_topics=5):
    """
    Extract key topics from uploaded content using AI
    """
    try:
        if model is None:
            st.warning("Gemini API not available for topic extraction")
            return []
            
        if not content or len(content.strip()) < 50:
            return []
        
        # Use Gemini to extract key topics
        prompt = f"""
        Extract the top {max_topics} most important topics or concepts from this training content:
        
        {content[:2000]}
        
        Return only the topic names, separated by commas. Keep them short and relevant.
        """
        
        response = model.generate_content(prompt)
        topics = [topic.strip() for topic in response.text.split(',') if topic.strip()]
        return topics[:max_topics]
    except Exception as e:
        st.warning(f"Could not extract topics from content: {str(e)}")
        return []

def calculate_text_dimensions(text, max_width, max_height):
    """
    Calculate appropriate dimensions for text widgets based on content length
    """
    # Base dimensions
    base_width = 200
    base_height = 60
    
    # Adjust based on text length
    text_length = len(text)
    
    if text_length <= 30:
        width = base_width
        height = base_height
    elif text_length <= 60:
        width = base_width + 50
        height = base_height + 20
    elif text_length <= 100:
        width = base_width + 100
        height = base_height + 40
    else:
        width = base_width + 150
        height = base_height + 60
    
    # Ensure we don't exceed maximum dimensions
    width = min(width, max_width)
    height = min(height, max_height)
    
    return width, height 

def gemini_generate_module_description(content: str) -> str:
    """
    Use Gemini to generate a grammatically correct, concise, and clear description for a module.
    """
    try:
        if not content or len(content.strip()) < 20:
            return "Module extracted from uploaded file."
        prompt = f"""
        Summarize the following training module content in 1-2 clear, grammatically correct sentences. The summary should be concise, legible, and suitable as a description for an onboarding module. Do not repeat the title. Do not use generic phrases like 'this module'.

        Content:
        {content[:2000]}
        """
        response = model.generate_content(prompt)
        desc = response.text.strip().replace('\n', ' ')
        return desc
    except Exception as e:
        st.warning(f"Could not generate module description: {str(e)}")
        return "Module extracted from uploaded file." 

def gemini_group_modules_into_sections(modules):
    """
    Use Gemini to group modules into logical sections and generate section titles.
    modules: list of dicts with 'title' and 'content'.
    Returns: list of dicts: { 'section_title': str, 'module_indices': [int, ...] }
    """
    try:
        if not modules or len(modules) < 2:
            return [{ 'section_title': 'General', 'module_indices': list(range(len(modules))) }]
        module_list_str = "\n".join([f"{i+1}. {m['title']}: {m['content'][:100]}" for i, m in enumerate(modules)])
        prompt = f"""
        You are an expert instructional designer. Given the following list of onboarding modules (with their titles and a content excerpt), group them into logical sections for an onboarding program. For each section, provide a clear, descriptive section title and list the module numbers that belong in that section. Return the result as JSON in the format: [{{"section_title": str, "module_indices": [int, ...]}}].

        Modules:
        {module_list_str}
        """
        response = model.generate_content(prompt)
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```", 1)[-1].strip()
        raw = raw.replace("'", '"')
        # Remove trailing commas before closing brackets
        raw = re.sub(r',([ \t\r\n]*[\]}])', r'\1', raw)
        # Fix unescaped double quotes in section titles (e.g., Manager"s -> Manager's)
        raw = re.sub(r'([A-Za-z])\"s', r"\1's", raw)
        # Extract the first JSON array
        match = re.search(r'(\[.*\])', raw, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            json_str = raw
        try:
            sections = json.loads(json_str)
            if isinstance(sections, list) and all('section_title' in s and 'module_indices' in s for s in sections):
                return sections
        except Exception as e:
            st.warning(f"Could not parse Gemini section grouping: {str(e)}\nRaw response:\n{json_str}")
            st.text_area("Raw Gemini Output (fix manually if needed):", value=json_str, height=200)
        return [{ 'section_title': 'General', 'module_indices': list(range(len(modules))) }]
    except Exception as e:
        st.warning(f"Could not group modules into sections: {str(e)}")
        return [{ 'section_title': 'General', 'module_indices': list(range(len(modules))) }] 

def group_modules_into_multiple_pathways(modules, training_context, num_pathways=3, sections_per_pathway=6, modules_per_section=4):
    """
    Use Gemini to group existing modules into multiple pathways, preserving the actual content from files.
    Returns: list of pathway dicts.
    """
    if not modules:
        return []
    
    # Create a mapping of module indices to actual module content
    module_mapping = {}
    for i, module in enumerate(modules):
        module_mapping[i] = module
    
    print(f"🤖 Grouping {len(modules)} modules into {num_pathways} pathways...")
    
    # Adjust number of pathways based on module count and training goals
    if len(modules) >= 25:
        num_pathways = 5
        sections_per_pathway = 6
        modules_per_section = 5
    elif len(modules) >= 20:
        num_pathways = 4
        sections_per_pathway = 6
        modules_per_section = 4
    elif len(modules) >= 15:
        num_pathways = 4
        sections_per_pathway = 5
        modules_per_section = 4
    elif len(modules) >= 10:
        num_pathways = 3
        sections_per_pathway = 5
        modules_per_section = 4
    elif len(modules) >= 5:
        num_pathways = 3
        sections_per_pathway = 4
        modules_per_section = 3
    else:
        num_pathways = 2
        sections_per_pathway = 3
        modules_per_section = 3
    
    # If we have very few modules, create a simple pathway
    if len(modules) <= 3:
        print(f"📝 Few modules ({len(modules)}), creating simple pathway structure")
        return [{
            "pathway_name": f"{training_context.get('training_type', 'Training')} Pathway - {training_context.get('target_audience', 'Employee')} Onboarding",
            "sections": [{
                'title': 'Training Content',
                'description': 'All extracted training content from uploaded files',
                'modules': [{
                    "title": m['title'],
                    "description": m['description'],
                    "content": m['content'],  # Preserve actual file content
                    "source": m.get('source', 'File content')
                } for m in modules]
            }]
        }]
    
    # Create pathway themes based on training goals
    training_goals = training_context.get('primary_goals', '').lower()
    training_type = training_context.get('training_type', 'Training')
    industry = training_context.get('industry', 'General')
    
    # Define pathway themes dynamically based on training context
    pathway_themes = []
    
    # Extract themes from training goals
    if 'workflow' in training_goals or 'process' in training_goals:
        pathway_themes.extend(['Workflow Fundamentals', 'Process Optimization', 'Quality Control', 'Efficiency Management'])
    if 'safety' in training_goals:
        pathway_themes.extend(['Safety Procedures', 'Equipment Safety', 'Emergency Response', 'Hazard Management'])
    if 'quality' in training_goals:
        pathway_themes.extend(['Quality Standards', 'Inspection Procedures', 'Documentation', 'Continuous Improvement'])
    if 'skill' in training_goals or 'technique' in training_goals:
        pathway_themes.extend(['Core Skills', 'Advanced Techniques', 'Best Practices', 'Skill Development'])
    if 'communication' in training_goals or 'team' in training_goals:
        pathway_themes.extend(['Communication Skills', 'Team Collaboration', 'Leadership', 'Interpersonal Skills'])
    if 'compliance' in training_goals or 'regulation' in training_goals:
        pathway_themes.extend(['Compliance & Regulations', 'Policy Adherence', 'Audit Preparation', 'Legal Requirements'])
    if 'management' in training_goals or 'supervision' in training_goals:
        pathway_themes.extend(['Management Skills', 'Supervision Techniques', 'Performance Management', 'Team Leadership'])
    if 'equipment' in training_goals or 'tool' in training_goals:
        pathway_themes.extend(['Equipment Operation', 'Tool Usage', 'Maintenance Procedures', 'Equipment Safety'])
    
    # Add themes based on training type
    if 'onboarding' in training_type.lower():
        pathway_themes.extend(['Orientation & Welcome', 'Company Policies', 'Role-Specific Training', 'Integration'])
    elif 'safety' in training_type.lower():
        pathway_themes.extend(['Safety Fundamentals', 'Hazard Recognition', 'Emergency Procedures', 'Safety Culture'])
    elif 'compliance' in training_type.lower():
        pathway_themes.extend(['Regulatory Requirements', 'Policy Implementation', 'Audit Procedures', 'Compliance Monitoring'])
    elif 'leadership' in training_type.lower():
        pathway_themes.extend(['Leadership Fundamentals', 'Team Management', 'Strategic Thinking', 'Decision Making'])
    elif 'technical' in training_type.lower():
        pathway_themes.extend(['Technical Fundamentals', 'Advanced Applications', 'Troubleshooting', 'Technical Skills'])
    
    # Add industry-specific themes if available
    if industry and industry.lower() != 'general':
        pathway_themes.extend([f'{industry.title()} Fundamentals', f'{industry.title()} Best Practices', f'{industry.title()} Compliance', f'{industry.title()} Operations'])
    
    # Add default themes if none found
    if not pathway_themes:
        pathway_themes = ['Core Skills', 'Advanced Techniques', 'Safety & Compliance', 'Quality Assurance', 'Professional Development']
    
    # Limit to number of pathways
    pathway_themes = pathway_themes[:num_pathways]
    
    prompt = f"""
You are an expert instructional designer. Given the following list of training modules (extracted from actual files), group them into {num_pathways} distinct training pathways focused on these themes: {', '.join(pathway_themes)}.

Each pathway should have {sections_per_pathway} sections, and each section should have {modules_per_section} modules (if enough modules are available).

Training Context:
- Training Type: {training_type}
- Target Audience: {training_context.get('target_audience', 'New Employees')}
- Industry: {industry}
- Primary Goals: {training_context.get('primary_goals', '')}
- Success Metrics: {training_context.get('success_metrics', '')}

Available Modules (use the EXACT module numbers in your response):
"""
    for i, m in enumerate(modules):
        prompt += f"{i+1}. {m['title']}: {m['description']} | Content: {m['content'][:200]}...\n"
    
    prompt += f"""

Return as JSON with ONLY the module numbers (not new content):
[
  {{
    "pathway_name": "Descriptive pathway name based on theme",
    "sections": [
      {{
        "title": "Section title",
        "description": "Brief section description",
        "module_indices": [1, 3, 5]  // Use the actual module numbers from above
      }}
    ]
  }}
]

CRITICAL REQUIREMENTS:
- You MUST assign at least 1 module to each section using module_indices
- Use ONLY the module numbers (1, 2, 3, etc.) from the list above
- Do NOT create new content or descriptions
- Do NOT use module numbers that don't exist
- Group related modules together logically based on the pathway themes
- Preserve the actual file content in each module
- If you have fewer modules than sections, some sections can have fewer modules
- Distribute modules evenly across sections when possible
- Create meaningful pathway names that reflect the content focus and training goals
- Focus on practical, actionable training content
- Create comprehensive pathways with multiple sections for better learning structure
"""
    
    response = model.generate_content(prompt)
    raw = response.text.strip()
    cleaned = clean_gemini_json(raw)
    
    try:
        array_match = re.search(r'\[.*\]', cleaned, re.DOTALL)
        if array_match:
            json_array = array_match.group(0)
            pathways_data = json.loads(json_array)
            
            if isinstance(pathways_data, list):
                # Convert module indices back to actual module content
                final_pathways = []
                for pathway_data in pathways_data:
                    pathway = {
                        "pathway_name": pathway_data.get("pathway_name", "Training Pathway"),
                        "sections": []
                    }
                    
                    for section_data in pathway_data.get("sections", []):
                        section = {
                            "title": section_data.get("title", "General"),
                            "description": section_data.get("description", ""),
                            "modules": []
                        }
                        
                        # Get actual modules using the indices - PRESERVE ORIGINAL CONTENT
                        module_indices = section_data.get("module_indices", [])
                        for idx in module_indices:
                            # Convert 1-based index to 0-based
                            actual_idx = idx - 1
                            if actual_idx in module_mapping:
                                # Use the original module with its actual file content
                                original_module = module_mapping[actual_idx]
                                section["modules"].append({
                                    "title": original_module['title'],
                                    "description": original_module['description'],
                                    "content": original_module['content'],  # Preserve actual file content
                                    "source": original_module.get('source', 'File content')
                                })
                        
                        # Only add sections that have modules
                        if section["modules"]:
                            pathway["sections"].append(section)
                    
                    # Only add pathways that have sections with modules
                    if pathway["sections"]:
                        final_pathways.append(pathway)
                
                # If AI didn't create valid pathways, use fallback
                if not final_pathways:
                    print(f"⚠️ AI didn't create valid pathways, using fallback")
                    return create_fallback_pathways(modules, training_context)
                
                return final_pathways
    except Exception as e:
        print(f"⚠️ Could not parse Gemini multi-pathway grouping: {str(e)}")
    
    # Fallback: create one pathway with all modules, preserving actual content
    print(f"🔄 Using fallback pathway creation")
    return create_fallback_pathways(modules, training_context)

def gemini_generate_complete_pathway(training_context, extracted_file_contents, file_inventory, bypass_filtering=False):
    """
    Use Gemini to generate one or more complete pathway structures including sections and modules
    based on the training context and extracted content.
    Returns: dict with 'pathways': list of pathway dicts
    """
    try:
        st.write("🔧 **AI Function Debug:**")
        if model is None:
            st.error("❌ Gemini API is not configured. Please check your GEMINI_API_KEY in the .env file.")
            return None
        st.write("✅ Model is available")
        training_type = training_context.get('training_type', 'Onboarding')
        target_audience = training_context.get('target_audience', 'New Employees')
        industry = training_context.get('industry', 'General')
        company_size = training_context.get('company_size', 'Medium')
        st.write(f"📋 Training Context: {training_type}, {target_audience}, {industry}")
        if not training_context:
            training_context = {
                'training_type': 'Onboarding',
                'target_audience': 'New Employees',
                'industry': 'General',
                'company_size': 'Medium'
            }
        file_based_modules = []
        content_analysis = []
        st.write(f"📁 Processing {len(extracted_file_contents)} files...")
        
        # Use parallel processing for multiple files
        if len(extracted_file_contents) > 1:
            print(f"🚀 **Using parallel processing for {len(extracted_file_contents)} files**")
            
            def process_single_file(file_data):
                """Process a single file for modules"""
                filename, content = file_data
                
                # Skip video files that might cause timeouts
                if filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                    print(f"⏭️ Skipping video file: {filename} (will process separately if needed)")
                    return {
                        'filename': filename,
                        'modules': [],
                        'success': False,
                        'reason': 'Video file skipped for speed'
                    }
                
                if content and len(content.strip()) > 50:
                    print(f"🔍 Processing file: {filename} (content length: {len(content)})")
                    
                    # Extract modules from file
                    file_modules = extract_modules_from_file_content(filename, content, training_context, bypass_filtering)
                    
                    return {
                        'filename': filename,
                        'modules': file_modules,
                        'success': True
                    }
                else:
                    return {
                        'filename': filename,
                        'modules': [],
                        'success': False,
                        'reason': 'No content or too short'
                    }
            
            # Process files in parallel with better error handling
            config = get_parallel_config()
            max_workers = min(config['max_file_workers'], len(extracted_file_contents))
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_file = {executor.submit(process_single_file, file_data): file_data for file_data in extracted_file_contents.items()}
                
                # Collect results with better timeout handling
                completed_files = 0
                for future in concurrent.futures.as_completed(future_to_file, timeout=config['timeout_seconds']):
                    try:
                        result = future.result(timeout=30)  # Individual file timeout
                        if result['success']:
                            file_based_modules.extend(result['modules'])
                            content_analysis.append(f"File: {result['filename']}\nExtracted {len(result['modules'])} content modules")
                            print(f"✅ Extracted {len(result['modules'])} content modules from {result['filename']}")
                        else:
                            print(f"⚠️ Skipping {result['filename']} - {result['reason']}")
                        completed_files += 1
                    except concurrent.futures.TimeoutError:
                        # Handle individual file timeout
                        file_data = future_to_file[future]
                        filename = file_data[0]
                        print(f"⚠️ File {filename} processing timed out - skipping")
                        content_analysis.append(f"File: {filename}\nTimed out - skipped")
                    except Exception as e:
                        # Handle other errors
                        file_data = future_to_file[future]
                        filename = file_data[0]
                        print(f"⚠️ Error processing {filename}: {str(e)}")
                        content_analysis.append(f"File: {filename}\nError: {str(e)}")
                
                # Check if we have any results
                if not file_based_modules:
                    print("⚠️ No modules extracted from parallel processing, trying fallback...")
                    # Fallback to processing files sequentially
                    for filename, content in extracted_file_contents.items():
                        if content and len(content.strip()) > 50:
                            print(f"🔄 Fallback processing: {filename}")
                            file_modules = extract_modules_from_file_content(filename, content, training_context, bypass_filtering)
                            file_based_modules.extend(file_modules)
                            content_analysis.append(f"File: {filename}\nFallback extracted {len(file_modules)} modules")
        else:
            # Single file processing (original method)
            for filename, content in extracted_file_contents.items():
                if content and len(content.strip()) > 50:
                    print(f"🔍 Processing file: {filename} (content length: {len(content)})")
                    
                    # Extract actual content from files
                    file_modules = extract_modules_from_file_content(filename, content, training_context, bypass_filtering)
                    
                    file_based_modules.extend(file_modules)
                    content_analysis.append(f"File: {filename}\nExtracted {len(file_modules)} content modules")
                    print(f"✅ Extracted {len(file_modules)} content modules from {filename}")
                else:
                    print(f"⚠️ Skipping {filename} - no content or too short")
        print(f"📊 Total modules extracted: {len(file_based_modules)}")
        inventory_summary = []
        if file_inventory.get('process_docs'):
            inventory_summary.append(f"Process documents: {file_inventory['process_docs']}")
        if file_inventory.get('training_materials'):
            inventory_summary.append(f"Training materials: {file_inventory['training_materials']}")
        if file_inventory.get('policies'):
            inventory_summary.append(f"Policies: {file_inventory['policies']}")
        if file_inventory.get('technical_docs'):
            inventory_summary.append(f"Technical documentation: {file_inventory['technical_docs']}")
        print(f"📝 Inventory summary: {inventory_summary}")
        # --- MULTI-PATHWAY LOGIC ---
        if file_based_modules:
            print("🛤️ Creating multiple pathways from file modules...")
            print(f"📊 Modules to organize: {len(file_based_modules)}")
            for i, module in enumerate(file_based_modules[:3]):  # Show first 3 modules
                print(f"   Module {i+1}: {module.get('title', 'No title')} - {len(module.get('content', ''))} chars")
            
            try:
                pathways = group_modules_into_multiple_pathways(file_based_modules, training_context, num_pathways=2, sections_per_pathway=5, modules_per_section=5)
                print(f"✅ Pathways created: {len(pathways)}")
                
                # Debug pathway structure
                for i, pathway in enumerate(pathways):
                    print(f"   Pathway {i+1}: {pathway.get('pathway_name', 'Unknown')}")
                    sections = pathway.get('sections', [])
                    print(f"   Sections: {len(sections)}")
                    for j, section in enumerate(sections):
                        modules = section.get('modules', [])
                        print(f"     Section {j+1}: {section.get('title', 'Unknown')} - {len(modules)} modules")
                
                return {"pathways": pathways}
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "quota" in error_msg.lower() or "rate" in error_msg.lower():
                    print(f"⚠️ API rate limit hit: {error_msg}")
                    print("🔄 Falling back to non-AI pathway creation...")
                    
                    # Create pathways without AI
                    fallback_pathways = create_fallback_pathways(file_based_modules, training_context)
                    if fallback_pathways:
                        print(f"✅ Fallback pathways created: {len(fallback_pathways)}")
                        return {"pathways": fallback_pathways}
                    else:
                        print("❌ Fallback pathway creation also failed")
                        return None
                else:
                    # Re-raise other errors
                    raise e
        else:
            print("🛤️ Creating generic pathway...")
            result = create_generic_pathway(training_context, inventory_summary)
            print(f"✅ Generic pathway created: {result}")
            return {"pathways": [result]}
    except Exception as e:
        st.error(f"❌ Error generating pathway with AI: {str(e)}")
        st.info("💡 This might be due to:")
        st.info("• Network connectivity issues")
        st.info("• Invalid API key")
        st.info("• API rate limits")
        st.info("• Insufficient training context")
        import traceback
        st.code(traceback.format_exc())
        return None

def clean_gemini_json(raw):
    """
    Clean Gemini's JSON output: remove trailing commas, fix lists in 'content', etc.
    Returns a string ready for json.loads.
    """
    # Remove code block markers
    if raw.startswith("```json"):
        raw = raw.split("```json", 1)[-1].strip()
    elif raw.startswith("```"):
        raw = raw.split("```", 1)[-1].strip()
    # Remove trailing commas before closing brackets/braces
    raw = re.sub(r',([ \t\r\n]*[\]}])', r'\1', raw)
    # Fix unescaped double quotes in section titles (e.g., Manager"s -> Manager's)
    raw = re.sub(r'([A-Za-z])\"s', r"\1's", raw)
    # Replace single quotes with double quotes (if not inside content)
    # raw = raw.replace("'", '"')
    # Fix lists in 'content' fields: "content": [ ... ] => join as string
    def content_list_to_string(match):
        items = match.group(1)
        # Remove quotes and join with newlines
        lines = re.findall(r'"(.*?)"', items)
        return '"content": "' + '\\n'.join(lines) + '"'
    raw = re.sub(r'"content"\s*:\s*\[(.*?)\]', content_list_to_string, raw, flags=re.DOTALL)
    return raw

def extract_modules_from_file_content(filename, content, training_context, bypass_filtering=False):
    """
    Extract content from uploaded files that aligns with primary training goals.
    Uses semantic topic analysis to identify relevant content sections.
    """
    try:
        print(f"📄 **Extracting semantically relevant content from {filename}**")
        print(f"📄 Content length: {len(content)} characters")
        print(f"📄 Content preview: {content[:200]}...")
        
        if not content or len(content.strip()) < 50:
            print(f"⚠️ {filename} has insufficient content for extraction")
            return []
        
        # Use semantic topic analysis to identify relevant content
        return extract_modules_from_file_content_fallback(filename, content, training_context, bypass_filtering)
        
    except Exception as e:
        print(f"⚠️ Could not extract semantically relevant content from {filename}: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return []

def chunk_content_for_rag(content, chunk_size=500, overlap=100):
    """
    Split content into overlapping chunks for RAG retrieval
    """
    chunks = []
    words = content.split()
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        chunk_text = ' '.join(chunk_words)
        if len(chunk_text.strip()) > 100:  # Only keep substantial chunks
            chunks.append({
                'text': chunk_text,
                'start_word': i,
                'end_word': min(i + chunk_size, len(words))
            })
    
    return chunks

def retrieve_relevant_chunks(topic, chunks, training_context, model, top_k=3):
    """
    Retrieve the most relevant chunks for a given topic using semantic similarity
    """
    try:
        # Create a simple retrieval prompt
        prompt = f"""
        Given the topic "{topic}", rank these content chunks by relevance (1 = most relevant, 3 = least relevant).
        Return only the chunk numbers in order of relevance.

        Chunks:
        """
        for i, chunk in enumerate(chunks[:5]):  # Limit to first 5 chunks for efficiency
            prompt += f"\n{i+1}. {chunk['text'][:200]}...\n"
        
        response = model.generate_content(prompt)
        
        # Extract chunk numbers from response
        import re
        numbers = re.findall(r'\d+', response.text)

        relevant_chunks = []
        for num in numbers[:top_k]:
            idx = int(num) - 1
            if 0 <= idx < len(chunks):
                relevant_chunks.append(chunks[idx])

        return relevant_chunks
    except Exception as e:
        print(f"⚠️ Chunk retrieval error: {str(e)}")
        return chunks[:top_k]  # Fallback to first chunks

def synthesize_module_content(topic, relevant_chunks, training_context, model):
    """
    Use direct content from file chunks instead of AI synthesis
    """
    try:
        # Combine relevant chunks directly - no AI synthesis
        combined_content = " ".join([chunk['text'] for chunk in relevant_chunks])
        
        # Clean up the content slightly but keep it as close to original as possible
        cleaned_content = combined_content.strip()
        
        # If content is too long, truncate it but keep the most relevant parts
        if len(cleaned_content) > 2000:
            # Try to find the most relevant section
            words = cleaned_content.split()
            if len(words) > 300:
                # Take the first 300 words (approximately 2000 characters)
                cleaned_content = " ".join(words[:300]) + "..."
        
        st.write(f"📄 Using direct content from file chunks (no AI synthesis)")
        st.write(f"📄 Content length: {len(cleaned_content)} characters")
        
        return cleaned_content
            
    except Exception as e:
        st.write(f"⚠️ Content processing error: {str(e)}")
        # Fallback: combine chunks directly
        return " ".join([chunk['text'] for chunk in relevant_chunks])

def create_pathway_from_file_modules(file_modules, training_context, content_analysis, inventory_summary):
    """
    Create a pathway structure from file-based modules
    """
    try:
        # Group modules into logical sections
        sections = group_modules_into_sections(file_modules)
        # Fallback: if sections is empty, create one section with all modules
        if not sections or not any(s.get('modules') for s in sections):
            sections = [{
                'title': 'General',
                'description': 'All modules grouped together',
                'modules': file_modules
            }]
        # Create pathway name based on content
        pathway_name = f"{training_context.get('training_type', 'Training')} Pathway - {training_context.get('target_audience', 'Employee')} Onboarding"
        return {
            "pathway_name": pathway_name,
            "sections": sections
        }
    except Exception as e:
        st.warning(f"Could not create pathway from file modules: {str(e)}")
        # Fallback: one section with all modules
        return {
            "pathway_name": f"{training_context.get('training_type', 'Training')} Pathway - {training_context.get('target_audience', 'Employee')} Onboarding",
            "sections": [{
                'title': 'General',
                'description': 'All modules grouped together',
                'modules': file_modules
            }]
        }

def group_modules_into_sections(modules):
    """
    Group modules into logical sections using AI, preserving actual content from files
    """
    try:
        if not modules:
            return []
        
        # Create module list for AI analysis
        module_list = "\n".join([f"{i+1}. {m['title']}: {m['content'][:200]}" for i, m in enumerate(modules)])
        
        prompt = f"""
        Group these training modules (extracted from actual files) into logical sections. Each section should have a clear theme and contain 2-4 related modules.
        
        Available Modules (use the EXACT module numbers in your response):
        {module_list}
        
        Return as JSON with ONLY the module numbers:
        [
            {{
                "title": "Section title",
                "description": "Brief description of what this section covers",
                "module_indices": [1, 3, 5]  // Use the actual module numbers from above
            }}
        ]
        
        IMPORTANT: 
        - Use ONLY the module numbers (1, 2, 3, etc.) from the list above
        - Do NOT create new content or descriptions
        - Group modules that are related or follow a logical progression
        - Create 3-5 sections total
        - Preserve the actual file content in each module
        """
        
        response = model.generate_content(prompt)
        raw = response.text.strip()
        cleaned = clean_gemini_json(raw)
        
        try:
            sections_data = json.loads(cleaned)
            if isinstance(sections_data, list) and len(sections_data) > 0:
                # Convert module indices back to actual module content
                final_sections = []
                for section_data in sections_data:
                    section = {
                        "title": section_data.get("title", "General"),
                        "description": section_data.get("description", ""),
                        "modules": []
                    }
                    
                    # Get actual modules using the indices - PRESERVE ORIGINAL CONTENT
                    module_indices = section_data.get("module_indices", [])
                    for idx in module_indices:
                        # Convert 1-based index to 0-based
                        actual_idx = idx - 1
                        if 0 <= actual_idx < len(modules):
                            original_module = modules[actual_idx]
                            section["modules"].append({
                                "title": original_module['title'],
                                "description": original_module['description'],
                                "content": original_module['content'],  # Preserve actual file content
                                "source": original_module.get('source', 'File content')
                            })
                    
                    if section["modules"]:  # Only add sections that have modules
                        final_sections.append(section)
                
                if final_sections:
                    return final_sections
            else:
                    # Fallback: one section with all modules, preserving actual content
                    return [{
                        'title': 'All Modules',
                        'description': 'All extracted modules grouped together',
                        'modules': [{
                            "title": m['title'],
                            "description": m['description'],
                            "content": m['content'],  # Preserve actual file content
                            "source": m.get('source', 'File content')
                        } for m in modules]
                    }]
        except json.JSONDecodeError as e:
            # Log the error to a file
            try:
                with open('section_json_error_log.txt', 'w') as f:
                    f.write(f"Section JSON Decode Error: {str(e)}\n")
                    f.write(f"Error Position: Line {e.lineno}, Column {e.colno}\n")
                    f.write(f"Raw Response:\n{cleaned}\n")
                    f.write(f"Response Length: {len(cleaned)}\n")
            except:
                pass
            # Fallback: one section with all modules, preserving actual content
            return [{
                'title': 'All Modules',
                'description': 'All extracted modules grouped together',
                'modules': [{
                    "title": m['title'],
                    "description": m['description'],
                    "content": m['content'],  # Preserve actual file content
                    "source": m.get('source', 'File content')
                } for m in modules]
            }]
    except Exception as e:
        st.warning(f"Could not group modules into sections: {str(e)}")
        # Fallback: one section with all modules, preserving actual content
        return [{
            'title': 'All Modules',
            'description': 'All extracted modules grouped together',
            'modules': [{
                "title": m['title'],
                "description": m['description'],
                "content": m['content'],  # Preserve actual file content
                "source": m.get('source', 'File content')
            } for m in modules]
        }]

def create_generic_pathway(training_context, inventory_summary):
    """
    Create a generic pathway when no file content is available
    """
    try:
        st.write("🔧 **Creating Generic Pathway Debug:**")
        
        training_type = training_context.get('training_type', 'Onboarding')
        target_audience = training_context.get('target_audience', 'New Employees')
        industry = training_context.get('industry', 'General')
        
        st.write(f"📋 Training type: {training_type}")
        st.write(f"📋 Target audience: {target_audience}")
        st.write(f"📋 Industry: {industry}")
        st.write(f"📝 Inventory summary: {inventory_summary}")
        
        # If no inventory, create a basic pathway based on training context
        if not inventory_summary:
            st.write("📝 No inventory provided, creating basic pathway...")
            pathway_name = f"{training_type} Pathway for {target_audience}"
            
            # Create a basic pathway structure
            basic_pathway = {
                "pathway_name": pathway_name,
                "sections": [
                    {
                        "title": "Introduction and Welcome",
                        "description": "Getting started with the organization and basic orientation",
                        "modules": [
                            {
                                "title": "Welcome and Introduction",
                                "description": "Overview of the organization and what to expect",
                                "content": f"Welcome to {training_type} for {target_audience}. This module provides an introduction to the organization and sets expectations for your learning journey."
                            },
                            {
                                "title": "Company Overview",
                                "description": "Understanding the organization's mission, values, and structure",
                                "content": f"Learn about the company's mission, values, and organizational structure. Understand how your role fits into the broader {industry} industry context."
                            }
                        ]
                    },
                    {
                        "title": "Essential Skills and Knowledge",
                        "description": "Core competencies and skills needed for success",
                        "modules": [
                            {
                                "title": "Role-Specific Training",
                                "description": "Training tailored to your specific role and responsibilities",
                                "content": f"Develop the essential skills and knowledge needed for your role as {target_audience}. This module covers role-specific training and competencies."
                            },
                            {
                                "title": "Tools and Systems",
                                "description": "Learning the tools, systems, and processes you'll use daily",
                                "content": "Familiarize yourself with the tools, systems, and processes you'll use in your daily work. This includes software, procedures, and best practices."
                            }
                        ]
                    },
                    {
                        "title": "Integration and Support",
                        "description": "Connecting with the team and available resources",
                        "modules": [
                            {
                                "title": "Team Integration",
                                "description": "Building relationships and understanding team dynamics",
                                "content": "Learn about your team structure, communication channels, and how to effectively collaborate with colleagues."
                            },
                            {
                                "title": "Resources and Support",
                                "description": "Knowing where to find help and additional resources",
                                "content": "Discover the resources, support systems, and contacts available to help you succeed in your role."
                            }
                        ]
                    }
                ]
            }
            
            st.write(f"✅ Created basic pathway with {len(basic_pathway['sections'])} sections")
            return basic_pathway
        
        # If there is inventory, use AI to create a pathway
        st.write("📝 Using AI to create pathway from inventory...")
        
        prompt = f"""
        Create a training pathway structure based on:
        
        Training Context:
        - Type: {training_type}
        - Target Audience: {target_audience}
        - Industry: {industry}
        
        Manual Inventory:
        {chr(10).join(inventory_summary) if inventory_summary else "No manual inventory provided"}
        
        Return as JSON:
        {{
            "pathway_name": "Descriptive pathway name",
            "sections": [
                {{
                    "title": "Section title",
                    "description": "Brief section description",
                    "modules": [
                        {{
                            "title": "Module title",
                            "description": "Clear module description",
                            "content": "Detailed content or learning objectives for this module"
                        }}
                    ]
                }}
            ]
        }}
        """
        
        st.write("🤖 Calling AI for generic pathway...")
        response = model.generate_content(prompt)
        st.write(f"✅ AI response received: {len(response.text)} characters")
        
        raw = response.text.strip()
        
        # Clean up JSON response
        import json
        import re
        
        cleaned = clean_gemini_json(raw)
        
        st.write(f"🧹 Cleaned JSON: {cleaned[:500]}...")
        
        try:
            pathway_data = json.loads(cleaned)
            st.write(f"✅ Successfully parsed pathway data")
            return pathway_data
        except json.JSONDecodeError as e:
            st.write(f"❌ JSON decode error: {str(e)}")
            # Log the error
            try:
                with open('generic_pathway_error_log.txt', 'w') as f:
                    f.write(f"Generic Pathway JSON Error: {str(e)}\n")
                    f.write(f"Raw Response:\n{cleaned}\n")
            except:
                pass
            return None
            
    except Exception as e:
        st.warning(f"Could not create generic pathway: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None 

def extract_modules_from_file_content_fallback(filename, content, training_context, bypass_filtering=False):
    """
    Extract content from uploaded files that aligns with primary training goals.
    Uses semantic topic analysis to identify relevant content sections.
    """
    try:
        print(f"📄 **Extracting semantically relevant content from {filename}**")
        
        if not content or len(content.strip()) < 50:
            return []
        
        # Get training goals and success metrics for semantic analysis
        primary_goals = training_context.get('primary_goals', '')
        success_metrics = training_context.get('success_metrics', '')
        training_type = training_context.get('training_type', '')
        target_audience = training_context.get('target_audience', '')
        industry = training_context.get('industry', '')
        
        print(f"🎯 **Training Goals:** {primary_goals}")
        print(f"📊 **Success Metrics:** {success_metrics}")
        print(f"📋 **Training Type:** {training_type}")
        print(f"👥 **Target Audience:** {target_audience}")
        print(f"🏢 **Industry:** {industry}")
        
        # Extract training-relevant information directly from content
        training_info = extract_training_information_from_content(content, training_context)
        
        if not training_info:
            print(f"⚠️ No training-relevant information found in {filename}")
            return []
        
        print(f"📄 **Training Information Extracted:** {len(training_info)} sections")
        
        modules = []
        
        # Create modules from training-relevant information using cohesive approach
        for i, info_section in enumerate(training_info[:15]):  # Limit to 15 modules
            if len(info_section.strip()) > 100:  # Minimum length for quality
                # Use cohesive module creation approach
                cohesive_module = create_cohesive_module_content(info_section, training_context, i+1)
                
                if cohesive_module:
                    modules.append({
                        'title': cohesive_module['title'],
                        'description': cohesive_module['description'],
                        'content': cohesive_module['content'],
                        'source': f'Training information from {filename}',
                        'key_points': extract_key_points_from_content(info_section, training_context),
                        'relevance_score': 0.9,  # High relevance since it's filtered and cohesive
                        'full_reason': f'Cohesive training content focused on {cohesive_module["core_topic"]}'
                    })
        
        print(f"✅ Extracted {len(modules)} cohesive training modules from {filename}")
        return modules
        
    except Exception as e:
        print(f"⚠️ Training content extraction failed for {filename}: {str(e)}")
        return []

def extract_training_information_from_content(content, training_context):
    """
    Extract training-relevant information from content based on user's training goals
    """
    try:
        # Get training goals and keywords
        primary_goals = training_context.get('primary_goals', '').lower()
        training_type = training_context.get('training_type', '').lower()
        industry = training_context.get('industry', '').lower()
        
        # Create goal-specific keywords
        goal_keywords = []
        
        # Extract keywords from training goals
        if primary_goals:
            goal_words = [word for word in primary_goals.split() if len(word) >= 3]
            goal_keywords.extend(goal_words)
        
        # Add training type specific keywords
        if 'process' in training_type:
            goal_keywords.extend(['process', 'procedure', 'workflow', 'step', 'sequence', 'method', 'system'])
        elif 'safety' in training_type:
            goal_keywords.extend(['safety', 'ppe', 'protective', 'emergency', 'hazard', 'risk', 'compliance'])
        elif 'quality' in training_type:
            goal_keywords.extend(['quality', 'inspection', 'standard', 'specification', 'verification', 'testing'])
        elif 'technical' in training_type:
            goal_keywords.extend(['technical', 'equipment', 'tool', 'operation', 'maintenance', 'calibration'])
        
        # Add industry-specific keywords
        if 'construction' in industry:
            goal_keywords.extend(['construction', 'fabrication', 'assembly', 'welding', 'cutting', 'material'])
        elif 'manufacturing' in industry:
            goal_keywords.extend(['manufacturing', 'production', 'assembly', 'quality', 'inspection'])
        
        # Add general training keywords
        general_keywords = [
            'training', 'learning', 'skill', 'knowledge', 'competency',
            'procedure', 'process', 'workflow', 'system', 'method',
            'safety', 'quality', 'compliance', 'standard', 'specification',
            'equipment', 'tool', 'material', 'operation', 'maintenance',
            'inspection', 'verification', 'testing', 'documentation', 'record'
        ]
        goal_keywords.extend(general_keywords)
        
        # Remove duplicates
        goal_keywords = list(set(goal_keywords))
        
        print(f"🎯 **Goal-Specific Keywords:** {goal_keywords[:10]}...")
        
        # Split content into sentences and filter for training-relevant information
        sentences = re.split(r'[.!?]+', content)
        training_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 40:  # Increased minimum length for better quality
                continue
                
            # Skip conversational sentences
            if any(conv in sentence.lower() for conv in [
                'yeah', 'okay', 'um', 'uh', 'oh', 'right', 'so', 'well', 'you know',
                'excuse me', 'hang on', 'wait', 'sorry', 'hello', 'goodbye',
                'thank you', 'thanks', 'bye', 'see you', 'talk to you later',
                'can you hear me', 'do you get it', 'is that working',
                'you\'re a bit lagging', 'i think we can hear you',
                'backgrounds', 'filters', 'appearance', 'interesting to learn'
            ]):
                continue
            
            # Skip speaker names and timestamps
            if re.match(r'^\w+:\s*$', sentence) or re.match(r'^\d+:\d+\s*-\s*\w+', sentence):
                continue
            
            # Skip fragmented or repetitive sentences
            words = sentence.split()
            if len(words) < 6:  # Too short
                continue
            if len(set(words)) < len(words) * 0.6:  # Too repetitive
                continue
            
            # Check if sentence contains training-relevant keywords
            sentence_lower = sentence.lower()
            keyword_matches = sum(1 for keyword in goal_keywords if keyword in sentence_lower)
            
            # Only include sentences with meaningful training content
            if keyword_matches >= 2 or (len(sentence) > 100 and keyword_matches >= 1):
                # Clean up the sentence
                cleaned_sentence = re.sub(r'^\w+:\s*', '', sentence)  # Remove speaker prefixes
                cleaned_sentence = cleaned_sentence.strip()
                
                if len(cleaned_sentence) > 30:
                    training_sentences.append(cleaned_sentence)
        
        # Group related sentences into training sections
        training_sections = []
        current_section = []
        
        for sentence in training_sentences:
            if len(current_section) < 3:  # Reduced to 3 for better cohesion
                current_section.append(sentence)
            else:
                if current_section:
                    section_text = '. '.join(current_section) + '.'
                    # Only add sections that are substantial
                    if len(section_text) > 100:
                        training_sections.append(section_text)
                current_section = [sentence]
        
        # Add the last section
        if current_section:
            section_text = '. '.join(current_section) + '.'
            if len(section_text) > 100:
                training_sections.append(section_text)
        
        return training_sections
        
    except Exception as e:
        print(f"⚠️ Training information extraction failed: {str(e)}")
        return []

def create_cohesive_module_content(content, training_context, module_number):
    """
    Create cohesive title, description, and content that work together as a unit
    Transforms conversational content into professional training material
    """
    try:
        # First, validate that the content is actually meaningful
        if not is_meaningful_training_content(content, training_context):
            return None
        
        # Extract the core topic from content
        core_topic = extract_core_topic(content, training_context)
        
        # Create cohesive title
        title = create_cohesive_title(content, core_topic, training_context, module_number)
        
        # Create cohesive description
        description = create_cohesive_description(content, core_topic, training_context)
        
        # Transform conversational content into professional training content
        professional_content = transform_conversational_to_professional(content, core_topic, training_context)
        
        return {
            'title': title,
            'description': description,
            'content': professional_content,
            'core_topic': core_topic
        }
        
    except Exception as e:
        print(f"⚠️ Cohesive module creation failed: {str(e)}")
        return None

def is_meaningful_training_content(content, training_context):
    """
    Validate that content is meaningful training content
    More lenient to preserve actual file content
    """
    try:
        content_lower = content.lower()
        
        # Check for conversational indicators
        conversational_indicators = [
            'yeah', 'okay', 'um', 'uh', 'oh', 'right', 'so', 'well', 'you know',
            'excuse me', 'hang on', 'wait', 'sorry', 'hello', 'goodbye',
            'thank you', 'thanks', 'bye', 'see you', 'talk to you later',
            'can you hear me', 'do you get it', 'is that working',
            'you\'re a bit lagging', 'i think we can hear you',
            'backgrounds', 'filters', 'appearance', 'interesting to learn'
        ]
        
        conv_count = sum(1 for indicator in conversational_indicators if indicator in content_lower)
        
        # More lenient validation to preserve actual file content
        
        # Only reject if content is clearly conversational
        if conv_count >= 5:  # Increased threshold
            return False
        
        # Accept content if it's substantial
        if len(content) < 50:  # Reduced minimum length
            return False
        
        # Check for training keywords (more lenient)
        training_keywords = get_training_keywords(training_context)
        keyword_matches = sum(1 for keyword in training_keywords if keyword in content_lower)
        
        # Accept if it has keywords OR is substantial content
        if keyword_matches < 1 and len(content) < 200:  # More lenient
            return False
        
        # Check for meaningful structure (more lenient)
        sentences = content.split('.')
        meaningful_sentences = 0
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and not any(conv in sentence.lower() for conv in conversational_indicators):
                meaningful_sentences += 1
        
        # Accept if it has meaningful sentences OR is substantial content
        return meaningful_sentences >= 1 or len(content) > 150
        
    except Exception as e:
        # If validation fails, accept the content to preserve file content
        return True

def extract_core_topic(content, training_context):
    """
    Extract the core topic from content for cohesive module creation
    """
    try:
        content_lower = content.lower()
        training_type = training_context.get('training_type', '').lower()
        
        # Define topic categories
        topics = {
            'safety': ['safety', 'ppe', 'protective', 'emergency', 'hazard', 'risk'],
            'quality': ['quality', 'inspection', 'standard', 'specification', 'verification'],
            'process': ['process', 'procedure', 'workflow', 'step', 'sequence', 'method'],
            'equipment': ['equipment', 'tool', 'operation', 'maintenance', 'calibration'],
            'material': ['material', 'fabrication', 'assembly', 'welding', 'cutting'],
            'documentation': ['documentation', 'record', 'report', 'form', 'checklist']
        }
        
        # Find the most prominent topic
        topic_scores = {}
        for topic, keywords in topics.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            topic_scores[topic] = score
        
        # Get the topic with highest score
        if topic_scores:
            primary_topic = max(topic_scores, key=topic_scores.get)
            if topic_scores[primary_topic] > 0:
                return primary_topic
        
        # Fallback based on training type
        if 'safety' in training_type:
            return 'safety'
        elif 'quality' in training_type:
            return 'quality'
        elif 'process' in training_type:
            return 'process'
        else:
            return 'general'
            
    except Exception as e:
        return 'general'

def create_cohesive_title(content, core_topic, training_context, module_number):
    """
    Create a cohesive title that reflects the core topic and content
    """
    try:
        import hashlib
        training_type = training_context.get('training_type', 'Training')
        target_audience = training_context.get('target_audience', 'employees')
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Create topic-specific titles
        topic_titles = {
            'safety': f"Safety Procedures for {target_audience.title()}",
            'quality': f"Quality Control and Inspection",
            'process': f"Process and Workflow Management",
            'equipment': f"Equipment Operation and Maintenance",
            'material': f"Material Handling and Fabrication",
            'documentation': f"Documentation and Record Keeping"
        }
        
        base_title = topic_titles.get(core_topic, f"{training_type} Procedures")
        
        # Add specific identifier
        specific_identifier = extract_specific_identifier(content)
        if specific_identifier:
            title = f"{base_title}: {specific_identifier}"
        else:
            title = f"{base_title} - Module {module_number}"
        
        # Add hash for uniqueness
        return f"{title} [{content_hash[:4]}]"
        
    except Exception as e:
        return f"Training Module {module_number}"

def create_cohesive_description(content, core_topic, training_context):
    """
    Create a cohesive description that matches the title and content, making each module unique
    """
    try:
        import hashlib
        target_audience = training_context.get('target_audience', 'employees')
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Extract specific content details for uniqueness
        specific_phrases = extract_specific_phrases_from_content(content)
        specific_procedures = extract_specific_procedures(content)
        meaningful_snippet = extract_meaningful_content_snippet(content)
        
        # Create content-specific description approaches
        description_approaches = []
        
        # Approach 1: Use specific procedures if available
        if specific_procedures:
            procedure_desc = f"Focuses on {specific_procedures[0]} procedures"
            if meaningful_snippet:
                procedure_desc += f". Example: {meaningful_snippet[:60]}..."
            description_approaches.append(procedure_desc)
        
        # Approach 2: Use specific phrases if available
        if specific_phrases:
            phrase_desc = f"Covers {specific_phrases[0]} techniques and methods"
            if len(specific_phrases) > 1:
                phrase_desc += f" including {specific_phrases[1]}"
            description_approaches.append(phrase_desc)
        
        # Approach 3: Use meaningful snippet with context
        if meaningful_snippet and len(meaningful_snippet) > 30:
            snippet_desc = f"Addresses {meaningful_snippet[:80]}..."
            description_approaches.append(snippet_desc)
        
        # Approach 4: Use core topic with specific content details
        topic_descriptions = {
            'safety': f"Essential safety procedures for {target_audience}",
            'quality': f"Quality control and inspection processes",
            'process': f"Workflow management and process optimization",
            'equipment': f"Equipment operation and maintenance procedures",
            'material': f"Material handling and fabrication techniques",
            'documentation': f"Documentation and record keeping procedures"
        }
        
        base_topic_desc = topic_descriptions.get(core_topic, f"Training content for {target_audience}")
        
        # Add specific content details to base topic
        if specific_phrases:
            topic_desc = f"{base_topic_desc} with focus on {specific_phrases[0]}"
        elif specific_procedures:
            topic_desc = f"{base_topic_desc} covering {specific_procedures[0]}"
        else:
            topic_desc = base_topic_desc
        
        description_approaches.append(topic_desc)
        
        # Approach 5: Use content length and complexity indicators
        content_words = content.split()
        if len(content_words) > 100:
            complexity_desc = f"Comprehensive training covering multiple aspects of {core_topic} procedures"
        elif len(content_words) > 50:
            complexity_desc = f"Focused training on key {core_topic} procedures"
        else:
            complexity_desc = f"Essential {core_topic} training for {target_audience}"
        
        description_approaches.append(complexity_desc)
        
        # Select the best approach based on content hash for variety
        approach_index = int(content_hash[:2], 16) % len(description_approaches)
        selected_description = description_approaches[approach_index]
        
        # Add unique identifier to ensure uniqueness
        unique_suffix = f" [{content_hash[:4]}]"
        
        return f"{selected_description}{unique_suffix}"
        
    except Exception as e:
        return f"Training content for {training_context.get('target_audience', 'employees')}."

def create_cohesive_content_structure(content, core_topic, training_context):
    """
    Create cohesive content structure that matches the title and description
    """
    try:
        training_type = training_context.get('training_type', 'Training')
        target_audience = training_context.get('target_audience', 'employees')
        
        # Create topic-specific headers
        topic_headers = {
            'safety': f"Safety Procedures for {target_audience.title()}",
            'quality': "Quality Control and Inspection Procedures",
            'process': "Process and Workflow Management",
            'equipment': "Equipment Operation and Maintenance",
            'material': "Material Handling and Fabrication",
            'documentation': "Documentation and Record Keeping"
        }
        
        header = topic_headers.get(core_topic, f"{training_type} Information")
        
        # Extract key learning points
        key_points = extract_key_learning_points(content, core_topic)
        
        # Structure the content
        structured_content = f"{header}\n"
        structured_content += f"Training Type: {training_type}\n"
        structured_content += f"Target Audience: {target_audience}\n"
        structured_content += "=" * 50 + "\n\n"
        
        # Add main content
        structured_content += f"Content:\n{content}\n\n"
        
        # Add key learning points
        if key_points:
            structured_content += "Key Learning Points:\n"
            for i, point in enumerate(key_points[:4], 1):
                structured_content += f"{i}. {point}\n"
            structured_content += "\n"
        
        # Add practical application
        practical_section = create_practical_application_section(core_topic, training_context)
        structured_content += practical_section
        
        return structured_content
        
    except Exception as e:
        return content

def transform_conversational_to_professional(content, core_topic, training_context):
    """
    Transform conversational content into professional training material using AI
    """
    try:
        import google.generativeai as genai
        from modules.config import api_key
        
        if not api_key or api_key == "your_gemini_api_key_here":
            # Fallback to basic transformation if no API key
            return transform_conversational_basic(content, core_topic, training_context)
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Create AI prompt for professional transformation
        training_type = training_context.get('training_type', 'Process Training')
        target_audience = training_context.get('target_audience', 'fabricators')
        industry = training_context.get('industry', 'manufacturing')
        primary_goals = training_context.get('primary_goals', '')
        
        prompt = f"""
Transform this conversational content into professional training material for {target_audience} in {industry}.

**Training Context:**
- Training Type: {training_type}
- Target Audience: {target_audience}
- Industry: {industry}
- Primary Goals: {primary_goals}
- Core Topic: {core_topic}

**Conversational Content:**
{content}

**Requirements:**
1. Create a professional "Module Overview" section
2. Transform conversational language into clear, instructional content
3. Maintain all technical information and procedures
4. Use professional training language
5. Include learning objectives
6. Make it engaging and educational

**Format:**
Module Overview: [Professional Title]

In this module, we'll focus on [topic] and its importance in [industry].

[Transformed content with clear explanations]

[Learning objectives and practical applications]

This training is essential for [purpose] and helps ensure [benefits].
"""
        
        # Generate professional content using AI
        response = model.generate_content(prompt)
        professional_content = response.text.strip()
        
        # If AI fails or returns empty content, fallback to basic transformation
        if not professional_content or len(professional_content) < 100:
            return transform_conversational_basic(content, core_topic, training_context)
        
        return professional_content
        
    except Exception as e:
        print(f"AI transformation failed: {str(e)}")
        # Fallback to basic transformation
        return transform_conversational_basic(content, core_topic, training_context)

def transform_conversational_basic(content, core_topic, training_context):
    """
    Basic transformation when AI is not available
    """
    try:
        import re
        
        # Clean up conversational elements
        content_clean = content.strip()
        
        # Remove conversational fillers and informal language
        conversational_patterns = [
            r'\b(um|uh|oh|yeah|okay|right|so|well|you know|excuse me|hang on|wait|sorry)\b',
            r'\b(hello|goodbye|thank you|thanks|bye|see you|talk to you later)\b',
            r'\b(can you hear me|do you get it|is that working|you\'re a bit lagging)\b',
            r'\b(i think we can hear you|backgrounds|filters|appearance)\b',
            r'\b(interesting to learn about it)\b',
            r'\b(that\'s the truss|but it hasn\'t got the zigzags in yet)\b',
            r'\b(if you go to|if you go if they\'re near)\b',
            r'\b(and what they do is they make)\b',
            r'\b(this is the biggest bridge we make)\b',
            r'\b(and the advantage of this is that)\b',
            r'\b(could you repeat that one more time)\b',
            r'\b(your question)\b',
            r'\b(what you just showed me)\b',
            r'\b(because what we can do)\b',
            r'\b(come up with the workflow)\b',
            r'\b(how you can film everything)\b'
        ]
        
        for pattern in conversational_patterns:
            content_clean = re.sub(pattern, '', content_clean, flags=re.IGNORECASE)
        
        # Clean up extra whitespace and punctuation
        content_clean = re.sub(r'\s+', ' ', content_clean)
        content_clean = re.sub(r'[.!?]+', '.', content_clean)
        content_clean = content_clean.strip()
        
        # If content is too short after cleaning, use AI to generate professional content
        if len(content_clean) < 100:
            return generate_professional_content_from_topic(core_topic, training_context)
        
        # Transform the cleaned content into professional training language
        training_type = training_context.get('training_type', 'Process Training')
        target_audience = training_context.get('target_audience', 'fabricators')
        industry = training_context.get('industry', 'manufacturing')
        
        professional_content = f"""
Module Overview: {core_topic.title()} in {industry.title()}

In this module, we'll focus on {core_topic.lower()} and its importance in {industry} processes.

{content_clean}

This training is essential for {training_type.lower()} and helps ensure proper {core_topic.lower()} procedures are followed by {target_audience} in {industry} environments.
"""
        
        return professional_content.strip()
        
    except Exception as e:
        # Fallback to generating professional content from topic
        return generate_professional_content_from_topic(core_topic, training_context)

def extract_process_elements_from_content(content):
    """
    Extract process elements from content for professional training
    """
    try:
        import re
        
        # Look for process-related content
        process_patterns = [
            r'\b(truss|deck|abutment|assembly|components?|workflow)\b',
            r'\b(fabrication|welding|cutting|inspection|testing)\b',
            r'\b(material|steel|bridge|construction)\b'
        ]
        
        found_elements = []
        for pattern in process_patterns:
            matches = re.findall(pattern, content, flags=re.IGNORECASE)
            found_elements.extend(matches)
        
        if found_elements:
            unique_elements = list(set(found_elements))
            return f"The {core_topic.lower()} process involves {', '.join(unique_elements[:3])} procedures."
        
        return None
        
    except Exception as e:
        return None

def extract_first_step(content):
    """Extract the first step from content"""
    try:
        sentences = content.split('.')
        for sentence in sentences:
            if any(word in sentence.lower() for word in ['first', 'start', 'begin', 'truss', 'component']):
                return sentence.strip()
        return "Begin the assembly process"
    except:
        return "Begin the assembly process"

def extract_second_step(content):
    """Extract the second step from content"""
    try:
        sentences = content.split('.')
        for sentence in sentences:
            if any(word in sentence.lower() for word in ['then', 'next', 'deck', 'abutment']):
                return sentence.strip()
        return "Continue with the next phase"
    except:
        return "Continue with the next phase"

def extract_final_step(content):
    """Extract the final step from content"""
    try:
        sentences = content.split('.')
        for sentence in sentences:
            if any(word in sentence.lower() for word in ['final', 'complete', 'finish', 'workflow']):
                return sentence.strip()
        return "Complete the process and verify quality"
    except:
        return "Complete the process and verify quality"

def generate_professional_content_from_topic(core_topic, training_context):
    """
    Generate professional training content from topic when conversational content is insufficient
    """
    try:
        training_type = training_context.get('training_type', 'Process Training')
        target_audience = training_context.get('target_audience', 'fabricators')
        industry = training_context.get('industry', 'manufacturing')
        
        professional_content = f"""
In this module, we'll walk through the {core_topic.lower()} process step-by-step.

**Overview:**
{core_topic} is a critical component of {training_type.lower()} in {industry}. This module provides comprehensive training for {target_audience} to understand and execute {core_topic.lower()} procedures effectively.

**Learning Objectives:**
- Understand the fundamentals of {core_topic.lower()}
- Learn proper procedures and best practices
- Identify potential challenges and solutions
- Apply knowledge in real-world scenarios

**Key Components:**
The {core_topic.lower()} process involves several key steps that must be followed in sequence to ensure quality and safety standards are met.
"""
        
        return professional_content.strip()
        
    except Exception as e:
        return f"Professional training content for {core_topic}."

def extract_specific_identifier(content):
    """
    Extract a specific identifier from content using AI-driven approach
    """
    try:
        # Use AI to identify the most relevant technical term
        technical_terms = extract_ai_driven_terminology(content, {}, "technical")
        if technical_terms:
            return technical_terms[0].title()
        
        # Fallback to basic extraction
        basic_terms = extract_basic_terminology(content, {}, "technical")
        if basic_terms:
            return basic_terms[0].title()
        
        return None
        
    except Exception as e:
        return None

def extract_key_learning_points(content, core_topic):
    """
    Extract key learning points based on core topic
    """
    try:
        content_lower = content.lower()
        key_points = []
        
        # Topic-specific learning points
        if core_topic == 'safety':
            if 'ppe' in content_lower:
                key_points.append("Proper PPE usage and requirements")
            if 'hazard' in content_lower:
                key_points.append("Hazard identification and assessment")
            if 'emergency' in content_lower:
                key_points.append("Emergency response procedures")
        
        elif core_topic == 'quality':
            if 'inspection' in content_lower:
                key_points.append("Inspection procedures and standards")
            if 'verification' in content_lower:
                key_points.append("Quality verification processes")
            if 'standard' in content_lower:
                key_points.append("Quality standards and specifications")
        
        elif core_topic == 'process':
            if 'workflow' in content_lower:
                key_points.append("Workflow optimization and management")
            if 'procedure' in content_lower:
                key_points.append("Standard operating procedures")
            if 'sequence' in content_lower:
                key_points.append("Process sequencing and timing")
        
        # Add general learning points
        if 'equipment' in content_lower:
            key_points.append("Equipment operation and maintenance")
        if 'material' in content_lower:
            key_points.append("Material handling and processing")
        if 'documentation' in content_lower:
            key_points.append("Documentation and record keeping")
        
        return key_points[:3]  # Limit to top 3
        
    except Exception as e:
        return []

def create_practical_application_section(core_topic, training_context):
    """
    Create practical application section based on core topic
    """
    try:
        target_audience = training_context.get('target_audience', 'employees')
        
        topic_applications = {
            'safety': f"""Practical Application:
• Always wear appropriate PPE as specified in procedures
• Conduct hazard assessments before starting work
• Report safety concerns immediately to supervisors
• Participate in safety training and drills regularly
• Follow emergency procedures without hesitation""",
            
            'quality': f"""Practical Application:
• Perform inspections according to established procedures
• Document all quality control activities accurately
• Report non-conformances immediately
• Follow quality standards consistently
• Participate in continuous improvement initiatives""",
            
            'process': f"""Practical Application:
• Follow standard operating procedures exactly
• Maintain workflow efficiency and organization
• Communicate process issues to team members
• Suggest process improvements when appropriate
• Document process changes and outcomes""",
            
            'equipment': f"""Practical Application:
• Perform equipment checks before operation
• Follow maintenance schedules strictly
• Report equipment issues immediately
• Use equipment only for intended purposes
• Keep equipment clean and properly stored""",
            
            'material': f"""Practical Application:
• Handle materials according to specifications
• Store materials in designated areas
• Follow material processing procedures
• Report material issues or shortages
• Maintain material traceability""",
            
            'documentation': f"""Practical Application:
• Complete all required documentation accurately
• Maintain organized record keeping systems
• Follow documentation procedures consistently
• Review and verify documentation regularly
• Ensure documentation is accessible to team members"""
        }
        
        return topic_applications.get(core_topic, f"""Practical Application:
• Apply learned concepts in daily work activities
• Follow established procedures and protocols
• Communicate effectively with team members
• Maintain high standards of work quality
• Continuously improve skills and knowledge""")
        
    except Exception as e:
        return "Practical Application: Apply learned concepts in daily work activities."

def extract_key_points_from_content(content, training_context):
    """
    Extract key learning points from content based on training goals
    """
    try:
        content_lower = content.lower()
        key_points = []
        
        # Look for specific training-related terms
        if any(word in content_lower for word in ['safety', 'ppe', 'protective']):
            key_points.extend(['Safety Procedures', 'Personal Protective Equipment', 'Hazard Identification'])
        if any(word in content_lower for word in ['quality', 'inspection', 'standard']):
            key_points.extend(['Quality Control', 'Inspection Procedures', 'Quality Standards'])
        if any(word in content_lower for word in ['process', 'procedure', 'workflow']):
            key_points.extend(['Process Procedures', 'Workflow Management', 'Process Optimization'])
        if any(word in content_lower for word in ['equipment', 'tool', 'operation']):
            key_points.extend(['Equipment Operation', 'Tool Usage', 'Maintenance Procedures'])
        if any(word in content_lower for word in ['material', 'handling', 'storage']):
            key_points.extend(['Material Handling', 'Storage Procedures', 'Transportation Safety'])
        if any(word in content_lower for word in ['documentation', 'record', 'report']):
            key_points.extend(['Documentation', 'Record Keeping', 'Reporting Procedures'])
        
        # Remove duplicates and limit
        unique_points = list(set(key_points))
        return unique_points[:5]
        
    except Exception as e:
        return []

def create_basic_modules_from_content(filename, content, training_context):
    """
    Create basic modules from content when all other methods fail
    """
    try:
        st.write(f"🔄 **Creating basic modules from {filename}**")
        
        if not content or len(content.strip()) < 50:
            return []
        
        modules = []
        
        # Split content into sections
        sections = content.split('\n\n')
        
        for i, section in enumerate(sections[:6]):  # Limit to 6 modules
            if len(section.strip()) > 30:
                # Create a simple title from the first line
                lines = section.strip().split('\n')
                first_line = lines[0].strip()
                
                if len(first_line) > 10 and len(first_line) < 100:
                    title = first_line
                else:
                    title = f"Module {i+1} from {filename}"
                
                # Clean up title
                title = title.replace(':', '').replace('-', '').strip()
                if len(title) > 60:
                    title = title[:60] + "..."
                
                # Create a simple description
                description = f"Training content from {filename} - {title}"
                
                modules.append({
                    'title': title,
                    'description': description,
                    'content': section.strip(),
                    'source': f'Basic module from {filename}',
                    'key_points': []
                })
        
        st.write(f"🔄 Created {len(modules)} basic modules from {filename}")
        return modules
        
    except Exception as e:
        st.warning(f"Basic module creation failed for {filename}: {str(e)}")
        return []

def parallel_semantic_analysis(sections, training_goals, training_topics, max_workers=None):
    """
    Process multiple sections in parallel using multiple AI agents
    """
    config = get_parallel_config()
    if max_workers is None:
        max_workers = config['max_section_workers']
    
    # Use print instead of st.write for worker threads to avoid context issues
    print(f"🚀 **Starting parallel semantic analysis with {max_workers} agents**")
    
    # Prepare tasks for parallel processing
    tasks = []
    for i, section in enumerate(sections):
        if len(section.strip()) > 80:  # Higher threshold for quality
            tasks.append({
                'index': i,
                'section': section,
                'training_goals': training_goals,
                'training_topics': training_topics
            })
    
    print(f"📋 Processing {len(tasks)} sections in parallel...")
    print(f"⚡ **Progress: 0/{len(tasks)} sections completed**")
    
    # Process sections in parallel
    results = []
    
    def analyze_section(task):
        """Analyze a single section for relevance"""
        try:
            relevance_prompt = f"""
            Evaluate how relevant this content section is to the training goals.
            
            Training Goals: {task['training_goals']}
            Training Topics: {', '.join(task['training_topics'])}
            
            Content Section:
            {task['section'][:1000]}
            
            Rate the relevance from 0-10 and explain why:
            - 0-2: Not relevant to training goals (conversational, off-topic, or too generic)
            - 3-5: Somewhat relevant, could be useful but not directly related
            - 6-8: Relevant and valuable for training (contains specific procedures, skills, or knowledge)
            - 9-10: Highly relevant and essential for training (directly addresses training goals)
            
            Be strict about relevance. Only give high scores (6+) to content that directly relates to:
            - Specific procedures, processes, or workflows
            - Technical skills, equipment operation, or safety procedures
            - Quality standards, compliance requirements, or best practices
            - Management techniques, communication skills, or leadership
            - Industry-specific knowledge or operational procedures
            
            Return only: "Score: X, Reason: brief explanation"
            """
            
            response = model.generate_content(relevance_prompt)
            response_text = response.text.strip()
            
            # Extract score from response
            score_match = re.search(r'Score:\s*(\d+)', response_text)
            if score_match:
                relevance_score = int(score_match.group(1)) / 10.0
            else:
                relevance_score = 0.3  # Lower default score
            
            # Extract reason
            reason_match = re.search(r'Reason:\s*(.+)', response_text)
            reason = reason_match.group(1) if reason_match else "Semantic analysis"
            
            return {
                'index': task['index'],
                'section': task['section'],
                'relevance_score': relevance_score,
                'reason': reason,
                'success': True
            }
            
        except Exception as e:
            return {
                'index': task['index'],
                'section': task['section'],
                'relevance_score': 0.3,  # Lower default score
                'reason': f"Analysis failed: {str(e)}",
                'success': False
            }
    
    # Use ThreadPoolExecutor for parallel processing with timeout
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_task = {executor.submit(analyze_section, task): task for task in tasks}
        
        # Collect results as they complete
        completed = 0
        try:
            for future in concurrent.futures.as_completed(future_to_task, timeout=config['timeout_seconds']):
                try:
                    result = future.result(timeout=config['timeout_seconds'])
                    results.append(result)
                    completed += 1
                    
                    # Show progress using print instead of st.write
                    print(f"⚡ **Progress: {completed}/{len(tasks)} sections completed**")
                    
                    # Show individual results using print
                    if result['success']:
                        print(f"✅ Section {result['index']+1} (score: {result['relevance_score']:.1f}, reason: {result['reason'][:80]}...)")
                    else:
                        print(f"⚠️ Section {result['index']+1} failed: {result['reason']}")
                        
                except concurrent.futures.TimeoutError:
                    print(f"⚠️ Section analysis timed out")
                    # Add default result for timeout
                    task = future_to_task[future]
                    results.append({
                        'index': task['index'],
                        'section': task['section'],
                        'relevance_score': 0.3,  # Lower default score
                        'reason': 'Analysis timed out',
                        'success': False
                    })
        except concurrent.futures.TimeoutError:
            print(f"⚠️ Overall parallel analysis timed out after {config['timeout_seconds']} seconds")
            # Add default results for remaining tasks
            for future in future_to_task:
                if future not in [f for f, _ in future_to_task.items() if f.done()]:
                    task = future_to_task[future]
                    results.append({
                        'index': task['index'],
                        'section': task['section'],
                        'relevance_score': 0.3,  # Lower default score
                        'reason': 'Overall timeout',
                        'success': False
                    })
    
    print(f"✅ Parallel analysis completed: {len(results)} results processed")
    return results

def batch_topic_analysis(files_content, training_context, max_workers=2):
    """
    Analyze multiple files for topics in parallel
    """
    st.write(f"🚀 **Starting parallel topic analysis with {max_workers} agents**")
    
    def analyze_file_topics(file_data):
        """Analyze topics for a single file"""
        try:
            filename, content = file_data
            
            topic_analysis_prompt = f"""
            Analyze this file content and identify the main topics, themes, and subjects discussed.
            Focus on identifying topics that could be relevant for training purposes.
            
            File: {filename}
            Content:
            {content[:3000]}
            
            Return a list of 5-10 main topics or themes found in this content, separated by commas.
            Focus on practical, actionable topics that could be used for training.
            """
            
            response = model.generate_content(topic_analysis_prompt)
            file_topics = [topic.strip() for topic in response.text.split(',') if topic.strip()]
            
            return {
                'filename': filename,
                'topics': file_topics,
                'success': True
            }
            
        except Exception as e:
            return {
                'filename': filename,
                'topics': [],
                'success': False,
                'error': str(e)
            }
    
    # Process files in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(analyze_file_topics, file_data): file_data for file_data in files_content.items()}
        
        results = {}
        for future in concurrent.futures.as_completed(future_to_file):
            result = future.result()
            results[result['filename']] = result['topics']
            
            if result['success']:
                st.write(f"✅ {result['filename']}: {len(result['topics'])} topics identified")
            else:
                st.write(f"⚠️ {result['filename']}: Analysis failed")
    
    return results 

def preprocess_content_for_training(content, training_context):
    """
    Preprocess content to focus on training-relevant information and remove conversational noise
    """
    try:
        # Get training keywords dynamically from training goals and context
        training_keywords = []
        
        # Extract keywords from primary goals
        if training_context.get('primary_goals'):
            goals = training_context['primary_goals'].lower()
            # Extract meaningful words from goals (3+ characters, not common words)
            goal_words = [word for word in goals.split() if len(word) >= 3 and word not in ['the', 'and', 'for', 'with', 'that', 'this', 'will', 'need', 'want', 'must', 'should', 'have', 'been', 'from', 'into', 'during', 'until', 'against', 'among', 'through', 'throughout', 'toward', 'towards', 'within', 'without']]
            training_keywords.extend(goal_words)
        
        # Extract keywords from success metrics
        if training_context.get('success_metrics'):
            metrics = training_context['success_metrics'].lower()
            metric_words = [word for word in metrics.split() if len(word) >= 3 and word not in ['the', 'and', 'for', 'with', 'that', 'this', 'will', 'need', 'want', 'must', 'should', 'have', 'been', 'from', 'into', 'during', 'until', 'against', 'among', 'through', 'throughout', 'toward', 'towards', 'within', 'without']]
            training_keywords.extend(metric_words)
        
        # Extract keywords from training type
        if training_context.get('training_type'):
            training_type = training_context['training_type'].lower()
            type_words = [word for word in training_type.split() if len(word) >= 3]
            training_keywords.extend(type_words)
        
        # Extract keywords from industry
        if training_context.get('industry'):
            industry = training_context['industry'].lower()
            industry_words = [word for word in industry.split() if len(word) >= 3]
            training_keywords.extend(industry_words)
        
        # Extract keywords from target audience
        if training_context.get('target_audience'):
            audience = training_context['target_audience'].lower()
            audience_words = [word for word in audience.split() if len(word) >= 3]
            training_keywords.extend(audience_words)
        
        # Add general training-related keywords that apply to any industry
        general_training_keywords = [
            'process', 'procedure', 'training', 'learning', 'skill', 'knowledge', 
            'workflow', 'system', 'method', 'technique', 'practice', 'standard',
            'quality', 'safety', 'compliance', 'regulation', 'policy', 'guideline',
            'equipment', 'tool', 'material', 'resource', 'documentation', 'record',
            'inspection', 'verification', 'testing', 'assessment', 'evaluation',
            'communication', 'coordination', 'collaboration', 'teamwork', 'leadership',
            'management', 'supervision', 'mentoring', 'coaching', 'development',
            'operation', 'maintenance', 'installation', 'configuration', 'calibration',
            'assembly', 'fabrication', 'production', 'manufacturing', 'construction',
            'handling', 'storage', 'transportation', 'packaging', 'shipping',
            'customer', 'client', 'service', 'support', 'troubleshooting', 'repair'
        ]
        training_keywords.extend(general_training_keywords)
        
        # Remove duplicates and limit to most relevant
        training_keywords = list(set(training_keywords))[:25]  # Increased to 25 keywords
        
        print(f"🔍 **Dynamic Training Keywords:** {training_keywords}")
        
        # Split content into lines and filter relevant ones
        lines = content.split('\n')
        relevant_lines = []
        
        for line in lines:
            line = line.strip()
            if len(line) < 15:  # Higher threshold for quality content
                continue
                
            # Skip obvious conversational elements but be more lenient
            if any(skip in line.lower() for skip in [
                'yeah', 'okay', 'um', 'uh', 'oh', 'right', 'so', 'well', 'you know',
                'excuse me', 'hang on', 'wait', 'sorry', 'hello', 'goodbye',
                'can you hear me', 'do you get it', 'is that working',
                'meeting pin', 'dialed in', 'camera', 'sound', 'microphone',
                'thank you', 'thanks', 'bye', 'see you', 'talk to you later',
                'have a good day', 'have a good one', 'take care'
            ]):
                continue
            
            # Skip timestamp lines (e.g., "0:00 - Bruce Mullaney")
            if re.match(r'^\d+:\d+\s*-\s*\w+', line):
                continue
            
            # Skip speaker names alone (e.g., "Bruce:", "Sarah:")
            if re.match(r'^\w+:\s*$', line):
                continue
            
            # Skip very short responses
            if len(line) < 20 and any(word in line.lower() for word in ['yes', 'no', 'ok', 'sure', 'fine', 'good', 'bad']):
                continue
            
            # Keep lines that contain training-relevant keywords or are substantial
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in training_keywords) or len(line) > 30:  # Higher threshold
                relevant_lines.append(line)
        
        # Join relevant lines and create meaningful sections
        if relevant_lines:
            # Group consecutive relevant lines into sections
            sections = []
            current_section = []
            
            for line in relevant_lines:
                if len(current_section) < 6:  # Group up to 6 lines for better sections
                    current_section.append(line)
                else:
                    if current_section:
                        sections.append('\n'.join(current_section))
                    current_section = [line]
            
            # Add the last section
            if current_section:
                sections.append('\n'.join(current_section))
            
            # Filter sections for quality
            quality_sections = []
            for section in sections:
                # Only keep sections with substantial content
                if len(section.strip()) > 100:  # Higher threshold for quality
                    # Check if section contains training-relevant keywords
                    section_lower = section.lower()
                    keyword_count = sum(1 for keyword in training_keywords if keyword in section_lower)
                    if keyword_count >= 1 or len(section) > 200:  # Must have keywords or be substantial
                        quality_sections.append(section)
            
            # Limit to most relevant sections
            if len(quality_sections) > 20:  # Reduced for quality
                quality_sections = quality_sections[:20]
            
            return '\n\n'.join(quality_sections)
        else:
            # If no relevant content found, return a subset of the original
            return content[:3000]  # Reduced for quality
            
    except Exception as e:
        print(f"⚠️ Content preprocessing failed: {str(e)}")
        return content[:3000]  # Fallback to limited content

def create_quick_pathway(training_context, extracted_file_contents, file_inventory):
    """
    Create a pathway quickly without AI analysis for testing purposes
    """
    try:
        print("⚡ **Creating Quick Pathway (No AI Analysis)**")
        
        file_based_modules = []
        
        # Process files quickly without AI
        for filename, content in extracted_file_contents.items():
            if content and len(content.strip()) > 50:
                print(f"📄 Processing {filename} quickly...")
                
                # Preprocess content
                preprocessed_content = preprocess_content_for_training(content, training_context)
                
                # Create basic modules from preprocessed content
                modules = create_basic_modules_from_content(filename, preprocessed_content, training_context)
                file_based_modules.extend(modules)
                
                print(f"✅ Created {len(modules)} basic modules from {filename}")
        
        if file_based_modules:
            # Create a simple pathway structure
            pathway_name = f"{training_context.get('training_type', 'Training')} Pathway - {training_context.get('target_audience', 'Employee')} Onboarding"
            
            # Group modules into sections (max 3 sections for speed)
            sections = []
            modules_per_section = max(1, len(file_based_modules) // 3)
            
            for i in range(0, len(file_based_modules), modules_per_section):
                section_modules = file_based_modules[i:i + modules_per_section]
                section = {
                    "title": f"Section {len(sections) + 1}",
                    "description": f"Training content from uploaded files",
                    "modules": [{
                        "title": m['title'],
                        "description": m['description'],
                        "content": m['content'],
                        "source": m.get('source', 'File content')
                    } for m in section_modules]
                }
                sections.append(section)
            
            pathway = {
                "pathway_name": pathway_name,
                "sections": sections
            }
            
            print(f"✅ Quick pathway created with {len(sections)} sections and {len(file_based_modules)} modules")
            return {"pathways": [pathway]}
        else:
            # Create a basic pathway if no modules
            basic_pathway = {
                "pathway_name": f"{training_context.get('training_type', 'Training')} Pathway",
                "sections": [{
                    "title": "Basic Training",
                    "description": "Basic training content",
                    "modules": [{
                        "title": "Introduction",
                        "description": "Welcome to the training program",
                        "content": f"Welcome to {training_context.get('training_type', 'Training')} for {training_context.get('target_audience', 'employees')}.",
                        "source": "Quick pathway generation"
                    }]
                }]
            }
            return {"pathways": [basic_pathway]}
            
    except Exception as e:
        print(f"❌ Quick pathway creation failed: {str(e)}")
        return None 

def create_fallback_pathways(modules, training_context):
    """
    Create pathways without AI when rate limits are hit
    """
    try:
        print("🔄 **Creating Fallback Pathways (No AI)**")
        
        if not modules:
            return []
        
        # Get training goals to create themed pathways
        training_goals = training_context.get('primary_goals', '').lower()
        training_type = training_context.get('training_type', 'Training')
        target_audience = training_context.get('target_audience', 'Employee')
        
        # Create simple pathway structure
        pathway_name = f"{training_type} Pathway - {target_audience} Onboarding"
        
        # If we have few modules, create one section
        if len(modules) <= 3:
            pathway = {
                "pathway_name": pathway_name,
                "sections": [{
                    "title": "Training Content",
                    "description": "All extracted training content from uploaded files",
                    "modules": [{
                        "title": m['title'],
                        "description": m['description'],
                        "content": m['content'],
                        "source": m.get('source', 'File content')
                    } for m in modules]
                }]
            }
        else:
            # Create multiple pathways based on training goals
            pathways = []
            
            # Determine pathway themes based on training goals
            if 'workflow' in training_goals or 'process' in training_goals:
                # Create workflow-focused pathways
                workflow_modules = [m for m in modules if any(word in m['title'].lower() or any(word in m['content'].lower()) for word in ['workflow', 'process', 'procedure', 'step', 'sequence', 'method', 'system'])]
                safety_modules = [m for m in modules if any(word in m['title'].lower() or any(word in m['content'].lower()) for word in ['safety', 'ppe', 'protective', 'emergency', 'hazard', 'risk'])]
                quality_modules = [m for m in modules if any(word in m['title'].lower() or any(word in m['content'].lower()) for word in ['quality', 'inspection', 'standard', 'specification', 'verification'])]
                other_modules = [m for m in modules if m not in workflow_modules and m not in safety_modules and m not in quality_modules]
                
                if workflow_modules:
                    pathways.append({
                        "pathway_name": f"{training_type} - Workflow & Process Management",
                        "sections": [{
                            "title": "Process Fundamentals",
                            "description": "Core workflow and process training content",
                            "modules": [{
                                "title": m['title'],
                                "description": m['description'],
                                "content": m['content'],
                                "source": m.get('source', 'File content')
                            } for m in workflow_modules]
                        }]
                    })
                
                if safety_modules:
                    pathways.append({
                        "pathway_name": f"{training_type} - Safety & Compliance",
                        "sections": [{
                            "title": "Safety Procedures",
                            "description": "Essential safety training and compliance content",
                            "modules": [{
                                "title": m['title'],
                                "description": m['description'],
                                "content": m['content'],
                                "source": m.get('source', 'File content')
                            } for m in safety_modules]
                        }]
                    })
                
                if quality_modules:
                    pathways.append({
                        "pathway_name": f"{training_type} - Quality Assurance",
                        "sections": [{
                            "title": "Quality Standards",
                            "description": "Quality control and assurance procedures",
                            "modules": [{
                                "title": m['title'],
                                "description": m['description'],
                                "content": m['content'],
                                "source": m.get('source', 'File content')
                            } for m in quality_modules]
                        }]
                    })
                
                if other_modules:
                    pathways.append({
                        "pathway_name": f"{training_type} - Supporting Skills & Knowledge",
                        "sections": [{
                            "title": "Additional Training Content",
                            "description": "Supporting training content and procedures",
                            "modules": [{
                                "title": m['title'],
                                "description": m['description'],
                                "content": m['content'],
                                "source": m.get('source', 'File content')
                            } for m in other_modules]
                        }]
                    })
            
            elif 'safety' in training_goals:
                # Create safety-focused pathways
                safety_modules = [m for m in modules if any(word in m['title'].lower() or any(word in m['content'].lower()) for word in ['safety', 'ppe', 'protective', 'emergency', 'hazard', 'risk', 'compliance'])]
                operational_modules = [m for m in modules if any(word in m['title'].lower() or any(word in m['content'].lower()) for word in ['operation', 'procedure', 'workflow', 'process', 'equipment'])]
                quality_modules = [m for m in modules if any(word in m['title'].lower() or any(word in m['content'].lower()) for word in ['quality', 'inspection', 'standard', 'verification'])]
                other_modules = [m for m in modules if m not in safety_modules and m not in operational_modules and m not in quality_modules]
                
                if safety_modules:
                    pathways.append({
                        "pathway_name": f"{training_type} - Safety & Compliance",
                        "sections": [{
                            "title": "Safety Procedures",
                            "description": "Essential safety training and compliance content",
                            "modules": [{
                                "title": m['title'],
                                "description": m['description'],
                                "content": m['content'],
                                "source": m.get('source', 'File content')
                            } for m in safety_modules]
                        }]
                    })
                
                if operational_modules:
                    pathways.append({
                        "pathway_name": f"{training_type} - Operational Procedures",
                        "sections": [{
                            "title": "Operational Training",
                            "description": "Operational skills and procedures",
                            "modules": [{
                                "title": m['title'],
                                "description": m['description'],
                                "content": m['content'],
                                "source": m.get('source', 'File content')
                            } for m in operational_modules]
                        }]
                    })
                
                if quality_modules:
                    pathways.append({
                        "pathway_name": f"{training_type} - Quality & Standards",
                        "sections": [{
                            "title": "Quality Control",
                            "description": "Quality control and standards training",
                            "modules": [{
                                "title": m['title'],
                                "description": m['description'],
                                "content": m['content'],
                                "source": m.get('source', 'File content')
                            } for m in quality_modules]
                        }]
                    })
                
                if other_modules:
                    pathways.append({
                        "pathway_name": f"{training_type} - General Training",
                        "sections": [{
                            "title": "General Training",
                            "description": "General training content and procedures",
                            "modules": [{
                                "title": m['title'],
                                "description": m['description'],
                                "content": m['content'],
                                "source": m.get('source', 'File content')
                            } for m in other_modules]
                        }]
                    })
            
            elif 'quality' in training_goals:
                # Create quality-focused pathways
                quality_modules = [m for m in modules if any(word in m['title'].lower() or any(word in m['content'].lower()) for word in ['quality', 'inspection', 'standard', 'specification', 'verification', 'testing'])]
                operational_modules = [m for m in modules if any(word in m['title'].lower() or any(word in m['content'].lower()) for word in ['operation', 'procedure', 'workflow', 'process'])]
                safety_modules = [m for m in modules if any(word in m['title'].lower() or any(word in m['content'].lower()) for word in ['safety', 'ppe', 'protective', 'emergency'])]
                other_modules = [m for m in modules if m not in quality_modules and m not in operational_modules and m not in safety_modules]
                
                if quality_modules:
                    pathways.append({
                        "pathway_name": f"{training_type} - Quality Assurance",
                        "sections": [{
                            "title": "Quality Standards",
                            "description": "Quality control and assurance procedures",
                            "modules": [{
                                "title": m['title'],
                                "description": m['description'],
                                "content": m['content'],
                                "source": m.get('source', 'File content')
                            } for m in quality_modules]
                        }]
                    })
                
                if operational_modules:
                    pathways.append({
                        "pathway_name": f"{training_type} - Core Operations",
                        "sections": [{
                            "title": "Core Training",
                            "description": "Core operational training content",
                            "modules": [{
                                "title": m['title'],
                                "description": m['description'],
                                "content": m['content'],
                                "source": m.get('source', 'File content')
                            } for m in operational_modules]
                        }]
                    })
                
                if safety_modules:
                    pathways.append({
                        "pathway_name": f"{training_type} - Safety & Compliance",
                        "sections": [{
                            "title": "Safety Training",
                            "description": "Safety procedures and compliance training",
                            "modules": [{
                                "title": m['title'],
                                "description": m['description'],
                                "content": m['content'],
                                "source": m.get('source', 'File content')
                            } for m in safety_modules]
                        }]
                    })
                
                if other_modules:
                    pathways.append({
                        "pathway_name": f"{training_type} - Supporting Skills",
                        "sections": [{
                            "title": "Supporting Training",
                            "description": "Supporting skills and knowledge",
                            "modules": [{
                                "title": m['title'],
                                "description": m['description'],
                                "content": m['content'],
                                "source": m.get('source', 'File content')
                            } for m in other_modules]
                        }]
                    })
            
            elif 'communication' in training_goals or 'team' in training_goals:
                # Create communication-focused pathways
                comm_modules = [m for m in modules if any(word in m['title'].lower() or any(word in m['content'].lower()) for word in ['communication', 'team', 'collaboration', 'leadership', 'management'])]
                technical_modules = [m for m in modules if any(word in m['title'].lower() or any(word in m['content'].lower()) for word in ['technical', 'skill', 'procedure', 'process', 'equipment'])]
                safety_modules = [m for m in modules if any(word in m['title'].lower() or any(word in m['content'].lower()) for word in ['safety', 'ppe', 'protective', 'emergency'])]
                other_modules = [m for m in modules if m not in comm_modules and m not in technical_modules and m not in safety_modules]
                
                if comm_modules:
                    pathways.append({
                        "pathway_name": f"{training_type} - Communication & Leadership",
                        "sections": [{
                            "title": "Communication Skills",
                            "description": "Communication and leadership training content",
                            "modules": [{
                                "title": m['title'],
                                "description": m['description'],
                                "content": m['content'],
                                "source": m.get('source', 'File content')
                            } for m in comm_modules]
                        }]
                    })
                
                if technical_modules:
                    pathways.append({
                        "pathway_name": f"{training_type} - Technical Skills",
                        "sections": [{
                            "title": "Technical Training",
                            "description": "Technical skills and procedures",
                            "modules": [{
                                "title": m['title'],
                                "description": m['description'],
                                "content": m['content'],
                                "source": m.get('source', 'File content')
                            } for m in technical_modules]
                        }]
                    })
                
                if safety_modules:
                    pathways.append({
                        "pathway_name": f"{training_type} - Safety & Compliance",
                        "sections": [{
                            "title": "Safety Training",
                            "description": "Safety procedures and compliance training",
                            "modules": [{
                                "title": m['title'],
                                "description": m['description'],
                                "content": m['content'],
                                "source": m.get('source', 'File content')
                            } for m in safety_modules]
                        }]
                    })
                
                if other_modules:
                    pathways.append({
                        "pathway_name": f"{training_type} - General Training",
                        "sections": [{
                            "title": "General Training",
                            "description": "General training content and procedures",
                            "modules": [{
                                "title": m['title'],
                                "description": m['description'],
                                "content": m['content'],
                                "source": m.get('source', 'File content')
                            } for m in other_modules]
                        }]
                    })
            
            else:
                # Create general pathways with multiple sections
                sections = []
                modules_per_section = max(1, len(modules) // 5)  # 5 sections max
                
                for i in range(0, len(modules), modules_per_section):
                    section_modules = modules[i:i + modules_per_section]
                    section = {
                        "title": f"Section {len(sections) + 1}",
                        "description": f"Training content from uploaded files",
                        "modules": [{
                            "title": m['title'],
                            "description": m['description'],
                            "content": m['content'],
                            "source": m.get('source', 'File content')
                        } for m in section_modules]
                    }
                    sections.append(section)
                
                pathways.append({
                    "pathway_name": pathway_name,
                    "sections": sections
                })
            
            # If no pathways created, create a simple one
            if not pathways:
                pathways = [{
                    "pathway_name": pathway_name,
                    "sections": [{
                        "title": "Training Content",
                        "description": "All extracted training content from uploaded files",
                        "modules": [{
                            "title": m['title'],
                            "description": m['description'],
                            "content": m['content'],
                            "source": m.get('source', 'File content')
                        } for m in modules]
                    }]
                }]
        
        print(f"✅ Fallback pathway created with {len(pathways)} pathways and {len(modules)} total modules")
        return pathways
        
    except Exception as e:
        print(f"❌ Fallback pathway creation failed: {str(e)}")
        return []

def create_meaningful_title(section, filename, module_number):
    """
    Create a meaningful title from section content
    """
    try:
        # Try to extract a meaningful title from the content
        lines = section.split('\n')
        
        # Look for lines that could be titles
        for line in lines[:3]:  # Check first 3 lines
            line = line.strip()
            if len(line) > 10 and len(line) < 80:
                # Check if it looks like a title
                if not any(skip in line.lower() for skip in ['yeah', 'okay', 'um', 'uh', 'oh', 'right', 'so', 'well']):
                    # Clean up the title
                    title = line.replace(':', '').replace('-', '').replace('*', '').strip()
                    if len(title) > 5:
                        return title
        
        # If no good title found, create one based on content
        words = section.split()[:6]
        if words:
            title = ' '.join(words).replace(':', '').replace('-', '').strip()
            if len(title) > 10:
                return title[:60] + "..." if len(title) > 60 else title
        
        # Fallback title
        return f"Training Module {module_number} from {filename}"
        
    except Exception as e:
        return f"Training Module {module_number} from {filename}"

def create_meaningful_description(section, filename, training_context, matched_topics):
    """
    Create a meaningful description for the module that's comprehensive and user-friendly
    """
    try:
        # Extract key concepts from the content
        key_concepts = extract_key_concepts(section)
        
        # Get training context for better descriptions
        training_type = training_context.get('training_type', 'Training')
        target_audience = training_context.get('target_audience', 'employees')
        primary_goals = training_context.get('primary_goals', 'workplace skills')
        
        # Create a structured, comprehensive description
        description_parts = []
        
        # Start with what the learner will learn
        if key_concepts:
            description_parts.append(f"This module covers: {', '.join(key_concepts[:3])}")
        
        # Add context based on training type
        if training_type == 'Process Training':
            description_parts.append("Essential process knowledge and procedures for daily operations")
        elif training_type == 'Safety Training':
            description_parts.append("Critical safety information and compliance requirements")
        elif training_type == 'Technical Training':
            description_parts.append("Technical skills and specialized procedures")
        elif training_type == 'Compliance Training':
            description_parts.append("Regulatory compliance and policy requirements")
        elif training_type == 'Leadership Training':
            description_parts.append("Leadership skills and management techniques")
        else:
            description_parts.append("Important training content relevant to your role")
        
        # Add audience-specific context
        if 'manager' in target_audience.lower() or 'supervisor' in target_audience.lower():
            description_parts.append("Includes supervisory responsibilities and team management")
        elif 'new' in target_audience.lower() or 'employee' in target_audience.lower():
            description_parts.append("Essential knowledge for new team members")
        
        # Add relevance to training goals
        if matched_topics and matched_topics[0] != 'bypass_filtering':
            description_parts.append(f"Directly supports: {matched_topics[0]}")
        
        # Combine into a comprehensive description
        if description_parts:
            description = ". ".join(description_parts) + "."
            # Ensure it's not too long
            if len(description) > 300:
                description = description[:297] + "..."
            return description
        else:
            return f"Training content from {filename} that supports {primary_goals} for {target_audience}."
            
    except Exception as e:
        return f"Training content from {filename} relevant to workplace skills."

def create_meaningful_content(section, training_context):
    """
    Create meaningful, structured content from raw section text that focuses on actual training information
    """
    try:
        # Clean up the content and extract actual training information
        content = section.strip()
        
        # Remove conversational elements but keep the substance
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if len(line) < 15:  # Higher threshold for quality content
                continue
                
            # Skip obvious conversational elements
            if any(skip in line.lower() for skip in [
                'yeah', 'okay', 'um', 'uh', 'oh', 'right', 'so', 'well', 'you know',
                'excuse me', 'hang on', 'wait', 'sorry', 'hello', 'goodbye',
                'can you hear me', 'do you get it', 'is that working',
                'meeting pin', 'dialed in', 'camera', 'sound', 'microphone',
                'thank you', 'thanks', 'bye', 'see you', 'talk to you later',
                'have a good day', 'have a good one', 'take care'
            ]):
                continue
            
            # Skip timestamp lines
            if re.match(r'^\d+:\d+\s*-\s*\w+', line):
                continue
            
            # Skip speaker names alone (e.g., "Bruce:", "Sarah:")
            if re.match(r'^\w+:\s*$', line):
                continue
            
            # Skip very short responses
            if len(line) < 25 and any(word in line.lower() for word in ['yes', 'no', 'ok', 'sure', 'fine', 'good', 'bad']):
                continue
            
            # Clean up speaker prefixes but keep the content
            if re.match(r'^\w+:\s*', line):
                # Remove speaker name but keep the content
                line = re.sub(r'^\w+:\s*', '', line)
            
            # Keep substantial lines that contain actual information
            if len(line) > 20:
                cleaned_lines.append(line)
        
        if cleaned_lines:
            # Join lines and create structured content
            structured_content = '\n\n'.join(cleaned_lines)
            
            # Extract actual training information from the content
            training_info = extract_training_information(structured_content, training_context)
            
            # Add context based on training type
            training_type = training_context.get('training_type', 'Training')
            target_audience = training_context.get('target_audience', 'employees')
            
            # Create a comprehensive, structured format
            header = f"Training Content for {target_audience.title()}\n"
            header += f"Training Type: {training_type}\n"
            header += "=" * 50 + "\n\n"
            
            # Add section-specific context
            if training_type == 'Process Training':
                structured_content = f"{header}Process Information:\n{training_info}"
            elif training_type == 'Safety Training':
                structured_content = f"{header}Safety Procedures:\n{training_info}"
            elif training_type == 'Technical Training':
                structured_content = f"{header}Technical Information:\n{training_info}"
            elif training_type == 'Compliance Training':
                structured_content = f"{header}Compliance Requirements:\n{training_info}"
            elif training_type == 'Leadership Training':
                structured_content = f"{header}Leadership Skills:\n{training_info}"
            else:
                structured_content = f"{header}Training Information:\n{training_info}"
            
            # Add key learning points
            key_concepts = extract_key_concepts(training_info)
            if key_concepts:
                structured_content += f"\n\nKey Learning Points:\n"
                for i, concept in enumerate(key_concepts[:6], 1):  # Increased to 6 points
                    structured_content += f"{i}. {concept}\n"
            
            # Add practical application section
            structured_content += f"\nPractical Application:\n"
            structured_content += f"• Review this information carefully and take notes\n"
            structured_content += f"• Identify how these procedures apply to your daily work\n"
            structured_content += f"• Practice these skills in a safe environment\n"
            structured_content += f"• Discuss any questions with your supervisor or trainer\n"
            structured_content += f"• Document your understanding and any areas needing clarification\n"
            
            # Limit content length but keep it substantial
            if len(structured_content) > 3000:
                words = structured_content.split()
                if len(words) > 500:
                    # Keep the header and first part, then truncate
                    header_end = structured_content.find("=" * 50) + 50
                    main_content = structured_content[header_end:].strip()
                    words = main_content.split()
                    if len(words) > 400:
                        main_content = " ".join(words[:400]) + "..."
                    structured_content = structured_content[:header_end] + "\n\n" + main_content
            
            return structured_content
        else:
            # If no good content found, return a minimal version
            return f"Training content: {content[:500]}..." if len(content) > 500 else content
            
    except Exception as e:
        return section[:1200] + "..." if len(section) > 1200 else section

def extract_training_information(content, training_context):
    """
    Extract actual training information from content, removing conversational elements
    """
    try:
        # Split content into sentences
        sentences = re.split(r'[.!?]+', content)
        training_sentences = []
        
        # Get training keywords for filtering
        training_keywords = get_training_keywords(training_context)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue
                
            # Skip conversational sentences
            if any(conv in sentence.lower() for conv in [
                'yeah', 'okay', 'um', 'uh', 'oh', 'right', 'so', 'well', 'you know',
                'excuse me', 'hang on', 'wait', 'sorry', 'hello', 'goodbye',
                'thank you', 'thanks', 'bye', 'see you', 'talk to you later'
            ]):
                continue
            
            # Keep sentences that contain training-relevant information
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in training_keywords) or len(sentence) > 50:
                # Clean up the sentence
                cleaned_sentence = re.sub(r'^\w+:\s*', '', sentence)  # Remove speaker prefixes
                cleaned_sentence = cleaned_sentence.strip()
                
                if len(cleaned_sentence) > 15:
                    training_sentences.append(cleaned_sentence)
        
        # Join sentences into coherent paragraphs
        if training_sentences:
            # Group related sentences
            paragraphs = []
            current_paragraph = []
            
            for sentence in training_sentences:
                if len(current_paragraph) < 3:  # Group up to 3 sentences
                    current_paragraph.append(sentence)
                else:
                    if current_paragraph:
                        paragraphs.append('. '.join(current_paragraph) + '.')
                    current_paragraph = [sentence]
            
            # Add the last paragraph
            if current_paragraph:
                paragraphs.append('. '.join(current_paragraph) + '.')
            
            return '\n\n'.join(paragraphs)
        else:
            # If no training sentences found, return cleaned content
            return content
            
    except Exception as e:
        return content

def get_training_keywords(training_context):
    """
    Get training-relevant keywords using AI-driven approach
    """
    try:
        # Create a sample content from training context
        context_content = f"""
        Training goals: {training_context.get('primary_goals', '')}
        Training type: {training_context.get('training_type', '')}
        Target audience: {training_context.get('target_audience', '')}
        Industry: {training_context.get('industry', '')}
        Success metrics: {training_context.get('success_metrics', '')}
        """
        
        # Use AI to extract relevant keywords
        keywords = extract_ai_driven_terminology(context_content, training_context, "all")
        if keywords:
            return keywords[:30]
        
        # Fallback to basic extraction
        return extract_basic_terminology(context_content, training_context, "all")[:30]
        
    except Exception as e:
        # Ultimate fallback
        return [
            'process', 'procedure', 'workflow', 'system', 'method', 'technique',
            'quality', 'safety', 'compliance', 'standard', 'specification',
            'inspection', 'testing', 'verification', 'documentation', 'record',
            'equipment', 'tool', 'material', 'resource', 'maintenance',
            'operation', 'installation', 'configuration', 'calibration',
            'training', 'learning', 'skill', 'knowledge', 'competency'
        ]

def extract_key_concepts(content):
    """
    Extract key concepts from content using AI-driven approach
    """
    try:
        # Use AI to extract concepts if available
        concepts = extract_ai_driven_terminology(content, {}, "technical")
        if concepts:
            return concepts[:5]
        
        # Fallback to basic extraction
        return extract_basic_terminology(content, {}, "technical")[:5]
        
    except Exception as e:
        return []

def extract_specific_phrases_from_content(content):
    """
    Extract specific phrases from content using AI-driven approach
    """
    try:
        # Use AI to extract relevant phrases
        phrases = extract_ai_driven_terminology(content, {}, "all")
        if phrases:
            return phrases[:4]
        
        # Fallback to basic extraction
        return extract_basic_terminology(content, {}, "all")[:4]
        
    except Exception as e:
        return []

def extract_first_meaningful_sentence(content):
    """
    Extract the first meaningful sentence from content for description
    """
    try:
        sentences = content.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and not any(skip in sentence.lower() for skip in [
                'yeah', 'okay', 'um', 'uh', 'oh', 'right', 'so', 'well', 'you know'
            ]):
                return sentence
        return None
    except Exception as e:
        return None

def extract_ai_driven_terminology(content, training_context, terminology_type="all"):
    """
    Use AI to dynamically extract relevant terminology from content and context
    Replaces hardcoded lists of technical terms, action words, and industry terms
    
    Args:
        content: The content to analyze
        training_context: Training context for relevance
        terminology_type: "technical", "action", "industry", or "all"
    
    Returns:
        List of relevant terms/phrases
    """
    try:
        if not api_key or api_key == "your_gemini_api_key_here":
            # Fallback to basic extraction if no API key
            return extract_basic_terminology(content, training_context, terminology_type)
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Create context-aware prompt
        training_goals = training_context.get('primary_goals', '')
        training_type = training_context.get('training_type', '')
        target_audience = training_context.get('target_audience', '')
        industry = training_context.get('industry', '')
        
        prompt = f"""
        Analyze the following content and extract relevant terminology for training purposes.
        
        Training Context:
        - Goals: {training_goals}
        - Type: {training_type}
        - Audience: {target_audience}
        - Industry: {industry}
        
        Content to analyze: {content[:2000]}...
        
        Extract {terminology_type} terminology that would be relevant for training modules.
        Focus on terms that are:
        1. Specific to the industry/domain
        2. Action-oriented for procedures
        3. Technical concepts that need explanation
        4. Relevant to the training goals
        
        Return only the terms/phrases, one per line, without explanations.
        Limit to 10-15 most relevant terms.
        """
        
        response = model.generate_content(prompt)
        if response.text:
            # Parse the response into a list of terms
            terms = [term.strip() for term in response.text.split('\n') if term.strip()]
            # Clean up any AI formatting artifacts
            cleaned_terms = []
            for term in terms:
                # Remove numbering, bullets, etc.
                term = re.sub(r'^[\d\-\.\s]+', '', term)
                if term and len(term) > 2:
                    cleaned_terms.append(term)
            return cleaned_terms[:15]  # Limit to 15 terms
        
        return []
        
    except Exception as e:
        print(f"AI terminology extraction failed: {e}")
        # Fallback to basic extraction
        return extract_basic_terminology(content, training_context, terminology_type)

def extract_basic_terminology(content, training_context, terminology_type="all"):
    """
    Basic fallback terminology extraction when AI is not available
    Uses simple pattern matching and context awareness
    """
    try:
        content_lower = content.lower()
        terms = []
        
        # Extract from training context
        if training_context.get('primary_goals'):
            goal_words = [word for word in training_context['primary_goals'].lower().split() 
                         if len(word) >= 4 and word not in ['the', 'and', 'for', 'with', 'that', 'this']]
            terms.extend(goal_words)
        
        # Extract from content using basic patterns
        sentences = content.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Look for technical/procedural patterns
            if any(word in sentence_lower for word in ['procedure', 'process', 'method', 'technique', 'system']):
                # Extract noun phrases around these words
                words = sentence.split()
                for i, word in enumerate(words):
                    if any(tech in word.lower() for tech in ['procedure', 'process', 'method', 'technique', 'system']):
                        start = max(0, i-2)
                        end = min(len(words), i+3)
                        phrase = ' '.join(words[start:end])
                        if len(phrase) > 5 and len(phrase) < 50:
                            terms.append(phrase.strip())
                        break
            
            # Look for action words
            action_patterns = ['check', 'verify', 'inspect', 'test', 'measure', 'assemble', 'install', 'configure']
            for action in action_patterns:
                if action in sentence_lower:
                    # Extract the action phrase
                    words = sentence.split()
                    for i, word in enumerate(words):
                        if action in word.lower():
                            start = max(0, i-1)
                            end = min(len(words), i+2)
                            phrase = ' '.join(words[start:end])
                            if len(phrase) > 3 and len(phrase) < 40:
                                terms.append(phrase.strip())
                            break
        
        # Remove duplicates and limit
        unique_terms = list(set(terms))
        return unique_terms[:10]
        
    except Exception as e:
        return []

def extract_key_concepts(content):
    """
    Extract key concepts from content using AI-driven approach
    """
    try:
        # Use AI to extract concepts if available
        concepts = extract_ai_driven_terminology(content, {}, "technical")
        if concepts:
            return concepts[:5]
        
        # Fallback to basic extraction
        return extract_basic_terminology(content, {}, "technical")[:5]
        
    except Exception as e:
        return []

def extract_specific_phrases_from_content(content):
    """
    Extract specific phrases from content using AI-driven approach
    """
    try:
        # Use AI to extract relevant phrases
        phrases = extract_ai_driven_terminology(content, {}, "all")
        if phrases:
            return phrases[:4]
        
        # Fallback to basic extraction
        return extract_basic_terminology(content, {}, "all")[:4]
        
    except Exception as e:
        return []

def extract_specific_identifier(content):
    """
    Extract a specific identifier from content using AI-driven approach
    """
    try:
        # Use AI to identify the most relevant technical term
        technical_terms = extract_ai_driven_terminology(content, {}, "technical")
        if technical_terms:
            return technical_terms[0].title()
        
        # Fallback to basic extraction
        basic_terms = extract_basic_terminology(content, {}, "technical")
        if basic_terms:
            return basic_terms[0].title()
        
        return None
        
    except Exception as e:
        return None

def get_training_keywords(training_context):
    """
    Get training-relevant keywords using AI-driven approach
    """
    try:
        # Create a sample content from training context
        context_content = f"""
        Training goals: {training_context.get('primary_goals', '')}
        Training type: {training_context.get('training_type', '')}
        Target audience: {training_context.get('target_audience', '')}
        Industry: {training_context.get('industry', '')}
        Success metrics: {training_context.get('success_metrics', '')}
        """
        
        # Use AI to extract relevant keywords
        keywords = extract_ai_driven_terminology(context_content, training_context, "all")
        if keywords:
            return keywords[:30]
        
        # Fallback to basic extraction
        return extract_basic_terminology(context_content, training_context, "all")[:30]
        
    except Exception as e:
        # Ultimate fallback
        return [
            'process', 'procedure', 'workflow', 'system', 'method', 'technique',
            'quality', 'safety', 'compliance', 'standard', 'specification',
            'inspection', 'testing', 'verification', 'documentation', 'record',
            'equipment', 'tool', 'material', 'resource', 'maintenance',
            'operation', 'installation', 'configuration', 'calibration',
            'training', 'learning', 'skill', 'knowledge', 'competency'
        ]

def extract_specific_procedures(content):
    """
    Extract specific procedures from content
    """
    try:
        import re
        content_lower = content.lower()
        procedures = []
        
        # Look for procedure-related patterns
        procedure_patterns = [
            r'\b(assembly|fabrication|welding|cutting|inspection|testing|maintenance|calibration)\b',
            r'\b(truss|deck|abutment|bridge|steel|material|component)\b',
            r'\b(workflow|process|procedure|method|technique|approach)\b'
        ]
        
        for pattern in procedure_patterns:
            matches = re.findall(pattern, content_lower)
            procedures.extend(matches)
        
        # Remove duplicates and return unique procedures
        unique_procedures = list(set(procedures))
        return unique_procedures[:3]  # Return top 3
        
    except Exception as e:
        return []

def extract_meaningful_content_snippet(content):
    """
    Extract a meaningful snippet from content
    """
    try:
        # Split into sentences and find the most meaningful one
        sentences = content.split('.')
        meaningful_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30 and len(sentence) < 200:
                # Check if sentence contains meaningful content
                if any(word in sentence.lower() for word in ['process', 'procedure', 'method', 'technique', 'assembly', 'fabrication', 'quality', 'safety']):
                    meaningful_sentences.append(sentence)
        
        if meaningful_sentences:
            return meaningful_sentences[0]
        else:
            # Fallback to first substantial sentence
            for sentence in sentences:
                if len(sentence.strip()) > 20:
                    return sentence.strip()
        
        return content[:100] + "..." if len(content) > 100 else content
        
    except Exception as e:
        return content[:100] + "..." if len(content) > 100 else content