#!/usr/bin/env python
import subprocess
import sys

def build():
    print("📦 Collecting static files...")
    subprocess.run([sys.executable, "manage.py", "collectstatic", "--noinput", "--clear"], check=True)
    
    print("🗄️ Running migrations...")
    subprocess.run([sys.executable, "manage.py", "migrate", "--noinput"], check=True)
    
    print("✅ Build complete!")

if __name__ == "__main__":
    build()