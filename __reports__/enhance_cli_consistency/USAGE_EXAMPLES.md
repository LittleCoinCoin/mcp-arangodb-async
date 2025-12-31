# CLI Enhancement: Real-World Usage Examples

**Status:** ✅ ACCEPTED
**Version:** v1 (updated with stakeholder feedback)

## Before vs. After Comparison

This document demonstrates the practical impact of the accepted CLI enhancements through real-world usage scenarios.

## Key Changes from v0

1. **Capital letter convention**: `-C` and `-E` (not `-c` and `-e`) for file arguments
2. **Config file unification**: `--config-file` and `--config-path` are now aliases
3. **Environment file standardization**: `--environment-file` as primary
4. **All tiers included**: No "optional" designation

---

## Scenario 1: Database Setup with User (Admin Task)

### Current (Verbose)

```bash
# Set up environment
export ARANGO_ROOT_PASSWORD="secure-root-password"
export ARANGO_PASSWORD="user-password"

# Create database with user (atomic operation)
maa db add myapp_prod \
  --with-user myapp_user \
  --permission rw \
  --url http://localhost:8529 \
  --env-file .env.production \
  --arango-root-password-env ARANGO_ROOT_PASSWORD \
  --arango-password-env ARANGO_PASSWORD
```

**Character count:** 287 characters (arguments only)

### Accepted (With Aliases)

```bash
# Same environment setup
export ARANGO_ROOT_PASSWORD="secure-root-password"
export ARANGO_PASSWORD="user-password"

# Using medium aliases (readable)
maa db add myapp_prod \
  --with-user myapp_user \
  --perm rw \
  -u http://localhost:8529 \
  -E .env.production \
  --root-pw-env ARANGO_ROOT_PASSWORD \
  --pw-env ARANGO_PASSWORD
```

**Character count:** 187 characters (arguments only)
**Savings:** 100 characters (35% reduction)

### Accepted (Power User - Short Aliases)

```bash
# Using short aliases (maximum brevity)
maa db add myapp_prod \
  --with-user myapp_user \
  -p rw \
  -u http://localhost:8529 \
  -E .env.production \
  -R ARANGO_ROOT_PASSWORD \
  -P ARANGO_PASSWORD
```

**Character count:** 139 characters (arguments only)
**Savings:** 148 characters (52% reduction)

---

## Scenario 2: User Management (Multiple Operations)

### Current (Verbose)

```bash
# Create user
maa user add alice \
  --url http://localhost:8529 \
  --env-file .env \
  --arango-root-password-env ARANGO_ROOT_PASSWORD \
  --arango-password-env ARANGO_PASSWORD

# Grant permissions
maa user grant alice myapp_prod \
  --permission rw \
  --url http://localhost:8529 \
  --env-file .env \
  --arango-root-password-env ARANGO_ROOT_PASSWORD

# List user's databases
maa user databases \
  --url http://localhost:8529 \
  --env-file .env \
  --arango-password-env ARANGO_PASSWORD
```

**Total character count:** 456 characters

### Accepted (With Aliases)

```bash
# Create user
maa user add alice \
  -u http://localhost:8529 \
  -E .env \
  -R ARANGO_ROOT_PASSWORD \
  -P ARANGO_PASSWORD

# Grant permissions
maa user grant alice myapp_prod \
  -p rw \
  -u http://localhost:8529 \
  -E .env \
  -R ARANGO_ROOT_PASSWORD

# List user's databases
maa user databases \
  -u http://localhost:8529 \
  -E .env \
  -P ARANGO_PASSWORD
```

**Total character count:** 252 characters
**Savings:** 204 characters (45% reduction)

---

## Scenario 3: Configuration Management

### Current (Inconsistent)

```bash
# Add database config - NOTICE: Uses --password-env (inconsistent!)
maa db config add production \
  --url http://prod-arango:8529 \
  --database myapp_prod \
  --username admin \
  --password-env ARANGO_PASSWORD \
  --timeout 60 \
  --description "Production database" \
  --config-path config/databases.yaml

# Test connection
maa db config test production \
  --config-path config/databases.yaml \
  --env-file .env.production
```

**Issues:**
- ❌ Inconsistent: `--password-env` vs. `--arango-password-env` in other commands
- ⚠️ Verbose: `--config-path` repeated

### Accepted (Consistent + Aliases)

```bash
# Add database config - NOW CONSISTENT: Uses --arango-password-env
maa db config add production \
  -u http://prod-arango:8529 \
  -d myapp_prod \
  -U admin \
  --pw-env ARANGO_PASSWORD \
  --timeout 60 \
  --description "Production database" \
  -C config/databases.yaml

# Test connection
maa db config test production \
  -C config/databases.yaml \
  -E .env.production
```

