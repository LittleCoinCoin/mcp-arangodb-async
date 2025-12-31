# Implementation Roadmap: CLI Consistency Enhancement

**Mode:** Mode 2 (Milestone Plan)
**Target Version:** 0.5.1 (PATCH version bump - usability improvement)
**Current Version:** 0.5.0
**Status:** Implementation Ready
**Created:** 2025-12-31

---

## Executive Summary

This roadmap implements a comprehensive CLI consistency enhancement for the mcp-arangodb-async project, adding argument aliases and standardizing naming conventions across all CLI commands. The enhancement improves user experience through shorter, more ergonomic command-line arguments while maintaining 100% backward compatibility.

**Key Deliverables:**
- Standardized argument naming (config file/path, password env, environment file)
- 3-tier alias system (primary + medium + short)
- 9 new short aliases (`-R`, `-P`, `-N`, `-C`, `-E`, `-p`, `-u`, `-d`, `-U`)
- Updated documentation and help text
- Comprehensive test coverage

**Total Estimated Effort:** 14.5-22.5 hours (12-20 hours implementation + 2.5 hours testing)

---

## Version Planning

### Target Version: 0.5.1

**Rationale for PATCH version bump:**
- ✅ Usability improvement: CLI argument aliases for better ergonomics
- ✅ Backward compatible: All existing argument names remain valid
- ✅ No breaking changes: Existing scripts continue to work unchanged
- ✅ No new functionality: Just convenience aliases for existing arguments
- ✅ Follows semantic versioning: PATCH = backward-compatible improvements

**Version Bump Command:**
```bash
python scripts/bvn.py --version "0.5.1" --pypi false
```

**Changelog Entry:**
```markdown
## [0.5.1] - 2025-01-XX

### Added
- **CLI Argument Aliases**: 3-tier alias system for improved ergonomics
  - Short aliases: `-R`, `-P`, `-N`, `-C`, `-E`, `-p`, `-u`, `-d`, `-U`
  - Medium aliases: `--root-pw-env`, `--pw-env`, `--new-pw-env`, `--cfgf`, `--cfgp`, `--envf`, `--perm`
  - Standardized naming: `--arango-new-password-env`, `--environment-file`, `--config-file`
- **Backward Compatibility**: All existing argument names remain valid as aliases
  - `--password-env` → `--arango-password-env` (in `db config add`)
  - `--new-password-env` → `--arango-new-password-env` (in `user password`)
  - `--config-path` → `--config-file` (everywhere)
  - `--env-file` → `--environment-file` (everywhere)

### Changed
- **Help Text**: All commands now document available aliases
- **Documentation**: CLI reference updated with alias tables and examples

### Technical Details
- 40-50% character reduction for common operations using short aliases
- Zero breaking changes: 100% backward compatibility maintained
- Argparse-based alias resolution (no custom parsing logic)
- Usability enhancement only - no new functionality added
```

---

## Milestone Overview

| Milestone | Description | Tasks | Estimated Effort |
|-----------|-------------|-------|------------------|
| **M1** | Test Baseline & Preparation | 2 | 1.5 hours |
| **M2** | Phase 1: Standardization | 4 | 3-5 hours |
| **M3** | Phase 2: Tier 1 Aliases | 3 | 4-6 hours |
| **M4** | Phase 3: Tier 2 & 3 Aliases | 3 | 2-4 hours |
| **M5** | Phase 4: Documentation | 3 | 4-6 hours |
| **M6** | Final Validation & Release | 3 | 1.5-2 hours |
| **Total** | | **18 tasks** | **14.5-22.5 hours** |

---

## Milestone 1: Test Baseline & Preparation

**Goal:** Establish test baseline and prepare for implementation

**Pre-conditions:**
- Current version is 0.5.0
- All existing tests pass
- Git working directory is clean

**Success Gate:**
- ✅ Test baseline documented (100% pass rate)
- ✅ Branch created: `enhance/cli-consistency`
- ✅ Reports reviewed and approved

---

### M1.T1: Establish Test Baseline

**Estimated Effort:** 30 minutes

**Pre-conditions:**
- All dependencies installed
- Test environment configured

**Success Criteria:**
- All existing CLI tests pass
- Pass rate documented

#### M1.T1.S1: Run existing test suite

**Commit Message:** `test: establish baseline for CLI tests before enhancement`

**Commands:**
```bash
# Run CLI-related tests
pytest tests/test_cli_args_unit.py -v --tb=short
pytest tests/test_cli_db_unit.py -v --tb=short
pytest tests/test_admin_cli.py -v --tb=short

# Document results
echo "Test Baseline - $(date)" > test_baseline.txt
pytest tests/test_cli_args_unit.py tests/test_cli_db_unit.py tests/test_admin_cli.py -v --tb=line >> test_baseline.txt
```

**Verification:**
```bash
# Should show 100% pass rate
grep -E "(PASSED|FAILED)" test_baseline.txt | wc -l
```

**Files Modified:** None (baseline only)

---

### M1.T2: Create Feature Branch

**Estimated Effort:** 15 minutes

**Pre-conditions:**
- Git working directory clean
- On `master` branch

**Success Criteria:**
- Feature branch created
- Reports committed to branch

#### M1.T2.S1: Create and switch to feature branch

**Commit Message:** `chore: create feature branch for CLI consistency enhancement`

**Commands:**
```bash
git checkout -b enhance/cli-consistency
git add __reports__/enhance_cli_consistency/
git add __design__/cli-consistency-enhancement-roadmap.md
git commit -m "docs: add Phase 1 & 2 reports and implementation roadmap for CLI enhancement"
```

**Verification:**
```bash
git branch --show-current  # Should show: enhance/cli-consistency
git log -1 --oneline       # Should show reports commit
```

**Files Modified:**
- `__reports__/enhance_cli_consistency/*.md` (committed)
- `__design__/cli-consistency-enhancement-roadmap.md` (committed)

---

## Milestone 2: Phase 1 - Standardization

**Goal:** Fix naming inconsistencies (config file/path, password env, environment file)

**Pre-conditions:**
- M1 complete (baseline established, branch created)
- Architecture report reviewed

