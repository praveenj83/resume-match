# Resume PDF Parser & Job Profile Matcher

A comprehensive PDF parsing tool for resumes using LangChain with advanced table extraction capabilities, error handling, and logging. Now includes AI-powered job profile matching using GPT-4o to assess how well resumes fit job descriptions.

## Features

### Resume Parsing
- **LangChain Integration**: Uses LangChain's PyPDFLoader for robust text extraction
- **Table Handling**: Extracts and processes tables using pdfplumber and pandas
- **Comprehensive Metadata**: Extracts PDF metadata using PyMuPDF
- **Error Handling**: Robust error handling with detailed logging
- **Multiple Output Formats**: Text and JSON export options
- **File Validation**: Validates PDF files before processing
- **Batch Processing**: Support for processing multiple resumes

### AI-Powered Job Matching (NEW!)
- **GPT-4o Integration**: Uses OpenAI's GPT-4o for intelligent resume assessment
- **Job Profile Analysis**: Reads job descriptions from text files
- **Scoring System**: Provides 0-10 match scores for resume-job fit
- **Detailed Assessment**: Analyzes skills, experience, education, and industry background
- **Structured Reports**: Generates comprehensive assessment reports with strengths, gaps, and recommendations
- **Batch Assessment**: Process multiple resumes against a single job profile
- **JSON Export**: Machine-readable assessment results

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up OpenAI API key or TogetherAI API key (required for job profile matching):

```bash
export OPENAI_API_KEY='your-openai-api-key-here'
```
or
```bash
export TOGETHER_API_KEY='your-togetherai-api-key-here'
```

## Usage

### Resume Parsing (Basic Usage)

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

### Job Profile Assessment (NEW!)

```python
from resume_job_matcher import ResumeJobMatcher

# Initialize the matcher (requires OPENAI_API_KEY)
matcher = ResumeJobMatcher()

# Assess a single resume against a job profile
result = matcher.assess_resume_job_fit(
    resume_path="candidate_resume.pdf",
    job_profile_path="job_description.txt"
)

if result['success']:
    assessment = result['llm_assessment']
    print(f"Match Score: {assessment['overall_score']}/10")
    print(f"Summary: {assessment['summary']}")
    
    # Save detailed report
    matcher.save_assessment_report(result, "assessment_report.txt")
else:
    print(f"Assessment failed: {result['error']}")
```

### Command Line Usage

#### Resume Parsing
Process a single resume:
```bash
python example_usage.py --file resume.pdf
```

Process multiple resumes within a folder:
```bash
python example_usage.py --file Samples/
```

#### Job Profile Assessment
Assess a single resume against a job profile:
```bash
python assess_resume_example.py --resume resume.pdf --job-profile job_description.txt
```

Batch assess multiple resumes:
```bash
python assess_resume_example.py --job-profile job_description.txt --resume-dir ./resumes/
```

Create sample files for testing:
```bash
python assess_resume_example.py --create-samples
```

### Advanced Usage

#### Resume Parsing Advanced Features
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

#### Job Profile Assessment Advanced Features
```python
from resume_job_matcher import ResumeJobMatcher

matcher = ResumeJobMatcher()

# Batch assessment of multiple resumes
results = matcher.batch_assess_resumes(
    job_profile_path="job_description.txt",
    resume_directory="./candidate_resumes/",
    output_directory="./assessment_reports/"
)

# Process results
for result in results:
    if result['success']:
        score = result['llm_assessment']['overall_score']
        resume_name = result['resume_path']
        print(f"{resume_name}: {score}/10")
```

## Output Structure

### Resume Parser Output
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

### Job Profile Assessment Output
The job matcher returns a comprehensive assessment structure:

```python
{
    'success': bool,                    # Whether assessment was successful
    'resume_path': str,                 # Path to the resume file
    'job_profile_path': str,            # Path to the job profile file
    'resume_parsing_result': dict,      # Full resume parsing results
    'job_profile_content': str,         # Job profile text content
    'llm_assessment': {               # GPT-4o analysis results
        'overall_score': int,           # Match score (0-10)
        'summary': str,                 # Executive summary
        'detailed_analysis': {
            'skills_match': str,        # Skills alignment analysis
            'experience_relevance': str, # Experience relevance analysis
            'education_qualifications': str, # Education assessment
            'industry_background': str  # Industry fit analysis
        },
        'strengths': [str],             # Candidate strengths
        'gaps_and_concerns': [str],     # Areas of concern
        'recommendations': {
            'proceed_with_candidate': str,  # Yes/No/Maybe
            'additional_information_needed': str,
            'development_areas': [str]   # Areas for improvement
        }
    },
    'error': str                        # Error message (if failed)
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

### Core Dependencies
- **langchain**: Document loading and text splitting
- **pdfplumber**: Table extraction and detailed PDF analysis
- **pymupdf (fitz)**: Metadata extraction and PDF manipulation
- **pandas**: Table data processing
- **pypdf**: Additional PDF support
- **python-magic**: File type detection

### AI Integration Dependencies (NEW!)
- **openai**: GPT-4o API integration for job profile assessment

## Limitations

### Resume Parsing Limitations
- Large PDFs may require significant memory
- Complex table layouts might not be perfectly extracted
- Scanned PDFs require OCR (not included in this tool)
- Some password-protected PDFs may not be supported

### Job Profile Assessment Limitations
- Requires OpenAI API key or TogetherAI API key along with Internet connection
- Assessment quality depends on the quality of job profile descriptions
- May have rate limits based on LLM used

## License

This project is licensed under the terms specified in the LICENSE file.
