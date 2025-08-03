#!/usr/bin/env python3
"""
Resume-Job Profile Assessment Example
=====================================

This script demonstrates how to use the ResumeJobMatcher to assess how well 
a resume matches a job profile description using GPT-4o.

Usage Examples:
--------------
1. Assess a single resume against a job profile:
   python assess_resume_example.py --resume resume.pdf --job-profile job_description.txt

2. Batch assess multiple resumes in a directory:
   python assess_resume_example.py --job-profile job_description.txt --resume-dir ./resumes/

3. Create sample files for testing:
   python assess_resume_example.py --create-samples

Requirements:
------------
- Set OPENAI_API_KEY environment variable with your OpenAI API key
- Install dependencies: pip install -r requirements.txt
"""

import os
import sys
import argparse
import json
from pathlib import Path
from resume_job_matcher import ResumeJobMatcher


def create_sample_job_profile():
    """Create a sample job profile for testing purposes."""
    job_profile_content = """
Software Engineer - Full Stack Developer

Job Description:
We are seeking a talented Full Stack Software Engineer to join our growing team. The ideal candidate will have strong experience in both front-end and back-end development, with a passion for creating scalable web applications.

Key Responsibilities:
• Design and develop robust, scalable web applications using modern frameworks
• Collaborate with cross-functional teams to define, design, and ship new features
• Write clean, maintainable code following best practices
• Participate in code reviews and provide constructive feedback
• Troubleshoot, debug and upgrade existing systems
• Stay up-to-date with emerging technologies and industry trends

Required Qualifications:
• Bachelor's degree in Computer Science, Software Engineering, or related field
• 3+ years of experience in full-stack web development
• Proficiency in JavaScript, HTML5, CSS3
• Experience with modern JavaScript frameworks (React, Vue.js, or Angular)
• Strong backend development skills with Node.js, Python, or Java
• Experience with relational databases (PostgreSQL, MySQL)
• Familiarity with version control systems (Git)
• Understanding of RESTful APIs and web services
• Experience with cloud platforms (AWS, Azure, or GCP)

Preferred Qualifications:
• Experience with TypeScript
• Knowledge of containerization technologies (Docker, Kubernetes)
• Experience with CI/CD pipelines
• Understanding of microservices architecture
• Experience with NoSQL databases (MongoDB, Redis)
• Knowledge of test-driven development (TDD)
• Experience with agile development methodologies

Technical Skills:
• Programming Languages: JavaScript, TypeScript, Python, Java
• Frontend: React, Vue.js, HTML5, CSS3, SASS/SCSS
• Backend: Node.js, Express.js, Django, Spring Boot
• Databases: PostgreSQL, MySQL, MongoDB, Redis
• Cloud: AWS (EC2, S3, RDS, Lambda), Azure, Docker
• Tools: Git, Jenkins, Docker, Kubernetes, Jest, Webpack

Company Culture:
We value innovation, collaboration, and continuous learning. Our team is passionate about technology and committed to delivering high-quality solutions. We offer competitive compensation, comprehensive benefits, and opportunities for professional growth.

Employment Type: Full-time
Location: San Francisco, CA (Hybrid work options available)
Salary Range: $120,000 - $160,000 annually
"""
    
    with open("sample_job_profile.txt", "w", encoding="utf-8") as f:
        f.write(job_profile_content)
    
    print("✅ Created sample_job_profile.txt")
    return "sample_job_profile.txt"