**Success Gate:**
- ✅ Config file/path unified to `--config-file`
- ✅ Password env standardized to `--arango-password-env`
- ✅ New password env standardized to `--arango-new-password-env`
- ✅ Environment file standardized to `--environment-file`
- ✅ All backward compatibility aliases working
- ✅ Updated tests pass

---

### M2.T1: Unify Config File/Path Naming

**Estimated Effort:** 1-1.5 hours

**Pre-conditions:**
- Feature branch active
- Test baseline established

**Success Criteria:**
- `--config-file` is primary everywhere
- `--config-path` works as backward-compatible alias
- All `db config` commands use unified naming
- Server command accepts both forms

#### M2.T1.S1: Update server command argument parser

**Commit Message:** `feat(cli): add --config-path alias to server command for consistency`

**File:** `mcp_arangodb_async/__main__.py`

**Changes:**
```python
# Line 101-107: Update server_parser.add_argument
server_parser.add_argument(
    "--config-file",      # Primary name (existing)
    "--config-path",      # Backward compat (NEW: unified)
    "--cfgf",            # Medium alias (existing)
    "--cfgp",            # Medium alias (NEW: symmetric)
    "-C",                # Short alias (NEW: capital for file)
    dest="config_file",  # Keep existing dest
    default=None,
    help="Path to database configuration YAML file. Aliases: --config-path, --cfgf, --cfgp, -C",
)
```

**Verification:**
```bash
# Test both forms work
maa server --help | grep -E "(--config-file|--config-path|--cfgf|--cfgp|-C)"
python -c "import sys; sys.argv = ['maa', 'server', '--config-path', 'test.yaml']; from mcp_arangodb_async.__main__ import main"
```

**Files Modified:**
- `mcp_arangodb_async/__main__.py` (lines 101-107)

---

#### M2.T1.S2: Update db config commands argument parsers

**Commit Message:** `feat(cli): add --config-file alias to db config commands for consistency`

**File:** `mcp_arangodb_async/__main__.py`

**Changes:**
```python
# Lines 158-161, 169-172, 178-181, 187-190, 195-198
# Update all db config subcommands (add, remove, list, test, status)

# Example for config_add_parser (line 158):
config_add_parser.add_argument(
    "--config-file",      # Primary name (NEW: unified)
    "--config-path",      # Backward compat (OLD: keep working)
    "--cfgf",            # Medium alias (NEW)
    "--cfgp",            # Medium alias (NEW)
    "-C",                # Short alias (NEW)
    dest="config_path",  # Keep existing dest for handler compatibility
    default="config/databases.yaml",
    help="Path to configuration file. Aliases: --config-path, --cfgf, --cfgp, -C",
)

# Repeat for: config_remove_parser, config_list_parser, config_test_parser, config_status_parser
```

**Verification:**
```bash
# Test all db config commands accept both forms
maa db config add --help | grep -E "(--config-file|--config-path)"
maa db config list --help | grep -E "(--config-file|--config-path)"
```

**Files Modified:**
- `mcp_arangodb_async/__main__.py` (5 argument definitions updated)

---

#### M2.T1.S3: Update test files to use config_file parameter

**Commit Message:** `test: update db config tests to use config_file parameter name`

**Files:**
- `tests/test_cli_db_unit.py`
- `tests/test_admin_cli.py`

**Changes:**
```python
# test_cli_db_unit.py: Update all Namespace objects (15 functions)
# BEFORE:
args = Namespace(config_path=self.config_path)

# AFTER:
args = Namespace(config_file=self.config_path)

# test_admin_cli.py: Update TestDBConfig class (3 functions)
# Lines 158, 253, 369
# BEFORE:
args = Namespace(config_path=str(config_path), ...)

# AFTER:
args = Namespace(config_file=str(config_path), ...)
```

**Verification:**
```bash
# Run updated tests
pytest tests/test_cli_db_unit.py -v -k "config"
pytest tests/test_admin_cli.py::TestDBConfig -v
```

**Files Modified:**
- `tests/test_cli_db_unit.py` (~15 functions)
- `tests/test_admin_cli.py` (3 functions in TestDBConfig)

---

#### M2.T1.S4: Add backward compatibility test for --config-path

**Commit Message:** `test: add backward compatibility test for --config-path alias`

**File:** `tests/test_cli_args_unit.py`

**Changes:**
```python
# Add new test in TestCLIArgumentParsing class
def test_server_config_path_backward_compat(self):
    """Verify --config-path backward compatibility in server command."""
    with patch(
        "sys.argv",
        ["mcp_arangodb_async", "server", "--config-path", "/path/to/config.yaml"],
    ):
        with patch("mcp_arangodb_async.entry.main") as mock_entry:
            from mcp_arangodb_async.__main__ import main

            mock_entry.return_value = None
            result = main()

            # Should call with config_file kwarg (unified dest parameter)
            mock_entry.assert_called_once_with(config_file="/path/to/config.yaml")
            assert result == 0
```

**Verification:**
```bash
pytest tests/test_cli_args_unit.py::TestCLIArgumentParsing::test_server_config_path_backward_compat -v
```

**Files Modified:**
- `tests/test_cli_args_unit.py` (1 new test)

---

### M2.T2: Standardize Password Env Naming

**Estimated Effort:** 45 minutes

**Pre-conditions:**
- M2.T1 complete (config file/path unified)

**Success Criteria:**
- `--arango-password-env` is primary in `db config add`
- `--password-env` works as backward-compatible alias
- Tests updated to use standardized name

#### M2.T2.S1: Update db config add argument parser

**Commit Message:** `feat(cli): standardize to --arango-password-env in db config add`

**File:** `mcp_arangodb_async/__main__.py`

**Changes:**
```python
# Lines 141-145: Update config_add_parser.add_argument
config_add_parser.add_argument(
    "--arango-password-env",  # Primary name (NEW: standardized)
    "--password-env",         # Backward compat (OLD: keep working)
    "--pw-env",              # Medium alias (NEW)
    "-P",                    # Short alias (NEW)
    dest="password_env",     # Keep existing dest for handler compatibility
    required=True,
    help="Environment variable name containing password. Aliases: --password-env, --pw-env, -P",
)
```

**Verification:**
```bash
maa db config add --help | grep -E "(--arango-password-env|--password-env|--pw-env|-P)"
```

**Files Modified:**
- `mcp_arangodb_async/__main__.py` (lines 141-145)

