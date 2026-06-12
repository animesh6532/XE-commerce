#!/usr/bin/env python3
"""
Model Training Orchestrator Script for Aura-Commerce-AI (Xecomerce).
Automatically runs the training pipelines for all 5 machine learning models:
1. Recommendation Model
2. Sentiment Model
3. Fake Review Model
4. Demand Forecast Model
5. Price Prediction Model

It handles working directory paths, writes logs, handles exceptions, and presents a visual dashboard.

Requirements:
- Python 3.13
- rich
"""

import os
import sys
import time
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, List

# Try importing rich for premium CLI styling
try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.live import Live
    from rich import print as rprint
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("train_all_models.log", mode="w", encoding="utf-8")
    ]
)
logger = logging.getLogger("TrainAllModels")

BASE_DIR = Path(__file__).resolve().parent.parent

# Define the models to train
MODELS_TO_TRAIN = [
    {
        "name": "Recommendation Model",
        "script_path": "ml_models/recommendation/train_recommendation.py",
        "description": "Content-based product similarity matching"
    },
    {
        "name": "Sentiment Model",
        "script_path": "ml_models/sentiment/train_sentiment.py",
        "description": "Review sentiment classification (Logistic Regression)"
    },
    {
        "name": "Fake Review Model",
        "script_path": "ml_models/fake_review/train_fake_review.py",
        "description": "Fake review detection (TF-IDF + Logistic Regression)"
    },
    {
        "name": "Demand Forecast Model",
        "script_path": "ml_models/demand_forecasting/train_demand_model.py",
        "description": "Time-series daily order forecasting (Random Forest)"
    },
    {
        "name": "Price Prediction Model",
        "script_path": "ml_models/price_prediction/train_price_model.py",
        "description": "Original price predictor based on discount rates and ratings"
    }
]


