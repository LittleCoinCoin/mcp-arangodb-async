# Multi-Tenancy Architectural Analysis for mcp-arangodb-async

**Project:** mcp-arangodb-async  
**Version:** 0.3.2  
**Analysis Date:** 2025-11-08  
**Analyst:** Augment Agent  
**Status:** Phase 1 - Architectural Analysis (v2)

---

## Changes from v1

### Major Corrections and Clarifications

1. **CLI Framework Correction**
   - **Issue**: v1 incorrectly recommended `click` library for CLI implementation
   - **Correction**: Use `argparse` (Python standard library) - already used in codebase at `mcp_arangodb_async/__main__.py:15`
   - **Rationale**: Consistency with existing codebase, no new dependencies, familiar API
   - **Impact**: All CLI code examples updated to use `argparse.ArgumentParser` instead of `@click.command()` decorators

2. **Multi-Server Capability Clarification**
   - **Issue**: v1 focused primarily on multiple databases on a single ArangoDB server
   - **Clarification**: The YAML config `url` field supports **multiple ArangoDB server instances** (different URLs/hosts), not just multiple databases on one server
   - **New Content**: Added Section 1.3 "Multi-Server Deployment Scenarios" with three detailed examples:
     - Scenario 1: Multiple databases on single server (multi-tenant SaaS)
     - Scenario 2: Multiple ArangoDB server instances (geo-distributed, enterprise)
     - Scenario 3: Hybrid - multiple servers + multiple databases per server
   - **Impact**: Architecture supports geo-distributed deployments, environment separation (prod/staging/analytics), and complex enterprise topologies

3. **Configuration Priority Hierarchy Expansion**
   - **Issue**: v1 had incomplete configuration priority explanation
   - **Enhancement**: Expanded Section 6.3 with detailed 6-level configuration priority system:
     - **Level 1**: Tool argument `database` parameter (per-call override)
     - **Level 2**: Session focused database (`set_focused_database()`)
     - **Level 3**: Config file `default_database` setting
     - **Level 4**: Environment variable `MCP_DEFAULT_DATABASE`
     - **Level 5**: Environment variables (ARANGO_URL, ARANGO_DB, etc.) for backward compatibility
     - **Level 6**: Hardcoded defaults (_system database on localhost:8529)
   - **Impact**: Clear resolution algorithm for database selection in all scenarios

4. **Environment Variable Integration Examples**
   - **New Content**: Added Section 1.4 "Configuration Integration Scenarios" with concrete examples:
     - **Scenario A**: Simple single-database (env vars only, backward compatible)
     - **Scenario B**: Multi-database (config file + env vars for passwords)
     - **Scenario C**: Override default database via env var
   - **Impact**: Demonstrates how CLI/config file/env vars work together, clarifies backward compatibility

### Minor Updates

- Updated all code examples to use `argparse` instead of `click`
- Added connection pool architecture for multi-server support
- Enhanced security considerations for multi-server credential management
- Clarified that each database config can point to different ArangoDB server instances

---

## Executive Summary

The current mcp-arangodb-async implementation **does not support multi-tenancy** for database access. The architecture is designed for **single-database, single-tenant operation** with configuration loaded exclusively from environment variables at server startup. Database context is established globally during server initialization and remains fixed for the server's lifetime.

**Key Findings:**
- ⚠️ Port configuration embedded in `ARANGO_URL` (no separate `ARANGO_PORT` variable)
- ❌ No multi-database support - single database per server instance
- ❌ No per-request or per-connection database selection
- ❌ Configuration is static (startup-time only), not dynamic
- ❌ Global singleton connection manager enforces single-database constraint

**Stakeholder Requirement:** Multi-tenancy MUST be implemented within a single MCP server instance to avoid context window pollution in LLM-based agent systems.

**Multi-Server Capability:** The proposed solution supports **multiple ArangoDB server instances** (different URLs/hosts), not just multiple databases on one server. This enables geo-distributed deployments, environment separation, and complex enterprise architectures.

**Impact:** Current architecture requires complete redesign to support multiple databases and multiple servers within one MCP server instance.

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

**Port Configuration Clarification:**

⚠️ **Important**: There is **no separate `ARANGO_PORT` environment variable**. The port is embedded within the `ARANGO_URL` parameter.

**Examples:**
- Default: `ARANGO_URL=http://localhost:8529` (port 8529)
- Custom port: `ARANGO_URL=http://localhost:8530` (port 8530)
- Remote server: `ARANGO_URL=http://arango.example.com:8529`
- HTTPS: `ARANGO_URL=https://arango.example.com:443`

**Docker Deployment Context:**

In Docker deployments, port configuration is managed via `docker-compose.yml` port mapping, not environment variables:

```yaml
# docker-compose.yml
services:
  mcp-server:
    environment:
      ARANGO_URL: http://arangodb:8529  # Internal Docker network
    ports:
      - "8000:8000"  # MCP HTTP port mapping
  
  arangodb:
    ports:
      - "8529:8529"  # ArangoDB port mapping
```

**Multi-Tenancy Implication:**

To support multiple ArangoDB server instances (different ports or hosts), the configuration must allow specifying different `ARANGO_URL` values for each database. This requires moving beyond environment variables to a configuration file or runtime configuration mechanism.

### 1.3 Multi-Server Deployment Scenarios

The proposed YAML configuration with `url` field supports **multiple ArangoDB server instances**, enabling three deployment scenarios:

#### Scenario 1: Multiple Databases on Single ArangoDB Server

**Use Case:** Multi-tenant SaaS where each tenant has isolated database on shared ArangoDB server.

