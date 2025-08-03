#!/usr/bin/env python3
"""
Example usage of the Resume PDF Parser
"""

import sys
import json
from pathlib import Path
from resume_parser import ResumeParser


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


def main():
    """Main function for example usage."""
    if len(sys.argv) < 2:
        print("Usage: python example_usage.py <pdf_file1> [pdf_file2] ...")
        print("\nExample:")
        print("  python example_usage.py resume1.pdf")
        print("  python example_usage.py resume1.pdf resume2.pdf resume3.pdf")
        return
    
    pdf_files = sys.argv[1:]
    
    # Validate files exist
    valid_files = []
    for pdf_file in pdf_files:
        if Path(pdf_file).exists():
            valid_files.append(pdf_file)
        else:
            print(f"❌ File not found: {pdf_file}")
    
    if not valid_files:
        print("❌ No valid PDF files found.")
        return
    
    if len(valid_files) == 1:
        # Parse single resume
        result = parse_single_resume(valid_files[0])
        
        # Offer to export to JSON
        response = input("\nExport to JSON? (y/n): ").lower().strip()
        if response == 'y':
            parser = ResumeParser()
            result = parser.parse_resume(valid_files[0])
            json_file = f"{Path(valid_files[0]).stem}_parsed.json"
            export_to_json(result, json_file)
    
    else:
        # Parse multiple resumes
        results = parse_multiple_resumes(valid_files)
        
        # Offer to export all to JSON
        response = input("\nExport all results to JSON? (y/n): ").lower().strip()
        if response == 'y':
            for i, (pdf_path, result) in enumerate(zip(valid_files, results)):
                json_file = f"{Path(pdf_path).stem}_parsed.json"
                export_to_json(result, json_file)


if __name__ == "__main__":
    main()