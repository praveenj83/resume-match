import os
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

import openai
from resume_parser import ResumeParser

# Configure logging
logger = logging.getLogger(__name__)


class ResumeJobMatcher:
    """
    A tool to assess how well a resume matches a job profile description using GPT-4o.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the resume job matcher.
        
        Args:
            api_key (Optional[str]): OpenAI API key. If not provided, will try to get from environment.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Initialize resume parser
        self.resume_parser = ResumeParser()
        
        logger.info("ResumeJobMatcher initialized successfully")
    
    def read_job_profile(self, file_path: str) -> str:
        """
        Read job profile description from a text file.
        
        Args:
            file_path (str): Path to the job profile text file
            
        Returns:
            str: Job profile description content
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            Exception: If there's an error reading the file
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise FileNotFoundError(f"Job profile file does not exist: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                raise ValueError(f"Job profile file is empty: {file_path}")
            
            logger.info(f"Successfully read job profile from: {file_path}")
            return content
            
        except Exception as e:
            logger.error(f"Error reading job profile file {file_path}: {str(e)}")
            raise
    
    def create_assessment_prompt(self, job_profile: str, resume_text: str) -> str:
        """
        Create a prompt for GPT-4o to assess resume-job fit.
        
        Args:
            job_profile (str): Job profile description
            resume_text (str): Resume content
            
        Returns:
            str: Formatted prompt for GPT-4o
        """
        prompt = f"""
You are an expert HR professional and recruitment specialist. Your task is to assess how well a candidate's resume matches a given job profile description.

Please analyze the following job profile description and resume, then provide a comprehensive assessment.

**JOB PROFILE DESCRIPTION:**
{job_profile}

**CANDIDATE RESUME:**
{resume_text}

**ASSESSMENT REQUIREMENTS:**

1. **Overall Match Score**: Provide a score from 0-10 (where 10 is a perfect match) that represents how well this resume fits the job profile.

2. **Detailed Analysis**: Provide a structured analysis covering:
   - **Skills Match**: How well do the candidate's skills align with job requirements?
   - **Experience Relevance**: How relevant is their work experience to the role?
   - **Education & Qualifications**: Do they meet the educational requirements?
   - **Industry Background**: How well does their industry experience align?

3. **Strengths**: List the top 3-5 strengths that make this candidate a good fit.

4. **Gaps & Concerns**: Identify any significant gaps or concerns in the candidate's profile.

5. **Recommendations**: Provide specific recommendations for:
   - Whether to proceed with this candidate (Yes/No/Maybe)
   - What additional information or clarification might be needed
   - Areas where the candidate might need development

**OUTPUT FORMAT:**
Please structure your response as a JSON object with the following format:

{{
    "overall_score": <score_0_to_10>,
    "summary": "<brief_2_3_sentence_summary>",
    "detailed_analysis": {{
        "skills_match": "<analysis>",
        "experience_relevance": "<analysis>",
        "education_qualifications": "<analysis>",
        "industry_background": "<analysis>"
    }},
    "strengths": [
        "<strength_1>",
        "<strength_2>",
        "<strength_3>"
    ],
    "gaps_and_concerns": [
        "<gap_or_concern_1>",
        "<gap_or_concern_2>"
    ],
    "recommendations": {{
        "proceed_with_candidate": "<Yes/No/Maybe>",
        "additional_information_needed": "<what_to_clarify>",
        "development_areas": [
            "<area_1>",
            "<area_2>"
        ]
    }}
}}

Ensure your response is valid JSON and provides actionable insights for the hiring decision.
"""
        return prompt
    
    def query_gpt4o(self, prompt: str) -> Dict[str, Any]:
        """
        Query GPT-4o with the assessment prompt.
        
        Args:
            prompt (str): The formatted prompt for assessment
            
        Returns:
            Dict[str, Any]: Parsed response from GPT-4o
            
        Raises:
            Exception: If there's an error with the OpenAI API call
        """
        try:
            logger.info("Sending assessment request to GPT-4o")
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert HR professional and recruitment specialist. Always respond with valid JSON format as requested."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent, focused responses
                max_tokens=2000
            )
            
            # Extract the response content
            content = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                assessment_result = json.loads(content)
                logger.info("Successfully received and parsed GPT-4o response")
                return assessment_result
            except json.JSONDecodeError as e:
                logger.warning(f"GPT-4o response was not valid JSON: {e}")
                # Return a structured fallback response
                return {
                    "overall_score": None,
                    "summary": content,
                    "detailed_analysis": {},
                    "strengths": [],
                    "gaps_and_concerns": [],
                    "recommendations": {},
                    "raw_response": content,
                    "parsing_error": str(e)
                }
            
        except Exception as e:
            logger.error(f"Error querying GPT-4o: {str(e)}")
            raise
    
    def assess_resume_job_fit(self, resume_path: str, job_profile_path: str) -> Dict[str, Any]:
        """
        Complete pipeline to assess how well a resume fits a job profile.
        
        Args:
            resume_path (str): Path to the resume PDF file
            job_profile_path (str): Path to the job profile text file
            
        Returns:
            Dict[str, Any]: Comprehensive assessment results
        """
        logger.info(f"Starting resume-job fit assessment")
        logger.info(f"Resume: {resume_path}")
        logger.info(f"Job Profile: {job_profile_path}")
        
        result = {
            'success': False,
            'resume_path': resume_path,
            'job_profile_path': job_profile_path,
            'resume_parsing_result': None,
            'job_profile_content': None,
            'gpt4o_assessment': None,
            'error': None
        }
        
        try:
            # Step 1: Read job profile
            logger.info("Step 1: Reading job profile description")
            job_profile = self.read_job_profile(job_profile_path)
            result['job_profile_content'] = job_profile
            
            # Step 2: Parse resume
            logger.info("Step 2: Parsing resume PDF")
            resume_result = self.resume_parser.parse_resume(resume_path)
            result['resume_parsing_result'] = resume_result
            
            if not resume_result['success']:
                raise Exception(f"Resume parsing failed: {resume_result.get('error', 'Unknown error')}")
            
            # Step 3: Get combined resume text
            logger.info("Step 3: Extracting resume text content")
            resume_text = self.resume_parser.get_combined_text(resume_result)
            
            if not resume_text.strip():
                raise Exception("No text content extracted from resume")
            
            # Step 4: Create assessment prompt
            logger.info("Step 4: Creating assessment prompt")
            prompt = self.create_assessment_prompt(job_profile, resume_text)
            
            # Step 5: Query GPT-4o
            logger.info("Step 5: Querying GPT-4o for assessment")
            assessment = self.query_gpt4o(prompt)
            result['gpt4o_assessment'] = assessment
            
            result['success'] = True
            logger.info("Resume-job fit assessment completed successfully")
            
        except Exception as e:
            logger.error(f"Error during assessment: {str(e)}")
            result['error'] = str(e)
        
        return result
    
    def save_assessment_report(self, assessment_result: Dict[str, Any], output_path: str) -> bool:
        """
        Save the assessment results to a formatted report file.
        
        Args:
            assessment_result (Dict[str, Any]): Result from assess_resume_job_fit method
            output_path (str): Path to save the assessment report
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("RESUME-JOB PROFILE ASSESSMENT REPORT\n")
                f.write("=" * 50 + "\n\n")
                
                # Basic information
                f.write("Assessment Details:\n")
                f.write("-" * 20 + "\n")
                f.write(f"Resume File: {assessment_result['resume_path']}\n")
                f.write(f"Job Profile File: {assessment_result['job_profile_path']}\n")
                f.write(f"Assessment Status: {'SUCCESS' if assessment_result['success'] else 'FAILED'}\n\n")
                
                if not assessment_result['success']:
                    f.write(f"Error: {assessment_result.get('error', 'Unknown error')}\n")
                    return True
                
                # GPT-4o Assessment Results
                gpt_assessment = assessment_result.get('gpt4o_assessment', {})
                
                if 'overall_score' in gpt_assessment and gpt_assessment['overall_score'] is not None:
                    f.write(f"OVERALL MATCH SCORE: {gpt_assessment['overall_score']}/10\n")
                    f.write("=" * 30 + "\n\n")
                
                if 'summary' in gpt_assessment:
                    f.write("EXECUTIVE SUMMARY:\n")
                    f.write("-" * 20 + "\n")
                    f.write(f"{gpt_assessment['summary']}\n\n")
                
                # Detailed Analysis
                if 'detailed_analysis' in gpt_assessment:
                    f.write("DETAILED ANALYSIS:\n")
                    f.write("-" * 20 + "\n")
                    analysis = gpt_assessment['detailed_analysis']
                    
                    for key, value in analysis.items():
                        f.write(f"{key.replace('_', ' ').title()}: {value}\n\n")
                
                # Strengths
                if 'strengths' in gpt_assessment and gpt_assessment['strengths']:
                    f.write("CANDIDATE STRENGTHS:\n")
                    f.write("-" * 20 + "\n")
                    for i, strength in enumerate(gpt_assessment['strengths'], 1):
                        f.write(f"{i}. {strength}\n")
                    f.write("\n")
                
                # Gaps and Concerns
                if 'gaps_and_concerns' in gpt_assessment and gpt_assessment['gaps_and_concerns']:
                    f.write("GAPS AND CONCERNS:\n")
                    f.write("-" * 20 + "\n")
                    for i, concern in enumerate(gpt_assessment['gaps_and_concerns'], 1):
                        f.write(f"{i}. {concern}\n")
                    f.write("\n")
                
                # Recommendations
                if 'recommendations' in gpt_assessment:
                    f.write("RECOMMENDATIONS:\n")
                    f.write("-" * 20 + "\n")
                    recommendations = gpt_assessment['recommendations']
                    
                    if 'proceed_with_candidate' in recommendations:
                        f.write(f"Proceed with Candidate: {recommendations['proceed_with_candidate']}\n")
                    
                    if 'additional_information_needed' in recommendations:
                        f.write(f"Additional Information Needed: {recommendations['additional_information_needed']}\n")
                    
                    if 'development_areas' in recommendations and recommendations['development_areas']:
                        f.write("Development Areas:\n")
                        for i, area in enumerate(recommendations['development_areas'], 1):
                            f.write(f"  {i}. {area}\n")
                    f.write("\n")
                
                # Raw response if there was a parsing error
                if 'raw_response' in gpt_assessment:
                    f.write("RAW GPT-4o RESPONSE:\n")
                    f.write("-" * 20 + "\n")
                    f.write(f"{gpt_assessment['raw_response']}\n\n")
                
                # Resume parsing details
                if assessment_result.get('resume_parsing_result'):
                    resume_result = assessment_result['resume_parsing_result']
                    f.write("RESUME PARSING DETAILS:\n")
                    f.write("-" * 20 + "\n")
                    f.write(f"Pages: {resume_result['metadata'].get('page_count', 'Unknown')}\n")
                    f.write(f"Text Chunks: {len(resume_result['text_content'])}\n")
                    f.write(f"Tables Found: {len(resume_result['tables'])}\n\n")
            
            logger.info(f"Assessment report saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving assessment report: {str(e)}")
            return False
    
    def batch_assess_resumes(self, job_profile_path: str, resume_directory: str, output_directory: str = "assessments") -> List[Dict[str, Any]]:
        """
        Assess multiple resumes against a single job profile.
        
        Args:
            job_profile_path (str): Path to the job profile text file
            resume_directory (str): Directory containing resume PDF files
            output_directory (str): Directory to save assessment reports
            
        Returns:
            List[Dict[str, Any]]: List of assessment results
        """
        logger.info(f"Starting batch assessment of resumes in: {resume_directory}")
        
        # Create output directory
        output_dir = Path(output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all PDF files in the resume directory
        resume_dir = Path(resume_directory)
        pdf_files = list(resume_dir.glob("*.pdf")) + list(resume_dir.glob("*.PDF"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in directory: {resume_directory}")
            return []
        
        logger.info(f"Found {len(pdf_files)} PDF files to assess")
        
        results = []
        
        for pdf_file in pdf_files:
            try:
                logger.info(f"Assessing: {pdf_file.name}")
                
                # Perform assessment
                result = self.assess_resume_job_fit(str(pdf_file), job_profile_path)
                results.append(result)
                
                # Save individual report
                report_filename = f"{pdf_file.stem}_assessment.txt"
                report_path = output_dir / report_filename
                self.save_assessment_report(result, str(report_path))
                
                # Log result
                if result['success'] and result.get('gpt4o_assessment', {}).get('overall_score') is not None:
                    score = result['gpt4o_assessment']['overall_score']
                    logger.info(f"  ✅ Completed - Score: {score}/10")
                else:
                    logger.warning(f"  ❌ Failed - {result.get('error', 'Unknown error')}")
                
            except Exception as e:
                logger.error(f"Error assessing {pdf_file.name}: {str(e)}")
                results.append({
                    'success': False,
                    'resume_path': str(pdf_file),
                    'job_profile_path': job_profile_path,
                    'error': str(e)
                })
        
        # Create summary report
        self._create_batch_summary_report(results, job_profile_path, output_dir)
        
        logger.info(f"Batch assessment completed. Results saved to: {output_directory}")
        return results
    
    def _create_batch_summary_report(self, results: List[Dict[str, Any]], job_profile_path: str, output_dir: Path):
        """Create a summary report for batch assessment results."""
        try:
            summary_path = output_dir / "batch_assessment_summary.txt"
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("BATCH RESUME ASSESSMENT SUMMARY\n")
                f.write("=" * 40 + "\n\n")
                f.write(f"Job Profile: {job_profile_path}\n")
                f.write(f"Total Resumes Assessed: {len(results)}\n\n")
                
                # Sort results by score (if available)
                scored_results = []
                failed_results = []
                
                for result in results:
                    if result['success'] and result.get('gpt4o_assessment', {}).get('overall_score') is not None:
                        scored_results.append(result)
                    else:
                        failed_results.append(result)
                
                # Sort by score (descending)
                scored_results.sort(
                    key=lambda x: x['gpt4o_assessment']['overall_score'], 
                    reverse=True
                )
                
                f.write("ASSESSMENT RESULTS (RANKED BY SCORE):\n")
                f.write("-" * 30 + "\n")
                
                for i, result in enumerate(scored_results, 1):
                    score = result['gpt4o_assessment']['overall_score']
                    resume_name = Path(result['resume_path']).name
                    f.write(f"{i:2d}. {resume_name:<25} Score: {score}/10\n")
                
                if failed_results:
                    f.write(f"\nFAILED ASSESSMENTS ({len(failed_results)}):\n")
                    f.write("-" * 20 + "\n")
                    for result in failed_results:
                        resume_name = Path(result['resume_path']).name
                        error = result.get('error', 'Unknown error')
                        f.write(f"- {resume_name}: {error}\n")
                
                # Statistics
                if scored_results:
                    scores = [r['gpt4o_assessment']['overall_score'] for r in scored_results]
                    f.write(f"\nSTATISTICS:\n")
                    f.write("-" * 15 + "\n")
                    f.write(f"Average Score: {sum(scores)/len(scores):.1f}\n")
                    f.write(f"Highest Score: {max(scores)}\n")
                    f.write(f"Lowest Score: {min(scores)}\n")
                    f.write(f"Candidates with Score >= 7: {len([s for s in scores if s >= 7])}\n")
                    f.write(f"Candidates with Score >= 8: {len([s for s in scores if s >= 8])}\n")
            
            logger.info(f"Batch summary report saved to: {summary_path}")
            
        except Exception as e:
            logger.error(f"Error creating batch summary report: {str(e)}")


def main():
    """Example usage of the ResumeJobMatcher."""
    try:
        # Initialize the matcher
        matcher = ResumeJobMatcher()
        
        # Example paths (replace with actual file paths)
        resume_path = "sample_resume.pdf"
        job_profile_path = "job_profile.txt"
        
        # Check if files exist
        if not os.path.exists(resume_path):
            print(f"❌ Resume file not found: {resume_path}")
            print("Please provide a valid resume PDF file.")
            return
        
        if not os.path.exists(job_profile_path):
            print(f"❌ Job profile file not found: {job_profile_path}")
            print("Please provide a valid job profile text file.")
            return
        
        # Perform assessment
        print("🔍 Starting resume-job profile assessment...")
        result = matcher.assess_resume_job_fit(resume_path, job_profile_path)
        
        if result['success']:
            print("✅ Assessment completed successfully!")
            
            # Display key results
            assessment = result['gpt4o_assessment']
            if assessment.get('overall_score') is not None:
                print(f"📊 Overall Match Score: {assessment['overall_score']}/10")
            
            if assessment.get('summary'):
                print(f"📋 Summary: {assessment['summary']}")
            
            # Save report
            report_path = f"{Path(resume_path).stem}_assessment_report.txt"
            if matcher.save_assessment_report(result, report_path):
                print(f"💾 Detailed report saved to: {report_path}")
        
        else:
            print(f"❌ Assessment failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("Make sure you have set the OPENAI_API_KEY environment variable.")


if __name__ == "__main__":
    main()