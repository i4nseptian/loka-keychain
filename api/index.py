import sys
import os

# Tambahkan root directory ke path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.wsgi import application

app = application