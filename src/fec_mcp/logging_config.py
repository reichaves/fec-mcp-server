
import logging
import sys
import os

def setup_logging(level=logging.INFO):
    """Configure logging for the application"""
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, "fec_mcp.log")
    
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )
    
    # Quiet down httpx
    logging.getLogger("httpx").setLevel(logging.WARNING)

def get_logger(name):
    """Get a logger instance"""
    return logging.getLogger(name)
