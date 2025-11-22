# Multi-Tenancy Architectural Analysis for mcp-arangodb-async

**Project:** mcp-arangodb-async  
**Version:** 0.3.2  
**Analysis Date:** 2025-11-08  
**Analyst:** Augment Agent  
**Status:** Phase 1 - Architectural Analysis

---

## Executive Summary

The current mcp-arangodb-async implementation **does not support multi-tenancy** for database access. The architecture is designed for **single-database, single-tenant operation** with configuration loaded exclusively from environment variables at server startup. Database context is established globally during server initialization and remains fixed for the server's lifetime.

**Key Findings:**
- ✅ Port configuration exists via `ARANGO_URL` environment variable
- ❌ No multi-database support - single database per server instance
- ❌ No per-request or per-connection database selection
- ❌ Configuration is static (startup-time only), not dynamic
- ❌ Global singleton connection manager enforces single-database constraint

**Impact:** Each MCP client requiring access to a different ArangoDB database must run a separate server instance with distinct environment configurations.

---

## 1. Configuration Analysis

### 1.1 Configuration Mechanisms

The server uses **environment variables exclusively** for configuration, with optional `.env` file support via `python-dotenv`.

**Configuration Loading Flow:**
```
Startup → load_config() → Environment Variables → Config dataclass → ConnectionManager
```

**File References:**
- `mcp_arangodb_async/config.py` (lines 45-72): `load_config()` function
- `mcp_arangodb_async/entry.py` (lines 179-211): Server lifespan initialization
- `mcp_arangodb_async/db.py` (lines 25-99): ConnectionManager singleton

### 1.2 Configuration Parameters

#### ArangoDB Connection Parameters

| Parameter | Type | Default | Scope | Source |
|-----------|------|---------|-------|--------|
| `ARANGO_URL` | String (URL) | `http://localhost:8529` | Global | `config.py:55` |
| `ARANGO_DB` | String | `_system` | Global | `config.py:56` |
| `ARANGO_USERNAME` | String | `root` | Global | `config.py:57` |
| `ARANGO_PASSWORD` | String | `""` (empty) | Global | `config.py:58` |
| `ARANGO_TIMEOUT_SEC` | Float | `30.0` | Global | `config.py:59-64` |

**Port Configuration:** ✅ **Exists** - The port is specified within `ARANGO_URL` (e.g., `http://localhost:8529`). The URL is parsed by the `python-arango` library's `ArangoClient` class.

#### Connection Tuning Parameters

| Parameter | Type | Default | Scope | Source |
|-----------|------|---------|-------|--------|
| `ARANGO_CONNECT_RETRIES` | Integer | `3` | Global | `entry.py:183` |
| `ARANGO_CONNECT_DELAY_SEC` | Float | `1.0` | Global | `entry.py:184` |

#### MCP Transport Parameters

| Parameter | Type | Default | Scope | Source |
|-----------|------|---------|-------|--------|
| `MCP_TRANSPORT` | Enum | `stdio` | Global | `__main__.py:86` |
| `MCP_HTTP_HOST` | String | `0.0.0.0` | Global | `__main__.py:94` |
| `MCP_HTTP_PORT` | Integer | `8000` | Global | `__main__.py:95` |
| `MCP_HTTP_STATELESS` | Boolean | `false` | Global | `__main__.py:96-97` |
| `MCP_HTTP_CORS_ORIGINS` | String (CSV) | `*` | Global | `__main__.py:98-100` |

#### Logging Parameters

| Parameter | Type | Default | Scope | Source |
|-----------|------|---------|-------|--------|
| `LOG_LEVEL` | Enum | `INFO` | Global | `entry.py:161` |

### 1.3 Configuration Lifecycle

**Static Configuration (Startup-Time Only):**
1. Server starts → `server_lifespan()` context manager invoked (`entry.py:158`)
2. `load_config()` reads environment variables once (`entry.py:179`)
3. `get_client_and_db(cfg)` creates connection (`entry.py:187`)
4. Connection stored in lifespan context (`entry.py:214`)
5. **Configuration remains fixed until server restart**

