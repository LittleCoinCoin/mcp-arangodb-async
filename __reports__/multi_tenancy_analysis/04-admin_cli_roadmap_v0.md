# Milestone 4.3: Admin CLI – Implementation Roadmap (v0)

**Project**: mcp-arangodb-async – Model Context Protocol Server for ArangoDB  
**Roadmap Date**: 2025-12-02  
**Phase**: Implementation  
**Source**: GitHub Issue #33 + Stakeholder Decision (2025-12-02) + Code Change Phases  
**Current Version**: v0.4.x (Phase 4.2 complete)  
**Milestone Target**: Milestone 4.3 (precedes Phase 5 Verification & Release)  
**Timeline**: 6-8 days (test-driven, architecture-first approach)

---

## Executive Summary

This roadmap defines Milestone 4.3, a new milestone inserted between the completed Milestone 4.2 (Multi-Tenancy Tools) and Phase 5 (Verification & Release). It implements a cross-platform Python CLI to replace the Windows-only `scripts/setup-arango.ps1` and provide comprehensive user/database management.

**Stakeholder Decision (2025-12-02)**:
- ✅ **Full Scope**: All 10 CLI commands from Issue #33 (no reduction)
- ✅ **Proper Engineering**: Follow `code-change-phases.instructions.md` cycle
- ✅ **Milestone Placement**: Insert as Milestone 4.3 before Phase 5

**Key Features**:
- Admin user CRUD: `create`, `delete`, `list`, `grant`, `revoke` (5 commands)
- Admin database CRUD: `create`, `delete`, `list` (3 commands)
- User self-service: `databases`, `password` (2 commands)

**Architectural Decision**:
Extend existing argparse CLI infrastructure with two new subcommand groups (`admin` and `user`). Root authentication via environment variables (consistent with existing password handling patterns). No new dependencies required (python-arango already provides all needed APIs).

---

## Scope Alignment

**GitHub Issue #33 - Full Scope**:

| Command Group | Command | Description | Phase |
|---------------|---------|-------------|-------|
| `admin user` | `create` | Create ArangoDB user | Implementation |
| `admin user` | `delete` | Delete ArangoDB user | Implementation |
| `admin user` | `list` | List ArangoDB users | Implementation |
| `admin user` | `grant` | Grant user access to database | Implementation |
| `admin user` | `revoke` | Revoke user access from database | Implementation |
| `admin database` | `create` | Create ArangoDB database | Implementation |
| `admin database` | `delete` | Delete ArangoDB database | Implementation |
| `admin database` | `list` | List ArangoDB databases | Implementation |
| `user` | `databases` | List databases accessible to user | Implementation |
| `user` | `password` | Change user's own password | Implementation |

**Deprecation Target**: `scripts/setup-arango.ps1` (after CLI complete)

---

## Git Workflow

**Branch Hierarchy**: 
```
main
  └── dev
      └── feat/multi-arangodb-tenancy
          └── milestone/4.3-admin-cli
              ├── task/4.3.1-scope-analysis
              ├── task/4.3.2-test-suite
              ├── task/4.3.3-implementation
              └── task/4.3.4-documentation
```

**Workflow Rules**:
1. All work from `feat/multi-arangodb-tenancy` branch (existing feature branch)
2. Milestone branch `milestone/4.3-admin-cli` from `feat/multi-arangodb-tenancy`
3. Task branches from milestone branch
4. Merge hierarchy: Task → Milestone → Feature → Dev → Main
5. Conventional commits for automated versioning

---

## Milestone 4.3: Admin CLI (6-8 days)

**Version Target**: No version increment (tasks are sub-units of milestones)

**Objective**: Implement cross-platform Python CLI for ArangoDB user and database management, replacing Windows-only PowerShell script.

### Task 4.3.1 – Scope Analysis & Design (1 day)

**Context**:
- Code Change Phases, Phase 1: Architectural Analysis
- Requires study of python-arango user/database management APIs
- Defines design decisions for all 10 CLI commands
- Stakeholder review gate before implementation

**Rationale**: Proper scope analysis prevents implementation churn and ensures all design decisions are vetted before coding begins.

**Goal**: Produce design document defining CLI structure, authentication patterns, and API mappings

