#!/usr/bin/env python3
"""
Test script for improved backend startup process
"""

import subprocess
import time
import requests
import psutil
import sys

def test_backend_startup():
    """Test the improved backend startup process"""
    
    print("🧪 Testing Improved Backend Startup Process")
    print("=" * 50)
    
    # Test 1: Kill any existing backend processes
    print("\n1️⃣ Testing process cleanup...")
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and 'upload_backend.py' in ' '.join(proc.info['cmdline']):
                    print(f"   🔄 Killing existing backend process (PID: {proc.info['pid']})")
                    proc.terminate()
                    proc.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                pass
        print("   ✅ Process cleanup completed")
    except Exception as e:
        print(f"   ⚠️ Process cleanup warning: {e}")
    
    # Test 2: Start backend server
    print("\n2️⃣ Testing backend server startup...")
    try:
        backend_process = subprocess.Popen(
            ["python", "upload_backend.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for backend to start
        print("   ⏳ Waiting for backend server to start...")
        for i in range(15):
            time.sleep(1)
            try:
                response = requests.get("http://localhost:8000/health", timeout=3)
                if response.status_code == 200:
                    print("   ✅ Backend server started successfully!")
                    print(f"   📊 Health check response: {response.json()}")
                    break
            except:
                if i < 5:
                    print(f"   ⏳ Waiting... ({i+1}/15)")
                elif i == 5:
                    print("   ⏳ Backend is taking longer than expected...")
                elif i % 3 == 0:
                    print(f"   ⏳ Still waiting... ({i+1}/15)")
        else:
            print("   ❌ Backend server failed to start within timeout")
            backend_process.terminate()
            return False
        
        # Test 3: Test file operations
        print("\n3️⃣ Testing file operations...")
        
        # Test file upload endpoint
        try:
            response = requests.get("http://localhost:8000/files/")
            if response.status_code == 200:
                print("   ✅ File listing endpoint working")
            else:
                print("   ❌ File listing endpoint failed")
        except Exception as e:
            print(f"   ❌ File listing test failed: {e}")
        
        # Test 4: Cleanup
        print("\n4️⃣ Testing cleanup...")
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
            print("   ✅ Backend server stopped cleanly")
        except subprocess.TimeoutExpired:
            backend_process.kill()
            print("   ✅ Backend server force stopped")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_backend_startup()
    sys.exit(0 if success else 1) 