```yaml
# ~/.mcp-arangodb-async/config.yaml
version: "1.0"
default_database: tenant1

databases:
  tenant1:
    url: http://localhost:8529        # Same server
    database: tenant1_db              # Different database
    username: tenant1_user
    password_env: TENANT1_PASSWORD
    timeout: 30.0
  
  tenant2:
    url: http://localhost:8529        # Same server
    database: tenant2_db              # Different database
    username: tenant2_user
    password_env: TENANT2_PASSWORD
    timeout: 30.0
  
  tenant3:
    url: http://localhost:8529        # Same server
    database: tenant3_db              # Different database
    username: tenant3_user
    password_env: TENANT3_PASSWORD
    timeout: 30.0
```

**Architecture:**
```
┌─────────────────────────────────────┐
│   MCP Server (Single Instance)     │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ MultiDatabaseConnectionMgr   │  │
│  │                              │  │
│  │  Connection Pool:            │  │
│  │  ├─ tenant1 → (client, db)   │  │
│  │  ├─ tenant2 → (client, db)   │  │
│  │  └─ tenant3 → (client, db)   │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
                 │
                 ▼
    ┌────────────────────────┐
    │  ArangoDB Server       │
    │  localhost:8529        │
    │                        │
    │  ├─ tenant1_db         │
    │  ├─ tenant2_db         │
    │  └─ tenant3_db         │
    └────────────────────────┘
```

**Benefits:**
- ✅ Resource efficiency (single ArangoDB instance)
- ✅ Simple deployment and maintenance
- ✅ Database-level isolation for tenants

**Limitations:**
- ⚠️ Shared server resources (CPU, memory, I/O)
- ⚠️ Single point of failure
- ⚠️ No geographic distribution

---

#### Scenario 2: Multiple ArangoDB Server Instances (Geo-Distributed)

**Use Case:** Enterprise deployments with regional ArangoDB clusters for data locality and compliance (GDPR, data residency requirements).

```yaml
# ~/.mcp-arangodb-async/config.yaml
version: "1.0"
default_database: us_east

databases:
  us_east:
    url: http://arango-us-east.example.com:8529    # US East server
    database: production
    username: app_user
    password_env: US_EAST_PASSWORD
    timeout: 30.0
    description: "US East production database"
  
  eu_west:
    url: http://arango-eu-west.example.com:8529    # EU West server
    database: production
    username: app_user
    password_env: EU_WEST_PASSWORD
    timeout: 30.0
    description: "EU West production database (GDPR compliant)"
  
  asia_pacific:
    url: http://arango-apac.example.com:8530       # APAC server (different port)
    database: production
    username: app_user
    password_env: APAC_PASSWORD
    timeout: 30.0
    description: "Asia Pacific production database"
```

**Architecture:**
```
┌─────────────────────────────────────────────────────────┐
│         MCP Server (Single Instance)                    │
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │ MultiDatabaseConnectionManager                    │  │
│  │                                                   │  │
│  │  Connection Pool:                                │  │
│  │  ├─ us_east → (client_us, db_us)                 │  │
│  │  ├─ eu_west → (client_eu, db_eu)                 │  │
│  │  └─ asia_pacific → (client_apac, db_apac)        │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
  │ ArangoDB     │    │ ArangoDB     │    │ ArangoDB     │
  │ US East      │    │ EU West      │    │ APAC         │
  │ :8529        │    │ :8529        │    │ :8530        │
  │              │    │              │    │              │
  │ production   │    │ production   │    │ production   │
  └──────────────┘    └──────────────┘    └──────────────┘
```

