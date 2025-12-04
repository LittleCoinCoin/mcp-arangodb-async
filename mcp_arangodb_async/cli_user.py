"""CLI commands for ArangoDB user management.

This module provides CLI commands for managing ArangoDB users and permissions.
Includes both admin operations (require root) and self-service operations.

Functions:
- handle_user_add() - Create ArangoDB user (admin)
- handle_user_remove() - Delete ArangoDB user (admin)
- handle_user_list() - List ArangoDB users (admin)
- handle_user_grant() - Grant database permissions (admin)
- handle_user_revoke() - Revoke database permissions (admin)
- handle_user_databases() - List accessible databases (self-service)
- handle_user_password() - Change own password (self-service)
"""

from __future__ import annotations

import sys
import json
import os
from typing import Optional
from argparse import Namespace
from arango import ArangoClient
from arango.database import StandardDatabase
from arango.exceptions import ArangoError

from .cli_utils import (
    load_credentials,
    confirm_action,
    ResultReporter,
    ConsequenceType,
    EXIT_SUCCESS,
    EXIT_ERROR,
    EXIT_CANCELLED,
)


def _get_system_db(credentials: dict) -> Optional[StandardDatabase]:
    """Connect to _system database as root for admin operations.
    
    Args:
        credentials: Dictionary with 'url' and 'root_password' keys
    
    Returns:
        StandardDatabase instance for _system database, or None on error
    """
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
        print(f"Error: Unexpected error connecting to ArangoDB: {e}", file=sys.stderr)
        return None


