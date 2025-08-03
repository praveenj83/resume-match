#!/usr/bin/env python3
"""
Setup script for Resume PDF Parser
Handles installation and basic setup.
"""

import subprocess
import sys
import os
from pathlib import Path


def install_requirements():
    """Install required packages from requirements.txt."""
    print("Installing dependencies...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print("Error output:", e.stderr)
        return False
    except FileNotFoundError:
        print("❌ requirements.txt not found!")
        return False


def verify_installation():
    """Verify that the installation was successful."""
    print("\nVerifying installation...")
    try:
        # Import the test script and run a quick test
        sys.path.insert(0, os.getcwd())
        from test_parser import test_imports
        return test_imports()
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False


def create_sample_config():
    """Create a sample configuration or usage guide."""
    config_content = '''# Resume PDF Parser - Quick Start Guide

## Basic Usage

```python
from resume_parser import ResumeParser

# Initialize parser
parser = ResumeParser()

# Parse a resume
result = parser.parse_resume("path/to/resume.pdf")

if result['success']:
    print(f"Found {len(result['tables'])} tables")
    print(f"Extracted {len(result['text_content'])} text chunks")
    
    # Save results
    parser.save_results_to_file(result, "output.txt")
else:
    print(f"Error: {result['error']}")
```

## Command Line Usage

```bash
# Parse single resume
python example_usage.py resume.pdf

# Parse multiple resumes
python example_usage.py resume1.pdf resume2.pdf

# Run tests
python test_parser.py
```

## Troubleshooting

1. If you get import errors, run: `pip install -r requirements.txt`
2. For permission issues, try: `pip install --user -r requirements.txt`
3. For testing: `python test_parser.py --quick`
'''
    
    try:
        with open('QUICK_START.md', 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ Created QUICK_START.md guide")
        return True
    except Exception as e:
        print(f"⚠️  Could not create quick start guide: {e}")
        return False


def main():
    """Main setup function."""
    print("Resume PDF Parser - Setup")
    print("=" * 40)
    
    # Check if we're in the right directory
    required_files = ['resume_parser.py', 'requirements.txt']
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("Please run this script from the project directory.")
        return False
    
    success = True
    
    # Install dependencies
    if not install_requirements():
        success = False
    
    # Verify installation
    if success and not verify_installation():
        success = False
    
    # Create quick start guide
    create_sample_config()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Place your PDF files in this directory")
        print("2. Run: python example_usage.py your_resume.pdf")
        print("3. Or run tests: python test_parser.py")
        print("4. Check QUICK_START.md for more examples")
    else:
        print("❌ Setup encountered some issues.")
        print("Please check the error messages above and try:")
        print("1. pip install -r requirements.txt")
        print("2. python test_parser.py --quick")
    
    return success


if __name__ == "__main__":
    main()