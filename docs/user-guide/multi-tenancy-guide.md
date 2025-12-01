# Multi-Tenancy Guide

Complete guide to using multiple ArangoDB databases with the mcp-arangodb-async server.

**Audience:** End Users and Developers  
**Prerequisites:** Server installed, databases configured via CLI  
**Estimated Time:** 20-30 minutes

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Database Resolution](#database-resolution)
4. [Multi-Tenancy Tools](#multi-tenancy-tools)
5. [Database Parameter](#database-parameter)
6. [Usage Patterns](#usage-patterns)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

Multi-tenancy enables working with multiple ArangoDB databases in a single MCP session. This is useful for:

- **Multi-environment workflows** - Switch between dev, staging, and production
- **Cross-database operations** - Compare data across databases
- **Tenant isolation** - Separate data for different customers or projects
- **Testing and validation** - Test queries against staging before production

### Architecture

The multi-tenancy system consists of three layers:

1. **Configuration Layer** - YAML file with database configurations (managed via CLI)
2. **Resolution Layer** - Algorithm to determine which database to use
3. **Tool Layer** - MCP tools with optional database parameter

### Security Model: Password Environment Variables

**Passwords are never stored in the YAML configuration file.** Instead:

1. **YAML file stores:** Database URLs, usernames, and **environment variable names**
2. **Environment stores:** Actual passwords (never in YAML)
3. **At connection time:** Server reads environment variables to get passwords

**Important:** Passwords are bound to **users**, not databases. If you're using the same user on the same ArangoDB server for multiple databases, you only need one password environment variable.

**Example - Same server, same user (common case):**

```yaml
# config/databases.yaml
databases:
  production:
    url: "http://localhost:8529"
    database: "myapp_prod"
    username: "admin"
    password_env: "ARANGO_PASSWORD"  # ← Same user, same password env var

  staging:
    url: "http://localhost:8529"
    database: "myapp_staging"
    username: "admin"
    password_env: "ARANGO_PASSWORD"  # ← Same user, same password env var
```

```bash
export ARANGO_PASSWORD="admin-password"  # ← One password for user "admin"
```

**Example - Different servers (separate ArangoDB instances):**

```yaml
databases:
  production:
    url: "http://prod-server:8529"
    database: "myapp_prod"
    username: "admin"
    password_env: "PROD_ARANGO_PASSWORD"  # ← Different server = different password

  staging:
    url: "http://staging-server:8529"
    database: "myapp_staging"
    username: "admin"
    password_env: "STAGING_ARANGO_PASSWORD"  # ← Different server = different password
```

```bash
export PROD_ARANGO_PASSWORD="prod-admin-password"
export STAGING_ARANGO_PASSWORD="staging-admin-password"
```

**Why this design?**
- Passwords are never committed to version control
- Supports both single-server and multi-server setups
- Passwords can be rotated without changing YAML files
- Follows security best practices (12-factor app)

---

## Quick Start

### Step 1: Configure Databases

Use the CLI tool to add database configurations. The `--password-env` parameter specifies the **name** of an environment variable that contains the password for that user.

**Same server, same user (typical local development):**

```bash
# Both databases on same server, same user = same password env var
python -m mcp_arangodb_async db add production \
  --url http://localhost:8529 \
  --database myapp_prod \
  --username admin \
  --password-env ARANGO_PASSWORD

python -m mcp_arangodb_async db add staging \
  --url http://localhost:8529 \
  --database myapp_staging \
  --username admin \
  --password-env ARANGO_PASSWORD  # Same user = same password
```

**Different servers (separate ArangoDB instances):**

```bash
# Different servers have separate users/passwords
python -m mcp_arangodb_async db add production \
  --url http://prod-server:8529 \
  --database myapp_prod \
  --username admin \
  --password-env PROD_ARANGO_PASSWORD

python -m mcp_arangodb_async db add staging \
  --url http://staging-server:8529 \
  --database myapp_staging \
  --username admin \
  --password-env STAGING_ARANGO_PASSWORD
```

### Step 2: Set Environment Variables

Set the password for each user:

```bash
# Same server, same user - one password
export ARANGO_PASSWORD="admin-password"

# OR for different servers - different passwords
export PROD_ARANGO_PASSWORD="prod-admin-password"
export STAGING_ARANGO_PASSWORD="staging-admin-password"
```

**Key insight:** Passwords are bound to **users**, not databases. If you use the same user on the same server for multiple databases, they share the same password.

### Step 3: Start MCP Server

```bash
python -m mcp_arangodb_async server
```

**Important:** The server reads the configuration file at startup. If you add or remove databases, you must restart the server for changes to take effect.

### Step 3: Use Multi-Tenancy Tools

```json
// List available databases
{
  "tool": "arango_list_available_databases"
}

// Set focused database
{
  "tool": "arango_set_focused_database",
  "arguments": {
    "database_key": "staging"
  }
}

// Query the focused database
{
  "tool": "arango_query",
  "arguments": {
    "query": "FOR doc IN users RETURN doc"
  }
}

// Override with database parameter
{
  "tool": "arango_query",
  "arguments": {
    "query": "FOR doc IN users RETURN doc",
    "database": "production"
  }
}
```

---

## Database Resolution

The server uses a **6-level resolution algorithm** to determine which database to use for each tool call:

### Resolution Order

1. **Tool Argument** - `database` parameter in tool call (highest priority)
2. **Focused Database** - Set via `arango_set_focused_database` (session state)
3. **Config Default** - `default_database` in YAML configuration
4. **Environment Variable** - `MCP_DEFAULT_DATABASE` environment variable
5. **First Configured** - First database in YAML configuration
6. **Fallback** - `_system` database (lowest priority)

### Example Resolution

**Configuration:**

```yaml
default_database: "production"
databases:
  production:
    url: "http://localhost:8529"
    database: "myapp_prod"
    ...
  staging:
    url: "http://staging:8529"
    database: "myapp_staging"
    ...
```

**Scenarios:**

| Tool Call | Focused DB | Result | Reason |
|-----------|------------|--------|--------|
| `arango_query(query="...")` | None | `production` | Config default |
| `arango_query(query="...")` | `staging` | `staging` | Focused database |
| `arango_query(query="...", database="production")` | `staging` | `production` | Tool argument (highest priority) |

### View Resolution Status

Use the `arango_get_database_resolution` tool to see the current resolution:

```json
{
  "tool": "arango_get_database_resolution"
}
```

**Response:**

```json
{
  "focused_database": "staging",
  "config_default": "production",
  "env_default": null,
  "first_configured": "production",
  "fallback": "_system",
  "resolution_order": [
    "1. Tool argument (database parameter)",
    "2. Focused database (session state): staging",
    "3. Config default (from YAML): production",
    "4. Environment variable (MCP_DEFAULT_DATABASE): Not set",
    "5. First configured database: production",
    "6. Fallback to '_system'"
  ],
  "current_database": "staging"
}
```

---

## Multi-Tenancy Tools

Six MCP tools for database management and monitoring.

### arango_set_focused_database

Set the focused database for the current session.

**Parameters:**

- `database_key` (string, required) - Database key from configuration

**Example:**

```json
{
  "tool": "arango_set_focused_database",
  "arguments": {
    "database_key": "staging"
  }
}
```

**Response:**

```json
{
  "success": true,
  "previous_database": "production",
  "new_database": "staging",
  "message": "Focused database set to 'staging'"
}
```

---

### arango_get_focused_database

Get the currently focused database.

**Parameters:** None

**Example:**

```json
{
  "tool": "arango_get_focused_database"
}
```

**Response:**

```json
{
  "focused_database": "staging",
  "is_set": true
}
```

---

### arango_list_available_databases

List all configured databases.

**Parameters:** None

**Example:**

```json
{
  "tool": "arango_list_available_databases"
}
```

**Response:**

```json
{
  "databases": [
    {
      "key": "production",
      "url": "http://localhost:8529",
      "database": "myapp_prod",
      "username": "admin",
      "timeout": 60.0,
      "description": "Production database"
    },
    {
      "key": "staging",
      "url": "http://staging:8529",
      "database": "myapp_staging",
      "username": "admin",
      "timeout": 30.0,
      "description": "Staging database"
    }
  ],
  "count": 2,
  "default_database": "production"
}
```

---

### arango_get_database_resolution

Show the database resolution algorithm and current state.

**Parameters:** None

**Example:** See [Database Resolution](#database-resolution) section above.

---

### arango_test_database_connection

Test connection to a specific database.

**Parameters:**

- `database_key` (string, required) - Database key to test

**Example:**

```json
{
  "tool": "arango_test_database_connection",
  "arguments": {
    "database_key": "production"
  }
}
```

**Response (Success):**

```json
{
  "database_key": "production",
  "connected": true,
  "version": "3.11.0",
  "message": "Connection successful"
}
```

**Response (Failure):**

```json
{
  "database_key": "staging",
  "connected": false,
  "error": "Connection refused",
  "message": "Connection failed"
}
```

---

### arango_get_multi_database_status

Get status of all configured databases.

**Parameters:** None

**Example:**

```json
{
  "tool": "arango_get_multi_database_status"
}
```

**Response:**

```json
{
  "databases": [
    {
      "key": "production",
      "connected": true,
      "version": "3.11.0"
    },
    {
      "key": "staging",
      "connected": false,
      "error": "Connection refused"
    }
  ],
  "total": 2,
  "connected": 1,
  "failed": 1
}
```

---

## Database Parameter

All 32 data operation tools support an optional `database` parameter for per-tool database override.

### Supported Tools

**Core Data Operations (7):**
- arango_query
- arango_list_collections
- arango_insert
- arango_update
- arango_remove
- arango_create_collection
- arango_backup

**Indexing & Query Analysis (4):**
- arango_list_indexes
- arango_create_index
- arango_delete_index
- arango_explain_query

**Validation & Bulk Operations (4):**
- arango_validate_references
- arango_insert_with_validation
- arango_bulk_insert
- arango_bulk_update

**Graph Operations (12):**
- arango_create_graph
- arango_add_edge
- arango_traverse
- arango_shortest_path
- arango_list_graphs
- arango_add_vertex_collection
- arango_add_edge_definition
- arango_backup_graph
- arango_restore_graph
- arango_backup_named_graphs
- arango_validate_graph_integrity
- arango_graph_statistics

**Schema Management (2):**
- arango_create_schema
- arango_validate_document

**Enhanced Query Tools (2):**
- arango_query_builder
- arango_query_profile

**Health & Status (1):**
- arango_database_status

### Usage Example

```json
// Query staging database (focused database)
{
  "tool": "arango_query",
  "arguments": {
    "query": "FOR doc IN users RETURN doc"
  }
}

// Query production database (override with parameter)
{
  "tool": "arango_query",
  "arguments": {
    "query": "FOR doc IN users RETURN doc",
    "database": "production"
  }
}
```

---

## Usage Patterns

### Pattern 1: Environment Switching

Switch between environments during development:

```json
// Start with staging
{
  "tool": "arango_set_focused_database",
  "arguments": {"database_key": "staging"}
}

// Test query on staging
{
  "tool": "arango_query",
  "arguments": {"query": "FOR doc IN users LIMIT 10 RETURN doc"}
}

// Switch to production
{
  "tool": "arango_set_focused_database",
  "arguments": {"database_key": "production"}
}

// Run same query on production
{
  "tool": "arango_query",
  "arguments": {"query": "FOR doc IN users LIMIT 10 RETURN doc"}
}
```

---

### Pattern 2: Cross-Database Comparison

Compare data across databases without switching:

```json
// Get staging count
{
  "tool": "arango_query",
  "arguments": {
    "query": "RETURN LENGTH(users)",
    "database": "staging"
  }
}

// Get production count
{
  "tool": "arango_query",
  "arguments": {
    "query": "RETURN LENGTH(users)",
    "database": "production"
  }
}
```

---

### Pattern 3: Safe Testing Workflow

Test queries on staging before running on production:

```json
// 1. Set focused database to staging
{
  "tool": "arango_set_focused_database",
  "arguments": {"database_key": "staging"}
}

// 2. Test query on staging
{
  "tool": "arango_query",
  "arguments": {
    "query": "FOR doc IN users FILTER doc.age > 18 UPDATE doc WITH {verified: true} IN users"
  }
}

// 3. Verify results on staging
{
  "tool": "arango_query",
  "arguments": {
    "query": "FOR doc IN users FILTER doc.verified == true RETURN COUNT(doc)"
  }
}

// 4. If successful, run on production with override
{
  "tool": "arango_query",
  "arguments": {
    "query": "FOR doc IN users FILTER doc.age > 18 UPDATE doc WITH {verified: true} IN users",
    "database": "production"
  }
}
```

---

## Best Practices

### 1. Use Focused Database for Workflows

Set focused database at the start of a workflow to avoid repeating database parameter:

```json
// Good: Set once, use many times
{
  "tool": "arango_set_focused_database",
  "arguments": {"database_key": "staging"}
}
// All subsequent tools use staging automatically

// Avoid: Repeating database parameter
{
  "tool": "arango_query",
  "arguments": {"query": "...", "database": "staging"}
}
{
  "tool": "arango_insert",
  "arguments": {"collection": "...", "document": {...}, "database": "staging"}
}
```

### 2. Use Database Parameter for One-Off Overrides

Use database parameter for occasional cross-database operations:

```json
// Focused database is staging
{
  "tool": "arango_set_focused_database",
  "arguments": {"database_key": "staging"}
}

// Most operations use staging
{
  "tool": "arango_query",
  "arguments": {"query": "FOR doc IN users RETURN doc"}
}

// One-off production query
{
  "tool": "arango_query",
  "arguments": {
    "query": "FOR doc IN users RETURN COUNT(doc)",
    "database": "production"
  }
}
```

### 3. Verify Resolution Before Critical Operations

Always check database resolution before destructive operations:

```json
// Check current database
{
  "tool": "arango_get_database_resolution"
}

// Verify it's the intended database
// Then proceed with operation
{
  "tool": "arango_remove",
  "arguments": {
    "collection": "users",
    "key": "123"
  }
}
```

### 4. Test Connections Before Use

Test database connections before starting work:

```json
// Test all databases
{
  "tool": "arango_get_multi_database_status"
}

// Or test specific database
{
  "tool": "arango_test_database_connection",
  "arguments": {"database_key": "production"}
}
```

---

## Troubleshooting

### Issue: Wrong database being used

**Symptom:** Tool operates on unexpected database

**Solution:** Check database resolution:

```json
{
  "tool": "arango_get_database_resolution"
}
```

Review the resolution order and verify:
1. No unintended database parameter in tool call
2. Focused database is set correctly
3. Config default is as expected

---

### Issue: Database not found

**Symptom:** Error "Database 'xyz' not found in configuration"

**Solution:** List available databases:

```json
{
  "tool": "arango_list_available_databases"
}
```

Verify the database key exists. If not, add it via CLI:

```bash
python -m mcp_arangodb_async db add xyz ...
```

---

### Issue: Connection failed

**Symptom:** Error "Failed to connect to database 'xyz'"

**Solution:** Test connection:

```json
{
  "tool": "arango_test_database_connection",
  "arguments": {"database_key": "xyz"}
}
```

Check:
1. ArangoDB server is running
2. URL and port are correct
3. Credentials are valid
4. Network connectivity

---

## Related Documentation

- [CLI Reference](cli-reference.md) - Database configuration management
- [Tools Reference](tools-reference.md) - Complete tool documentation
- [Configuration Guide](../deployment/configuration.md) - Server configuration

---

**Next Steps:**

1. Configure your databases using the [CLI tool](cli-reference.md)
2. Test connections using `arango_test_database_connection`
3. Set focused database using `arango_set_focused_database`
4. Start using data operation tools with automatic database resolution
