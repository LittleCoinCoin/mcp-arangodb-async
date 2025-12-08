# Multi-Tenancy Analysis for mcp-arangodb-async

This directory contains comprehensive analysis and documentation for multi-tenancy capabilities in the mcp-arangodb-async MCP server.

---

## Documents

### Phase 1: Architectural Analysis

- **[00-multi_tenancy_assessment_v2.md](./00-multi_tenancy_assessment_v2.md)** ⭐ **CURRENT** - Comprehensive architectural analysis (v2)
  - **Changes from v1**: CLI framework corrected to `argparse` (already in codebase), multi-server capability clarified (supports multiple ArangoDB server instances), configuration priority hierarchy expanded (6-level system), environment variable integration examples added
  - Configuration mechanisms and parameters
  - Multi-tenancy assessment and limitations
  - Architecture review and connection management
  - Industry standards comparison
  - Multi-server deployment scenarios (geo-distributed, hybrid)
  - Implementation recommendations (Option A-Enhanced + Approach 3B using argparse)

- **[01-architecture_design_v3.md](./01-architecture_design_v3.md)** ⭐ **CURRENT** - Complete architecture design for multi-tenancy (v3 - Final)
  - **Changes from v2**: Integrated Integration Design v3 findings (terminology resolution, session management clarification, per-tool database override, async/await concurrency, implementation phases restructured)
  - **Purpose**: Final architectural design for Option A-Enhanced + Approach 3B
  - **Format**: Focused summary covering all key points (766 lines)
  - High-level architecture (Mermaid diagrams: architecture, data flow with per-tool override)
  - Component design (8 components: MultiDatabaseConnectionManager, SessionState, ConfigFileLoader, database resolver, session ID extractor, 6 multi-tenancy tools, 8 design pattern tools, 35 data tools)
  - Configuration & security (YAML schema, 6-level priority, password best practices)
  - Session management (definition, implicit creation, concurrency model)
  - Backward compatibility (single-database migration path)
  - Implementation phases (5 phases, 4 weeks: foundation → renaming → migration → override → verification)
  - Summary (architectural decisions table, implementation checklist, success criteria)
  - **Key Changes**: SessionContextManager → SessionState, 3 tools renamed, 35 tools require `database` parameter, asyncio.Lock (not threading.Lock)
  - **Status**: Ready for Implementation

- **[01-architecture_design_v2.md](./01-architecture_design_v2.md)** 📦 **ARCHIVED** - Architecture design v2
  - **Issue**: Missing terminology resolution (context overload)
  - **Issue**: Missing per-tool database override details
  - **Issue**: Missing session management clarification
  - Superseded by v3 after integration design analysis

- **[01-architecture_design_v1.md](./01-architecture_design_v1.md)** 📦 **ARCHIVED** - Architecture design v1
  - Superseded by v2 based on v0.4.0 sprint changes

- **[01-architecture_design_v0.md](./01-architecture_design_v0.md)** 📦 **ARCHIVED** - Architecture design v0
  - Superseded by v1 based on stakeholder feedback

- **[02-integration_design_v3.md](./02-integration_design_v3.md)** ⭐ **CURRENT** - Final streamlined integration design (v3)
  - **Purpose**: Define integration between v0.4.0 Design Patterns and v0.5.0 Multi-Tenancy
  - **Scope**: Final decisions only, no peripheral discussions
  - Terminology resolution (rename "context" → "workflow")
  - Session management (sequential within session, implicit creation)
  - Database selection architecture (focused database + per-tool override)
  - State migration (global → per-session for 6 tools + 1 helper)
  - Implementation checklist (file changes, code patterns, verification steps)
  - Integration risks & mitigations (4 key risks)
  - Implementation order (5 phases)
  - **Key Feature**: Per-tool database override (35 tools require `database` parameter)
  - **Length**: 467 lines (within 300-500 target)
  - **Status**: Ready for Implementation

- **[02-integration_design_v0.md](./02-integration_design_v0.md)** 📦 **ARCHIVED** - Initial integration design
  - Superseded by v3 after stakeholder feedback iterations

