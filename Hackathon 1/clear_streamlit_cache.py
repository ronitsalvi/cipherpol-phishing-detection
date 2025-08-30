#!/usr/bin/env python3
"""
Clear Streamlit Cache and Fix Cached Detector Issue
The detector works perfectly but Streamlit is using a broken cached instance
"""

import os
import shutil
import glob
import time

def clear_streamlit_cache():
    """Clear all Streamlit cache directories and files"""
    
    print("🧹 STREAMLIT CACHE CLEARING UTILITY")
    print("=" * 50)
    
    cleared_items = []
    errors = []
    
    # Common Streamlit cache locations
    cache_locations = [
        os.path.expanduser("~/.streamlit"),
        os.path.expanduser("~/.streamlit/cache"),
        os.path.expanduser("~/.cache/streamlit"),
        ".streamlit",
        ".streamlit/cache",
        "__pycache__",
        "modules/__pycache__",
        "diagnostics/__pycache__"
    ]
    
    # Also check for .pyc files
    pyc_patterns = [
        "*.pyc",
        "*/*.pyc",
        "*/*/*.pyc",
        "**/*.pyc"
    ]
    
    print("🔍 Searching for Streamlit cache files and directories...")
    
    # Clear cache directories
    for cache_path in cache_locations:
        abs_path = os.path.abspath(cache_path)
        if os.path.exists(abs_path):
            try:
                if os.path.isdir(abs_path):
                    print(f"📁 Removing directory: {abs_path}")
                    shutil.rmtree(abs_path)
                    cleared_items.append(f"Directory: {abs_path}")
                else:
                    print(f"📄 Removing file: {abs_path}")
                    os.remove(abs_path)
                    cleared_items.append(f"File: {abs_path}")
            except Exception as e:
                error_msg = f"Failed to remove {abs_path}: {e}"
                print(f"❌ {error_msg}")
                errors.append(error_msg)
        else:
            print(f"⏭️  Not found: {abs_path}")
    
    # Clear .pyc files
    print("\n🐍 Searching for Python cache files (.pyc)...")
    for pattern in pyc_patterns:
        pyc_files = glob.glob(pattern, recursive=True)
        for pyc_file in pyc_files:
            try:
                abs_path = os.path.abspath(pyc_file)
                print(f"🗑️  Removing: {abs_path}")
                os.remove(abs_path)
                cleared_items.append(f"PyCache: {abs_path}")
            except Exception as e:
                error_msg = f"Failed to remove {pyc_file}: {e}"
                print(f"❌ {error_msg}")
                errors.append(error_msg)
    
    # Clear any Streamlit temporary files
    print("\n🔍 Searching for Streamlit temporary files...")
    temp_patterns = [
        "/tmp/streamlit*",
        "/var/tmp/streamlit*",
        os.path.expanduser("~/Library/Caches/streamlit*")
    ]
    
    for pattern in temp_patterns:
        temp_files = glob.glob(pattern)
        for temp_file in temp_files:
            try:
                abs_path = os.path.abspath(temp_file)
                if os.path.isdir(abs_path):
                    print(f"📁 Removing temp directory: {abs_path}")
                    shutil.rmtree(abs_path)
                else:
                    print(f"📄 Removing temp file: {abs_path}")
                    os.remove(abs_path)
                cleared_items.append(f"Temp: {abs_path}")
            except Exception as e:
                error_msg = f"Failed to remove {temp_file}: {e}"
                print(f"❌ {error_msg}")
                errors.append(error_msg)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 CACHE CLEARING SUMMARY")
    print("=" * 50)
    
    if cleared_items:
        print(f"✅ Cleared {len(cleared_items)} items:")
        for item in cleared_items:
            print(f"   • {item}")
    else:
        print("ℹ️  No cache items found to clear")
    
    if errors:
        print(f"\n❌ {len(errors)} errors occurred:")
        for error in errors:
            print(f"   • {error}")
    
    print(f"\n🎯 Cache clearing completed!")
    print("💡 Recommendation: Restart Streamlit server to ensure fresh start")

def create_cache_cleared_marker():
    """Create a marker file to indicate cache was cleared"""
    marker_path = ".cache_cleared_" + str(int(time.time()))
    with open(marker_path, 'w') as f:
        f.write(f"Streamlit cache cleared at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    print(f"🏷️  Created marker file: {marker_path}")

def main():
    """Main cache clearing function"""
    clear_streamlit_cache()
    create_cache_cleared_marker()
    
    print("\n🚀 NEXT STEPS:")
    print("1. Run: pkill -f streamlit  (to kill any existing Streamlit processes)")
    print("2. Run: python3 simple_launcher.py  (to start fresh Streamlit server)")
    print("3. Test: https://github.com/new  (should now get LOW RISK, not CRITICAL)")

if __name__ == "__main__":
    main()