**No Dynamic Configuration:** The architecture does not support runtime configuration changes. Changing databases requires:
1. Stopping the server
2. Updating environment variables
3. Restarting the server

### 1.4 Configuration Sources Priority

1. **Command-line arguments** (HTTP transport only: `--host`, `--port`, `--stateless`)
2. **Environment variables** (all configuration)
3. **`.env` file** (loaded automatically if present)
4. **Hardcoded defaults** (fallback values in `config.py`)

---

## 2. Multi-Tenancy Assessment

### 2.1 Current Multi-Database Support

**Verdict: ❌ NOT SUPPORTED**

The implementation enforces **single-database operation** through multiple architectural constraints:

#### Constraint 1: Singleton Connection Manager

**File:** `mcp_arangodb_async/db.py` (lines 25-99)

```python
class ConnectionManager:
    """Thread-safe singleton connection manager for ArangoDB connections."""
    
    _instance: Optional['ConnectionManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'ConnectionManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._client = None      # Single client
                    cls._instance._db = None          # Single database
                    cls._instance._config = None      # Single config
        return cls._instance
```

**Analysis:**
- Singleton pattern ensures only **one ConnectionManager instance** per process
- Stores **single** `_client`, `_db`, and `_config` attributes
- `get_connection()` method (lines 41-73) reuses existing connection if config matches
- **No support for multiple simultaneous database connections**

#### Constraint 2: Global Lifespan Context

**File:** `mcp_arangodb_async/entry.py` (lines 157-221)

```python
@asynccontextmanager
async def server_lifespan(server: Server) -> AsyncIterator[Dict[str, Any]]:
    """Initialize ArangoDB client+db once and share via request context."""
    cfg = load_config()  # Single config loaded once
    # ... connection logic ...
    try:
        yield {"db": db, "client": client}  # Single db shared globally
    finally:
        # ... cleanup ...
```

**Analysis:**
- Lifespan context initialized **once at server startup**
- Single `db` object shared across **all requests**
- No mechanism to switch databases per-request or per-connection

#### Constraint 3: Request Handler Architecture

**File:** `mcp_arangodb_async/entry.py` (lines 324-420)

```python
@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.Content]:
    """Execute a tool by dispatching to its registered handler."""
    ctx = server.request_context
    db = ctx.lifespan_context.get("db")  # Always retrieves same global db
    # ... tool execution ...
```

**Analysis:**
- All tool handlers receive the **same `db` object** from lifespan context
- No per-request database selection mechanism
- Tool arguments do not include database parameter

### 2.2 Database Selection Scope

**Current Scope:** Globally fixed (server-level)

| Scope Level | Supported | Implementation |
|-------------|-----------|----------------|
| **Per-server** | ✅ Yes | Environment variables at startup |
| **Per-connection** | ❌ No | No connection-level configuration |
| **Per-request** | ❌ No | No request-level database parameter |
| **Per-tool-call** | ❌ No | Tool arguments don't include database |

### 2.3 Multi-Client Scenarios

**Scenario 1: Multiple Clients, Same Database**
- ✅ **Supported** - All clients share the same database connection
- Use case: Multiple AI assistants accessing shared data

**Scenario 2: Multiple Clients, Different Databases**
- ❌ **NOT Supported** - Requires separate server instances
- Current workaround: Run multiple server processes with different environment configs

**Scenario 3: Single Client, Multiple Databases**
- ❌ **NOT Supported** - Client cannot switch databases
- Current workaround: Configure multiple MCP server entries in client config

### 2.4 Connection Pooling Analysis

**File:** `mcp_arangodb_async/db.py` (lines 41-73)

The `ConnectionManager.get_connection()` method implements **connection reuse**, not true pooling:

```python
def get_connection(self, cfg: Config) -> Tuple[ArangoClient, StandardDatabase]:
    """Get or create a connection to ArangoDB.
    
    Reuses existing connection if configuration matches, otherwise creates new one.
    """
    with self._lock:
        if (self._client is None or self._db is None or
            self._config is None or not self._config_matches(cfg)):
            # Close existing connection
            # Create new connection
            self._client = ArangoClient(hosts=cfg.arango_url, ...)
            self._db = self._client.db(cfg.database, ...)
        return self._client, self._db
```

