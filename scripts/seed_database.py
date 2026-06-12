#!/usr/bin/env python3
"""
Database Seeding Script for Aura-Commerce-AI (Xecomerce).
Executes database/seed_data.sql and prints a seeding validation report showing rows in each table.

Requirements:
- Python 3.13
- PyMySQL
- python-dotenv
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict

# Import python-dotenv to read .env
try:
    from dotenv import load_dotenv
except ImportError:
    print("Warning: python-dotenv not found. Standard environment variables will be used.")
    def load_dotenv(): pass

# Import PyMySQL for database connection
try:
    import pymysql
    from pymysql.cursors import DictCursor
except ImportError:
    print("Error: PyMySQL is required to run this script. Please run 'pip install pymysql' first.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("database_seeding.log", mode="w", encoding="utf-8")
    ]
)
logger = logging.getLogger("SeedDatabase")

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
SQL_PATH = BASE_DIR / "database" / "seed_data.sql"

# Load environment variables
if ENV_PATH.exists():
    load_dotenv(dotenv_path=str(ENV_PATH))


def get_db_connection() -> pymysql.Connection:
    """
    Establishes connection to the MySQL database.
    """
    host = os.getenv("MYSQL_HOST", "localhost")
    port = int(os.getenv("MYSQL_PORT", "3306"))
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    db_name = os.getenv("MYSQL_DATABASE", "xecomerce")

    try:
        return pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name,
            cursorclass=DictCursor,
            autocommit=True
        )
    except Exception as e:
        logger.error(f"Failed to connect to MySQL database '{db_name}': {e}")
        raise


def parse_sql_file(file_path: Path) -> List[str]:
    """
    Parses a SQL script file into separate statements.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"SQL file not found at {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    statements = []
    current_statement = []
    delimiter = ";"
    
    lines = content.splitlines()
    for line in lines:
        stripped = line.strip()
        
        # Skip comments and empty lines
        if not stripped or stripped.startswith("--") or stripped.startswith("#"):
            continue
            
        if stripped.lower().startswith("delimiter"):
            parts = stripped.split()
            if len(parts) >= 2:
                delimiter = parts[1]
            continue
            
        current_statement.append(line)
        
        if stripped.endswith(delimiter):
            stmt = "\n".join(current_statement).strip()
            if stmt.endswith(delimiter):
                stmt = stmt[:-len(delimiter)].strip()
            if stmt:
                statements.append(stmt)
            current_statement = []
            
    return statements


def seed_database() -> None:
    """
    Executes seed_data.sql and prints the seeding report.
    """
    logger.info("Starting database seeding...")
    
    if not SQL_PATH.exists():
        logger.error(f"Seed SQL file not found at {SQL_PATH}")
        sys.exit(1)

    try:
        conn = get_db_connection()
        statements = parse_sql_file(SQL_PATH)
        logger.info(f"Loaded {len(statements)} SQL statements from {SQL_PATH.name}")

        with conn.cursor() as cursor:
            # Disable foreign key checks temporarily during seeding if needed
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            
            for idx, stmt in enumerate(statements, 1):
                first_line = stmt.splitlines()[0] if stmt.splitlines() else ""
                logger.info(f"Executing statement {idx}/{len(statements)}: {first_line[:50]}...")
                try:
                    cursor.execute(stmt)
                except Exception as stmt_err:
                    logger.error(f"Error executing statement {idx}: {stmt_err}")
                    raise stmt_err
            
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

        logger.info("Seed data execution completed successfully.")
        conn.close()
    except Exception as e:
        logger.error(f"Seeding database failed: {e}")
        sys.exit(1)

    # Verify rows and generate report
    generate_seeding_report()


def generate_seeding_report() -> None:
    """
    Counts rows in each table and displays a professional report.
    """
    tables = [
        "categories", "products", "users", "carts", "cart_items",
        "wishlist", "orders", "order_items", "reviews", "ratings",
        "user_activity", "chatbot_logs", "recommendations_logs",
        "model_predictions", "search_history"
    ]

    report_data: Dict[str, int] = {}
    logger.info("Generating Seeding Validation Report...")

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM `{table}`;")
                result = cursor.fetchone()
                count = result["count"] if result else 0
                report_data[table] = count
        conn.close()
        
        # Display report in log
        logger.info("=========================================")
        logger.info("       DATABASE SEEDING STATISTICS       ")
        logger.info("=========================================")
        total_seeded = 0
        for table, count in report_data.items():
            status = "SUCCESS" if count > 0 else "EMPTY  "
            logger.info(f"  Table: {table:<22} | Rows: {count:<4} | Status: {status}")
            total_seeded += count
        logger.info("=========================================")
        
        if total_seeded == 0:
            logger.warning("Warning: Seeding completed but 0 total rows were inserted across all tables.")
        else:
            logger.info("Database seeding verification completed successfully!")
            
    except Exception as e:
        logger.error(f"Failed to generate seeding report: {e}")
        sys.exit(1)


if __name__ == "__main__":
    seed_database()