---

#### M2.T2.S2: Update test files to use arango_password_env

**Commit Message:** `test: update db config add tests to use arango_password_env`

**File:** `tests/test_admin_cli.py`

**Changes:**
```python
# TestDBConfig class: Update 3 functions (lines 155, 250, 366)
# BEFORE:
args = Namespace(
    password_env="TEST_PASSWORD",
    ...
)

# AFTER:
args = Namespace(
    arango_password_env="TEST_PASSWORD",
    ...
)
```

**Verification:**
```bash
pytest tests/test_admin_cli.py::TestDBConfig -v
```

**Files Modified:**
- `tests/test_admin_cli.py` (3 functions in TestDBConfig)

---

#### M2.T2.S3: Add backward compatibility test for --password-env

**Commit Message:** `test: add backward compatibility test for --password-env alias`

**File:** `tests/test_admin_cli.py`

**Changes:**
```python
# Add new test in TestDBConfig class
def test_config_add_password_env_backward_compat(self, temp_config_dir, capsys):
    """Verify --password-env backward compatibility in db config add."""
    from mcp_arangodb_async import cli_db

    config_path = Path(temp_config_dir) / "databases.yaml"

    # Use OLD argument name (--password-env)
    args = Namespace(
        key="testdb",
        url="http://localhost:8529",
        database="test",
        username="testuser",
        password_env="TEST_PASSWORD",  # OLD name (backward compat)
        timeout=30.0,
        description="Test database",
        config_file=str(config_path),
        dry_run=False,
        yes=True,
    )

    result = cli_db.handle_add(args)
    assert result == EXIT_SUCCESS

    # Verify config was created correctly
    assert config_path.exists()
    with open(config_path) as f:
        config = yaml.safe_load(f)
    assert config["databases"]["testdb"]["password_env"] == "TEST_PASSWORD"
```

**Verification:**
```bash
pytest tests/test_admin_cli.py::TestDBConfig::test_config_add_password_env_backward_compat -v
```

**Files Modified:**
- `tests/test_admin_cli.py` (1 new test)

---

### M2.T3: Standardize New Password Env Naming

**Estimated Effort:** 30 minutes

**Pre-conditions:**
- M2.T2 complete (password env standardized)

**Success Criteria:**
- `--arango-new-password-env` is primary in `user password`
- `--new-password-env` works as backward-compatible alias
- Tests added for backward compatibility

#### M2.T3.S1: Update user password argument parser

**Commit Message:** `feat(cli): standardize to --arango-new-password-env in user password`

**File:** `mcp_arangodb_async/__main__.py`

**Changes:**
```python
# Lines 297: Update user_password_parser.add_argument
user_password_parser.add_argument(
    "--arango-new-password-env",  # Primary name (NEW: standardized)
    "--new-password-env",         # Backward compat (OLD: keep working)
    "--new-pw-env",              # Medium alias (NEW)
    "-N",                        # Short alias (NEW)
    dest="new_password_env",
    default="ARANGO_NEW_PASSWORD",
    help="New password env var (default: ARANGO_NEW_PASSWORD). Aliases: --new-password-env, --new-pw-env, -N",
)
```

**Verification:**
```bash
maa user password --help | grep -E "(--arango-new-password-env|--new-password-env|--new-pw-env|-N)"
```

**Files Modified:**
- `mcp_arangodb_async/__main__.py` (line 297)

---

#### M2.T3.S2: Add backward compatibility test for --new-password-env

**Commit Message:** `test: add backward compatibility test for --new-password-env alias`

**File:** `tests/test_admin_cli.py`

**Changes:**
```python
# Add new test in TestUserAdmin class
def test_user_password_new_password_env_backward_compat(
    self, mock_arango_client_user, mock_sys_db, capsys
):
    """Verify --new-password-env backward compatibility in user password."""
    mock_sys_db.has_user.return_value = True

    args = Namespace(
        username="testuser",
        env_file=None,
        arango_password_env=None,
        new_password_env="NEW_PASSWORD",  # OLD name (backward compat)
        dry_run=False,
        yes=True,
    )

    os.environ["ARANGO_PASSWORD"] = "oldpass"
    os.environ["NEW_PASSWORD"] = "newpass"

    result = cli_user.handle_user_password(args)
    assert result == EXIT_SUCCESS

    mock_sys_db.update_user.assert_called_once_with("testuser", "newpass")

    del os.environ["ARANGO_PASSWORD"]
    del os.environ["NEW_PASSWORD"]
```

**Verification:**
```bash
pytest tests/test_admin_cli.py::TestUserAdmin::test_user_password_new_password_env_backward_compat -v
```

**Files Modified:**
- `tests/test_admin_cli.py` (1 new test)

---

### M2.T4: Standardize Environment File Naming

**Estimated Effort:** 1 hour

**Pre-conditions:**
- M2.T3 complete (new password env standardized)

**Success Criteria:**
- `--environment-file` is primary everywhere
- `--env-file` works as backward-compatible alias
- All commands updated with new aliases

#### M2.T4.S1: Update all commands with --env-file argument

**Commit Message:** `feat(cli): standardize to --environment-file with --env-file alias`

**File:** `mcp_arangodb_async/__main__.py`

**Changes:**
```python
# Update all parsers that use --env-file (9 commands):
# - db_add_parser (line 208)
# - db_remove_parser (line 215)
# - db_list_parser (line 226)
# - user_add_parser (line 242)
# - user_remove_parser (line 251)
# - user_list_parser (line 259)
# - user_grant_parser (line 268)
# - user_revoke_parser (line 277)
# - user_databases_parser (line 285)
# - user_password_parser (line 295)

# Example for db_add_parser:
db_add_parser.add_argument(
    "--environment-file",  # Primary name (NEW: explicit)
    "--env-file",         # Backward compat (OLD: most common)
    "--envf",            # Medium alias (NEW)
    "-E",                # Short alias (NEW: capital for file)
    dest="env_file",     # Keep existing dest
    help="Path to .env file for credentials. Aliases: --env-file, --envf, -E",
)

# Repeat for all 10 commands
```

**Verification:**
```bash
# Test a few commands
maa db add --help | grep -E "(--environment-file|--env-file|--envf|-E)"
maa user add --help | grep -E "(--environment-file|--env-file|--envf|-E)"
```

