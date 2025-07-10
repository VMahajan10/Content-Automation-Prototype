#!/usr/bin/env python3
"""
Simple launcher for Gateway Content Automation
Run this script to start the application with automatic backend management.
"""

import os
import sys
import subprocess

def main():
    print("🚀 Gateway Content Automation Launcher")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ Error: app.py not found in current directory")
        print("💡 Please run this script from the Gateway Content Automation directory")
        sys.exit(1)
    
    # Check if virtual environment exists
    if os.path.exists(".venv"):
        print("✅ Virtual environment found")
        
        # Determine the Python executable to use
        if sys.platform == "win32":
            python_cmd = ".venv\\Scripts\\python.exe"
        else:
            python_cmd = ".venv/bin/python"
        
        if os.path.exists(python_cmd):
            print("✅ Using virtual environment Python")
            # Run the start script with virtual environment Python
            try:
                subprocess.run([python_cmd, "start_app.py"])
            except KeyboardInterrupt:
                print("\n🛑 Application stopped by user")
            except Exception as e:
                print(f"❌ Error: {e}")
                print("💡 Try running: python start_app.py")
        else:
            print("⚠️ Virtual environment Python not found, using system Python")
            try:
                subprocess.run([sys.executable, "start_app.py"])
            except KeyboardInterrupt:
                print("\n🛑 Application stopped by user")
            except Exception as e:
                print(f"❌ Error: {e}")
    else:
        print("⚠️ Virtual environment not found, using system Python")
        print("💡 Consider creating a virtual environment: python -m venv .venv")
        try:
            subprocess.run([sys.executable, "start_app.py"])
        except KeyboardInterrupt:
            print("\n🛑 Application stopped by user")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 