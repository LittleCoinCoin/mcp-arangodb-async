# Alias Documentation Locations Report

**Date:** 2025-12-31  
**Phase:** M5.T2 - Documentation Updates  
**Purpose:** Identify documentation files where collapsible alias sections should be added

---

## Executive Summary

This report identifies **7 documentation files** where collapsible sections with shorthand command aliases should be added. These files contain **126 total command examples** that would benefit from progressive disclosure of advanced shorthand syntax.

**Recommendation:** Add collapsible sections to reference and tutorial documentation while preserving the educational clarity of quickstart guides.

---

## Categorization

### ✅ Files to Update (7 files, 126 commands)

| File | Commands | Type | Priority | Rationale |
|------|----------|------|----------|-----------|
| `docs/user-guide/cli-reference.md` | 57 | Reference | **High** | Comprehensive CLI reference - users expect advanced options |
| `docs/getting-started/powershell-migration.md` | 39 | Migration | **High** | Migration guide - users are already experienced |
| `docs/user-guide/multi-tenancy-guide.md` | 11 | Tutorial | **Medium** | Tutorial with multiple examples |
| `docs/user-guide/multi-tenancy-scenarios/01-single-instance-single-database.md` | 5 | Tutorial | **Medium** | Step-by-step scenario |
| `docs/user-guide/multi-tenancy-scenarios/02-single-instance-multiple-databases.md` | 5 | Tutorial | **Medium** | Step-by-step scenario |
| `docs/user-guide/multi-tenancy-scenarios/03-multiple-instances-multiple-databases.md` | 6 | Tutorial | **Medium** | Step-by-step scenario |
| `docs/user-guide/troubleshooting.md` | 3 | Reference | **Low** | Troubleshooting examples |

### ❌ Files to Skip (5 files)

| File | Reason |
|------|--------|
| `docs/getting-started/quickstart.md` | Educational - first-time users need clarity |
| `docs/index.md` | Landing page - keep simple |
| `docs/getting-started/install-arangodb.md` | Installation guide - not CLI-focused |
| `docs/getting-started/install-from-source.md` | Installation guide - not CLI-focused |
| `docs/developer-guide/changelog.md` | Historical record - no updates needed |

---

## Detailed Analysis

### 1. `docs/user-guide/cli-reference.md` (57 commands)

**Priority:** High  
**Command Types:**
- Server commands: `maa server`, `maa health`, `maa version`
- DB config: `maa db config add/remove/list/test/status`
- DB operations: `maa db add/remove/list`
- User management: `maa user add/remove/list/grant/revoke/databases/password`

**Recommendation:**
- Add collapsible sections after each command example
- Include both individual alias examples and "power user" combined examples
- Example placement: After each command's "Basic Usage" section

**Sample Collapsible Section:**
```markdown
<details>
<summary>💡 Advanced: Shorthand aliases</summary>

**Using short aliases:**
```bash
maa db add mydb -u http://localhost:8529 -R ARANGO_ROOT_PASSWORD -P USER_PASSWORD
```

**Using medium aliases:**
```bash
maa db add mydb --url http://localhost:8529 --root-pw-env ARANGO_ROOT_PASSWORD --pw-env USER_PASSWORD
```
</details>
```

---

### 2. `docs/getting-started/powershell-migration.md` (39 commands)

**Priority:** High  
**Command Types:**
- All command types (comprehensive migration guide)
- Heavy focus on `db add`, `user add`, `user grant`

**Recommendation:**
- Add collapsible sections in the "Quick Reference Table" section
- Add a dedicated "Shorthand Aliases" section after the main migration examples
- Target audience is experienced users migrating from PowerShell

**Rationale:** Migration guide users are already familiar with CLI concepts and would appreciate efficiency gains from aliases.

---

### 3. `docs/user-guide/multi-tenancy-guide.md` (11 commands)

**Priority:** Medium  
**Command Types:**
- `maa db config add`
- `maa server`
- Focus on configuration and server startup

**Recommendation:**
- Add collapsible sections after the "Quick Start" examples
- Keep main examples verbose for clarity
- Add one comprehensive "power user" example at the end

---

### 4. Multi-Tenancy Scenarios (3 files, 16 commands total)

**Files:**
- `01-single-instance-single-database.md` (5 commands)
- `02-single-instance-multiple-databases.md` (5 commands)
- `03-multiple-instances-multiple-databases.md` (6 commands)

**Priority:** Medium  
**Command Types:**
- `maa db add --with-user`
- `maa db list`
- `maa db config add/test`

**Recommendation:**
- Add collapsible sections at the end of each scenario
- Title: "Advanced: Using Shorthand Aliases"
- Show the complete scenario workflow using aliases

**Rationale:** Tutorial users benefit from seeing the full verbose syntax first, then learning shortcuts after understanding the concepts.

---

### 5. `docs/user-guide/troubleshooting.md` (3 commands)

**Priority:** Low  
**Command Types:**
- `maa db add` (2 occurrences)
- `maa user grant` (1 occurrence)

**Recommendation:**
- Add minimal collapsible sections inline with each command
- Keep it brief - troubleshooting users want quick solutions

---

## Implementation Strategy

### Collapsible Section Template

```markdown
<details>
<summary>💡 Advanced: Shorthand aliases</summary>

**Short aliases (fastest):**
```bash
[command with -R, -P, -u, -d, -U, etc.]
```

**Medium aliases (readable):**
```bash
[command with --root-pw-env, --pw-env, etc.]
```

**Alias reference:**
- `-R` = `--arango-root-password-env` / `--root-pw-env`
- `-P` = `--arango-password-env` / `--pw-env`
- `-u` = `--url`
- `-d` = `--database`
- `-U` = `--username`
- `-p` = `--permission` / `--perm`

See [CLI Reference](../user-guide/cli-reference.md#alias-reference) for complete list.
</details>
```

### Placement Guidelines

1. **Reference docs** (cli-reference.md): After each command's basic example
2. **Migration guide** (powershell-migration.md): Dedicated section + inline examples
3. **Tutorials** (multi-tenancy): At end of each major section or scenario
4. **Troubleshooting**: Inline with each command example

---

## Summary

**Total files to update:** 7  
**Total commands affected:** 126  
**Estimated effort:** 3-4 hours (part of M5.T2)

**Next Steps:**
1. Update cli-reference.md (highest priority, most commands)
2. Update powershell-migration.md (high priority, experienced users)
3. Update multi-tenancy guides (medium priority, tutorial flow)
4. Update troubleshooting.md (low priority, minimal changes)