- **[04-admin_cli_roadmap_v0.md](./04-admin_cli_roadmap_v0.md)** ⭐ **CURRENT** - Milestone 4.3 Admin CLI roadmap (v0)
  - **Purpose**: Implementation roadmap for GitHub Issue #33 (Admin CLI)
  - **Scope**: All 10 CLI commands (full scope per stakeholder decision)
  - 4 tasks: Scope Analysis → Test Suite → Implementation → Documentation
  - Timeline: 6-8 days (test-driven, architecture-first)
  - **Status**: Ready for Implementation

- **[03-scope_extension_evaluation_v0.md](./03-scope_extension_evaluation_v0.md)** 📦 **ARCHIVED** - Scope extension evaluation for Issues #33 and #34 (v0)
  - **Purpose**: Evaluate late-stage feature requests for v0.5.0 release
  - **Issue #33**: Admin CLI for User/Database CRUD (portability blocker)
  - **Issue #34**: Hot Reload Configuration (DX improvement)
  - Decision matrix and recommended action plan
  - **Original Recommendation**: #33 IMPLEMENT (reduced scope), #34 DEFER to v0.6.0
  - **Stakeholder Decision**: #33 IMPLEMENT (full scope) → See 04-admin_cli_roadmap_v0.md

- **[02-implementation_roadmap_v3.md](./02-implementation_roadmap_v3.md)** ⭐ **CURRENT** - Implementation roadmap for v0.4.0 → v0.5.0 (v3 - Final)
  - **NOTE**: Milestone 4.3 (Admin CLI) inserted between 4.2 and 5.1 per 04-admin_cli_roadmap_v0.md
  - **Changes from v2**: Added Context (1-4 bullets) and Rationale (1-2 sentences) to all 23 tasks, enhanced testing specifications (90% coverage target, style compliance, scope discipline), enhanced documentation gates (style guide compliance, integration analysis), added deferred feature (server-side multi-threading within single session)
  - **Purpose**: Actionable implementation roadmap aligned with Architecture Design v3
  - **Format**: Focused, comprehensive (707 lines)
  - 5 phases over 4 weeks: Foundation (1 week) → Tool Renaming (3 days) → State Migration (4 days) → Database Override (5 days) → Verification (3 days)
  - 7 milestones: 1.1 Foundation Core, 1.2 Foundation Integration, 2.1 Tool Renaming, 3.1 State Migration Tools, 3.2 State Migration Cleanup, 4.1 Database Override Models, 4.2 Multi-Tenancy Tools, 5.1 Verification & Release
  - 23 tasks with Context, Rationale, goals, pre-conditions, enhanced success gates
  - Git workflow with feature branch (feat/multi-arangodb-tenancy)
  - Versioning strategy (v0.4.1 → v0.5.0)
  - Topological ordering for parallel development
  - Success criteria (functional + quality requirements)
  - Deferred features (v0.6.0+: global stats aggregation, connection pool limits, session timeout cleanup, server-side multi-threading)
  - **Status**: Ready for Implementation

- **[02-implementation_roadmap_v2.md](./02-implementation_roadmap_v2.md)** 📦 **ARCHIVED** - Implementation roadmap v2
  - **Issue**: Missing Context and Rationale sections for tasks
  - **Issue**: Testing specifications lacked explicit coverage targets and scope discipline
  - **Issue**: Documentation gates lacked style guide compliance and integration analysis requirements
  - Superseded by v3 based on stakeholder feedback

- **[02-implementation_roadmap_v1.md](./02-implementation_roadmap_v1.md)** 📦 **ARCHIVED** - Implementation roadmap v1
  - **Issue**: Based on v0.3.2 → v0.4.0 (outdated version targets)
  - **Issue**: Missing v3 architecture decisions (terminology, per-tool override, session management)
  - Superseded by v2 based on v3 architecture design