**Files Modified:**
- `mcp_arangodb_async/__main__.py` (10 argument definitions updated)

---

#### M2.T4.S2: Run Phase 1 test suite

**Commit Message:** `test: verify Phase 1 standardization passes all tests`

**Commands:**
```bash
# Run all CLI tests
pytest tests/test_cli_args_unit.py -v
pytest tests/test_cli_db_unit.py -v
pytest tests/test_admin_cli.py -v

# Should show all tests passing including 3 new backward compat tests
```

**Verification:**
```bash
# Count new tests added
git diff master --stat tests/ | grep -E "(test_cli_args_unit|test_admin_cli)"

# Verify all pass
pytest tests/test_cli_args_unit.py tests/test_cli_db_unit.py tests/test_admin_cli.py --tb=line
```

**Files Modified:** None (verification only)

---

## Milestone 3: Phase 2 - Tier 1 Aliases (Password-Related)

**Goal:** Add medium and short aliases for password-related arguments

**Pre-conditions:**
- M2 complete (Phase 1 standardization done)
- All Phase 1 tests passing

**Success Gate:**
- ✅ `--arango-root-password-env` has `--root-pw-env` and `-R` aliases
- ✅ `--arango-password-env` has `--pw-env` and `-P` aliases (already added in M2)
- ✅ `--arango-new-password-env` has `--new-pw-env` and `-N` aliases (already added in M2)
- ✅ All tests still passing

---

### M3.T1: Add Aliases to --arango-root-password-env

**Estimated Effort:** 2-3 hours

**Pre-conditions:**
- Phase 1 complete

**Success Criteria:**
- All 9 commands with `--arango-root-password-env` have aliases
- Help text shows aliases

#### M3.T1.S1: Update db operations commands (3 commands)

**Commit Message:** `feat(cli): add --root-pw-env and -R aliases to db operations`

**File:** `mcp_arangodb_async/__main__.py`

**Changes:**
```python
# Update db_add_parser (line 209), db_remove_parser (line 216), db_list_parser (line 227)

# Example for db_add_parser:
db_add_parser.add_argument(
    "--arango-root-password-env",  # Primary name (existing)
    "--root-pw-env",              # Medium alias (NEW)
    "-R",                         # Short alias (NEW)
    dest="arango_root_password_env",
    help="Root password env var (default: ARANGO_ROOT_PASSWORD). Aliases: --root-pw-env, -R",
)
```

**Verification:**
```bash
maa db add --help | grep -E "(--arango-root-password-env|--root-pw-env|-R)"
maa db remove --help | grep -E "(--arango-root-password-env|--root-pw-env|-R)"
maa db list --help | grep -E "(--arango-root-password-env|--root-pw-env|-R)"
```

**Files Modified:**
- `mcp_arangodb_async/__main__.py` (3 argument definitions)

---

#### M3.T1.S2: Update user operations commands (6 commands)

**Commit Message:** `feat(cli): add --root-pw-env and -R aliases to user operations`

**File:** `mcp_arangodb_async/__main__.py`

**Changes:**
```python
# Update user_add_parser (line 243), user_remove_parser (line 252),
# user_list_parser (line 260), user_grant_parser (line 269),
# user_revoke_parser (line 278), user_databases_parser (line 286)

# Example for user_add_parser:
user_add_parser.add_argument(
    "--arango-root-password-env",  # Primary name (existing)
    "--root-pw-env",              # Medium alias (NEW)
    "-R",                         # Short alias (NEW)
    dest="arango_root_password_env",
    help="Root password env var (default: ARANGO_ROOT_PASSWORD). Aliases: --root-pw-env, -R",
)
```

**Verification:**
```bash
maa user add --help | grep -E "(--arango-root-password-env|--root-pw-env|-R)"
maa user grant --help | grep -E "(--arango-root-password-env|--root-pw-env|-R)"
```

**Files Modified:**
- `mcp_arangodb_async/__main__.py` (6 argument definitions)

---

### M3.T2: Add Aliases to --arango-password-env

**Estimated Effort:** 1 hour

**Pre-conditions:**
- M3.T1 complete

**Success Criteria:**
- All remaining commands with `--arango-password-env` have aliases
- Aliases already added in Phase 1 for `db config add`

#### M3.T2.S1: Update remaining user commands with --arango-password-env

**Commit Message:** `feat(cli): add --pw-env and -P aliases to remaining user commands`

**File:** `mcp_arangodb_async/__main__.py`

**Changes:**
```python
# Update user_add_parser (line 244), user_databases_parser (line 287), user_password_parser (line 296)
# Note: db config add already has these aliases from M2.T2

# Example for user_add_parser:
user_add_parser.add_argument(
    "--arango-password-env",  # Primary name (existing)
    "--pw-env",              # Medium alias (NEW)
    "-P",                    # Short alias (NEW)
    dest="arango_password_env",
    help="User password env var (default: ARANGO_PASSWORD). Aliases: --pw-env, -P",
)
```

**Verification:**
```bash
maa user add --help | grep -E "(--arango-password-env|--pw-env|-P)"
maa user databases --help | grep -E "(--arango-password-env|--pw-env|-P)"
maa user password --help | grep -E "(--arango-password-env|--pw-env|-P)"
```

**Files Modified:**
- `mcp_arangodb_async/__main__.py` (3 argument definitions)

---

### M3.T3: Run Phase 2 Test Suite

**Estimated Effort:** 30 minutes

**Pre-conditions:**
- M3.T2 complete (all Tier 1 aliases added)

**Success Criteria:**
- All existing tests still pass
- No regressions introduced

#### M3.T3.S1: Verify all tests pass with Tier 1 aliases

**Commit Message:** `test: verify Phase 2 Tier 1 aliases pass all tests`

**Commands:**
```bash
# Run full CLI test suite
pytest tests/test_cli_args_unit.py tests/test_cli_db_unit.py tests/test_admin_cli.py -v

# Test a few aliases manually
python -c "import sys; sys.argv = ['maa', 'db', 'add', 'test', '-R', 'ROOT_PW', '-P', 'USER_PW']; from mcp_arangodb_async.__main__ import main"
```

