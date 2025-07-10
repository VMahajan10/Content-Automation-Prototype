#!/usr/bin/env python3
"""
Fixed version of utils.py with correct syntax
"""

import json
import re
import concurrent.futures
import streamlit as st
from modules.config import model

def get_parallel_config():
    """
    Get configuration for parallel processing based on system capabilities
    (Optimized for speed: reduced AI calls and faster processing)
    """
    return {
        'max_file_workers': 2,      # Reduced workers to avoid timeouts
        'max_section_workers': 2,   # Reduced AI workers
        'max_topic_workers': 2,     # Reduced topic analysis workers
        'timeout_seconds': 60,      # Reduced timeout for faster processing
        'max_modules_per_file': 2,  # Reduced module limit for speed
        'batch_ai_calls': False,    # Disable batching to avoid timeouts
        'parallel_ai_processing': False  # Disable parallel AI for reliability
    }

def debug_print(message, is_error=False):
    """
    Print debug information to both console and Streamlit
    """
    print(message)
    if is_error:
        st.error(message)
    else:
        st.info(message)

def extract_and_transform_content(content, training_context):
    """
    Universal content extraction and transformation system
    Works with ANY file type and ANY subject matter for onboarding
    """
    try:
        # Universal content analysis - works for any type of content
        content_lower = content.lower()
        
        # Universal content type detection
        content_type = detect_content_type(content)
        debug_print(f"🔍 **Universal Content Analysis:**")
        debug_print(f"   Content type: {content_type}")
        debug_print(f"   Content length: {len(content)} characters")
        debug_print(f"   Content preview: {content[:200]}...")
        
        # Apply universal transformation based on content type
        if content_type == "structured_training":
            return apply_conservative_transformation(content, training_context)
        elif content_type == "conversational":
            return apply_comprehensive_transformation(content, training_context)
        elif content_type == "technical_documentation":
            return apply_technical_transformation(content, training_context)
        elif content_type == "procedural":
            return apply_procedural_transformation(content, training_context)
        else:
            # Default to comprehensive transformation for unknown types
            return apply_comprehensive_transformation(content, training_context)
            
    except Exception as e:
        debug_print(f"⚠️ Universal content transformation failed: {str(e)}")
        return None

def detect_content_type(content):
    """
    Universal content type detection - works for any file type and subject
    """
    try:
        if not content or len(content.strip()) < 10:
            return "conversational"
            
        content_lower = content.lower()
        
        # Check for meeting transcript patterns first (these should override other detection)
        meeting_patterns = [
            r'teams meeting',
            r'meet meeting', 
            r'meeting transcript',
            r'\d{1,2}:\d{2}\s*-\s*[A-Za-z]',  # Time stamps like "0:00 - Name"
            r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday),\s*\w+\s+\d{1,2},\s*\d{4}',  # Date patterns
            r'yeah,\s*\w+',  # Conversational patterns
            r'um,\s*\w+',
            r'uh,\s*\w+'
        ]
        
        # Check for meeting patterns
        meeting_matches = 0
        import re
        for pattern in meeting_patterns:
            if re.search(pattern, content_lower):
                meeting_matches += 1
        
        # If content has meeting indicators, it's conversational regardless of other scores
        if meeting_matches >= 1:  # Any meeting indicator means it's conversational
            debug_print(f"   Detected content type: conversational (meeting transcript - {meeting_matches} indicators)")
            return "conversational"
        
        # Universal content type indicators
        content_types = {
            "structured_training": {
                "indicators": [
                    'training', 'onboarding', 'guide', 'manual', 'procedure', 'process',
                    'instruction', 'tutorial', 'workflow', 'standard operating procedure',
                    'sop', 'policy', 'guideline', 'best practice', 'step-by-step',
                    'how to', 'overview', 'introduction', 'getting started', 'admin',
                    'user guide', 'reference', 'documentation', 'handbook'
                ],
                "patterns": [
                    r'\d+\.\s',  # Numbered sections
                    r'[•\-\*]\s',  # Bullet points
                    r'^[A-Z][A-Z\s]+$',  # Headers
                    r'step\s+\d+',  # Step-by-step
                    r'procedure\s+\d+',  # Procedures
                ]
            },
            "conversational": {
                "indicators": [
                    'meeting transcript', 'teams meeting', 'meet meeting', 'zoom meeting',
                    'conference call', 'video call', 'meeting recording', 'call transcript',
                    'um', 'uh', 'yeah', 'okay', 'right', 'so', 'well', 'you know',
                    'can you hear me', 'is that working', 'are you there'
                ],
                "patterns": [
                    r'\d{1,2}:\d{2}\s*-\s*[A-Za-z]',  # Time stamps
                    r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',  # Days
                    r'yeah,\s*\w+',  # Conversational patterns
                    r'um,\s*\w+',
                    r'uh,\s*\w+'
                ]
            },
            "technical_documentation": {
                "indicators": [
                    'specification', 'technical', 'engineering', 'design', 'architecture',
                    'system', 'component', 'module', 'interface', 'api', 'database',
                    'configuration', 'installation', 'setup', 'deployment'
                ],
                "patterns": [
                    r'[A-Z]{2,}\s+\d+',  # Technical codes
                    r'version\s+\d+',  # Version numbers
                    r'api\s+endpoint',  # API references
                    r'configuration\s+file',  # Config references
                ]
            },
            "procedural": {
                "indicators": [
                    'procedure', 'process', 'workflow', 'method', 'technique',
                    'operation', 'maintenance', 'calibration', 'inspection',
                    'quality control', 'safety', 'compliance'
                ],
                "patterns": [
                    r'step\s+\d+',  # Step procedures
                    r'check\s+list',  # Checklists
                    r'verify\s+that',  # Verification steps
                    r'ensure\s+that',  # Safety checks
                ]
            }
        }
        
        # Score each content type
        content_scores = {}
        
        for content_type, detection in content_types.items():
            score = 0
            
            # Count indicator matches
            indicator_matches = sum(1 for indicator in detection["indicators"] if indicator in content_lower)
            score += indicator_matches * 2  # Weight indicators more heavily
            
            # Count pattern matches
            pattern_matches = 0
            for pattern in detection["patterns"]:
                if re.search(pattern, content, re.IGNORECASE):
                    pattern_matches += 1
            score += pattern_matches * 3  # Weight patterns even more heavily
            
            content_scores[content_type] = score
        
        # Find the content type with highest score
        best_type = "conversational"  # Default
        best_score = 0
        
        if content_scores:
            try:
                best_type = max(content_scores, key=content_scores.get)
                best_score = content_scores[best_type]
            except Exception as e:
                debug_print(f"⚠️ Error finding best content type: {e}")
                best_type = "conversational"
                best_score = 0
        
        # Only classify if we have a clear winner
        if best_score >= 3:
            debug_print(f"   Detected content type: {best_type} (score: {best_score})")
            return best_type
        
        # Default to conversational if unclear
        debug_print(f"   Defaulting to conversational content type")
        return "conversational"
        
    except Exception as e:
        debug_print(f"⚠️ Content type detection failed: {str(e)}")
        return "conversational"

def apply_technical_transformation(content, training_context):
    """
    Transform technical documentation into onboarding material using simple methods
    """
    try:
        # Use simple content cleaning instead of AI
        cleaned_content = clean_content_basic(content)
        
        if len(cleaned_content) < 100:
            debug_print("⚠️ Technical transformation failed, using original content")
            return content
        
        debug_print(f"✅ Applied technical transformation for onboarding")
        return cleaned_content
            
    except Exception as e:
        debug_print(f"⚠️ Technical transformation failed: {str(e)}")
        return content

def apply_procedural_transformation(content, training_context):
    """
    Transform procedural content into onboarding material using simple methods
    """
    try:
        # Use simple content cleaning instead of AI
        cleaned_content = clean_content_basic(content)
        
        if len(cleaned_content) < 100:
            debug_print("⚠️ Procedural transformation failed, using original content")
            return content
        
        debug_print(f"✅ Applied procedural transformation for onboarding")
        return cleaned_content
        
    except Exception as e:
        debug_print(f"⚠️ Procedural transformation failed: {str(e)}")
        return content

def apply_conservative_transformation(content, training_context):
    """
    Apply minimal transformation to preserve original training content using simple methods
    """
    try:
        # Use simple content cleaning instead of AI
        cleaned_content = clean_content_basic(content)
        
        if len(cleaned_content) < 100:
            debug_print("⚠️ Conservative transformation failed, using original content")
            return content
        
        debug_print(f"✅ Applied conservative transformation, preserved original content")
        return cleaned_content
        
    except Exception as e:
        debug_print(f"⚠️ Conservative transformation failed: {str(e)}")
        return content

def apply_comprehensive_transformation(content, training_context):
    """
    Apply comprehensive transformation for unstructured content using Gemini API
    """
    try:
        if not model:
            # Fallback to basic transformation if no API key
            cleaned_content = clean_content_basic(content)
            
            if len(cleaned_content) < 100:
                debug_print(f"⚠️ Content too short after cleaning")
                return None
            
            # Check if content has relevant training information
            training_keywords = get_training_keywords(training_context)
            content_lower = cleaned_content.lower()
            
            # Count keyword matches
            keyword_matches = sum(1 for keyword in training_keywords if keyword in content_lower)
            
            if keyword_matches >= 2:  # At least 2 keyword matches
                debug_print(f"✅ Content has relevant training information ({keyword_matches} keywords)")
                return cleaned_content
            else:
                debug_print(f"⚠️ No relevant content found for transformation")
                return None
        
        # Use Gemini API for comprehensive transformation
        training_type = training_context.get('training_type', 'Training')
        target_audience = training_context.get('target_audience', 'employees')
        industry = training_context.get('industry', 'general')
        primary_goals = training_context.get('primary_goals', '')
        
        prompt = f"""
        Transform this unstructured content into professional training material.
        
        Original Content:
        {content[:3000]}
        
        Training Context:
        - Type: {training_type}
        - Target Audience: {target_audience}
        - Industry: {industry}
        - Primary Goals: {primary_goals}
        
        REQUIREMENTS:
        1. Extract and structure training-relevant information
        2. Remove conversational elements and informal language
        3. Convert to professional training format
        4. Organize into clear sections with headings
        5. Focus on actionable training content
        6. Make it suitable for {target_audience} in {industry}
        7. Align with training goals: {primary_goals}
        8. Preserve important technical information and procedures
        
        If the content contains valuable training information, transform it into professional training material.
        If the content is not suitable for training, return "NO_TRAINING_CONTENT".
        
        Return the transformed professional training content or "NO_TRAINING_CONTENT".
        """
        
        response = model.generate_content(prompt)
        transformed_content = response.text.strip()
        
        # Check if Gemini determined there's no training content
        if "NO_TRAINING_CONTENT" in transformed_content.upper():
            debug_print(f"⚠️ No relevant training content found")
            return None
        
        # Ensure we have meaningful content
        if len(transformed_content) < 100:
            debug_print(f"⚠️ Transformed content too short")
            return None
        
        debug_print(f"✅ Content transformed using Gemini API")
        return transformed_content
            
    except Exception as e:
        debug_print(f"⚠️ Comprehensive transformation failed: {str(e)}")
        return None

def clean_content_basic(content):
    """
    Clean content without AI calls for speed
    """
    try:
        import re
        
        # Basic cleaning without AI
        cleaned = content.strip()
        
        # Remove common conversational elements
        conversational_elements = ['um', 'uh', 'yeah', 'okay', 'right', 'so', 'well', 'you know']
        for element in conversational_elements:
            pattern = re.escape(element)
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned if len(cleaned) > 50 else content
        
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
        if not model:
            # Fallback to basic extraction if no API key
            return extract_basic_terminology(content, training_context, terminology_type)
        
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
        debug_print(f"AI terminology extraction failed: {e}")
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
            sentence = sentence.strip()
            # Look for technical/procedural patterns
            if any(word in sentence.lower() for word in ['procedure', 'process', 'method', 'technique', 'system']):
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
                if action in sentence.lower():
                    words = sentence.split()
                    for i, word in enumerate(words):
                        if action in word.lower():
                            start = max(0, i-1)
                            end = min(len(words), i+2)
                            phrase = ' '.join(words[start:end])
                            if len(phrase) > 3 and len(phrase) < 40:
                                terms.append(phrase.strip())
                            break
        unique_terms = list(set(terms))
        return unique_terms[:10]
    except Exception as e:
        return []