def run_training_script(script_relative_path: str) -> Dict[str, Any]:
    """
    Executes a model training script as a subprocess in its native directory.
    """
    script_full_path = BASE_DIR / script_relative_path
    script_dir = script_full_path.parent
    script_name = script_full_path.name
    
    result = {
        "success": False,
        "duration": 0.0,
        "error_message": "",
        "output": ""
    }

    if not script_full_path.exists():
        msg = f"Script not found at {script_full_path}"
        logger.error(msg)
        result["error_message"] = msg
        return result

    start_time = time.time()
    logger.info(f"Starting execution of {script_relative_path} in {script_dir}...")
    
    try:
        # Set environment variables to force UTF-8 output
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        
        # Run python script as subprocess. Use sys.executable to ensure same python environment.
        process = subprocess.run(
            [sys.executable, script_name],
            cwd=str(script_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=600 # 10 minute timeout per script
        )
        
        result["duration"] = time.time() - start_time
        result["output"] = process.stdout
        
        # Log outputs
        with open("train_all_models.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"\n=========================================\n")
            log_file.write(f"SCRIPT: {script_relative_path}\n")
            log_file.write(f"TIME: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file.write(f"DURATION: {result['duration']:.2f} seconds\n")
            log_file.write(f"RETURN CODE: {process.returncode}\n")
            log_file.write(f"=========================================\n")
            log_file.write("--- STDOUT ---\n")
            log_file.write(process.stdout)
            log_file.write("--- STDERR ---\n")
            log_file.write(process.stderr)
            
        if process.returncode == 0:
            logger.info(f"Successfully completed training for {script_relative_path} in {result['duration']:.2f}s")
            result["success"] = True
        else:
            logger.error(f"Script {script_relative_path} exited with code {process.returncode}")
            result["error_message"] = process.stderr.strip().splitlines()[-1] if process.stderr.strip() else "Unknown failure"
            
    except subprocess.TimeoutExpired as te:
        result["duration"] = time.time() - start_time
        msg = f"Script execution timed out after 10 minutes: {te}"
        logger.error(msg)
        result["error_message"] = "Timeout"
    except Exception as e:
        result["duration"] = time.time() - start_time
        msg = f"Failed to run script {script_relative_path}: {e}"
        logger.error(msg)
        result["error_message"] = str(e)

    return result


def print_rich_dashboard(results: List[Dict[str, Any]], current_idx: int = -1) -> None:
    """
    Renders a premium CLI dashboard using rich table formatting.
    """
    console = Console()
    console.clear()
    
    console.print("[bold purple]Aura-Commerce-AI (Xecomerce) - ML Training Orchestrator[/bold purple]\n")
    
    table = Table(title="Model Training Progress and Status", show_header=True, header_style="bold cyan")
    table.add_column("Model Name", style="bold white", width=25)
    table.add_column("Status", width=12)
    table.add_column("Duration (s)", justify="right", width=15)
    table.add_column("Details / Error Summary", style="dim", width=40)
    
    for idx, model in enumerate(MODELS_TO_TRAIN):
        status_text = ""
        duration_text = "-"
        details = model["description"]
        
        if idx < len(results):
            res = results[idx]
            if res["success"]:
                status_text = "[green]Success[/green]"
                duration_text = f"{res['duration']:.2f}s"
            else:
                status_text = "[red]Failed[/red]"
                duration_text = f"{res['duration']:.2f}s"
                details = f"[red]Error: {res['error_message']}[/red]"
        elif idx == current_idx:
            status_text = "[yellow]Running...[/yellow]"
            duration_text = "-"
        else:
            status_text = "[dim]Queued[/dim]"
            duration_text = "-"
            
        table.add_row(model["name"], status_text, duration_text, details)
        
    console.print(table)
    console.print("\n[dim]Detailed logs are written to: train_all_models.log[/dim]")


def print_basic_dashboard(results: List[Dict[str, Any]], current_idx: int = -1) -> None:
    """
    Standard console output fallback if rich is not installed.
    """
    print("\n" + "=" * 80)
    print("      AURA-COMMERCE-AI ML TRAINING ORCHESTRATOR STATUS")
    print("=" * 80)
    
    for idx, model in enumerate(MODELS_TO_TRAIN):
        status = "QUEUED"
        duration = "-"
        details = model["description"]
        
        if idx < len(results):
            res = results[idx]
            status = "SUCCESS" if res["success"] else "FAILED"
            duration = f"{res['duration']:.2f}s"
            if not res["success"]:
                details = f"Error: {res['error_message']}"
        elif idx == current_idx:
            status = "RUNNING"
            
        print(f"[{status:<7}] {model['name']:<25} | Duration: {duration:<8} | {details}")
        
    print("=" * 80)
    print("Detailed logs are written to: train_all_models.log")


def main() -> None:
    """
    Orchestrates the sequential model training process.
    """
    results = []
    
    logger.info("Initializing ML training run for all models...")
    print("Starting Model Training Orchestrator. Please wait...")
    
    if HAS_RICH:
        print_rich_dashboard(results, current_idx=0)
    else:
        print_basic_dashboard(results, current_idx=0)
        
    for idx, model in enumerate(MODELS_TO_TRAIN):
        logger.info(f"Training {model['name']}...")
        
        # Update dashboard to show current is running
        if HAS_RICH:
            print_rich_dashboard(results, current_idx=idx)
        else:
            print_basic_dashboard(results, current_idx=idx)
            
        # Run script
        res = run_training_script(model["script_path"])
        results.append(res)
        
    # Final dashboard update
    if HAS_RICH:
        print_rich_dashboard(results)
    else:
        print_basic_dashboard(results)
        
    # Check if there were any failures
    failures = [m["name"] for i, m in enumerate(MODELS_TO_TRAIN) if not results[i]["success"]]
    if failures:
        print(f"\n[WARNING] Training completed with failures in: {', '.join(failures)}")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All 5 models trained successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