**Analysis:**
- **Single connection reuse**, not a pool of multiple connections
- Config matching logic (lines 75-85) compares: URL, database, username, password, timeout
- **Changing database requires closing existing connection** and creating new one
- No support for maintaining multiple database connections simultaneously

---

## 3. Architecture Review

### 3.1 Connection Management Architecture

**Architectural Pattern:** Singleton + Lifespan Context

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server Process                        │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         server_lifespan() Context Manager          │    │
│  │  • Initialized once at startup                     │    │
│  │  • Loads config from environment                   │    │
│  │  • Creates single db connection                    │    │
│  │  • Yields {"db": db, "client": client}            │    │
│  └────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          ▼                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │         ConnectionManager (Singleton)              │    │
│  │  • _instance: Single instance per process          │    │
│  │  • _client: Single ArangoClient                    │    │
│  │  • _db: Single StandardDatabase                    │    │
│  │  • _config: Single Config                          │    │
│  └────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          ▼                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Request Handlers                       │    │
│  │  • call_tool() retrieves db from lifespan context  │    │
│  │  • All handlers receive same db object             │    │
│  │  • No per-request database selection               │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 MCP Protocol Implementation

**MCP SDK:** `mcp>=1.18.0` (low-level Server API)

**File:** `mcp_arangodb_async/entry.py` (lines 223-484)

**Server Initialization:**
```python
server = Server("mcp-arangodb-async", lifespan=server_lifespan)
```

**Protocol Handlers:**
1. `@server.list_tools()` → `handle_list_tools()` (lines 226-244)
2. `@server.call_tool()` → `call_tool()` (lines 324-420)

**Transport Support:**
- **stdio** (default): `run_stdio()` (lines 465-484)
- **HTTP**: `run_http_server()` in `http_transport.py` (lines 119-179)

### 3.3 Client-Server Interaction Patterns

#### stdio Transport (Desktop Clients)

```
┌──────────────────┐         ┌─────────────────────┐         ┌──────────────┐
│  Claude Desktop  │         │  MCP Server         │         │  ArangoDB    │
│                  │         │  (stdio)            │         │              │
│  1. Launch       │────────▶│  2. Load env vars   │         │              │
│     server       │         │     ARANGO_DB=db1   │         │              │
│                  │         │  3. Connect to db1  │────────▶│  Database    │
│                  │         │                     │         │  "db1"       │
│  4. Call tool    │────────▶│  5. Execute on db1  │────────▶│              │
│                  │◀────────│  6. Return result   │◀────────│              │
│                  │         │                     │         │              │
│  ❌ Cannot       │         │  ❌ Cannot switch   │         │              │
│     switch to    │         │     to db2 without  │         │              │
│     db2          │         │     restart         │         │              │
└──────────────────┘         └─────────────────────┘         └──────────────┘
```

**Limitation:** Each client connection is bound to a single database for the server's lifetime.

#### HTTP Transport (Web Clients)

**File:** `mcp_arangodb_async/http_transport.py` (lines 119-179)

```python
async def run_http_server(...):
    # Manually enter server's lifespan context
    async with server_lifespan(mcp_server) as lifespan_context:
        # Store database in Starlette app.state
        starlette_app.state.db = lifespan_context.get("db")
        # Run server
        await server.serve()
```

**Analysis:**
- Database connection stored in `app.state.db` (line 171)
- **Shared across all HTTP requests**
- No per-session or per-request database selection
- Stateless mode (`MCP_HTTP_STATELESS=true`) still uses same global database

### 3.4 MCP Protocol Multi-Tenancy Capabilities

**Research Finding:** The MCP protocol specification does not define native multi-tenancy or per-request database selection mechanisms.

