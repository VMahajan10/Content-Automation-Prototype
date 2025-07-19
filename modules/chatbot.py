#!/usr/bin/env python3
"""
Chatbot module for pathway management
Handles module regeneration, file ingestion, and content updates
"""

import streamlit as st
import re
from modules.config import model
from modules.utils import debug_print, extract_modules_from_file_content, gemini_generate_complete_pathway

def create_pathway_chatbot():
    """
    Create a chatbot interface for pathway management
    Allows admins to regenerate modules and ingest new files
    """
    st.markdown("---")
    st.markdown("### 🤖 AI Pathway Assistant")
    st.markdown("Use this chatbot to regenerate modules, update content, or ingest new files.")
    
    # Initialize chat history
    if 'chatbot_history' not in st.session_state:
        st.session_state.chatbot_history = []
    
    # Chatbot interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Display chat history
        st.markdown("**💬 Chat History:**")
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.chatbot_history:
                if message['role'] == 'user':
                    st.markdown(f"**👤 You:** {message['content']}")
                else:
                    st.markdown(f"**🤖 Assistant:** {message['content']}")
        
        # User input
        user_input = st.text_input("Ask me about regenerating modules, updating content, or ingesting new files:", 
                                  key="chatbot_input", 
                                  placeholder="e.g., 'Regenerate module 2 with a more professional tone'")
        
        if st.button("Send", key="send_chat"):
            if user_input:
                # Add user message to history
                st.session_state.chatbot_history.append({
                    'role': 'user',
                    'content': user_input
                })
                
                # Process the request
                response = process_chatbot_request(user_input)
                
                # Add assistant response to history
                st.session_state.chatbot_history.append({
                    'role': 'assistant',
                    'content': response
                })
                
                st.rerun()
    
    with col2:
        st.markdown("**🛠️ Quick Actions:**")
        
        if st.button("🔄 Regenerate Current Module", key="regenerate_current"):
            regenerate_current_module()
        
        if st.button("📁 Ingest New Files", key="ingest_new_files"):
            ingest_new_files_interface()
        
        if st.button("🎨 Update Module Tone", key="update_tone"):
            update_module_tone_interface()
        
        if st.button("📝 Add Missing Info", key="add_missing_info"):
            add_missing_info_interface()
        
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.chatbot_history = []
            st.rerun()

