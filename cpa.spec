# -*- mode: python ; coding: utf-8 -*-
import os
import sys
import site
import importlib
import shutil
import subprocess

# Get the path to pip to find installed packages
try:
    import pip
    pip_path = os.path.dirname(pip.__file__)
    print(f"Pip path: {pip_path}")
except ImportError:
    pip_path = None
    print("Pip not found, using alternative methods")

# Create a directory to hold source files
work_dir = "pyinstaller_build"
if not os.path.exists(work_dir):
    os.makedirs(work_dir)

# Initialize data lists
all_datas = []
all_binaries = []
all_hiddenimports = ['speech_recognition', 'gtts', 'gtts.lang', 'gtts.tokenizer', 'gtts.utils', 
                    'pydub', 'pydub.utils', 'pydub.silence', 'pydub.generators',
                    'pyautogui']

# Dictionary mapping module import names to PyPI package names
package_mapping = {
    'speech_recognition': 'SpeechRecognition',
    'gtts': 'gTTS',
    'pydub': 'pydub',
    'pyautogui': 'PyAutoGUI'
}

# Function to collect module files
def collect_module(module_name, target_name=None):
    if target_name is None:
        target_name = module_name
    
    module_dir = None
    module_path = None
    
    # Method 1: Try importing and getting __file__
    try:
        module = importlib.import_module(module_name)
        module_path = module.__file__
        module_dir = os.path.dirname(module_path)
        print(f"Found {module_name} at: {module_dir}")
    except ImportError:
        print(f"Could not import {module_name} directly")
    
    # Method 2: Use pip to install module into work directory
    if not module_dir or not os.path.exists(module_dir):
        print(f"Installing {module_name} into a temporary directory")
        try:
            # Use the package_name for pip install, target_name for directory
            package_name = package_mapping.get(module_name, module_name)
            print(f"Using package name: {package_name}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", 
                                "--target", work_dir, package_name])
            module_dir = os.path.join(work_dir, target_name)
            if os.path.exists(module_dir):
                print(f"Installed {package_name} to: {module_dir}")
            else:
                # Check if it was installed with a different name
                possible_dirs = [
                    os.path.join(work_dir, name)
                    for name in [target_name, module_name.replace('_', ''), package_name.lower()]
                ]
                for possible_dir in possible_dirs:
                    if os.path.exists(possible_dir):
                        module_dir = possible_dir
                        print(f"Found module at: {module_dir}")
                        break
                if not module_dir or not os.path.exists(module_dir):
                    print(f"Failed to install {package_name}")
        except Exception as e:
            print(f"Error installing with pip: {e}")
    
    # Add files to datas
    file_count = 0
    if module_dir and os.path.exists(module_dir):
        print(f"Adding {module_name} from {module_dir}")
        # Copy all files from the module directory
        for root, dirs, files in os.walk(module_dir):
            for file in files:
                src_file = os.path.join(root, file)
                # Calculate relative path for destination
                rel_path = os.path.relpath(root, os.path.dirname(module_dir))
                if rel_path == '.':
                    dest_dir = target_name
                else:
                    dest_dir = os.path.join(target_name, rel_path)
                # Add to datas
                all_datas.append((src_file, dest_dir))
                file_count += 1
        print(f"Added {file_count} files from {module_name}")
    else:
        print(f"WARNING: Could not find {module_name} directory")

        # Try to find module in site-packages as a last resort
        for site_path in sys.path:
            possible_path = os.path.join(site_path, module_name)
            if os.path.isdir(possible_path):
                print(f"Found {module_name} in Python path: {possible_path}")
                module_dir = possible_path
                # Add files to datas
                for root, dirs, files in os.walk(module_dir):
                    for file in files:
                        src_file = os.path.join(root, file)
                        # Calculate relative path for destination
                        rel_path = os.path.relpath(root, os.path.dirname(module_dir))
                        if rel_path == '.':
                            dest_dir = target_name
                        else:
                            dest_dir = os.path.join(target_name, rel_path)
                        # Add to datas
                        all_datas.append((src_file, dest_dir))
                        file_count += 1
                print(f"Added {file_count} files from {module_name} (found in path)")
                break
    
    return module_dir