**Standard MCP Request Structure:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "arango_query",
    "arguments": {
      "query": "FOR doc IN collection RETURN doc"
    }
  }
}
```

**No Database Parameter:** Tool arguments do not include database selection.

**Industry Pattern:** Multi-tenancy in MCP servers is typically implemented through:
1. **Server-level configuration** (current approach)
2. **Custom tool arguments** (e.g., adding `database` parameter to each tool)
3. **Session-based routing** (HTTP transport with session headers)
4. **Separate server instances** (most common for isolation)

---

## 4. Limitations and Constraints

### 4.1 Architectural Barriers to Multi-Tenancy

#### Barrier 1: Singleton Connection Manager

**File:** `mcp_arangodb_async/db.py` (lines 25-39)

**Issue:** The singleton pattern enforces a single connection instance per process.

**Code Location:**
```python
class ConnectionManager:
    _instance: Optional['ConnectionManager'] = None  # Line 28
    
    def __new__(cls) -> 'ConnectionManager':
        if cls._instance is None:  # Line 32
            # ... create single instance ...
```

**Impact:** Cannot maintain multiple database connections simultaneously.

**Refactoring Required:** Replace singleton with connection pool supporting multiple databases.

#### Barrier 2: Global Lifespan Context

**File:** `mcp_arangodb_async/entry.py` (lines 157-221)

**Issue:** Server lifespan yields a single database object shared globally.

**Code Location:**
```python
@asynccontextmanager
async def server_lifespan(server: Server) -> AsyncIterator[Dict[str, Any]]:
    cfg = load_config()  # Line 179 - single config
    # ...
    yield {"db": db, "client": client}  # Line 214 - single db
```

**Impact:** All requests use the same database connection.

**Refactoring Required:** Implement per-request database resolution mechanism.

#### Barrier 3: Static Configuration Loading

**File:** `mcp_arangodb_async/config.py` (lines 45-72)

**Issue:** Configuration loaded once from environment variables at startup.

**Code Location:**
```python
def load_config() -> Config:
    """Load configuration from environment variables."""
    url = os.getenv("ARANGO_URL", "http://localhost:8529")  # Line 55
    db = os.getenv("ARANGO_DB", "_system")  # Line 56
    # ... returns frozen Config dataclass
```

**Impact:** Cannot change database without restarting server.

**Refactoring Required:** Support dynamic configuration sources (e.g., config file with multiple database definitions).

#### Barrier 4: Tool Handler Signature

**File:** `mcp_arangodb_async/handlers.py` (lines 9-13)

**Issue:** Handler signature does not include database parameter.

**Code Location:**
```python
# Handler Signature Patterns:
# Most handlers follow the standard pattern:
#     (db: StandardDatabase, args: Dict[str, Any]) -> Dict[str, Any]
```

**Impact:** Handlers cannot receive database selection from tool arguments.

**Refactoring Required:** Extend handler signature or add database parameter to all tool models.

### 4.2 Security Implications

**Current Design Security Posture:**

✅ **Strengths:**
- **Isolation by process:** Each server instance is isolated
- **No credential leakage:** Single database = single credential set
- **Simple access control:** Environment-based configuration

❌ **Multi-Tenancy Security Concerns (if implemented):**
- **Credential management:** Storing multiple database credentials securely
- **Access control:** Ensuring clients can only access authorized databases
- **Connection pooling:** Preventing connection exhaustion attacks
- **Audit logging:** Tracking which client accessed which database

**Industry Best Practice:** Multi-tenant database proxies typically implement:
1. **Authentication layer:** Verify client identity before database access
2. **Authorization layer:** Map client to allowed databases
3. **Connection limits:** Per-tenant connection quotas
4. **Audit trails:** Log all database access with tenant context

---

## 5. Industry Standards Comparison

### 5.1 ArangoDB Native Multi-Tenancy

**ArangoDB Documentation:** [Databases - Multi-Tenancy](https://docs.arangodb.com/3.13/concepts/data-structure/databases/)

**ArangoDB Capabilities:**
- ✅ Multiple databases per server instance
- ✅ Fully isolated collections per database
- ✅ Per-database access control
- ✅ Single ArangoClient can access multiple databases

**python-arango Library Support:**

```python
from arango import ArangoClient

# Single client, multiple databases
client = ArangoClient(hosts="http://localhost:8529")