def create_pathway_chatbot_popup(context="main"):
    """
    Create a popup chatbot interface for pathway management
    This version appears as a floating popup when toggled
    """
    # Always use a floating popup on the right, never sidebar
    if context == "floating":
        # Render the popup only if chatbot_visible is True
        if st.session_state.get("chatbot_visible", False):
            # Use sidebar for floating effect
            with st.sidebar:
                st.markdown("### 🤖 AI Assistant")
                
                # Show AI status
                if model:
                    st.success("✅ Gemini AI Connected")
                else:
                    st.error("❌ Gemini AI Not Available")
                    st.info("Please check your API key in Settings")
                
                # Show current module structure
                editable_pathways = st.session_state.get('editable_pathways', {})
                if editable_pathways:
                    st.markdown("**📚 Current Modules:**")
                    module_reference_help = format_module_reference_help(editable_pathways)
                    # Show a condensed version with decimal numbering to match generation
                    section_count = 0
                    for section_name, modules in editable_pathways.items():
                        section_count += 1
                        st.markdown(f"**{section_name}:**")
                        for i, module in enumerate(modules):
                            module_number = f"{section_count}.{i+1}"
                            st.markdown(f"  • Module {module_number}: {module['title']}")
                        st.markdown("")
                else:
                    st.info("📚 No modules available yet")
                
                # Close button
                if st.button("✕ Close", key=f"sidebar_close_{context}", help="Close AI Assistant"):
                    st.session_state.chatbot_visible = False
                    st.rerun()
                
                # Chat history
                if 'popup_chatbot_history' not in st.session_state:
                    st.session_state.popup_chatbot_history = []
                
                # Display recent messages
                recent_messages = st.session_state.popup_chatbot_history[-8:] if st.session_state.popup_chatbot_history else []
                for message in recent_messages:
                    if message['role'] == 'user':
                        st.markdown(f"**👤 You:** {message['content']}")
                    else:
                        st.markdown(f"**🤖 Assistant:** {message['content']}")
                
                st.markdown("---")
                
                # File upload section
                st.markdown("**📁 Upload Files:**")
                uploaded_files = st.file_uploader(
                    "Upload files to add to your pathway",
                    type=['pdf', 'doc', 'docx', 'txt', 'mp4', 'avi', 'mov'],
                    key=f"sidebar_file_upload_{context}",
                    accept_multiple_files=True
                )
                
                # Show uploaded files status
                if uploaded_files:
                    st.success(f"📁 {len(uploaded_files)} files ready")
                    for i, file in enumerate(uploaded_files):
                        st.write(f"• {file.name} ({file.size} bytes)")
                    
                    # Process files button
                    if st.button("🔄 Process Files Now", key=f"sidebar_process_files_{context}"):
                        st.info(f"🚀 Processing {len(uploaded_files)} files...")
                        
                        # Add progress indicator
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        # Process files with progress updates
                        for i, file in enumerate(uploaded_files):
                            status_text.text(f"Processing {file.name}... ({i+1}/{len(uploaded_files)})")
                            progress_bar.progress((i + 1) / len(uploaded_files))
                        
                        result = process_new_files(uploaded_files)
                        
                        # Clear progress indicators
                        progress_bar.empty()
                        status_text.empty()
                        
                        if result:
                            st.success(f"✅ Successfully processed {len(uploaded_files)} files!")
                            # Add success message to chat
                            st.session_state.popup_chatbot_history.append({
                                'role': 'assistant',
                                'content': f"✅ Successfully processed {len(uploaded_files)} files! Now tell me where you'd like to add or update content. For example:\n\n• \"Update module 2 with the new content\"\n• \"Add the new content to the safety section\"\n• \"Replace module 1 with the uploaded file\"\n• \"Add new modules to pathway 3 section 2\""
                            })
                            # Store processed files info in session state to show after rerun
                            st.session_state['last_processed_files'] = {
                                'count': len(uploaded_files),
                                'names': [f.name for f in uploaded_files]
                            }
                            st.rerun()
                        else:
                            st.error("❌ Failed to process files. Please try again.")
                            # Add error message to chat
                            st.session_state.popup_chatbot_history.append({
                                'role': 'assistant',
                                'content': "❌ Failed to process files. Please check the file format and try again."
                            })
                            st.rerun()
                else:
                    st.info("📁 No files uploaded yet")
                    st.info("💡 Upload files above, then click 'Process Files Now' to add them to your pathway")
                    
                    # Show last processed files info if available
                    if 'last_processed_files' in st.session_state:
                        last_files = st.session_state['last_processed_files']
                        st.success(f"✅ Last processed: {last_files['count']} files")
                        for name in last_files['names']:
                            st.write(f"• {name}")
                        # Clear the info after showing it
                        del st.session_state['last_processed_files']
                
                st.markdown("---")
                
                # User input section
                st.markdown("**💬 Ask me anything:**")
                user_input = st.text_input("Your message:", key=f"sidebar_input_{context}", placeholder="e.g., 'Update module 2 with new file' or 'Regenerate module 1'")
                
                if st.button("Send", key=f"sidebar_send_{context}"):
                    if user_input:
                        # Add user message to history
                        st.session_state.popup_chatbot_history.append({
                            'role': 'user',
                            'content': user_input
                        })
                        
                        # Process the request
                        response = process_chatbot_request(user_input, uploaded_files)
                        
                        # Add assistant response to history
                        st.session_state.popup_chatbot_history.append({
                            'role': 'assistant',
                            'content': response
                        })
                        
                        st.rerun()

def process_chatbot_request(user_input, uploaded_files=None):
    """
    Process chatbot requests and return appropriate responses
    """
    try:
        user_input_lower = user_input.lower()
        
        # Check for different types of requests
        if any(word in user_input_lower for word in ['regenerate', 'update', 'change', 'modify']):
            return handle_module_regeneration(user_input)
        
        elif any(word in user_input_lower for word in ['ingest', 'upload', 'add file', 'process file']):
            return handle_file_ingestion(user_input)
        
        elif any(word in user_input_lower for word in ['tone', 'style', 'professional', 'casual']):
            return handle_tone_change(user_input)
        
        elif any(word in user_input_lower for word in ['add', 'missing', 'information', 'content']):
            return handle_content_addition(user_input)
        
        elif any(word in user_input_lower for word in ['module', 'section', 'pathway']):
            return handle_module_specific_request(user_input)
        
        elif any(word in user_input_lower for word in ['help', 'what can you do', 'how to']):
            return get_chatbot_help()
        
        elif any(word in user_input_lower for word in ['past', 'previous', 'history']):
            return handle_past_pathway_request(user_input)
        
        elif any(word in user_input_lower for word in ['search', 'find', 'look for']):
            return handle_content_question_request(user_input)
        
        else:
            return "I'm here to help with pathway management! You can:\n\n• Regenerate modules with different tones\n• Upload and process new files\n• Update module content\n• Search through existing content\n• Get help with specific tasks\n\nWhat would you like to do?"
    
    except Exception as e:
        debug_print(f"⚠️ Chatbot request processing failed: {str(e)}")
        return "Sorry, I encountered an error processing your request. Please try again or ask for help."

