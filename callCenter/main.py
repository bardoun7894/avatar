#!/usr/bin/env python3
"""
Call Center Application Entry Point
Runs the FastAPI backend server with WebSocket support
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    try:
        import uvicorn
        from callCenter.api import app

        logger.info("Starting Call Center API Server...")
        logger.info("Server will be available at http://localhost:8000")
        logger.info("API documentation at http://localhost:8000/docs")
        logger.info("WebSocket endpoint at ws://localhost:8000/ws/updates")

        # Run the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )

    except ImportError as e:
        logger.error(f"Missing dependency: {str(e)}")
        logger.info("Install dependencies with: pip install fastapi uvicorn python-multipart")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
