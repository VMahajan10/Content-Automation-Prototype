    try:
        # Universal content analysis - works for any type of content
        content_lower = content.lower()
        
        # Universal content type detection
        content_type = detect_content_type(content)
        debug_print(f"🔍 **Universal Content Analysis:**")
        debug_print(f"   Content type: {content_type}")
        debug_print(f"   Content length: {len(content)} characters")
        debug_print(f"   Content preview: {content[:200]}...")
        
