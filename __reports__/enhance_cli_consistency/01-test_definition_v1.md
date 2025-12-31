# Phase 2: Test Definition Report - CLI Consistency Enhancement

**Status:** Phase 2 (Test Definition)  
**Version:** v1  
**Date:** 2025-12-31  
**Architecture Report:** [00-architecture_analysis_v1.md](./00-architecture_analysis_v1.md)

---

## Executive Summary

This report defines a **minimal, focused test strategy** for the CLI consistency enhancement. We avoid over-testing by trusting argparse's built-in alias resolution and focus on:

1. **Regression testing**: Ensuring existing tests continue to pass
2. **Critical backward compatibility**: Testing only the most important argument name changes
3. **Behavioral validation**: Verifying functionality works regardless of argument name used

**Key Principle:** Test behavior, not implementation. Argparse handles alias resolution; we verify the right environment variables are loaded and the right actions occur.

---

## Test Scope Overview

### In Scope

✅ **Regression Tests**: All existing CLI tests must continue to pass  
✅ **Critical Backward Compatibility**: `--password-env`, `--config-path`, `--env-file`, `--new-password-env` aliases  
✅ **Credential Loading**: Verify `load_credentials()` works with all argument name variations  
✅ **Help Text**: Verify aliases are documented in help output

### Out of Scope

❌ **Exhaustive Alias Combinations**: No testing of every possible alias permutation  
❌ **Argparse Internals**: We trust argparse's alias resolution mechanism  
❌ **New Functionality**: This is a refactoring; no new behavior to test  
❌ **Performance**: Alias resolution has negligible performance impact

---

## Existing Test Inventory

### Test Files Requiring Review

| Test File | Purpose | Commands Tested | Review Action |
|-----------|---------|-----------------|---------------|
| `test_cli_args_unit.py` | Server argument parsing | `server` | ✅ **PASS-THROUGH** - No changes needed |
| `test_cli_db_unit.py` | DB config handlers | `db config add/remove/list/test/status` | ⚠️ **UPDATE** - Change `config_path` → `config_file` in test setup |
| `test_admin_cli.py` | Admin CLI integration | All `db config`, `db`, `user` commands | ⚠️ **UPDATE** - Update `password_env` → `arango_password_env` |
| `test_cli_user.py` | User management (if exists) | `user` commands | 🔍 **VERIFY** - Check if exists |

### Test Coverage Analysis

**Current Coverage:**
- ✅ Server command: `--config-file` argument (lines 177-191 in `test_cli_args_unit.py`)
- ✅ DB config commands: `config_path` parameter (throughout `test_cli_db_unit.py`)
- ✅ User commands: `arango_root_password_env`, `arango_password_env` (throughout `test_admin_cli.py`)
- ✅ Credential loading: Environment variable resolution (`cli_utils.load_credentials()`)

**Gaps Identified:**
- ⚠️ No explicit test for `--new-password-env` → `--arango-new-password-env` standardization
- ⚠️ No test for `--config-path` alias working in server command
- ⚠️ No test for `--password-env` alias working in `db config add`

---

## Regression Test Strategy

### Phase 1: Standardization (Config/Password/Env File)

**Affected Tests:**

1. **`test_cli_db_unit.py`** - DB config handlers
   - **Current**: Uses `config_path` parameter in `Namespace` objects
   - **Action**: Update to use `config_file` as primary (matches new `dest` parameter)
   - **Backward Compat Test**: Add ONE test verifying `--config-path` CLI arg still works
   - **Lines to Update**: ~15 test functions using `Namespace(config_path=...)`

2. **`test_admin_cli.py`** - Admin CLI integration
   - **Current**: Uses `password_env` in `db config add` tests (lines 155, 250, 366)
   - **Action**: Update to use `arango_password_env` (matches standardized name)
   - **Backward Compat Test**: Add ONE test verifying `--password-env` CLI arg still works
   - **Lines to Update**: 3 occurrences in `TestDBConfig` class

3. **`test_cli_args_unit.py`** - Server argument parsing
   - **Current**: Tests `--config-file` argument (line 181)
   - **Action**: ✅ **NO CHANGES NEEDED** - Already uses primary name
   - **Backward Compat Test**: Add ONE test verifying `--config-path` works for server command

### Phase 2-4: Alias Additions

**Affected Tests:**

✅ **NO EXISTING TESTS NEED UPDATES** - We're only adding aliases, not changing behavior

**New Tests Required:** NONE - Argparse handles alias resolution automatically

---

## Critical Backward Compatibility Tests

### Minimal Test Set (4 Tests Total)

These tests verify the most critical argument name changes don't break existing usage:

#### Test 1: `--password-env` Backward Compatibility (db config add)

