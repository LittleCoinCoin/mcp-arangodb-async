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

    # Database management subcommand
    db_parser = subparsers.add_parser(
        "db",
        help="Manage database configurations",
    )
    db_subparsers = db_parser.add_subparsers(dest="db_command", help="Database command")

    # db add subcommand
    add_parser = db_subparsers.add_parser("add", help="Add a database configuration")
    add_parser.add_argument("key", help="Database key (unique identifier)")
    add_parser.add_argument("--url", required=True, help="ArangoDB server URL")
    add_parser.add_argument("--database", required=True, help="Database name")
    add_parser.add_argument("--username", required=True, help="Username")
    add_parser.add_argument(
        "--password-env",
        required=True,
        help="Environment variable name containing password",
    )
    add_parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Connection timeout in seconds (default: 30.0)",
    )
    add_parser.add_argument(
        "--description",
        default=None,
        help="Optional description",
    )
    add_parser.add_argument(
        "--config-path",
        default="config/databases.yaml",
        help="Path to configuration file (default: config/databases.yaml)",
    )

    # db remove subcommand
    remove_parser = db_subparsers.add_parser("remove", help="Remove a database configuration")
    remove_parser.add_argument("key", help="Database key to remove")
    remove_parser.add_argument(
        "--config-path",
        default="config/databases.yaml",
        help="Path to configuration file (default: config/databases.yaml)",
    )

    # db list subcommand
    list_parser = db_subparsers.add_parser("list", help="List all configured databases")
    list_parser.add_argument(
        "--config-path",
        default="config/databases.yaml",
        help="Path to configuration file (default: config/databases.yaml)",
    )

    # db test subcommand
    test_parser = db_subparsers.add_parser("test", help="Test database connection")
    test_parser.add_argument("key", help="Database key to test")
    test_parser.add_argument(
        "--config-path",
        default="config/databases.yaml",
        help="Path to configuration file (default: config/databases.yaml)",
    )

    # db status subcommand
    status_parser = db_subparsers.add_parser("status", help="Show database resolution status")
    status_parser.add_argument(
        "--config-path",
        default="config/databases.yaml",
        help="Path to configuration file (default: config/databases.yaml)",
    )

    args = parser.parse_args()

    # Handle db subcommands
    if args.command == "db":
        if args.db_command == "add":
            return cli_db.handle_add(args)
        elif args.db_command == "remove":
            return cli_db.handle_remove(args)
        elif args.db_command == "list":
            return cli_db.handle_list(args)
        elif args.db_command == "test":
            return cli_db.handle_test(args)
        elif args.db_command == "status":
            return cli_db.handle_status(args)
        else:
            db_parser.print_help()
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
