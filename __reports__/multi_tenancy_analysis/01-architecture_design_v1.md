# Multi-Tenancy Architecture Design for mcp-arangodb-async

**Project:** mcp-arangodb-async  
**Version:** 0.3.2  
**Design Date:** 2025-11-08  
**Architect:** Augment Agent  
**Status:** Phase 1 - Architecture Design (v1)

---

## Changes from v0

This v1 report incorporates stakeholder feedback and addresses four key areas:

### 1. Comprehensive Database Status MCP Tools (New Section 2.8)

**Rationale:** The v0 design had only 3 basic MCP tools for database context management. Stakeholders need comprehensive status reporting to understand the current database resolution state.

**Changes:**
- **Researched existing tool:** Found `arango_database_status` in `handlers.py:1725-1791` that tests connection status for currently connected database
- **Designed extension:** Updated `arango_database_status` to work with multi-database context
- **Added new tools:**
  - `arango_database_resolution_status` - Shows which database would be used for next operation (based on 6-level priority)
  - `arango_list_database_configs` - Lists all configured databases with connection status
- **Total MCP tools:** Increased from 3 to 5 for comprehensive status reporting

### 2. CLI Command for Database Status Inspection (Section 2.4)

**Rationale:** Users (not just LLM agents) need to inspect current database configuration state from the command line.

**Changes:**
- Added `mcp-arangodb-async db status` command to CLI design
- Shows same information as MCP status tools (focused database, config file default, all configured databases, resolution preview)
- Included in implementation phases (Phase 2)

### 3. CLI Command Renamed for Clarity (Throughout Document)

**Rationale:** `mcp-arangodb-async config` is ambiguous - could mean "configure the MCP server" but actually means "manage ArangoDB database configurations".

**Changes:**
- **Old:** `mcp-arangodb-async config`
- **New:** `mcp-arangodb-async db`
- **Rationale:** Short, memorable, and clearly indicates we're managing ArangoDB databases (not MCP server configuration)
- **Updated:** All references throughout document (Section 2.4, examples, implementation phases)

### 4. ASCII Data Flow Diagram Converted to Mermaid (Section 1.2)

**Rationale:** Mermaid diagrams are more maintainable, interactive, and consistent with Section 1.1's architecture diagram.

**Changes:**
- Converted ASCII art data flow diagram to Mermaid sequence diagram
- Shows LLM agent request → database resolution → ArangoDB server interaction
- Improved readability and visual consistency

---

## Executive Summary

This document provides detailed architectural design for implementing **Option A-Enhanced (Focused Database Context with Optional Override)** + **Approach 3B (CLI-based Configuration Management)** in the mcp-arangodb-async MCP server.

**Design Goals:**
- ✅ Single MCP server instance supporting multiple databases and multiple ArangoDB servers
- ✅ Focused database context with optional per-tool override
- ✅ Secure configuration management via CLI (using `argparse`)
- ✅ Comprehensive status reporting for LLM agents and users
- ✅ Backward compatibility with existing single-database deployments
- ✅ Production-ready security posture

**Key Design Decisions:**
1. **Session-based focused database context** - Set once, work within it
2. **Multi-database connection pool** - Support multiple servers and databases
3. **YAML configuration file** - Multiple database definitions with environment variable references
4. **CLI-based configuration CRUD** - Secure, admin-controlled (using `argparse`)
5. **Optional database parameter** - Per-tool override for cross-database operations
6. **Comprehensive status tools** - 5 MCP tools for database resolution visibility

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```mermaid
graph TB
    subgraph "LLM Agent"
        A[LLM Agent]
    end
    
    subgraph "MCP Server Process"
        B[MCP Server]
        C[SessionContextManager]
        D[MultiDatabaseConnectionManager]
        E[ConfigFileLoader]
        F[Tool Handlers]
    end
    
    subgraph "Configuration"
        G[YAML Config File]
        H[Environment Variables]
        I[CLI Tool: mcp-arangodb-async db]
    end
    
    subgraph "ArangoDB Instances"
        J[ArangoDB Server 1]
        K[ArangoDB Server 2]
        L[ArangoDB Server N]
    end
    
    A -->|MCP Protocol| B
    B --> C
    B --> F
    F --> C
    F --> D
    D --> E
    E --> G
    E --> H
    I -->|Manages| G
    D -->|Connection Pool| J
    D -->|Connection Pool| K
    D -->|Connection Pool| L
```

### 1.2 Data Flow Diagram

```mermaid
sequenceDiagram
    participant Agent as LLM Agent
    participant MCP as MCP Server
    participant Session as SessionContextManager
    participant Resolver as Database Resolver
    participant Pool as MultiDatabaseConnectionManager
    participant ArangoDB as ArangoDB Server
    
    Note over Agent,ArangoDB: Step 1: Set Focused Database
    Agent->>MCP: set_focused_database("production")
    MCP->>Session: set_focused_database(session_id, "production")
    Session-->>MCP: Success
    MCP-->>Agent: {"success": true, "focused_database": "production"}
    
    Note over Agent,ArangoDB: Step 2: Query with Focused Database
    Agent->>MCP: arango_query("FOR doc IN users RETURN doc")
    MCP->>Resolver: resolve_database(tool_args, session, config)
    Resolver->>Session: get_focused_database(session_id)
    Session-->>Resolver: "production"
    Resolver-->>MCP: "production"
    MCP->>Pool: get_connection("production")
    Pool-->>MCP: (client, db)
    MCP->>ArangoDB: Execute query on production database
    ArangoDB-->>MCP: Query results
    MCP-->>Agent: Query results
    
    Note over Agent,ArangoDB: Step 3: Query with Override
    Agent->>MCP: arango_query("FOR doc IN logs RETURN doc", database="analytics")
    MCP->>Resolver: resolve_database(tool_args, session, config)
    Note over Resolver: Tool arg "database" = "analytics" (Level 1 priority)
    Resolver-->>MCP: "analytics"
    MCP->>Pool: get_connection("analytics")
    Pool-->>MCP: (client, db)
    MCP->>ArangoDB: Execute query on analytics database
    ArangoDB-->>MCP: Query results
    MCP-->>Agent: Query results
```

### 1.3 Integration Points with Existing Codebase

