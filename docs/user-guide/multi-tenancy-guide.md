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
    url: "http://staging-server:8530"
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
  --url http://staging-server:8530 \
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

Details about other multi-tenancy tools can be found in the [tools reference](./tools-reference.md#multi-tenancy-tools-6).

Regarding, per-tool database override (resolution level 1), **all 32 data operation tools** support an optional `database` parameter for per-tool database override.

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
// Check status of all databases
{
  "tool": "arango_database_status"
}
```

---

## Incremental Setup Scenarios

This section provides step-by-step scenarios for setting up multi-tenancy, building from simple to complex configurations. Each scenario includes architecture diagrams, copy-pastable commands, and verification steps.

For detailed tutorials with complete setup instructions, see the [Multi-Tenancy Scenarios](multi-tenancy-scenarios/) directory.

### [Scenario 1: Single Instance, Single Database](multi-tenancy-scenarios/01-single-instance-single-database.md)

**Setup:** 1 user + 1 MCP server + 1 ArangoDB instance (port 8529) + 1 database

**Use Case:** Basic setup for a single project or development environment.

Learn the fundamentals of ArangoDB setup, Admin CLI configuration, and MCP server connection.

### [Scenario 2: Single Instance, Multiple Databases](multi-tenancy-scenarios/02-single-instance-multiple-databases.md)

**Setup:** 1 user + 1 MCP server + 1 ArangoDB instance (port 8529) + 2 databases

**Use Case:** Database separation on the same ArangoDB instance.

**Building on:** Scenario 1 (db1 already exists)

Practice database switching, focused database management, and cross-database operations.

### [Scenario 3: Multiple Instances, Multiple Databases](multi-tenancy-scenarios/03-multiple-instances-multiple-databases.md)

**Setup:** 1 user + 1 MCP server + 2 ArangoDB instances (ports 8529 & 8530) + 3 databases total

**Use Case:** Complete isolation between environments, different ArangoDB versions, or production/non-production separation.

**Building on:** Scenario 2 (db1 and db2 on port 8529)

Scale to multiple ArangoDB instances with Docker Compose and manage separate credentials.

### [Scenario 4: Agent-Based Access Control](multi-tenancy-scenarios/04-agent-based-access-control.md)

**Setup:** 1 MCP server + 1 ArangoDB instance + 2 databases + 2 users with different permissions

**Use Case:** Protect sensitive content while allowing controlled agent access.

Implement fine-grained access control with read-only and read-write permissions for AI agents.

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

**Solution:** Check database status:

```json
{
  "tool": "arango_database_status"
}
```

Review the status for database 'xyz' and check:
1. ArangoDB server is running
2. URL and port are correct
3. Credentials are valid
4. Network connectivity

---

## Related Documentation

- [CLI Reference](cli-reference.md) - Database configuration management
- [Tools Reference](tools-reference.md) - Complete tool documentation
- [Environment Variables](../configuration/environment-variables.md) - Server configuration
- [Transport Configuration](../configuration/transport-configuration.md) - Transport setup

---

**Next Steps:**

1. Configure your databases using the [CLI tool](cli-reference.md)
2. Check database status using `arango_database_status`
3. Set focused database using `arango_set_focused_database`
4. Start using data operation tools with automatic database resolution