- **[02-implementation_roadmap_v0.md](./02-implementation_roadmap_v0.md)** 📦 **ARCHIVED** - Implementation roadmap v0
  - Superseded by v1 based on organizational reporting standards

- **[00-multi_tenancy_assessment_v1.md](./00-multi_tenancy_assessment_v1.md)** 📦 **ARCHIVED** - Second iteration
  - **Issue**: Incorrectly recommended `click` library instead of `argparse`
  - **Issue**: Did not emphasize multi-server capability clearly enough
  - Superseded by v2 based on stakeholder clarifications

- **[00-multi_tenancy_assessment_v0.md](./00-multi_tenancy_assessment_v0.md)** 📦 **ARCHIVED** - Initial analysis
  - Superseded by v1 based on stakeholder feedback

---

## Quick Summary

### Critical Findings

**Multi-Tenancy Support:** ❌ **NOT SUPPORTED**

The current implementation enforces single-database operation through:

- Singleton ConnectionManager (single connection per process)
- Global lifespan context (single database shared across all requests)
- Static configuration (environment variables loaded once at startup)
- No per-request or per-connection database selection

**Port Configuration:** ⚠️ **EMBEDDED IN URL**

Port is embedded within `ARANGO_URL` environment variable (e.g., `http://localhost:8529`). There is **no separate `ARANGO_PORT` environment variable**.

### Architectural Barriers

1. **Singleton Connection Manager** (`db.py:25-99`) - Enforces single connection instance
2. **Global Lifespan Context** (`entry.py:157-221`) - Single database shared globally
3. **Static Configuration** (`config.py:45-72`) - Environment variables loaded once
4. **Tool Handler Signature** (`handlers.py:9-13`) - No database parameter support

### Recommended Approaches

#### Option A-Enhanced: Focused Database Context with Optional Override (⭐ RECOMMENDED)

- **Complexity:** Medium-High
- **Effort:** 5.5 weeks
- **Benefits:**
  - Single server instance (no context window pollution)
  - Natural LLM agent workflow (set context once, work within it)
  - No repeated database parameter in most calls
  - Flexible cross-database operations (optional override)
  - Backward compatible
  - **MCP Design Pattern support** (NEW in v0.4.0): Progressive Tool Discovery reduces tool loading from 43 to 2-5 tools
- **Implementation:**
  - Session-based focused database context (`set_focused_database()` tool)
  - Optional `database` parameter in all 43 tools for override
  - Multi-database connection pool
  - YAML configuration file for multiple databases
  - Enhanced SessionContextManager with workflow context and stage management

#### Approach 3B: Separate Administrative CLI (⭐ RECOMMENDED for Configuration)

- **Complexity:** Medium
- **Effort:** 1 week (included in 5.5 week total)
- **Benefits:**
  - Secure configuration management (no credential exposure to LLM)
  - Clear separation of concerns (admin vs. operational tasks)
  - Familiar CLI tool pattern
  - Uses `argparse` (already in codebase, no new dependencies)
  - Comprehensive status reporting (6 MCP tools for database resolution visibility)
  - **Design pattern integration** (NEW in v0.4.0): 8 additional tools for Progressive Tool Discovery, Context Switching, Tool Unloading
- **Implementation:**
  - CLI tool `mcp-arangodb-async db` for database configuration CRUD operations (using `argparse`)
  - CLI `status` command for users to inspect current configuration state
  - 14 MCP tools: 3 for context management + 3 for status reporting + 8 for design pattern management
  - YAML configuration file with environment variable references
  - Supports multiple ArangoDB server instances (different URLs/hosts)
  - Enhanced SessionContextManager with workflow context and stage tracking

#### Option C: Separate Server Instances (⚠️ STILL NOT RECOMMENDED, but less problematic with v0.4.0)

- **Complexity:** Low
- **Effort:** 0 (already implemented)
- **Limitations:**
  - **Context window pollution (mitigated in v0.4.0):** 43 tools × N instances = 43N tool definitions, BUT Progressive Tool Discovery can load just 2-5 tools per instance
  - **Still breaks local LLMs:** Even with design patterns, multiple instances add complexity
  - Resource overhead, complex deployment
  - Design patterns work BETTER with single instance (unified tool discovery, cross-database insights)
