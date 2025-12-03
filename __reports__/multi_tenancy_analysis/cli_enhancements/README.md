# CLI Enhancements – Milestone 4.3

Analysis and design documents for the Admin CLI feature (GitHub Milestone #9).

## Documents

### Phase 1: Analysis

- **[00-cli_design_analysis_v2.md](./00-cli_design_analysis_v2.md)** ⭐ **CURRENT** - Final CLI design specification (v2)
  - Standardized `[CONSEQUENCE_TYPE]` result reporting format
  - Comprehensive side-effect feedback for all mutating operations
  - Unified format for `--dry-run` preview and actual execution
  - Implementation-ready with `ResultReporter` utility class
- [00-cli_design_analysis_v1.md](./00-cli_design_analysis_v1.md) - Previous version (design rationale)

## Quick Summary

### Final Design (v2)

1. **Command Structure**: Unified `db` hierarchy; config commands at `db config`
2. **Atomic Operations**: `--with-user` flag on `db add` for database+user creation
3. **Safety Features**: `--dry-run` preview + interactive confirmation with `--yes` bypass
4. **Result Reporting**: Standardized `[CONSEQUENCE_TYPE]` format for all operations
5. **Consistent Naming**: `add/remove` verbs with Unix aliases (`rm`, `ls`)

### Result Reporting Format

All mutating commands report consequences using consistent format:

```text
<command name>:
[ADDED] Database 'mydb'
[ADDED] User 'myuser' (active: true)
[GRANTED] Permission rw: myuser → mydb
```

For `--dry-run`, append `- DRY-RUN`:

```text
[ADDED - DRY-RUN] Database 'mydb'
```

### Consequence Types

| Type | Used By |
|------|---------|
| `ADDED` | `db add`, `db config add`, `user add` |
| `REMOVED` | `db remove`, `db config remove`, `user remove` |
| `GRANTED` | `user grant` |
| `REVOKED` | `user revoke` |
| `UPDATED` | `user password` |

### Command Structure

```text
mcp-arangodb-async
├── server, health           # Existing
├── version                  # NEW: Display version info
├── db                       # UNIFIED: Database management
│   ├── config               # MOVED: YAML config management
│   │   ├── add, remove|rm, list|ls, test, status
│   ├── add, remove|rm, list|ls  # NEW: ArangoDB database CRUD
└── user                     # NEW: ArangoDB user management
    ├── add, remove|rm, list|ls, grant, revoke (admin)
    ├── databases, password (self-service)
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v2 | 2025-12-03 | Enhanced result reporting with `[CONSEQUENCE_TYPE]` format; streamlined for implementation |
| v1 | 2025-12-03 | Merged `db` hierarchy, `--yes` pattern, consistent naming |
| v0 | 2025-12-03 | Initial analysis |

## Status

- ✅ Phase 1: Analysis Complete (v2 - Final Design)
- ⏳ Phase 2: Test Suite Development

---

**Last Updated**: 2025-12-03
