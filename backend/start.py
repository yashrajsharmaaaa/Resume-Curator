#!/usr/bin/env python3
"""
Render-specific startup script for Resume Curator API
"""

import os
import uvicorn

if __name__ == "__main__":
    # Render provides PORT environment variable
    port = int(os.getenv("PORT", 10000))
    host = "0.0.0.0"
    
    print(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,  # Never reload in production
        log_level="info"
    )