# Collect required modules
sr_dir = collect_module('speech_recognition')
gtts_dir = collect_module('gtts')
pydub_dir = collect_module('pydub')
pyautogui_dir = collect_module('pyautogui')

# Create bootstrap directory
bootstrap_dir = os.path.join(work_dir, "bootstrap")
if not os.path.exists(bootstrap_dir):
    os.makedirs(bootstrap_dir)

# Create a bootstrap module template
def create_bootstrap_module(module_name, target_name=None):
    if target_name is None:
        target_name = module_name
    
    file_path = os.path.join(bootstrap_dir, f"{target_name}.py")
    with open(file_path, "w") as f:
        f.write(f"""
# This is a bootstrap module for {module_name}
import os
import sys
import importlib.util

def find_and_load():
    # Find the {module_name} directory
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
    module_dir = os.path.join(exe_dir, '{target_name}')
    
    if os.path.exists(module_dir):
        # Add it to the path
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
        
        # Try to find __init__.py
        init_py = os.path.join(module_dir, '__init__.py')
        if os.path.exists(init_py):
            try:
                # Load the module
                spec = importlib.util.spec_from_file_location('{module_name}', init_py)
                module = importlib.util.module_from_spec(spec)
                sys.modules['{module_name}'] = module
                spec.loader.exec_module(module)
                return module
            except Exception as e:
                print(f"Error loading {module_name}: {{e}}")
    
    raise ImportError("Could not find {module_name} package")

# Load the module
sys.modules['{module_name}'] = find_and_load()
""")
    
    # Add the bootstrap file to datas
    all_datas.append((file_path, '.'))
    return file_path

# Create bootstrap modules for each module
create_bootstrap_module('speech_recognition')
create_bootstrap_module('gtts')
create_bootstrap_module('pydub')
create_bootstrap_module('pyautogui')  # Added PyAutoGUI

# Create a runtime hook
with open(os.path.join(work_dir, "runtime_hook.py"), "w") as f:
    f.write("""
import os
import sys
import importlib.util

# Add current directory to path
exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
if exe_dir not in sys.path:
    sys.path.insert(0, exe_dir)
    print(f"Added {exe_dir} to Python path")

# Add module directories to path
for module_name in ['speech_recognition', 'gtts', 'pydub', 'pyautogui']:
    module_dir = os.path.join(exe_dir, module_name)
    if os.path.exists(module_dir) and module_dir not in sys.path:
        sys.path.insert(0, module_dir)
        print(f"Added {module_dir} to Python path")
    
    # Try alternative name (without underscores)
    alt_module_dir = os.path.join(exe_dir, module_name.replace('_', ''))
    if os.path.exists(alt_module_dir) and alt_module_dir not in sys.path:
        sys.path.insert(0, alt_module_dir)
        print(f"Added {alt_module_dir} to Python path")
        
    # Also add parent directory
    parent_dir = os.path.dirname(module_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
        print(f"Added {parent_dir} to Python path")

# Print Python path for debugging
print("Python path:")
for p in sys.path:
    print(f" - {p}")
""")

# Use PyInstaller's utilities for other packages
from PyInstaller.utils.hooks import collect_all

# Add other necessary packages
for package in ['numpy', 'pyperclip', 'pymsgbox', 'pytweening']:
    try:
        print(f"Collecting {package}...")
        datas, binaries, hiddenimports = collect_all(package)
        all_datas.extend(datas)
        all_binaries.extend(binaries)
        all_hiddenimports.extend(hiddenimports)
    except Exception as e:
        print(f"Warning: Failed to collect {package}: {e}")

a = Analysis(
    ['cross-platform-assistant.py'],
    pathex=[work_dir, bootstrap_dir],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[os.path.join(work_dir, "runtime_hook.py")],
    excludes=[],
    noarchive=True,  # Important for module loading
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='cross-platform-assistant',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)