| Component | Existing File | Integration Point | Change Type |
|-----------|---------------|-------------------|-------------|
| **Server Lifespan** | `entry.py:157-221` | Replace singleton connection with multi-database pool | Refactor |
| **Tool Handlers** | `handlers.py:9-13` | Add database resolution logic | Extend |
| **Configuration** | `config.py:45-72` | Add YAML config file support | Extend |
| **Connection Manager** | `db.py:25-99` | Replace singleton with multi-database pool | Replace |
| **CLI Entry Point** | `__main__.py:22-172` | Add `db` subcommand | Extend |
| **Database Status Tool** | `handlers.py:1725-1791` | Extend for multi-database context | Extend |

---

## 2. Component Design

### 2.1 MultiDatabaseConnectionManager

**Purpose:** Manages connections to multiple ArangoDB servers and databases with connection pooling and reuse.

**Responsibilities:**
- Load database configurations from YAML file and environment variables
- Create and maintain connection pool for multiple databases
- Provide thread-safe access to database connections
- Handle connection lifecycle (creation, reuse, cleanup)

**Key Methods (Pseudo-code):**

```python
class MultiDatabaseConnectionManager:
    """Manages connections to multiple ArangoDB servers and databases."""
    
    def __init__(self, config_loader: ConfigFileLoader):
        self._pools: Dict[str, Tuple[ArangoClient, StandardDatabase]] = {}
        self._configs: Dict[str, DatabaseConfig] = {}
        self._lock = threading.Lock()
        self._config_loader = config_loader
    
    def initialize(self):
        """Load database configurations from config file and env vars."""
        # Load from YAML config file
        # Load from environment variables (backward compatibility)
        # Validate configurations
    
    def get_connection(self, database_key: str) -> Tuple[ArangoClient, StandardDatabase]:
        """Get or create connection for specified database."""
        # Thread-safe connection retrieval
        # Create connection if not in pool
        # Reuse existing connection if available
    
    def get_configured_databases(self) -> Dict[str, DatabaseConfig]:
        """Get all configured databases."""
        # Return _configs dictionary
    
    def test_connection(self, database_key: str) -> Dict[str, Any]:
        """Test connection to a specific database."""
        # Get connection, call db.version(), return status
    
    def register_database(self, database_key: str, config: DatabaseConfig):
        """Register a new database configuration at runtime."""
        # Add to _configs
        # Optionally pre-create connection
    
    def close_all(self):
        """Close all connections in the pool."""
        # Cleanup on server shutdown
```

**Strategic Code Snippet (Connection Retrieval):**

```python
def get_connection(self, database_key: str) -> Tuple[ArangoClient, StandardDatabase]:
    with self._lock:
        if database_key not in self._pools:
            config = self._configs.get(database_key)
            if not config:
                raise ValueError(f"Database '{database_key}' not configured")
            
            # Create ArangoClient for this server URL
            client = ArangoClient(hosts=config.url, request_timeout=config.timeout)
            db = client.db(config.database, username=config.username, 
                          password=os.getenv(config.password_env))
            
            self._pools[database_key] = (client, db)
        
        return self._pools[database_key]
```

**Integration Points:**
- **Replaces:** `ConnectionManager` in `db.py:25-99`
- **Called by:** `call_tool()` in `entry.py:324-420`
- **Initialized in:** `server_lifespan()` in `entry.py:157-221`

**File Location:** `mcp_arangodb_async/multi_db_manager.py` (new file)

---

### 2.2 SessionContextManager

**Purpose:** Manages per-session focused database context for MCP connections.

**Responsibilities:**
- Track focused database for each session (stdio or HTTP)
- Provide thread-safe access to session context
- Clean up session context when connection closes
- Support both stdio (persistent) and HTTP (stateful) transports

**Key Methods (Pseudo-code):**

```python
class SessionContextManager:
    """Manages per-session database context for MCP connections."""
    
    def __init__(self, db_manager: MultiDatabaseConnectionManager):
        self._focused_db: Dict[str, str] = {}  # session_id -> database_key
        self._lock = threading.Lock()
        self._db_manager = db_manager
    
    def set_focused_database(self, session_id: str, database_key: str):
        """Set the focused database for a session."""
        # Validate database_key exists in configuration
        # Store in _focused_db
    
    def get_focused_database(self, session_id: str) -> Optional[str]:
        """Get the focused database for a session."""
        # Return focused database or None
    
    def has_focused_database(self, session_id: str) -> bool:
        """Check if session has a focused database set."""
        # Return True if session_id in _focused_db
    
    def clear_session(self, session_id: str):
        """Clear session context when connection closes."""
        # Remove from _focused_db
```

**Strategic Code Snippet (Set Focused Database):**

```python
def set_focused_database(self, session_id: str, database_key: str):
    # Validate database exists in configuration
    if database_key not in self._db_manager.get_configured_databases():
        raise ValueError(f"Database '{database_key}' not configured")
    
    with self._lock:
        self._focused_db[session_id] = database_key
```

**Integration Points:**
- **Called by:** `set_focused_database()` tool handler
- **Called by:** `call_tool()` for database resolution
- **Initialized in:** `server_lifespan()` in `entry.py:157-221`

**File Location:** `mcp_arangodb_async/session_context.py` (new file)

---

### 2.3 ConfigFileLoader

**Purpose:** Load and validate database configurations from YAML file and environment variables.

**Responsibilities:**
- Parse YAML configuration file
- Validate configuration schema using Pydantic
- Merge config file with environment variables
- Provide configuration to MultiDatabaseConnectionManager

**Key Methods (Pseudo-code):**

```python
class ConfigFileLoader:
    """Load and validate database configurations."""

    def __init__(self, config_path: Path = Path.home() / ".mcp-arangodb-async" / "config.yaml"):
        self._config_path = config_path
        self._config_data: Optional[ConfigFile] = None

    def load(self) -> Dict[str, DatabaseConfig]:
        """Load configurations from YAML file and environment variables."""
        # Load YAML file if exists
        # Load from environment variables (backward compatibility)
        # Validate using Pydantic
        # Return merged configurations

    def get_default_database(self) -> Optional[str]:
        """Get default database from config file or environment."""
        # Check config file default_database
        # Check MCP_DEFAULT_DATABASE env var
        # Check ARANGO_DB env var
        # Return None if not found

    def reload(self):
        """Reload configuration from file (for runtime updates)."""
        # Re-read YAML file
        # Validate and update _config_data
```

