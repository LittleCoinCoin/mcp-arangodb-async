"""CLI utilities for admin commands.

This module provides shared utilities for CLI commands including:
- Credential loading from environment files
- Result reporting with color-coded output
- Confirmation prompts with dry-run support
- Database connection utilities
- Exit code constants

Functions:
- load_credentials() - Load credentials from env file or environment
- confirm_action() - Interactive confirmation with --yes bypass
- get_system_db() - Connect to _system database with warning suppression
- ResultReporter - Color-coded result reporting class
"""

from __future__ import annotations

import logging
import os
import sys
import warnings
from typing import Optional, Dict, Any
from argparse import Namespace
from enum import Enum

from arango import ArangoClient
from arango.database import StandardDatabase
from arango.exceptions import ArangoError

# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_CANCELLED = 2

# ANSI color codes
class Color(Enum):
    """ANSI color codes for terminal output."""
    GREEN = "\033[92m"
    GREEN_DIM = "\033[32m"
    RED = "\033[91m"
    RED_DIM = "\033[31m"
    YELLOW = "\033[93m"
    YELLOW_DIM = "\033[33m"
    GRAY = "\033[90m"
    RESET = "\033[0m"


class ConsequenceType(Enum):
    """Consequence types for result reporting."""
    ADD = ("ADD", Color.GREEN_DIM, Color.GREEN)
    ADDED = ("ADDED", Color.GREEN_DIM, Color.GREEN)
    CREATE = ("CREATE", Color.GREEN_DIM, Color.GREEN)
    CREATED = ("CREATED", Color.GREEN_DIM, Color.GREEN)
    GRANT = ("GRANT", Color.GREEN_DIM, Color.GREEN)
    GRANTED = ("GRANTED", Color.GREEN_DIM, Color.GREEN)
    REMOVE = ("REMOVE", Color.RED_DIM, Color.RED)
    REMOVED = ("REMOVED", Color.RED_DIM, Color.RED)
    REVOKE = ("REVOKE", Color.RED_DIM, Color.RED)
    REVOKED = ("REVOKED", Color.RED_DIM, Color.RED)
    UPDATE = ("UPDATE", Color.YELLOW_DIM, Color.YELLOW)
    UPDATED = ("UPDATED", Color.YELLOW_DIM, Color.YELLOW)
    
    def __init__(self, label: str, prompt_color: Color, result_color: Color):
        self.label = label
        self.prompt_color = prompt_color
        self.result_color = result_color


def load_credentials(args: Namespace) -> Dict[str, Any]:
    """Load credentials from environment file or environment variables.
    
    Args:
        args: Parsed command-line arguments with optional env_file,
              arango_root_password_env, arango_password_env attributes
    
    Returns:
        Dictionary with credentials:
        - root_password: Root password for admin operations
        - user_password: User password for self-service operations
        - url: ArangoDB server URL
        - username: Username for self-service operations
    """
    # Load from dotenv file if specified
    if hasattr(args, 'env_file') and args.env_file:
        try:
            from dotenv import load_dotenv
            load_dotenv(args.env_file)
        except ImportError:
            print("Warning: python-dotenv not installed, skipping .env file", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Failed to load .env file: {e}", file=sys.stderr)
    
    # Determine variable names (use overrides or defaults)
    root_pw_var = getattr(args, 'arango_root_password_env', None) or "ARANGO_ROOT_PASSWORD"
    user_pw_var = getattr(args, 'arango_password_env', None) or "ARANGO_PASSWORD"
    
    # Retrieve values from environment
    return {
        "root_password": os.getenv(root_pw_var),
        "user_password": os.getenv(user_pw_var),
        "url": os.getenv("ARANGO_URL", "http://localhost:8529"),
        "username": os.getenv("ARANGO_USERNAME", "root"),
    }


def get_system_db(credentials: dict) -> Optional[StandardDatabase]:
    """Connect to _system database as root for admin operations.

    Suppresses urllib3 connection warnings for cleaner error output.

    Args:
        credentials: Dictionary with 'url' and 'root_password' keys

    Returns:
        StandardDatabase instance for _system database, or None on error
    """
    # Suppress urllib3 retry warnings for cleaner output
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)

    # Also suppress urllib3 InsecureRequestWarning and other warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=Warning, module="urllib3")

        try:
            client = ArangoClient(hosts=credentials["url"])
            sys_db = client.db("_system", username="root", password=credentials["root_password"])
            # Validate connection
            _ = sys_db.version()
            return sys_db
        except ArangoError as e:
            print(f"Error: Failed to connect to ArangoDB: {e}", file=sys.stderr)
            return None
        except Exception as e:
            # Handle connection refused, timeout, etc.
            error_msg = str(e)
            if "Connection refused" in error_msg or "NewConnectionError" in error_msg:
                print(f"Error: Cannot connect to ArangoDB at {credentials.get('url', 'unknown')}", file=sys.stderr)
                print("Hint: Is the ArangoDB server running?", file=sys.stderr)
            elif "timeout" in error_msg.lower():
                print(f"Error: Connection to ArangoDB timed out", file=sys.stderr)
            else:
                print(f"Error: Unexpected error connecting to ArangoDB: {e}", file=sys.stderr)
            return None


