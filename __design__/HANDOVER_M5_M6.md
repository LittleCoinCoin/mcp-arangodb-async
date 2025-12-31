# CLI Consistency Enhancement - M5 & M6 Handover

## Context

I've completed **Milestones 1-4** of the CLI consistency enhancement project. The core implementation is complete, and all tests are passing. Only documentation and release tasks remain.

**What's Done:**
- ✅ **M1:** Test Baseline & Preparation (1 commit)
- ✅ **M2:** Phase 1 - Standardization (11 commits)
- ✅ **M3:** Phase 2 - Tier 1 Aliases (3 commits)
- ✅ **M4:** Phase 3 - Tier 2 & 3 Aliases (4 commits)
- ✅ **Total:** 19 commits, all 80 tests passing

**Current State:**
```bash
Branch: enhance/cli-consistency
Tests: 80/80 passing (100% pass rate)
Commits: 20 (including roadmap update)
Latest: fd35a27 - "docs: update M5 roadmap to focus on multi-tenancy scenarios with collapsible sections"
```

## Implementation Summary

### ✅ Completed Features

**Standardization (M2):**
- Config file/path unified (`--config-file` ↔ `--config-path`)
- Password env standardized (`--arango-password-env` ↔ `--password-env`)
- New password env standardized (`--arango-new-password-env` ↔ `--new-password-env`)
- Environment file standardized (`--environment-file` ↔ `--env-file`)

**Aliases Added (M3 & M4):**
- **Tier 1 (Password):** `-R`, `-P`, `-N` + medium aliases (`--root-pw-env`, `--pw-env`, `--new-pw-env`)
- **Tier 2 (File/Path):** `-C`, `-E`, `-p` + medium aliases (`--cfgf`, `--cfgp`, `--envf`, `--perm`)
- **Tier 3 (Common):** `-u`, `-d`, `-U`

**Testing:**
- 4 backward compatibility tests added
- 18 test functions updated
- 100% backward compatibility maintained

## Your Task

Implement **Milestones 5 & 6** following the detailed roadmap in `__design__/cli-consistency-enhancement-roadmap.md`.

**Remaining Work:**
- **M5:** Phase 4 - Documentation (3-4 hours, 6 commits)
- **M6:** Final Validation & Release (1.5-2 hours, 4 commits)

**Total:** ~10 commits, 4.5-6 hours

## M5: Documentation (Phase 4)

### M5.T1: Update CLI Reference Documentation (2-3 hours)

**Goal:** Update `docs/user-guide/cli-reference.md` with alias tables for all commands.

**Key Tasks:**
1. **M5.T1.S1:** Update server command documentation with alias table
2. **M5.T1.S2:** Update all db config and db/user operations with alias tables

**Example Format:**
```markdown
**Arguments:**

| Argument | Aliases | Description |
|----------|---------|-------------|
| `--url` | `-u` | ArangoDB server URL |
| `--database` | `-d` | Database name |
| `--arango-password-env` | `--password-env`, `--pw-env`, `-P` | Environment variable containing password |
```

**Files to Update:**
- `docs/user-guide/cli-reference.md` (all command sections)

---

### M5.T2: Add Collapsible Alias Sections to Tutorials (2 hours)

**Goal:** Add collapsible sections with shorthand examples to multi-tenancy guides while preserving educational clarity.

**Key Tasks:**
1. **M5.T2.S1:** Add collapsible section to `docs/user-guide/multi-tenancy-guide.md`
2. **M5.T2.S2:** Add collapsible sections to 3 multi-tenancy scenario files
3. **M5.T2.S3:** Add collapsible sections to `docs/user-guide/troubleshooting.md`

**Collapsible Section Template:**
```markdown
<details>
<summary>💡 Advanced: Using shorthand aliases</summary>

**Short aliases (fastest):**
```bash
maa db add mydb -u http://localhost:8529 -R ROOT_PW -P USER_PW
```

**Alias reference:**
- `-u` = `--url`
- `-R` = `--arango-root-password-env` / `--root-pw-env`
- `-P` = `--arango-password-env` / `--pw-env`

See [CLI Reference](../cli-reference.md) for complete list.
</details>
```

**Files to Update:**
- `docs/user-guide/multi-tenancy-guide.md`
- `docs/user-guide/multi-tenancy-scenarios/01-single-instance-single-database.md`
- `docs/user-guide/multi-tenancy-scenarios/02-single-instance-multiple-databases.md`
- `docs/user-guide/multi-tenancy-scenarios/03-multiple-instances-multiple-databases.md`
- `docs/user-guide/troubleshooting.md`

**Important:** Keep verbose examples as primary. Aliases go in collapsible sections only.

---

### M5.T3: Update README and Changelog (1 hour)

**Key Tasks:**
1. **M5.T3.S1:** Update README with alias mention (OPTIONAL - keep minimal)
2. **M5.T3.S2:** Add changelog entry for v0.6.0

**Changelog Entry Location:** `docs/developer-guide/changelog.md` (after line 44)

**Version:** 0.6.0 (MINOR - new feature with backward compatibility)

---

## M6: Final Validation & Release (1.5-2 hours)

### M6.T1: Final Test Suite Run (30 minutes)

**Commands:**
```bash
pytest tests/ -v --tb=short
pytest tests/test_cli_args_unit.py tests/test_cli_db_unit.py tests/test_admin_cli.py -v
```

**Manual Verification:**
```bash
maa server --help
maa db config add --help
maa db add --help
maa user add --help
```

---

### M6.T2: Version Bump and Release Preparation (30 minutes)

**Tasks:**
1. **M6.T2.S1:** Bump version to 0.6.0
   ```bash
   python scripts/bvn.py --version "0.6.0" --pypi false
   ```

2. **M6.T2.S2:** Finalize changelog with release date
   - Update `## [0.6.0] - 2025-01-XX` with actual date

---

### M6.T3: Create Pull Request (30 minutes)

**Command:**
```bash
git push origin enhance/cli-consistency
gh pr create --title "feat: CLI consistency enhancement with 3-tier alias system (v0.6.0)" --base master --head enhance/cli-consistency
```

**PR Description:** See roadmap section M6.T3.S1 for complete PR body template.

---

## Critical Resources

### Primary Documentation
1. **Roadmap:** `__design__/cli-consistency-enhancement-roadmap.md`
   - Complete step-by-step instructions for M5 & M6
   - Exact commit messages
   - Verification commands

2. **Documentation Locations Report:** `__reports__/cli-consistency/03-alias-documentation-locations_v1.md`
   - Analysis of which files need updates
   - Rationale for each file
   - Implementation strategy

3. **Architecture Analysis:** `__reports__/cli-consistency/00-architecture_analysis_v1.md`
   - Complete alias mapping
   - Design decisions

### Key Principles

1. **Educational Clarity:** Verbose examples remain primary in all documentation
2. **Progressive Disclosure:** Aliases in collapsible sections only
3. **Focus on Tutorials:** Multi-tenancy scenarios are high priority
4. **No Noise:** Skip quickstart guides and README (keep minimal)

---

## Expected Outcome

After completing M5 & M6:
- ✅ Version bumped to 0.6.0
- ✅ All documentation updated with collapsible alias sections
- ✅ Changelog entry added
- ✅ Pull request created and ready for merge
- ✅ 80 tests passing
- ✅ Zero breaking changes

---

## Start Here

Begin with **Milestone 5, Task 1, Step 1** (M5.T1.S1) in the roadmap:
- File: `docs/user-guide/cli-reference.md`
- Change: Update server command section with alias table
- Commit: `"docs: update server command with config file aliases"`

The roadmap has everything you need. Follow it step by step.