**Strategic Code Snippet (Load Configuration):**

```python
def load(self) -> Dict[str, DatabaseConfig]:
    configs = {}

    # Load from YAML file
    if self._config_path.exists():
        with open(self._config_path) as f:
            data = yaml.safe_load(f)
            config_file = ConfigFile(**data)  # Pydantic validation
            configs.update(config_file.databases)

    # Backward compatibility: Load from environment variables
    if os.getenv("ARANGO_URL"):
        configs["_env_default"] = DatabaseConfig(
            url=os.getenv("ARANGO_URL", "http://localhost:8529"),
            database=os.getenv("ARANGO_DB", "_system"),
            username=os.getenv("ARANGO_USERNAME", "root"),
            password_env="ARANGO_PASSWORD",
            timeout=float(os.getenv("ARANGO_TIMEOUT_SEC", "30.0"))
        )

    return configs
```

**Integration Points:**
- **Called by:** `MultiDatabaseConnectionManager.initialize()`
- **Initialized in:** `server_lifespan()` in `entry.py:157-221`

**File Location:** `mcp_arangodb_async/config_loader.py` (new file)

---

### 2.4 ConfigCLI (argparse-based) - Renamed to `mcp-arangodb-async db`

**Purpose:** Command-line interface for database configuration CRUD operations.

**Responsibilities:**
- Add/remove/list/update database configurations
- Show current database configuration status
- Validate configuration inputs
- Test database connections
- Manage YAML configuration file

**Key Commands:**

```bash
# Add database
mcp-arangodb-async db add --name production --url http://localhost:8529 \
  --database prod_db --username prod_user --password-env PROD_DB_PASSWORD

# List databases
mcp-arangodb-async db list

# Show current status (NEW in v1)
mcp-arangodb-async db status

# Remove database
mcp-arangodb-async db remove --name staging --yes

# Update database
mcp-arangodb-async db update --name production --timeout 60.0

# Test connection
mcp-arangodb-async db test --name production
```

**Strategic Code Snippet (Main Entry Point):**

```python
def main():
    parser = argparse.ArgumentParser(
        prog="mcp-arangodb-async db",
        description="Manage ArangoDB database configurations"
    )

    subparsers = parser.add_subparsers(dest="command")

    # Add subcommand
    add_parser = subparsers.add_parser("add", help="Add a new database configuration")
    add_parser.add_argument("--name", required=True, help="Database configuration name")
    add_parser.add_argument("--url", required=True, help="ArangoDB URL")
    add_parser.add_argument("--database", required=True, help="Database name")
    add_parser.add_argument("--username", required=True, help="Username")
    add_parser.add_argument("--password-env", required=True, help="Environment variable for password")

    # Status subcommand (NEW in v1)
    status_parser = subparsers.add_parser("status", help="Show current database configuration status")

    # ... other subcommands ...

    args = parser.parse_args()

    if args.command == "add":
        return handle_add(args)
    elif args.command == "status":
        return handle_status(args)
    # ... other handlers ...
```

**Status Command Implementation (NEW in v1):**

```python
def handle_status(args):
    """Show current database configuration status."""
    config_loader = ConfigFileLoader()
    configs = config_loader.load()
    default_db = config_loader.get_default_database()

    print("Database Configuration Status")
    print("=" * 60)
    print(f"Config file: {config_loader._config_path}")
    print(f"Default database: {default_db or '(none)'}")
    print(f"\nConfigured databases ({len(configs)}):")

    for name, config in configs.items():
        print(f"\n  {name}:")
        print(f"    URL: {config.url}")
        print(f"    Database: {config.database}")
        print(f"    Username: {config.username}")
        print(f"    Password env: {config.password_env}")

        # Test connection
        try:
            db_manager = MultiDatabaseConnectionManager(config_loader)
            status = db_manager.test_connection(name)
            print(f"    Status: ✅ Connected (version: {status['version']})")
        except Exception as e:
            print(f"    Status: ❌ Failed ({str(e)})")
```

**Integration Points:**
- **Modifies:** YAML config file at `~/.mcp-arangodb-async/config.yaml`
- **Entry point:** `pyproject.toml` console script or `__main__.py` subcommand

**File Location:** `mcp_arangodb_async/cli/db.py` (new file, renamed from `config.py`)

---

### 2.5 Updated server_lifespan()

**Purpose:** Initialize multi-database infrastructure during server startup.

**Responsibilities:**
- Create MultiDatabaseConnectionManager
- Create SessionContextManager
- Load configurations
- Yield context to server

**Strategic Code Snippet (Refactored Lifespan):**

```python
@asynccontextmanager
async def server_lifespan(server: Server) -> AsyncIterator[Dict[str, Any]]:
    logger = logging.getLogger("mcp_arangodb_async.entry")

    # Initialize configuration loader
    config_loader = ConfigFileLoader()

    # Initialize multi-database connection manager
    db_manager = MultiDatabaseConnectionManager(config_loader)
    db_manager.initialize()

    # Initialize session context manager
    session_manager = SessionContextManager(db_manager)

    # Yield context with managers
    yield {
        "db_manager": db_manager,
        "session_manager": session_manager,
        "config_loader": config_loader
    }

    # Cleanup on shutdown
    db_manager.close_all()
```

**Integration Points:**
- **Replaces:** Current `server_lifespan()` in `entry.py:157-221`
- **Yields:** Multi-database context instead of single db

---

### 2.6 Updated call_tool()

**Purpose:** Resolve database using 6-level priority and execute tool handler.

**Responsibilities:**
- Extract session_id from request context
- Resolve database using priority hierarchy
- Get database connection from pool
- Execute tool handler with resolved database

**Strategic Code Snippet (Database Resolution):**

```python
async def call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    ctx = server.request_context
    db_manager = ctx.lifespan_context["db_manager"]
    session_manager = ctx.lifespan_context["session_manager"]

    # Extract session ID (stdio or HTTP)
    session_id = get_session_id(ctx)

    # Resolve database using 6-level priority
    database_key = resolve_database(
        tool_args=arguments,
        session_manager=session_manager,
        session_id=session_id,
        config_loader=db_manager._config_loader
    )

    # Get database connection
    client, db = db_manager.get_connection(database_key)

    # Execute tool handler
    tool_reg = TOOL_REGISTRY.get(name)
    result = tool_reg.handler(db, arguments)

    return _json_content(result)
```