**Benefits:**
- ✅ Geographic distribution (low latency for regional users)
- ✅ Data residency compliance (GDPR, data sovereignty)
- ✅ Fault isolation (regional outages don't affect other regions)
- ✅ Independent scaling per region

**Use Cases:**
- Global SaaS applications with regional data requirements
- Compliance-driven architectures (GDPR, CCPA, data localization laws)
- Disaster recovery and business continuity

---

#### Scenario 3: Hybrid - Multiple Servers + Multiple Databases

**Use Case:** Complex enterprise deployment with production/staging/analytics/development environments across multiple servers.

```yaml
# ~/.mcp-arangodb-async/config.yaml
version: "1.0"
default_database: prod_primary

databases:
  # Production cluster (primary)
  prod_primary:
    url: http://arango-prod-1.example.com:8529
    database: production
    username: prod_user
    password_env: PROD_PASSWORD
    timeout: 30.0
    description: "Production primary database"
  
  # Production cluster (replica for read-only queries)
  prod_replica:
    url: http://arango-prod-2.example.com:8529
    database: production
    username: readonly_user
    password_env: PROD_READONLY_PASSWORD
    timeout: 30.0
    description: "Production read replica"
  
  # Staging environment (separate server)
  staging:
    url: http://arango-staging.example.com:8529
    database: staging
    username: staging_user
    password_env: STAGING_PASSWORD
    timeout: 30.0
    description: "Staging environment"
  
  # Analytics database (separate server, different port)
  analytics:
    url: http://arango-analytics.example.com:8530
    database: analytics_db
    username: analytics_user
    password_env: ANALYTICS_PASSWORD
    timeout: 60.0
    description: "Analytics and reporting database"
  
  # Local development (localhost)
  development:
    url: http://localhost:8529
    database: dev_db
    username: root
    password_env: DEV_PASSWORD
    timeout: 30.0
    description: "Local development database"
```

**Architecture:**
```
┌──────────────────────────────────────────────────────────────────┐
│              MCP Server (Single Instance)                        │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ MultiDatabaseConnectionManager                             │ │
│  │                                                            │ │
│  │  Connection Pool:                                         │ │
│  │  ├─ prod_primary → (client_prod1, db_prod1)               │ │
│  │  ├─ prod_replica → (client_prod2, db_prod2)               │ │
│  │  ├─ staging → (client_staging, db_staging)                │ │
│  │  ├─ analytics → (client_analytics, db_analytics)          │ │
│  │  └─ development → (client_dev, db_dev)                    │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
     │           │           │              │              │
     ▼           ▼           ▼              ▼              ▼
┌─────────┐ ┌─────────┐ ┌─────────┐  ┌──────────┐  ┌──────────┐
│ Prod-1  │ │ Prod-2  │ │ Staging │  │Analytics │  │  Local   │
│ :8529   │ │ :8529   │ │ :8529   │  │ :8530    │  │ :8529    │
│         │ │         │ │         │  │          │  │          │
│ prod db │ │ prod db │ │ stg db  │  │ anly db  │  │ dev db   │
│ (R/W)   │ │ (R/O)   │ │         │  │          │  │          │
└─────────┘ └─────────┘ └─────────┘  └──────────┘  └──────────┘
```

**Benefits:**
- ✅ Environment isolation (prod/staging/dev on separate servers)
- ✅ Read/write separation (primary + replica for query offloading)
- ✅ Specialized workloads (analytics server with different configuration)
- ✅ Flexible development workflow (local + remote databases)

**LLM Agent Workflow Examples:**

```python
# Example 1: Geo-distributed query
set_focused_database("us_east")
results_us = arango_query("FOR doc IN users RETURN doc")

set_focused_database("eu_west")
results_eu = arango_query("FOR doc IN users RETURN doc")

# Combine results from multiple regions
combined = merge(results_us, results_eu)

# Example 2: Production + Analytics
set_focused_database("prod_primary")
recent_orders = arango_query("FOR o IN orders FILTER o.created > @date RETURN o", 
                             bind_vars={"date": "2025-01-01"})

set_focused_database("analytics")
arango_create_document(collection="daily_reports", 
                       document={"date": "2025-01-08", "orders": recent_orders})

# Example 3: Cross-database join (override pattern)
set_focused_database("production")
users = arango_query("FOR u IN users RETURN u")

# Override focused context for one-off query
analytics = arango_query("FOR a IN user_analytics RETURN a", 
                         database="analytics")

combined = join(users, analytics)
```

### 1.4 Configuration Integration Scenarios

This section demonstrates how the proposed CLI/config file/environment variable system works together, addressing the stakeholder question: "How does this integrate/supersede the current environment variables way of setting up the MCP server?"

**Answer:** The CLI **complements** environment variables, it doesn't supersede them. Environment variables remain the simplest path for single-database setups. Config file is optional and only needed for multi-database scenarios.

---

#### Scenario A: Simple Single-Database Setup (Backward Compatible)

**Use Case:** Existing deployments with single database, no config file needed.

**Configuration:**
```bash
# User sets environment variables (existing workflow)
export ARANGO_URL=http://localhost:8529
export ARANGO_DB=my_database
export ARANGO_USERNAME=my_user
export ARANGO_PASSWORD=my_password

# Start server (no config file needed)
mcp-arangodb-async
```

**Result:** Server uses environment variables, no config file required. **100% backward compatible with existing deployments.**

**Configuration Priority:**
```
Level 5: Environment variables (ARANGO_URL, ARANGO_DB, etc.)
  ↓
Level 6: Hardcoded defaults (_system on localhost:8529)
```

**No changes required for existing users.**

---

#### Scenario B: Multi-Database Setup (New Capability)

**Use Case:** Multi-tenant deployment with multiple databases, config file required.

**Step 1: Admin creates config file using CLI**

```bash
# Add production database
mcp-arangodb-async config add \
  --name production \
  --url http://localhost:8529 \
  --database prod_db \
  --username prod_user \
  --password-env PROD_DB_PASSWORD \
  --description "Production database"

# Add staging database
mcp-arangodb-async config add \
  --name staging \
  --url http://localhost:8529 \
  --database staging_db \
  --username staging_user \
  --password-env STAGING_DB_PASSWORD \
  --description "Staging database"

# Add analytics database (different server)
mcp-arangodb-async config add \
  --name analytics \
  --url http://analytics.example.com:8530 \
  --database analytics_db \
  --username analytics_user \
  --password-env ANALYTICS_DB_PASSWORD \
  --timeout 60.0 \
  --description "Analytics database"
```

**Generated Config File:**
```yaml
# ~/.mcp-arangodb-async/config.yaml
version: "1.0"
default_database: production

databases:
  production:
    url: http://localhost:8529
    database: prod_db
    username: prod_user
    password_env: PROD_DB_PASSWORD
    timeout: 30.0
    description: "Production database"
  
  staging:
    url: http://localhost:8529
    database: staging_db
    username: staging_user
    password_env: STAGING_DB_PASSWORD
    timeout: 30.0
    description: "Staging database"
  
  analytics:
    url: http://analytics.example.com:8530
    database: analytics_db
    username: analytics_user
    password_env: ANALYTICS_DB_PASSWORD
    timeout: 60.0
    description: "Analytics database"
```

**Step 2: Set password environment variables**

```bash
# Passwords stored in environment variables, NOT in config file
export PROD_DB_PASSWORD=prod_secret
export STAGING_DB_PASSWORD=staging_secret
export ANALYTICS_DB_PASSWORD=analytics_secret
```

**Step 3: Start server**

```bash
mcp-arangodb-async
```

**Step 4: LLM agent sets focused database**

```python
# Via MCP tool call
set_focused_database("production")

# All subsequent operations use production database
arango_query("FOR doc IN users RETURN doc")
arango_create_document(collection="orders", document={...})

# Switch to staging
set_focused_database("staging")

# Now all operations use staging database
arango_query("FOR doc IN users RETURN doc")
```

**Configuration Priority:**
```
Level 2: Session focused database (set_focused_database("production"))
  ↓
Level 3: Config file default_database setting
  ↓
Level 5: Environment variables (fallback if no config file)
```

---

#### Scenario C: Override Default Database via Environment Variable

**Use Case:** Temporarily change default database without editing config file.

**Config File:**
```yaml
# ~/.mcp-arangodb-async/config.yaml
version: "1.0"
default_database: production  # Default from config file

databases:
  production: {...}
  staging: {...}
  development: {...}
```

**Override via Environment Variable:**
```bash
# Override default database
export MCP_DEFAULT_DATABASE=staging

# Start server
mcp-arangodb-async
```

**Result:** Server uses `staging` as default instead of `production`.

**Configuration Priority:**
```
Level 4: Environment variable MCP_DEFAULT_DATABASE (overrides config file)
  ↓
Level 3: Config file default_database setting
```

**Use Cases:**
- Testing with different default database
- CI/CD pipelines with environment-specific defaults
- Temporary overrides without editing config file

---

### Configuration Priority Summary

| Level | Source | Purpose | Example |
|-------|--------|---------|---------|
| **1** | Tool argument `database` parameter | Per-call override | `arango_query(..., database="analytics")` |
| **2** | Session focused database | Persistent context | `set_focused_database("production")` |
| **3** | Config file `default_database` | Default for multi-database | `default_database: production` |
| **4** | Environment variable `MCP_DEFAULT_DATABASE` | Override config file default | `export MCP_DEFAULT_DATABASE=staging` |
| **5** | Environment variables (ARANGO_*) | Backward compatibility | `export ARANGO_DB=my_database` |
| **6** | Hardcoded defaults | Last resort fallback | `_system` on `localhost:8529` |

**Resolution Algorithm:**
```
1. Check tool call for explicit `database` parameter → Use it (Level 1)
2. Check session context for focused database → Use it (Level 2)
3. Check config file for default_database → Use it (Level 3)
4. Check MCP_DEFAULT_DATABASE env var → Use it (Level 4)
5. Check ARANGO_DB env var → Use it (Level 5)
6. Use hardcoded default: "_system" (Level 6)
```

---

## 2. Multi-Tenancy Assessment

### 2.1 Current Multi-Tenancy Support

**Assessment:** ❌ **NOT SUPPORTED**

The current implementation is designed for **single-database, single-tenant operation**. There is no mechanism for:
- Selecting different databases per request
- Maintaining multiple database connections
- Dynamic database configuration
- Per-session database context

### 2.2 Evidence of Single-Tenant Design

#### Evidence 1: Singleton Connection Manager

**File:** `mcp_arangodb_async/db.py` (lines 25-39)

<augment_code_snippet path="mcp_arangodb_async/db.py" mode="EXCERPT">
````python
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
````
</augment_code_snippet>

**Analysis:** The singleton pattern enforces exactly one connection instance per process. Cannot maintain multiple database connections simultaneously.

#### Evidence 2: Global Lifespan Context

**File:** `mcp_arangodb_async/entry.py` (lines 157-221)

<augment_code_snippet path="mcp_arangodb_async/entry.py" mode="EXCERPT">
````python
@asynccontextmanager
async def server_lifespan(server: Server) -> AsyncIterator[Dict[str, Any]]:
    cfg = load_config()  # Single config loaded once
    # ...
    yield {"db": db, "client": client}  # Single db object shared globally
````
</augment_code_snippet>

**Analysis:** Server lifespan yields a single database object that is shared globally across all requests. No per-request or per-session database selection.

#### Evidence 3: Static Configuration

**File:** `mcp_arangodb_async/config.py` (lines 45-72)

<augment_code_snippet path="mcp_arangodb_async/config.py" mode="EXCERPT">
````python
def load_config() -> Config:
    """Load configuration from environment variables."""
    url = os.getenv("ARANGO_URL", "http://localhost:8529")
    db = os.getenv("ARANGO_DB", "_system")
    user = os.getenv("ARANGO_USERNAME", os.getenv("ARANGO_USER", "root"))
    pwd = os.getenv("ARANGO_PASSWORD", os.getenv("ARANGO_PASS", ""))
    # ... returns frozen Config dataclass
````
</augment_code_snippet>

**Analysis:** Configuration loaded once from environment variables at startup. Cannot change database without restarting server.

#### Evidence 4: Tool Handler Signature

**File:** `mcp_arangodb_async/handlers.py` (lines 9-13)

**Handler Signature Pattern:**
```python
# All handlers follow this signature:
(db: StandardDatabase, args: Dict[str, Any]) -> Dict[str, Any]
```

**Analysis:** Handlers receive a single `db` object from global context. No database parameter in handler signatures.

### 2.3 Multi-Tenancy Requirements

Based on stakeholder feedback, the multi-tenancy solution MUST:

1. ✅ **Single MCP server instance** - Avoid context window pollution (34 tools × N instances)
2. ✅ **Multiple databases** - Support multiple databases within one server
3. ✅ **Multiple servers** - Support multiple ArangoDB server instances (different URLs)
4. ✅ **Focused database context** - Set database once, work within it (natural LLM workflow)
5. ✅ **Optional override** - Per-tool database parameter for cross-database operations
6. ✅ **Backward compatible** - Existing single-database deployments continue to work
7. ✅ **Secure configuration** - No credential exposure to LLM agents

---

## 3. Architecture Review

### 3.1 Current Architecture

**High-Level Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server Process                        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Server Lifespan (entry.py:157-221)                     │ │
│  │                                                        │ │
│  │  1. Load config from environment variables            │ │
│  │  2. Create single ArangoClient                        │ │
│  │  3. Connect to single database                        │ │
│  │  4. Yield {"db": db, "client": client}                │ │
│  │                                                        │ │
│  │  Global Context: Single database for all requests     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Tool Handlers (handlers.py)                            │ │
│  │                                                        │ │
│  │  • All handlers receive same db object                │ │
│  │  • No database selection mechanism                    │ │
│  │  • Execute on global database                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ ConnectionManager (db.py:25-99)                        │ │
│  │                                                        │ │
│  │  Singleton Pattern:                                   │ │
│  │  • _client: Single ArangoClient                       │ │
│  │  • _db: Single StandardDatabase                       │ │
│  │  • _config: Single Config                             │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
            ┌────────────────────────┐
            │  ArangoDB Server       │
            │  (Single Instance)     │
            │                        │
            │  Single Database       │
            └────────────────────────┘
```

**Key Characteristics:**
- ❌ Single database connection per server instance
- ❌ Global database context (no per-request selection)
- ❌ Static configuration (startup-time only)
- ❌ Singleton connection manager (cannot support multiple databases)

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
- **stdio** (default): `run_stdio()` (lines 465-484) - Desktop AI clients (Claude Desktop, Augment Code)
- **HTTP**: `run_http_server()` in `http_transport.py` (lines 119-179) - Web applications, containerized deployments

**Session Management Considerations:**

**stdio Transport:**
- Single persistent connection per client
- Session context can be stored in server memory (keyed by connection ID)
- Focused database persists for entire client session

**HTTP Transport:**
- Stateless mode: No session persistence (requires database parameter in every call)
- Stateful mode: Session cookies or headers for session identification
- Focused database stored in session state

---

## 4. Limitations and Constraints

### 4.1 Architectural Barriers to Multi-Tenancy

#### Barrier 1: Singleton Connection Manager

**File:** `mcp_arangodb_async/db.py` (lines 25-39)

**Issue:** The singleton pattern enforces a single connection instance per process.

**Impact:** Cannot maintain multiple database connections simultaneously.

**Refactoring Required:** Replace singleton with connection pool supporting multiple databases and multiple servers.

#### Barrier 2: Global Lifespan Context

**File:** `mcp_arangodb_async/entry.py` (lines 157-221)

**Issue:** Server lifespan yields a single database object shared globally.

**Impact:** All requests use the same database connection.

**Refactoring Required:** Implement per-session database resolution mechanism with focused context support.

#### Barrier 3: Static Configuration Loading

**File:** `mcp_arangodb_async/config.py` (lines 45-72)

**Issue:** Configuration loaded once from environment variables at startup.

**Impact:** Cannot change database without restarting server.

**Refactoring Required:** Support dynamic configuration sources (YAML config file with multiple database definitions).

#### Barrier 4: Tool Handler Signature

**File:** `mcp_arangodb_async/handlers.py` (lines 9-13)

**Issue:** Handler signature does not include database parameter.

**Impact:** Handlers cannot receive database selection from tool arguments.

**Refactoring Required:** Add optional `database` parameter to all 34 tool models (Pydantic models).

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
- **Configuration CRUD security:** Who can add/remove/modify database configurations?

**Industry Best Practice:** Multi-tenant database proxies typically implement:
1. **Authentication layer:** Verify client identity before database access
2. **Authorization layer:** Map client to allowed databases
3. **Connection limits:** Per-tenant connection quotas
4. **Audit trails:** Log all database access with tenant context
5. **Secure credential storage:** Encrypted configuration files or secret management systems

**Critical Security Question for Configuration Management:**

Should database configuration CRUD operations be:
- **Exposed to LLM agents** via MCP tools? (High risk, high flexibility)
- **Restricted to administrators** via separate CLI? (Low risk, lower flexibility)

See Section 6.2 for detailed evaluation.

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

**Multi-Server Support:**

```python
# Multiple ArangoDB server instances
client_us = ArangoClient(hosts="http://arango-us.example.com:8529")
client_eu = ArangoClient(hosts="http://arango-eu.example.com:8529")

db_us = client_us.db("production", username="user", password="pass")
db_eu = client_eu.db("production", username="user", password="pass")

# Execute queries on different servers
results_us = db_us.aql.execute("FOR doc IN users RETURN doc")
results_eu = db_eu.aql.execute("FOR doc IN users RETURN doc")
```

**Conclusion:** The underlying `python-arango` library **fully supports** multi-database and multi-server access. The limitation is in the MCP server architecture, not the database driver.

### 5.2 Database Proxy Multi-Tenancy Patterns

**Research Finding:** Common patterns for multi-tenant database proxies:

#### Pattern 1: Per-Request Database Selection

**Example:** Django multi-tenant with database routers

**Pros:**
- ✅ Single server instance
- ✅ Dynamic tenant routing
- ✅ Efficient resource usage

**Cons:**
- ❌ Complex routing logic
- ❌ Requires authentication/authorization layer
- ❌ Database parameter required in every request (context pollution)

#### Pattern 2: Session-Based Database Context (⭐ RECOMMENDED)

**Example:** PostgreSQL connection pooling with schema-per-tenant

**Implementation:**
```python
# Set session context once
session.set_search_path(f"tenant_{tenant_id}")

# All subsequent queries use tenant schema
result = session.execute("SELECT * FROM users")  # Uses tenant schema
```

**Pros:**
- ✅ Single server instance
- ✅ No repeated database parameter in every call
- ✅ Natural workflow (set context, then work)

**Cons:**
- ❌ Requires session management
- ❌ Stateful (not compatible with stateless HTTP)

**This is the pattern recommended for Option A-Enhanced.**

#### Pattern 3: Connection Pool Per Tenant

**Example:** AWS RDS Proxy with tenant-aware connection pooling

**Pros:**
- ✅ Efficient connection reuse
- ✅ Per-tenant connection limits
- ✅ Scalable to many tenants

**Cons:**
- ❌ Memory overhead (multiple pools)
- ❌ Complex pool management

---

## 6. Recommendations

### 6.1 Multi-Tenancy Implementation Approaches

#### Option A-Enhanced: Focused Database Context with Optional Override (⭐ RECOMMENDED)

**Complexity:** Medium-High
**Impact:** Moderate (requires architectural changes)
**Use Case:** Single server instance serving multiple databases/servers with natural LLM agent workflow
**Estimated Effort:** 4-5 weeks

**Core Concept:**

Combine **persistent session context** with **optional per-tool override** to eliminate context pollution while maintaining flexibility.

**Workflow:**
1. LLM agent sets focused database once: `set_focused_database("production")`
2. All subsequent tool calls operate on `production` without repeating database parameter
3. Optional override for cross-database operations: `arango_query(query="...", database="analytics")`
4. Switch context when needed: `set_focused_database("staging")`

**Implementation Components:**

**1. SessionContextManager** - Manages per-session focused database
**2. MultiDatabaseConnectionManager** - Connection pool for multiple databases/servers
**3. ConfigFileLoader** - YAML config file parsing and validation
**4. New MCP Tools:**
   - `set_focused_database(database_name)` - Set focused database
   - `get_focused_database()` - Get current focused database
   - `list_available_databases()` - List configured databases
**5. Updated Tool Models** - Optional `database` parameter in all 34 tools

**Benefits:**
- ✅ Single server instance (no context window pollution)
- ✅ Natural LLM agent workflow (set context once, work within it)
- ✅ No repeated database parameter (eliminates context pollution)
- ✅ Flexible cross-database operations (optional override)
- ✅ Supports multiple ArangoDB server instances (geo-distributed, enterprise)
- ✅ Backward compatible (default database fallback)

**Comparison with Original Option A:**

| Aspect | Original Option A | Option A-Enhanced |
|--------|------------------|-------------------|
| Database parameter | Required in every call | Optional (only for override) |
| Context pollution | High (34 params × N calls) | Low (set once per session) |
| LLM agent workflow | Repetitive | Natural |
| Multi-server support | Yes | Yes |
| Implementation complexity | Medium | Medium-High |
| Estimated effort | 2-3 weeks | 4-5 weeks |

### 6.2 Configuration Management Approaches

**Critical Question:** How should database configuration CRUD operations be handled?

#### Approach 3A: MCP Tools for Database Configuration (⚠️ NOT RECOMMENDED)

**Concept:** Expose database configuration management as MCP tools accessible to LLM agents.

**Proposed Tools:**
- `add_database_config(name, url, database, username, password, timeout)`
- `remove_database_config(name)`
- `list_database_configs()`
- `update_database_config(name, ...)`

**Pros:**
- ✅ **Dynamic:** LLM agents can add/remove databases at runtime
- ✅ **Flexible:** No manual intervention required
- ✅ **Convenient:** Configuration changes via natural language

**Cons:**
- ❌ **Security Risk:** Database passwords exposed in LLM context
- ❌ **No Access Control:** Any client can modify configuration
- ❌ **Prompt Injection:** Malicious prompts could delete databases
- ❌ **Accidental Deletion:** LLM errors could remove critical databases
- ❌ **Audit Trail:** Difficult to track who made configuration changes

**Security Analysis:**

```python
# Example of security risk:
# LLM agent receives this tool call:
add_database_config(
    name="production",
    url="http://prod-db.example.com:8529",
    database="prod_db",
    username="admin",
    password="super_secret_password"  # ❌ Password in LLM context!
)
```

**Verdict:** ⚠️ **NOT RECOMMENDED** for production deployments due to security risks.

---

#### Approach 3B: Separate Administrative CLI (⭐ RECOMMENDED)

**Concept:** Separate CLI tool for database configuration management, with read-only MCP tools for database discovery.

**CLI Tool:** `mcp-arangodb-async config` (using `argparse`)

**CLI Commands:**
- `mcp-arangodb-async config add --name <name> --url <url> --database <db> --username <user> --password-env <env_var>`
- `mcp-arangodb-async config remove --name <name> [--yes]`
- `mcp-arangodb-async config list`
- `mcp-arangodb-async config update --name <name> [--url <url>] [--database <db>] ...`
- `mcp-arangodb-async config test --name <name>`

**Read-Only MCP Tools:**
- `list_available_databases()` - List configured databases (names only, no credentials)

**Implementation (using argparse):**

```python
# mcp_arangodb_async/cli/config.py

import argparse
import yaml
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".mcp-arangodb-async"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

def main():
    """Main entry point for config CLI."""
    parser = argparse.ArgumentParser(
        prog="mcp-arangodb-async config",
        description="Manage database configurations for mcp-arangodb-async"
    )

    subparsers = parser.add_subparsers(dest="command", help="Configuration commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new database configuration")
    add_parser.add_argument("--name", required=True, help="Database configuration name")
    add_parser.add_argument("--url", required=True, help="ArangoDB URL (e.g., http://localhost:8529)")
    add_parser.add_argument("--database", required=True, help="Database name")
    add_parser.add_argument("--username", required=True, help="Username")
    add_parser.add_argument("--password-env", required=True, help="Environment variable for password")
    add_parser.add_argument("--timeout", type=float, default=30.0, help="Request timeout in seconds")
    add_parser.add_argument("--description", help="Optional description")

    # List command
    list_parser = subparsers.add_parser("list", help="List all configured databases")

    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a database configuration")
    remove_parser.add_argument("--name", required=True, help="Database configuration name")
    remove_parser.add_argument("--yes", action="store_true", help="Skip confirmation prompt")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update a database configuration")
    update_parser.add_argument("--name", required=True, help="Database configuration name")
    update_parser.add_argument("--url", help="New ArangoDB URL")
    update_parser.add_argument("--database", help="New database name")
    update_parser.add_argument("--username", help="New username")
    update_parser.add_argument("--password-env", help="New environment variable for password")
    update_parser.add_argument("--timeout", type=float, help="New request timeout")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test a database connection")
    test_parser.add_argument("--name", required=True, help="Database configuration name")

    args = parser.parse_args()

    if args.command == "add":
        return handle_add(args)
    elif args.command == "list":
        return handle_list(args)
    elif args.command == "remove":
        return handle_remove(args)
    elif args.command == "update":
        return handle_update(args)
    elif args.command == "test":
        return handle_test(args)
    else:
        parser.print_help()
        return 0

def handle_add(args):
    """Handle 'add' command."""
    config_data = load_config_file()

    if args.name in config_data.get("databases", {}):
        print(f"Error: Database '{args.name}' already exists", file=sys.stderr)
        return 1

    config_data.setdefault("databases", {})[args.name] = {
        "url": args.url,
        "database": args.database,
        "username": args.username,
        "password_env": args.password_env,
        "timeout": args.timeout,
    }

    if args.description:
        config_data["databases"][args.name]["description"] = args.description

    save_config_file(config_data)
    print(f"✓ Database '{args.name}' added successfully")
    return 0

# ... other handlers ...
```

**Pros:**
- ✅ **Secure:** Configuration management separated from LLM agent access
- ✅ **Clear separation of concerns:** Admin tasks vs. operational tasks
- ✅ **No credential exposure:** Passwords stored in environment variables, not config file
- ✅ **Access control:** CLI permissions control who can modify configuration
- ✅ **Audit-friendly:** Shell history logs configuration changes
- ✅ **Familiar pattern:** Standard CLI tool workflow

**Cons:**
- ❌ **Manual intervention:** Admin must run CLI commands
- ❌ **Not dynamic:** Cannot add databases at runtime via LLM

**Hybrid Approach (⭐ RECOMMENDED):**

Combine CLI for CRUD operations with read-only MCP tools for discovery:

**Admin Workflow (CLI):**
```bash
# Admin adds database configuration
mcp-arangodb-async config add \
  --name production \
  --url http://localhost:8529 \
  --database prod_db \
  --username prod_user \
  --password-env PROD_DB_PASSWORD

# Admin sets password in environment
export PROD_DB_PASSWORD=secret
```

**LLM Agent Workflow (MCP Tools):**
```python
# LLM agent discovers available databases
databases = list_available_databases()
# Returns: ["production", "staging", "analytics"]

# LLM agent sets focused database
set_focused_database("production")

# LLM agent works with production database
arango_query("FOR doc IN users RETURN doc")
```

**Security Benefits:**
- ✅ **No credential exposure:** Passwords never passed through LLM context
- ✅ **Read-only discovery:** LLM can see database names, but cannot modify configuration
- ✅ **Admin control:** Only administrators can add/remove databases

**Verdict:** ⭐ **RECOMMENDED** for production deployments.

### 6.3 Configuration Hierarchy (Expanded)

**6-Level Configuration Priority System:**

```
┌─────────────────────────────────────────────────────────────┐
│                  Configuration Resolution                    │
│                                                              │
│  Level 1: Tool argument `database` parameter                │
│  ├─ Source: Per-call override in tool arguments             │
│  ├─ Example: arango_query(..., database="analytics")        │
│  └─ Use Case: One-off cross-database operations             │
│                                                              │
│  Level 2: Session focused database                          │
│  ├─ Source: set_focused_database() MCP tool                 │
│  ├─ Example: set_focused_database("production")             │
│  └─ Use Case: Persistent context for work session           │
│                                                              │
│  Level 3: Config file default_database                      │
│  ├─ Source: ~/.mcp-arangodb-async/config.yaml               │
│  ├─ Example: default_database: production                   │
│  └─ Use Case: Default for multi-database deployments        │
│                                                              │
│  Level 4: Environment variable MCP_DEFAULT_DATABASE         │
│  ├─ Source: export MCP_DEFAULT_DATABASE=staging             │
│  ├─ Example: Override config file default                   │
│  └─ Use Case: CI/CD, testing, temporary overrides           │
│                                                              │
│  Level 5: Environment variables (ARANGO_*)                  │
│  ├─ Source: export ARANGO_DB=my_database                    │
│  ├─ Example: Backward compatibility mode                    │
│  └─ Use Case: Single-database deployments (existing users)  │
│                                                              │
│  Level 6: Hardcoded defaults                                │
│  ├─ Source: Code defaults                                   │
│  ├─ Example: _system database on localhost:8529             │
│  └─ Use Case: Last resort fallback                          │
└─────────────────────────────────────────────────────────────┘
```

**Resolution Algorithm (Pseudo-code):**

```python
def resolve_database(tool_args, session_context, config_file, env_vars):
    """Resolve database using 6-level priority system."""

    # Level 1: Tool argument override
    if "database" in tool_args:
        return tool_args["database"]

    # Level 2: Session focused database
    if session_context.has_focused_database():
        return session_context.get_focused_database()

    # Level 3: Config file default
    if config_file.exists() and config_file.has_default_database():
        return config_file.get_default_database()

    # Level 4: Environment variable override
    if "MCP_DEFAULT_DATABASE" in env_vars:
        return env_vars["MCP_DEFAULT_DATABASE"]

    # Level 5: Legacy environment variables (backward compatibility)
    if "ARANGO_DB" in env_vars:
        return env_vars["ARANGO_DB"]

    # Level 6: Hardcoded default
    return "_system"
```

### 6.4 Final Recommendations

**Primary Recommendation:** **Option A-Enhanced + Approach 3B (Hybrid)**

**Multi-Tenancy Approach:** Focused Database Context with Optional Override
- Session-based focused database context (`set_focused_database()`)
- Optional `database` parameter in all 34 tools for override
- 3 new MCP tools for context management
- Supports multiple ArangoDB server instances (geo-distributed, enterprise)

**Configuration Management:** Separate Administrative CLI + Read-Only MCP Tools
- CLI tool for database configuration CRUD operations (using `argparse`)
- Read-only `list_available_databases()` tool for LLM agents
- YAML configuration file with environment variable references for passwords
- No credential exposure to LLM agents

**Total Estimated Effort:** 4-5 weeks

**Implementation Phases:**

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| **Phase 1: Core Infrastructure** | 1.5 weeks | MultiDatabaseConnectionManager, SessionContextManager, config file support |
| **Phase 2: CLI Tool** | 1 week | Database configuration CLI with add/remove/list/update commands (argparse) |
| **Phase 3: Context Management Tools** | 0.5 weeks | set_focused_database, get_focused_database, list_available_databases |
| **Phase 4: Tool Model Updates** | 1 week | Add optional database parameter to all 34 tools |
| **Phase 5: Testing & Documentation** | 1 week | Comprehensive testing, security review, documentation |

**Benefits:**
- ✅ Single server instance (no context window pollution)
- ✅ Natural LLM agent workflow (set context once, work within it)
- ✅ Secure configuration management (CLI-based, no credential exposure)
- ✅ Flexible cross-database operations (optional override)
- ✅ Multi-server support (geo-distributed, environment separation)
- ✅ Backward compatible (default database fallback)
- ✅ Production-ready security posture

### 6.5 Not Recommended: Option C (Separate Server Instances)

**Approach:** Run multiple MCP server instances, one per database.

**Why Not Recommended:**

❌ **Context Window Pollution:**
- 34 tools × N instances = 34N tool definitions in LLM context
- Example: 3 databases = 102 tool definitions
- Breaks local LLM-based agent systems with limited context windows (e.g., 8K, 16K tokens)

❌ **Resource Overhead:**
- Multiple server processes
- Duplicate memory usage
- Complex deployment management

❌ **No Dynamic Tenant Management:**
- Cannot add databases without deploying new server instances
- Requires infrastructure changes for each new tenant

**When to Use (Temporary Workaround Only):**

✅ **Large LLM providers** (OpenAI, Anthropic) with 100K+ token context windows
✅ **Only 1-2 databases** (minimal duplication)
✅ **Temporary solution** until multi-tenancy implemented

**Long-Term Recommendation:** Migrate to Option A-Enhanced for production deployments.

---

## 7. Conclusion

### 7.1 Summary of Findings

**Current State:**
- ❌ No multi-tenancy support
- ❌ Single database per server instance
- ❌ Static configuration (startup-time only)
- ❌ Singleton connection manager

**Stakeholder Requirements:**
- ✅ Single MCP server instance (avoid context pollution)
- ✅ Multiple databases within one server
- ✅ Multiple ArangoDB server instances (geo-distributed, enterprise)
- ✅ Focused database context (natural LLM workflow)
- ✅ Secure configuration management

**Recommended Solution:**
- ⭐ **Option A-Enhanced:** Focused Database Context with Optional Override
- ⭐ **Approach 3B:** Separate Administrative CLI (using `argparse`)
- ⭐ **Hybrid:** CLI for CRUD + Read-only MCP tools for discovery

### 7.2 Key Corrections from v1

1. **CLI Framework:** Use `argparse` (already in codebase), not `click`
2. **Multi-Server Support:** YAML config supports multiple ArangoDB server instances (different URLs), not just multiple databases on one server
3. **Configuration Priority:** Expanded 6-level hierarchy with detailed resolution algorithm
4. **Environment Variable Integration:** Demonstrated backward compatibility and integration scenarios

### 7.3 Next Steps

**If Stakeholder Approves:**

1. **Phase 2: Test Definition Report** - Define comprehensive test suite for multi-tenancy implementation
2. **Phase 3: Implementation** - Implement Option A-Enhanced + Approach 3B
3. **Phase 4: Testing & Validation** - Execute tests, validate security, performance testing
4. **Phase 5: Documentation** - Update user documentation, API reference, deployment guides

**Questions for Stakeholder:**

1. Does Option A-Enhanced address the context window pollution concern?
2. Is the focused database context workflow natural for LLM agents?
3. Do you agree with Approach 3B (CLI using `argparse`) for secure configuration management?
4. Should I proceed with Phase 2 test definition for this approach?
5. Any additional requirements or concerns to address?

---

**Report Version:** v2
**Last Updated:** 2025-11-08
**Status:** Ready for Stakeholder Review


