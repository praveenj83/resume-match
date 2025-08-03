import os
import logging
import traceback
from typing import Dict, List, Optional, Any
from pathlib import Path

import pandas as pd
import pdfplumber
import fitz  # PyMuPDF
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('resume_parser.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ResumeParser:
    """
    A comprehensive PDF resume parser using LangChain with table extraction capabilities.
    """
    
    def __init__(self):
        """Initialize the resume parser."""
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        logger.info("ResumeParser initialized successfully")
    
    def validate_file(self, file_path: str) -> bool:
        """
        Validate if the file exists and is a PDF.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            bool: True if file is valid, False otherwise
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                logger.error(f"File does not exist: {file_path}")
                return False
            
            if not path.suffix.lower() == '.pdf':
                logger.error(f"File is not a PDF: {file_path}")
                return False
            
            if path.stat().st_size == 0:
                logger.error(f"File is empty: {file_path}")
                return False
            
            logger.info(f"File validation successful: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating file {file_path}: {str(e)}")
            return False
    
    def extract_text_with_langchain(self, file_path: str) -> List[Document]:
        """
        Extract text from PDF using LangChain's PyPDFLoader.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            List[Document]: List of LangChain Document objects
        """
        try:
            logger.info(f"Extracting text using LangChain from: {file_path}")
            
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # Split documents into chunks
            split_docs = self.text_splitter.split_documents(documents)
            
            logger.info(f"Successfully extracted {len(split_docs)} document chunks")
            return split_docs
            
        except Exception as e:
            logger.error(f"Error extracting text with LangChain: {str(e)}")
            logger.error(traceback.format_exc())
            return []
    
    def extract_tables_with_pdfplumber(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract tables from PDF using pdfplumber.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            List[Dict]: List of extracted tables with metadata
        """
        tables_data = []
        
        try:
            logger.info(f"Extracting tables using pdfplumber from: {file_path}")
            
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    tables = page.extract_tables()
                    
                    if tables:
                        logger.info(f"Found {len(tables)} table(s) on page {page_num}")
                        
                        for table_num, table in enumerate(tables, 1):
                            if table and len(table) > 0:
                                # Convert table to DataFrame for better handling
                                try:
                                    df = pd.DataFrame(table[1:], columns=table[0])
                                    # Clean the DataFrame
                                    df = df.fillna('').astype(str)
                                    
                                    table_data = {
                                        'page': page_num,
                                        'table_number': table_num,
                                        'raw_table': table,
                                        'dataframe': df,
                                        'text_representation': df.to_string(index=False)
                                    }
                                    tables_data.append(table_data)
                                    
                                except Exception as table_error:
                                    logger.warning(f"Error processing table {table_num} on page {page_num}: {str(table_error)}")
                                    # Fallback: store raw table data
                                    table_data = {
                                        'page': page_num,
                                        'table_number': table_num,
                                        'raw_table': table,
                                        'dataframe': None,
                                        'text_representation': str(table)
                                    }
                                    tables_data.append(table_data)
            
            logger.info(f"Successfully extracted {len(tables_data)} table(s)")
            return tables_data
            
        except Exception as e:
            logger.error(f"Error extracting tables with pdfplumber: {str(e)}")
            logger.error(traceback.format_exc())
            return []
    
    def extract_metadata_with_pymupdf(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from PDF using PyMuPDF.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            Dict: PDF metadata
        """
        try:
            logger.info(f"Extracting metadata using PyMuPDF from: {file_path}")
            
            doc = fitz.open(file_path)
            metadata = doc.metadata
            
            # Add additional information
            metadata.update({
                'page_count': doc.page_count,
                'file_size': os.path.getsize(file_path),
                'file_path': file_path
            })
            
            doc.close()
            logger.info("Successfully extracted metadata")
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            logger.error(traceback.format_exc())
            return {}
    
    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """
        Complete resume parsing pipeline.
        
        Args:
            file_path (str): Path to the PDF file
            
        Returns:
            Dict: Comprehensive parsing results
        """
        logger.info(f"Starting resume parsing for: {file_path}")
        
        # Validate file
        if not self.validate_file(file_path):
            return {
                'success': False,
                'error': 'File validation failed',
                'file_path': file_path
            }
        
        result = {
            'success': True,
            'file_path': file_path,
            'text_content': [],
            'tables': [],
            'metadata': {},
            'error': None
        }
        
        try:
            # Extract text using LangChain
            documents = self.extract_text_with_langchain(file_path)
            result['text_content'] = [
                {
                    'page': doc.metadata.get('page', 'unknown'),
                    'content': doc.page_content,
                    'source': doc.metadata.get('source', file_path)
                }
                for doc in documents
            ]
            
            # Extract tables
            tables = self.extract_tables_with_pdfplumber(file_path)
            result['tables'] = tables
            
            # Extract metadata
            metadata = self.extract_metadata_with_pymupdf(file_path)
            result['metadata'] = metadata
            
            logger.info(f"Successfully completed parsing for: {file_path}")
            
        except Exception as e:
            logger.error(f"Error during parsing: {str(e)}")
            logger.error(traceback.format_exc())
            result['success'] = False
            result['error'] = str(e)
        
        return result
    
    def get_combined_text(self, parsing_result: Dict[str, Any]) -> str:
        """
        Combine all extracted text including tables into a single string.
        
        Args:
            parsing_result (Dict): Result from parse_resume method
            
        Returns:
            str: Combined text content
        """
        if not parsing_result.get('success', False):
            return ""
        
        combined_text = []
        
        # Add regular text content
        for text_chunk in parsing_result.get('text_content', []):
            combined_text.append(text_chunk['content'])
        
        # Add table content
        for table in parsing_result.get('tables', []):
            combined_text.append(f"\n--- Table from Page {table['page']} ---")
            combined_text.append(table['text_representation'])
            combined_text.append("--- End Table ---\n")
        
        return "\n".join(combined_text)
    
    def save_results_to_file(self, parsing_result: Dict[str, Any], output_path: str) -> bool:
        """
        Save parsing results to a text file.
        
        Args:
            parsing_result (Dict): Result from parse_resume method
            output_path (str): Path to save the results
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            combined_text = self.get_combined_text(parsing_result)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Resume Parsing Results\n")
                f.write(f"=" * 50 + "\n\n")
                f.write(f"Source File: {parsing_result['file_path']}\n")
                f.write(f"Success: {parsing_result['success']}\n\n")
                
                if parsing_result.get('metadata'):
                    f.write("Metadata:\n")
                    f.write("-" * 20 + "\n")
                    for key, value in parsing_result['metadata'].items():
                        f.write(f"{key}: {value}\n")
                    f.write("\n")
                
                f.write("Extracted Content:\n")
                f.write("-" * 20 + "\n")
                f.write(combined_text)
            
            logger.info(f"Results saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            return False


def main():
    """Example usage of the ResumeParser."""
    parser = ResumeParser()
    
    # Example file path - replace with actual PDF path
    pdf_path = "sample_resume.pdf"
    
    if not os.path.exists(pdf_path):
        logger.warning(f"Sample file {pdf_path} not found. Please provide a valid PDF path.")
        return
    
    # Parse the resume
    result = parser.parse_resume(pdf_path)
    
    if result['success']:
        print("Parsing successful!")
        print(f"Extracted {len(result['text_content'])} text chunks")
        print(f"Found {len(result['tables'])} tables")
        
        # Save results
        output_file = f"{Path(pdf_path).stem}_parsed.txt"
        parser.save_results_to_file(result, output_file)
        
        # Display combined text (first 500 characters)
        combined_text = parser.get_combined_text(result)
        print(f"\nFirst 500 characters of extracted text:")
        print("-" * 50)
        print(combined_text[:500] + "..." if len(combined_text) > 500 else combined_text)
        
    else:
        print(f"Parsing failed: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()