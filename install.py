import subprocess
import sys

# List of required libraries
libraries = [
    "requests", "urllib3", "beautifulsoup4", "termcolor", 
    "colorama", "rich"
]

def install_library(lib):
    """Install a Python library using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
        print(f"Successfully installed {lib}")
    except subprocess.CalledProcessError:
        print(f"Failed to install {lib}")

# Install all required libraries
for lib in libraries:
    install_library(lib)

print("All required libraries have been installed.")