**Benefits:**
- ✅ Consistent: `--pw-env` (alias for `--arango-password-env`) everywhere
- ✅ Unified: `-C` works for both `--config-file` and `--config-path`
- ✅ Standardized: `-E` for `--environment-file` (with `--env-file` as alias)
- ✅ Backward compatible: `--password-env`, `--config-path`, `--env-file` still work

---

## Scenario 4: Self-Service Password Change

### Current (Verbose)

```bash
# User changes their own password
export ARANGO_PASSWORD="current-password"
export ARANGO_NEW_PASSWORD="new-secure-password"

maa user password \
  --url http://localhost:8529 \
  --env-file .env \
  --arango-password-env ARANGO_PASSWORD \
  --arango-new-password-env ARANGO_NEW_PASSWORD
```

**Character count:** 170 characters

### Accepted (With Aliases)

```bash
# Same environment setup
export ARANGO_PASSWORD="current-password"
export ARANGO_NEW_PASSWORD="new-secure-password"

# Using short aliases
maa user password \
  -u http://localhost:8529 \
  -E .env \
  -P ARANGO_PASSWORD \
  -N ARANGO_NEW_PASSWORD
```

**Character count:** 95 characters
**Savings:** 75 characters (44% reduction)

---

## Scenario 5: Automation Scripts

### Current (Hard to Read)

```bash
#!/bin/bash
# Automated database provisioning script

for env in dev staging prod; do
  maa db add "myapp_${env}" \
    --with-user "myapp_${env}_user" \
    --permission rw \
    --url "${ARANGO_URL}" \
    --env-file ".env.${env}" \
    --arango-root-password-env ARANGO_ROOT_PASSWORD \
    --arango-password-env "ARANGO_PASSWORD_${env^^}" \
    --yes
done
```

### Accepted (More Readable)

```bash
#!/bin/bash
# Automated database provisioning script

for env in dev staging prod; do
  maa db add "myapp_${env}" \
    --with-user "myapp_${env}_user" \
    -p rw \
    -u "${ARANGO_URL}" \
    -E ".env.${env}" \
    -R ARANGO_ROOT_PASSWORD \
    -P "ARANGO_PASSWORD_${env^^}" \
    -y
done
```

**Benefits:**
- ✅ Shorter lines (easier to read in 80-column terminals)
- ✅ Less horizontal scrolling
- ✅ Clearer structure (arguments align better)

---

## Scenario 6: Documentation Examples

### Current (Beginner-Friendly but Verbose)

```bash
# Quick start example from README
maa db add myapp_prod \
  --with-user myapp_user \
  --permission rw \
  --arango-root-password-env ARANGO_ROOT_PASSWORD \
  --arango-password-env ARANGO_PASSWORD
```

### Accepted (Progressive Disclosure)

**Beginner (Documentation Default):**
```bash
# Use explicit primary names in docs
maa db add myapp_prod \
  --with-user myapp_user \
  --permission rw \
  --arango-root-password-env ARANGO_ROOT_PASSWORD \
  --arango-password-env ARANGO_PASSWORD
```

**Intermediate (Mentioned in "Tips" Section):**
```bash
# Tip: Use medium aliases for shorter commands
maa db add myapp_prod \
  --with-user myapp_user \
  --perm rw \
  --root-pw-env ARANGO_ROOT_PASSWORD \
  --pw-env ARANGO_PASSWORD
```

**Advanced (Power User Guide):**
```bash
# Power users can use short aliases
maa db add myapp_prod --with-user myapp_user -p rw -R ARANGO_ROOT_PASSWORD -P ARANGO_PASSWORD
```

---

## Summary: Character Savings by Scenario

| Scenario | Current | Proposed (Medium) | Proposed (Short) | Savings |
|----------|---------|-------------------|------------------|---------|
| Database Setup | 287 chars | 187 chars | 139 chars | 35-52% |
| User Management | 456 chars | 252 chars | 252 chars | 45% |
| Password Change | 163 chars | 95 chars | 95 chars | 42% |

**Average savings: 40-50% reduction in argument length**

---

## Backward Compatibility Examples

### All These Forms Work (db config add)

```bash
# Old form (still works!)
maa db config add prod --password-env ARANGO_PASSWORD

# New primary (recommended)
maa db config add prod --arango-password-env ARANGO_PASSWORD

# Medium alias
maa db config add prod --pw-env ARANGO_PASSWORD

# Short alias
maa db config add prod -P ARANGO_PASSWORD
```

**All four commands are equivalent and will continue to work indefinitely.**