def handle_module_regeneration(user_input):
    """
    Handle module regeneration requests
    """
    try:
        # Extract module information from input
        module_info = extract_module_info_from_input(user_input)
        tone = extract_tone_from_input(user_input)
        content_focus = extract_content_focus_from_input(user_input)
        changes_requested = extract_changes_from_input(user_input)
        
        if not module_info:
            return "I couldn't identify which module you want to regenerate. Please specify the module number, title, or section. For example: 'Regenerate module 2' or 'Update the safety module'."
        
        # Find the target module
        editable_pathways = st.session_state.get('editable_pathways', {})
        target_module = find_module_by_info(module_info, editable_pathways)
        
        if not target_module:
            return f"I couldn't find the module you specified: {module_info}. Please check the module reference and try again."
        
        # Regenerate the module
        new_content = regenerate_module_content(target_module, tone, content_focus, changes_requested)
        
        if new_content:
            # Update the module in the pathway
            update_module_in_pathway(target_module, new_content)
            return f"✅ Successfully regenerated {target_module['title']} with {tone if tone else 'default'} tone and {content_focus if content_focus else 'general'} focus."
        else:
            return "❌ Failed to regenerate the module. Please try again."
    
    except Exception as e:
        debug_print(f"⚠️ Module regeneration failed: {str(e)}")
        return "Sorry, I encountered an error while regenerating the module. Please try again."

def handle_file_ingestion(user_input):
    """
    Handle file ingestion requests
    """
    try:
        editable_pathways = st.session_state.get('editable_pathways', {})
        if not editable_pathways:
            return "No pathways available. Please create a pathway first before ingesting files."
        
        # Check if there are uploaded files in session state
        uploaded_files = st.session_state.get('uploaded_files', [])
        if not uploaded_files:
            return "No files uploaded. Please upload files first using the file uploader."
        
        # Process the files
        result = process_new_files(uploaded_files)
        
        if result:
            return f"✅ Successfully processed {len(uploaded_files)} files! The new content has been integrated into your pathway."
        else:
            return "❌ Failed to process the uploaded files. Please check the file format and try again."
    
    except Exception as e:
        debug_print(f"⚠️ File ingestion failed: {str(e)}")
        return "Sorry, I encountered an error while processing the files. Please try again."

def handle_tone_change(user_input):
    """
    Handle tone change requests
    """
    try:
        tone = extract_tone_from_input(user_input)
        if not tone:
            return "I couldn't identify the tone you want to apply. Please specify a tone like 'professional', 'casual', 'technical', or 'friendly'."
        
        # This would typically involve regenerating modules with the new tone
        return f"I understand you want to change the tone to {tone}. Please specify which module(s) you'd like to update, or use 'Update all modules with {tone} tone'."
    
    except Exception as e:
        debug_print(f"⚠️ Tone change failed: {str(e)}")
        return "Sorry, I encountered an error while processing the tone change. Please try again."

def handle_content_addition(user_input):
    """
    Handle content addition requests
    """
    try:
        return "I can help you add missing content! Please specify:\n\n• Which module or section needs content\n• What type of content you want to add\n• Any specific requirements or focus areas"
    
    except Exception as e:
        debug_print(f"⚠️ Content addition failed: {str(e)}")
        return "Sorry, I encountered an error while processing the content addition. Please try again."

def handle_module_specific_request(user_input):
    """
    Handle module-specific requests
    """
    try:
        module_info = extract_module_info_from_input(user_input)
        if not module_info:
            return "I couldn't identify which module you're referring to. Please specify the module number, title, or section."
        
        editable_pathways = st.session_state.get('editable_pathways', {})
        target_module = find_module_by_info(module_info, editable_pathways)
        
        if not target_module:
            return f"I couldn't find the module: {module_info}. Please check the module reference and try again."
        
        return f"I found the module: {target_module['title']}. What would you like to do with it? You can:\n\n• Regenerate it with a different tone\n• Update its content\n• Add specific information\n• Change its focus area"
    
    except Exception as e:
        debug_print(f"⚠️ Module-specific request failed: {str(e)}")
        return "Sorry, I encountered an error while processing your request. Please try again."