def create_sample_resume_content():
    """Create sample resume content for testing (would normally be a PDF)."""
    resume_content = """
JOHN DOE
Software Engineer
Email: john.doe@email.com | Phone: (555) 123-4567
LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe

PROFESSIONAL SUMMARY
Experienced Full Stack Developer with 4+ years of expertise in JavaScript, React, Node.js, and cloud technologies. 
Proven track record of building scalable web applications and leading development teams. Passionate about clean code, 
modern development practices, and emerging technologies.

TECHNICAL SKILLS
Programming Languages: JavaScript, TypeScript, Python, Java
Frontend Technologies: React, Redux, HTML5, CSS3, SASS, Bootstrap
Backend Technologies: Node.js, Express.js, Django, RESTful APIs
Databases: PostgreSQL, MongoDB, MySQL, Redis
Cloud Platforms: AWS (EC2, S3, RDS, Lambda), Docker
Tools & Technologies: Git, GitHub, Jenkins, Docker, Jest, Webpack, Kubernetes
Methodologies: Agile, Scrum, Test-Driven Development (TDD)

PROFESSIONAL EXPERIENCE

Senior Software Engineer | TechCorp Solutions | Jan 2022 - Present
• Led development of a microservices-based e-commerce platform serving 100K+ users
• Implemented React-based frontend with TypeScript, resulting in 40% improvement in code maintainability
• Designed and built RESTful APIs using Node.js and Express.js with PostgreSQL database
• Deployed applications on AWS using Docker containers and managed CI/CD pipelines with Jenkins
• Mentored 3 junior developers and conducted code reviews following best practices
• Collaborated with product managers and designers in agile development cycles

Software Engineer | StartupXYZ | Jun 2020 - Dec 2021
• Developed full-stack web applications using React, Node.js, and MongoDB
• Built responsive user interfaces with modern CSS frameworks and implemented real-time features using Socket.io
• Integrated third-party APIs and payment gateways (Stripe, PayPal)
• Optimized application performance, reducing load times by 30%
• Participated in architectural decisions and technical planning sessions
• Implemented automated testing strategies using Jest and Cypress

Junior Software Developer | WebDev Agency | Aug 2019 - May 2020
• Created custom WordPress themes and plugins for client websites
• Developed interactive frontend components using JavaScript and jQuery
• Worked with MySQL databases and PHP for backend functionality
• Collaborated with design team to implement pixel-perfect UI/UX designs
• Gained experience in client communication and project management

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley | Graduated: May 2019
Relevant Coursework: Data Structures, Algorithms, Database Systems, Software Engineering, Web Development

PROJECTS
E-Commerce Platform (Personal Project)
• Built a full-stack e-commerce application using MERN stack (MongoDB, Express.js, React, Node.js)
• Implemented user authentication, payment processing, and real-time inventory management
• Deployed on AWS with Docker containers and configured auto-scaling
• Technologies: React, Node.js, MongoDB, Redux, Stripe API, AWS, Docker

Task Management App (Open Source)
• Developed a collaborative task management application with real-time updates
• Used React hooks, Context API, and Socket.io for real-time communication
• Implemented drag-and-drop functionality and responsive design
• Technologies: React, Node.js, Socket.io, PostgreSQL, CSS3

CERTIFICATIONS
• AWS Certified Solutions Architect - Associate (2023)
• MongoDB Certified Developer (2022)
• React Developer Certification - Meta (2021)

ACHIEVEMENTS
• Led team that won "Best Innovation" award at company hackathon (2023)
• Contributed to open-source projects with 500+ GitHub stars
• Spoke at local tech meetup about "Modern React Patterns" (2022)
"""
    
    # Note: In a real scenario, this would be a PDF file
    print("ℹ️  Sample resume content created (this would normally be a PDF file)")
    print("📝 For a complete demo, you would need an actual PDF resume file")
    return resume_content


