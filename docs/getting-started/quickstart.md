# Quickstart Guide

Get started with mcp-arangodb-async in minutes using PyPI installation.

**Audience:** End Users  
**Prerequisites:** Python 3.11+, ArangoDB running ([see installation guide](install-arangodb.md))  
**Estimated Time:** 10 minutes

---

## What You'll Accomplish

By the end of this guide, you will:

- Install the MCP server from PyPI
- Configure your MCP client (Claude Desktop, Augment Code, LM Studio, or Gemini CLI)
- Execute your first AQL query through the MCP interface

---

## Prerequisites

Before proceeding, ensure you have:

1. **Python 3.11+** installed

   ```powershell
   python --version
   # Expected: Python 3.11.x or higher
   ```

2. **ArangoDB running** with a configured database and user

   If you haven't set up ArangoDB yet, follow the [ArangoDB Installation Guide](install-arangodb.md).

---

## Step 1: Install from PyPI

```powershell
pip install mcp-arangodb-async
```

**Verify Installation:**

```powershell
maa --version
```

---

## Step 2: Verify Database Connection

Test that the MCP server can connect to your ArangoDB instance:

```powershell
# Set environment variables
$env:ARANGO_URL = "http://localhost:8529"
$env:ARANGO_DB = "mcp_arangodb_test"
$env:ARANGO_USERNAME = "mcp_arangodb_user"
$env:ARANGO_PASSWORD = "mcp_arangodb_password"

# Run health check
maa --health
```

**Expected Output:**

```json
{"ok": true, "db": "mcp_arangodb_test", "user": "mcp_arangodb_user"}
```

✅ **Success!** The server can connect to ArangoDB.

❌ **If you see an error:**

- Check ArangoDB is running
- Verify credentials match your database setup
- See [Troubleshooting](#troubleshooting) section

---

## Step 3: Configure MCP Client

Choose your transport mode and client:

| Transport | Use Case |
|-----------|----------|
| **stdio** | Desktop AI assistants |
| **HTTP** | Web applications, remote access |

### stdio Transport (Desktop Clients)

#### Claude Desktop

**Location:** `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/.config/Claude/claude_desktop_config.json` (macOS/Linux)

```json
{
  "mcpServers": {
    "arangodb": {
      "command": "python",
      "args": ["-m", "mcp_arangodb_async"],
      "env": {
        "ARANGO_URL": "http://localhost:8529",
        "ARANGO_DB": "mcp_arangodb_test",
        "ARANGO_USERNAME": "mcp_arangodb_user",
        "ARANGO_PASSWORD": "mcp_arangodb_password"
      }
    }
  }
}
```

**Restart Claude Desktop** after saving the configuration.

#### Augment Code

**Option 1: Settings UI**

1. Open Augment Code settings
2. Navigate to MCP Servers section
3. Add new server with the same configuration as Claude Desktop

**Option 2: Import JSON**

```json
{
  "mcpServers": {
    "arangodb": {
      "command": "python",
      "args": ["-m", "mcp_arangodb_async"],
      "env": {
        "ARANGO_URL": "http://localhost:8529",
        "ARANGO_DB": "mcp_arangodb_test",
        "ARANGO_USERNAME": "mcp_arangodb_user",
        "ARANGO_PASSWORD": "mcp_arangodb_password"
      }
    }
  }
}
```

---

### HTTP Transport (Web Clients)

First, start the MCP server in HTTP mode:

```powershell
# Set environment variables
$env:ARANGO_URL = "http://localhost:8529"
$env:ARANGO_DB = "mcp_arangodb_test"
$env:ARANGO_USERNAME = "mcp_arangodb_user"
$env:ARANGO_PASSWORD = "mcp_arangodb_password"

# Start HTTP server
python -m mcp_arangodb_async --transport http --port 8000
```

**Verify the server is running:**

```powershell
curl http://localhost:8000/health
```

#### LM Studio

```json
{
  "mcpServers": {
    "arangodb": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

#### Gemini CLI

```json
{
  "mcpServers": {
    "arangodb": {
      "httpUrl": "http://localhost:8000/mcp"
    }
  }
}
```

---

## Step 4: First Interaction

### Test Basic Functionality

**Prompt:** "List all collections in my database."

**Expected Behavior:**

- Claude/Augment calls `arango_list_collections` tool
- Returns list of collection names

### Test Write Operation

**Prompt:** "Use arango_insert to add a document with name='test_document' and value=1 to a collection named 'tests'."

**Expected Behavior:**

- Creates `tests` collection if it doesn't exist
- Inserts document with `_key`, `_id`, `_rev` fields
- Returns the inserted document

See [First Interaction Guide](first-interaction.md) for more prompts and examples.

---

## Troubleshooting

### Server Won't Start

**Symptom:** `python -m mcp_arangodb_async` fails immediately

**Solutions:**

1. Check Python version: `python --version` (must be 3.11+)
2. Reinstall package: `pip install --force-reinstall mcp-arangodb-async`
3. Check for port conflicts: `netstat -ano | findstr :8000`

### Connection Refused

**Symptom:** Health check fails with connection error

**Solutions:**

1. Verify ArangoDB is running
2. Check ArangoDB is accessible: `curl http://localhost:8529`
3. Verify port 8529 is not blocked by firewall

### Authentication Failed

**Symptom:** Health check fails with "unauthorized" error

**Solutions:**

1. Verify credentials match your ArangoDB setup
2. Check user permissions in ArangoDB web UI: http://localhost:8529
3. Re-run database initialization

### MCP Client Can't Connect

**Symptom:** Client reports "server not found" or similar

**Solutions:**

1. Verify server is running: `maa --health`
2. Check configuration file location and JSON syntax
3. Restart your MCP client after configuration changes
4. Use full Python path if `python` is not in PATH

---

## Next Steps

✅ **You're ready to use the MCP server!**

**Learn More:**

- [First Interaction Guide](first-interaction.md) - Detailed test prompts and examples
- [Tools Reference](../user-guide/tools-reference.md) - Complete tool documentation
- [Transport Configuration](../configuration/transport-configuration.md) - Advanced transport options
- [Environment Variables](../configuration/environment-variables.md) - All configuration options

**For Developers:**

- [Install from Source](install-from-source.md) - Development setup and Docker deployment of the MCP server

---

## Related Documentation

- [ArangoDB Installation](install-arangodb.md)
- [First Interaction Guide](first-interaction.md)
- [Transport Configuration](../configuration/transport-configuration.md)
- [Environment Variables](../configuration/environment-variables.md)
- [Troubleshooting](../user-guide/troubleshooting.md)