**File:** `test_admin_cli.py` (new test in `TestDBConfig`)

**Purpose:** Verify `--password-env` still works in `db config add` after standardization to `--arango-password-env`

**Test Code:**
```python
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
        config_path=str(config_path),
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

**Rationale:** This is the ONLY inconsistent naming in the current codebase. Must verify backward compatibility.

---

#### Test 2: `--config-path` Backward Compatibility (server command)

**File:** `test_cli_args_unit.py` (new test in `TestCLIArgumentParsing`)

**Purpose:** Verify `--config-path` works in server command after unification with `--config-file`

**Test Code:**
```python
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

**Rationale:** Verifies unification of `--config-file` and `--config-path` works in server command.

---

#### Test 3: `--new-password-env` Backward Compatibility (user password)

**File:** `test_admin_cli.py` (new test in `TestUserAdmin`)

**Purpose:** Verify `--new-password-env` still works after standardization to `--arango-new-password-env`

**Test Code:**
```python
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

**Rationale:** Verifies standardization to `--arango-new-password-env` maintains backward compatibility.

---

#### Test 4: Credential Loading with All Argument Variations

**File:** `test_cli_utils.py` (new file or add to existing)

**Purpose:** Verify `load_credentials()` works with both old and new argument names

**Test Code:**
```python
def test_load_credentials_argument_name_variations():
    """Verify load_credentials works with old and new argument names."""
    import os
    from argparse import Namespace
    from mcp_arangodb_async.cli_utils import load_credentials

    # Set up environment
    os.environ["TEST_ROOT_PW"] = "rootpass"
    os.environ["TEST_USER_PW"] = "userpass"
    os.environ["TEST_NEW_PW"] = "newpass"

    # Test with new standardized names
    args_new = Namespace(
        arango_root_password_env="TEST_ROOT_PW",
        arango_password_env="TEST_USER_PW",
        new_password_env="TEST_NEW_PW",
        env_file=None,
        url="http://localhost:8529",
    )

    creds = load_credentials(args_new)
    assert creds["root_password"] == "rootpass"
    assert creds["user_password"] == "userpass"
    assert creds["new_password"] == "newpass"
    assert creds["url"] == "http://localhost:8529"

    # Test with old names (backward compat)
    args_old = Namespace(
        password_env="TEST_USER_PW",  # OLD name in db config add
        env_file=None,
        url=None,
    )

    # Should still work (argparse maps to same dest)
    creds_old = load_credentials(args_old)
    assert creds_old["user_password"] == "userpass"

    # Cleanup
    del os.environ["TEST_ROOT_PW"]
    del os.environ["TEST_USER_PW"]
    del os.environ["TEST_NEW_PW"]
```

**Rationale:** Core credential loading must work with all argument name variations.

---

## Selective Test Updates

### Files Requiring Updates

#### 1. `test_cli_db_unit.py`

**Change:** Update `config_path` → `config_file` in `Namespace` objects

**Affected Functions:** (15 functions)
- `test_add_database_config_success`
- `test_add_database_config_duplicate_key`
- `test_remove_database_config_success`
- `test_remove_database_config_nonexistent`
- `test_list_databases_empty_config`
- `test_list_databases_multiple_configs`
- `test_list_databases_no_config_file_default_env_fallback`
- `test_test_connection_success`
- `test_test_connection_failure`
- `test_status_all_databases`
- And 5 more...

**Example Change:**
```python
# BEFORE
args = Namespace(config_path=self.config_path)

# AFTER
args = Namespace(config_file=self.config_path)
```

**Rationale:** The `dest` parameter in argparse will be unified to `config_file`. Tests must use the same parameter name.

---

#### 2. `test_admin_cli.py`

**Change:** Update `password_env` → `arango_password_env` in `db config add` tests

**Affected Functions:** (3 functions in `TestDBConfig`)
- `test_config_add_success` (line 155)
- `test_config_list_success` (line 250)
- `test_config_status_success` (line 366)

**Example Change:**
```python
# BEFORE
args = Namespace(
    key="testdb",
    password_env="TEST_PASSWORD",  # OLD inconsistent name
    ...
)

# AFTER
args = Namespace(
    key="testdb",
    arango_password_env="TEST_PASSWORD",  # NEW standardized name
    ...
)
```

**Rationale:** Standardizing to `--arango-password-env` everywhere. Tests should use primary name for clarity.

---

## Help Text Validation

### Manual Verification Required

After implementation, manually verify help text shows aliases:

```bash
# Verify server command
maa server --help
# Should show: --config-file, --cfgf, --cfgp, -C, --config-path (backward compat)

# Verify db config add
maa db config add --help
# Should show: --arango-password-env, --pw-env, -P, --password-env (backward compat)

