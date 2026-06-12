# logging_utils.py

import os
import json
import logging
from pathlib import Path

# Base dir is workspace root: d:\PROJECTS\Xecomerce
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MONITORING_DIR = BASE_DIR / "monitoring"

# Ensure monitoring directory exists
MONITORING_DIR.mkdir(parents=True, exist_ok=True)

def setup_logger(name: str, log_file: Path) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.FileHandler(log_file, encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        # Prevent logs from bubbling up to root console logger unnecessarily
        logger.propagate = False
    return logger

# Configure specific log files
router_logger = setup_logger("router_logger", MONITORING_DIR / "router_logs.log")
retrieval_logger = setup_logger("retrieval_logger", MONITORING_DIR / "retrieval_logs.log")
chatbot_logger = setup_logger("chatbot_logger", MONITORING_DIR / "chatbot_logs.log")

def log_router(query: str, dataset_selected: str, search_time: float):
    """Logs routing query details, selected dataset, and time taken."""
    log_data = {
        "query": query,
        "dataset_selected": dataset_selected,
        "search_time_seconds": round(search_time, 4)
    }
    router_logger.info(json.dumps(log_data))

def log_retrieval(query: str, dataset: str, retrieval_time: float, num_results: int):
    """Logs retrieval query details, dataset name, retrieval time, and results count."""
    log_data = {
        "query": query,
        "dataset": dataset,
        "retrieval_time_seconds": round(retrieval_time, 4),
        "num_results": num_results
    }
    retrieval_logger.info(json.dumps(log_data))

def log_chatbot(query: str, dataset: str, recommendation_time: float, source: str):
    """Logs chatbot query details, selected dataset, response generation/recommendation time, and LLM source."""
    log_data = {
        "query": query,
        "dataset": dataset,
        "recommendation_time_seconds": round(recommendation_time, 4),
        "source": source
    }
    chatbot_logger.info(json.dumps(log_data))