**Integration Points:**
- **Replaces:** Current `call_tool()` in `entry.py:324-420`
- **Calls:** `resolve_database()` helper function

---

### 2.7 New MCP Tools (Context Management)

#### Tool 1: set_focused_database

**Purpose:** Set the focused database for the current session.

**Signature:**
```python
def set_focused_database(session_manager, args: Dict[str, Any]) -> Dict[str, Any]:
    """Set the focused database for the current session."""
    database_name = args["database_name"]
    session_id = args["_session_id"]  # Injected by call_tool()

    session_manager.set_focused_database(session_id, database_name)

    return {"success": True, "focused_database": database_name}
```

**Tool Model:**
```python
class SetFocusedDatabaseArgs(BaseModel):
    database_name: str = Field(description="Name of the database to focus on")
```

#### Tool 2: get_focused_database

**Purpose:** Get the currently focused database for the session.

**Signature:**
```python
def get_focused_database(session_manager, args: Dict[str, Any]) -> Dict[str, Any]:
    """Get the currently focused database."""
    session_id = args["_session_id"]

    focused_db = session_manager.get_focused_database(session_id)

    return {"focused_database": focused_db}
```

#### Tool 3: list_available_databases

**Purpose:** List all configured databases (read-only, no credentials).

**Signature:**
```python
def list_available_databases(db_manager, args: Dict[str, Any]) -> Dict[str, Any]:
    """List all configured databases."""
    databases = db_manager.get_configured_databases()

    return {
        "databases": [
            {"name": name, "description": config.description}
            for name, config in databases.items()
        ]
    }
```

---

### 2.8 New MCP Tools (Status Reporting) - NEW in v1

**Purpose:** Provide comprehensive database resolution status to LLM agents.

#### Tool 4: arango_database_status (Extended)

**Existing Tool:** `handlers.py:1725-1791`

**Current Behavior:**
- Returns connection status for currently connected database
- Works even when database is unavailable
- Returns server version and database name if connected

**Extension for Multi-Database:**

```python
@register_tool(
    name=ARANGO_DATABASE_STATUS,
    description="Check database connection status and return diagnostic information.",
    model=ArangoDatabaseStatusArgs,
)
@handle_errors
def handle_arango_database_status(
    db_manager: MultiDatabaseConnectionManager,
    session_manager: SessionContextManager,
    args: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Check database connection status (extended for multi-database)."""

    # Get current session's focused database
    session_id = args.get("_session_id")
    focused_db = session_manager.get_focused_database(session_id)

    # Get default database from config
    default_db = db_manager._config_loader.get_default_database()

    # Resolve which database would be used
    database_key = resolve_database(args, session_manager, session_id, db_manager._config_loader)

    # Test connection to resolved database
    try:
        client, db = db_manager.get_connection(database_key)
        version = db.version()

        return {
            "connected": True,
            "current_database": database_key,
            "database_name": db.name,
            "server_version": version,
            "focused_database": focused_db,
            "default_database": default_db,
            "message": "Database connection is active"
        }
    except Exception as e:
        return {
            "connected": False,
            "current_database": database_key,
            "focused_database": focused_db,
            "default_database": default_db,
            "error": str(e),
            "message": "Database connection failed"
        }
```

**Integration Points:**
- **Extends:** Existing `handle_arango_database_status()` in `handlers.py:1725-1791`
- **Adds:** Multi-database context awareness

#### Tool 5: arango_database_resolution_status (NEW)

**Purpose:** Show which database would be used for the next operation based on 6-level priority.

**Signature:**
```python
def handle_arango_database_resolution_status(
    db_manager: MultiDatabaseConnectionManager,
    session_manager: SessionContextManager,
    args: Dict[str, Any]
) -> Dict[str, Any]:
    """Show database resolution status."""
    session_id = args.get("_session_id")

    # Get all resolution levels
    focused_db = session_manager.get_focused_database(session_id)
    default_db = db_manager._config_loader.get_default_database()
    env_db = os.getenv("ARANGO_DB")

    # Resolve which would be used
    resolved_db = resolve_database(args, session_manager, session_id, db_manager._config_loader)

    return {
        "resolved_database": resolved_db,
        "resolution_levels": {
            "level_1_tool_argument": args.get("database"),
            "level_2_session_focused": focused_db,
            "level_3_config_default": default_db,
            "level_4_env_mcp_default": os.getenv("MCP_DEFAULT_DATABASE"),
            "level_5_env_arango_db": env_db,
            "level_6_hardcoded_default": "_system"
        },
        "message": f"Next operation will use database: {resolved_db}"
    }
```

**Tool Model:**
```python
class ArangoDatabaseResolutionStatusArgs(BaseModel):
    """Arguments for arango_database_resolution_status tool."""
    database: Optional[str] = Field(default=None, description="Optional database to test resolution with")
```

#### Tool 6: arango_list_database_configs (NEW)

**Purpose:** List all configured databases with connection status.

**Signature:**
```python
def handle_arango_list_database_configs(
    db_manager: MultiDatabaseConnectionManager,
    args: Dict[str, Any]
) -> Dict[str, Any]:
    """List all configured databases with connection status."""
    configs = db_manager.get_configured_databases()

    databases = []
    for name, config in configs.items():
        # Test connection
        try:
            status = db_manager.test_connection(name)
            databases.append({
                "name": name,
                "url": config.url,
                "database": config.database,
                "description": config.description,
                "connected": True,
                "server_version": status.get("version")
            })
        except Exception as e:
            databases.append({
                "name": name,
                "url": config.url,
                "database": config.database,
                "description": config.description,
                "connected": False,
                "error": str(e)
            })

    return {
        "databases": databases,
        "total_count": len(databases),
        "connected_count": sum(1 for db in databases if db["connected"])
    }
```

**Tool Model:**
```python
class ArangoListDatabaseConfigsArgs(BaseModel):
    """Arguments for arango_list_database_configs tool (no parameters required)."""
    pass
```

**Summary of Status Tools:**

