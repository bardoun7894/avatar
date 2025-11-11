#!/usr/bin/env python3
"""
Entry point for Call Center FastAPI application
Runs with uvicorn - FastAPI will handle all routing
"""

import uvicorn

# In Docker, uvicorn loads the API module which handles all imports
if __name__ == "__main__":
    # Run the FastAPI app from api.py
    # The app variable in api.py is the FastAPI instance
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    )
