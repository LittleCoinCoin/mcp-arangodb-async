# mcp-arangodb-async v0.4.0 – Multi-Tenancy Implementation Roadmap (v0 - Initial)

**Project**: mcp-arangodb-async – Model Context Protocol Server for ArangoDB  
**Roadmap Date**: 2025-11-08  
**Phase**: Planning  
**Source**: Architecture Design v1 + Stakeholder Decisions + Test-Driven Development Workflow  
**Current Version**: v0.3.2 (single-database, production)  
**Target Version**: v0.4.0 (multi-tenancy MVP, production-ready)  
**Timeline**: 5.5 weeks (test-driven, architecture-first approach)

---

## Executive Summary

This roadmap defines the implementation path for adding multi-tenancy capabilities to mcp-arangodb-async, enabling a single MCP server instance to manage multiple ArangoDB databases and servers through focused database context with optional per-tool override.

**Stakeholder Decisions**:
- ✅ **Multi-Tenancy Pattern**: Option A-Enhanced (Focused Database Context with Optional Override) - Single server instance, session-based context, no context window pollution
- ✅ **Configuration Management**: Approach 3B (CLI-based) - Secure admin-controlled configuration using `argparse`, YAML config file with environment variable references
- ✅ **CLI Framework**: Use `argparse` (already in codebase at `__main__.py:15`) - No new dependencies
- ✅ **CLI Command Name**: `mcp-arangodb-async db` - Clear, short, memorable
- ✅ **Status Reporting**: 6 MCP tools (3 context management + 3 comprehensive status reporting) - Full database resolution visibility
- ✅ **Multi-Server Support**: Yes - Supports multiple ArangoDB server instances (different URLs/hosts)
- ✅ **Backward Compatibility**: Mandatory - Existing environment variable configuration must continue to work

**Architectural Decision**:
Complete redesign of connection management architecture from singleton pattern to multi-database connection pool with session-based context management. This avoids retrofitting multi-tenancy support after implementation, which creates technical debt and maintenance challenges. The new architecture integrates multi-database support as a first-class concern from the ground up.

---

## Versioning Strategy

**Semantic Versioning (SemVer)**: `Major.Minor.Patch`

**Version Progression**:
- **Major Version**: 0 (pre-1.0 development) → 0 (maintained)
  - Major=0 enforced until v1.0.0 release (API stabilization)
  - Breaking changes allowed during Major=0 phase (pre-production)
  - Major=1 signals production-ready stable API

- **Minor Version**: Increments per Phase completion
  - Phase 1 complete → v0.3.3 (Core Infrastructure)
  - Phase 2 complete → v0.3.4 (CLI Tool)
  - Phase 3 complete → v0.3.5 (Context Management & Status Tools)
  - Phase 4 complete → v0.3.6 (Tool Model Updates)
  - Final release → v0.4.0 (Multi-Tenancy MVP)

- **Patch Version**: Increments per Milestone completion within a Phase
  - Milestone 1.1 complete → v0.3.3 (first milestone of Phase 1)
  - Milestone 1.2 complete → v0.3.3 (second milestone of Phase 1, no version bump)
  - Milestone 2.1 complete → v0.3.4 (first milestone of Phase 2)
  - Milestone 3.1 complete → v0.3.5 (first milestone of Phase 3)
  - Milestone 4.1 complete → v0.3.6 (first milestone of Phase 4)
  - Milestone 5.1 complete → v0.4.0 (final release)

- **Tasks**: Do NOT increment version (tasks are sub-units of milestones)

**Version Management**:
- Configured in `pyproject.toml` with `python-semantic-release`
- Automated version bumping based on conventional commits
- Git tags created automatically on version increments
- PyPI publishing triggered on v0.4.0 tag

---

## Git Workflow

**mcp-arangodb-async-Specific Branching Strategy** (Project Variation)

**Branch Hierarchy**:
```
main (production, v0.4.0 release only)
  └── dev (development integration branch)
      ├── milestone/1.1-core-infrastructure
      │   ├── task/1.1.1-test-definition
      │   ├── task/1.1.2-multi-db-manager
      │   ├── task/1.1.3-session-context-manager
      │   └── task/1.1.4-config-loader
      ├── milestone/2.1-cli-tool
      │   ├── task/2.1.1-test-definition
      │   ├── task/2.1.2-cli-implementation
      │   └── task/2.1.3-cli-integration
      ├── milestone/3.1-context-status-tools
      │   ├── task/3.1.1-test-definition
      │   ├── task/3.1.2-context-tools
      │   └── task/3.1.3-status-tools
      ├── milestone/4.1-tool-model-updates
      │   ├── task/4.1.1-test-definition
      │   ├── task/4.1.2-model-updates
      │   └── task/4.1.3-integration
      └── milestone/5.1-testing-documentation
          ├── task/5.1.1-e2e-tests
          ├── task/5.1.2-security-audit
          └── task/5.1.3-documentation
```

