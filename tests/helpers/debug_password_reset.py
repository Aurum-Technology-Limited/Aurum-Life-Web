#!/usr/bin/env python3
"""
Debug Password Reset - Check Supabase Response Structure
"""

from supabase_client import supabase_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_generate_link():
    """Debug the generate_link response structure"""
    try:
        supabase = supabase_manager.get_client()
        
        # Test the generate_link call
        opts = {
            "email": "marc.alleyne@aurumtechnologyltd.com", 
            "type": "recovery",
            "options": {"redirect_to": "https://smart-life-os.preview.emergentagent.com/reset-password"}
        }
        
        print("Calling supabase.auth.admin.generate_link with:")
        print(f"  opts: {opts}")
        
        gen = supabase.auth.admin.generate_link(opts)
        
        print(f"\nResponse type: {type(gen)}")
        print(f"Response: {gen}")
        
        if hasattr(gen, '__dict__'):
            print(f"Response attributes: {gen.__dict__}")
        
        if hasattr(gen, 'data'):
            print(f"gen.data: {gen.data}")
            print(f"gen.data type: {type(gen.data)}")
            if hasattr(gen.data, '__dict__'):
                print(f"gen.data attributes: {gen.data.__dict__}")
        
        # Try different ways to extract the action_link
        recovery_url = None
        
        # Method 1: gen.data.action_link
        if hasattr(gen, 'data') and hasattr(gen.data, 'action_link'):
            recovery_url = gen.data.action_link
            print(f"Method 1 (gen.data.action_link): {recovery_url}")
        
        # Method 2: gen.data as dict
        if hasattr(gen, 'data') and isinstance(gen.data, dict):
            recovery_url = gen.data.get('action_link')
            print(f"Method 2 (gen.data dict): {recovery_url}")
        
        # Method 3: gen as dict
        if isinstance(gen, dict):
            recovery_url = gen.get('action_link')
            print(f"Method 3 (gen dict): {recovery_url}")
        
        # Method 4: Check for other possible keys
        if hasattr(gen, 'data') and isinstance(gen.data, dict):
            print(f"All keys in gen.data: {list(gen.data.keys())}")
        
        if isinstance(gen, dict):
            print(f"All keys in gen: {list(gen.keys())}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_generate_link()