def extract_json_from_ai_response(raw_text):
    """
    Extract JSON from AI response with robust error handling
    """
    try:
        # Check if response is empty or None
        if not raw_text or not raw_text.strip():
            debug_print("⚠️ Empty AI response received")
            return None
            
        # Clean up the response
        cleaned_text = raw_text.strip()
        
        # Remove markdown code blocks
        if cleaned_text.startswith('```'):
            cleaned_text = cleaned_text.split('```', 1)[-1].strip()
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3].strip()
        
        # Remove JSON prefix if present
        if cleaned_text.startswith('json'):
            cleaned_text = cleaned_text[4:].strip()
        
        # Try to find JSON object/array
        import re
        
        # Look for JSON array first (preferred for modules)
        start = cleaned_text.find('[')
        if start != -1:
            bracket_count = 0
            end = start
            for i, char in enumerate(cleaned_text[start:], start):
                if char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        end = i + 1
                        break
            if end > start:
                json_str = cleaned_text[start:end]
                # Remove trailing commas
                json_str = re.sub(r',([ \t\r\n]*[\]}])', r'\1', json_str)
                try:
                    result = json.loads(json_str)
                    if isinstance(result, list):
                        debug_print(f"✅ Successfully extracted JSON array with {len(result)} items")
                        return result
                    else:
                        debug_print(f"⚠️ JSON is not an array: {type(result).__name__}")
                except json.JSONDecodeError as e:
                    debug_print(f"⚠️ JSON array decode error: {e}")
                    # Try to fix common JSON issues
                    json_str = re.sub(r'([^\\])"([^"]*)"([^\\])', r'\1"\2"\3', json_str)
                    try:
                        result = json.loads(json_str)
                        if isinstance(result, list):
                            debug_print(f"✅ Successfully extracted JSON array after fix with {len(result)} items")
                            return result
                    except:
                        debug_print(f"⚠️ JSON array fix failed")
        
        # Look for JSON object (fallback)
        start = cleaned_text.find('{')
        if start != -1:
            brace_count = 0
            end = start
            for i, char in enumerate(cleaned_text[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            if end > start:
                json_str = cleaned_text[start:end]
                # Remove trailing commas
                json_str = re.sub(r',([ \t\r\n]*[\]}])', r'\1', json_str)
                try:
                    result = json.loads(json_str)
                    # If it's a single object, wrap it in an array
                    if isinstance(result, dict):
                        debug_print(f"✅ Successfully extracted JSON object, wrapping in array")
                        return [result]
                except json.JSONDecodeError as e:
                    debug_print(f"⚠️ JSON object decode error: {e}")
                    # Try to fix common JSON issues
                    json_str = re.sub(r'([^\\])"([^"]*)"([^\\])', r'\1"\2"\3', json_str)
                    try:
                        result = json.loads(json_str)
                        if isinstance(result, dict):
                            debug_print(f"✅ Successfully extracted JSON object after fix, wrapping in array")
                            return [result]
                    except:
                        debug_print(f"⚠️ JSON object fix failed")
        
        # Enhanced fallback: Try to extract structured content from text
        debug_print(f"🔄 **Enhanced fallback: Extracting structured content from text**")
        
        # Look for patterns that might indicate structured content
        lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
        if lines:
            # Try to extract structured items
            structured_items = []
            current_item = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for title patterns
                if re.match(r'^["\']?[A-Z][^:]*["\']?\s*[:]?\s*$', line):
                    # This looks like a title
                    if current_item:
                        structured_items.append(current_item)
                    current_item = {'title': line.strip('"\'')}
                elif 'title' in line.lower() and ':' in line:
                    # Extract title from "title: value" pattern
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        if current_item:
                            structured_items.append(current_item)
                        current_item = {'title': parts[1].strip()}
                elif 'description' in line.lower() and ':' in line:
                    # Extract description
                    parts = line.split(':', 1)
                    if len(parts) == 2 and current_item:
                        current_item['description'] = parts[1].strip()
                elif 'content' in line.lower() and ':' in line:
                    # Extract content
                    parts = line.split(':', 1)
                    if len(parts) == 2 and current_item:
                        current_item['content'] = parts[1].strip()
                elif len(line) > 20 and not any(skip in line.lower() for skip in ['um,', 'uh,', 'yeah,', 'okay,']):
                    # This might be content
                    if current_item:
                        if 'content' not in current_item:
                            current_item['content'] = line
                        else:
                            current_item['content'] += ' ' + line
                    else:
                        # Start a new item
                        current_item = {'title': f'Module {len(structured_items)+1}', 'content': line}
            
            # Add the last item
            if current_item:
                structured_items.append(current_item)
            
            if structured_items:
                debug_print(f"✅ Extracted {len(structured_items)} structured items from text")
                return structured_items
        
        # Special handling for pathway creation responses
        debug_print(f"🔄 **Special handling for pathway creation responses**")
        
        # Look for pathway-like patterns in the text
        pathway_patterns = [
            r'pathway[^:]*:\s*([^\n]+)',
            r'pathway[^:]*name[^:]*:\s*([^\n]+)',
            r'section[^:]*:\s*([^\n]+)',
            r'title[^:]*:\s*([^\n]+)'
        ]
        
        found_pathways = []
        for pattern in pathway_patterns:
            matches = re.findall(pattern, cleaned_text, re.IGNORECASE)
            if matches:
                found_pathways.extend(matches)
        
        if found_pathways:
            debug_print(f"✅ Found pathway-like content: {found_pathways[:3]}")
            # Create a simple pathway structure
            return {
                'pathways': [{
                    'pathway_name': found_pathways[0] if found_pathways else 'Generated Pathway',
                    'sections': [{
                        'title': found_pathways[1] if len(found_pathways) > 1 else 'Training Section',
                        'modules': []
                    }]
                }]
            }
        
        # If no structured content found, try to extract simple list from text
        lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
        if lines:
            # Try to extract simple list items
            items = []
            for line in lines:
                # Remove common prefixes
                line = re.sub(r'^[\d\-\.\s]+', '', line)
                if line and len(line) > 2:
                    items.append(line)
            if items:
                debug_print(f"✅ Extracted {len(items)} simple items from text")
                return items
        
        debug_print(f"⚠️ No valid JSON or structured content found in response")
        debug_print(f"📋 Raw response preview: {cleaned_text[:300]}...")
        return None
        
    except Exception as e:
        debug_print(f"⚠️ JSON extraction failed: {str(e)}")
        return None

def create_fast_ai_pathways(modules, training_context):
    """
    Create company-specific pathways using actual content analysis with unique naming
    """
    try:
        if not modules:
            return []
            
        debug_print(f"🚀 **Fast AI Pathway Creation:** {len(modules)} modules")
        
        # Get company context for pathway naming
        training_type = training_context.get('training_type', 'Onboarding')
        target_audience = training_context.get('target_audience', 'New Employees')
        industry = training_context.get('industry', 'General')
        primary_goals = training_context.get('primary_goals', '')
        
        # Analyze module content to create meaningful pathways
        pathway_themes = analyze_module_themes(modules, training_context)
        debug_print(f"🎯 **Identified themes:** {pathway_themes}")
        
        if len(modules) <= 2:
            # Single comprehensive pathway with unique naming
            pathway_name = generate_unique_pathway_name_from_theme(training_type, pathway_themes[0] if pathway_themes else 'comprehensive', primary_goals, industry, 1)
            return [{
                'pathway_name': pathway_name,
                'sections': [{
                    'title': generate_unique_section_name(pathway_themes, 1),
                    'modules': modules
                }],
                'module_count': len(modules)
            }]
        elif len(modules) <= 6:
            # Two logical pathways based on content themes
            mid_point = len(modules) // 2
            pathway1_modules = modules[:mid_point]
            pathway2_modules = modules[mid_point:]
            
            # Analyze themes for each pathway group separately
            pathway1_theme = analyze_pathway_theme(pathway1_modules, training_context)
            pathway2_theme = analyze_pathway_theme(pathway2_modules, training_context)
            
            # Ensure different themes if possible
            if pathway1_theme == pathway2_theme and len(pathway_themes) > 1:
                pathway2_theme = pathway_themes[1] if len(pathway_themes) > 1 else 'application'
            
            debug_print(f"🎯 **Pathway 1 theme:** {pathway1_theme}")
            debug_print(f"🎯 **Pathway 2 theme:** {pathway2_theme}")
            
            # Generate unique names based on actual pathway themes
            pathway1_name = generate_unique_pathway_name_from_theme(training_type, pathway1_theme, primary_goals, industry, 1)
            pathway2_name = generate_unique_pathway_name_from_theme(training_type, pathway2_theme, primary_goals, industry, 2)
            
            return [
                {
                    'pathway_name': pathway1_name,
                    'sections': [{
                        'title': generate_unique_section_name([pathway1_theme], 1),
                        'modules': pathway1_modules
                    }],
                    'module_count': len(pathway1_modules)
                },
                {
                    'pathway_name': pathway2_name,
                    'sections': [{
                        'title': generate_unique_section_name([pathway2_theme], 2),
                        'modules': pathway2_modules
                    }],
                    'module_count': len(pathway2_modules)
                }
            ]
        else:
            # Three comprehensive pathways based on content analysis
            third = len(modules) // 3
            pathway1_modules = modules[:third]
            pathway2_modules = modules[third:2*third]
            pathway3_modules = modules[2*third:]
            
            # Analyze themes for each pathway group separately
            theme1 = analyze_pathway_theme(pathway1_modules, training_context)
            theme2 = analyze_pathway_theme(pathway2_modules, training_context)
            theme3 = analyze_pathway_theme(pathway3_modules, training_context)
            
            # Ensure different themes if possible
            if theme1 == theme2 == theme3 and len(pathway_themes) >= 3:
                theme1 = pathway_themes[0] if len(pathway_themes) > 0 else 'foundation'
                theme2 = pathway_themes[1] if len(pathway_themes) > 1 else 'application'
                theme3 = pathway_themes[2] if len(pathway_themes) > 2 else 'mastery'
            elif theme1 == theme2 and len(pathway_themes) >= 2:
                theme2 = pathway_themes[1] if len(pathway_themes) > 1 else 'application'
            elif theme2 == theme3 and len(pathway_themes) >= 2:
                theme3 = pathway_themes[1] if len(pathway_themes) > 1 else 'mastery'
            
            debug_print(f"🎯 **Pathway 1 theme:** {theme1}")
            debug_print(f"🎯 **Pathway 2 theme:** {theme2}")
            debug_print(f"🎯 **Pathway 3 theme:** {theme3}")
            
            # Generate unique names based on actual pathway themes
            pathway1_name = generate_unique_pathway_name_from_theme(training_type, theme1, primary_goals, industry, 1)
            pathway2_name = generate_unique_pathway_name_from_theme(training_type, theme2, primary_goals, industry, 2)
            pathway3_name = generate_unique_pathway_name_from_theme(training_type, theme3, primary_goals, industry, 3)
            
            return [
                {
                    'pathway_name': pathway1_name,
                    'sections': [{
                        'title': generate_unique_section_name([theme1], 1),
                        'modules': pathway1_modules
                    }],
                    'module_count': len(pathway1_modules)
                },
                {
                    'pathway_name': pathway2_name,
                    'sections': [{
                        'title': generate_unique_section_name([theme2], 2),
                        'modules': pathway2_modules
                    }],
                    'module_count': len(pathway2_modules)
                },
                {
                    'pathway_name': pathway3_name,
                    'sections': [{
                        'title': generate_unique_section_name([theme3], 3),
                        'modules': pathway3_modules
                    }],
                    'module_count': len(pathway3_modules)
                }
            ]
        
    except Exception as e:
        debug_print(f"⚠️ Fast AI pathway creation failed: {str(e)}")
        return create_fast_company_specific_pathways(modules, training_context)

def generate_unique_pathway_name_from_theme(training_type, theme, primary_goals, industry, pathway_number):
    """
    Generate unique pathway names based on specific theme and pathway number
    """
    try:
        theme = theme.lower() if theme else 'general'
        
        # Theme-specific pathway names with variety
        theme_pathways = {
            'safety': [
                'Safety Excellence Pathway',
                'Protection Protocols Program',
                'Risk Management Mastery',
                'Safety First Initiative',
                'Hazard Prevention Program',
                'Emergency Response Training'
            ],
            'quality': [
                'Quality Excellence Pathway',
                'Standards Mastery Program',
                'Quality Control Initiative',
                'Excellence Track Program',
                'Inspection Excellence',
                'Quality Assurance Mastery'
            ],
            'process': [
                'Process Excellence Pathway',
                'Workflow Mastery Program',
                'Procedure Implementation',
                'Operational Excellence',
                'Process Optimization',
                'Workflow Efficiency Program'
            ],
            'equipment': [
                'Equipment Mastery Pathway',
                'Tool Operations Program',
                'System Management Initiative',
                'Technical Excellence Program',
                'Equipment Operations Mastery',
                'Technical Systems Program'
            ],
            'communication': [
                'Communication Excellence Pathway',
                'Collaboration Skills Program',
                'Team Dynamics Initiative',
                'Interpersonal Mastery',
                'Communication Skills Program',
                'Team Collaboration Mastery'
            ],
            'documentation': [
                'Documentation Excellence Pathway',
                'Record Management Program',
                'Information Systems Initiative',
                'Knowledge Management',
                'Documentation Mastery',
                'Information Management Program'
            ],
            'technical': [
                'Technical Excellence Pathway',
                'System Mastery Program',
                'Technology Implementation',
                'Expert Development Program',
                'Technical Skills Mastery',
                'System Operations Program'
            ],
            'compliance': [
                'Compliance Excellence Pathway',
                'Regulatory Mastery Program',
                'Standards Adherence Initiative',
                'Policy Implementation',
                'Compliance Mastery Program',
                'Regulatory Excellence'
            ],
            'leadership': [
                'Leadership Development Pathway',
                'Management Excellence Program',
                'Team Leadership Initiative',
                'Strategic Thinking Program',
                'Leadership Mastery',
                'Management Skills Program'
            ],
            'customer': [
                'Customer Service Excellence',
                'Client Relations Program',
                'Service Excellence Initiative',
                'Customer Experience Mastery',
                'Client Service Program',
                'Customer Relations Mastery'
            ],
            'foundation': [
                'Foundation Skills Program',
                'Core Competency Pathway',
                'Essential Skills Mastery',
                'Basic Training Excellence',
                'Fundamental Skills Program',
                'Core Learning Pathway'
            ],
            'application': [
                'Applied Skills Program',
                'Practical Implementation Pathway',
                'Real-world Application Mastery',
                'Hands-on Training Excellence',
                'Practical Skills Program',
                'Application Learning Pathway'
            ],
            'mastery': [
                'Advanced Skills Program',
                'Expert Level Pathway',
                'Professional Mastery Program',
                'Advanced Training Excellence',
                'Expert Skills Program',
                'Mastery Learning Pathway'
            ],
            'core': [
                'Core Skills Program',
                'Essential Training Pathway',
                'Primary Skills Mastery',
                'Basic Training Excellence',
                'Core Learning Program',
                'Essential Skills Pathway'
            ],
            'specialized': [
                'Specialized Skills Program',
                'Advanced Training Pathway',
                'Expert Skills Mastery',
                'Specialized Training Excellence',
                'Advanced Skills Program',
                'Expert Training Pathway'
            ],
            'comprehensive': [
                'Complete Training Program',
                'Full-Spectrum Pathway',
                'Comprehensive Skills Mastery',
                'Complete Training Excellence',
                'Full Training Program',
                'Comprehensive Learning Pathway'
            ]
        }
        
        # Get pathway names for the theme
        if theme in theme_pathways:
            pathway_names = theme_pathways[theme]
            # Use pathway number to select different name
            index = (pathway_number - 1) % len(pathway_names)
            pathway_name = pathway_names[index]
        else:
            # Create unique fallback naming based on pathway number and training type
            fallback_names = [
                f"{training_type} Excellence Program",
                f"{training_type} Mastery Pathway",
                f"{training_type} Skills Program",
                f"{training_type} Training Excellence",
                f"{training_type} Learning Pathway",
                f"{training_type} Development Program"
            ]
            index = (pathway_number - 1) % len(fallback_names)
            pathway_name = fallback_names[index]
        
        # Add industry context if available
        if industry and industry.lower() != 'general':
            pathway_name = f"{pathway_name} - {industry.title()}"
        
        return pathway_name
        
    except Exception as e:
        debug_print(f"⚠️ Theme-based pathway name generation failed: {e}")
        # Create unique fallback names
        fallback_names = [
            f"{training_type} Excellence Program",
            f"{training_type} Mastery Pathway", 
            f"{training_type} Skills Program"
        ]
        index = (pathway_number - 1) % len(fallback_names)
        pathway_name = fallback_names[index]
        if industry and industry.lower() != 'general':
            pathway_name = f"{pathway_name} - {industry.title()}"
        return pathway_name

def create_fast_company_specific_pathways(modules, training_context):
    """
    Create company-specific pathways quickly without AI calls with unique naming
    """
    try:
        if not modules:
            return []
        
        debug_print(f"🚀 **Fast Company-Specific Pathway Creation:** {len(modules)} modules")
        
        # Get company context for pathway naming
        training_type = training_context.get('training_type', 'Onboarding')
        target_audience = training_context.get('target_audience', 'New Employees')
        industry = training_context.get('industry', 'General')
        primary_goals = training_context.get('primary_goals', '')
        
        # Create unique pathways based on module count and content
        if len(modules) <= 3:
            # Single comprehensive pathway with unique name
            pathway_name = generate_unique_pathway_name_from_theme(training_type, 'comprehensive', primary_goals, industry, 1)
            return [{
                'pathway_name': pathway_name,
                'sections': [{
                    'title': generate_unique_section_name(['Comprehensive'], 1),
                    'modules': modules
                }],
                'module_count': len(modules)
            }]
        elif len(modules) <= 6:
            # Two logical pathways with unique names
            mid_point = len(modules) // 2
            pathway1_name = generate_unique_pathway_name_from_theme(training_type, 'core', primary_goals, industry, 1)
            pathway2_name = generate_unique_pathway_name_from_theme(training_type, 'specialized', primary_goals, industry, 2)
            
            return [
                {
                    'pathway_name': pathway1_name,
                    'sections': [{
                        'title': generate_unique_section_name(['Core'], 1),
                        'modules': modules[:mid_point]
                    }],
                    'module_count': mid_point
                },
                {
                    'pathway_name': pathway2_name,
                    'sections': [{
                        'title': generate_unique_section_name(['Specialized'], 2),
                        'modules': modules[mid_point:]
                    }],
                    'module_count': len(modules) - mid_point
                }
            ]
        else:
            # Three comprehensive pathways with unique names
            third = len(modules) // 3
            pathway1_name = generate_unique_pathway_name_from_theme(training_type, 'foundation', primary_goals, industry, 1)
            pathway2_name = generate_unique_pathway_name_from_theme(training_type, 'application', primary_goals, industry, 2)
            pathway3_name = generate_unique_pathway_name_from_theme(training_type, 'mastery', primary_goals, industry, 3)
            
            return [
                {
                    'pathway_name': pathway1_name,
                    'sections': [{
                        'title': generate_unique_section_name(['Foundation'], 1),
                        'modules': modules[:third]
                    }],
                    'module_count': third
                },
                {
                    'pathway_name': pathway2_name,
                    'sections': [{
                        'title': generate_unique_section_name(['Application'], 2),
                        'modules': modules[third:2*third]
                    }],
                    'module_count': third
                },
                {
                    'pathway_name': pathway3_name,
                    'sections': [{
                        'title': generate_unique_section_name(['Mastery'], 3),
                        'modules': modules[2*third:]
                    }],
                    'module_count': len(modules) - 2*third
                }
            ]
        
    except Exception as e:
        debug_print(f"⚠️ Fast company-specific pathway creation failed: {str(e)}")
        return []

def generate_unique_pathway_name(training_type, themes, primary_goals, industry):
    """
    Generate unique pathway names based on training context and themes
    """
    try:
        # Extract key concepts from primary goals
        goal_words = []
        if primary_goals:
            goal_words = [word.lower() for word in primary_goals.split() 
                         if len(word) >= 4 and word.lower() not in ['the', 'and', 'for', 'with', 'that', 'this', 'learn', 'how', 'what', 'when', 'where', 'why']]
        
        # Industry-specific pathway names
        industry_pathways = {
            'manufacturing': ['Production Excellence', 'Quality Assurance', 'Safety First', 'Process Optimization'],
            'healthcare': ['Patient Care', 'Clinical Procedures', 'Safety Protocols', 'Medical Excellence'],
            'technology': ['Technical Mastery', 'Development Skills', 'System Operations', 'Innovation Lab'],
            'finance': ['Financial Operations', 'Compliance Excellence', 'Risk Management', 'Client Services'],
            'education': ['Learning Excellence', 'Teaching Methods', 'Student Engagement', 'Curriculum Development'],
            'retail': ['Customer Service', 'Sales Excellence', 'Inventory Management', 'Store Operations'],
            'construction': ['Safety Protocols', 'Project Management', 'Quality Control', 'Site Operations'],
            'transportation': ['Safety First', 'Route Optimization', 'Vehicle Operations', 'Customer Service']
        }
        
        # Training type specific names
        training_type_names = {
            'onboarding': ['New Employee Journey', 'Welcome Program', 'Integration Pathway', 'First Steps'],
            'skills development': ['Skill Building', 'Competency Development', 'Expertise Growth', 'Mastery Track'],
            'compliance': ['Regulatory Excellence', 'Compliance Mastery', 'Standards Adherence', 'Policy Implementation'],
            'process training': ['Process Excellence', 'Workflow Mastery', 'Procedure Implementation', 'Operational Excellence'],
            'leadership': ['Leadership Development', 'Management Excellence', 'Team Leadership', 'Strategic Thinking'],
            'technical': ['Technical Excellence', 'System Mastery', 'Technology Implementation', 'Expert Development']
        }
        
        # Theme-based pathway names
        theme_pathways = {
            'safety': ['Safety Excellence', 'Protection Protocols', 'Risk Management', 'Safety First'],
            'quality': ['Quality Excellence', 'Standards Mastery', 'Quality Control', 'Excellence Track'],
            'process': ['Process Excellence', 'Workflow Mastery', 'Procedure Implementation', 'Operational Excellence'],
            'equipment': ['Equipment Mastery', 'Tool Operations', 'System Management', 'Technical Excellence'],
            'communication': ['Communication Excellence', 'Collaboration Skills', 'Team Dynamics', 'Interpersonal Mastery'],
            'documentation': ['Documentation Excellence', 'Record Management', 'Information Systems', 'Knowledge Management']
        }
        
        # Generate pathway name based on context
        pathway_name = ""
        
        # Try industry-specific naming first
        if industry.lower() in industry_pathways:
            pathway_name = industry_pathways[industry.lower()][0]
        # Try training type specific naming
        elif training_type.lower() in training_type_names:
            pathway_name = training_type_names[training_type.lower()][0]
        # Try theme-based naming
        elif themes and themes[0].lower() in theme_pathways:
            pathway_name = theme_pathways[themes[0].lower()][0]
        # Use goal-based naming
        elif goal_words:
            pathway_name = f"{goal_words[0].title()} Excellence"
        # Fallback to generic but unique name
        else:
            pathway_name = f"{training_type} Excellence Pathway"
        
        # Add industry context if available
        if industry and industry.lower() != 'general':
            pathway_name = f"{pathway_name} - {industry.title()}"
        
        return pathway_name
        
    except Exception as e:
        debug_print(f"⚠️ Pathway name generation failed: {e}")
        return f"{training_type} Excellence Pathway"

def generate_unique_section_name(themes, section_number):
    """
    Generate unique section names based on themes and context
    """
    try:
        if not themes:
            return f"Section {section_number}"
        
        theme = themes[0].lower()
        
        # Theme-specific section names
        theme_sections = {
            'safety': ['Safety Fundamentals', 'Protection Protocols', 'Risk Assessment', 'Emergency Procedures'],
            'quality': ['Quality Fundamentals', 'Standards & Procedures', 'Inspection Methods', 'Quality Assurance'],
            'process': ['Process Fundamentals', 'Workflow Procedures', 'Operational Methods', 'Process Optimization'],
            'equipment': ['Equipment Fundamentals', 'Tool Operations', 'System Management', 'Technical Procedures'],
            'communication': ['Communication Fundamentals', 'Collaboration Methods', 'Team Dynamics', 'Interpersonal Skills'],
            'documentation': ['Documentation Fundamentals', 'Record Management', 'Information Systems', 'Knowledge Management'],
            'comprehensive': ['Essential Fundamentals', 'Core Procedures', 'Key Methods', 'Critical Skills'],
            'core': ['Core Fundamentals', 'Essential Procedures', 'Primary Methods', 'Basic Skills'],
            'specialized': ['Specialized Procedures', 'Advanced Methods', 'Expert Skills', 'Advanced Applications'],
            'foundation': ['Foundation Skills', 'Basic Procedures', 'Essential Methods', 'Core Fundamentals'],
            'application': ['Applied Procedures', 'Practical Methods', 'Implementation Skills', 'Real-world Applications'],
            'mastery': ['Mastery Skills', 'Advanced Procedures', 'Expert Methods', 'Professional Excellence']
        }
        
        # Get section names for the theme
        if theme in theme_sections:
            section_names = theme_sections[theme]
            # Use section number to select appropriate name
            index = min(section_number - 1, len(section_names) - 1)
            return section_names[index]
        
        # Fallback to theme-based naming
        return f"{theme.title()} {section_number}"
        
    except Exception as e:
        debug_print(f"⚠️ Section name generation failed: {e}")
        return f"Section {section_number}"

def analyze_module_themes(modules, training_context):
    """
    Analyze modules to identify common themes for pathway creation with enhanced detection
    """
    try:
        themes = []
        theme_scores = {}
        
        for module in modules:
            content = module.get('content', '').lower()
            title = module.get('title', '').lower()
            description = module.get('description', '').lower()
            
            # Enhanced theme detection with scoring
            theme_keywords = {
                'safety': ['safety', 'ppe', 'protective', 'hazard', 'risk', 'emergency', 'accident', 'injury', 'prevention'],
                'quality': ['quality', 'inspection', 'control', 'standard', 'specification', 'testing', 'verification', 'assurance'],
                'process': ['process', 'procedure', 'workflow', 'method', 'technique', 'system', 'operation', 'protocol'],
                'equipment': ['equipment', 'tool', 'operation', 'maintenance', 'calibration', 'installation', 'configuration'],
                'communication': ['communication', 'meeting', 'collaboration', 'teamwork', 'presentation', 'discussion', 'coordination'],
                'documentation': ['documentation', 'record', 'report', 'form', 'checklist', 'log', 'file', 'database'],
                'technical': ['technical', 'engineering', 'design', 'architecture', 'system', 'component', 'interface', 'api'],
                'compliance': ['compliance', 'regulation', 'policy', 'guideline', 'requirement', 'standard', 'audit', 'certification'],
                'leadership': ['leadership', 'management', 'supervision', 'coordination', 'decision', 'strategy', 'planning'],
                'customer': ['customer', 'client', 'service', 'support', 'satisfaction', 'experience', 'interaction']
            }
            
            # Score each theme based on keyword matches
            for theme, keywords in theme_keywords.items():
                score = 0
                for keyword in keywords:
                    if keyword in content or keyword in title or keyword in description:
                        score += 1
                
                if score > 0:
                    if theme not in theme_scores:
                        theme_scores[theme] = 0
                    theme_scores[theme] += score
        
        # Get top themes by score
        if theme_scores:
            sorted_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)
            themes = [theme for theme, score in sorted_themes[:3]]  # Top 3 themes
        
        # If no themes found, use default themes based on training context
        if not themes:
            training_type = training_context.get('training_type', '').lower()
            if 'safety' in training_type or 'compliance' in training_type:
                themes = ['Safety', 'Compliance']
            elif 'quality' in training_type:
                themes = ['Quality', 'Process']
            elif 'technical' in training_type:
                themes = ['Technical', 'Equipment']
            elif 'leadership' in training_type:
                themes = ['Leadership', 'Communication']
            else:
                themes = ['Process', 'Communication', 'Documentation']
        
        debug_print(f"🎯 **Identified themes:** {themes}")
        return themes
        
    except Exception as e:
        debug_print(f"⚠️ Theme analysis failed: {str(e)}")
        return ['Process', 'Communication', 'Documentation']

def analyze_pathway_theme(modules, training_context):
    """
    Analyze a group of modules to determine the pathway theme with enhanced detection
    """
    try:
        themes = analyze_module_themes(modules, training_context)
        if themes:
            return themes[0]  # Return the most common theme
        else:
            # Enhanced fallback theme detection based on training context
            training_type = training_context.get('training_type', '').lower()
            primary_goals = training_context.get('primary_goals', '').lower()
            
            # Check for specific themes in training context
            if any(word in training_type or word in primary_goals for word in ['safety', 'ppe', 'protective', 'hazard']):
                return 'Safety'
            elif any(word in training_type or word in primary_goals for word in ['quality', 'inspection', 'control', 'standard']):
                return 'Quality'
            elif any(word in training_type or word in primary_goals for word in ['process', 'procedure', 'workflow', 'method']):
                return 'Process'
            elif any(word in training_type or word in primary_goals for word in ['equipment', 'tool', 'operation', 'technical']):
                return 'Equipment'
            elif any(word in training_type or word in primary_goals for word in ['communication', 'meeting', 'collaboration', 'team']):
                return 'Communication'
            elif any(word in training_type or word in primary_goals for word in ['documentation', 'record', 'report', 'file']):
                return 'Documentation'
            elif any(word in training_type or word in primary_goals for word in ['leadership', 'management', 'supervision']):
                return 'Leadership'
            elif any(word in training_type or word in primary_goals for word in ['customer', 'client', 'service']):
                return 'Customer'
            else:
                # Default themes based on pathway position (if we can determine it)
                return 'Process'  # Default to process theme
        
    except Exception as e:
        debug_print(f"⚠️ Pathway theme analysis failed: {str(e)}")
        return 'Process'  # Default fallback

def extract_modules_from_file_content(filename, content, training_context, bypass_filtering=False, preserve_original_content=False):
    """
    Extract content from uploaded files that aligns with primary training goals.
    Focus on actual file content and training goals.
    """
    try:
        debug_print(f"📄 **Extracting content from {filename}**")
        debug_print(f"📄 Content length: {len(content)} characters")
        debug_print(f"🎯 Training goals: {training_context.get('primary_goals', 'Not specified')}")
        
        if not content or len(content.strip()) < 50:
            debug_print(f"⚠️ {filename} has insufficient content for extraction")
            return []
        
        # Get training goals for content analysis
        primary_goals = training_context.get('primary_goals', '')
        training_type = training_context.get('training_type', 'Training')
        target_audience = training_context.get('target_audience', 'employees')
        industry = training_context.get('industry', 'general')
        
        debug_print(f"📋 Training type: {training_type}")
        debug_print(f"👥 Target audience: {target_audience}")
        debug_print(f"🏢 Industry: {industry}")
        
        # Extract training-relevant information directly from content
        if preserve_original_content:
            # For structured content, preserve original with minimal processing
            training_info = [content] if content and len(content.strip()) > 100 else []
        else:
            # Use training goals to extract relevant content
            training_info = extract_training_information_from_content(content, training_context)
        
        if not training_info:
            debug_print(f"⚠️ No training-relevant information found in {filename}")
            # Use original content as fallback
            debug_print(f"🔄 Using original content as fallback")
            training_info = [content] if content and len(content.strip()) > 100 else []
        
        debug_print(f"📄 **Training Information Extracted:** {len(training_info)} sections")
        
        modules = []
        
        # Get performance configuration
        config = get_parallel_config()
        max_modules = config.get('max_modules_per_file', 10)
        batch_ai_calls = config.get('batch_ai_calls', True)
        
        # Create modules from training-relevant information
        for i, info_section in enumerate(training_info[:max_modules]):  # Limit modules for speed
            if len(info_section.strip()) > 100:  # Minimum length for quality
                debug_print(f"🔧 Creating module {i+1} from content section")
                debug_print(f"📄 Section content length: {len(info_section)} characters")
                
                # Use AI-powered module creation with optimized approach
                cohesive_module = create_cohesive_module_content_optimized(info_section, training_context, i+1, batch_ai_calls)
                if cohesive_module:
                    # Add debugging source information to content
                    debug_source = f"\n\n--- DEBUG SOURCE ---\nContent extracted from: {filename}\nModule created by: Cohesive module creation\nContent length: {len(cohesive_module['content'])} characters\nTraining goals: {training_context.get('primary_goals', 'Not specified')}\n--- END DEBUG SOURCE ---\n\n"
                    content_with_debug = debug_source + cohesive_module['content']
                    
                    modules.append({
                        'title': cohesive_module['title'],
                        'description': cohesive_module['description'],
                        'content': content_with_debug,
                        'source': clean_source_field(f'Training information from {filename}'),
                        'key_points': extract_key_points_from_content(info_section, training_context),
                        'relevance_score': 0.9,  # High relevance since it's filtered and cohesive
                        'full_reason': f'Cohesive training content focused on {cohesive_module["core_topic"]}',
                        'content_types': cohesive_module.get('content_types', generate_fallback_content_types(info_section, training_context))
                    })
                    debug_print(f"✅ Module {i+1} created successfully with debug source info")
                else:
                    debug_print(f"⚠️ Module {i+1} creation failed")
        
        debug_print(f"✅ Extracted {len(modules)} cohesive training modules from {filename}")
        return modules
        
    except Exception as e:
        debug_print(f"⚠️ Training content extraction failed for {filename}: {str(e)}")
        return []

def extract_training_information_from_content(content, training_context):
    """
    Extract training-relevant information from content using simple methods
    Focus on actual file content and training goals
    """
    try:
        debug_print(f"🔍 **Extracting training information from content**")
        debug_print(f"📄 Content length: {len(content)} characters")
        debug_print(f"🎯 Training goals: {training_context.get('primary_goals', 'Not specified')}")
        
        # Get training goals for content analysis
        primary_goals = training_context.get('primary_goals', '')
        training_type = training_context.get('training_type', 'Training')
        target_audience = training_context.get('target_audience', 'employees')
        industry = training_context.get('industry', 'general')
        
        debug_print(f"📋 Training type: {training_type}")
        debug_print(f"👥 Target audience: {target_audience}")
        debug_print(f"🏢 Industry: {industry}")
        
        # First, try to extract and transform any relevant content
        transformed_content = extract_and_transform_content(content, training_context)
        
        if not transformed_content:
            debug_print("⚠️ No transformed content available, using original content")
            transformed_content = content
        
        # Use training goals to generate relevant keywords
        relevant_keywords = get_training_keywords_from_goals(training_context)
        
        debug_print(f"🎯 **Keywords from training goals:** {relevant_keywords[:10]}...")
        
        # Extract sentences that match training goals
        training_sentences = extract_goal_aligned_sentences(transformed_content, training_context)
        
        # If no goal-aligned sentences, try broader extraction
        if not training_sentences:
            debug_print("🔄 No goal-aligned sentences found, trying broader content extraction...")
            training_sentences = extract_broader_training_content(transformed_content, training_context)
        
        # If still no sentences, use the original content
        if not training_sentences:
            debug_print("🔄 No training sentences found, using original content sections...")
            training_sentences = extract_content_sections(transformed_content)
        
        debug_print(f"📄 **Training sentences extracted:** {len(training_sentences)}")
        
        # Group related sentences into training sections
        training_sections = group_sentences_basic(training_sentences)
        
        debug_print(f"📚 **Training sections created:** {len(training_sections)}")
        
        return training_sections
        
    except Exception as e:
        debug_print(f"⚠️ Training information extraction failed: {str(e)}")
        # Fallback to basic extraction
        return extract_training_information_basic(content, training_context)

def get_training_keywords_from_goals(training_context):
    """
    Generate keywords based on training goals and context
    """
    try:
        primary_goals = training_context.get('primary_goals', '').lower()
        training_type = training_context.get('training_type', '').lower()
        target_audience = training_context.get('target_audience', '').lower()
        industry = training_context.get('industry', '').lower()
        
        keywords = []
        
        # Extract keywords from primary goals
        if primary_goals:
            goal_words = [word for word in primary_goals.split() 
                         if len(word) >= 4 and word not in ['the', 'and', 'for', 'with', 'that', 'this', 'how', 'what', 'when', 'where', 'why']]
            keywords.extend(goal_words)
        
        # Add context-specific keywords
        if 'bridge' in primary_goals or 'fabrication' in primary_goals:
            keywords.extend(['bridge', 'fabrication', 'welding', 'steel', 'construction', 'assembly'])
        
        if 'process' in training_type:
            keywords.extend(['process', 'procedure', 'workflow', 'method', 'technique'])
        
        if 'safety' in training_type or 'safety' in primary_goals:
            keywords.extend(['safety', 'ppe', 'protective', 'hazard', 'risk'])
        
        if 'quality' in training_type or 'quality' in primary_goals:
            keywords.extend(['quality', 'inspection', 'testing', 'verification', 'standard'])
        
        if 'manufacturing' in industry:
            keywords.extend(['manufacturing', 'production', 'assembly', 'equipment', 'tool'])
        
        if 'transportation' in industry:
            keywords.extend(['transportation', 'logistics', 'delivery', 'routing', 'fleet'])
        
        # Add general training keywords
        keywords.extend(['training', 'learning', 'skill', 'knowledge', 'competency'])
        
        # Remove duplicates and limit
        unique_keywords = list(set(keywords))
        return unique_keywords[:20]
        
    except Exception as e:
        debug_print(f"⚠️ Keyword generation failed: {str(e)}")
        return ['training', 'learning', 'skill', 'knowledge']

def extract_goal_aligned_sentences(content, training_context):
    """
    Extract sentences that align with training goals
    """
    try:
        primary_goals = training_context.get('primary_goals', '').lower()
        keywords = get_training_keywords_from_goals(training_context)
        
        sentences = re.split(r'[.!?]+', content)
        aligned_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Minimum sentence length
                sentence_lower = sentence.lower()
                
                # Check if sentence contains goal-related keywords
                keyword_matches = sum(1 for keyword in keywords if keyword in sentence_lower)
                
                # Accept if it has keyword matches OR contains goal-related content
                if keyword_matches >= 1:
                    aligned_sentences.append(sentence)
                elif primary_goals and any(goal_word in sentence_lower for goal_word in primary_goals.split()):
                    aligned_sentences.append(sentence)
                # Also accept substantial sentences that might contain valuable info
                elif len(sentence) > 50:
                    aligned_sentences.append(sentence)
        
        return aligned_sentences
        
    except Exception as e:
        debug_print(f"⚠️ Goal-aligned extraction failed: {str(e)}")
        return []

def extract_content_sections(content):
    """
    Extract content sections when no training-specific content is found
    """
    try:
        sentences = re.split(r'[.!?]+', content)
        content_sections = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30:  # Accept substantial sentences
                content_sections.append(sentence)
        
        return content_sections
            
    except Exception as e:
        debug_print(f"⚠️ Content section extraction failed: {str(e)}")
        return []

def extract_broader_training_content(content, training_context):
    """
    Extract training content more broadly when keyword matching fails
    """
    try:
        sentences = re.split(r'[.!?]+', content)
        training_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Minimum sentence length
                # Accept sentences that contain training-related concepts
                sentence_lower = sentence.lower()
                
                # Check for training-related patterns
                training_patterns = [
                    'process', 'procedure', 'workflow', 'method', 'technique',
                    'safety', 'quality', 'inspection', 'testing', 'verification',
                    'equipment', 'tool', 'operation', 'maintenance', 'calibration',
                    'material', 'handling', 'storage', 'transportation',
                    'documentation', 'record', 'report', 'form', 'checklist',
                    'standard', 'specification', 'requirement', 'guideline',
                    'training', 'learning', 'skill', 'knowledge', 'competency'
                ]
                
                # Accept if sentence contains any training pattern
                if any(pattern in sentence_lower for pattern in training_patterns):
                    training_sentences.append(sentence)
                # Also accept substantial sentences (they might contain valuable info)
                elif len(sentence) > 50:
                    training_sentences.append(sentence)
        
        return training_sentences
        
    except Exception as e:
        debug_print(f"⚠️ Broader content extraction failed: {str(e)}")
        return []

def extract_training_information_basic(content, training_context):
    """
    Basic fallback for training information extraction
    """
    # Simple sentence splitting and filtering
    sentences = re.split(r'[.!?]+', content)
    training_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 50 and len(sentence) < 500:
            # Basic filtering
            if not any(conv in sentence.lower() for conv in ['um', 'uh', 'yeah', 'okay']):
                training_sentences.append(sentence)
    
    # Simple grouping
    return group_sentences_basic(training_sentences)

def group_sentences_basic(sentences):
    """
    Basic fallback for sentence grouping
    """
    if not sentences:
        return []
    
    # Simple grouping: 3 sentences per section
    sections = []
    current_section = []
    
    for sentence in sentences:
        current_section.append(sentence)
        if len(current_section) >= 3:
            sections.append('. '.join(current_section) + '.')
            current_section = []
    
    # Add remaining sentences
    if current_section:
        sections.append('. '.join(current_section) + '.')
    
    return sections

def create_cohesive_module_content_optimized(content, training_context, module_number, batch_ai_calls=True):
    """
    Create cohesive title, description, and content that work together as a unit
    Focus on actual file content and training goals with content type generation
    """
    try:
        debug_print(f"🔧 **Creating module {module_number} from content**")
        debug_print(f"📄 Content length: {len(content)} characters")
        debug_print(f"🎯 Training goals: {training_context.get('primary_goals', 'Not specified')}")
        
        # First, validate that the content is actually meaningful
        if not is_meaningful_training_content(content, training_context):
            debug_print(f"⚠️ Module {module_number}: Content not meaningful, using anyway")
        
        if not model:
            # Fallback to simple approach without AI
            title = extract_first_sentence_title(content)
            description = f"Training content from uploaded file - Module {module_number}"
            cleaned_content = clean_content_basic(content)
            
            return {
                'title': f'Module {module_number}: {title}',
                'description': description,
                'content': cleaned_content,
                'core_topic': 'Training Content',
                'learning_objectives': ['Understand key concepts', 'Learn practical skills', 'Apply knowledge'],
                'content_types': generate_fallback_content_types(cleaned_content, training_context)
            }
        
        # Use Gemini API to create better titles and descriptions with content types
        training_type = training_context.get('training_type', 'Training')
        target_audience = training_context.get('target_audience', 'employees')
        industry = training_context.get('industry', 'general')
        primary_goals = training_context.get('primary_goals', '')
        
        prompt = f"""
        Create a professional training module from this content with specific content types.
        
        Content:
        {content[:2000]}
        
        Training Context:
        - Type: {training_type}
        - Target Audience: {target_audience}
        - Industry: {industry}
        - Primary Goals: {primary_goals}
        - Module Number: {module_number}
        
        REQUIREMENTS:
        1. Create a clear, professional title (max 60 characters) that reflects the actual content
        2. Write a concise description (1-2 sentences) that describes what the module covers
        3. Transform the content into professional training material
        4. Focus on actionable training information from the actual content
        5. Make it suitable for {target_audience} in {industry}
        6. Remove conversational elements and informal language
        7. Structure content with clear sections
        8. Extract and preserve important technical information and procedures
        9. Use the actual content, not generic placeholder text
        10. If the content contains specific procedures, processes, or technical information, highlight these
        11. Align with training goals: {primary_goals}
        12. Generate 1-3 content types that would best enhance this module's learning experience
        
        CONTENT TYPES TO CHOOSE FROM:
        - text: Explanatory text content
        - list: Bullet points or numbered lists
        - image: Visual content descriptions
        - flashcards: Key concept cards for memorization
        - video: Short video descriptions for demonstrations
        - file: Downloadable resources or templates
        - accordion: Expandable content sections
        - divider: Visual separators
        - tabs: Organized content in tabs
        - knowledge_check: Quiz or assessment questions
        - survey: Feedback or evaluation questions
        - assignment: Practical exercises or tasks
        
        Return as JSON:
        {{
            "title": "Professional module title based on actual content",
            "description": "Clear description of what this specific module covers",
            "content": "Transformed professional training content from the actual file",
            "content_types": [
                {{
                    "type": "content_type_name",
                    "title": "Content type title",
                    "description": "How this content type should be generated",
                    "content": "Specific content or instructions for this content type"
                }}
            ]
        }}
        """
        
        response = model.generate_content(prompt)
        raw = response.text.strip()
        
        # Extract JSON from response with better error handling
        module_data = extract_json_from_ai_response(raw)
        
        if module_data and isinstance(module_data, dict):
            title = module_data.get('title', f'Module {module_number}')
            description = module_data.get('description', f'Training content from uploaded file - Module {module_number}')
            transformed_content = module_data.get('content', content)
            content_types = module_data.get('content_types', [])
            
            # Validate the extracted data
            if not title or len(title.strip()) < 3:
                title = f'Module {module_number}'
            if not description or len(description.strip()) < 10:
                description = f'Training content from uploaded file - Module {module_number}'
            if not transformed_content or len(transformed_content.strip()) < 50:
                transformed_content = clean_content_basic(content)
            
            # Generate content types if not provided or invalid
            if not content_types or not isinstance(content_types, list):
                content_types = generate_content_types_with_ai(transformed_content, training_context)
            
            return {
                'title': f'Module {module_number}: {title}',
                'description': description,
                'content': transformed_content,
                'core_topic': 'Training Content',
                'learning_objectives': ['Understand key concepts', 'Learn practical skills', 'Apply knowledge'],
                'content_types': content_types
            }
        else:
            # Fallback to simple approach when JSON parsing fails
            debug_print(f"⚠️ Module {module_number}: JSON parsing failed, using fallback")
            title = extract_first_sentence_title(content)
            description = f"Training content from uploaded file - Module {module_number}"
            cleaned_content = clean_content_basic(content)
            content_types = generate_content_types_with_ai(cleaned_content, training_context)
            
            return {
                'title': f'Module {module_number}: {title}',
                'description': description,
                'content': cleaned_content,
                'core_topic': 'Training Content',
                'learning_objectives': ['Understand key concepts', 'Learn practical skills', 'Apply knowledge'],
                'content_types': content_types
            }
        
    except Exception as e:
        debug_print(f"⚠️ Optimized module creation failed: {str(e)}")
        # Ultimate fallback
        try:
            title = extract_first_sentence_title(content)
            description = f"Training content from uploaded file - Module {module_number}"
            cleaned_content = clean_content_basic(content)
            content_types = generate_fallback_content_types(cleaned_content, training_context)
            
            return {
                'title': f'Module {module_number}: {title}',
                'description': description,
                'content': cleaned_content,
                'core_topic': 'Training Content',
                'learning_objectives': ['Understand key concepts', 'Learn practical skills', 'Apply knowledge'],
                'content_types': content_types
            }
        except Exception as fallback_error:
            debug_print(f"⚠️ Ultimate fallback also failed: {str(fallback_error)}")
        return None

def generate_content_types_with_ai(module_content, training_context):
    """
    Use Gemini API to determine the best content types for a module and generate actual content
    """
    try:
        if not model:
            return generate_fallback_content_types(module_content, training_context)
        
        training_type = training_context.get('training_type', 'Training')
        target_audience = training_context.get('target_audience', 'employees')
        industry = training_context.get('industry', 'general')
        primary_goals = training_context.get('primary_goals', '')
        
        prompt = f"""
        Analyze this training module content and determine the best content types to enhance learning.
        
        MODULE CONTENT:
        {module_content[:1500]}
        
        TRAINING CONTEXT:
        - Type: {training_type}
        - Target Audience: {target_audience}
        - Industry: {industry}
        - Primary Goals: {primary_goals}
        
        CONTENT TYPES AVAILABLE:
        - text: Explanatory text content
        - list: Bullet points or numbered lists
        - image: Visual content descriptions
        - flashcards: Key concept cards for memorization
        - video: Short video descriptions for demonstrations
        - file: Downloadable resources or templates
        - accordion: Expandable content sections
        - divider: Visual separators
        - tabs: Organized content in tabs
        - knowledge_check: Quiz or assessment questions
        - survey: Feedback or evaluation questions
        - assignment: Practical exercises or tasks
        
        REQUIREMENTS:
        1. Select 1-3 content types that would best enhance this module's learning experience
        2. Consider the module's content and training goals
        3. Choose content types that complement the existing content
        4. For each content type, generate the ACTUAL content (not just descriptions)
        5. For videos, provide a written description of what the video should show
        6. Make content specific to the module's actual content and training goals
        7. Generate REAL content for each type, not placeholder text
        
        Return as JSON array:
        [
            {{
                "type": "content_type_name",
                "title": "Descriptive title for this content type",
                "description": "How this content type should be generated",
                "content": "ACTUAL GENERATED CONTENT for this content type"
            }}
        ]
        """
        
        response = model.generate_content(prompt)
        raw = response.text.strip()
        
        # Extract JSON from response
        content_types_data = extract_json_from_ai_response(raw)
        
        if content_types_data and isinstance(content_types_data, list):
            # Validate and clean content types, then generate actual content
            valid_content_types = []
            for content_type in content_types_data:
                if isinstance(content_type, dict):
                    content_type_name = content_type.get('type', '').lower()
                    if content_type_name in ['text', 'list', 'image', 'flashcards', 'video', 'file', 'accordion', 'divider', 'tabs', 'knowledge_check', 'survey', 'assignment']:
                        # Generate actual content for this content type using Gemini
                        generated_content = generate_actual_content_for_type(
                            content_type_name, 
                            module_content, 
                            training_context,
                            content_type.get('title', '')
                        )
                        
                        valid_content_types.append({
                            'type': content_type_name,
                            'title': content_type.get('title', f'{content_type_name.title()} Content'),
                            'description': content_type.get('description', ''),
                            'content': generated_content
                        })
            
            debug_print(f"✅ Generated {len(valid_content_types)} content types with actual Gemini content for module")
            return valid_content_types[:3]  # Limit to 3 content types
        
        # If AI content type selection failed, generate all content types with Gemini
        debug_print(f"⚠️ AI content type selection failed, generating all content types with Gemini")
        return generate_all_content_types_with_gemini(module_content, training_context)
        
    except Exception as e:
        debug_print(f"⚠️ AI content type generation failed: {e}")
        # Generate all content types with Gemini as fallback
        return generate_all_content_types_with_gemini(module_content, training_context)

def generate_all_content_types_with_gemini(module_content, training_context):
    """
    Generate all content types using Gemini API when content type selection fails
    """
    try:
        if not model:
            return generate_fallback_content_types(module_content, training_context)
        
        debug_print(f"🔄 Generating all content types with Gemini API")
        
        # Select the best 3 content types based on module content
        content_lower = module_content.lower()
        selected_types = []
        
        # Determine content types based on content analysis
        if any(word in content_lower for word in ['procedure', 'process', 'step', 'method']):
            selected_types.append('list')
        if any(word in content_lower for word in ['safety', 'ppe', 'protective', 'hazard']):
            selected_types.append('flashcards')
        if any(word in content_lower for word in ['quality', 'inspection', 'standard', 'requirement']):
            selected_types.append('knowledge_check')
        if any(word in content_lower for word in ['equipment', 'tool', 'operation', 'maintenance']):
            selected_types.append('video')
        if any(word in content_lower for word in ['documentation', 'record', 'report', 'form']):
            selected_types.append('file')
        
        # Add general content types if none specific found
        if not selected_types:
            selected_types = ['text', 'knowledge_check', 'assignment']
        elif len(selected_types) < 3:
            # Add more content types to reach 3
            additional_types = ['text', 'survey', 'accordion', 'tabs']
            for content_type in additional_types:
                if content_type not in selected_types and len(selected_types) < 3:
                    selected_types.append(content_type)
        
        # Generate actual content for each selected type
        content_types = []
        for content_type in selected_types[:3]:
            generated_content = generate_actual_content_for_type(
                content_type, 
                module_content, 
                training_context,
                f"{content_type.title()} Content"
            )
            
            content_types.append({
                'type': content_type,
                'title': f"{content_type.title()} Content",
                'description': f"Generated {content_type} content for this module",
                'content': generated_content
            })
        
        debug_print(f"✅ Generated {len(content_types)} content types with Gemini")
        return content_types
        
    except Exception as e:
        debug_print(f"⚠️ All content type generation failed: {e}")
        return generate_fallback_content_types(module_content, training_context)

def generate_actual_content_for_type(content_type, module_content, training_context, content_title):
    """
    Generate actual content for a specific content type using Gemini API
    """
    try:
        if not model:
            return f"Content for {content_type} - {content_title}"
        
        training_type = training_context.get('training_type', 'Training')
        target_audience = training_context.get('target_audience', 'employees')
        industry = training_context.get('industry', 'general')
        primary_goals = training_context.get('primary_goals', '')
        
        # Create specific prompts for each content type
        if content_type == 'text':
            prompt = f"""
            Generate explanatory text content for this training module.
            
            MODULE CONTENT:
            {module_content[:1000]}
            
            TRAINING CONTEXT:
            - Type: {training_type}
            - Target Audience: {target_audience}
            - Industry: {industry}
            - Primary Goals: {primary_goals}
            
            REQUIREMENTS:
            1. Create detailed explanatory text that expands on the module content
            2. Make it suitable for {target_audience} in {industry}
            3. Focus on key concepts and important details
            4. Use clear, professional language
            5. Align with training goals: {primary_goals}
            6. Provide 2-3 paragraphs of detailed explanation
            
            Return only the generated text content, no JSON formatting.
            """
        
        elif content_type == 'list':
            prompt = f"""
            Generate a structured list (bullet points or numbered) for this training module.
            
            MODULE CONTENT:
            {module_content[:1000]}
            
            TRAINING CONTEXT:
            - Type: {training_type}
            - Target Audience: {target_audience}
            - Industry: {industry}
            - Primary Goals: {primary_goals}
            
            REQUIREMENTS:
            1. Create a structured list of key points, steps, or concepts
            2. Use bullet points or numbered format as appropriate
            3. Make it suitable for {target_audience} in {industry}
            4. Focus on actionable items and important details
            5. Align with training goals: {primary_goals}
            6. Provide 5-8 list items
            
            Return only the list content with proper formatting (• or 1. 2. 3.), no JSON.
            """
        
        elif content_type == 'flashcards':
            prompt = f"""
            Generate flashcards for key concepts in this training module.
            
            MODULE CONTENT:
            {module_content[:1000]}
            
            TRAINING CONTEXT:
            - Type: {training_type}
            - Target Audience: {target_audience}
            - Industry: {industry}
            - Primary Goals: {primary_goals}
            
            REQUIREMENTS:
            1. Create 5-8 flashcards with question/answer format
            2. Focus on key concepts, terms, and important details
            3. Make questions suitable for {target_audience} in {industry}
            4. Align with training goals: {primary_goals}
            5. Use format: "Q: [Question] A: [Answer]"
            
            Return only the flashcards content, no JSON formatting.
            """
        
        elif content_type == 'knowledge_check':
            prompt = f"""
            Generate quiz questions to test understanding of this training module.
            
            MODULE CONTENT:
            {module_content[:1000]}
            
            TRAINING CONTEXT:
            - Type: {training_type}
            - Target Audience: {target_audience}
            - Industry: {industry}
            - Primary Goals: {primary_goals}
            
            REQUIREMENTS:
            1. Create 5-8 multiple choice questions
            2. Include 4 options (A, B, C, D) for each question
            3. Make questions suitable for {target_audience} in {industry}
            4. Focus on key concepts and important details
            5. Align with training goals: {primary_goals}
            6. Use format: "Q1: [Question] A) [Option] B) [Option] C) [Option] D) [Option]"
            
            Return only the quiz content, no JSON formatting.
            """
        
        elif content_type == 'survey':
            prompt = f"""
            Generate survey questions to gather feedback on this training module.
            
            MODULE CONTENT:
            {module_content[:1000]}
            
            TRAINING CONTEXT:
            - Type: {training_type}
            - Target Audience: {target_audience}
            - Industry: {industry}
            - Primary Goals: {primary_goals}
            
            REQUIREMENTS:
            1. Create 3-5 survey questions to evaluate training effectiveness
            2. Include rating scales and open-ended questions
            3. Focus on learning outcomes and practical application
            4. Make questions suitable for {target_audience} in {industry}
            5. Align with training goals: {primary_goals}
            
            Return only the survey content, no JSON formatting.
            """
        
        elif content_type == 'assignment':
            prompt = f"""
            Generate practical exercises or assignments for this training module.
            
            MODULE CONTENT:
            {module_content[:1000]}
            
            TRAINING CONTEXT:
            - Type: {training_type}
            - Target Audience: {target_audience}
            - Industry: {industry}
            - Primary Goals: {primary_goals}
            
            REQUIREMENTS:
            1. Create 2-3 practical exercises or assignments
            2. Focus on hands-on application of concepts
            3. Make assignments suitable for {target_audience} in {industry}
            4. Include clear instructions and objectives
            5. Align with training goals: {primary_goals}
            
            Return only the assignment content, no JSON formatting.
            """
        
        elif content_type == 'file':
            prompt = f"""
            Generate downloadable resource templates for this training module.
            
            MODULE CONTENT:
            {module_content[:1000]}
            
            TRAINING CONTEXT:
            - Type: {training_type}
            - Target Audience: {target_audience}
            - Industry: {industry}
            - Primary Goals: {primary_goals}
            
            REQUIREMENTS:
            1. Create template content for downloadable resources
            2. Include checklists, forms, or reference guides
            3. Make templates suitable for {target_audience} in {industry}
            4. Focus on practical tools and resources
            5. Align with training goals: {primary_goals}
            
            Return only the template content, no JSON formatting.
            """
        
        elif content_type == 'accordion':
            prompt = f"""
            Generate expandable content sections for this training module.
            
            MODULE CONTENT:
            {module_content[:1000]}
            
            TRAINING CONTEXT:
            - Type: {training_type}
            - Target Audience: {target_audience}
            - Industry: {industry}
            - Primary Goals: {primary_goals}
            
            REQUIREMENTS:
            1. Create 3-4 expandable sections with titles and content
            2. Organize information into logical categories
            3. Make content suitable for {target_audience} in {industry}
            4. Focus on detailed explanations and examples
            5. Align with training goals: {primary_goals}
            6. Use format: "Section 1: [Title] [Content] | Section 2: [Title] [Content]"
            
            Return only the accordion content, no JSON formatting.
            """
        
        elif content_type == 'tabs':
            prompt = f"""
            Generate organized content in tabs for this training module.
            
            MODULE CONTENT:
            {module_content[:1000]}
            
            TRAINING CONTEXT:
            - Type: {training_type}
            - Target Audience: {target_audience}
            - Industry: {industry}
            - Primary Goals: {primary_goals}
            
            REQUIREMENTS:
            1. Create 3-4 tab sections with different aspects of the topic
            2. Organize content into logical categories
            3. Make content suitable for {target_audience} in {industry}
            4. Focus on different perspectives or approaches
            5. Align with training goals: {primary_goals}
            6. Use format: "Tab 1: [Title] [Content] | Tab 2: [Title] [Content]"
            
            Return only the tabs content, no JSON formatting.
            """
        
        elif content_type == 'image':
            prompt = f"""
            Generate visual content descriptions for this training module.
            
            MODULE CONTENT:
            {module_content[:1000]}
            
            TRAINING CONTEXT:
            - Type: {training_type}
            - Target Audience: {target_audience}
            - Industry: {industry}
            - Primary Goals: {primary_goals}
            
            REQUIREMENTS:
            1. Create detailed descriptions of visual content (diagrams, charts, images)
            2. Describe what visual elements should be included
            3. Make descriptions suitable for {target_audience} in {industry}
            4. Focus on visual aids that support learning
            5. Align with training goals: {primary_goals}
            
            Return only the visual content descriptions, no JSON formatting.
            """
        
        elif content_type == 'video':
            prompt = f"""
            Generate a written description for a video demonstration for this training module.
            
            MODULE CONTENT:
            {module_content[:1000]}
            
            TRAINING CONTEXT:
            - Type: {training_type}
            - Target Audience: {target_audience}
            - Industry: {industry}
            - Primary Goals: {primary_goals}
            
            REQUIREMENTS:
            1. Create a detailed written description of what the video should show
            2. Include key scenes, demonstrations, and learning points
            3. Make description suitable for {target_audience} in {industry}
            4. Focus on visual demonstrations and practical examples
            5. Align with training goals: {primary_goals}
            6. Provide 2-3 paragraphs describing the video content
            
            Return only the video description, no JSON formatting.
            """
        
        else:
            # Default fallback
            return f"Generated content for {content_type} - {content_title}"
        
        # Generate content using Gemini API
        response = model.generate_content(prompt)
        if response.text:
            return response.text.strip()
        else:
            return f"Generated content for {content_type} - {content_title}"
        
    except Exception as e:
        debug_print(f"⚠️ Content generation for {content_type} failed: {e}")
        return f"Generated content for {content_type} - {content_title}"

def generate_fallback_content_types(module_content, training_context):
    """
    Generate fallback content types when AI is not available with actual content
    """
    try:
        # Try to use Gemini API first, even in fallback
        if model:
            debug_print(f"🔄 Using Gemini API for fallback content generation")
            return generate_all_content_types_with_gemini(module_content, training_context)
        
        # Only use basic fallback if no Gemini API available
        content_lower = module_content.lower()
        training_type = training_context.get('training_type', 'Training').lower()
        primary_goals = training_context.get('primary_goals', '').lower()
        
        content_types = []
        
        # Determine content types based on content analysis and generate actual content
        if any(word in content_lower for word in ['procedure', 'process', 'step', 'method']):
            # Generate actual list content
            list_content = generate_fallback_list_content(module_content, training_context)
            content_types.append({
                'type': 'list',
                'title': 'Step-by-Step Process',
                'description': 'Organized list of procedural steps',
                'content': list_content
            })
        
        if any(word in content_lower for word in ['safety', 'ppe', 'protective', 'hazard']):
            # Generate actual flashcards content
            flashcard_content = generate_fallback_flashcard_content(module_content, training_context)
            content_types.append({
                'type': 'flashcards',
                'title': 'Safety Key Points',
                'description': 'Important safety concepts for memorization',
                'content': flashcard_content
            })
        
        if any(word in content_lower for word in ['quality', 'inspection', 'standard', 'requirement']):
            # Generate actual knowledge check content
            quiz_content = generate_fallback_quiz_content(module_content, training_context)
            content_types.append({
                'type': 'knowledge_check',
                'title': 'Quality Standards Quiz',
                'description': 'Assessment of quality standards understanding',
                'content': quiz_content
            })
        
        if any(word in content_lower for word in ['equipment', 'tool', 'operation', 'maintenance']):
            # Generate video description
            video_content = generate_fallback_video_content(module_content, training_context)
            content_types.append({
                'type': 'video',
                'title': 'Equipment Operation Demo',
                'description': 'Video demonstration of equipment operation',
                'content': video_content
            })
        
        if any(word in content_lower for word in ['documentation', 'record', 'report', 'form']):
            # Generate file template content
            file_content = generate_fallback_file_content(module_content, training_context)
            content_types.append({
                'type': 'file',
                'title': 'Documentation Templates',
                'description': 'Downloadable templates and forms',
                'content': file_content
            })
        
        # Add general content types if none specific found
        if not content_types:
            text_content = generate_fallback_text_content(module_content, training_context)
            content_types.append({
                'type': 'text',
                'title': 'Key Concepts',
                'description': 'Explanatory text for key concepts',
                'content': text_content
            })
        
        # Add assessment if training type suggests it
        if 'compliance' in training_type or 'assessment' in primary_goals:
            quiz_content = generate_fallback_quiz_content(module_content, training_context)
            content_types.append({
                'type': 'knowledge_check',
                'title': 'Understanding Check',
                'description': 'Assessment of module understanding',
                'content': quiz_content
            })
        
        return content_types[:3]  # Limit to 3 content types
        
    except Exception as e:
        debug_print(f"⚠️ Fallback content type generation failed: {e}")
        return [{
            'type': 'text',
            'title': 'Module Content',
            'description': 'Explanatory text content',
            'content': 'Provide detailed explanations of module content'
        }]

def generate_fallback_text_content(module_content, training_context):
    """Generate fallback text content"""
    try:
        sentences = module_content.split('.')
        key_sentences = [s.strip() for s in sentences if len(s.strip()) > 20][:3]
        return ' '.join(key_sentences) + '.'
    except:
        return f"Detailed explanation of key concepts from the module content."

def generate_fallback_list_content(module_content, training_context):
    """Generate fallback list content"""
    try:
        sentences = module_content.split('.')
        key_points = [s.strip() for s in sentences if len(s.strip()) > 15][:5]
        return '\n• ' + '\n• '.join(key_points)
    except:
        return "• Step 1: [First step]\n• Step 2: [Second step]\n• Step 3: [Third step]"

def generate_fallback_flashcard_content(module_content, training_context):
    """Generate fallback flashcard content"""
    try:
        sentences = module_content.split('.')
        key_concepts = [s.strip() for s in sentences if len(s.strip()) > 20][:3]
        flashcards = []
        for i, concept in enumerate(key_concepts, 1):
            flashcards.append(f"Q{i}: What is the key concept about {concept[:30]}...?\nA{i}: {concept}")
        return '\n\n'.join(flashcards)
    except:
        return "Q1: What is the main safety principle?\nA1: [Safety principle]\n\nQ2: What PPE is required?\nA2: [PPE requirements]"

def generate_fallback_quiz_content(module_content, training_context):
    """Generate fallback quiz content"""
    try:
        return "Q1: What is the primary focus of this module?\nA) [Option A]\nB) [Option B]\nC) [Option C]\nD) [Option D]\n\nQ2: Which of the following is most important?\nA) [Option A]\nB) [Option B]\nC) [Option C]\nD) [Option D]"
    except:
        return "Q1: [Question about module content]\nA) [Option A]\nB) [Option B]\nC) [Option C]\nD) [Option D]"

def generate_fallback_video_content(module_content, training_context):
    """Generate fallback video description"""
    try:
        return f"This video should demonstrate the key concepts from the module content. It should include visual demonstrations, step-by-step procedures, and practical examples suitable for {training_context.get('target_audience', 'employees')} in {training_context.get('industry', 'general')}."
    except:
        return "Video demonstration of key concepts and procedures from this module."

def generate_fallback_file_content(module_content, training_context):
    """Generate fallback file template content"""
    try:
        return f"Template for {training_context.get('training_type', 'Training')} documentation:\n\n[Template content based on module requirements]\n\nInclude sections for:\n- Key information\n- Required fields\n- Instructions\n- Reference materials"
    except:
        return "Downloadable template for documentation and reporting requirements."

def is_meaningful_training_content(content, training_context):
    """
    Validate that content is meaningful training content
    More lenient to preserve actual file content from meeting transcripts
    """
    try:
        if not content or len(content.strip()) < 20:  # Reduced minimum length
            return False
        
        content_lower = content.lower()
        
        # Check for training keywords (more lenient)
        training_keywords = get_training_keywords(training_context)
        keyword_matches = sum(1 for keyword in training_keywords if keyword in content_lower)
        
        # Accept content if it has keywords OR is substantial content
        if keyword_matches >= 1 or len(content) > 100:  # More lenient
            return True
        
        # Check for meaningful structure (more lenient)
        sentences = content.split('.')
        meaningful_sentences = 0
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 15:  # Reduced minimum sentence length
                meaningful_sentences += 1
        
        # Accept if it has meaningful sentences OR is substantial content
        return meaningful_sentences >= 1 or len(content) > 80  # More lenient
        
    except Exception as e:
        # If validation fails, accept the content to preserve file content
        return True

def extract_first_sentence_title(content):
    """
    Extract a title from the first meaningful sentence of content
    """
    try:
        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and len(sentence) < 100:
                # Clean up the sentence
                sentence = re.sub(r'^\w+:\s*', '', sentence)  # Remove speaker prefixes
                sentence = sentence.strip()
                
                if len(sentence) > 10:
                    return sentence[:60] + "..." if len(sentence) > 60 else sentence
        
        # Fallback: use first 50 characters
        return content[:50] + "..." if len(content) > 50 else content
        
    except Exception as e:
        return "Training Content"

def clean_source_field(source):
    """
    Clean the source field to ensure it's a proper string without character splitting
    """
    if isinstance(source, str):
        # If it's already a string, return as is
        return source
    elif isinstance(source, (list, tuple)):
        # If it's a list/tuple of characters, join them
        return ''.join(source)
    else:
        # Convert to string
        return str(source)

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

def create_quick_pathway(context, extracted_file_contents, inventory):
    """
    Fast, non-AI fallback for pathway creation.
    Groups all file contents into a single pathway and section.
    """
    modules = []
    for i, (filename, content) in enumerate(extracted_file_contents.items(), 1):
        modules.append({
            'title': f'Module {i}: {filename}',
            'description': f'Content extracted from {filename}',
            'content': content,
            'source': filename
        })
    return {
        'pathways': [{
            'pathway_name': 'Quick Pathway',
            'sections': [{
                'title': 'All Modules',
                'modules': modules
            }]
        }]
    } 

def gemini_generate_complete_pathway(context, extracted_file_contents, inventory, bypass_filtering=False, preserve_original_content=False):
    """
    AI-powered pathway generation using Gemini API.
    Creates goal-aligned pathways based on primary training goals and file contents.
    Optimized for speed while maintaining quality.
    """
    try:
        debug_print(f"🎯 **Goal-Aligned Pathway Generation (Optimized)**")
        debug_print(f"📋 Training Context: {context}")
        debug_print(f"📄 Files to process: {len(extracted_file_contents)}")
        debug_print(f"📄 File names: {list(extracted_file_contents.keys())}")
        
        # Get primary training goals
        primary_goals = context.get('primary_goals', '')
        training_type = context.get('training_type', 'Training')
        target_audience = context.get('target_audience', 'employees')
        industry = context.get('industry', 'general')
        
        debug_print(f"🎯 **Primary Goals:** '{primary_goals}'")
        debug_print(f"📋 **Training Type:** {training_type}")
        debug_print(f"👥 **Target Audience:** {target_audience}")
        debug_print(f"🏢 **Industry:** {industry}")
        
        if not primary_goals:
            debug_print("⚠️ **FALLBACK REASON:** No primary goals specified, using quick pathway")
            return create_quick_pathway(context, extracted_file_contents, inventory)
        
        # Fast initial content analysis to identify relevant files
        debug_print(f"🔍 **Fast content analysis for goal alignment**")
        relevant_files = {}
        
        for filename, content in extracted_file_contents.items():
            if not content or len(content.strip()) < 50:
                debug_print(f"⚠️ {filename}: Content too short ({len(content) if content else 0} chars)")
                continue
            
            # Quick goal relevance check
            content_lower = content.lower()
            goal_keywords = primary_goals.lower().split()
            relevance_score = sum(1 for keyword in goal_keywords if keyword in content_lower)
            
            debug_print(f"🔍 {filename}: {relevance_score} goal matches out of {len(goal_keywords)} keywords")
            debug_print(f"   Keywords: {goal_keywords}")
            debug_print(f"   Content preview: {content[:100]}...")
            
            if relevance_score > 0 or len(content) > 200:  # Include substantial content
                relevant_files[filename] = content
                debug_print(f"✅ {filename}: {relevance_score} goal matches, {len(content)} chars - INCLUDED")
            else:
                debug_print(f"⚠️ {filename}: No goal relevance found - EXCLUDED")
        
        debug_print(f"🎯 **Relevant files found:** {len(relevant_files)} out of {len(extracted_file_contents)}")
        
        if not relevant_files:
            debug_print("⚠️ **FALLBACK REASON:** No relevant files found, using quick pathway")
            return create_quick_pathway(context, extracted_file_contents, inventory)
        
        debug_print(f"🎯 **Relevant files for AI processing:** {len(relevant_files)}")
        debug_print(f"📄 Relevant file names: {list(relevant_files.keys())}")
        
        # Use AI to thoroughly analyze and extract goal-aligned content
        goal_aligned_modules = []
        
        # Process files in parallel for speed (limited to avoid timeouts)
        max_concurrent_files = 3  # Limit concurrent processing
        files_to_process = list(relevant_files.items())
        
        for i in range(0, len(files_to_process), max_concurrent_files):
            batch = files_to_process[i:i + max_concurrent_files]
            debug_print(f"🚀 **Processing batch {i//max_concurrent_files + 1}:** {len(batch)} files")
            
            for filename, content in batch:
                debug_print(f"🔍 **AI analyzing {filename} thoroughly**")
                
                # Use AI to extract goal-aligned modules with thorough analysis
                file_modules = extract_ai_goal_aligned_modules(
                    filename, 
                    content, 
                    context, 
                    primary_goals,
                    bypass_filtering=bypass_filtering,
                    preserve_original_content=preserve_original_content
                )
                
                if file_modules:
                    goal_aligned_modules.extend(file_modules)
                    debug_print(f"✅ Extracted {len(file_modules)} AI-analyzed modules from {filename}")
                else:
                    debug_print(f"⚠️ No AI-aligned content found in {filename}")
        
        debug_print(f"🎯 **Total AI-aligned modules:** {len(goal_aligned_modules)}")
        
        if not goal_aligned_modules:
            debug_print("⚠️ **FALLBACK REASON:** No AI-aligned modules found, using quick pathway")
            return create_quick_pathway(context, extracted_file_contents, inventory)
        
        debug_print(f"🎯 **Proceeding with AI pathway creation for {len(goal_aligned_modules)} modules**")
        
        # Use AI to create goal-focused pathways
        return create_ai_goal_pathways(goal_aligned_modules, context, primary_goals)
        
    except Exception as e:
        debug_print(f"⚠️ **FALLBACK REASON:** AI pathway generation failed: {e}")
        import traceback
        debug_print(f"📝 Full error: {traceback.format_exc()}")
        # Fallback to quick pathway
        return create_quick_pathway(context, extracted_file_contents, inventory)

def extract_ai_goal_aligned_modules(filename, content, context, primary_goals, bypass_filtering=False, preserve_original_content=False):
    """
    Use AI to thoroughly analyze file content and extract goal-aligned modules
    """
    try:
        if not model:
            debug_print(f"⚠️ {filename}: No AI model available, using basic extraction")
            # Fallback to basic extraction if no AI
            return extract_modules_from_file_content(filename, content, context, bypass_filtering, preserve_original_content)
        
        debug_print(f"🤖 **AI analyzing {filename} for goal alignment**")
        debug_print(f"📄 Content length: {len(content)} characters")
        debug_print(f"🎯 Goals to align with: {primary_goals}")
        
        # Prepare content for AI analysis (limit size for speed)
        content_for_ai = content[:8000] if len(content) > 8000 else content
        debug_print(f"📝 Content for AI analysis: {len(content_for_ai)} characters")
        
        training_type = context.get('training_type', 'Training')
        target_audience = context.get('target_audience', 'employees')
        industry = context.get('industry', 'general')
        
        # Check if this is a meeting transcript
        is_meeting_transcript = any(keyword in filename.lower() for keyword in ['meeting', 'transcript', 'teams', 'zoom', 'call'])
        content_lower = content.lower()
        has_meeting_patterns = any(pattern in content_lower for pattern in ['teams meeting', 'meet meeting', 'meeting transcript', '0:00', 'yeah,', 'um,', 'uh,'])
        
        if is_meeting_transcript or has_meeting_patterns:
            debug_print(f"🎤 **Detected meeting transcript: {filename}**")
            # Use specialized prompt for meeting transcripts
            prompt = f"""
            Analyze this meeting transcript and extract training-relevant information.
            
            FILE: {filename}
            CONTENT: {content_for_ai}
            
            TRAINING GOALS: {primary_goals}
            TRAINING TYPE: {training_type}
            TARGET AUDIENCE: {target_audience}
            INDUSTRY: {industry}
            
            REQUIREMENTS:
            1. This is a meeting transcript - extract training-relevant information from the conversation
            2. Look for specific procedures, processes, policies, or knowledge discussed
            3. Extract 2-4 training modules that support the training goals
            4. Focus on actionable content, not just conversational elements
            5. Transform conversational language into professional training content
            6. Include specific procedures, processes, or knowledge mentioned
            7. Make modules suitable for {target_audience} in {industry}
            8. Focus on content that helps achieve: {primary_goals}
            9. If no training-relevant content found, return empty array
            
            IMPORTANT: Return ONLY valid JSON array. Do not include any explanatory text.
            
            Return as JSON array of modules:
            [
                {{
                    "title": "Specific training topic from the meeting",
                    "description": "Clear description of what this module covers",
                    "content": "Professional training content extracted from the meeting",
                    "key_points": ["Point 1", "Point 2", "Point 3"]
                }}
            ]
            
            Only include modules that are directly relevant to the training goals.
            """
        else:
            # Standard prompt for other content types
            prompt = f"""
            Thoroughly analyze this file content and extract training modules that align with the specific training goals.
            
            FILE: {filename}
            CONTENT: {content_for_ai}
            
            TRAINING GOALS: {primary_goals}
            TRAINING TYPE: {training_type}
            TARGET AUDIENCE: {target_audience}
            INDUSTRY: {industry}
            
            REQUIREMENTS:
            1. Read the content thoroughly and identify key parts relevant to the training goals
            2. Extract 2-4 specific training modules that directly support the training goals
            3. Each module should focus on actionable training content
            4. Include specific procedures, processes, or knowledge from the file
            5. Make modules suitable for {target_audience} in {industry}
            6. Focus on content that helps achieve: {primary_goals}
            7. If content doesn't align with goals, return empty array
            
            IMPORTANT: Return ONLY valid JSON array. Do not include any explanatory text.
            
            Return as JSON array of modules:
            [
                {{
                    "title": "Specific module title based on content",
                    "description": "Clear description of what this module covers",
                    "content": "Extracted and structured training content from the file",
                    "key_points": ["Point 1", "Point 2", "Point 3"]
                }}
            ]
            
            Only include modules that are directly relevant to the training goals.
            """
        
        debug_print(f"🤖 Sending AI request for {filename}...")
        response = model.generate_content(prompt)
        raw = response.text.strip()
        debug_print(f"📋 AI response length: {len(raw)} characters")
        debug_print(f"📋 AI response preview: {raw[:200]}...")
        
        # Extract JSON from response with improved handling
        modules_data = extract_json_from_ai_response(raw)
        
        if modules_data and isinstance(modules_data, list):
            debug_print(f"✅ AI returned {len(modules_data)} modules for {filename}")
            modules = []
            for i, module_data in enumerate(modules_data):
                if isinstance(module_data, dict):
                    title = module_data.get('title', f'Module {i+1}')
                    description = module_data.get('description', f'Training content from {filename}')
                    content = module_data.get('content', '')
                    key_points = module_data.get('key_points', [])
                    
                    debug_print(f"📄 Module {i+1}: '{title}' - {len(content)} chars")
                    
                    if content and len(content.strip()) > 50:
                        # Add debugging source information to content
                        debug_source = f"\n\n--- DEBUG SOURCE ---\nContent extracted from: {filename}\nModule created by: AI analysis\nContent length: {len(content)} characters\n--- END DEBUG SOURCE ---\n\n"
                        content_with_debug = debug_source + content
                        
                        # Generate content types for this module
                        content_types = generate_content_types_with_ai(content, context)
                        
                        modules.append({
                            'title': title,
                            'description': description,
                            'content': content_with_debug,
                            'source': filename,
                            'key_points': key_points,
                            'relevance_score': 0.9,  # High relevance since AI filtered
                            'content_types': content_types
                        })
                        debug_print(f"✅ Module {i+1} added successfully with debug source info and {len(content_types)} content types")
                    else:
                        debug_print(f"⚠️ Module {i+1} content too short ({len(content)} chars)")
            
            debug_print(f"✅ Final result: {len(modules)} valid modules extracted from {filename}")
            return modules
        else:
            debug_print(f"⚠️ AI returned invalid response for {filename}")
            debug_print(f"📋 Raw response: {raw}")
            
            # Enhanced fallback for meeting transcripts
            if is_meeting_transcript or has_meeting_patterns:
                debug_print(f"🔄 **Enhanced fallback for meeting transcript: {filename}**")
                # Try to extract meaningful content from meeting transcript
                fallback_modules = extract_meeting_transcript_modules(filename, content, context, primary_goals)
                if fallback_modules:
                    debug_print(f"✅ Fallback extracted {len(fallback_modules)} modules from meeting transcript")
                    return fallback_modules
            
            return []
        
    except Exception as e:
        debug_print(f"⚠️ AI module extraction failed for {filename}: {e}")
        import traceback
        debug_print(f"📝 Full error: {traceback.format_exc()}")
        # Fallback to basic extraction
        return extract_modules_from_file_content(filename, content, context, bypass_filtering, preserve_original_content)

def extract_meeting_transcript_modules(filename, content, context, primary_goals):
    """
    Extract training modules from meeting transcripts when AI fails
    """
    try:
        debug_print(f"🔄 **Extracting modules from meeting transcript: {filename}**")
        
        # Split content into sentences
        sentences = re.split(r'[.!?]+', content)
        meaningful_sentences = []
        
        # Filter for meaningful sentences (not just conversational elements)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30:  # Minimum meaningful length
                sentence_lower = sentence.lower()
                
                # Skip purely conversational elements
                if any(conv in sentence_lower for conv in ['um,', 'uh,', 'yeah,', 'okay,', 'right,', 'so,', 'well,']):
                    continue
                
                # Look for training-relevant content
                training_keywords = get_training_keywords_from_goals(context)
                keyword_matches = sum(1 for keyword in training_keywords if keyword in sentence_lower)
                
                # Accept if it has training keywords OR is substantial content
                if keyword_matches >= 1 or len(sentence) > 100:
                    meaningful_sentences.append(sentence)
        
        debug_print(f"📄 Found {len(meaningful_sentences)} meaningful sentences in meeting transcript")
        
        if not meaningful_sentences:
            debug_print(f"⚠️ No meaningful content found in meeting transcript")
        return []

        # Group sentences into modules
        modules = []
        sentences_per_module = max(1, len(meaningful_sentences) // 3)  # 3 modules max
        
        for i in range(0, len(meaningful_sentences), sentences_per_module):
            module_sentences = meaningful_sentences[i:i + sentences_per_module]
            if module_sentences:
                module_content = '. '.join(module_sentences) + '.'
                
                # Create a simple title from the first sentence
                first_sentence = module_sentences[0]
                title = first_sentence[:60] + "..." if len(first_sentence) > 60 else first_sentence
                
                # Clean up title
                title = re.sub(r'^[A-Za-z]+:\s*', '', title)  # Remove speaker prefixes
                title = title.strip()
                
                # Add debugging source information to content
                debug_source = f"\n\n--- DEBUG SOURCE ---\nContent extracted from: {filename}\nModule created by: Fallback extraction\nContent length: {len(module_content)} characters\nExtraction method: Meeting transcript fallback\n--- END DEBUG SOURCE ---\n\n"
                module_content_with_debug = debug_source + module_content
                
                # Generate content types for this module
                content_types = generate_fallback_content_types(module_content, context)
                
                modules.append({
                    'title': f'Module {len(modules)+1}: {title}',
                    'description': f'Training content extracted from {filename}',
                    'content': module_content_with_debug,
                    'source': filename,
                    'key_points': extract_key_points_from_content(module_content, context),
                    'relevance_score': 0.7,  # Medium relevance since it's fallback
                    'content_types': content_types
                })
        
        debug_print(f"✅ Created {len(modules)} fallback modules from meeting transcript")
        return modules
        
    except Exception as e:
        debug_print(f"⚠️ Meeting transcript fallback extraction failed: {e}")
        return []

def create_ai_goal_pathways(modules, context, primary_goals):
    """
    Use AI to create goal-focused pathways from modules with semantic search and RAG
    """
    try:
        if not model:
            # Fallback to basic pathway creation
            debug_print(f"⚠️ No AI model available, using fallback pathway creation")
            return create_fast_ai_pathways(modules, context)
        
        debug_print(f"🤖 **AI creating goal-focused pathways with semantic search**")
        debug_print(f"📄 Number of modules to organize: {len(modules)}")
        
        training_type = context.get('training_type', 'Training')
        target_audience = context.get('target_audience', 'employees')
        industry = context.get('industry', 'general')
        
        # Enhanced semantic search for related concepts
        semantic_keywords = extract_semantic_keywords(primary_goals, context)
        debug_print(f"🔍 **Semantic keywords extracted:** {semantic_keywords}")
        
        # RAG: Retrieve additional context from modules
        enhanced_context = retrieve_related_context(modules, primary_goals, semantic_keywords)
        debug_print(f"📚 **Enhanced context retrieved:** {len(enhanced_context)} related concepts")
        
        # Prepare module summaries with semantic relevance scores
        module_summaries = []
        for i, module in enumerate(modules[:10]):  # Limit for speed
            semantic_score = calculate_semantic_relevance(module, primary_goals, semantic_keywords)
            module_summaries.append({
                'index': i + 1,
                'title': module.get('title', f'Module {i+1}'),
                'description': module.get('description', ''),
                'content_preview': module.get('content', '')[:200] + '...',
                'semantic_relevance': semantic_score
            })
        
        debug_print(f"📋 Module summaries prepared with semantic relevance: {len(module_summaries)} modules")
        
        # Create enhanced prompt with semantic context
        enhanced_prompt = f"""
        Create goal-aligned training pathways from these modules using semantic understanding.
        
        TRAINING GOALS: {primary_goals}
        TRAINING TYPE: {training_type}
        TARGET AUDIENCE: {target_audience}
        INDUSTRY: {industry}
        
        SEMANTIC CONTEXT:
        - Primary Goals: {primary_goals}
        - Related Concepts: {', '.join(semantic_keywords)}
        - Enhanced Context: {enhanced_context}
        
        MODULES WITH SEMANTIC RELEVANCE: {module_summaries}
        
        REQUIREMENTS:
        1. Use semantic understanding to group modules by related concepts, not just exact keyword matches
        2. Create 1-3 pathways that support the training goals through related topics
        3. Group modules logically based on semantic similarity and training progression
        4. Each pathway should have a clear focus that supports the primary goals
        5. Create meaningful section titles that reflect the training objectives
        6. Include descriptions that reference the specific training goals and related concepts
        7. Make pathways suitable for {target_audience} in {industry}
        8. Consider both direct relevance and related concepts that support the goals
        9. Return ONLY valid JSON - no explanatory text
        
        SEMANTIC GROUPING GUIDELINES:
        - Look for modules that cover related aspects of the same topic
        - Group foundational concepts together
        - Group advanced applications together
        - Consider learning progression from basic to advanced
        - Include modules that support the goals indirectly through related skills
        
        Return as JSON:
        {{
            "pathways": [
                {{
                    "pathway_name": "Semantic pathway name based on related concepts",
                    "sections": [
                        {{
                            "title": "Section title reflecting semantic grouping",
                            "description": "Description referencing training goals and related concepts",
                            "modules": [module_indices]
                        }}
                    ],
                    "module_count": number
                }}
            ]
        }}
        
        Focus on creating pathways that semantically support: {primary_goals}
        IMPORTANT: Return ONLY valid JSON array. Do not include any explanatory text.
        """
        
        debug_print(f"🤖 Sending enhanced AI pathway creation request with semantic search...")
        response = model.generate_content(enhanced_prompt)
        raw = response.text.strip()
        debug_print(f"📋 AI pathway response length: {len(raw)} characters")
        debug_print(f"📋 AI pathway response preview: {raw[:300]}...")
        
        # Extract JSON from response with improved error handling
        pathway_data = extract_json_from_ai_response(raw)
        debug_print(f"📋 Extracted pathway data type: {type(pathway_data).__name__}")
        
        if pathway_data and isinstance(pathway_data, dict):
            debug_print(f"📋 Pathway data keys: {list(pathway_data.keys())}")
            
            if 'pathways' in pathway_data:
                pathways_list = pathway_data['pathways']
                debug_print(f"📋 Found {len(pathways_list)} pathways in AI response")
                
                # Convert AI pathway structure to actual modules
                ai_pathways = []
                
                for i, pathway in enumerate(pathways_list):
                    debug_print(f"📋 Processing pathway {i+1}: {pathway.get('pathway_name', 'Unknown')}")
                    
                    pathway_modules = []
                    sections = pathway.get('sections', [])
                    debug_print(f"📋 Pathway {i+1} has {len(sections)} sections")
                    
                    for j, section in enumerate(sections):
                        section_modules = []
                        module_indices = section.get('modules', [])
                        debug_print(f"📋 Section {j+1} has {len(module_indices)} module indices: {module_indices}")

                        for idx in module_indices:
                            if 0 <= idx < len(modules):
                                section_modules.append(modules[idx])
                                debug_print(f"✅ Added module {idx+1} to section {j+1}")
                            else:
                                debug_print(f"⚠️ Invalid module index {idx} (max: {len(modules)-1})")

                        if section_modules:
                            pathway_modules.append({
                                'title': section.get('title', f'Training Section {j+1}'),
                                'description': section.get('description', ''),
                                'modules': section_modules
                            })
                            debug_print(f"✅ Added section {j+1} with {len(section_modules)} modules")
                        else:
                            debug_print(f"⚠️ Section {j+1} has no valid modules")
                    
                    if pathway_modules:
                        ai_pathways.append({
                            'pathway_name': pathway.get('pathway_name', f'{training_type} Pathway {i+1}'),
                            'sections': pathway_modules,
                            'module_count': sum(len(section['modules']) for section in pathway_modules)
                        })
                        debug_print(f"✅ Added pathway {i+1} with {len(pathway_modules)} sections")
                    else:
                        debug_print(f"⚠️ Pathway {i+1} has no valid sections")
                
                if ai_pathways:
                    debug_print(f"✅ Successfully created {len(ai_pathways)} AI pathways with semantic search")
                    return {'pathways': ai_pathways}
                else:
                    debug_print(f"⚠️ No valid pathways created from AI response")
            else:
                debug_print(f"⚠️ No 'pathways' key found in AI response")
        elif pathway_data and isinstance(pathway_data, list):
            # Handle case where AI returns a list instead of dictionary
            debug_print(f"📋 AI returned list instead of dictionary, converting to pathway structure")
            
            # Convert list to pathway structure
            ai_pathways = []
            for i, pathway in enumerate(pathway_data):
                if isinstance(pathway, dict):
                    pathway_name = pathway.get('pathway_name', f'{training_type} Pathway {i+1}')
                    sections = pathway.get('sections', [])
                    
                    pathway_modules = []
                    for section in sections:
                        if isinstance(section, dict):
                            section_modules = []
                            module_indices = section.get('modules', [])
                            
                            for idx in module_indices:
                                if 0 <= idx < len(modules):
                                    section_modules.append(modules[idx])
                            
                            if section_modules:
                                pathway_modules.append({
                                    'title': section.get('title', f'Training Section {len(pathway_modules)+1}'),
                                    'description': section.get('description', ''),
                                    'modules': section_modules
                                })
                    
                    if pathway_modules:
                        ai_pathways.append({
                            'pathway_name': pathway_name,
                            'sections': pathway_modules,
                            'module_count': sum(len(section['modules']) for section in pathway_modules)
                        })
            
            if ai_pathways:
                debug_print(f"✅ Successfully converted list to {len(ai_pathways)} pathways")
                return {'pathways': ai_pathways}
            else:
                debug_print(f"⚠️ Failed to convert list to valid pathways")
        else:
            debug_print(f"⚠️ Invalid pathway data structure: {type(pathway_data).__name__}")
        
        # Fallback to robust pathway creation
        debug_print(f"⚠️ AI pathway creation failed, using robust fallback")
        fallback_result = create_robust_fallback_pathways(modules, context, primary_goals)
        debug_print(f"📋 Robust fallback created {len(fallback_result.get('pathways', []))} pathways")
        return fallback_result
        
    except Exception as e:
        debug_print(f"⚠️ AI pathway creation failed: {e}")
        import traceback
        debug_print(f"📝 Full error: {traceback.format_exc()}")
        fallback_result = create_robust_fallback_pathways(modules, context, primary_goals)
        debug_print(f"📋 Exception robust fallback created {len(fallback_result.get('pathways', []))} pathways")
        return fallback_result

def create_robust_fallback_pathways(modules, context, primary_goals):
    """
    Create robust fallback pathways when AI fails completely with unique naming
    """
    try:
        debug_print(f"🛡️ **Creating robust fallback pathways**")
        debug_print(f"📄 Number of modules: {len(modules)}")
        
        if not modules:
            debug_print(f"⚠️ No modules available for fallback")
            return {'pathways': []}
        
        training_type = context.get('training_type', 'Training')
        target_audience = context.get('target_audience', 'employees')
        industry = context.get('industry', 'general')
        
        # Create unique pathways based on module count and content
        if len(modules) <= 3:
            # Single comprehensive pathway with unique name
            pathway_name = generate_unique_pathway_name_from_theme(training_type, 'comprehensive', primary_goals, industry, 1)
            sections = [{
                'title': generate_unique_section_name(['Comprehensive'], 1),
                'modules': modules
            }]
        elif len(modules) <= 6:
            # Two logical pathways with unique names
            mid_point = len(modules) // 2
            pathway1_name = generate_unique_pathway_name_from_theme(training_type, 'core', primary_goals, industry, 1)
            pathway2_name = generate_unique_pathway_name_from_theme(training_type, 'specialized', primary_goals, industry, 2)
            
            sections1 = [{
                'title': generate_unique_section_name(['Core'], 1),
                'modules': modules[:mid_point]
            }]
            
            sections2 = [{
                'title': generate_unique_section_name(['Specialized'], 2),
                'modules': modules[mid_point:]
            }]
            
            return {
                'pathways': [
                    {
                        'pathway_name': pathway1_name,
                        'sections': sections1,
                        'module_count': len(modules[:mid_point])
                    },
                    {
                        'pathway_name': pathway2_name,
                        'sections': sections2,
                        'module_count': len(modules[mid_point:])
                    }
                ]
            }
        else:
            # Three comprehensive pathways with unique names
            third = len(modules) // 3
            pathway1_name = generate_unique_pathway_name_from_theme(training_type, 'foundation', primary_goals, industry, 1)
            pathway2_name = generate_unique_pathway_name_from_theme(training_type, 'application', primary_goals, industry, 2)
            pathway3_name = generate_unique_pathway_name_from_theme(training_type, 'mastery', primary_goals, industry, 3)
            
            sections1 = [{
                'title': generate_unique_section_name(['Foundation'], 1),
                'modules': modules[:third]
            }]
            
            sections2 = [{
                'title': generate_unique_section_name(['Application'], 2),
                'modules': modules[third:2*third]
            }]
            
            sections3 = [{
                'title': generate_unique_section_name(['Mastery'], 3),
                'modules': modules[2*third:]
            }]
            
            return {
                'pathways': [
                    {
                        'pathway_name': pathway1_name,
                        'sections': sections1,
                        'module_count': third
                    },
                    {
                        'pathway_name': pathway2_name,
                        'sections': sections2,
                        'module_count': third
                    },
                    {
                        'pathway_name': pathway3_name,
                        'sections': sections3,
                        'module_count': len(modules) - 2*third
                    }
                ]
            }
        
        # Single pathway case
        return {
            'pathways': [{
                'pathway_name': pathway_name,
                'sections': sections,
                'module_count': len(modules)
            }]
        }
        
    except Exception as e:
        debug_print(f"⚠️ Robust fallback pathway creation failed: {e}")
        # Ultimate fallback - single pathway with all modules
        pathway_name = generate_unique_pathway_name_from_theme(training_type, 'comprehensive', primary_goals, industry, 1)
        return {
            'pathways': [{
                'pathway_name': pathway_name,
                'sections': [{
                    'title': generate_unique_section_name(['Comprehensive'], 1),
                    'modules': modules
                }],
                'module_count': len(modules)
            }]
        }

def extract_semantic_keywords(primary_goals, context):
    """
    Extract semantic keywords that are related to the primary goals but not exact matches
    """
    try:
        if not model:
            # Fallback to basic semantic expansion
            return extract_basic_semantic_keywords(primary_goals, context)
        
        debug_print(f"🔍 **Extracting semantic keywords for:** {primary_goals}")
        
        training_type = context.get('training_type', 'Training')
        target_audience = context.get('target_audience', 'employees')
        industry = context.get('industry', 'general')
        
        prompt = f"""
        Extract semantic keywords that are related to this training goal but not exact matches.
        
        PRIMARY GOAL: {primary_goals}
        TRAINING TYPE: {training_type}
        TARGET AUDIENCE: {target_audience}
        INDUSTRY: {industry}
        
        REQUIREMENTS:
        1. Find related concepts, skills, and knowledge areas that support the primary goal
        2. Include broader industry terms, related processes, and supporting skills
        3. Consider prerequisite knowledge and advanced applications
        4. Include safety, quality, and compliance aspects if relevant
        5. Focus on terms that would help create comprehensive training pathways
        6. Return only the keywords, one per line, without explanations
        
        Examples:
        - If goal is "learn bridge fabrication", include: welding, steel, construction, assembly, safety, quality control, engineering drawings, measurements, tools, equipment, materials, processes, standards, regulations
        
        Return 10-15 semantic keywords that support the training goal.
        """
        
        response = model.generate_content(prompt)
        if response.text:
            keywords = [keyword.strip() for keyword in response.text.split('\n') if keyword.strip()]
            # Clean up any AI formatting
            cleaned_keywords = []
            for keyword in keywords:
                # Remove numbering, bullets, etc.
                keyword = re.sub(r'^[\d\-\.\s]+', '', keyword)
                if keyword and len(keyword) > 2:
                    cleaned_keywords.append(keyword)
            
            debug_print(f"✅ Extracted {len(cleaned_keywords)} semantic keywords")
            return cleaned_keywords[:15]  # Limit to 15 keywords
        
        return []
        
    except Exception as e:
        debug_print(f"⚠️ Semantic keyword extraction failed: {e}")
        return extract_basic_semantic_keywords(primary_goals, context)

def extract_basic_semantic_keywords(primary_goals, context):
    """
    Basic fallback for semantic keyword extraction
    """
    try:
        goals_lower = primary_goals.lower()
        industry = context.get('industry', '').lower()
        training_type = context.get('training_type', '').lower()
        
        semantic_keywords = []
        
        # Industry-specific semantic expansion
        if 'manufacturing' in industry or 'fabrication' in goals_lower:
            semantic_keywords.extend([
                'welding', 'steel', 'construction', 'assembly', 'materials',
                'equipment', 'tools', 'measurements', 'quality control',
                'safety protocols', 'engineering drawings', 'specifications',
                'processes', 'workflow', 'standards', 'regulations'
            ])
        
        if 'bridge' in goals_lower:
            semantic_keywords.extend([
                'structural engineering', 'load calculations', 'stress analysis',
                'connection methods', 'foundation', 'abutments', 'decking',
                'support systems', 'inspection', 'maintenance'
            ])
        
        if 'fabrication' in goals_lower:
            semantic_keywords.extend([
                'cutting', 'forming', 'joining', 'finishing', 'inspection',
                'quality assurance', 'documentation', 'project management'
            ])
        
        # General training semantic keywords
        semantic_keywords.extend([
            'learning objectives', 'skill development', 'competency',
            'best practices', 'troubleshooting', 'problem solving',
            'communication', 'teamwork', 'leadership'
        ])
        
        # Remove duplicates and limit
        unique_keywords = list(set(semantic_keywords))
        return unique_keywords[:15]
        
    except Exception as e:
        debug_print(f"⚠️ Basic semantic keyword extraction failed: {e}")
        return []

def retrieve_related_context(modules, primary_goals, semantic_keywords):
    """
    RAG: Retrieve related context from modules using semantic search
    """
    try:
        debug_print(f"📚 **Retrieving related context from {len(modules)} modules**")
        
        related_concepts = []
        
        # Search through module content for related concepts
        for module in modules:
            content = module.get('content', '').lower()
            title = module.get('title', '').lower()
            
            # Check for semantic keyword matches
            for keyword in semantic_keywords:
                if keyword.lower() in content or keyword.lower() in title:
                    related_concepts.append(keyword)
            
            # Look for related concepts based on content analysis
            if any(word in content for word in ['safety', 'ppe', 'protective']):
                related_concepts.extend(['safety protocols', 'personal protective equipment'])
            
            if any(word in content for word in ['quality', 'inspection', 'control']):
                related_concepts.extend(['quality control', 'inspection procedures'])
            
            if any(word in content for word in ['process', 'procedure', 'workflow']):
                related_concepts.extend(['process management', 'workflow optimization'])
            
            if any(word in content for word in ['equipment', 'tool', 'operation']):
                related_concepts.extend(['equipment operation', 'tool usage'])
        
        # Remove duplicates and limit
        unique_concepts = list(set(related_concepts))
        debug_print(f"✅ Retrieved {len(unique_concepts)} related concepts")
        
        return unique_concepts[:10]  # Limit to 10 concepts
        
    except Exception as e:
        debug_print(f"⚠️ Context retrieval failed: {e}")
        return [] 

def calculate_semantic_relevance(module, primary_goals, semantic_keywords):
    """
    Calculate semantic relevance score for a module
    """
    try:
        content = module.get('content', '').lower()
        title = module.get('title', '').lower()
        description = module.get('description', '').lower()
        
        # Count semantic keyword matches
        keyword_matches = 0
        for keyword in semantic_keywords:
            if keyword.lower() in content or keyword.lower() in title or keyword.lower() in description:
                keyword_matches += 1
        
        # Calculate relevance score (0-1)
        relevance_score = min(1.0, keyword_matches / len(semantic_keywords)) if semantic_keywords else 0.5
        
        return round(relevance_score, 2)
        
    except Exception as e:
        debug_print(f"⚠️ Semantic relevance calculation failed: {e}")
        return 0.5  # Default medium relevance