**Pre-conditions**: Milestone 4.2 complete

**Success Gates**:
- **python-arango API Study**: Document all required methods:
  - `sys_db.create_user()`, `sys_db.delete_user()`, `sys_db.users()`, `sys_db.has_user()`
  - `sys_db.update_permission()`, `sys_db.reset_permission()`, `sys_db.permissions()`
  - `sys_db.create_database()`, `sys_db.delete_database()`, `sys_db.databases()`, `sys_db.has_database()`
  - `db.update_user()` (for password change)
- **Design Decision 1: CLI Structure** - Define argument structure:
  - Subcommand hierarchy: `admin user <action>`, `admin database <action>`, `user <action>`
  - Argument naming: positional vs named (e.g., `--password-env` vs positional)
  - Flag naming conventions (e.g., `--permission`, `--active`)
  - Collision analysis with existing `db` subcommand (from Task 4.2.2)
- **Design Decision 2: Authentication** - Define authentication patterns:
  - Root credential source: `ARANGO_ROOT_PASSWORD` env var (required for admin commands)
  - User credential source: `ARANGO_USER_PASSWORD` env var or interactive prompt
  - URL source: `ARANGO_URL` env var (consistent with existing config)
  - Error handling for missing/invalid credentials
- **Design Decision 3: Output Format** - Define output patterns:
  - List commands: Table format for human, JSON flag for scripts (`--json`)
  - Success messages: Human-readable confirmation
  - Error messages: Consistent format with exit codes
- **Design Decision 4: Permission Levels** - Define supported permission levels:
  - Valid values: `rw` (read-write), `ro` (read-only), `none` (no access)
  - Default for grant: `rw` (consistent with setup-arango.ps1)
- **Recommended Approach**: Clear selection with rationale for each design decision
- **Trade-off Analysis**: Document trade-offs for each decision
- **Comparison with setup-arango.ps1**: Document feature parity and extensions
- **Stakeholder Review**: Design document reviewed and approved before implementation

### Task 4.3.2 – Test Suite Development (1-2 days)

**Context**:
- Code Change Phases, Phase 2: Comprehensive Test Suite Development
- Test-driven approach: tests written before implementation
- Requires mock objects for ArangoDB connections (no real DB in unit tests)
- Integration tests may use containerized ArangoDB

**Rationale**: Test-first development ensures implementation matches design specifications and prevents scope creep during coding.

**Goal**: Create comprehensive test suite for all 10 CLI commands

**Pre-conditions**: Task 4.3.1 complete (design decisions finalized)

**Success Gates**:
- **Test File**: `tests/test_admin_cli.py` created
- **Admin User Tests**: 5 tests covering create, delete, list, grant, revoke
  - Test successful operations with mocked responses
  - Test error cases (user exists, user not found, permission denied)
  - Test argument validation (missing required args, invalid values)
- **Admin Database Tests**: 3 tests covering create, delete, list
  - Test successful operations with mocked responses
  - Test error cases (database exists, database not found)
  - Test edge cases (system database protection)
- **User Self-Service Tests**: 2 tests covering databases, password
  - Test successful operations with mocked responses
  - Test error cases (invalid credentials)
- **CLI Integration Tests**: Tests for argument parsing and help output
- **Mock Strategy**: Use `unittest.mock` or `pytest-mock` for ArangoDB client mocking
- **Coverage Target**: 100% coverage for test file itself (tests test all branches)
- **Style Compliance**: Tests follow existing test style and conventions

### Task 4.3.3 – Core Implementation (3-4 days)

**Context**:
- Code Change Phases, Phase 3: Core Feature Implementation + Phase 4: Debugging
- Implements all 10 CLI commands as defined in Task 4.3.1
- Iterates until all tests from Task 4.3.2 pass

**Rationale**: Implementation is bounded by pre-defined tests, ensuring feature completeness and preventing over-engineering.

**Goal**: Implement all 10 CLI commands with 100% test pass rate

**Pre-conditions**: Task 4.3.2 complete (test suite created)