**Workflow Rules**:

1. **All work from `dev` branch** (not `main`)
   - `main` is production-only, receives merges only at v0.4.0 release
   - `dev` is the integration branch for all development work

2. **Milestone branches from `dev`**
   - Branch naming: `milestone/<milestone-id>-<short-description>`
   - Example: `milestone/1.1-core-infrastructure`
   - Created when milestone work begins
   - Deleted after merge back to `dev`

3. **Task branches from milestone branches**
   - Branch naming: `task/<task-id>-<short-description>`
   - Example: `task/1.1.1-test-definition`
   - Created when task work begins
   - Deleted after merge back to milestone branch

4. **Merge Hierarchy**:
   - Task branches → Milestone branch (when task complete)
   - Milestone branch → `dev` (when ALL milestone tasks complete)
   - `dev` → `main` (when milestone in `dev` passes ALL tests: regression, unit, integration, performance)

5. **Merge Criteria**:
   - **Task → Milestone**: Task success gates met, task tests pass
   - **Milestone → dev**: All milestone tasks complete, all milestone tests pass, no regressions
   - **dev → main**: ALL tests pass (regression, unit, integration, performance), ready for release

6. **Conventional Commits**:
   - Follow organization's conventional commit format
   - Enables automated semantic versioning
   - See `git-workflow.md` for commit message standards

**Note**: This is a mcp-arangodb-async-specific variation of the organization's standard git workflow, optimized for milestone-based development with strict quality gates.

---

## Phase 1: Core Infrastructure (Weeks 1-1.5)

**Version Target**: v0.3.3 (after all Phase 1 milestones complete)

**Objective**: Build foundational multi-database connection management and session context infrastructure with comprehensive test coverage.

### Milestone 1.1: Core Infrastructure Implementation (1.5 weeks)

**Version Target**: v0.3.3 (first and only milestone of Phase 1)

**Tasks**:

**1.1.1 – Test Definition for Core Infrastructure**
- **Goal**: Define comprehensive test suite for MultiDatabaseConnectionManager, SessionContextManager, and ConfigFileLoader before implementation
- **Pre-conditions**: Architecture Design v1 approved
- **Success Gates**:
  - Test definition report created following org's reporting guidelines
  - Unit tests defined for MultiDatabaseConnectionManager (connection pooling, thread safety, configuration loading)
  - Unit tests defined for SessionContextManager (session lifecycle, focused database management, thread safety)
  - Unit tests defined for ConfigFileLoader (YAML parsing, Pydantic validation, environment variable integration)
  - Integration tests defined for component interaction (config load → connection creation → session management)
  - Edge case tests defined (invalid YAML, missing env vars, connection failures, concurrent access)
  - User review and approval of test definition report

**1.1.2 – MultiDatabaseConnectionManager Implementation**
- **Goal**: Implement multi-database connection pool with thread-safe access and configuration management
- **Pre-conditions**: Task 1.1.1 complete (test definition approved)
- **Success Gates**:
  - `mcp_arangodb_async/multi_db_manager.py` created
  - `MultiDatabaseConnectionManager` class implemented with connection pooling
  - Thread-safe connection retrieval using `threading.Lock`
  - Configuration loading from YAML file and environment variables
  - Connection lifecycle management (create, reuse, cleanup)
  - All unit tests from 1.1.1 pass for MultiDatabaseConnectionManager
  - Code follows existing codebase patterns from `db.py:25-99`

**1.1.3 – SessionContextManager Implementation**
- **Goal**: Implement per-session focused database context management with thread safety
- **Pre-conditions**: Task 1.1.1 complete (test definition approved)
- **Success Gates**:
  - `mcp_arangodb_async/session_context.py` created
  - `SessionContextManager` class implemented
  - Thread-safe session context storage using `threading.Lock`
  - Session lifecycle management (set, get, clear, has_focused_database)
  - Database validation against configured databases
  - All unit tests from 1.1.1 pass for SessionContextManager
  - Integration with MultiDatabaseConnectionManager validated

