# shared_module.py

import os
import sys

def get_script_directory():
    # Get the script directory based on the executable path
    return os.path.dirname(os.path.abspath(sys.argv[0]))