# Access different databases
db1 = client.db("tenant1_db", username="user1", password="pass1")
db2 = client.db("tenant2_db", username="user2", password="pass2")
db3 = client.db("tenant3_db", username="user3", password="pass3")

# Execute queries on different databases
results1 = db1.aql.execute("FOR doc IN collection RETURN doc")
results2 = db2.aql.execute("FOR doc IN collection RETURN doc")
```

**Conclusion:** The underlying `python-arango` library **fully supports** multi-database access. The limitation is in the MCP server architecture, not the database driver.

### 5.2 Database Proxy Multi-Tenancy Patterns

**Research Finding:** Common patterns for multi-tenant database proxies:

#### Pattern 1: Separate Server Instances (Current Approach)

**Example:** AWS RDS Proxy with separate proxies per tenant

**Pros:**
- ✅ Strong isolation
- ✅ Simple configuration
- ✅ No cross-tenant contamination risk

**Cons:**
- ❌ Resource overhead (one process per tenant)
- ❌ Complex deployment (multiple server instances)
- ❌ Difficult to scale (N tenants = N processes)

**Current mcp-arangodb-async:** Uses this pattern

#### Pattern 2: Per-Request Database Selection

**Example:** Django multi-tenant with database routers

**Implementation:**
```python
# Middleware extracts tenant from request
def get_database_for_request(request):
    tenant_id = request.headers.get("X-Tenant-ID")
    return f"tenant_{tenant_id}_db"

# Handler uses request-specific database
def handle_request(request):
    db_name = get_database_for_request(request)
    db = client.db(db_name, ...)
    # Execute query on tenant-specific database
```

**Pros:**
- ✅ Single server instance
- ✅ Dynamic tenant routing
- ✅ Efficient resource usage

**Cons:**
- ❌ Complex routing logic
- ❌ Requires authentication/authorization layer
- ❌ Connection pool management complexity

#### Pattern 3: Schema-Based Multi-Tenancy

**Example:** PostgreSQL with schema-per-tenant

**Note:** Not applicable to ArangoDB (uses database-level isolation, not schemas)

#### Pattern 4: Connection Pool Per Tenant

**Example:** AWS RDS Proxy with tenant-aware connection pooling

**Implementation:**
```python
class MultiTenantConnectionManager:
    def __init__(self):
        self._pools = {}  # tenant_id -> connection_pool
    
    def get_connection(self, tenant_id, config):
        if tenant_id not in self._pools:
            self._pools[tenant_id] = create_pool(config)
        return self._pools[tenant_id].get_connection()
```

**Pros:**
- ✅ Efficient connection reuse
- ✅ Per-tenant connection limits
- ✅ Scalable to many tenants

**Cons:**
- ❌ Memory overhead (multiple pools)
- ❌ Complex pool management
- ❌ Requires tenant identification mechanism

### 5.3 MCP Server Multi-Tenancy Examples

**Research Finding:** Limited public examples of multi-tenant MCP servers.

**Common Approaches:**
1. **Separate server instances** (most common)
2. **Tool argument-based selection** (custom implementation)
3. **Session-based routing** (HTTP transport only)

**Example: Tool Argument-Based Selection**

```python
# Hypothetical multi-tenant tool signature
@register_tool(
    name="arango_query",
    description="Execute AQL query on specified database",
    model=QueryArgs
)
def handle_arango_query(db_manager, args):
    database_name = args.get("database", "default")
    db = db_manager.get_database(database_name)
    return list(db.aql.execute(args["query"]))
