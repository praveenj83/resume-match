# Resume PDF Parser

A comprehensive PDF parsing tool for resumes using LangChain with advanced table extraction capabilities, error handling, and logging.

## Features

- **LangChain Integration**: Uses LangChain's PyPDFLoader for robust text extraction
- **Table Handling**: Extracts and processes tables using pdfplumber and pandas
- **Comprehensive Metadata**: Extracts PDF metadata using PyMuPDF
- **Error Handling**: Robust error handling with detailed logging
- **Multiple Output Formats**: Text and JSON export options
- **File Validation**: Validates PDF files before processing
- **Batch Processing**: Support for processing multiple resumes

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from resume_parser import ResumeParser

# Initialize the parser
parser = ResumeParser()

# Parse a resume
result = parser.parse_resume("path/to/resume.pdf")

if result['success']:
    print(f"Extracted {len(result['text_content'])} text chunks")
    print(f"Found {len(result['tables'])} tables")
    
    # Get combined text
    full_text = parser.get_combined_text(result)
    print(full_text)
    
    # Save to file
    parser.save_results_to_file(result, "output.txt")
else:
    print(f"Error: {result['error']}")
```

### Command Line Usage

Process a single resume:
```bash
python example_usage.py resume.pdf
```

Process multiple resumes:
```bash
python example_usage.py resume1.pdf resume2.pdf resume3.pdf
```

### Advanced Usage

```python
from resume_parser import ResumeParser
import json

parser = ResumeParser()
result = parser.parse_resume("resume.pdf")

# Access different components
text_content = result['text_content']  # List of text chunks
tables = result['tables']              # List of extracted tables
metadata = result['metadata']          # PDF metadata

# Work with tables
for table in tables:
    print(f"Table on page {table['page']}:")
    if table['dataframe'] is not None:
        # Access as pandas DataFrame
        df = table['dataframe']
        print(df.head())
    else:
        # Access raw table data
        print(table['raw_table'])
```

## Output Structure

The parser returns a dictionary with the following structure:

```python
{
    'success': bool,           # Whether parsing was successful
    'file_path': str,          # Path to the source PDF
    'text_content': [          # List of extracted text chunks
        {
            'page': int,       # Page number
            'content': str,    # Text content
            'source': str      # Source file path
        }
    ],
    'tables': [               # List of extracted tables
        {
            'page': int,              # Page number
            'table_number': int,      # Table number on page
            'raw_table': list,        # Raw table data as nested lists
            'dataframe': DataFrame,   # Pandas DataFrame (if successful)
            'text_representation': str # String representation
        }
    ],
    'metadata': {             # PDF metadata
        'page_count': int,    # Number of pages
        'file_size': int,     # File size in bytes
        'title': str,         # Document title (if available)
        'author': str,        # Document author (if available)
        # ... other metadata fields
    },
    'error': str              # Error message (if failed)
}
```

## Logging

The tool creates detailed logs in `resume_parser.log` and outputs to console. Log levels include:

- **INFO**: Normal operation messages
- **WARNING**: Non-critical issues (e.g., table processing problems)
- **ERROR**: Critical errors with full tracebacks

## Error Handling

The parser includes comprehensive error handling for:

- File validation (existence, format, size)
- PDF corruption or access issues
- Table extraction failures
- Memory limitations
- Encoding problems

## Dependencies

- **langchain**: Document loading and text splitting
- **pdfplumber**: Table extraction and detailed PDF analysis
- **pymupdf (fitz)**: Metadata extraction and PDF manipulation
- **pandas**: Table data processing
- **pypdf2**: Additional PDF support
- **python-magic**: File type detection

## Limitations

- Large PDFs may require significant memory
- Complex table layouts might not be perfectly extracted
- Scanned PDFs require OCR (not included in this tool)
- Some password-protected PDFs may not be supported

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the terms specified in the LICENSE file.