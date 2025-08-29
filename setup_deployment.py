#!/usr/bin/env python3
"""
Deployment Setup Helper for Resume Curator

This script helps configure your deployment settings for Vercel + Railway.
Run this after you get your deployment URLs.
"""

import os
import sys
from pathlib import Path

def update_cors_origins(backend_url, frontend_url):
    """Update CORS origins in backend environment files."""
    cors_origins = f'["https://{frontend_url}", "https://www.{frontend_url}", "https://{backend_url}"]'
    
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

def update_frontend_api_url(backend_url):
    """Update frontend API URL."""
    api_url = f"https://{backend_url}/api"
    
    env_file = 'frontend/.env.production'
    
    if not os.path.exists(env_file):
        print(f"⚠️  File not found: {env_file}")
        return
    
    try:
        with open(env_file, 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('VITE_API_URL='):
                lines[i] = f'VITE_API_URL={api_url}'
                break
        
        with open(env_file, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ Updated API URL in {env_file}")
        
    except Exception as e:
        print(f"❌ Error updating {env_file}: {e}")

def main():
    """Main setup function."""
    print("🚀 Resume Curator Deployment Setup")
    print("=" * 50)
    
    print("\nAfter deploying to Railway and Vercel, you'll get URLs like:")
    print("Backend (Railway): your-app-name.railway.app")
    print("Frontend (Vercel): your-app-name.vercel.app")
    print()
    
    # Get deployment URLs
    backend_url = input("Enter your Railway backend URL (without https://): ").strip()
    frontend_url = input("Enter your Vercel frontend URL (without https://): ").strip()
    
    if not backend_url or not frontend_url:
        print("❌ Both URLs are required!")
        return 1
    
    print(f"\n🔧 Configuring for:")
    print(f"   Backend: https://{backend_url}")
    print(f"   Frontend: https://{frontend_url}")
    
    # Update configuration files
    update_cors_origins(backend_url, frontend_url)
    update_frontend_api_url(backend_url)
    
    print("\n✅ Configuration updated!")
    print("\n📝 Next steps:")
    print("1. Commit and push these changes to GitHub")
    print("2. Both Vercel and Railway will auto-deploy")
    print("3. Test your deployed application")
    
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