| Tool | Purpose | Returns |
|------|---------|---------|
| `arango_database_status` | Current database connection status | Connected status, version, focused/default databases |
| `arango_database_resolution_status` | Preview database resolution | Which database would be used, all 6 resolution levels |
| `arango_list_database_configs` | List all configured databases | All databases with connection status |
| `set_focused_database` | Set session context | Success confirmation |
| `get_focused_database` | Get session context | Current focused database |
| `list_available_databases` | List database names | Database names and descriptions (no credentials) |

**Total MCP Tools:** 6 (increased from 3 in v0)

---

### 2.9 Updated Tool Models (Optional database Parameter)

**Purpose:** Add optional `database` parameter to all 34 existing tools for per-call override.

**Example (arango_query):**

```python
class QueryArgs(BaseModel):
    query: str = Field(description="AQL query to execute")
    bind_vars: Optional[Dict[str, Any]] = Field(default=None, description="Bind variables")
    database: Optional[str] = Field(default=None, description="Database to query (overrides focused database)")
```

**Implementation Strategy:**
- Add `database: Optional[str]` field to all 34 tool Pydantic models
- Update tool descriptions to mention optional database parameter
- No changes to handler logic (database resolution happens in `call_tool()`)

**File Locations:**
- `mcp_arangodb_async/tools/query.py`
- `mcp_arangodb_async/tools/collection.py`
- `mcp_arangodb_async/tools/document.py`
- ... (all tool model files)

---

## 3. Configuration File Schema

### 3.1 YAML Configuration File Structure

**File Location:** `~/.mcp-arangodb-async/config.yaml`

**Complete Schema:**

```yaml
# Configuration file version
version: "1.0"

# Default database to use when no focused database is set
default_database: production

# Database configurations
databases:
  production:
    url: http://localhost:8529
    database: prod_db
    username: prod_user
    password_env: PROD_DB_PASSWORD  # Environment variable reference
    timeout: 30.0
    description: "Production database for live data"

  staging:
    url: http://localhost:8529
    database: staging_db
    username: staging_user
    password_env: STAGING_DB_PASSWORD
    timeout: 30.0
    description: "Staging database for pre-production testing"

  analytics:
    url: http://analytics.example.com:8530  # Different server
    database: analytics_db
    username: analytics_user
    password_env: ANALYTICS_DB_PASSWORD
    timeout: 60.0
    description: "Analytics and reporting database"
```

### 3.2 Pydantic Models for Validation

```python
from pydantic import BaseModel, Field, validator
from typing import Dict, Optional

class DatabaseConfig(BaseModel):
    """Configuration for a single database connection."""

    url: str = Field(description="ArangoDB server URL (e.g., http://localhost:8529)")
    database: str = Field(description="Database name")
    username: str = Field(description="Username for authentication")
    password_env: str = Field(description="Environment variable containing password")
    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    description: Optional[str] = Field(default=None, description="Human-readable description")

    @validator("url")
    def validate_url(cls, v):
        """Validate URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v.rstrip("/")

    @validator("timeout")
    def validate_timeout(cls, v):
        """Validate timeout is positive."""
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v

class ConfigFile(BaseModel):
    """Root configuration file model."""

    version: str = Field(description="Configuration file version")
    default_database: Optional[str] = Field(default=None, description="Default database name")
    databases: Dict[str, DatabaseConfig] = Field(description="Database configurations")

    @validator("version")
    def validate_version(cls, v):
        """Validate version format."""
        if v != "1.0":
            raise ValueError("Unsupported configuration version")
        return v

    @validator("default_database")
    def validate_default_database(cls, v, values):
        """Validate default_database exists in databases."""
        if v and "databases" in values and v not in values["databases"]:
            raise ValueError(f"default_database '{v}' not found in databases")
        return v
```

### 3.3 Validation Rules

**Required Fields:**

- `version` - Must be "1.0"
- `databases` - Must contain at least one database configuration
- `url` - Must be valid HTTP/HTTPS URL
- `database` - Must be non-empty string
- `username` - Must be non-empty string
- `password_env` - Must be valid environment variable name

**Optional Fields:**

- `default_database` - If specified, must exist in `databases`
- `timeout` - Defaults to 30.0 seconds
- `description` - Human-readable description

**Security Rules:**

- ❌ **No passwords in config file** - Only environment variable references
- ✅ **Passwords in environment variables** - `export PROD_DB_PASSWORD=secret`

---

## 4. Database Resolution Algorithm

### 4.1 6-Level Priority System

**Pseudo-code:**

```python
def resolve_database(
    tool_args: Dict[str, Any],
    session_manager: SessionContextManager,
    session_id: str,
    config_loader: ConfigFileLoader
) -> str:
    """Resolve database using 6-level priority system.

    Returns:
        database_key: Name of the database to use

    Raises:
        ValueError: If no database can be resolved
    """

    # Level 1: Tool argument override
    if "database" in tool_args and tool_args["database"]:
        return tool_args["database"]

    # Level 2: Session focused database
    focused_db = session_manager.get_focused_database(session_id)
    if focused_db:
        return focused_db

    # Level 3: Config file default_database
    default_db = config_loader.get_default_database()
    if default_db:
        return default_db

    # Level 4: Environment variable MCP_DEFAULT_DATABASE
    env_default = os.getenv("MCP_DEFAULT_DATABASE")
    if env_default:
        return env_default

    # Level 5: Environment variables (backward compatibility)
    if os.getenv("ARANGO_DB"):
        return "_env_default"  # Special key for env-based config

    # Level 6: Hardcoded default
    return "_system"
```

### 4.2 Decision Tree

```mermaid
graph TD
    Start[Database Resolution] --> L1{Tool argument<br/>'database' present?}
    L1 -->|Yes| UseL1[Use tool argument<br/>Level 1]
    L1 -->|No| L2{Session focused<br/>database set?}
    L2 -->|Yes| UseL2[Use session focused<br/>Level 2]
    L2 -->|No| L3{Config file<br/>default_database?}
    L3 -->|Yes| UseL3[Use config default<br/>Level 3]
    L3 -->|No| L4{MCP_DEFAULT_DATABASE<br/>env var set?}
    L4 -->|Yes| UseL4[Use env var override<br/>Level 4]
    L4 -->|No| L5{ARANGO_DB<br/>env var set?}
    L5 -->|Yes| UseL5[Use legacy env var<br/>Level 5]
    L5 -->|No| UseL6[Use hardcoded default<br/>_system<br/>Level 6]

    UseL1 --> End[Return database_key]
    UseL2 --> End
    UseL3 --> End
    UseL4 --> End
    UseL5 --> End
    UseL6 --> End
```

