#!/usr/bin/env python3
"""
Example usage of the Resume PDF Parser
"""

import sys
import json
import argparse
import os
from pathlib import Path
from resume_parser import ResumeParser


def find_pdf_files(path: str) -> list:
    """Find all PDF files in a given path (file or directory)."""
    path_obj = Path(path)
    
    if path_obj.is_file():
        if path_obj.suffix.lower() == '.pdf':
            return [str(path_obj)]
        else:
            print(f"❌ File {path} is not a PDF file")
            return []
    
    elif path_obj.is_dir():
        pdf_files = []
        for file_path in path_obj.glob('*.pdf'):
            pdf_files.append(str(file_path))
        
        # Also check for uppercase PDF extension
        for file_path in path_obj.glob('*.PDF'):
            pdf_files.append(str(file_path))
        
        if not pdf_files:
            print(f"❌ No PDF files found in directory: {path}")
        else:
            print(f"📁 Found {len(pdf_files)} PDF file(s) in directory: {path}")
        
        return sorted(pdf_files)
    
    else:
        print(f"❌ Path does not exist: {path}")
        return []


def parse_single_resume(pdf_path: str):
    """Parse a single resume and display results."""
    print(f"Parsing resume: {pdf_path}")
    print("=" * 50)
    
    parser = ResumeParser()
    result = parser.parse_resume(pdf_path)
    
    if result['success']:
        print("✅ Parsing successful!")
        print(f"📄 Pages: {result['metadata'].get('page_count', 'Unknown')}")
        print(f"📝 Text chunks: {len(result['text_content'])}")
        print(f"📊 Tables found: {len(result['tables'])}")
        print(f"💾 File size: {result['metadata'].get('file_size', 'Unknown')} bytes")
        
        # Display metadata
        if result['metadata']:
            print("\n📋 Metadata:")
            for key, value in result['metadata'].items():
                if key not in ['file_path', 'file_size', 'page_count']:
                    print(f"  {key}: {value}")
        
        # Display table information
        if result['tables']:
            print(f"\n📊 Table Details:")
            for i, table in enumerate(result['tables'], 1):
                print(f"  Table {i}: Page {table['page']}, "
                      f"Size: {len(table['raw_table'])}x{len(table['raw_table'][0]) if table['raw_table'] else 0}")
        
        # Save to file
        output_file = f"{Path(pdf_path).stem}_parsed.txt"
        if parser.save_results_to_file(result, output_file):
            print(f"💾 Results saved to: {output_file}")
        
        # Display sample text
        combined_text = parser.get_combined_text(result)
        if combined_text:
            print(f"\n📖 Sample text (first 300 characters):")
            print("-" * 40)
            print(combined_text[:300] + "..." if len(combined_text) > 300 else combined_text)
    
    else:
        print(f"❌ Parsing failed: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 50)
    return result


def parse_multiple_resumes(pdf_paths: list):
    """Parse multiple resumes and provide summary statistics."""
    print(f"Parsing {len(pdf_paths)} resumes...")
    print("=" * 50)
    
    parser = ResumeParser()
    results = []
    
    for pdf_path in pdf_paths:
        print(f"Processing: {Path(pdf_path).name}")
        result = parser.parse_resume(pdf_path)
        results.append(result)
        
        if result['success']:
            print(f"  ✅ Success - {len(result['text_content'])} chunks, {len(result['tables'])} tables")
        else:
            print(f"  ❌ Failed - {result.get('error', 'Unknown error')}")
    
    # Summary statistics
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n📊 Summary:")
    print(f"  Total files: {len(results)}")
    print(f"  Successful: {len(successful)}")
    print(f"  Failed: {len(failed)}")
    
    if successful:
        total_chunks = sum(len(r['text_content']) for r in successful)
        total_tables = sum(len(r['tables']) for r in successful)
        print(f"  Total text chunks: {total_chunks}")
        print(f"  Total tables: {total_tables}")
    
    return results


def export_to_json(parsing_result: dict, output_path: str):
    """Export parsing results to JSON format."""
    try:
        # Create a JSON-serializable version of the result
        json_result = {
            'success': parsing_result['success'],
            'file_path': parsing_result['file_path'],
            'error': parsing_result.get('error'),
            'metadata': parsing_result.get('metadata', {}),
            'text_content': parsing_result.get('text_content', []),
            'tables': []
        }
        
        # Handle tables (exclude DataFrame objects)
        for table in parsing_result.get('tables', []):
            json_table = {
                'page': table['page'],
                'table_number': table['table_number'],
                'raw_table': table['raw_table'],
                'text_representation': table['text_representation']
            }
            json_result['tables'].append(json_table)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_result, f, indent=2, ensure_ascii=False)
        
        print(f"📄 JSON export saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error exporting to JSON: {str(e)}")
        return False


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Parse resume PDFs and extract structured information',
        epilog='''Examples:
  %(prog)s --file resume.pdf
  %(prog)s --file /path/to/resume.pdf
  %(prog)s --file /path/to/resumes/folder/
  %(prog)s --file ./resumes/ --json
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        required=True,
        help='Path to a single PDF file or directory containing PDF files'
    )
    
    parser.add_argument(
        '--json', '-j',
        action='store_true',
        help='Automatically export results to JSON format without prompting'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='.',
        help='Output directory for generated files (default: current directory)'
    )
    
    return parser.parse_args()


def main():
    """Main function for example usage."""
    args = parse_args()
    
    # Find PDF files
    pdf_files = find_pdf_files(args.file)
    
    if not pdf_files:
        print("❌ No valid PDF files found.")
        return 1
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if len(pdf_files) == 1:
        # Parse single resume
        print(f"📋 Processing single resume: {Path(pdf_files[0]).name}")
        result = parse_single_resume(pdf_files[0])
        
        # Handle JSON export
        if args.json or (not args.json and input("\nExport to JSON? (y/n): ").lower().strip() == 'y'):
            json_file = output_dir / f"{Path(pdf_files[0]).stem}_parsed.json"
            export_to_json(result, str(json_file))
    
    else:
        # Parse multiple resumes
        print(f"📋 Processing {len(pdf_files)} resumes from: {args.file}")
        results = parse_multiple_resumes(pdf_files)
        
        # Handle JSON export
        if args.json or (not args.json and input("\nExport all results to JSON? (y/n): ").lower().strip() == 'y'):
            for pdf_path, result in zip(pdf_files, results):
                json_file = output_dir / f"{Path(pdf_path).stem}_parsed.json"
                export_to_json(result, str(json_file))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())