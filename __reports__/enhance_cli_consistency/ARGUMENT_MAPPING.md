# CLI Argument Mapping: Current vs. Accepted

**Status:** ✅ ACCEPTED
**Version:** v1 (updated with stakeholder feedback)

## Quick Reference

This document provides a comprehensive mapping of all CLI arguments showing current state and accepted enhancements.

## Key Changes from v0

1. **Config file/path unification**: `--config-file` and `--config-path` are now aliases
2. **Environment file standardization**: `--environment-file` as primary, `--env-file` as alias
3. **Capital letter convention**: `-C` and `-E` for file arguments (not `-c` and `-e`)
4. **All tiers implemented**: No "optional" aliases; all three tiers are included

## Password-Related Arguments (Tier 1)

### --arango-root-password-env

**Current:**
```bash
maa db add mydb --arango-root-password-env ARANGO_ROOT_PASSWORD
maa user add alice --arango-root-password-env ARANGO_ROOT_PASSWORD
```

**Proposed (all forms valid):**
```bash
# Primary (recommended for scripts/docs)
maa db add mydb --arango-root-password-env ARANGO_ROOT_PASSWORD

# Medium alias (readable)
maa db add mydb --root-pw-env ARANGO_ROOT_PASSWORD

# Short alias (power users)
maa db add mydb -R ARANGO_ROOT_PASSWORD
```

**Commands Using This:**
- `db add`, `db remove`, `db list`
- `user add`, `user remove`, `user list`, `user grant`, `user revoke`

---

### --arango-password-env

**Current:**
```bash
# INCONSISTENT: db config add uses different name
maa db config add prod --password-env ARANGO_PASSWORD

# Other commands use full name
maa db add mydb --with-user alice --arango-password-env ARANGO_PASSWORD
maa user add alice --arango-password-env ARANGO_PASSWORD
```

**Proposed (all forms valid):**
```bash
# Primary (recommended, now CONSISTENT everywhere)
maa db config add prod --arango-password-env ARANGO_PASSWORD
maa db add mydb --with-user alice --arango-password-env ARANGO_PASSWORD

# Medium alias
maa db config add prod --pw-env ARANGO_PASSWORD

# Short alias
maa db config add prod -P ARANGO_PASSWORD

# Backward compatibility (db config add only)
maa db config add prod --password-env ARANGO_PASSWORD  # Still works!
```

**Commands Using This:**
- `db config add` (FIXED: now uses `--arango-password-env` as primary)
- `db add` (with `--with-user`)
- `user add`
- `user databases`
- `user password`

---

### --arango-new-password-env (STANDARDIZED)

**Current:**
```bash
maa user password --new-password-env ARANGO_NEW_PASSWORD
```

**Accepted (all forms valid, STANDARDIZED):**
```bash
# Primary (standardized to match --arango-password-env pattern)
maa user password --arango-new-password-env ARANGO_NEW_PASSWORD

# Medium alias
maa user password --new-pw-env ARANGO_NEW_PASSWORD

# Short alias
maa user password -N ARANGO_NEW_PASSWORD

# Backward compatibility
maa user password --new-password-env ARANGO_NEW_PASSWORD  # Still works!
```

**Commands Using This:**
- `user password`

**Change:** Standardized to `--arango-new-password-env` to match the pattern of `--arango-password-env` and `--arango-root-password-env`, keeping `--new-password-env` as backward-compatible alias

---

## Path/File Arguments (Tier 2)

### --config-file / --config-path (UNIFIED)

**Current (INCONSISTENT):**
```bash
# server command uses --config-file
maa server --config-file config/databases.yaml
maa server --cfgf config/databases.yaml  # Existing alias

# db config commands use --config-path
maa db config list --config-path config/databases.yaml
```

**Accepted (all forms valid, UNIFIED):**
```bash
# Primary (recommended everywhere)
maa server --config-file config/databases.yaml
maa db config list --config-file config/databases.yaml

# Medium aliases
maa server --cfgf config/databases.yaml
maa server --cfgp config/databases.yaml
maa db config list --cfgf config/databases.yaml
maa db config list --cfgp config/databases.yaml

# Short alias (capital C for file)
maa server -C config/databases.yaml
maa db config list -C config/databases.yaml

# Backward compatibility
maa server --config-path config/databases.yaml  # NEW: now works!
maa db config list --config-path config/databases.yaml  # Still works!
```

