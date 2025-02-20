#!/usr/bin/env python3
import re
import sys
import os
from pathlib import Path

# Patterns to detect sensitive information
SENSITIVE_PATTERNS = [
    (r'private_key["\']\s*:\s*["\'].*?["\']', "Private key found"),
    (r'client_secret["\']\s*:\s*["\'].*?["\']', "Client secret found"),
    (r'refresh_token["\']\s*:\s*["\'].*?["\']', "Refresh token found"),
    (r'access_token["\']\s*:\s*["\'].*?["\']', "Access token found"),
    (r'Bearer\s+[a-zA-Z0-9\-\._~\+\/]+={0,2}', "Bearer token found"),
    (r'(?<![A-Z])[A-Z0-9]{24}(?![A-Z])', "Possible API key found"),
    (r'password["\']\s*:\s*["\'].*?["\']', "Password found"),
    (r'WIFI_PASSWORD\s*=\s*["\'](?!your_wifi).*?["\']', "WiFi password found"),
    (r'WIFI_SSID\s*=\s*["\'](?!your_wifi).*?["\']', "Real WiFi SSID found"),
    (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', "Email address found"),
    (r'(?:^|\s)(?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6}))(?::\d{1,5})?(?:[^\s]*)?(?:\?[^\s]*)?(?:#[^\s]*)?(?:$|\s)', "URL found"),
]

# Files and directories to ignore
IGNORE_PATHS = [
    '.git',
    'venv',
    '__pycache__',
    'node_modules',
    'config_local.py',
]

def should_check_file(file_path):
    """Determine if a file should be checked"""
    # Check if path contains any ignored directories
    for ignore in IGNORE_PATHS:
        if ignore in str(file_path):
            return False
            
    # Only check certain file types
    allowed_extensions = {'.py', '.json', '.yml', '.yaml', '.md', '.txt', '.ini', '.cfg'}
    return file_path.suffix in allowed_extensions

def check_file(file_path):
    """Check a single file for sensitive information"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        issues = []
        for pattern, message in SENSITIVE_PATTERNS:
            matches = re.finditer(pattern, content)
            for match in matches:
                # Skip if it's in a comment
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.start())
                if line_end == -1:
                    line_end = len(content)
                line = content[line_start:line_end]
                
                # Skip commented lines
                if line.lstrip().startswith(('#', '//', '/*', '*', '--')):
                    continue
                    
                # Skip template values
                if any(skip in match.group(0).lower() for skip in ['your_', 'example', 'template', 'placeholder']):
                    continue
                    
                # Get line number
                line_num = content.count('\n', 0, match.start()) + 1
                issues.append((line_num, message, match.group(0)))
                
        return issues
        
    except Exception as e:
        return [(0, f"Error checking file: {str(e)}", "")]

def main():
    """Main function to check all relevant files"""
    root_dir = Path(__file__).parent.parent
    issues_found = False
    
    for file_path in root_dir.rglob('*'):
        if not file_path.is_file() or not should_check_file(file_path):
            continue
            
        relative_path = file_path.relative_to(root_dir)
        issues = check_file(file_path)
        
        if issues:
            issues_found = True
            print(f"\n🔍 Checking {relative_path}:")
            for line_num, message, content in issues:
                print(f"  ❌ Line {line_num}: {message}")
                print(f"     Found: {content[:50]}..." if len(content) > 50 else f"     Found: {content}")
                
    if issues_found:
        print("\n❌ Sensitive information found in files. Commit aborted.")
        sys.exit(1)
    else:
        print("\n✅ No sensitive information found.")
        sys.exit(0)

if __name__ == '__main__':
    main() 