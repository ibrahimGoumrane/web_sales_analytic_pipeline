from urllib.parse import urljoin

def handle_url(url, base_url=None):
    """
    Normalize and construct full URLs from relative or absolute URLs.
    
    Args:
        url: The URL to process (can be relative or absolute)
        base_url: Base URL to prepend to relative URLs (optional)
        
    Returns:
        Properly formatted full URL
    """
    if not url:
        return None
    
    # Already a full URL
    if url.startswith('http://') or url.startswith('https://'):
        return url
    
    if base_url:
        return urljoin(base_url, url)
    
    return url