### 4.3 Edge Case Handling

**Case 1: Database not found in configuration**

```python
def get_connection(self, database_key: str):
    if database_key not in self._configs:
        raise ValueError(
            f"Database '{database_key}' not configured. "
            f"Available databases: {list(self._configs.keys())}"
        )
```

**Case 2: Connection failure**

```python
def get_connection(self, database_key: str):
    try:
        client = ArangoClient(hosts=config.url, request_timeout=config.timeout)
        db = client.db(config.database, username=config.username, password=password)
        db.version()  # Validate connection
    except Exception as e:
        raise ConnectionError(
            f"Failed to connect to database '{database_key}': {e}"
        )
```

**Case 3: Invalid database reference in tool call**

```python
def resolve_database(...):
    database_key = ...  # Resolved from priority system

    # Validate database exists in configuration
    if database_key not in db_manager.get_configured_databases():
        raise ValueError(
            f"Database '{database_key}' not configured. "
            f"Use list_available_databases() to see available databases."
        )
```

---

## 5. Session Management Strategy

### 5.1 Session Identification

**stdio Transport:**
- **Session ID:** Connection-based (single persistent connection per client)
- **Lifetime:** Entire client session (until disconnect)
- **Storage:** In-memory dictionary keyed by connection ID

**HTTP Transport (Stateful Mode):**
- **Session ID:** HTTP session cookie or header
- **Lifetime:** Configurable session timeout
- **Storage:** In-memory dictionary or external session store (Redis)

**HTTP Transport (Stateless Mode):**
- **Session ID:** Not supported (no session persistence)
- **Fallback:** Require `database` parameter in every tool call

### 5.2 Session State Storage

```python
class SessionContextManager:
    def __init__(self, db_manager):
        self._focused_db: Dict[str, str] = {}  # session_id -> database_key
        self._session_metadata: Dict[str, Dict] = {}  # session_id -> metadata
        self._lock = threading.Lock()

    def get_session_id(self, request_context) -> str:
        """Extract session ID from request context."""
        # stdio: Use connection ID
        # HTTP: Use session cookie or header
        # Stateless HTTP: Raise error (no session support)
```

### 5.3 Session Lifecycle

```mermaid
sequenceDiagram
    participant Client as LLM Agent
    participant Server as MCP Server
    participant Session as SessionContextManager

    Note over Client,Session: 1. Connection Established
    Client->>Server: Connect
    Server->>Session: Initialize session context
    Note over Session: No focused database set<br/>(use default)

    Note over Client,Session: 2. Set Focused Database
    Client->>Server: set_focused_database("production")
    Server->>Session: set_focused_database(session_id, "production")
    Session-->>Server: Success
    Server-->>Client: Confirmation

    Note over Client,Session: 3. Work Within Context
    Client->>Server: arango_query(...)
    Server->>Session: get_focused_database(session_id)
    Session-->>Server: "production"
    Note over Server: All operations use "production"

    Note over Client,Session: 4. Switch Context
    Client->>Server: set_focused_database("staging")
    Server->>Session: set_focused_database(session_id, "staging")
    Note over Server: All operations now use "staging"

    Note over Client,Session: 5. Connection Closed
    Client->>Server: Disconnect
    Server->>Session: clear_session(session_id)
    Session-->>Server: Cleanup complete
```

### 5.4 Cleanup and Resource Management

```python
@asynccontextmanager
async def server_lifespan(server: Server):
    session_manager = SessionContextManager(db_manager)

    # Register cleanup handler
    def cleanup_session(session_id: str):
        session_manager.clear_session(session_id)

    # Yield context
    yield {"session_manager": session_manager, ...}

    # Cleanup on shutdown
    session_manager.clear_all_sessions()
```

---

## 6. Backward Compatibility Strategy

### 6.1 Compatibility Requirements

**Existing Deployments Must Continue to Work:**
- ✅ Environment variable configuration (ARANGO_URL, ARANGO_DB, etc.)
- ✅ Single database operation
- ✅ No config file required
- ✅ No code changes required

### 6.2 Backward Compatibility Implementation

**Strategy:** Treat environment variables as a special database configuration.

```python
class ConfigFileLoader:
    def load(self) -> Dict[str, DatabaseConfig]:
        configs = {}

        # Load from YAML file (new multi-database mode)
        if self._config_path.exists():
            configs.update(self._load_from_yaml())

        # Backward compatibility: Load from environment variables
        if os.getenv("ARANGO_URL"):
            configs["_env_default"] = DatabaseConfig(
                url=os.getenv("ARANGO_URL", "http://localhost:8529"),
                database=os.getenv("ARANGO_DB", "_system"),
                username=os.getenv("ARANGO_USERNAME", "root"),
                password_env="ARANGO_PASSWORD",
                timeout=float(os.getenv("ARANGO_TIMEOUT_SEC", "30.0"))
            )

        return configs
```

**Resolution Priority for Backward Compatibility:**

```
Level 5: Environment variables (ARANGO_DB)
  ↓
  Maps to special database key "_env_default"
  ↓
  Uses environment variable configuration
  ↓
  100% backward compatible
```

### 6.3 Migration Path

**Phase 1: Existing Users (No Changes)**
```bash
# Existing deployment continues to work
export ARANGO_URL=http://localhost:8529
export ARANGO_DB=my_database
export ARANGO_USERNAME=my_user
export ARANGO_PASSWORD=my_password

mcp-arangodb-async  # Works exactly as before
```

**Phase 2: Gradual Migration (Optional)**
```bash
# User creates config file for multi-database support
mcp-arangodb-async db add --name production \
  --url http://localhost:8529 \
  --database my_database \
  --username my_user \
  --password-env MY_DB_PASSWORD

# Environment variables still work as fallback
export MY_DB_PASSWORD=my_password

mcp-arangodb-async  # Now supports multi-database
```

