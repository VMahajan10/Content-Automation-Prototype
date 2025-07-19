1import re
import json
import time
import threading
from modules.config import model

# Thread-safe log buffer for background thread logs
debug_logs = []
debug_lock = threading.Lock()

def get_parallel_config():
    ""Get configuration for parallel processing"""
    return {
       max_file_workers: 3,    max_modules_per_file': 5
       batch_ai_calls: True,
       timeout_per_file': 60}

def debug_print(message, is_error=False):
Thread-safe debug printing   with debug_lock:
        debug_logs.append({
            message': message,
        is_error': is_error,
           timestamp': time.time()
        })
        print(message)

def flush_debug_logs_to_streamlit():
lush debug logs to Streamlit   with debug_lock:
        logs = debug_logs.copy()
        debug_logs.clear()
    return logs

def clean_content_basic(content):
  c content cleaning"""
    if not content:
        return ""
    
    # Remove extra whitespace
    cleaned = re.sub(r'\s+',   content.strip())
    
    # Remove common artifacts
    cleaned = re.sub(r[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}]',  cleaned)
    
    return cleaned

def clean_conversational_content(content):
    """Clean conversational content"""
    if not content:
        return ""
    
    # Remove timestamps and speaker names
    cleaned = re.sub(r'\d+:\d+\s*-\s*[A-Za-z\s]+:', '', content)
    cleaned = re.sub(r'^[A-Za-z]+:\s*', , cleaned, flags=re.MULTILINE)
    
    # Remove filler words
    filler_words = ['um,uh,yeah', okay', 'right, so,well',like', 'you know',i mean]for word in filler_words:
        cleaned = re.sub(rundefinedb' + word + rb, cleaned, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    cleaned = re.sub(r'\s+',   cleaned.strip())
    
    return cleaned

def make_content_professional(content):
 Make content more professional"""
    if not content:
        return "  # Basic cleaning
    cleaned = clean_content_basic(content)
    
    # Ensure proper sentence structure
    sentences = re.split(r'[.!?]+', cleaned)
    professional_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) >10         # Capitalize first letter
            if sentence and sentence[0].islower():
                sentence = sentence[0].upper() + sentence[1:]
            professional_sentences.append(sentence)
    
    return '. '.join(professional_sentences) + '.'

def get_training_keywords(training_context):
  training keywords from context
    primary_goals = training_context.get(primary_goals', '')
    training_type = training_context.get(training_type, ing')
    industry = training_context.get('industry', 'general')
    
    keywords = 
    if primary_goals:
        keywords.extend(primary_goals.lower().split())
    if training_type:
        keywords.append(training_type.lower())
    if industry:
        keywords.append(industry.lower())
    
    return list(set(keywords))

def clean_source_field(source):
 Clean source field"""
    if not source:
        returnUnknown source"
    
    # Remove file extensions and clean up
    cleaned = re.sub(r.[a-zA-Z0-9]+$, ource)
    cleaned = re.sub(r'[^\w\s\-_]',  cleaned)
    
    return cleaned.strip()

def extract_key_points_from_content(content, training_context):
Extract key points from content"""
    if not content:
        return []
    
    # Simple key point extraction
    sentences = re.split(r'[.!?]+', content)
    key_points = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 20 and len(sentence) < 200        key_points.append(sentence)
    
    return key_points[:5]  # Limit to 5 points

def create_quick_pathway(context, extracted_file_contents, inventory):
   k fallback pathway creation"""
    modules = []
    for i, (filename, content) in enumerate(extracted_file_contents.items(), 1):
        modules.append({
           title: fule {i}: {filename}',
           description': fContent extracted from {filename}',
            content': content,
            source': filename
        })
    return {
     pathways': [{
           pathway_name':Quick Pathway',
         sections[{
           title: ,
                modules': modules
            }]
        }]
    }