- **Use Only If:** Using large LLM providers (OpenAI, Anthropic) with 100K+ token context windows AND only 1-2 databases

### Implementation Recommendation

**Primary:** **Option A-Enhanced + Approach 3B (Hybrid)**

- **Multi-Tenancy:** Focused database context with optional override
- **Configuration:** Separate administrative CLI `mcp-arangodb-async db` (using `argparse`) + 14 MCP tools (3 context management + 3 status reporting + 8 design pattern management)
- **Multi-Server Support:** Yes - supports multiple ArangoDB server instances (different URLs/hosts)
- **Design Pattern Support:** Yes - Progressive Tool Discovery, Context Switching, Tool Unloading (NEW in v0.4.0)
- **Total Effort:** 5.5 weeks
- **Benefits:** Single server instance, natural LLM workflow, secure configuration management, comprehensive status reporting, context window optimization (load 2-5 tools instead of 43), no new dependencies

---

## Configuration Analysis

### Current Configuration Parameters

**ArangoDB Connection:**
- `ARANGO_URL` - Server URL with port (default: `http://localhost:8529`)
- `ARANGO_DB` - Database name (default: `_system`)
- `ARANGO_USERNAME` - Username (default: `root`)
- `ARANGO_PASSWORD` - Password (default: empty)
- `ARANGO_TIMEOUT_SEC` - Request timeout (default: `30.0`)

**Connection Tuning:**
- `ARANGO_CONNECT_RETRIES` - Retry attempts (default: `3`)
- `ARANGO_CONNECT_DELAY_SEC` - Retry delay (default: `1.0`)

**MCP Transport:**
- `MCP_TRANSPORT` - Transport type (default: `stdio`)
- `MCP_HTTP_HOST` - HTTP bind address (default: `0.0.0.0`)
- `MCP_HTTP_PORT` - HTTP port (default: `8000`)
- `MCP_HTTP_STATELESS` - Stateless mode (default: `false`)
- `MCP_HTTP_CORS_ORIGINS` - CORS origins (default: `*`)

**Logging:**
- `LOG_LEVEL` - Logging level (default: `INFO`)

### Configuration Lifecycle

**Static (Startup-Time Only):**
1. Server starts → `server_lifespan()` invoked
2. `load_config()` reads environment variables once
3. Connection created and stored in lifespan context
4. Configuration remains fixed until server restart

**No Dynamic Configuration:** Changing databases requires server restart.

---

## Multi-Tenancy Scenarios

### Scenario 1: Multiple Clients, Same Database
- ✅ **Supported** - All clients share the same database connection
- Use case: Multiple AI assistants accessing shared data

### Scenario 2: Multiple Clients, Different Databases
- ❌ **NOT Supported** - Requires separate server instances
- Workaround: Run multiple server processes with different environment configs

### Scenario 3: Single Client, Multiple Databases
- ❌ **NOT Supported** - Client cannot switch databases
- Workaround: Configure multiple MCP server entries in client config

---

## Industry Standards

### ArangoDB Native Multi-Tenancy

ArangoDB fully supports multiple databases per server instance:
- Multiple databases with isolated collections
- Per-database access control
- Single ArangoClient can access multiple databases

### python-arango Library Support

The underlying `python-arango` library fully supports multi-database access:

```python
from arango import ArangoClient

client = ArangoClient(hosts="http://localhost:8529")

# Access different databases
db1 = client.db("tenant1_db", username="user1", password="pass1")
db2 = client.db("tenant2_db", username="user2", password="pass2")
```

**Conclusion:** The limitation is in the MCP server architecture, not the database driver.

### Database Proxy Patterns

Common multi-tenant patterns:
1. **Separate Server Instances** (current approach) - Strong isolation, resource overhead
2. **Per-Request Database Selection** (recommended) - Single server, dynamic routing
3. **Schema-Based Multi-Tenancy** (not applicable to ArangoDB)
4. **Connection Pool Per Tenant** - Efficient reuse, complex management