def assess_single_resume(resume_path: str, job_profile_path: str, output_dir: str = "."):
    """Assess a single resume against a job profile."""
    try:
        print(f"🔍 Assessing resume: {Path(resume_path).name}")
        print(f"📋 Job profile: {Path(job_profile_path).name}")
        print("-" * 50)
        
        # Initialize the matcher
        matcher = ResumeJobMatcher()
        
        # Perform assessment
        result = matcher.assess_resume_job_fit(resume_path, job_profile_path)
        
        if result['success']:
            assessment = result['gpt4o_assessment']
            
            print("✅ Assessment completed successfully!")
            print(f"📊 Overall Match Score: {assessment.get('overall_score', 'N/A')}/10")
            
            if assessment.get('summary'):
                print(f"\n📋 Summary:")
                print(f"   {assessment['summary']}")
            
            # Show key strengths
            if assessment.get('strengths'):
                print(f"\n💪 Top Strengths:")
                for i, strength in enumerate(assessment['strengths'][:3], 1):
                    print(f"   {i}. {strength}")
            
            # Show recommendation
            if assessment.get('recommendations', {}).get('proceed_with_candidate'):
                proceed = assessment['recommendations']['proceed_with_candidate']
                print(f"\n🎯 Recommendation: {proceed}")
            
            # Save detailed report
            output_path = Path(output_dir) / f"{Path(resume_path).stem}_assessment_report.txt"
            if matcher.save_assessment_report(result, str(output_path)):
                print(f"\n💾 Detailed report saved to: {output_path}")
            
            # Save JSON results
            json_path = Path(output_dir) / f"{Path(resume_path).stem}_assessment_results.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                # Create a JSON-serializable version
                json_result = {
                    'success': result['success'],
                    'resume_path': result['resume_path'],
                    'job_profile_path': result['job_profile_path'],
                    'gpt4o_assessment': result['gpt4o_assessment'],
                    'resume_metadata': result['resume_parsing_result']['metadata'] if result['resume_parsing_result'] else None
                }
                json.dump(json_result, f, indent=2, ensure_ascii=False)
            print(f"📄 JSON results saved to: {json_path}")
            
        else:
            print(f"❌ Assessment failed: {result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error during assessment: {str(e)}")
        if "OPENAI_API_KEY" in str(e):
            print("\n💡 Tip: Make sure to set your OpenAI API key:")
            print("   export OPENAI_API_KEY='your-api-key-here'")
        return False


def batch_assess_resumes(job_profile_path: str, resume_dir: str, output_dir: str = "assessments"):
    """Assess multiple resumes in a directory against a job profile."""
    try:
        print(f"📂 Batch assessing resumes in: {resume_dir}")
        print(f"📋 Job profile: {Path(job_profile_path).name}")
        print(f"📁 Output directory: {output_dir}")
        print("-" * 50)
        
        # Initialize the matcher
        matcher = ResumeJobMatcher()
        
        # Perform batch assessment
        results = matcher.batch_assess_resumes(job_profile_path, resume_dir, output_dir)
        
        if not results:
            print("❌ No PDF files found in the specified directory")
            return False
        
        # Display summary
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        print(f"\n📊 Batch Assessment Summary:")
        print(f"   Total files processed: {len(results)}")
        print(f"   Successful assessments: {len(successful)}")
        print(f"   Failed assessments: {len(failed)}")
        
        if successful:
            # Show top candidates
            scored_results = [r for r in successful if r.get('gpt4o_assessment', {}).get('overall_score') is not None]
            if scored_results:
                scored_results.sort(key=lambda x: x['gpt4o_assessment']['overall_score'], reverse=True)
                
                print(f"\n🏆 Top Candidates:")
                for i, result in enumerate(scored_results[:5], 1):
                    score = result['gpt4o_assessment']['overall_score']
                    name = Path(result['resume_path']).name
                    print(f"   {i}. {name:<30} Score: {score}/10")
        
        if failed:
            print(f"\n❌ Failed Assessments:")
            for result in failed:
                name = Path(result['resume_path']).name
                error = result.get('error', 'Unknown error')
                print(f"   - {name}: {error}")
        
        print(f"\n💾 All reports saved to: {output_dir}/")
        print(f"📄 Batch summary: {output_dir}/batch_assessment_summary.txt")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during batch assessment: {str(e)}")
        return False


