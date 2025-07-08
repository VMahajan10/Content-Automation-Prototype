#!/usr/bin/env python3
"""
Gateway Content Automation - Startup Script
This script ensures the backend server is running and starts the Streamlit app.
"""

import subprocess
import time
import requests
import sys
import os
import signal
import psutil
import atexit

# Global variable to track backend process
backend_process = None

def kill_existing_backend():
    """Kill any existing backend processes"""
    try:
        # Find and kill any existing upload_backend.py processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and 'upload_backend.py' in ' '.join(proc.info['cmdline']):
                    print(f"🔄 Killing existing backend process (PID: {proc.info['pid']})")
                    proc.terminate()
                    proc.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                pass
    except Exception as e:
        print(f"⚠️ Warning: Could not kill existing processes: {e}")

def check_backend():
    """Check if backend server is running"""
    try:
        response = requests.get("http://localhost:8000/", timeout=3)
        return response.status_code == 200
    except:
        return False

def start_backend():
    """Start the backend server with improved reliability"""
    global backend_process
    
    print("🚀 Starting backend server...")
    
    # First, kill any existing backend processes
    kill_existing_backend()
    
    try:
        # Start backend in background with better error handling
        backend_process = subprocess.Popen(
            ["python", "upload_backend.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Wait for backend to start with better timeout handling
        print("⏳ Waiting for backend server to start...")
        for i in range(15):  # Increased timeout to 15 seconds
            time.sleep(1)
            if check_backend():
                print("✅ Backend server started successfully")
                return backend_process
            if i < 5:
                print(f"⏳ Waiting for backend... ({i+1}/15)")
            elif i == 5:
                print("⏳ Backend is taking longer than expected...")
            elif i % 3 == 0:
                print(f"⏳ Still waiting... ({i+1}/15)")
        
        # If we get here, backend didn't start
        print("❌ Backend server failed to start within timeout")
        if backend_process:
            backend_process.terminate()
            try:
                backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                backend_process.kill()
        return None
        
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def cleanup_backend():
    """Cleanup function to stop backend when app exits"""
    global backend_process
    if backend_process:
        try:
            print("\n🛑 Stopping backend server...")
            backend_process.terminate()
            backend_process.wait(timeout=5)
            print("✅ Backend server stopped")
        except:
            try:
                backend_process.kill()
                print("✅ Backend server force stopped")
            except:
                pass
        backend_process = None

def main():
    global backend_process
    
    print("🎯 Gateway Content Automation - Startup")
    print("=" * 50)
    
    # Register cleanup function
    atexit.register(cleanup_backend)
    
    # Check if backend is already running
    if check_backend():
        print("✅ Backend server is already running")
    else:
        # Start backend with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            if attempt > 0:
                print(f"🔄 Retry attempt {attempt + 1}/{max_retries}")
                time.sleep(2)  # Wait before retry
            
            backend_process = start_backend()
            if backend_process:
                break
            else:
                print(f"❌ Backend start attempt {attempt + 1} failed")
        
        if not backend_process:
            print("❌ Failed to start backend server after all attempts")
            print("💡 You can still run the app, but some features may not work")
            print("💡 To start backend manually: python upload_backend.py")
            print("💡 Check if port 8000 is available: lsof -i :8000")
    
    print("\n🌐 Starting Streamlit app...")
    print("💡 The app will open in your browser at http://localhost:8501")
    print("💡 Press Ctrl+C to stop the app")
    print("=" * 50)
    
    try:
        # Start Streamlit app
        subprocess.run(["streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n🛑 App stopped by user")
    except Exception as e:
        print(f"❌ Error starting Streamlit app: {e}")
        print("💡 Make sure Streamlit is installed: pip install streamlit")
    finally:
        # Ensure cleanup happens
        cleanup_backend()

if __name__ == "__main__":
    main() 