---

## Security Considerations

### Current Design Security Posture

**Strengths:**
- ✅ Isolation by process
- ✅ No credential leakage
- ✅ Simple access control

**Multi-Tenancy Security Concerns (if implemented):**
- ❌ Credential management complexity
- ❌ Access control enforcement
- ❌ Connection exhaustion prevention
- ❌ Audit logging requirements

### Best Practices for Multi-Tenant Implementation

1. **Authentication layer** - Verify client identity
2. **Authorization layer** - Map client to allowed databases
3. **Connection limits** - Per-tenant quotas
4. **Audit trails** - Log all database access with tenant context

---

## Next Steps

### If Proceeding with Multi-Tenancy Implementation (Option A)

**Phase 2: Test Definition**
- Define test cases for multi-database scenarios
- Edge case validation (connection failures, credential errors)
- Performance testing with multiple databases
- Backward compatibility testing

**Phase 3: Implementation**
- Replace singleton ConnectionManager
- Add configuration file support
- Update tool models with database parameter
- Implement database resolution logic

**Phase 4: Documentation**
- Multi-tenancy configuration guide
- Security best practices
- Deployment patterns
- Migration guide from single-database

### If Maintaining Current Approach (Option C)

**Documentation Tasks:**
- Document multi-instance deployment patterns
- Provide Claude Desktop configuration examples
- Docker Compose multi-instance setup
- Resource planning guidelines

---

## Status

- ✅ Phase 1: Architectural Analysis - **COMPLETE** (v2 assessment + v3 architecture design + v3 integration design + v1 roadmap pending update)
- ⏳ Phase 2: Implementation - **READY TO START** (all design decisions finalized)
- ⏳ Phase 3: Documentation - Integrated throughout implementation (incremental documentation in Milestones 2.1, 3.2, 4.2, 5.2)

**Final Architecture (v3)**:
- **Version:** 0.4.0 → 0.5.0
- **Tool Count:** 43 tools (34 core + 9 design pattern)
- **Tool Renaming:** 3 tools (arango_switch_workflow, arango_get_active_workflow, arango_list_workflows)
- **Database Parameter:** 35 tools require optional `database` parameter
- **New Components:** SessionState, MultiDatabaseConnectionManager, ConfigFileLoader, database resolver, session ID extractor
- **New Tools:** 6 multi-tenancy tools (set/get focused database, list databases, test connection, etc.)
- **Implementation Timeline:** 4 weeks (5 phases)

**Key Architectural Decisions**:
1. ✅ Terminology → Rename "context" → "workflow" (eliminates ambiguity)
2. ✅ Session storage → `session_state.py` (new file, replaces global variables)
3. ✅ Session injection → `lifespan_context` (no handler signature changes)
4. ✅ Tool naming → `arango_` prefix (consistency with existing tools)
5. ✅ Concurrency → Sequential within session, concurrent across sessions
6. ✅ Database override → Optional `database` parameter on 35 data tools (per-tool override)
7. ✅ Async locks → `asyncio.Lock()` for state mutations
8. ✅ Session creation → Implicit on first tool call (no explicit session management tools)
9. ✅ Database resolution → 6-level priority fallback (tool arg → focused → config → env → first → hardcoded)

**Implementation Phases**:
- **Phase 1:** Foundation (SessionState, MultiDatabaseConnectionManager, ConfigFileLoader) - 1 week
- **Phase 2:** Tool Renaming (3 tools, all references) - 3 days
- **Phase 3:** State Migration (6 tools + 1 helper, global → per-session) - 1 week
- **Phase 4:** Database Override (35 tools, 6 multi-tenancy tools, CLI tool) - 1.5 weeks
- **Phase 5:** Verification (tests, documentation, release) - 3 days

---

**Last Updated:** 2025-11-22
**Analyst:** Augment Agent
**Project:** mcp-arangodb-async v0.4.0

