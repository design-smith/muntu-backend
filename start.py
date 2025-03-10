import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        # Log the current directory and its contents
        logger.info(f"Current directory: {os.getcwd()}")
        logger.info("Directory contents:")
        for file in os.listdir():
            logger.info(f"- {file}")
            
        # Also log the contents of the app directory
        logger.info("App directory contents:")
        for file in os.listdir('app'):
            logger.info(f"- {file}")
        
        # Add the app directory to Python path
        sys.path.append(os.path.join(os.getcwd(), 'app'))
        
        # Import uvicorn here to catch import errors
        import uvicorn
        
        # Get the port number
        port = int(os.getenv("PORT", 8000))
        logger.info(f"Starting server on port {port}")
        
        # Try to run the server with the correct path
        uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1) 