def extract_modules_from_file_content(filename, content, training_context, bypass_filtering=False, preserve_original_content=False):
    tract modules from file content""try:
        debug_print(f"📄 **Extracting content from {filename}**")
        debug_print(f📄 Content length: {len(content)} characters")
        
        if not content or len(content.strip()) < 50:
            debug_print(f⚠️ {filename} has insufficient content for extraction")
            return []
        
        # Clean content
        cleaned_content = clean_content_basic(content)
        
        # Split into sections
        sections = re.split(rns*n, cleaned_content)
        meaningful_sections = [s.strip() for s in sections if len(s.strip()) > 100]
        
        if not meaningful_sections:
            return []
        
        # Create modules
        modules =    for i, section in enumerate(meaningful_sections:3Limit to 3 modules
            title = f"Module {i+1}: {filename.replace('.txt', ).replace('_',        professional_content = make_content_professional(section)
            
            modules.append({
              titlee,
               description': f'Training content from {filename},
        content': professional_content,
             source': clean_source_field(filename),
           key_points': extract_key_points_from_content(professional_content, training_context),
                relevance_score': 0.7
              content_types': ['text]      })
        
        debug_print(f✅ Extracted {len(modules)} modules from {filename}")
        return modules
        
    except Exception as e:
        debug_print(f"⚠️ Module extraction failed for {filename}: {str(e)}")
        return []

def gemini_generate_complete_pathway(context, extracted_file_contents, inventory, bypass_filtering=False, preserve_original_content=False, enhanced_content=False):
    Sequential, robust AI-powered pathway generation that clearly uses information from each uploaded file.
    Each file is processed one by one: modules are extracted using AI (if available), with strict timeout and error handling.
    If AI fails for a file, fallback to simple extraction for that file only. All modules are linked to their source file.
    Returns a dict with a 'pathways key.   import time
    debug_print(f"🚀 [AI Pathway] Starting pathway generation for {len(extracted_file_contents)} files")
    start_time = time.time()
    
    primary_goals = context.get(primary_goals', '')
    training_type = context.get(training_type, ining')
    target_audience = context.get(target_audience', 'employees')
    industry = context.get('industry', 'general')
    
    all_modules =]
    file_debug = []
    
    for filename, content in extracted_file_contents.items():
        if not content or len(content.strip()) < 50:
            debug_print(f"⚠️ Skipping {filename}: no content or too short")
            continue
        
        debug_print(f"🔍 Processing file: [object Object]filename} (length: {len(content)})")
        
        try:
            # Try AI-powered extraction with timeout
            result_holder = {}
            
            def ai_extract():
                try:
                    result_holder['modules'] = extract_modules_from_file_content(
                        filename, content, context, bypass_filtering, preserve_original_content
                    )
                except Exception as e:
                    result_holder[errorr(e)
            
            t = threading.Thread(target=ai_extract)
            t.start()
            t.join(timeout=60# 60s per file max
            
            if t.is_alive():
                debug_print(f"⏰ Timeout extracting modules from {filename}, using fallback.)
                t.join(0)  # Don't wait further
                modules = []
            elif 'modulesin result_holder:
                modules = result_holder['modules']
            else:
                debug_print(f"❌ AI extraction error for {filename}: {result_holder.get('error,nknown error')})           modules = []
            
            if not modules:
                # Fallback: simple chunking
                debug_print(f"🔄 Fallback: simple extraction for {filename})            chunks = [c.strip() for c in re.split(r\n\s*\n, content) if len(c.strip()) > 100           modules =                for i, chunk in enumerate(chunks[:3]):
                    modules.append({
                       title: f'Module {i+1}: {filename}',
                       description': fContent extracted from {filename}',
                        content                   source': filename
                    })
            else:
                # Ensure all modules have a source field
                for m in modules:
                    ifsource' not in m:
                        m['source'] = filename
            
            debug_print(f"✅ {filename}: {len(modules)} modules extracted)       all_modules.extend(modules)
            file_debug.append(f{filename}: {len(modules)} modules")
            
        except Exception as e:
            debug_print(f"❌ Exception processing {filename}: {e}")
            continue
    
    if not all_modules:
        debug_print("⚠️ No modules extracted from any file, returning quick fallback pathway.")
        return create_quick_pathway(context, extracted_file_contents, inventory)
    
    # Group modules into a single pathway
    pathway = [object Object]    pathway_name': f"{training_type} Pathway for {target_audience} ({industry})",
     sections': [{
           title': 'Modules from Uploaded Files',
        modules': all_modules
        }]
    }
    
    debug_print(f"🎯 Pathway generated with {len(all_modules)} modules from {len(extracted_file_contents)} files.)
    debug_print(f"⏱️ Total time: {round(time.time()-start_time,1)}s)
    debug_print(f"Files processed: {',.join(file_debug)}")
    return {'pathways: [pathway]}

def generate_fallback_content_types(module_content, training_context):
  Generate fallback content types return [{
      type:text',
    title': 'Text Content',
      description':Explanatory text content',
  content':Provide detailed explanations of module content'
    }]

def extract_meaningful_title_from_content(content, filename, training_context):
    """Extract meaningful title from content"""
    if not content:
        return fModule: {filename}"
    
    # Get first sentence as title
    sentences = re.split(r'[.!?]+, content)
    if sentences:
        title = sentences[0strip()
        if len(title) > 10:
            return title[:100Limit length
    
    return fModule: {filename}"

def generate_meaningful_description(content_preview, training_context):
    """Generate meaningful description"""
    if not content_preview:
        returnTraining content from uploaded file"
    
    # Use first few sentences as description
    sentences = re.split(r'[.!?]+, content_preview)
    if sentences:
        description = '. .join(sentences[:2]).strip()
        if len(description) > 20:
            return description
    
    returnTraining content from uploaded file" 