def handle_user_add(args: Namespace) -> int:
    """Create a new ArangoDB user.

    Args:
        args: Parsed command-line arguments with:
            - username: Username to create
            - arango_password_env: Password env var for new user
            - active: Whether user is active (default: True)
            - env_file: Optional .env file path
            - dry_run: Whether to simulate only
            - yes: Skip confirmation prompt

    Returns:
        Exit code (0=success, 1=error, 2=cancelled)
    """
    # Get active flag
    active = getattr(args, 'active', True)

    # Build consequence list based on arguments
    reporter = ResultReporter("user add", dry_run=args.dry_run)
    reporter.add(ConsequenceType.ADDED, f"User '{args.username}' (active: {str(active).lower()})")

    # Dry-run mode: report and exit without database connection
    if args.dry_run:
        reporter.report_result()
        return EXIT_SUCCESS

    # Load credentials (only needed for actual execution)
    credentials = load_credentials(args)
    if not credentials.get("root_password"):
        print("Error: ARANGO_ROOT_PASSWORD environment variable required", file=sys.stderr)
        return EXIT_ERROR

    # Connect to _system database
    sys_db = _get_system_db(credentials)
    if not sys_db:
        return EXIT_ERROR

    # Check if user already exists
    try:
        if sys_db.has_user(args.username):
            print(f"Error: User '{args.username}' already exists", file=sys.stderr)
            return EXIT_ERROR
    except ArangoError as e:
        print(f"Error: Failed to check user existence: {e}", file=sys.stderr)
        return EXIT_ERROR

    # Get user password
    user_password = credentials.get("user_password")
    if not user_password:
        password_env = getattr(args, 'arango_password_env', 'ARANGO_PASSWORD')
        print(f"Error: {password_env} environment variable required for user creation", file=sys.stderr)
        return EXIT_ERROR

    # Confirmation prompt
    if not confirm_action(reporter.report_prompt() + "\n\nAre you sure you want to proceed?", args):
        print("Operation cancelled", file=sys.stderr)
        return EXIT_CANCELLED

    # Execute operation
    try:
        sys_db.create_user(args.username, user_password, active=active)
        reporter.report_result()
        return EXIT_SUCCESS
    except ArangoError as e:
        print(f"Error: Failed to create user: {e}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        return EXIT_ERROR


def handle_user_remove(args: Namespace) -> int:
    """Delete an ArangoDB user.

    Args:
        args: Parsed command-line arguments with:
            - username: Username to delete
            - env_file: Optional .env file path
            - dry_run: Whether to simulate only
            - yes: Skip confirmation prompt

    Returns:
        Exit code (0=success, 1=error, 2=cancelled)
    """
    # Prevent deletion of root user (can check without connection)
    if args.username == "root":
        print("Error: Cannot delete root user", file=sys.stderr)
        return EXIT_ERROR

    # Build consequence list based on arguments
    reporter = ResultReporter("user remove", dry_run=args.dry_run)
    reporter.add(ConsequenceType.REMOVED, f"User '{args.username}'")

    # Dry-run mode: report and exit without database connection
    # Note: Cannot show revoked permissions without connection, but that's acceptable for dry-run
    if args.dry_run:
        reporter.report_result()
        return EXIT_SUCCESS

    # Load credentials (only needed for actual execution)
    credentials = load_credentials(args)
    if not credentials.get("root_password"):
        print("Error: ARANGO_ROOT_PASSWORD environment variable required", file=sys.stderr)
        return EXIT_ERROR

    # Connect to _system database
    sys_db = _get_system_db(credentials)
    if not sys_db:
        return EXIT_ERROR

    # Check if user exists
    try:
        if not sys_db.has_user(args.username):
            print(f"Error: User '{args.username}' not found", file=sys.stderr)
            return EXIT_ERROR
    except ArangoError as e:
        print(f"Error: Failed to check user existence: {e}", file=sys.stderr)
        return EXIT_ERROR

    # Check for user's database permissions (for informative output)
    try:
        perms = sys_db.permissions(args.username)
        for db_name, perm in perms.items():
            if perm != 'none':
                reporter.add(ConsequenceType.REVOKED, f"Permission: {args.username} → {db_name} (was: {perm})")
    except ArangoError:
        # If we can't query permissions, just proceed with user deletion
        pass

    # Confirmation prompt
    if not confirm_action(reporter.report_prompt() + "\n\nAre you sure you want to proceed?", args):
        print("Operation cancelled", file=sys.stderr)
        return EXIT_CANCELLED

    # Execute deletion
    try:
        sys_db.delete_user(args.username)
        reporter.report_result()
        return EXIT_SUCCESS
    except ArangoError as e:
        print(f"Error: Failed to delete user: {e}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        return EXIT_ERROR


def handle_user_list(args: Namespace) -> int:
    """List all ArangoDB users.

    Args:
        args: Parsed command-line arguments with:
            - env_file: Optional .env file path
            - json: Output as JSON

    Returns:
        Exit code (0=success, 1=error)
    """
    # Load credentials
    credentials = load_credentials(args)
    if not credentials.get("root_password"):
        print("Error: ARANGO_ROOT_PASSWORD environment variable required", file=sys.stderr)
        return EXIT_ERROR

    # Connect to _system database
    sys_db = _get_system_db(credentials)
    if not sys_db:
        return EXIT_ERROR

    # List users
    try:
        users = sys_db.users()

        # JSON output
        if getattr(args, 'json', False):
            print(json.dumps(users, indent=2))
            return EXIT_SUCCESS

        # Human-readable output
        print(f"Users ({len(users)}):")
        for user in sorted(users, key=lambda u: u.get('username', u.get('user', ''))):
            username = user.get('username') or user.get('user')
            active = user.get('active', True)
            status = "active" if active else "inactive"
            print(f"  - {username} ({status})")

        return EXIT_SUCCESS
    except ArangoError as e:
        print(f"Error: Failed to list users: {e}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        return EXIT_ERROR


def handle_user_grant(args: Namespace) -> int:
    """Grant database permissions to a user.

    Args:
        args: Parsed command-line arguments with:
            - username: Username to grant permissions to
            - database: Database name
            - permission: Permission level (rw, ro, none)
            - env_file: Optional .env file path
            - dry_run: Whether to simulate only
            - yes: Skip confirmation prompt

    Returns:
        Exit code (0=success, 1=error, 2=cancelled)
    """
    # Get permission level
    permission = getattr(args, 'permission', 'rw')

    # Build consequence list based on arguments
    reporter = ResultReporter("user grant", dry_run=args.dry_run)
    reporter.add(ConsequenceType.GRANTED, f"Permission {permission}: {args.username} → {args.database}")

    # Dry-run mode: report and exit without database connection
    if args.dry_run:
        reporter.report_result()
        return EXIT_SUCCESS

    # Load credentials (only needed for actual execution)
    credentials = load_credentials(args)
    if not credentials.get("root_password"):
        print("Error: ARANGO_ROOT_PASSWORD environment variable required", file=sys.stderr)
        return EXIT_ERROR

    # Connect to _system database
    sys_db = _get_system_db(credentials)
    if not sys_db:
        return EXIT_ERROR

    # Check if user exists
    try:
        if not sys_db.has_user(args.username):
            print(f"Error: User '{args.username}' not found", file=sys.stderr)
            return EXIT_ERROR
    except ArangoError as e:
        print(f"Error: Failed to check user existence: {e}", file=sys.stderr)
        return EXIT_ERROR

    # Check if database exists
    try:
        if not sys_db.has_database(args.database):
            print(f"Error: Database '{args.database}' not found", file=sys.stderr)
            return EXIT_ERROR
    except ArangoError as e:
        print(f"Error: Failed to check database existence: {e}", file=sys.stderr)
        return EXIT_ERROR

    # Confirmation prompt
    if not confirm_action(reporter.report_prompt() + "\n\nAre you sure you want to proceed?", args):
        print("Operation cancelled", file=sys.stderr)
        return EXIT_CANCELLED

    # Execute operation
    try:
        sys_db.update_permission(args.username, permission, args.database)
        reporter.report_result()
        return EXIT_SUCCESS
    except ArangoError as e:
        print(f"Error: Failed to grant permission: {e}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        return EXIT_ERROR


def handle_user_revoke(args: Namespace) -> int:
    """Revoke database permissions from a user.

    Args:
        args: Parsed command-line arguments with:
            - username: Username to revoke permissions from
            - database: Database name
            - env_file: Optional .env file path
            - dry_run: Whether to simulate only
            - yes: Skip confirmation prompt

    Returns:
        Exit code (0=success, 1=error, 2=cancelled)
    """
    # Build consequence list based on arguments
    # Note: Cannot show current permission without connection - acceptable for dry-run
    reporter = ResultReporter("user revoke", dry_run=args.dry_run)
    reporter.add(ConsequenceType.REVOKED, f"Permission: {args.username} → {args.database}")

    # Dry-run mode: report and exit without database connection
    if args.dry_run:
        reporter.report_result()
        return EXIT_SUCCESS

    # Load credentials (only needed for actual execution)
    credentials = load_credentials(args)
    if not credentials.get("root_password"):
        print("Error: ARANGO_ROOT_PASSWORD environment variable required", file=sys.stderr)
        return EXIT_ERROR

    # Connect to _system database
    sys_db = _get_system_db(credentials)
    if not sys_db:
        return EXIT_ERROR

    # Check if user exists
    try:
        if not sys_db.has_user(args.username):
            print(f"Error: User '{args.username}' not found", file=sys.stderr)
            return EXIT_ERROR
    except ArangoError as e:
        print(f"Error: Failed to check user existence: {e}", file=sys.stderr)
        return EXIT_ERROR

    # Get current permission (for informative output)
    current_perm = None
    try:
        perms = sys_db.permissions(args.username)
        current_perm = perms.get(args.database, 'none')
        # Update consequence with current permission info
        if current_perm and current_perm != 'none':
            reporter.consequences.clear()
            reporter.add(ConsequenceType.REVOKED, f"Permission: {args.username} → {args.database} (was: {current_perm})")
    except ArangoError:
        pass

    # Confirmation prompt
    if not confirm_action(reporter.report_prompt() + "\n\nAre you sure you want to proceed?", args):
        print("Operation cancelled", file=sys.stderr)
        return EXIT_CANCELLED

    # Execute operation
    try:
        sys_db.reset_permission(args.username, args.database)
        reporter.report_result()
        return EXIT_SUCCESS
    except ArangoError as e:
        print(f"Error: Failed to revoke permission: {e}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        return EXIT_ERROR


def handle_user_databases(args: Namespace) -> int:
    """List databases accessible to current user (self-service).

    Args:
        args: Parsed command-line arguments with:
            - env_file: Optional .env file path
            - json: Output as JSON

    Returns:
        Exit code (0=success, 1=error)
    """
    # Load credentials
    credentials = load_credentials(args)
    username = credentials.get("username", "root")
    user_password = credentials.get("user_password")

    if not user_password:
        password_env = getattr(args, 'arango_password_env', 'ARANGO_PASSWORD')
        print(f"Error: {password_env} environment variable required", file=sys.stderr)
        return EXIT_ERROR

    # Connect as the user
    try:
        client = ArangoClient(hosts=credentials["url"])
        sys_db = client.db("_system", username=username, password=user_password)
        # Validate connection
        _ = sys_db.version()
    except ArangoError as e:
        print(f"Error: Failed to connect to ArangoDB: {e}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as e:
        print(f"Error: Unexpected error connecting to ArangoDB: {e}", file=sys.stderr)
        return EXIT_ERROR

    # Get user's permissions
    try:
        perms = sys_db.permissions(username)

        # Filter to databases with non-none permissions
        accessible_dbs = {db: perm for db, perm in perms.items() if perm != 'none'}

        # JSON output
        if getattr(args, 'json', False):
            print(json.dumps(accessible_dbs, indent=2))
            return EXIT_SUCCESS

        # Human-readable output
        print(f"Accessible databases for user '{username}' ({len(accessible_dbs)}):")
        for db_name in sorted(accessible_dbs.keys()):
            perm = accessible_dbs[db_name]
            print(f"  - {db_name} (permission: {perm})")

        return EXIT_SUCCESS
    except ArangoError as e:
        print(f"Error: Failed to list databases: {e}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        return EXIT_ERROR


def handle_user_password(args: Namespace) -> int:
    """Change current user's password (self-service).

    Args:
        args: Parsed command-line arguments with:
            - env_file: Optional .env file path
            - new_password_env: Env var name for new password
            - dry_run: Whether to simulate only
            - yes: Skip confirmation prompt

    Returns:
        Exit code (0=success, 1=error, 2=cancelled)
    """
    # Get username for consequence reporting (use env var or default)
    username = os.getenv("ARANGO_USERNAME", "root")

    # Build consequence list based on arguments
    reporter = ResultReporter("user password", dry_run=args.dry_run)
    reporter.add(ConsequenceType.UPDATED, f"Password for user '{username}'")

    # Dry-run mode: report and exit without database connection
    if args.dry_run:
        reporter.report_result()
        return EXIT_SUCCESS

    # Load credentials (only needed for actual execution)
    credentials = load_credentials(args)
    username = credentials.get("username", "root")
    current_password = credentials.get("user_password")

    if not current_password:
        password_env = getattr(args, 'arango_password_env', 'ARANGO_PASSWORD')
        print(f"Error: {password_env} environment variable required", file=sys.stderr)
        return EXIT_ERROR

    # Get new password
    new_password_env = getattr(args, 'new_password_env', 'ARANGO_NEW_PASSWORD')
    new_password = os.getenv(new_password_env)
    if not new_password:
        print(f"Error: {new_password_env} environment variable required", file=sys.stderr)
        return EXIT_ERROR

    # Connect as the user
    try:
        client = ArangoClient(hosts=credentials["url"])
        sys_db = client.db("_system", username=username, password=current_password)
        # Validate connection
        _ = sys_db.version()
    except ArangoError as e:
        print(f"Error: Failed to connect to ArangoDB: {e}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as e:
        print(f"Error: Unexpected error connecting to ArangoDB: {e}", file=sys.stderr)
        return EXIT_ERROR

    # Update consequence with actual username from credentials
    reporter.consequences.clear()
    reporter.add(ConsequenceType.UPDATED, f"Password for user '{username}'")

    # Confirmation prompt
    if not confirm_action(reporter.report_prompt() + "\n\nAre you sure you want to proceed?", args):
        print("Operation cancelled", file=sys.stderr)
        return EXIT_CANCELLED

    # Execute operation
    try:
        sys_db.update_user(username, password=new_password)
        reporter.report_result()
        return EXIT_SUCCESS
    except ArangoError as e:
        print(f"Error: Failed to change password: {e}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        return EXIT_ERROR

