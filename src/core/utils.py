import logging
import re
import os
from streamlit_js_eval import streamlit_js_eval

logger = logging.getLogger(__name__)

def detect_code_blocks(text):
    """
    Extract code blocks from markdown text
    
    Args:
        text: Markdown text
        
    Returns:
        List of dictionaries with 'language' and 'code' keys
    """
    # Pattern to find code blocks with the language specified
    pattern = r'```([a-zA-Z0-9_+-]+)?\n([\s\S]*?)```'
    blocks = re.findall(pattern, text)
    result = []
    
    for language, code in blocks:
        result.append({
            'language': language.strip() if language else 'text',
            'code': code.strip()
        })
    
    return result

def copy_to_clipboard(text):
    """
    Copy text to clipboard using streamlit_js_eval
    
    Args:
        text: Text to copy
    """
    # Escape special characters
    text = text.replace('\'', '\\\'').replace('\"', '\\\"').replace('\n', '\\n')
    streamlit_js_eval(f"navigator.clipboard.writeText('{text}')")

def sanitize_filename(filename):
    """
    Sanitize a string to be used as a filename
    
    Args:
        filename: String to sanitize
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    # Limit length
    return sanitized[:100]

def ensure_directory_exists(directory):
    """
    Ensure a directory exists, create it if it doesn't
    
    Args:
        directory: Directory path
    """
    os.makedirs(directory, exist_ok=True)

def format_file_size(size_bytes):
    """
    Format file size from bytes to human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def count_files_in_directory(directory, extension=None):
    """
    Count files in a directory, optionally filtering by extension
    
    Args:
        directory: Directory path
        extension: Optional file extension to filter by
        
    Returns:
        Number of files
    """
    if not os.path.exists(directory):
        return 0
        
    count = 0
    for _, _, files in os.walk(directory):
        if extension:
            count += len([f for f in files if f.endswith(extension)])
        else:
            count += len(files)
    
    return count

def get_directory_size(directory):
    """
    Calculate the total size of files in a directory
    
    Args:
        directory: Directory path
        
    Returns:
        Size in bytes
    """
    total_size = 0
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    
    return total_size

def truncate_text(text, max_length=100, suffix="..."):
    """
    Truncate text to a maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + suffix

def get_file_extension(file_path):
    """
    Get the extension of a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension
    """
    return os.path.splitext(file_path)[1].lower()

def is_valid_url(url):
    """
    Check if a URL is valid
    
    Args:
        url: URL to check
        
    Returns:
        True if valid, False otherwise
    """
    url_pattern = re.compile(
        r'^(http|https)://'  # http:// or https://
        r'([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?'  # domain
        r'(/[a-zA-Z0-9_.,%/?=&-]*)?$'  # path
    )
    return bool(url_pattern.match(url))