# Verify user password
maa user password --help
# Should show: --arango-new-password-env, --new-pw-env, -N, --new-password-env (backward compat)
```

**Automated Test:** Add simple help text parsing test to verify aliases are mentioned:

```python
def test_help_text_includes_aliases():
    """Verify help text documents aliases."""
    import subprocess

    # Test server command
    result = subprocess.run(
        ["maa", "server", "--help"],
        capture_output=True,
        text=True,
    )
    assert "--config-file" in result.stdout
    assert "--cfgf" in result.stdout or "Aliases:" in result.stdout

    # Test db config add
    result = subprocess.run(
        ["maa", "db", "config", "add", "--help"],
        capture_output=True,
        text=True,
    )
    assert "--arango-password-env" in result.stdout
    assert "--pw-env" in result.stdout or "Aliases:" in result.stdout
```

---

## Test Execution Plan

### Phase 1: Pre-Implementation Baseline

1. **Run existing test suite**: Establish baseline (all tests should pass)
   ```bash
   pytest tests/test_cli_args_unit.py -v
   pytest tests/test_cli_db_unit.py -v
   pytest tests/test_admin_cli.py -v
   ```

2. **Document current pass rate**: Should be 100%

### Phase 2: Implementation + Test Updates

1. **Implement Phase 1 standardization** (config/password/env file)
2. **Update test files** (`test_cli_db_unit.py`, `test_admin_cli.py`)
3. **Add 4 backward compatibility tests**
4. **Run updated test suite**: All tests should pass

### Phase 3: Alias Additions

1. **Implement Phase 2-4 aliases** (Tier 1, 2, 3)
2. **No test updates required** (aliases don't change behavior)
3. **Run full test suite**: All tests should still pass

### Phase 4: Validation

1. **Manual help text verification**
2. **Add help text parsing test**
3. **Final full test suite run**

---

## Success Criteria

### Regression Tests

- ✅ All existing tests pass after implementation
- ✅ No test failures introduced by standardization
- ✅ No test failures introduced by alias additions

### Backward Compatibility

- ✅ 4 new backward compatibility tests pass
- ✅ `--password-env` works in `db config add`
- ✅ `--config-path` works in server command
- ✅ `--new-password-env` works in user password
- ✅ `load_credentials()` works with all argument variations

### Documentation

- ✅ Help text shows all aliases
- ✅ Help text parsing test passes
- ✅ Primary names used in all examples

---

## Risk Assessment

### Low Risk Areas

✅ **Alias additions (Phase 2-4)**: Argparse handles this natively, minimal risk
✅ **Credential loading**: Already abstracted in `load_credentials()`, works with any `dest` parameter
✅ **Help text**: Automatically generated by argparse

### Medium Risk Areas

⚠️ **Test parameter name changes**: Must update `Namespace` objects to match new `dest` parameters
⚠️ **Backward compatibility**: Must verify old argument names still work

### Mitigation

- **Comprehensive test updates**: Update all affected `Namespace` objects systematically
- **Backward compat tests**: Add 4 focused tests for critical argument name changes
- **Incremental implementation**: Test after each phase before proceeding

---

## Estimated Effort

| Phase | Task | Estimated Time |
|-------|------|----------------|
| **Baseline** | Run existing tests, document pass rate | 15 minutes |
| **Test Updates** | Update `test_cli_db_unit.py` (15 functions) | 30 minutes |
| **Test Updates** | Update `test_admin_cli.py` (3 functions) | 15 minutes |
| **New Tests** | Add 4 backward compatibility tests | 45 minutes |
| **Validation** | Manual help text verification | 15 minutes |
| **Help Test** | Add help text parsing test | 15 minutes |
| **Final Run** | Full test suite execution | 15 minutes |
| **Total** | | **2.5 hours** |

---

## Appendix: Test File Locations

| Test File | Path | Purpose |
|-----------|------|---------|
| `test_cli_args_unit.py` | `tests/test_cli_args_unit.py` | Server argument parsing |
| `test_cli_db_unit.py` | `tests/test_cli_db_unit.py` | DB config handlers |
| `test_admin_cli.py` | `tests/test_admin_cli.py` | Admin CLI integration |
| `test_cli_utils.py` | `tests/test_cli_utils.py` | Credential loading (may need creation) |

---

## Next Steps

1. **Review and approve** this test definition report
2. **Establish baseline**: Run existing tests, document pass rate
3. **Begin implementation**: Phase 1 standardization + test updates
4. **Iterative testing**: Test after each phase
5. **Final validation**: Help text verification + full test suite

---

**Report Status:** ✅ Ready for Review
**Next Phase:** Implementation (Phase 1: Standardization)