**Verification:**
```bash
# All tests should pass
pytest tests/test_cli_args_unit.py tests/test_cli_db_unit.py tests/test_admin_cli.py --tb=line -q
```

**Files Modified:** None (verification only)

---

## Milestone 4: Phase 3 - Tier 2 & 3 Aliases (Remaining)

**Goal:** Add remaining aliases for file/path and common arguments

**Pre-conditions:**
- M3 complete (Tier 1 aliases added)
- All tests passing

**Success Gate:**
- ✅ `--permission` has `--perm` and `-p` aliases
- ✅ `--url` has `-u` alias
- ✅ `--database` has `-d` alias
- ✅ `--username` has `-U` alias
- ✅ All tests still passing

---

### M4.T1: Add Aliases to --permission

**Estimated Effort:** 30 minutes

**Pre-conditions:**
- Phase 2 complete

**Success Criteria:**
- `db add` and `user grant` have permission aliases

#### M4.T1.S1: Update permission arguments

**Commit Message:** `feat(cli): add --perm and -p aliases to permission arguments`

**File:** `mcp_arangodb_async/__main__.py`

**Changes:**
```python
# Update db_add_parser (line 206) and user_grant_parser (line 270)

# Example for db_add_parser:
db_add_parser.add_argument(
    "--permission",  # Primary name (existing)
    "--perm",       # Medium alias (NEW)
    "-p",           # Short alias (NEW)
    dest="permission",
    choices=["rw", "ro", "none"],
    default="rw",
    help="Permission level (default: rw). Aliases: --perm, -p",
)
```

**Verification:**
```bash
maa db add --help | grep -E "(--permission|--perm|-p)"
maa user grant --help | grep -E "(--permission|--perm|-p)"
```

**Files Modified:**
- `mcp_arangodb_async/__main__.py` (2 argument definitions)

---

### M4.T2: Add Aliases to Common Arguments

**Estimated Effort:** 45 minutes

**Pre-conditions:**
- M4.T1 complete

**Success Criteria:**
- `--url`, `--database`, `--username` have short aliases

#### M4.T2.S1: Add -u alias to --url arguments

**Commit Message:** `feat(cli): add -u alias to --url arguments across all commands`

**File:** `mcp_arangodb_async/__main__.py`

**Changes:**
```python
# Update all commands with --url (13 commands):
# db config add, db add, db remove, db list,
# user add, user remove, user list, user grant, user revoke, user databases, user password

# Example for db_add_parser:
db_add_parser.add_argument(
    "--url",  # Primary name (existing)
    "-u",     # Short alias (NEW)
    dest="url",
    help="ArangoDB server URL (default: ARANGO_URL env or http://localhost:8529). Alias: -u",
)
```

**Verification:**
```bash
maa db add --help | grep -E "(--url|-u)"
maa user add --help | grep -E "(--url|-u)"
```

**Files Modified:**
- `mcp_arangodb_async/__main__.py` (13 argument definitions)

---

#### M4.T2.S2: Add -d and -U aliases to db config add

**Commit Message:** `feat(cli): add -d and -U aliases to db config add command`

**File:** `mcp_arangodb_async/__main__.py`

**Changes:**
```python
# Update config_add_parser (lines 139, 140)

# Database argument:
config_add_parser.add_argument(
    "--database",  # Primary name (existing)
    "-d",         # Short alias (NEW)
    dest="database",
    required=True,
    help="Database name. Alias: -d",
)

# Username argument:
config_add_parser.add_argument(
    "--username",  # Primary name (existing)
    "-U",         # Short alias (NEW, uppercase to avoid conflict with -u)
    dest="username",
    required=True,
    help="Username. Alias: -U",
)
```

**Verification:**
```bash
maa db config add --help | grep -E "(--database|-d)"
maa db config add --help | grep -E "(--username|-U)"
```

**Files Modified:**
- `mcp_arangodb_async/__main__.py` (2 argument definitions)

---

### M4.T3: Run Phase 3 Test Suite

**Estimated Effort:** 30 minutes

**Pre-conditions:**
- M4.T2 complete (all Tier 2 & 3 aliases added)

**Success Criteria:**
- All tests pass
- All aliases functional

#### M4.T3.S1: Verify all tests pass with all aliases

**Commit Message:** `test: verify Phase 3 Tier 2 & 3 aliases pass all tests`

**Commands:**
```bash
# Run full test suite
pytest tests/test_cli_args_unit.py tests/test_cli_db_unit.py tests/test_admin_cli.py -v

# Test various alias combinations
maa db add testdb -u http://localhost:8529 -R ROOT_PW -P USER_PW -p rw --help
maa db config add prod -u http://localhost:8529 -d mydb -U admin -P PASSWORD -C config.yaml --help
```

**Verification:**
```bash
# All tests should pass
pytest tests/ -k "cli" --tb=line -q
```

**Files Modified:** None (verification only)

---

## Milestone 5: Phase 4 - Documentation

**Goal:** Update all documentation to reflect new aliases

**Pre-conditions:**
- M4 complete (all aliases implemented)
- All tests passing

**Success Gate:**
- ✅ CLI reference updated with alias tables
- ✅ Help text consistent across all commands
- ✅ Examples use primary names
- ✅ Aliases documented in reference section

---

### M5.T1: Update CLI Reference Documentation

**Estimated Effort:** 2-3 hours

**Pre-conditions:**
- All aliases implemented

**Success Criteria:**
- All commands documented with aliases
- Alias tables added
- Examples updated

#### M5.T1.S1: Update server command documentation

**Commit Message:** `docs: update server command with config file aliases`

**File:** `docs/user-guide/cli-reference.md`

**Changes:**
```markdown
# Update server command section with alias table

**Syntax:**
```bash
maa server \
  [--transport <stdio|http>] \
  [--host <host>] \
  [--port <port>] \
  [--stateless] \
  [--config-file|--config-path|--cfgf|--cfgp|-C <path>]
```

**Arguments:**

| Argument | Aliases | Description |
|----------|---------|-------------|
| `--config-file` | `--config-path`, `--cfgf`, `--cfgp`, `-C` | Path to database configuration YAML file |
| `--transport` | - | Transport type (stdio or http) |
| `--host` | - | HTTP host (default: 0.0.0.0) |
| `--port` | - | HTTP port (default: 8000) |
| `--stateless` | - | Run HTTP in stateless mode |

**Examples:**
```bash
# Using primary name
maa server --config-file /etc/arango/databases.yaml