**Phase 3: Full Multi-Database (Optional)**
```bash
# User adds multiple databases
mcp-arangodb-async db add --name staging ...
mcp-arangodb-async db add --name analytics ...

# LLM agent can switch between databases
set_focused_database("production")
set_focused_database("staging")
```

### 6.4 Deprecation Timeline

**No Deprecation Planned:**
- Environment variable configuration will remain supported indefinitely
- No breaking changes for existing users
- Config file is optional enhancement, not replacement

---

## 7. Security Considerations

### 7.1 Credential Management

**Security Principle:** Passwords NEVER stored in config file, only in environment variables.

**Config File (Secure):**
```yaml
databases:
  production:
    password_env: PROD_DB_PASSWORD  # ✅ Environment variable reference
```

**Environment Variables (Secure):**
```bash
export PROD_DB_PASSWORD=super_secret_password  # ✅ Not in config file
```

**Anti-Pattern (Insecure):**
```yaml
databases:
  production:
    password: super_secret_password  # ❌ NEVER DO THIS
```

### 7.2 CLI Access Control

**File Permissions:**
```bash
# Config file should be readable only by user
chmod 600 ~/.mcp-arangodb-async/config.yaml

# Config directory should be user-only
chmod 700 ~/.mcp-arangodb-async/
```

**CLI Tool Permissions:**
- Only users with shell access can run `mcp-arangodb-async db` commands
- No remote access to configuration management
- Audit trail via shell history

### 7.3 MCP Tool Security

**Read-Only Database Discovery:**
```python
def list_available_databases(db_manager, args):
    """List databases (names only, no credentials)."""
    return {
        "databases": [
            {"name": name, "description": config.description}
            # ❌ NO url, username, password_env
        ]
    }
```

**No Configuration CRUD via MCP Tools:**
- ❌ No `add_database_config()` tool
- ❌ No `remove_database_config()` tool
- ❌ No `update_database_config()` tool
- ✅ Only read-only `list_available_databases()` tool

### 7.4 Connection Pool Security

**Connection Limits:**
```python
class MultiDatabaseConnectionManager:
    MAX_CONNECTIONS = 100  # Prevent connection exhaustion

    def get_connection(self, database_key: str):
        if len(self._pools) >= self.MAX_CONNECTIONS:
            raise RuntimeError("Maximum connection pool size exceeded")
```

**Credential Validation:**
```python
def get_connection(self, database_key: str):
    password = os.getenv(config.password_env)
    if not password:
        raise ValueError(
            f"Password environment variable '{config.password_env}' not set"
        )
```

### 7.5 Audit Logging

**Configuration Changes:**
```python
def handle_add(args):
    logger.info(f"Adding database configuration: {args.name}")
    # ... add database ...
    logger.info(f"Database '{args.name}' added successfully")
```

**Database Access:**
```python
def get_connection(self, database_key: str):
    logger.info(f"Accessing database: {database_key}")
    # ... get connection ...
```

**Focused Database Changes:**
```python
def set_focused_database(self, session_id: str, database_key: str):
    logger.info(f"Session {session_id} focused on database: {database_key}")
    # ... set focused database ...
```

---

## 8. Error Handling and Validation

### 8.1 Configuration Validation Errors

**Invalid YAML Syntax:**
```python
try:
    data = yaml.safe_load(f)
except yaml.YAMLError as e:
    raise ValueError(f"Invalid YAML syntax in config file: {e}")
```

**Schema Validation Errors:**
```python
try:
    config_file = ConfigFile(**data)
except ValidationError as e:
    raise ValueError(f"Configuration validation failed: {e}")
```

**Missing Environment Variables:**
```python
password = os.getenv(config.password_env)
if not password:
    raise ValueError(
        f"Password environment variable '{config.password_env}' not set. "
        f"Please set: export {config.password_env}=<password>"
    )
```

### 8.2 Connection Failures

**Per-Database Connection Failure:**
```python
def get_connection(self, database_key: str):
    try:
        client = ArangoClient(...)
        db = client.db(...)
        db.version()  # Validate connection
    except Exception as e:
        logger.error(f"Failed to connect to database '{database_key}': {e}")
        raise ConnectionError(
            f"Database '{database_key}' is unavailable. "
            f"Please check configuration and server status."
        )
```

**Graceful Degradation:**
- Connection failure for one database does not affect other databases
- Server continues to operate with available databases
- Clear error messages to LLM agent

### 8.3 Invalid Database References

**Database Not Configured:**
```python
def resolve_database(...):
    if database_key not in db_manager.get_configured_databases():
        available = ", ".join(db_manager.get_configured_databases().keys())
        raise ValueError(
            f"Database '{database_key}' not configured. "
            f"Available databases: {available}. "
            f"Use list_available_databases() tool to see all databases."
        )
```

**Tool Call Error Response:**
```json
{
  "error": "Database 'invalid_db' not configured",
  "available_databases": ["production", "staging", "analytics"],
  "suggestion": "Use list_available_databases() to see all databases"
}
```

### 8.4 Graceful Degradation Strategies

**Fallback to Default Database:**
```python
def resolve_database(...):
    try:
        return _resolve_with_priority(...)
    except Exception as e:
        logger.warning(f"Database resolution failed: {e}. Falling back to default.")
        return config_loader.get_default_database() or "_system"
```

**Partial Functionality:**
- If config file is invalid, fall back to environment variables
- If one database is unavailable, continue with other databases
- If session context is lost, fall back to default database

---

## 9. Implementation Phases

### 9.1 Phase 1: Core Infrastructure (1.5 weeks)

**Deliverables:**
- `MultiDatabaseConnectionManager` class
- `SessionContextManager` class
- `ConfigFileLoader` class
- Pydantic models for configuration validation
- Unit tests for core components

**Tasks:**
1. Create `multi_db_manager.py` with connection pool logic
2. Create `session_context.py` with session management
3. Create `config_loader.py` with YAML parsing
4. Define Pydantic models in `config_models.py`
5. Write unit tests for each component
6. Integration test: Load config, create connections, manage sessions

**Dependencies:** None (foundational work)

**Success Criteria:**
- ✅ Can load YAML config file
- ✅ Can create connections to multiple databases
- ✅ Can manage session context
- ✅ All unit tests pass

### 9.2 Phase 2: CLI Tool (1 week)