def confirm_action(message: str, args: Namespace) -> bool:
    """Prompt user for confirmation unless --yes flag is set.
    
    Args:
        message: Confirmation message to display
        args: Parsed arguments with optional 'yes' attribute
    
    Returns:
        True if user confirms or --yes flag is set, False otherwise
    """
    # Check --yes flag
    if hasattr(args, 'yes') and args.yes:
        return True
    
    # Check environment variable
    if os.getenv("MCP_ARANGODB_ASYNC_CLI_YES") == "1":
        return True
    
    # Interactive prompt
    try:
        response = input(f"{message} [y/N]: ").strip().lower()
        return response in ('y', 'yes')
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled", file=sys.stderr)
        return False


class ResultReporter:
    """Color-coded result reporter for CLI commands."""
    
    def __init__(self, command_name: str, dry_run: bool = False):
        """Initialize result reporter.
        
        Args:
            command_name: Name of the command (e.g., "db add")
            dry_run: Whether this is a dry-run operation
        """
        self.command_name = command_name
        self.dry_run = dry_run
        self.consequences = []
    
    def add(self, consequence_type: ConsequenceType, message: str):
        """Add a consequence to report.

        Args:
            consequence_type: Type of consequence (ADD, REMOVE, etc.)
            message: Description of the consequence
        """
        self.consequences.append((consequence_type, message))

    def report_prompt(self) -> str:
        """Generate confirmation prompt with present-tense consequences.

        Returns:
            Formatted prompt string with color-coded consequences
        """
        if not self.consequences:
            return ""

        lines = ["The following actions will be performed:"]
        for consequence_type, message in self.consequences:
            color = consequence_type.prompt_color.value
            reset = Color.RESET.value
            lines.append(f"  {color}[{consequence_type.label}]{reset} {message}")

        return "\n".join(lines)

    def report_result(self):
        """Print execution results with past-tense consequences."""
        if not self.consequences:
            return

        # Print header
        suffix = " (dry-run)" if self.dry_run else ""
        print(f"{self.command_name}{suffix}:")

        # Print consequences
        for consequence_type, message in self.consequences:
            if self.dry_run:
                # Dry-run: use result color + gray suffix
                color = consequence_type.result_color.value
                gray = Color.GRAY.value
                reset = Color.RESET.value
                print(f"{color}[{consequence_type.label} - DRY-RUN]{reset} {message}")
            else:
                # Actual execution: use bright result color
                color = consequence_type.result_color.value
                reset = Color.RESET.value
                print(f"{color}[{consequence_type.label}]{reset} {message}")

        # Print dry-run footer
        if self.dry_run:
            print(f"\n{Color.GRAY.value}No changes made. Remove --dry-run to execute.{Color.RESET.value}")

    def has_consequences(self) -> bool:
        """Check if any consequences have been added.

        Returns:
            True if consequences exist, False otherwise
        """
        return len(self.consequences) > 0