# Using short alias
maa server -C /etc/arango/databases.yaml
```
```

**Verification:**
```bash
grep -A 20 "### server" docs/user-guide/cli-reference.md
```

**Files Modified:**
- `docs/user-guide/cli-reference.md` (server section)

---

#### M5.T1.S2: Update db config and db/user operations documentation

**Commit Message:** `docs: update all CLI commands with alias tables and examples`

**File:** `docs/user-guide/cli-reference.md`

**Changes:**
```markdown
# Update all command sections with alias tables
# Include: db config add, db add, user add, user grant, user password, etc.

# Example for db config add:
**Arguments:**

| Argument | Aliases | Description |
|----------|---------|-------------|
| `--url` | `-u` | ArangoDB server URL |
| `--database` | `-d` | Database name |
| `--username` | `-U` | Username |
| `--arango-password-env` | `--password-env`, `--pw-env`, `-P` | Environment variable containing password |
| `--config-file` | `--config-path`, `--cfgf`, `--cfgp`, `-C` | Path to configuration file |

# Repeat for all commands
```

**Verification:**
```bash
grep -E "(Aliases|Argument)" docs/user-guide/cli-reference.md | wc -l
```

**Files Modified:**
- `docs/user-guide/cli-reference.md` (all command sections)

---

### M5.T2: Add Alias Quick Reference Section

**Estimated Effort:** 1 hour

**Pre-conditions:**
- M5.T1 complete (all commands documented)

**Success Criteria:**
- Quick reference table added
- Progressive disclosure examples added

#### M5.T2.S1: Add alias quick reference table

**Commit Message:** `docs: add CLI alias quick reference table with progressive examples`

**File:** `docs/user-guide/cli-reference.md`

**Changes:**
```markdown
# Add new section after command tree

## Alias Quick Reference

All CLI arguments support multiple forms for flexibility.

### Password & Credential Arguments

| Primary Argument | Medium Aliases | Short | Backward Compat | Commands |
|------------------|----------------|-------|-----------------|----------|
| `--arango-root-password-env` | `--root-pw-env` | `-R` | - | db add/rm/ls, user * |
| `--arango-password-env` | `--pw-env` | `-P` | `--password-env`* | db config add, user * |
| `--arango-new-password-env` | `--new-pw-env` | `-N` | `--new-password-env` | user password |

### File & Path Arguments

| Primary Argument | Medium Aliases | Short | Backward Compat | Commands |
|------------------|----------------|-------|-----------------|----------|
| `--config-file` | `--cfgf`, `--cfgp` | `-C` | `--config-path` | server, db config * |
| `--environment-file` | `--envf` | `-E` | `--env-file` | All commands with credentials |
| `--permission` | `--perm` | `-p` | - | db add, user grant |

### Common Arguments

| Primary Argument | Short | Commands |
|------------------|-------|----------|
| `--url` | `-u` | All db/user commands |
| `--database` | `-d` | db config add |
| `--username` | `-U` | db config add |

### Progressive Disclosure Examples

**Beginner (Documentation Default):**
```bash
maa db add myapp_prod \
  --with-user myapp_user \
  --permission rw \
  --arango-root-password-env ARANGO_ROOT_PASSWORD \
  --arango-password-env ARANGO_PASSWORD
```

**Advanced (Short Aliases):**
```bash
maa db add myapp_prod --with-user myapp_user -p rw -R ARANGO_ROOT_PASSWORD -P ARANGO_PASSWORD
```
```

**Verification:**
```bash
grep -A 50 "## Alias Quick Reference" docs/user-guide/cli-reference.md
```

**Files Modified:**
- `docs/user-guide/cli-reference.md` (new section)

---

### M5.T3: Update README and Changelog

**Estimated Effort:** 1 hour

**Pre-conditions:**
- M5.T2 complete (documentation updated)

**Success Criteria:**
- README mentions aliases
- Changelog entry added for v0.5.1

#### M5.T3.S1: Update README with alias mention

**Commit Message:** `docs: update README with CLI alias feature mention`

**File:** `README.md`

**Changes:**
```markdown
# Add note in CLI section

### Command-Line Interface

The `maa` command provides comprehensive database and user management:

```bash
# Database configuration (YAML file management)
maa db config add production --url http://localhost:8529 --database myapp -U admin -P PROD_PASSWORD

# Database operations (ArangoDB management)
maa db add myapp_prod --with-user myapp_user -p rw -R ARANGO_ROOT_PASSWORD -P ARANGO_PASSWORD

# User management
maa user add alice -R ARANGO_ROOT_PASSWORD -P ARANGO_PASSWORD
maa user grant alice myapp_prod -p rw -R ARANGO_ROOT_PASSWORD
```

**New in 0.5.1:** All CLI arguments now support short aliases for improved ergonomics. See [CLI Reference](docs/user-guide/cli-reference.md#alias-quick-reference) for complete alias documentation.
```

**Verification:**
```bash
grep -A 10 "Command-Line Interface" README.md
```

**Files Modified:**
- `README.md` (CLI section)

---

#### M5.T3.S2: Add changelog entry for 0.5.1

**Commit Message:** `docs: add changelog entry for v0.5.1 CLI enhancement`

**File:** `docs/developer-guide/changelog.md`

**Changes:**
```markdown
# Add new section at top (after line 44)

## [0.5.1] - 2025-01-XX

### Added

- **CLI Argument Aliases**: 3-tier alias system for improved ergonomics
  - **Short aliases** (9 new): `-R`, `-P`, `-N`, `-C`, `-E`, `-p`, `-u`, `-d`, `-U`
  - **Medium aliases** (7 new): `--root-pw-env`, `--pw-env`, `--new-pw-env`, `--cfgf`, `--cfgp`, `--envf`, `--perm`
  - **Standardized naming**: `--arango-new-password-env`, `--environment-file`, `--config-file`
  - **Character savings**: 40-50% reduction for common operations using short aliases

- **Backward Compatibility**: All existing argument names remain valid as aliases
  - `--password-env` → `--arango-password-env` (in `db config add`)
  - `--new-password-env` → `--arango-new-password-env` (in `user password`)
  - `--config-path` → `--config-file` (everywhere)
  - `--env-file` → `--environment-file` (everywhere)

### Changed

- **Help Text**: All commands now document available aliases
- **Documentation**: CLI reference updated with comprehensive alias tables and progressive disclosure examples

### Technical Details

- **Implementation**: Argparse-based alias resolution (no custom parsing logic)
- **Testing**: 4 new backward compatibility tests, 18 test functions updated
- **Zero Breaking Changes**: 100% backward compatibility maintained
- **Usability Enhancement**: Convenience aliases only, no new functionality

**Examples:**

```bash
# Before (verbose)
maa db add myapp_prod \
  --with-user myapp_user \
  --permission rw \
  --arango-root-password-env ARANGO_ROOT_PASSWORD \
  --arango-password-env ARANGO_PASSWORD