```

**Pros:**
- ✅ Explicit database selection
- ✅ Backward compatible (default database)

**Cons:**
- ❌ Requires updating all 34 tool signatures
- ❌ Exposes database names to clients
- ❌ No access control enforcement

---

## 6. Recommendations

### 6.1 Multi-Tenancy Implementation Approaches

#### Option A: Enhanced Per-Request Database Selection (Recommended)

**Complexity:** Medium  
**Impact:** Moderate (requires architectural changes)  
**Use Case:** Single server instance serving multiple databases

**Implementation Strategy:**

1. **Add database parameter to tool arguments**
   - Extend all Pydantic models with optional `database: Optional[str]` field
   - Default to environment-configured database for backward compatibility

2. **Replace singleton ConnectionManager with multi-database pool**
   ```python
   class MultiDatabaseConnectionManager:
       def __init__(self):
           self._pools: Dict[str, Tuple[ArangoClient, StandardDatabase]] = {}
           self._lock = threading.Lock()
       
       def get_connection(self, cfg: Config) -> Tuple[ArangoClient, StandardDatabase]:
           key = f"{cfg.arango_url}:{cfg.database}:{cfg.username}"
           with self._lock:
               if key not in self._pools:
                   self._pools[key] = create_connection(cfg)
               return self._pools[key]
   ```

3. **Implement database resolution in call_tool()**
   ```python
   @server.call_tool()
   async def call_tool(name: str, arguments: Dict[str, Any]):
       # Extract database from arguments or use default
       database_name = arguments.pop("database", None) or default_database
       
       # Build config for requested database
       cfg = build_config(database_name)
       
       # Get database-specific connection
       client, db = connection_manager.get_connection(cfg)
       
       # Execute tool
       result = handler(db, arguments)
       return result
   ```

4. **Add configuration file support**
   ```yaml
   # config.yaml
   databases:
     default:
       url: http://localhost:8529
       database: default_db
       username: user1
       password: pass1
     tenant1:
       url: http://localhost:8529
       database: tenant1_db
       username: tenant1_user
       password: tenant1_pass
     tenant2:
       url: http://localhost:8529
       database: tenant2_db
       username: tenant2_user
       password: tenant2_pass
   ```

**Pros:**
- ✅ Single server instance
- ✅ Flexible database selection
- ✅ Backward compatible (optional parameter)
- ✅ Leverages python-arango multi-database support

**Cons:**
- ❌ Requires updating all 34 tool models
- ❌ Credential management complexity
- ❌ No built-in access control

**Estimated Effort:** 2-3 weeks

#### Option B: HTTP Session-Based Routing

**Complexity:** High  
**Impact:** High (HTTP transport only)  
**Use Case:** Web applications with session management

**Implementation Strategy:**

1. **Add session middleware to HTTP transport**
   ```python
   class TenantSessionMiddleware:
       async def __call__(self, request):
           tenant_id = request.headers.get("X-Tenant-ID")
           database_name = resolve_tenant_database(tenant_id)
           request.state.database = database_name
           return await self.app(request)
   ```

2. **Modify call_tool() to use request state**
   ```python
   @server.call_tool()
   async def call_tool(name: str, arguments: Dict[str, Any]):
       # Access request-specific database from session
       database_name = request.state.database
       cfg = build_config(database_name)
       client, db = connection_manager.get_connection(cfg)
       # ...
   ```

**Pros:**
- ✅ No tool signature changes
- ✅ Transparent to clients
- ✅ Session-based isolation

**Cons:**
- ❌ HTTP transport only (not stdio)
- ❌ Requires authentication layer
- ❌ Complex session management
- ❌ Not compatible with desktop clients (Claude, Augment)

**Estimated Effort:** 3-4 weeks

#### Option C: Separate Server Instances (Current Approach - No Changes)

**Complexity:** Low  
**Impact:** None (status quo)  
**Use Case:** Strong tenant isolation requirements

**Implementation:** Already implemented

**Deployment Pattern:**
```json
// Claude Desktop config with multiple databases
{
  "mcpServers": {
    "arangodb_tenant1": {
      "command": "python",
      "args": ["-m", "mcp_arangodb_async"],
      "env": {
        "ARANGO_DB": "tenant1_db",
        "ARANGO_USERNAME": "tenant1_user",
        "ARANGO_PASSWORD": "tenant1_pass"
      }
    },
    "arangodb_tenant2": {
      "command": "python",
      "args": ["-m", "mcp_arangodb_async"],
      "env": {
        "ARANGO_DB": "tenant2_db",
        "ARANGO_USERNAME": "tenant2_user",
        "ARANGO_PASSWORD": "tenant2_pass"
      }
    }
  }
}
```

**Pros:**
- ✅ No code changes required
- ✅ Strong process-level isolation
- ✅ Simple configuration
- ✅ Works with all transports

**Cons:**
- ❌ Resource overhead (N processes)
- ❌ Complex deployment
- ❌ Difficult to scale

**Estimated Effort:** 0 (already implemented)

### 6.2 Recommended Approach

**Primary Recommendation: Option A (Enhanced Per-Request Database Selection)**

**Rationale:**
1. **Flexibility:** Supports both single-database and multi-database use cases
2. **Backward Compatibility:** Optional database parameter preserves existing behavior
3. **Scalability:** Single server instance reduces resource overhead
4. **Leverages Existing Capabilities:** python-arango already supports multi-database access

**Implementation Phases:**

**Phase 1: Core Infrastructure (Week 1-2)**
- Replace singleton ConnectionManager with MultiDatabaseConnectionManager
- Add configuration file support (YAML/JSON)
- Implement database resolution logic in call_tool()

**Phase 2: Tool Model Updates (Week 2-3)**
- Add optional `database: Optional[str]` field to all 34 Pydantic models
- Update tool descriptions to document database parameter
- Maintain backward compatibility with default database

**Phase 3: Testing & Documentation (Week 3)**
- Comprehensive testing with multiple databases
- Update documentation with multi-tenancy examples
- Security review and credential management guidelines

**Secondary Recommendation: Option C (Status Quo) for Simple Use Cases**

For users with:
- Small number of databases (1-3)
- Strong isolation requirements
- Desktop client usage (stdio transport)

**Recommendation:** Continue using separate server instances. This approach is simple, secure, and well-supported by the current architecture.

### 6.3 Configuration Mechanism Recommendations

**Recommended Configuration Hierarchy:**

1. **Tool arguments** (highest priority) - Per-request database selection
2. **Configuration file** (medium priority) - Multi-database definitions
3. **Environment variables** (lowest priority) - Default database fallback

**Example Configuration File:**

```yaml
# mcp_arangodb_config.yaml
default_database: production