**Success Gates**:
- **CLI Module**: `mcp_arangodb_async/admin_cli.py` created (or extension to `__main__.py`)
- **Admin User Commands**:
  - `mcp-arangodb-async admin user create <username> --password-env VAR [--active]`
  - `mcp-arangodb-async admin user delete <username>`
  - `mcp-arangodb-async admin user list [--json]`
  - `mcp-arangodb-async admin user grant <username> <database> [--permission rw|ro]`
  - `mcp-arangodb-async admin user revoke <username> <database>`
- **Admin Database Commands**:
  - `mcp-arangodb-async admin database create <name>`
  - `mcp-arangodb-async admin database delete <name>`
  - `mcp-arangodb-async admin database list [--json]`
- **User Self-Service Commands**:
  - `mcp-arangodb-async user databases [--json]`
  - `mcp-arangodb-async user password [--password-env VAR]`
- **Error Handling**: Clear error messages for all failure modes
- **Exit Codes**: 0 for success, non-zero for failures
- **Test Pass Rate**: 100% of tests from Task 4.3.2 pass
- **Coverage Target**: 90% code coverage for new code
- **Cross-Platform**: Works on Windows, macOS, Linux

### Task 4.3.4 – Documentation & Cleanup (1 day)

**Context**:
- Code Change Phases, Phase 6: Documentation Creation + Phase 7: Documentation Commits
- Documents all 10 CLI commands
- Creates migration guide from PowerShell script
- Deprecates `scripts/setup-arango.ps1`

**Rationale**: Comprehensive documentation enables adoption and reduces support burden.

**Goal**: Document CLI commands and deprecate PowerShell script

**Pre-conditions**: Task 4.3.3 complete (implementation done)

**Success Gates**:
- **CLI Reference**: `docs/cli/admin-commands.md` created
  - Documents all 10 commands with examples
  - Documents environment variables
  - Documents exit codes and error messages
- **Migration Guide**: `docs/migration/powershell-to-python-cli.md` created
  - Maps setup-arango.ps1 functionality to new CLI
  - Provides step-by-step migration instructions
- **PowerShell Deprecation**:
  - `scripts/setup-arango.ps1` marked as deprecated (comment header)
  - README updated to point to new CLI
- **README Update**: Add Admin CLI section with quick examples
- **Help Text**: All commands have comprehensive `--help` output
- **Style Guide Compliance**: Documentation follows project style guide

---

## Deferred Features (v0.6.0+)

**Batch Operations**:
- **Rationale**: Issue #33 specifies single-item operations; batch deferred for simplicity
- **Timeline**: v0.6.0 release
- **Benefit**: Create multiple users/databases in single command
- **Implementation**: `--batch` flag or YAML input file

**Interactive Mode**:
- **Rationale**: v0.5.0 uses env vars for passwords; interactive prompts deferred
- **Timeline**: v0.6.0 release
- **Benefit**: More user-friendly for manual operations
- **Implementation**: `--interactive` flag with password prompts

---

## Success Criteria for Milestone 4.3

**Functional Requirements**:
- ✅ All 10 CLI commands implemented and tested
- ✅ Cross-platform support (Windows, macOS, Linux)
- ✅ Root authentication via environment variables
- ✅ User authentication via environment variables
- ✅ Feature parity with `scripts/setup-arango.ps1`
- ✅ PowerShell script deprecated with migration guide

**Quality Requirements**:
- ✅ Test coverage ≥90% for new code
- ✅ 100% test pass rate
- ✅ Documentation complete
- ✅ Help text for all commands
- ✅ Clear error messages

---

## Topological Ordering

**Critical Path** (must complete in order):
1. Task 4.3.1 (Scope Analysis) → Task 4.3.2 (Test Suite) → Task 4.3.3 (Implementation) → Task 4.3.4 (Documentation)

**No Parallel Opportunities**: All tasks have linear dependencies.

---

## References

- [GitHub Issue #33](https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/33)
- [python-arango User Management](https://docs.python-arango.com/)
- [Code Change Phases](../../cracking-shells-playbook/instructions/code-change-phases.instructions.md)
- [Roadmap v3](./02-implementation_roadmap_v3.md) (parent roadmap)
- [PowerShell Script](../../scripts/setup-arango.ps1) (to be deprecated)

---

**Report Version**: v0
**Status**: Ready for Implementation
**Next Steps**: Begin Task 4.3.1 - Scope Analysis & Design