# After (with short aliases)
maa db add myapp_prod --with-user myapp_user -p rw -R ARANGO_ROOT_PASSWORD -P ARANGO_PASSWORD
```

---
```

**Verification:**
```bash
head -100 docs/developer-guide/changelog.md | grep -A 30 "0.5.1"
```

**Files Modified:**
- `docs/developer-guide/changelog.md` (new version section)

---

## Milestone 6: Final Validation & Release

**Goal:** Final testing, version bump, and release preparation

**Pre-conditions:**
- M5 complete (documentation updated)
- All tests passing

**Success Gate:**
- ✅ Full test suite passes
- ✅ Help text validation passes
- ✅ Version bumped to 0.5.1
- ✅ Ready for merge to master

---

### M6.T1: Final Test Suite Run

**Estimated Effort:** 30 minutes

**Pre-conditions:**
- All implementation complete

**Success Criteria:**
- All tests pass
- Help text shows aliases

#### M6.T1.S1: Run complete test suite

**Commit Message:** `test: final validation of CLI enhancement implementation`

**Commands:**
```bash
# Run all tests
pytest tests/ -v --tb=short

# Run CLI tests specifically
pytest tests/test_cli_args_unit.py tests/test_cli_db_unit.py tests/test_admin_cli.py -v

# Manual help text verification
maa server --help
maa db config add --help
maa db add --help
maa user add --help
maa user password --help
```

**Verification:**
```bash
# All tests should pass
pytest tests/ --tb=line -q

# Help text should show aliases
maa server --help | grep -E "Aliases:"
maa db config add --help | grep -E "Aliases:"
```

**Files Modified:** None (verification only)

---

### M6.T2: Version Bump and Release Preparation

**Estimated Effort:** 30 minutes

**Pre-conditions:**
- M6.T1 complete (all tests passing)

**Success Criteria:**
- Version bumped to 0.5.1
- Changelog finalized

#### M6.T2.S1: Bump version to 0.5.1

**Commit Message:** `chore: bump version to 0.5.1 for CLI enhancement release`

**Commands:**
```bash
# Bump version
python scripts/bvn.py --version "0.5.1" --pypi false

# Verify version updated
grep 'version = "0.5.1"' pyproject.toml
```

**Verification:**
```bash
# Check version in pyproject.toml
cat pyproject.toml | grep -A 2 "version ="
```

**Files Modified:**
- `pyproject.toml` (version field)

---

#### M6.T2.S2: Finalize changelog with release date

**Commit Message:** `docs: finalize changelog for v0.5.1 release`

**File:** `docs/developer-guide/changelog.md`

**Changes:**
```markdown
# Update release date (line 45)
## [0.5.1] - 2025-01-XX  # Replace XX with actual date
```

**Verification:**
```bash
head -50 docs/developer-guide/changelog.md | grep "0.5.1"
```

**Files Modified:**
- `docs/developer-guide/changelog.md` (release date)

---

### M6.T3: Create Pull Request

**Estimated Effort:** 30 minutes

**Pre-conditions:**
- M6.T2 complete (version bumped)

**Success Criteria:**
- PR created with comprehensive description
- All commits organized
- Ready for review

#### M6.T3.S1: Push feature branch and create PR

**Commit Message:** N/A (PR creation)

**Commands:**
```bash
# Push feature branch
git push origin enhance/cli-consistency

# Create PR (via GitHub CLI or web interface)
gh pr create \
  --title "feat: CLI consistency enhancement with 3-tier alias system (v0.5.1)" \
  --body "$(cat <<EOF
## Summary

Implements comprehensive CLI consistency enhancement with 3-tier alias system (primary + medium + short) for improved user experience.

## Changes

### Standardization (Phase 1)
- ✅ Unified \`--config-file\` and \`--config-path\` as aliases
- ✅ Standardized to \`--arango-password-env\` in \`db config add\`
- ✅ Standardized to \`--arango-new-password-env\` in \`user password\`
- ✅ Standardized to \`--environment-file\` with \`--env-file\` alias

### Aliases Added (Phases 2-3)
- ✅ Tier 1: Password-related aliases (\`-R\`, \`-P\`, \`-N\`)
- ✅ Tier 2: File/path aliases (\`-C\`, \`-E\`, \`-p\`)
- ✅ Tier 3: Common argument aliases (\`-u\`, \`-d\`, \`-U\`)

### Documentation (Phase 4)
- ✅ CLI reference updated with alias tables
- ✅ Quick reference section added
- ✅ Progressive disclosure examples
- ✅ Changelog entry for v0.5.1

## Testing

- ✅ 4 new backward compatibility tests
- ✅ 18 test functions updated
- ✅ All tests passing (100% pass rate)
- ✅ Help text validation complete

## Backward Compatibility

- ✅ Zero breaking changes
- ✅ All existing argument names remain valid
- ✅ Backward compatibility tests added

## Impact

- **Character Savings**: 40-50% reduction for common operations
- **User Experience**: Improved ergonomics for power users
- **Documentation**: Clear progressive disclosure (beginner → advanced)
- **Version**: 0.5.1 (PATCH - usability improvement)

## Related Reports

- Architecture Analysis: \`__reports__/enhance_cli_consistency/00-architecture_analysis_v1.md\`
- Test Definition: \`__reports__/enhance_cli_consistency/01-test_definition_v1.md\`
- Implementation Roadmap: \`__design__/cli-consistency-enhancement-roadmap.md\`

## Checklist

- [x] All tests passing
- [x] Documentation updated
- [x] Changelog entry added
- [x] Version bumped to 0.5.1
- [x] Backward compatibility maintained
- [x] Help text shows aliases
EOF
)" \
  --base master \
  --head enhance/cli-consistency
```