databases:
  production:
    url: http://localhost:8529
    database: prod_db
    username: prod_user
    password: ${PROD_DB_PASSWORD}  # Environment variable reference
    timeout: 30.0
  
  staging:
    url: http://localhost:8529
    database: staging_db
    username: staging_user
    password: ${STAGING_DB_PASSWORD}
    timeout: 30.0
  
  development:
    url: http://localhost:8529
    database: dev_db
    username: dev_user
    password: ${DEV_DB_PASSWORD}
    timeout: 30.0

# Optional: Access control
access_control:
  enabled: false  # Future enhancement
  rules:
    - client: "claude_desktop"
      allowed_databases: ["production", "staging"]
    - client: "web_client"
      allowed_databases: ["development"]
```

**Benefits:**
- ✅ Centralized configuration
- ✅ Environment variable support for secrets
- ✅ Clear database definitions
- ✅ Future-proof for access control

---

## 7. Conclusion

The current mcp-arangodb-async implementation is **single-tenant by design**, with database selection fixed at server startup via environment variables. While this approach provides strong isolation and simplicity, it limits flexibility for multi-database use cases.

**Key Takeaways:**

1. **Port Configuration:** ✅ Exists via `ARANGO_URL` environment variable
2. **Multi-Tenancy:** ❌ Not supported - requires architectural changes
3. **Database Selection:** Globally fixed (server-level), not per-request or per-connection
4. **Underlying Library:** python-arango fully supports multi-database access
5. **Architectural Barriers:** Singleton ConnectionManager, global lifespan context, static configuration

**Recommended Path Forward:**

- **Short-term:** Use separate server instances for multi-database scenarios (Option C)
- **Long-term:** Implement per-request database selection with configuration file support (Option A)

**Next Steps:**

1. User validation of analysis findings
2. Decision on multi-tenancy implementation approach
3. If proceeding with Option A: Phase 2 test definition report
4. If maintaining Option C: Document multi-instance deployment patterns

---

**Report Version:** v0  
**Last Updated:** 2025-11-08  
**Status:** Ready for User Review