**1.1.4 – ConfigFileLoader and Pydantic Models Implementation**
- **Goal**: Implement YAML configuration file loading with Pydantic validation and environment variable support
- **Pre-conditions**: Task 1.1.1 complete (test definition approved)
- **Success Gates**:
  - `mcp_arangodb_async/config_loader.py` created
  - `mcp_arangodb_async/config_models.py` created with Pydantic models
  - `ConfigFileLoader` class implemented with YAML parsing
  - `DatabaseConfig` and `ConfigFile` Pydantic models with validation
  - Environment variable reference support (password_env)
  - Backward compatibility with existing environment variables (ARANGO_URL, ARANGO_DB, etc.)
  - All unit tests from 1.1.1 pass for ConfigFileLoader
  - All integration tests from 1.1.1 pass
  - Test execution report generated and approved

---

## Phase 2: CLI Tool (Weeks 2-3)

**Version Target**: v0.3.4 (after all Phase 2 milestones complete)

**Objective**: Implement secure CLI-based configuration management tool for database CRUD operations and status inspection.

### Milestone 2.1: CLI Tool Implementation (1 week)

**Version Target**: v0.3.4 (first and only milestone of Phase 2)

**Tasks**:

**2.1.1 – Test Definition for CLI Tool**
- **Goal**: Define comprehensive test suite for CLI tool before implementation
- **Pre-conditions**: Milestone 1.1 complete (core infrastructure implemented and tested)
- **Success Gates**:
  - Test definition report created following org's reporting guidelines
  - CLI command tests defined (add, remove, list, update, test, status)
  - YAML file manipulation tests defined (create, update, delete entries)
  - Error handling tests defined (invalid inputs, missing files, permission errors)
  - Integration tests defined (CLI → ConfigFileLoader → YAML file)
  - User review and approval of test definition report

**2.1.2 – CLI Implementation**
- **Goal**: Implement argparse-based CLI tool with all database management commands
- **Pre-conditions**: Task 2.1.1 complete (test definition approved)
- **Success Gates**:
  - `mcp_arangodb_async/cli/db.py` created
  - argparse setup with subcommands (add, remove, list, update, test, status)
  - `handle_add()` command implemented (add database configuration)
  - `handle_remove()` command implemented (remove database configuration)
  - `handle_list()` command implemented (list all databases)
  - `handle_update()` command implemented (update database configuration)
  - `handle_test()` command implemented (test database connection)
  - `handle_status()` command implemented (show configuration status with connection testing)
  - All CLI tests from 2.1.1 pass
  - Follows existing argparse patterns from `__main__.py:15-70`

**2.1.3 – CLI Integration and Entry Point**
- **Goal**: Integrate CLI tool with project build system and validate end-to-end functionality
- **Pre-conditions**: Task 2.1.2 complete (CLI implementation tested)
- **Success Gates**:
  - CLI entry point added to `pyproject.toml` console scripts
  - CLI accessible via `mcp-arangodb-async db` command
  - YAML file correctly created/updated/deleted by CLI commands
  - File permissions set correctly (600 for config file, 700 for config directory)
  - All integration tests from 2.1.1 pass
  - Test execution report generated and approved

---

## Phase 3: Context Management & Status Tools (Weeks 3-4)

**Version Target**: v0.3.5 (after all Phase 3 milestones complete)

**Objective**: Implement 6 MCP tools for database context management and comprehensive status reporting.

### Milestone 3.1: Context Management Tools (0.5 weeks)

**Version Target**: v0.3.5 (first milestone of Phase 3)

**Tasks**:

**3.1.1 – Test Definition for Context Management Tools**
- **Goal**: Define comprehensive test suite for 3 context management MCP tools before implementation
- **Pre-conditions**: Milestone 2.1 complete (CLI tool implemented and tested)
- **Success Gates**:
  - Test definition report created following org's reporting guidelines
  - Tests defined for `set_focused_database()` tool (validation, session storage, error handling)
  - Tests defined for `get_focused_database()` tool (session retrieval, no session case)
  - Tests defined for `list_available_databases()` tool (database enumeration, no credentials exposed)
  - Integration tests defined (tool call → SessionContextManager → response)
  - Edge case tests defined (invalid database name, concurrent sessions, session cleanup)
  - User review and approval of test definition report