def get_chatbot_help():
    """
    Return help information for the chatbot
    """
    return """🤖 **AI Pathway Assistant Help**

I can help you manage your training pathways! Here's what I can do:

**📝 Module Management:**
• "Regenerate module 2 with professional tone"
• "Update the safety module with new content"
• "Change module 1 to focus on technical details"

**📁 File Processing:**
• "Upload and process new files"
• "Add the uploaded files to pathway 1"
• "Update module 3 with the new file"

**🎨 Content Customization:**
• "Make all modules more professional"
• "Change the tone to casual"
• "Add technical details to module 2"

**🔍 Content Search:**
• "Search for safety procedures"
• "Find modules about quality control"
• "Look for equipment maintenance"

**📚 Past Pathways:**
• "Show me past pathway 2"
• "Get module 3 from pathway 1"
• "Add past module to current pathway"

**💡 Quick Tips:**
• Be specific about which module you want to modify
• Specify the tone or style you want
• Upload files first, then tell me how to use them
• Ask for help anytime!

What would you like to do?"""

def extract_module_info_from_input(user_input):
    """
    Extract module information from user input
    """
    try:
        user_input_lower = user_input.lower()
        
        # Look for module numbers
        module_match = re.search(r'module\s+(\d+)', user_input_lower)
        if module_match:
            return f"module_{module_match.group(1)}"
        
        # Look for section numbers
        section_match = re.search(r'section\s+(\d+)', user_input_lower)
        if section_match:
            return f"section_{section_match.group(1)}"
        
        # Look for pathway numbers
        pathway_match = re.search(r'pathway\s+(\d+)', user_input_lower)
        if pathway_match:
            return f"pathway_{pathway_match.group(1)}"
        
        # Look for specific keywords
        keywords = ['safety', 'quality', 'procedure', 'training', 'equipment', 'maintenance']
        for keyword in keywords:
            if keyword in user_input_lower:
                return keyword
        
        return None
    
    except Exception as e:
        debug_print(f"⚠️ Module info extraction failed: {str(e)}")
        return None

def extract_tone_from_input(user_input):
    """
    Extract tone information from user input
    """
    try:
        user_input_lower = user_input.lower()
        
        tones = {
            'professional': ['professional', 'formal', 'business'],
            'casual': ['casual', 'informal', 'friendly'],
            'technical': ['technical', 'detailed', 'comprehensive'],
            'simple': ['simple', 'basic', 'easy'],
            'authoritative': ['authoritative', 'commanding', 'strict']
        }
        
        for tone, keywords in tones.items():
            if any(keyword in user_input_lower for keyword in keywords):
                return tone
        
        return None
    
    except Exception as e:
        debug_print(f"⚠️ Tone extraction failed: {str(e)}")
        return None

def extract_content_focus_from_input(user_input):
    """
    Extract content focus from user input
    """
    try:
        user_input_lower = user_input.lower()
        
        focus_areas = {
            'safety': ['safety', 'ppe', 'protective', 'hazard'],
            'quality': ['quality', 'inspection', 'standard'],
            'procedure': ['procedure', 'process', 'workflow'],
            'equipment': ['equipment', 'tool', 'machine'],
            'maintenance': ['maintenance', 'repair', 'service']
        }
        
        for focus, keywords in focus_areas.items():
            if any(keyword in user_input_lower for keyword in keywords):
                return focus
        
        return None
    
    except Exception as e:
        debug_print(f"⚠️ Content focus extraction failed: {str(e)}")
        return None

def extract_changes_from_input(user_input):
    """
    Extract specific changes requested from user input
    """
    try:
        # This is a simplified version - could be expanded
        return None
    except Exception as e:
        debug_print(f"⚠️ Changes extraction failed: {str(e)}")
        return None

def find_module_by_info(module_info, editable_pathways):
    """
    Find a module based on the provided information
    """
    try:
        if not editable_pathways:
            return None
        
        # Look for module by number
        if module_info.startswith('module_'):
            module_num = int(module_info.split('_')[1]) - 1
            for section_name, modules in editable_pathways.items():
                if 0 <= module_num < len(modules):
                    return modules[module_num]
        
        # Look for module by keyword
        for section_name, modules in editable_pathways.items():
            for module in modules:
                if module_info.lower() in module['title'].lower():
                    return module
        
        return None
    
    except Exception as e:
        debug_print(f"⚠️ Module finding failed: {str(e)}")
        return None

