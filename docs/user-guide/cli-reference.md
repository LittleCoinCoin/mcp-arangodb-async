# CLI Reference

Complete documentation for the `mcp-arangodb-async db` command-line tool for database configuration management.

**Audience:** System Administrators and DevOps Engineers  
**Prerequisites:** File system access to configuration files, Python 3.11+  
**Estimated Time:** 10-15 minutes

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Configuration File](#configuration-file)
4. [Commands](#commands)
5. [Examples](#examples)
6. [Security](#security)
7. [Troubleshooting](#troubleshooting)
8. [Related Documentation](#related-documentation)

---

## Overview

The `mcp-arangodb-async db` CLI tool provides admin-controlled database configuration management. It enables adding, removing, listing, testing, and monitoring database configurations without code changes or server restarts.

### Key Features

- **Admin-Only Access** - Requires file system access to modify YAML configuration
- **Secure Password Management** - Passwords stored in environment variables, not in YAML
- **Connection Testing** - Verify database connectivity before deployment
- **Status Reporting** - View database resolution order and configuration status
- **No Server Restart Required** - Changes take effect on next MCP server start

### Security Model

The CLI tool is **not exposed via MCP protocol**. Only system administrators with file system access can modify database configurations. This separation ensures agents cannot modify infrastructure configuration.

---

## Installation

The CLI tool is included with the mcp-arangodb-async package:

```bash
pip install mcp-arangodb-async
```

Verify installation:

```bash
python -m mcp_arangodb_async db --help
```

---

## Configuration File

### Default Location

```
config/databases.yaml
```

### How Configuration Works

The CLI tool manages a YAML configuration file that stores database connection details. **Passwords are NOT stored in the YAML file** - only the names of environment variables that contain passwords.

**Security Model:**
1. YAML file stores: database URLs, usernames, and **environment variable names**
2. Environment variables store: actual passwords (never in YAML)
3. At connection time: Server reads environment variables to get passwords

### YAML Schema

```yaml
# Optional: Default database to use when no focused database is set
default_database: "production"

# Database configurations
databases:
  production:
    url: "http://localhost:8529"
    database: "myapp_prod"
    username: "admin"
    password_env: "MCP_ARANGO_PROD_PASSWORD"  # ← NAME of env var (not the password!)
    timeout: 60.0
    description: "Production database for live data"  # Optional

  staging:
    url: "http://staging.example.com:8529"
    database: "myapp_staging"
    username: "admin"
    password_env: "MCP_ARANGO_STAGING_PASSWORD"  # ← Different env var for different password
    timeout: 30.0
    description: "Staging database for pre-production testing"
```

### Environment Variables

Passwords are stored in environment variables. The YAML file only references the environment variable **names**:

```bash
# Linux/macOS
export MCP_ARANGO_PROD_PASSWORD="your-secure-password"
export MCP_ARANGO_STAGING_PASSWORD="your-staging-password"

# Windows (PowerShell)
$env:MCP_ARANGO_PROD_PASSWORD="your-secure-password"
$env:MCP_ARANGO_STAGING_PASSWORD="your-staging-password"
```

**Important:** Each database can have a different password by using different environment variable names. This allows secure multi-environment setups where production and staging have different credentials.

---

## Important: Server Restart Required

**After using `db add` or `db remove`, the MCP server must be restarted to pick up the changes.**

The flow is:
1. Run `db add production ...` → Updates YAML file ✅
2. MCP server reads YAML file at startup
3. **Stop and restart the MCP server** to load new configuration
4. After restart, the database is accessible via MCP tools

**Why?** The server loads the configuration once at startup. Changes to the YAML file are not automatically reloaded while the server is running.

---

## Commands

### db add

Add a new database configuration to the YAML file.

**Syntax:**

```bash
python -m mcp_arangodb_async db add <key> \
  --url <url> \
  --database <database> \
  --username <username> \
  --password-env <env_var_name> \
  [--timeout <seconds>] \
  [--description <description>] \
  [--config-path <path>]
```

**Parameters:**

- `key` (required) - Unique identifier for this database configuration
- `--url` (required) - ArangoDB server URL (e.g., `http://localhost:8529`)
- `--database` (required) - Database name
- `--username` (required) - Username for authentication
- `--password-env` (required) - Environment variable name containing the password
- `--timeout` (optional) - Connection timeout in seconds (default: 30.0)
- `--description` (optional) - Human-readable description
- `--config-path` (optional) - Path to configuration file (default: `config/databases.yaml`)

**Example:**

```bash
python -m mcp_arangodb_async db add production \
  --url http://localhost:8529 \
  --database myapp_prod \
  --username admin \
  --password-env MCP_ARANGO_PROD_PASSWORD \
  --timeout 60 \
  --description "Production database for live data"
```

**Output:**

```
✓ Database 'production' added successfully
  URL: http://localhost:8529
  Database: myapp_prod
  Username: admin
  Password env: MCP_ARANGO_PROD_PASSWORD
  Timeout: 60.0s
  Description: Production database for live data

Configuration saved to: config/databases.yaml
```

---

### db remove

Remove a database configuration from the YAML file.

**Syntax:**

```bash
python -m mcp_arangodb_async db remove <key> [--config-path <path>]
```

**Parameters:**

- `key` (required) - Database key to remove
- `--config-path` (optional) - Path to configuration file (default: `config/databases.yaml`)

**Example:**

```bash
python -m mcp_arangodb_async db remove staging
```

**Output:**

```
✓ Database 'staging' removed successfully
Configuration saved to: config/databases.yaml
```

---

### db list

List all configured databases with their details.

**Syntax:**

```bash
python -m mcp_arangodb_async db list [--config-path <path>]
```

**Parameters:**

- `--config-path` (optional) - Path to configuration file (default: `config/databases.yaml`)

**Example:**

```bash
python -m mcp_arangodb_async db list
```

**Output:**

```
Configured databases (2):
Configuration file: config/databases.yaml
Default database: production

  production:
    URL: http://localhost:8529
    Database: myapp_prod
    Username: admin
    Password env: MCP_ARANGO_PROD_PASSWORD
    Timeout: 60.0s
    Description: Production database for live data

  staging:
    URL: http://staging.example.com:8529
    Database: myapp_staging
    Username: admin
    Password env: MCP_ARANGO_STAGING_PASSWORD
    Timeout: 30.0s
    Description: Staging database for pre-production testing
```

---

### db test

Test connection to a specific database configuration.

**Syntax:**

```bash
python -m mcp_arangodb_async db test <key> [--config-path <path>]
```

**Parameters:**

- `key` (required) - Database key to test
- `--config-path` (optional) - Path to configuration file (default: `config/databases.yaml`)

**Example (Success):**

```bash
python -m mcp_arangodb_async db test production
```

**Output:**

```
✓ Connection to 'production' successful
  ArangoDB version: 3.11.0
```

**Example (Failure):**

```bash
python -m mcp_arangodb_async db test staging
```

**Output:**

```
✗ Connection to 'staging' failed
  Error: Connection refused
```

**Exit Codes:**

- `0` - Connection successful
- `1` - Connection failed or database not found

---

### db status

Show database resolution status and configuration overview.

**Syntax:**

```bash
python -m mcp_arangodb_async db status [--config-path <path>]
```

**Parameters:**

- `--config-path` (optional) - Path to configuration file (default: `config/databases.yaml`)

**Example:**

```bash
python -m mcp_arangodb_async db status
```

**Output:**

```
Database Resolution Status:
Configuration file: config/databases.yaml

Default database (from config): production
Default database (from MCP_DEFAULT_DATABASE): Not set

Configured databases: 2
  - production
  - staging

Resolution order:
  1. Tool argument (database parameter)
  2. Focused database (session state)
  3. Config default (from YAML)
  4. Environment variable (MCP_DEFAULT_DATABASE)
  5. First configured database
  6. Fallback to '_system'
```

**Use Cases:**

- Verify configuration before deployment
- Troubleshoot database resolution issues
- Understand which database will be used in different scenarios
- Audit configured databases

---

## Examples

### Example 1: Initial Setup

Set up production and staging databases:

```bash
# Add production database
python -m mcp_arangodb_async db add production \
  --url http://localhost:8529 \
  --database myapp_prod \
  --username admin \
  --password-env MCP_ARANGO_PROD_PASSWORD \
  --timeout 60 \
  --description "Production database"

# Add staging database
python -m mcp_arangodb_async db add staging \
  --url http://staging:8529 \
  --database myapp_staging \
  --username admin \
  --password-env MCP_ARANGO_STAGING_PASSWORD \
  --timeout 30 \
  --description "Staging database"

# Set environment variables
export MCP_ARANGO_PROD_PASSWORD="prod-password"
export MCP_ARANGO_STAGING_PASSWORD="staging-password"

# Test connections
python -m mcp_arangodb_async db test production
python -m mcp_arangodb_async db test staging

# Verify configuration
python -m mcp_arangodb_async db list
```

---

### Example 2: Update Configuration

Replace an existing database configuration:

```bash
# Remove old configuration
python -m mcp_arangodb_async db remove production

# Add new configuration
python -m mcp_arangodb_async db add production \
  --url http://new-server:8529 \
  --database myapp_prod_v2 \
  --username admin \
  --password-env MCP_ARANGO_PROD_PASSWORD \
  --timeout 90 \
  --description "Production database (migrated)"

# Test new configuration
python -m mcp_arangodb_async db test production
```

---

### Example 3: Multi-Environment Setup

Configure databases for development, staging, and production:

```bash
# Development (local)
python -m mcp_arangodb_async db add dev \
  --url http://localhost:8529 \
  --database myapp_dev \
  --username root \
  --password-env MCP_ARANGO_DEV_PASSWORD \
  --description "Local development database"

# Staging (remote)
python -m mcp_arangodb_async db add staging \
  --url http://staging.example.com:8529 \
  --database myapp_staging \
  --username admin \
  --password-env MCP_ARANGO_STAGING_PASSWORD \
  --description "Staging environment"

# Production (remote, high timeout)
python -m mcp_arangodb_async db add production \
  --url http://prod.example.com:8529 \
  --database myapp_prod \
  --username admin \
  --password-env MCP_ARANGO_PROD_PASSWORD \
  --timeout 120 \
  --description "Production environment"

# Set environment variables
export MCP_ARANGO_DEV_PASSWORD="dev"
export MCP_ARANGO_STAGING_PASSWORD="staging-secret"
export MCP_ARANGO_PROD_PASSWORD="prod-secret"

# Verify all connections
for db in dev staging production; do
  python -m mcp_arangodb_async db test $db
done
```

---

## Security

### Password Management

**Best Practices:**

1. **Never store passwords in YAML** - Always use environment variables
2. **Use different passwords per environment** - Don't reuse passwords
3. **Rotate passwords regularly** - Update environment variables and test connections
4. **Use strong passwords** - Minimum 16 characters, mixed case, numbers, symbols
5. **Restrict file permissions** - Protect YAML file and environment variable files

**File Permissions:**

```bash
# Restrict YAML file to owner only
chmod 600 config/databases.yaml

# Restrict environment file to owner only
chmod 600 .env
```

### Access Control

The CLI tool requires:

- **File system access** to read/write YAML configuration
- **Environment variable access** to read passwords
- **Network access** to test database connections

Only grant CLI access to trusted administrators.

### Audit Trail

Track configuration changes using version control:

```bash
# Initialize git repository
git init
git add config/databases.yaml
git commit -m "Initial database configuration"

# Track changes
git diff config/databases.yaml
git log config/databases.yaml
```

---

## Troubleshooting

### Error: Database already exists

**Problem:**

```
Error: Database 'production' already exists
Use 'db remove' to remove it first, or choose a different key
```

**Solution:**

Remove the existing configuration first:

```bash
python -m mcp_arangodb_async db remove production
python -m mcp_arangodb_async db add production ...
```

---

### Error: Database not found

**Problem:**

```
Error: Database 'staging' not found
```

**Solution:**

List configured databases to verify the key:

```bash
python -m mcp_arangodb_async db list
```

---

### Error: Connection failed

**Problem:**

```
✗ Connection to 'production' failed
  Error: Connection refused
```

**Solutions:**

1. **Verify ArangoDB is running:**

```bash
curl http://localhost:8529/_api/version
```

2. **Check URL and port:**

```bash
python -m mcp_arangodb_async db list
```

3. **Verify credentials:**

```bash
echo $MCP_ARANGO_PROD_PASSWORD
```

4. **Test with curl:**

```bash
curl -u admin:$MCP_ARANGO_PROD_PASSWORD http://localhost:8529/_api/version
```

---

### Error: Permission denied

**Problem:**

```
Error: [Errno 13] Permission denied: 'config/databases.yaml'
```

**Solution:**

Check file permissions and ownership:

```bash
ls -l config/databases.yaml
chmod 600 config/databases.yaml
```

---

## Related Documentation

- [Multi-Tenancy Guide](multi-tenancy-guide.md) - Using multiple databases with MCP tools
- [Tools Reference](tools-reference.md) - MCP tools with database parameter
- [Configuration Guide](../deployment/configuration.md) - Server configuration options
- [Security Best Practices](../deployment/security.md) - Security guidelines

---

**Next Steps:**

1. Configure your databases using `db add`
2. Test connections using `db test`
3. Start the MCP server and use multi-tenancy tools
4. Read the [Multi-Tenancy Guide](multi-tenancy-guide.md) for usage patterns