def validate_files(resume_path: str = None, job_profile_path: str = None, resume_dir: str = None):
    """Validate that required files exist."""
    errors = []
    
    if resume_path and not Path(resume_path).exists():
        errors.append(f"Resume file not found: {resume_path}")
    
    if job_profile_path and not Path(job_profile_path).exists():
        errors.append(f"Job profile file not found: {job_profile_path}")
    
    if resume_dir and not Path(resume_dir).exists():
        errors.append(f"Resume directory not found: {resume_dir}")
    
    if resume_dir and Path(resume_dir).exists():
        pdf_files = list(Path(resume_dir).glob("*.pdf")) + list(Path(resume_dir).glob("*.PDF"))
        if not pdf_files:
            errors.append(f"No PDF files found in directory: {resume_dir}")
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        errors.append("OPENAI_API_KEY environment variable not set")
    
    return errors


def main():
    """Main function for the assessment example."""
    parser = argparse.ArgumentParser(
        description='Assess how well resumes match job profile descriptions using GPT-4o',
        epilog='''Examples:
  %(prog)s --resume resume.pdf --job-profile job_description.txt
  %(prog)s --job-profile job_description.txt --resume-dir ./resumes/
  %(prog)s --create-samples
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--resume', '-r',
        type=str,
        help='Path to a single resume PDF file'
    )
    
    parser.add_argument(
        '--job-profile', '-j',
        type=str,
        help='Path to job profile description text file'
    )
    
    parser.add_argument(
        '--resume-dir', '-d',
        type=str,
        help='Directory containing resume PDF files for batch processing'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='.',
        help='Output directory for reports (default: current directory)'
    )
    
    parser.add_argument(
        '--create-samples',
        action='store_true',
        help='Create sample job profile and resume content for testing'
    )
    
    args = parser.parse_args()
    
    # Handle sample creation
    if args.create_samples:
        print("📝 Creating sample files for testing...")
        job_profile_path = create_sample_job_profile()
        create_sample_resume_content()
        print(f"\n✅ Sample files created!")
        print(f"📋 Job profile: {job_profile_path}")
        print(f"📝 Note: You'll need an actual PDF resume file for testing")
        print(f"\n💡 To test with a real resume:")
        print(f"   python {sys.argv[0]} --resume your_resume.pdf --job-profile {job_profile_path}")
        return 0
    
    # Validate arguments
    if not args.job_profile:
        print("❌ Error: Job profile file is required")
        print("Use --job-profile to specify the job description file")
        print("Or use --create-samples to create sample files")
        return 1
    
    if not args.resume and not args.resume_dir:
        print("❌ Error: Either --resume or --resume-dir is required")
        print("Use --resume for single file assessment or --resume-dir for batch processing")
        return 1
    
    if args.resume and args.resume_dir:
        print("❌ Error: Cannot specify both --resume and --resume-dir")
        print("Use --resume for single file or --resume-dir for batch processing")
        return 1
    
    # Validate files
    validation_errors = validate_files(
        resume_path=args.resume,
        job_profile_path=args.job_profile,
        resume_dir=args.resume_dir
    )
    
    if validation_errors:
        print("❌ Validation errors:")
        for error in validation_errors:
            print(f"   - {error}")
        
        if "OPENAI_API_KEY" in str(validation_errors):
            print(f"\n💡 To set your OpenAI API key:")
            print(f"   export OPENAI_API_KEY='your-api-key-here'")
        
        return 1
    
    # Create output directory
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    # Perform assessment
    success = False
    
    if args.resume:
        # Single resume assessment
        success = assess_single_resume(args.resume, args.job_profile, args.output_dir)
    
    elif args.resume_dir:
        # Batch assessment
        success = batch_assess_resumes(args.job_profile, args.resume_dir, args.output_dir)
    
    if success:
        print(f"\n🎉 Assessment completed successfully!")
        print(f"📁 Check the output directory for detailed reports: {args.output_dir}")
        return 0
    else:
        print(f"\n❌ Assessment failed. Check the error messages above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())