def regenerate_module_content(target_module, tone, content_focus, changes_requested=None):
    """
    Regenerate module content with specified parameters
    """
    try:
        if not model:
            return "AI model not available for content regeneration."
        
        # Create a prompt for regeneration
        prompt = f"""Regenerate this training module content:

ORIGINAL CONTENT:
{target_module['content'][:1000]}

TONE: {tone if tone else 'professional'}
FOCUS: {content_focus if content_focus else 'general'}
CHANGES: {changes_requested if changes_requested else 'none'}

Generate improved content that maintains the key information while applying the specified tone and focus."""

        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
        else:
            return None
    
    except Exception as e:
        debug_print(f"⚠️ Module content regeneration failed: {str(e)}")
        return None

def update_module_in_pathway(target_module, new_content):
    """
    Update a module in the pathway with new content
    """
    try:
        target_module['content'] = new_content
        return True
    except Exception as e:
        debug_print(f"⚠️ Module update failed: {str(e)}")
        return False

def regenerate_current_module():
    """
    Regenerate the currently selected module
    """
    try:
        # This would need to be implemented based on the current UI state
        return "Please specify which module you want to regenerate."
    except Exception as e:
        debug_print(f"⚠️ Current module regeneration failed: {str(e)}")
        return "Error regenerating current module."

def ingest_new_files_interface():
    """
    Interface for ingesting new files
    """
    try:
        return "Please use the file uploader to upload files, then tell me how to process them."
    except Exception as e:
        debug_print(f"⚠️ File ingestion interface failed: {str(e)}")
        return "Error with file ingestion interface."

def update_module_tone_interface():
    """
    Interface for updating module tone
    """
    try:
        return "Please specify which module and what tone you want to apply."
    except Exception as e:
        debug_print(f"⚠️ Tone update interface failed: {str(e)}")
        return "Error with tone update interface."

def add_missing_info_interface():
    """
    Interface for adding missing information
    """
    try:
        return "Please specify which module needs additional information and what type of content you want to add."
    except Exception as e:
        debug_print(f"⚠️ Missing info interface failed: {str(e)}")
        return "Error with missing info interface."

def process_new_files(uploaded_files):
    """
    Process newly uploaded files
    """
    try:
        if not uploaded_files:
            return False
        
        # Extract content from files
        extracted_file_contents = {}
        for file in uploaded_files:
            try:
                content = file.read().decode('utf-8')
                extracted_file_contents[file.name] = content
            except Exception as e:
                debug_print(f"⚠️ Failed to read file {file.name}: {str(e)}")
                continue
        
        if not extracted_file_contents:
            return False
        
        # Get current context
        context = st.session_state.get('training_context', {})
        inventory = st.session_state.get('file_inventory', {})
        
        # Generate new pathway content
        result = gemini_generate_complete_pathway(context, extracted_file_contents, inventory)
        
        if result and 'pathways' in result:
            # Update session state with new pathways
            st.session_state['editable_pathways'] = result['pathways']
            return True
        
        return False
    
    except Exception as e:
        debug_print(f"⚠️ New file processing failed: {str(e)}")
        return False

def format_module_reference_help(editable_pathways):
    """
    Format module reference help information
    """
    try:
        help_text = "**Module Reference Guide:**\n\n"
        
        for section_name, modules in editable_pathways.items():
            help_text += f"**{section_name}:**\n"
            for i, module in enumerate(modules):
                help_text += f"  • Module {i+1}: {module['title']}\n"
            help_text += "\n"
        
        return help_text
    
    except Exception as e:
        debug_print(f"⚠️ Module reference formatting failed: {str(e)}")
        return "Error formatting module reference."

def handle_past_pathway_request(user_input):
    """
    Handle requests related to past pathways
    """
    try:
        return "Past pathway functionality is available. You can:\n\n• View past pathways\n• Copy modules from past pathways\n• Merge past sections into current pathways\n\nPlease specify what you'd like to do with past pathways."
    except Exception as e:
        debug_print(f"⚠️ Past pathway request failed: {str(e)}")
        return "Error processing past pathway request."

def handle_content_question_request(user_input):
    """
    Handle content search and question requests
    """
    try:
        return "I can help you search through your pathway content! Please specify what you're looking for, such as:\n\n• Specific procedures or processes\n• Safety information\n• Equipment details\n• Quality standards\n\nWhat would you like to search for?"
    except Exception as e:
        debug_print(f"⚠️ Content question request failed: {str(e)}")
        return "Error processing content search request." 