**Verification:**
```bash
# Check PR created
gh pr view enhance/cli-consistency
```

**Files Modified:** None (PR creation)

---

## Implementation Summary

### Total Scope

| Metric | Count |
|--------|-------|
| **Milestones** | 6 |
| **Tasks** | 18 |
| **Implementation Steps** | ~40 |
| **New Aliases** | 16 (9 short + 7 medium) |
| **Standardizations** | 4 |
| **Files Modified** | 8 |
| **Lines Modified** | ~520 |
| **New Tests** | 4 |
| **Test Functions Updated** | 18 |

### Effort Breakdown

| Phase | Effort | Percentage |
|-------|--------|------------|
| M1: Baseline & Preparation | 1.5 hours | 8% |
| M2: Phase 1 Standardization | 3-5 hours | 24% |
| M3: Phase 2 Tier 1 Aliases | 4-6 hours | 31% |
| M4: Phase 3 Tier 2 & 3 Aliases | 2-4 hours | 17% |
| M5: Phase 4 Documentation | 4-6 hours | 31% |
| M6: Final Validation & Release | 1.5-2 hours | 9% |
| **Total** | **14.5-22.5 hours** | **100%** |

### Deliverables Checklist

**Implementation:**
- [ ] Config file/path unified (`--config-file` ↔ `--config-path`)
- [ ] Password env standardized (`--arango-password-env` ↔ `--password-env`)
- [ ] New password env standardized (`--arango-new-password-env` ↔ `--new-password-env`)
- [ ] Environment file standardized (`--environment-file` ↔ `--env-file`)
- [ ] 9 short aliases added (`-R`, `-P`, `-N`, `-C`, `-E`, `-p`, `-u`, `-d`, `-U`)
- [ ] 7 medium aliases added (`--root-pw-env`, `--pw-env`, `--new-pw-env`, `--cfgf`, `--cfgp`, `--envf`, `--perm`)

**Testing:**
- [ ] 4 backward compatibility tests added
- [ ] 18 test functions updated
- [ ] All tests passing (100% pass rate)
- [ ] Help text validation complete

**Documentation:**
- [ ] CLI reference updated with alias tables
- [ ] Alias quick reference section added
- [ ] Progressive disclosure examples added
- [ ] README updated
- [ ] Changelog entry for v0.6.0 added

**Release:**
- [ ] Version bumped to 0.6.0
- [ ] Changelog finalized with release date
- [ ] Pull request created
- [ ] Zero breaking changes verified

---

## Success Criteria

### Functional Requirements

✅ **Backward Compatibility:**
- All existing argument names work as aliases
- No breaking changes to existing scripts
- Backward compatibility tests pass

✅ **Alias Functionality:**
- All 3 tiers of aliases work correctly
- Argparse handles alias resolution
- Help text shows all aliases

✅ **Standardization:**
- Consistent naming across all commands
- Primary names follow `--arango-*` pattern for credentials
- File arguments use `--*-file` pattern

### Quality Requirements

✅ **Testing:**
- 100% test pass rate maintained
- New backward compatibility tests added
- No regressions introduced

✅ **Documentation:**
- All aliases documented in CLI reference
- Quick reference table added
- Progressive disclosure examples provided

✅ **Code Quality:**
- Conventional commit messages used
- Incremental implementation with testing
- Clear commit history

---

## Risk Management

### Identified Risks

| Risk | Severity | Mitigation | Status |
|------|----------|------------|--------|
| Test parameter name changes | Medium | Systematic updates, run tests after each phase | Planned |
| Backward compatibility breaks | Medium | 4 focused backward compat tests | Planned |
| Documentation inconsistency | Low | Comprehensive Phase 4 documentation updates | Planned |
| Help text confusion | Low | Manual verification + automated parsing test | Planned |

### Mitigation Strategy

1. **Incremental Implementation**: Test after each milestone
2. **Backward Compatibility First**: Add aliases before removing old names
3. **Comprehensive Testing**: 4 new tests + 18 updated tests
4. **Documentation Last**: Update docs after implementation complete

---

## Appendix: Quick Reference

### Commit Message Format

```
<type>(<scope>): <description>

Types: feat, test, docs, chore
Scopes: cli, test, docs
```

### Key Files

| File | Purpose | Lines Modified |
|------|---------|----------------|
| `mcp_arangodb_async/__main__.py` | CLI argument parsers | ~50 |
| `tests/test_cli_args_unit.py` | Server argument tests | ~20 |
| `tests/test_cli_db_unit.py` | DB config tests | ~30 |
| `tests/test_admin_cli.py` | Admin CLI integration tests | ~60 |
| `docs/user-guide/cli-reference.md` | CLI documentation | ~300 |
| `README.md` | Project README | ~10 |
| `docs/developer-guide/changelog.md` | Changelog | ~50 |
| `pyproject.toml` | Version number | 1 |

### Verification Commands

```bash
# Test suite
pytest tests/test_cli_args_unit.py tests/test_cli_db_unit.py tests/test_admin_cli.py -v

# Help text verification
maa server --help | grep -E "Aliases:"
maa db config add --help | grep -E "Aliases:"
maa db add --help | grep -E "Aliases:"
maa user add --help | grep -E "Aliases:"
maa user password --help | grep -E "Aliases:"

# Version verification
grep 'version = "0.6.0"' pyproject.toml
```

---

**Roadmap Status:** ✅ Implementation Ready
**Next Action:** Begin M1.T1 (Establish Test Baseline)
**Target Version:** 0.5.1 (PATCH - usability improvement)
**Estimated Completion:** 14.5-22.5 hours from start

---

**Document Version:** 1.1
**Last Updated:** 2025-12-31
**Author:** AI Assistant (Augment Agent)
**Related Documents:**
- [Architecture Analysis v1](../__reports__/enhance_cli_consistency/00-architecture_analysis_v1.md)
- [Test Definition v1](../__reports__/enhance_cli_consistency/01-test_definition_v1.md)
