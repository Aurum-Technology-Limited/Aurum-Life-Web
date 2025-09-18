#!/usr/bin/env python3
"""
Dead Code Removal Script for Aurum Life Frontend
Identifies and removes unused imports and dead code
"""

import os
import re
from pathlib import Path

def analyze_component_imports(file_path):
    """Analyze a React component file for unused imports"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract imports
    import_pattern = r'import\s+(?:{([^}]+)}|\*\s+as\s+\w+|\w+)\s+from\s+[\'"]([^\'"]+)[\'"]'
    imports = re.findall(import_pattern, content)
    
    unused_imports = []
    
    for match in imports:
        if match[0]:  # Named imports
            named_imports = [imp.strip() for imp in match[0].split(',')]
            for named_import in named_imports:
                # Clean up the import name (remove 'as' aliases)
                import_name = named_import.split(' as ')[0].strip()
                
                # Check if import is used in the file
                if not re.search(rf'\b{re.escape(import_name)}\b', content.replace(f'import {{{match[0]}}}', '')):
                    unused_imports.append((import_name, match[1]))
    
    return unused_imports

def remove_unused_imports(file_path, unused_imports):
    """Remove unused imports from a file"""
    if not unused_imports:
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    for import_name, module in unused_imports:
        # Remove from named imports
        pattern = rf'import\s+\{{([^}}]*{re.escape(import_name)}[^}}]*)\}}\s+from\s+[\'"][^\'"]*{re.escape(module)}[\'"]'
        match = re.search(pattern, content)
        if match:
            imports_str = match.group(1)
            imports_list = [imp.strip() for imp in imports_str.split(',')]
            new_imports = [imp for imp in imports_list if import_name not in imp]
            
            if new_imports:
                new_imports_str = ', '.join(new_imports)
                new_import_line = f"import {{{new_imports_str}}} from '{module}'"
                content = re.sub(pattern, new_import_line, content)
            else:
                # Remove entire import line if no imports left
                content = re.sub(pattern + r';?\n?', '', content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """Main function to clean up dead code"""
    print("🧹 Dead Code Removal for Aurum Life Frontend")
    print("=" * 50)
    
    frontend_dir = Path("/app/frontend/src")
    components_dir = frontend_dir / "components"
    
    total_files = 0
    cleaned_files = 0
    
    # Analyze component files
    for file_path in components_dir.glob("*.jsx"):
        total_files += 1
        print(f"\n📄 Analyzing {file_path.name}...")
        
        unused_imports = analyze_component_imports(file_path)
        
        if unused_imports:
            print(f"   🗑️  Found {len(unused_imports)} unused imports:")
            for import_name, module in unused_imports:
                print(f"      - {import_name} from '{module}'")
            
            if remove_unused_imports(file_path, unused_imports):
                print(f"   ✅ Cleaned up unused imports")
                cleaned_files += 1
        else:
            print(f"   ✅ No unused imports found")
    
    print(f"\n📊 Summary:")
    print(f"   📄 Files analyzed: {total_files}")
    print(f"   🧹 Files cleaned: {cleaned_files}")
    print(f"   ✅ Dead code removal complete!")

if __name__ == "__main__":
    main()