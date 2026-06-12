#!/usr/bin/env python3
"""
Database Creation Script for Aura-Commerce-AI (Xecomerce).
Creates the MySQL database and initializes the schema, including tables, indexes, and triggers.

Requirements:
- Python 3.13
- PyMySQL
- python-dotenv
"""

import os
import sys
import logging
from pathlib import Path
from typing import List

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

# Configure logging with premium aesthetics via standard logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("database_setup.log", mode="w", encoding="utf-8")
    ]
)
logger = logging.getLogger("CreateDatabase")

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
SQL_PATH = BASE_DIR / "database" / "ecommerce.sql"

# Load environment variables
if ENV_PATH.exists():
    load_dotenv(dotenv_path=str(ENV_PATH))
else:
    logger.warning(f".env file not found at {ENV_PATH}. Falling back to default environment variables.")


def get_db_connection(select_db: bool = True) -> pymysql.Connection:
    """
    Establishes connection to the MySQL database server.
    """
    host = os.getenv("MYSQL_HOST", "localhost")
    port = int(os.getenv("MYSQL_PORT", "3306"))
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    db_name = os.getenv("MYSQL_DATABASE", "xecomerce")

    try:
        if select_db:
            return pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=db_name,
                cursorclass=DictCursor,
                autocommit=True
            )
        else:
            return pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                cursorclass=DictCursor,
                autocommit=True
            )
    except Exception as e:
        logger.error(f"Failed to connect to MySQL server (host={host}, user={user}): {e}")
        raise


def parse_sql_file(file_path: Path) -> List[str]:
    """
    Parses a SQL schema file, handling DELIMITER modifications for triggers.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"SQL file not found at {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    statements = []
    current_statement = []
    delimiter = ";"
    
    # Split content by line to process delimiters
    lines = content.splitlines()
    
    for line in lines:
        stripped = line.strip()
        
        # Skip comments and empty lines
        if not stripped or stripped.startswith("--") or stripped.startswith("#"):
            continue
            
        # Check if delimiter is redefined
        if stripped.lower().startswith("delimiter"):
            parts = stripped.split()
            if len(parts) >= 2:
                delimiter = parts[1]
            continue
            
        current_statement.append(line)
        
        # Check if the current line ends with the active delimiter
        if stripped.endswith(delimiter):
            # Reconstruct statement
            stmt = "\n".join(current_statement).strip()
            # Remove the delimiter string from the execution statement
            if stmt.endswith(delimiter):
                stmt = stmt[:-len(delimiter)].strip()
            if stmt:
                statements.append(stmt)
            current_statement = []
            
    return statements


def create_database() -> None:
    """
    Automatically creates the target MySQL database and tables from ecommerce.sql.
    """
    db_name = os.getenv("MYSQL_DATABASE", "xecomerce")
    logger.info("Starting database initialization...")

    # 1. Connect to server (without DB selected) and create database
    try:
        conn = get_db_connection(select_db=False)
        with conn.cursor() as cursor:
            logger.info(f"Creating database '{db_name}' if it does not exist...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;")
        conn.close()
    except Exception as e:
        logger.error("Database creation step failed. Exiting.")
        sys.exit(1)

    # 2. Connect to the database and run the schema script
    try:
        conn = get_db_connection(select_db=True)
        logger.info(f"Connected to database '{db_name}'. Parsing schema file {SQL_PATH}...")
        statements = parse_sql_file(SQL_PATH)
        logger.info(f"Found {len(statements)} SQL statements to execute.")

        with conn.cursor() as cursor:
            for idx, stmt in enumerate(statements, 1):
                # Print progress
                first_line = stmt.splitlines()[0] if stmt.splitlines() else ""
                logger.info(f"Executing statement {idx}/{len(statements)}: {first_line[:50]}...")
                try:
                    cursor.execute(stmt)
                except Exception as stmt_err:
                    logger.error(f"Error executing statement {idx}: {stmt_err}")
                    logger.error(f"SQL statement detail:\n{stmt}")
                    raise stmt_err

        logger.info("Schema execution completed successfully.")
        conn.close()
    except Exception as e:
        logger.error(f"Database schema initialization failed: {e}")
        sys.exit(1)

    # 3. Verify that tables are created
    verify_tables()


def verify_tables() -> None:
    """
    Verifies that all 15 required tables have been successfully created.
    """
    required_tables = {
        "categories", "products", "users", "carts", "cart_items",
        "wishlist", "orders", "order_items", "reviews", "ratings",
        "user_activity", "chatbot_logs", "recommendations_logs",
        "model_predictions", "search_history"
    }

    logger.info("Verifying tables...")
    try:
        conn = get_db_connection(select_db=True)
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            tables_in_db = {list(row.values())[0] for row in cursor.fetchall()}

        missing_tables = required_tables - tables_in_db
        found_tables = required_tables & tables_in_db

        logger.info(f"Verification results: Found {len(found_tables)}/{len(required_tables)} target tables.")
        
        for table in sorted(found_tables):
            logger.info(f"  [OK] Table '{table}' verified.")
            
        if missing_tables:
            logger.error(f"  [ERROR] Missing tables: {missing_tables}")
            sys.exit(1)
        else:
            logger.info("  [SUCCESS] All 15 database tables successfully created and verified!")
            
        conn.close()
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_database()
