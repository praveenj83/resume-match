#!/usr/bin/env python3
"""
Test script for the Resume PDF Parser
This script helps verify that all dependencies are properly installed.
"""

import sys
import traceback
from pathlib import Path


def test_imports():
    """Test if all required packages can be imported."""
    print("Testing imports...")
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import pdfplumber
        print("✅ pdfplumber imported successfully")
    except ImportError as e:
        print(f"❌ pdfplumber import failed: {e}")
        return False
    
    try:
        import fitz  # PyMuPDF
        print("✅ PyMuPDF (fitz) imported successfully")
    except ImportError as e:
        print(f"❌ PyMuPDF import failed: {e}")
        return False
    
    try:
        from langchain.document_loaders import PyPDFLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.schema import Document
        print("✅ LangChain components imported successfully")
    except ImportError as e:
        print(f"❌ LangChain import failed: {e}")
        return False
    
    try:
        from resume_parser import ResumeParser
        print("✅ ResumeParser imported successfully")
    except ImportError as e:
        print(f"❌ ResumeParser import failed: {e}")
        print("Make sure resume_parser.py is in the same directory")
        return False
    
    return True


def test_parser_initialization():
    """Test if the parser can be initialized."""
    print("\nTesting parser initialization...")
    
    try:
        from resume_parser import ResumeParser
        parser = ResumeParser()
        print("✅ ResumeParser initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Parser initialization failed: {e}")
        print("Full traceback:")
        traceback.print_exc()
        return False


def create_sample_pdf():
    """Create a simple sample PDF for testing if reportlab is available."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        filename = "test_resume.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        
        # Add some text content
        c.drawString(100, 750, "John Doe")
        c.drawString(100, 730, "Software Engineer")
        c.drawString(100, 710, "Email: john.doe@email.com")
        c.drawString(100, 690, "Phone: (555) 123-4567")
        
        c.drawString(100, 650, "Experience:")
        c.drawString(120, 630, "• Senior Developer at Tech Corp (2020-2023)")
        c.drawString(120, 610, "• Junior Developer at StartupXYZ (2018-2020)")
        
        c.drawString(100, 570, "Skills:")
        c.drawString(120, 550, "• Python, JavaScript, SQL")
        c.drawString(120, 530, "• Flask, Django, React")
        
        # Add a simple table-like structure
        c.drawString(100, 490, "Education:")
        c.drawString(120, 470, "University          | Degree        | Year")
        c.drawString(120, 450, "Tech University     | BS Computer   | 2018")
        c.drawString(120, 430, "                    | Science       |     ")
        
        c.save()
        print(f"✅ Sample PDF created: {filename}")
        return filename
        
    except ImportError:
        print("⚠️  reportlab not available - cannot create sample PDF")
        print("Install reportlab to generate test PDFs: pip install reportlab")
        return None
    except Exception as e:
        print(f"❌ Error creating sample PDF: {e}")
        return None


def test_with_sample_pdf(pdf_path):
    """Test parsing with a sample PDF."""
    print(f"\nTesting parser with sample PDF: {pdf_path}")
    
    try:
        from resume_parser import ResumeParser
        
        parser = ResumeParser()
        result = parser.parse_resume(pdf_path)
        
        if result['success']:
            print("✅ PDF parsed successfully!")
            print(f"   📄 Pages: {result['metadata'].get('page_count', 'Unknown')}")
            print(f"   📝 Text chunks: {len(result['text_content'])}")
            print(f"   📊 Tables: {len(result['tables'])}")
            
            # Show sample content
            if result['text_content']:
                sample_text = result['text_content'][0]['content'][:200]
                print(f"   📖 Sample text: {sample_text}...")
            
            return True
        else:
            print(f"❌ PDF parsing failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during PDF testing: {e}")
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and provide a summary."""
    print("Resume PDF Parser - Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Imports
    total_tests += 1
    if test_imports():
        tests_passed += 1
    
    # Test 2: Parser initialization
    total_tests += 1
    if test_parser_initialization():
        tests_passed += 1
    
    # Test 3: Sample PDF creation and parsing
    total_tests += 1
    sample_pdf = create_sample_pdf()
    if sample_pdf and test_with_sample_pdf(sample_pdf):
        tests_passed += 1
    elif sample_pdf is None:
        print("⚠️  Skipping PDF parsing test (no sample PDF)")
        total_tests -= 1  # Don't count this test
    
    print("\n" + "=" * 50)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The parser is ready to use.")
        if sample_pdf:
            print(f"\nYou can test with the sample PDF: {sample_pdf}")
            print(f"Run: python example_usage.py {sample_pdf}")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        print("\nCommon solutions:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Check if all files are in the same directory")
        print("3. Verify Python version compatibility")
    
    # Cleanup
    if sample_pdf and Path(sample_pdf).exists():
        try:
            Path(sample_pdf).unlink()
            print(f"\n🧹 Cleaned up sample file: {sample_pdf}")
        except Exception:
            pass


def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Quick test - just imports
        if test_imports():
            print("\n✅ Quick test passed! All dependencies are available.")
        else:
            print("\n❌ Quick test failed! Please install missing dependencies.")
    else:
        # Full test suite
        run_all_tests()


if __name__ == "__main__":
    main()