**3.1.2 – Context Management Tools Implementation**
- **Goal**: Implement 3 MCP tools for database context management
- **Pre-conditions**: Task 3.1.1 complete (test definition approved)
- **Success Gates**:
  - Tool models created in `mcp_arangodb_async/models.py` (SetFocusedDatabaseArgs, GetFocusedDatabaseArgs, ListAvailableDatabasesArgs)
  - `set_focused_database()` handler implemented in `mcp_arangodb_async/handlers.py`
  - `get_focused_database()` handler implemented
  - `list_available_databases()` handler implemented (read-only, no credentials)
  - Tools registered in TOOL_REGISTRY
  - Tool descriptions updated
  - All unit tests from 3.1.1 pass
  - Integration tests from 3.1.1 pass

### Milestone 3.2: Status Reporting Tools (0.5 weeks)

**Version Target**: v0.3.5 (second milestone of Phase 3)

**Tasks**:

**3.2.1 – Test Definition for Status Reporting Tools**
- **Goal**: Define comprehensive test suite for 3 status reporting MCP tools before implementation
- **Pre-conditions**: Milestone 3.1 complete (context management tools implemented and tested)
- **Success Gates**:
  - Test definition report created following org's reporting guidelines
  - Tests defined for extended `arango_database_status()` tool (multi-database context, connection status)
  - Tests defined for `arango_database_resolution_status()` tool (6-level priority preview, all resolution levels)
  - Tests defined for `arango_list_database_configs()` tool (all databases with connection status)
  - Integration tests defined (tool call → MultiDatabaseConnectionManager → connection testing → response)
  - Edge case tests defined (connection failures, missing databases, invalid configurations)
  - User review and approval of test definition report

**3.2.2 – Status Reporting Tools Implementation**
- **Goal**: Implement 3 MCP tools for comprehensive database status reporting
- **Pre-conditions**: Task 3.2.1 complete (test definition approved)
- **Success Gates**:
  - Existing `arango_database_status()` handler extended for multi-database context in `handlers.py:1725-1791`
  - `arango_database_resolution_status()` handler implemented (shows 6-level priority resolution)
  - `arango_list_database_configs()` handler implemented (lists all databases with connection testing)
  - Tool models created/updated in `models.py`
  - Tools registered in TOOL_REGISTRY
  - Tool descriptions updated
  - All unit tests from 3.2.1 pass
  - All integration tests from 3.2.1 pass
  - Test execution report generated and approved

---

## Phase 4: Tool Model Updates & Integration (Weeks 4-5)

**Version Target**: v0.3.6 (after all Phase 4 milestones complete)

**Objective**: Add optional database parameter to all 34 existing tools and integrate database resolution into server lifecycle.

### Milestone 4.1: Database Resolution Integration (0.5 weeks)

**Version Target**: v0.3.6 (first milestone of Phase 4)

**Tasks**:

**4.1.1 – Test Definition for Database Resolution**
- **Goal**: Define comprehensive test suite for database resolution algorithm and server lifecycle integration
- **Pre-conditions**: Milestone 3.2 complete (all 6 MCP tools implemented and tested)
- **Success Gates**:
  - Test definition report created following org's reporting guidelines
  - Tests defined for `resolve_database()` function (6-level priority algorithm)
  - Tests defined for updated `server_lifespan()` (multi-database context initialization)
  - Tests defined for updated `call_tool()` (database resolution, connection retrieval, tool execution)
  - Tests defined for session ID extraction (stdio and HTTP transports)
  - Integration tests defined (full request flow: tool call → resolution → connection → execution)
  - Edge case tests defined (missing session, invalid database, connection failures, fallback scenarios)
  - User review and approval of test definition report

**4.1.2 – Database Resolution Implementation**
- **Goal**: Implement database resolution algorithm and integrate into server lifecycle
- **Pre-conditions**: Task 4.1.1 complete (test definition approved)
- **Success Gates**:
  - `resolve_database()` function implemented with 6-level priority algorithm
  - `server_lifespan()` refactored in `entry.py:157-221` for multi-database context
  - `call_tool()` updated in `entry.py:324-420` with database resolution
  - Session ID extraction implemented for stdio and HTTP transports
  - Database connection retrieval from MultiDatabaseConnectionManager
  - All unit tests from 4.1.1 pass
  - All integration tests from 4.1.1 pass

### Milestone 4.2: Tool Model Updates (0.5 weeks)

**Version Target**: v0.3.6 (second milestone of Phase 4)

**Tasks**:

**4.2.1 – Test Definition for Tool Model Updates**
- **Goal**: Define test suite for optional database parameter in all 34 tools
- **Pre-conditions**: Milestone 4.1 complete (database resolution integrated)
- **Success Gates**:
  - Test definition report created following org's reporting guidelines
  - Tests defined for optional database parameter in representative tools (query, collection, document)
  - Tests defined for database override behavior (tool arg overrides session context)
  - Regression tests defined (existing functionality without database parameter)
  - Integration tests defined (database parameter → resolution → correct database used)
  - User review and approval of test definition report

**4.2.2 – Tool Model Updates Implementation**
- **Goal**: Add optional database parameter to all 34 existing tool Pydantic models
- **Pre-conditions**: Task 4.2.1 complete (test definition approved)
- **Success Gates**:
  - `database: Optional[str]` field added to all 34 tool Pydantic models
  - Tool descriptions updated to mention optional database parameter
  - Tool documentation updated
  - All unit tests from 4.2.1 pass
  - All regression tests from 4.2.1 pass
  - All integration tests from 4.2.1 pass
  - Backward compatibility validated (existing tool calls work without database parameter)
  - Test execution report generated and approved

---

## Phase 5: Testing, Security & Documentation (Weeks 5-5.5)

**Version Target**: v0.4.0 (Multi-Tenancy MVP - Production Release)

**Objective**: Comprehensive end-to-end testing, security audit, performance validation, and complete documentation.

### Milestone 5.1: End-to-End Testing & Security (0.5 weeks)

**Version Target**: v0.4.0 (first milestone of Phase 5)

**Tasks**:

**5.1.1 – End-to-End Integration Tests**
- **Goal**: Validate complete multi-tenancy workflows from LLM agent perspective
- **Pre-conditions**: Milestone 4.2 complete (all tool models updated and tested)
- **Success Gates**:
  - E2E test scenarios defined and implemented:
    - Scenario 1: Set focused database → query → verify correct database used
    - Scenario 2: Query with database override → verify override works
    - Scenario 3: Multiple sessions with different focused databases → verify isolation
    - Scenario 4: Database resolution priority → verify 6-level algorithm
    - Scenario 5: Backward compatibility → verify environment variable configuration works
  - All E2E tests pass
  - No regressions in existing functionality
  - Test execution report generated

**5.1.2 – Security Audit**
- **Goal**: Validate security posture of multi-tenancy implementation
- **Pre-conditions**: Task 5.1.1 complete (E2E tests passing)
- **Success Gates**:
  - Credential management audit complete (no passwords in config file, only env var references)
  - CLI access control validated (file permissions 600 for config, 700 for directory)
  - MCP tool security validated (no credential exposure via list_available_databases)
  - Connection pool security validated (connection limits, credential validation)
  - Audit logging validated (configuration changes, database access, focused database changes)
  - Security audit report generated and approved

**5.1.3 – Performance Testing**
- **Goal**: Validate performance characteristics of multi-database connection pool and session management
- **Pre-conditions**: Task 5.1.2 complete (security audit passed)
- **Success Gates**:
  - Connection pool performance benchmarked (connection creation, reuse, cleanup)
  - Session management performance benchmarked (concurrent sessions, context switching)
  - Database resolution performance benchmarked (6-level priority algorithm overhead)
  - Performance targets met (≤5% overhead vs. single-database baseline)
  - Performance test report generated and approved

### Milestone 5.2: Documentation & Release (0.5 weeks)

**Version Target**: v0.4.0 (final release milestone)

**Tasks**:

**5.2.1 – User Documentation**
- **Goal**: Create comprehensive user-facing documentation for multi-tenancy features
- **Pre-conditions**: Milestone 5.1 complete (testing, security, performance validated)
- **Success Gates**:
  - README.md updated with multi-database examples
  - Multi-tenancy configuration guide created
  - CLI tool usage guide created (mcp-arangodb-async db commands)
  - MCP tool reference updated (6 new/updated tools documented)
  - Migration guide created for existing users (environment variables → YAML config)
  - Deployment guide created for multi-database setups
  - Troubleshooting guide created (common issues, error messages, resolution steps)

**5.2.2 – API Reference Updates**
- **Goal**: Update API reference documentation for all changed components
- **Pre-conditions**: Task 5.2.1 complete (user documentation created)
- **Success Gates**:
  - API reference updated for MultiDatabaseConnectionManager
  - API reference updated for SessionContextManager
  - API reference updated for ConfigFileLoader
  - API reference updated for all 6 MCP tools
  - API reference updated for database resolution algorithm
  - Code examples added for common use cases
  - Docstrings validated for all public APIs

