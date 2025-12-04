"""
ArangoDB MCP Server - Command Line Interface

This module provides a command-line interface for ArangoDB diagnostics and health checks.
Can be run as: python -m mcp_arangodb_async [command]

Functions:
- main() - Main entry point for command line execution
"""

from __future__ import annotations

import sys
import json
import argparse
import os

from .config import load_config
from .db import get_client_and_db, health_check
from . import cli_db
from . import cli_db_arango
from . import cli_user


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="mcp_arangodb_async",
        description="ArangoDB MCP Server with stdio and HTTP transport support",
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Server subcommand (default)
    server_parser = subparsers.add_parser(
        "server",
        help="Run MCP server (default)",
    )
    server_parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default=None,
        help="Transport type (default: stdio, or from MCP_TRANSPORT env var)",
    )
    server_parser.add_argument(
        "--host",
        default=None,
        help="HTTP host (default: 0.0.0.0, or from MCP_HTTP_HOST env var)",
    )
    server_parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="HTTP port (default: 8000, or from MCP_HTTP_PORT env var)",
    )
    server_parser.add_argument(
        "--stateless", action="store_true", help="Run HTTP in stateless mode"
    )

    # Health subcommand
    health_parser = subparsers.add_parser(
        "health",
        help="Run health check and output JSON",
    )

    # Version subcommand
    version_parser = subparsers.add_parser(
        "version",
        help="Display version information",
    )

    # Database management subcommand
    db_parser = subparsers.add_parser(
        "db",
        help="Manage databases (both config files and ArangoDB databases)",
    )
    db_subparsers = db_parser.add_subparsers(dest="db_command", help="Database command")

    # db config subcommand group (existing YAML config management)
    db_config_parser = db_subparsers.add_parser(
        "config",
        help="Manage YAML database configurations",
    )
    db_config_subparsers = db_config_parser.add_subparsers(dest="db_config_command", help="Config command")

    # db config add subcommand
    config_add_parser = db_config_subparsers.add_parser("add", help="Add a database configuration")
    config_add_parser.add_argument("key", help="Database key (unique identifier)")
    config_add_parser.add_argument("--url", required=True, help="ArangoDB server URL")
    config_add_parser.add_argument("--database", required=True, help="Database name")
    config_add_parser.add_argument("--username", required=True, help="Username")
    config_add_parser.add_argument(
        "--password-env",
        required=True,
        help="Environment variable name containing password",
    )
    config_add_parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Connection timeout in seconds (default: 30.0)",
    )
    config_add_parser.add_argument(
        "--description",
        default=None,
        help="Optional description",
    )
    config_add_parser.add_argument(
        "--config-path",
        default="config/databases.yaml",
        help="Path to configuration file (default: config/databases.yaml)",
    )
    config_add_parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    config_add_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")

    # db config remove subcommand
    config_remove_parser = db_config_subparsers.add_parser("remove", aliases=["rm"], help="Remove a database configuration")
    config_remove_parser.add_argument("key", help="Database key to remove")
    config_remove_parser.add_argument(
        "--config-path",
        default="config/databases.yaml",
        help="Path to configuration file (default: config/databases.yaml)",
    )
    config_remove_parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    config_remove_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")

    # db config list subcommand
    config_list_parser = db_config_subparsers.add_parser("list", aliases=["ls"], help="List all configured databases")
    config_list_parser.add_argument(
        "--config-path",
        default="config/databases.yaml",
        help="Path to configuration file (default: config/databases.yaml)",
    )

    # db config test subcommand
    config_test_parser = db_config_subparsers.add_parser("test", help="Test database connection")
    config_test_parser.add_argument("key", help="Database key to test")
    config_test_parser.add_argument(
        "--config-path",
        default="config/databases.yaml",
        help="Path to configuration file (default: config/databases.yaml)",
    )

    # db config status subcommand
    config_status_parser = db_config_subparsers.add_parser("status", help="Show database resolution status")
    config_status_parser.add_argument(
        "--config-path",
        default="config/databases.yaml",
        help="Path to configuration file (default: config/databases.yaml)",
    )

    # db add subcommand (ArangoDB database creation)
    db_add_parser = db_subparsers.add_parser("add", help="Create ArangoDB database")
    db_add_parser.add_argument("name", help="Database name")
    db_add_parser.add_argument("--with-user", help="Create user and grant access")
    db_add_parser.add_argument("--permission", choices=["rw", "ro", "none"], default="rw", help="Permission level (default: rw)")
    db_add_parser.add_argument("--env-file", help="Path to .env file")
    db_add_parser.add_argument("--arango-root-password-env", help="Root password env var (default: ARANGO_ROOT_PASSWORD)")
    db_add_parser.add_argument("--arango-password-env", help="User password env var (default: ARANGO_PASSWORD)")
    db_add_parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    db_add_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")

    # db remove subcommand (ArangoDB database deletion)
    db_remove_parser = db_subparsers.add_parser("remove", aliases=["rm"], help="Delete ArangoDB database")
    db_remove_parser.add_argument("name", help="Database name")
    db_remove_parser.add_argument("--env-file", help="Path to .env file")
    db_remove_parser.add_argument("--arango-root-password-env", help="Root password env var (default: ARANGO_ROOT_PASSWORD)")
    db_remove_parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    db_remove_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")

    # db list subcommand (ArangoDB database listing)
    db_list_parser = db_subparsers.add_parser("list", aliases=["ls"], help="List ArangoDB databases")
    db_list_parser.add_argument("--env-file", help="Path to .env file")
    db_list_parser.add_argument("--arango-root-password-env", help="Root password env var (default: ARANGO_ROOT_PASSWORD)")
    db_list_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # User management subcommand
    user_parser = subparsers.add_parser(
        "user",
        help="Manage ArangoDB users and permissions",
    )
    user_subparsers = user_parser.add_subparsers(dest="user_command", help="User command")

    # user add subcommand
    user_add_parser = user_subparsers.add_parser("add", help="Create ArangoDB user")
    user_add_parser.add_argument("username", help="Username")
    user_add_parser.add_argument("--active", action="store_true", default=True, help="User is active (default: true)")
    user_add_parser.add_argument("--env-file", help="Path to .env file")
    user_add_parser.add_argument("--arango-root-password-env", help="Root password env var (default: ARANGO_ROOT_PASSWORD)")
    user_add_parser.add_argument("--arango-password-env", help="User password env var (default: ARANGO_PASSWORD)")
    user_add_parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    user_add_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")

    # user remove subcommand
    user_remove_parser = user_subparsers.add_parser("remove", aliases=["rm"], help="Delete ArangoDB user")
    user_remove_parser.add_argument("username", help="Username")
    user_remove_parser.add_argument("--env-file", help="Path to .env file")
    user_remove_parser.add_argument("--arango-root-password-env", help="Root password env var (default: ARANGO_ROOT_PASSWORD)")
    user_remove_parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    user_remove_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")

    # user list subcommand
    user_list_parser = user_subparsers.add_parser("list", aliases=["ls"], help="List ArangoDB users")
    user_list_parser.add_argument("--env-file", help="Path to .env file")
    user_list_parser.add_argument("--arango-root-password-env", help="Root password env var (default: ARANGO_ROOT_PASSWORD)")
    user_list_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # user grant subcommand
    user_grant_parser = user_subparsers.add_parser("grant", help="Grant database permissions")
    user_grant_parser.add_argument("username", help="Username")
    user_grant_parser.add_argument("database", help="Database name")
    user_grant_parser.add_argument("--permission", choices=["rw", "ro", "none"], default="rw", help="Permission level (default: rw)")
    user_grant_parser.add_argument("--env-file", help="Path to .env file")
    user_grant_parser.add_argument("--arango-root-password-env", help="Root password env var (default: ARANGO_ROOT_PASSWORD)")
    user_grant_parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    user_grant_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")

    # user revoke subcommand
    user_revoke_parser = user_subparsers.add_parser("revoke", help="Revoke database permissions")
    user_revoke_parser.add_argument("username", help="Username")
    user_revoke_parser.add_argument("database", help="Database name")
    user_revoke_parser.add_argument("--env-file", help="Path to .env file")
    user_revoke_parser.add_argument("--arango-root-password-env", help="Root password env var (default: ARANGO_ROOT_PASSWORD)")
    user_revoke_parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    user_revoke_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")

    # user databases subcommand (self-service)
    user_databases_parser = user_subparsers.add_parser("databases", help="List accessible databases (self-service)")
    user_databases_parser.add_argument("--env-file", help="Path to .env file")
    user_databases_parser.add_argument("--arango-password-env", help="User password env var (default: ARANGO_PASSWORD)")
    user_databases_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # user password subcommand (self-service)
    user_password_parser = user_subparsers.add_parser("password", help="Change own password (self-service)")
    user_password_parser.add_argument("--env-file", help="Path to .env file")
    user_password_parser.add_argument("--arango-password-env", help="Current password env var (default: ARANGO_PASSWORD)")
    user_password_parser.add_argument("--new-password-env", default="ARANGO_NEW_PASSWORD", help="New password env var (default: ARANGO_NEW_PASSWORD)")
    user_password_parser.add_argument("--dry-run", action="store_true", help="Preview changes without executing")
    user_password_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")

    args = parser.parse_args()

    # Handle version command
    if args.command == "version":
        try:
            from importlib.metadata import version
            pkg_version = version("mcp-arangodb-async")
        except Exception:
            pkg_version = "unknown"

        import sys
        print(f"mcp-arangodb-async version {pkg_version}")
        print(f"Python {sys.version.split()[0]}")
        return 0

    # Handle db subcommands
    if args.command == "db":
        # Handle db config subcommands
        if args.db_command == "config":
            if args.db_config_command == "add":
                return cli_db.handle_add(args)
            elif args.db_config_command in ("remove", "rm"):
                return cli_db.handle_remove(args)
            elif args.db_config_command in ("list", "ls"):
                return cli_db.handle_list(args)
            elif args.db_config_command == "test":
                return cli_db.handle_test(args)
            elif args.db_config_command == "status":
                return cli_db.handle_status(args)
            else:
                db_config_parser.print_help()
                return 1
        # Handle ArangoDB database operations
        elif args.db_command == "add":
            return cli_db_arango.handle_db_add(args)
        elif args.db_command in ("remove", "rm"):
            return cli_db_arango.handle_db_remove(args)
        elif args.db_command in ("list", "ls"):
            return cli_db_arango.handle_db_list(args)
        else:
            db_parser.print_help()
            return 1

    # Handle user subcommands
    if args.command == "user":
        if args.user_command == "add":
            return cli_user.handle_user_add(args)
        elif args.user_command in ("remove", "rm"):
            return cli_user.handle_user_remove(args)
        elif args.user_command in ("list", "ls"):
            return cli_user.handle_user_list(args)
        elif args.user_command == "grant":
            return cli_user.handle_user_grant(args)
        elif args.user_command == "revoke":
            return cli_user.handle_user_revoke(args)
        elif args.user_command == "databases":
            return cli_user.handle_user_databases(args)
        elif args.user_command == "password":
            return cli_user.handle_user_password(args)
        else:
            user_parser.print_help()
            return 1

    # Determine mode: if no command, default to MCP server
    run_health = args.command == "health"
    run_server = args.command == "server" or args.command is None

    # Delegate to MCP server entry point
    if run_server:
        try:
            from .entry import main as entry_main

            # NEW: Build transport config from args and env vars
            transport = getattr(args, "transport", None) or os.getenv("MCP_TRANSPORT", "stdio")

            if transport == "http":
                # Only import TransportConfig if HTTP transport is requested
                from .transport_config import TransportConfig

                transport_config = TransportConfig(
                    transport="http",
                    http_host=getattr(args, "host", None) or os.getenv("MCP_HTTP_HOST", "0.0.0.0"),
                    http_port=getattr(args, "port", None) or int(os.getenv("MCP_HTTP_PORT", "8000")),
                    http_stateless=getattr(args, "stateless", False)
                    or os.getenv("MCP_HTTP_STATELESS", "false").lower() == "true",
                    http_cors_origins=os.getenv("MCP_HTTP_CORS_ORIGINS", "*").split(
                        ","
                    ),
                )
                entry_main(transport_config)
            else:
                # Default stdio transport - no config needed
                entry_main()

            return 0
        except ImportError as e:
            print(
                f"Error: Could not import MCP server entry point: {e}", file=sys.stderr
            )
            print("Please ensure the package is properly installed.", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Error starting MCP server: {e}", file=sys.stderr)
            return 1

    cfg = load_config()

    # CLI diagnostic mode (health check or info)
    try:
        client, db = get_client_and_db(cfg)
        if run_health:
            info = health_check(db)
            print(
                json.dumps(
                    {
                        "ok": True,
                        "url": cfg.arango_url,
                        "db": cfg.database,
                        "user": cfg.username,
                        "info": info,
                    },
                    ensure_ascii=False,
                )
            )
        else:
            version = db.version()
            print(
                f"Connected to ArangoDB {version} at {cfg.arango_url}, DB='{cfg.database}' as user '{cfg.username}'"
            )
            # Optional: quick sanity query to list collections
            try:
                cols = [c["name"] for c in db.collections() if not c.get("isSystem")]
                print(f"Non-system collections: {cols}")
            except Exception as e:
                # Collection listing failed, but don't crash the health check
                print(f"Warning: Could not list collections: {e}")
        client.close()
        return 0
    except Exception as e:
        if run_health:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "error": str(e),
                        "url": cfg.arango_url,
                        "db": cfg.database,
                        "user": cfg.username,
                    },
                    ensure_ascii=False,
                ),
                file=sys.stderr,
            )
        else:
            print(f"Connection failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