**Deliverables:**
- `cli/db.py` with argparse-based CLI (renamed from `config.py`)
- Add/remove/list/update/test/status commands
- YAML file manipulation logic
- CLI integration tests

**Tasks:**
1. Create `cli/db.py` with argparse setup
2. Implement `handle_add()` command
3. Implement `handle_remove()` command
4. Implement `handle_list()` command
5. Implement `handle_update()` command
6. Implement `handle_test()` command (connection test)
7. Implement `handle_status()` command (NEW in v1)
8. Add CLI entry point to `pyproject.toml`
9. Write CLI integration tests

**Dependencies:** Phase 1 (ConfigFileLoader)

**Success Criteria:**
- ✅ Can add database via CLI
- ✅ Can list databases via CLI
- ✅ Can show status via CLI (NEW in v1)
- ✅ Can remove database via CLI
- ✅ Can test connection via CLI
- ✅ YAML file correctly updated

### 9.3 Phase 3: Context Management & Status Tools (1 week - expanded from 0.5 weeks)

**Deliverables:**
- `set_focused_database()` MCP tool
- `get_focused_database()` MCP tool
- `list_available_databases()` MCP tool
- `arango_database_status()` MCP tool (extended)
- `arango_database_resolution_status()` MCP tool (NEW in v1)
- `arango_list_database_configs()` MCP tool (NEW in v1)
- Tool registration and handlers

**Tasks:**
1. Create tool models for new tools
2. Implement tool handlers
3. Extend existing `arango_database_status` for multi-database context
4. Implement `arango_database_resolution_status` tool (NEW in v1)
5. Implement `arango_list_database_configs` tool (NEW in v1)
6. Register tools in TOOL_REGISTRY
7. Update tool documentation
8. Write tool integration tests

**Dependencies:** Phase 1 (SessionContextManager, MultiDatabaseConnectionManager)

**Success Criteria:**
- ✅ Can set focused database via MCP tool
- ✅ Can get focused database via MCP tool
- ✅ Can list databases via MCP tool
- ✅ Can check database status via MCP tool
- ✅ Can preview database resolution via MCP tool (NEW in v1)
- ✅ Can list all database configs with status via MCP tool (NEW in v1)
- ✅ All tool tests pass

### 9.4 Phase 4: Tool Model Updates (1 week)

**Deliverables:**
- Optional `database` parameter in all 34 tools
- Updated tool descriptions
- Updated tool documentation

**Tasks:**
1. Add `database: Optional[str]` to all tool Pydantic models
2. Update tool descriptions to mention database parameter
3. Update `call_tool()` to use database resolution
4. Refactor `server_lifespan()` for multi-database context
5. Update all tool integration tests
6. Regression testing for existing functionality

**Dependencies:** Phase 1, Phase 3

**Success Criteria:**
- ✅ All 34 tools support optional database parameter
- ✅ Database resolution works correctly
- ✅ Backward compatibility maintained
- ✅ All existing tests pass

### 9.5 Phase 5: Testing & Documentation (1 week)

**Deliverables:**
- Comprehensive test suite
- Security review
- Performance testing
- User documentation
- API reference updates
- Deployment guides

**Tasks:**
1. Write end-to-end integration tests
2. Security audit (credential management, access control)
3. Performance testing (connection pool, session management)
4. Update README.md with multi-database examples
5. Create migration guide for existing users
6. Update API reference documentation
7. Create deployment guide for multi-database setups
8. Document new status tools (NEW in v1)

**Dependencies:** Phase 1-4 (all implementation complete)

**Success Criteria:**
- ✅ 100% test pass rate
- ✅ Security review complete
- ✅ Performance benchmarks meet targets
- ✅ Documentation complete and accurate

---

## 10. Summary

### 10.1 Architecture Highlights

- ✅ **Multi-database connection pool** - Supports multiple ArangoDB servers and databases
- ✅ **Session-based focused context** - Natural LLM agent workflow
- ✅ **6-level configuration priority** - Flexible and backward compatible
- ✅ **CLI-based configuration management** - Secure, admin-controlled (using `argparse`, renamed to `mcp-arangodb-async db`)
- ✅ **Optional database parameter** - Per-tool override for cross-database operations
- ✅ **Comprehensive status reporting** - 6 MCP tools for database resolution visibility (increased from 3 in v0)

### 10.2 Key Design Decisions

1. **argparse for CLI** - Consistency with existing codebase, no new dependencies
2. **CLI renamed to `mcp-arangodb-async db`** - Clear, short, memorable (NEW in v1)
3. **YAML for config file** - Human-readable, industry standard
4. **Environment variables for passwords** - Security best practice
5. **Session-based context** - Eliminates context pollution
6. **Backward compatibility** - Existing deployments continue to work
7. **Comprehensive status tools** - 6 MCP tools for visibility (NEW in v1)
8. **Mermaid diagrams** - Improved visual consistency (NEW in v1)

### 10.3 Changes from v0

| Change | Rationale | Impact |
|--------|-----------|--------|
| **CLI renamed to `mcp-arangodb-async db`** | Clarity - explicitly indicates ArangoDB database management | All CLI examples updated |
| **Added 3 new status MCP tools** | Comprehensive database resolution visibility for LLM agents | Total MCP tools: 6 (was 3) |
| **Added CLI `status` command** | Users need to inspect configuration state from command line | Phase 2 expanded |
| **Converted ASCII to Mermaid** | Visual consistency, maintainability, interactivity | Section 1.2 rewritten |

### 10.4 Implementation Effort

| Phase | Duration | Complexity | Changes from v0 |
|-------|----------|------------|-----------------|
| Phase 1: Core Infrastructure | 1.5 weeks | Medium-High | No change |
| Phase 2: CLI Tool | 1 week | Medium | Added `status` command |
| Phase 3: Context & Status Tools | 1 week | Medium | Expanded from 0.5 weeks, added 3 status tools |
| Phase 4: Tool Model Updates | 1 week | Medium | No change |
| Phase 5: Testing & Documentation | 1 week | Medium | Added status tool documentation |
| **Total** | **5.5 weeks** | **Medium-High** | **+0.5 weeks from v0** |

---

**Report Version:** v1
**Last Updated:** 2025-11-08
**Status:** Ready for Stakeholder Review