**Commands Using This:**
- `server` (currently `--config-file`)
- `db config add`, `db config remove`, `db config list`, `db config test`, `db config status` (currently `--config-path`)

**Change:** Unified naming with `--config-file` as primary, `--config-path` as backward-compatible alias everywhere

---

### --environment-file / --env-file (STANDARDIZED)

**Current:**
```bash
maa db add mydb --env-file .env.production
```

**Accepted (all forms valid, STANDARDIZED):**
```bash
# Primary (explicit, recommended)
maa db add mydb --environment-file .env.production

# Medium alias (consistent with --cfgf pattern)
maa db add mydb --envf .env.production

# Short alias (capital E for file)
maa db add mydb -E .env.production

# Backward compatibility (most common form)
maa db add mydb --env-file .env.production  # Still works!
```

**Commands Using This:**
- All `db` and `user` commands that need credentials

**Change:** Standardized to `--environment-file` as primary for consistency with `--config-file`, keeping `--env-file` as widely-used alias

---

### --permission

**Current:**
```bash
maa user grant alice mydb --permission rw
```

**Proposed (all forms valid):**
```bash
# Primary
maa user grant alice mydb --permission rw

# Medium alias
maa user grant alice mydb --perm rw

# Short alias
maa user grant alice mydb -p rw
```

**Commands Using This:**
- `db add` (with `--with-user`)
- `user grant`

---

## Common Arguments (Tier 3)

### --url

**Current:**
```bash
maa db add mydb --url http://localhost:8529
```

**Accepted (all forms valid):**
```bash
# Primary
maa db add mydb --url http://localhost:8529

# Short alias
maa db add mydb -u http://localhost:8529
```

**Commands Using This:**
- All `db` and `user` commands

---

### --database

**Current:**
```bash
maa db config add prod --database myapp_prod
```

**Accepted (all forms valid):**
```bash
# Primary
maa db config add prod --database myapp_prod

# Short alias
maa db config add prod -d myapp_prod
```

**Commands Using This:**
- `db config add`

---

### --username

**Current:**
```bash
maa db config add prod --username admin
```

**Accepted (all forms valid):**
```bash
# Primary
maa db config add prod --username admin

# Short alias (uppercase to avoid conflict with -u for url)
maa db config add prod -U admin
```

**Commands Using This:**
- `db config add`

---

## Already Aliased (No Changes)

### --config-file

**Current (already has alias):**
```bash
maa server --config-file config/databases.yaml
maa server --cfgf config/databases.yaml
```

**Status:** ✅ No changes needed

---

### --yes

**Current (already has alias):**
```bash
maa db remove mydb --yes
maa db remove mydb -y
```

**Status:** ✅ No changes needed

---

## Summary Table

| Argument | Current Length | Primary | Medium Aliases | Short Alias | Savings |
|----------|----------------|---------|----------------|-------------|---------|
| `--arango-root-password-env` | 26 | ✓ | `--root-pw-env` (14) | `-R` (2) | 12-24 chars |
| `--arango-password-env` | 21 | ✓ | `--pw-env` (8) | `-P` (2) | 13-19 chars |
| `--arango-new-password-env` | 24 | ✓ | `--new-pw-env` (13) | `-N` (2) | 11-22 chars |
| `--config-file` (unified) | 13 | ✓ | `--cfgf`, `--cfgp` (11) | `-C` (2) | 2-11 chars |
| `--environment-file` | 17 | ✓ | `--envf` (6) | `-E` (2) | 11-15 chars |
| `--permission` | 12 | ✓ | `--perm` (6) | `-p` (2) | 6-10 chars |
| `--url` | 5 | ✓ | - | `-u` (2) | 3 chars |
| `--database` | 10 | ✓ | - | `-d` (2) | 8 chars |
| `--username` | 10 | ✓ | - | `-U` (2) | 8 chars |

**Note:** Backward compatibility aliases (`--config-path`, `--env-file`, `--password-env`, `--new-password-env`) not shown in savings calculation.

---

## Backward Compatibility Guarantee

**All existing argument forms remain valid indefinitely:**

✅ `--password-env` continues to work in `db config add`  
✅ All current argument names unchanged  
✅ No deprecation warnings  
✅ No breaking changes to existing scripts  

**New aliases are additive only.**