**5.2.3 – Release Preparation**
- **Goal**: Prepare v0.4.0 release with complete documentation and validation
- **Pre-conditions**: Task 5.2.2 complete (API reference updated)
- **Success Gates**:
  - All tests pass (unit, integration, E2E, regression, performance)
  - All documentation complete and accurate
  - CHANGELOG.md updated with v0.4.0 release notes
  - Version bumped to v0.4.0 in pyproject.toml
  - Git tag v0.4.0 created
  - Release notes prepared
  - PyPI publishing validated (dry-run)
  - Knowledge transfer report generated following org's reporting guidelines
  - Final release approval obtained

---

## Deferred Features (v0.5.0+)

**HTTP Session Store (Redis/Memcached)**:
- Rationale: In-memory session storage sufficient for MVP, external store needed for horizontal scaling
- Timeline: v0.5.0 release
- Benefit: Enables stateful HTTP sessions across multiple server instances
- Implementation: Add Redis/Memcached adapter for SessionContextManager

**Connection Pool Metrics and Monitoring**:
- Rationale: Basic connection management sufficient for MVP, advanced monitoring needed for production observability
- Timeline: v0.5.0 release
- Benefit: Provides visibility into connection pool health, usage patterns, and performance
- Implementation: Add Prometheus metrics for connection pool, session management, database resolution

**Dynamic Configuration Reload**:
- Rationale: Server restart acceptable for MVP, hot reload needed for zero-downtime configuration updates
- Timeline: v0.6.0 release
- Benefit: Enables configuration changes without server restart
- Implementation: Add file watcher for YAML config, implement safe configuration reload

**Per-Database Connection Limits**:
- Rationale: Global connection limit sufficient for MVP, per-database limits needed for resource isolation
- Timeline: v0.6.0 release
- Benefit: Prevents single database from exhausting connection pool
- Implementation: Add per-database connection limit configuration and enforcement

---

## Success Criteria for v0.4.0

**Functional Requirements**:
- ✅ Single MCP server instance supports multiple databases and multiple ArangoDB servers
- ✅ Session-based focused database context (set once, work within it)
- ✅ Optional database parameter in all 34 tools for per-call override
- ✅ CLI tool `mcp-arangodb-async db` for secure configuration management
- ✅ 6 MCP tools for database context and status reporting
- ✅ YAML configuration file with environment variable references
- ✅ 6-level database resolution algorithm (tool arg → session → config → env vars → default)
- ✅ Backward compatibility with existing environment variable configuration

**Quality Requirements**:
- ✅ Test coverage >90% for new components
- ✅ Performance ≤5% overhead vs. single-database baseline
- ✅ Platform support: Windows, Linux, macOS (existing support maintained)
- ✅ Security audit passed (credential management, access control, audit logging)
- ✅ Documentation complete (user guides, API reference, migration guide, troubleshooting)
- ✅ All existing tests pass (no regressions)
- ✅ All new tests pass (unit, integration, E2E, performance)

---

## Topological Ordering for Parallel Development

**Critical Path** (must complete in order):
1. Phase 1 (Core Infrastructure) → Phase 2 (CLI Tool) → Phase 3 (Context & Status Tools) → Phase 4 (Tool Model Updates) → Phase 5 (Testing & Documentation)

**Parallel Opportunities**:
- Milestone 3.1 (Context Management Tools) and Milestone 3.2 (Status Reporting Tools) can start simultaneously after Phase 2 complete
- Task 4.1.2 (Database Resolution Implementation) and Task 4.2.2 (Tool Model Updates) can run in parallel after their respective test definitions approved
- Tasks 5.1.1, 5.1.2, 5.1.3 (E2E Testing, Security Audit, Performance Testing) can run in parallel after Phase 4 complete
- Tasks 5.2.1, 5.2.2 (User Documentation, API Reference) can run in parallel after Milestone 5.1 complete

**Note**: Test definition tasks (X.X.1) must always complete before implementation tasks (X.X.2+) per test-driven development workflow.

---

**Report Version**: v0 (Initial)
**Status**: Ready for implementation
**Next Steps**: Create GitHub Issues for each task, assign to team members, begin Phase 1 with Milestone 1.1 (Core Infrastructure)

