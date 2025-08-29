#!/usr/bin/env python3
"""
Portfolio Setup for Resume Curator

This script configures your project for portfolio deployment using:
- GitHub Pages (Frontend) - FREE
- Render (Backend) - FREE
"""

import os
import sys

def update_github_username():
    """Update configuration with your GitHub username."""
    username = input("Enter your GitHub username: ").strip()
    
    if not username:
        print("❌ GitHub username is required!")
        return None
    
    # Update CORS origins
    cors_origins = f'["https://{username}.github.io", "https://resume-curator-api.onrender.com"]'
    
    env_files = ['backend/.env', 'backend/.env.production']
    
    for env_file in env_files:
        if not os.path.exists(env_file):
            continue
            
        try:
            with open(env_file, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('CORS_ORIGINS='):
                    lines[i] = f'CORS_ORIGINS={cors_origins}'
                    break
            
            with open(env_file, 'w') as f:
                f.write('\n'.join(lines))
            
            print(f"✅ Updated CORS in {env_file}")
            
        except Exception as e:
            print(f"❌ Error updating {env_file}: {e}")
    
    return username

def create_portfolio_readme():
    """Create a portfolio-focused README section."""
    readme_addition = """

## 🎯 Portfolio Project

This is a portfolio project showcasing full-stack development skills for job applications.

### 🚀 Live Demo
- **Frontend**: https://yourusername.github.io/resume-curator
- **Backend API**: https://resume-curator-api.onrender.com
- **Source Code**: https://github.com/yourusername/resume-curator

### 💼 Skills Demonstrated
- **Frontend**: React, Vite, Tailwind CSS, Responsive Design
- **Backend**: FastAPI, Python, RESTful APIs
- **Database**: SQLite/PostgreSQL, Data Modeling
- **AI Integration**: AtlasCloud API, Natural Language Processing
- **DevOps**: GitHub Actions, CI/CD, Deployment
- **Tools**: Git, npm, pip, Environment Management

### 🎨 Features for Recruiters
- Upload resume files (PDF, DOC, DOCX)
- AI-powered resume analysis and feedback
- Job description matching and scoring
- Responsive design for all devices
- Professional UI/UX design

### 🔧 Technical Highlights
- Clean, maintainable code architecture
- Proper error handling and validation
- Automated testing and deployment
- Security best practices
- Modern development workflow

---

*This project was built to demonstrate my capabilities as a full-stack developer and my ability to integrate modern AI services into web applications.*
"""
    
    try:
        with open('README.md', 'a') as f:
            f.write(readme_addition)
        print("✅ Added portfolio section to README.md")
    except Exception as e:
        print(f"❌ Error updating README: {e}")

def main():
    """Main setup function."""
    print("🎓 Resume Curator - Portfolio Setup")
    print("=" * 50)
    print("Setting up your project for portfolio deployment...")
    print()
    
    # Get GitHub username
    username = update_github_username()
    if not username:
        return 1
    
    # Add portfolio section to README
    create_portfolio_readme()
    
    print(f"\n🎉 Portfolio setup complete!")
    print(f"\n📝 Next steps:")
    print(f"1. Push your code to GitHub")
    print(f"2. Enable GitHub Pages in repository settings")
    print(f"3. Deploy backend to Render.com")
    print(f"4. Your portfolio will be live at:")
    print(f"   https://{username}.github.io/resume-curator")
    
    print(f"\n💼 Add to your resume:")
    print(f"Resume Curator - AI-Powered Resume Analysis Tool")
    print(f"Live Demo: https://{username}.github.io/resume-curator")
    print(f"Source: https://github.com/{username}/resume-curator")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)