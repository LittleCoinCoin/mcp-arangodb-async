# CLI Consistency Enhancement - Implementation Prompt

## Context

I've completed **Milestone 1 (Test Baseline & Preparation)** of the CLI consistency enhancement project. The foundation is ready for implementation.

**What's Done:**
- ✅ Test baseline established: 77 tests passing, 2 warnings
- ✅ Feature branch created: `enhance/cli-consistency`
- ✅ Analysis reports committed (architecture, test definition, roadmap)
- ✅ Commit: `76681ab` - "docs: add CLI consistency enhancement analysis and roadmap"

**Current State:**
```bash
Branch: enhance/cli-consistency
Tests: 77/77 passing
Commits: 2 (1 from previous work + 1 from M1)
```

## Your Task

Implement the remaining milestones (M2 through M6) following the detailed roadmap in `__design__/cli-consistency-enhancement-roadmap.md`.

**Roadmap Structure:**
- **M2:** Phase 1 - Standardization (3-5 hours, 11 commits)
- **M3:** Phase 2 - Tier 1 Aliases (4-6 hours, 3 commits)
- **M4:** Phase 3 - Tier 2 & 3 Aliases (2-4 hours, 3 commits)
- **M5:** Phase 4 - Documentation (4-6 hours, 5 commits)
- **M6:** Final Validation & Release (1.5-2 hours, 4 commits)

**Total:** ~26 commits, 14.5-22.5 hours

## Instructions

1. **Read the roadmap:** `__design__/cli-consistency-enhancement-roadmap.md`
2. **Start with M2.T1:** Follow each task and step exactly as documented
3. **Use the exact commit messages** provided in the roadmap
4. **Run verification commands** after each step
5. **Ensure tests pass** before moving to the next step

Each milestone section in the roadmap includes:
- Pre-conditions and success criteria
- Specific file paths and line numbers
- Exact code changes to make
- Conventional commit messages
- Verification commands

## Critical Constraints

- ✅ **Zero breaking changes:** All existing argument names MUST continue to work
- ✅ **Backward compatibility:** Add 3 new backward compatibility tests in M2
- ✅ **Test-driven:** All 80+ tests must pass after every commit
- ✅ **Conventional commits:** Use exact commit messages from roadmap

## Supporting Documentation

- `__reports__/enhance_cli_consistency/00-architecture_analysis_v1.md` - Architecture details
- `__reports__/enhance_cli_consistency/01-test_definition_v1.md` - Test strategy
- `__reports__/enhance_cli_consistency/00-architecture_analysis_v1.md` - Argument mapping in context

## Expected Outcome

After completing all milestones:
- ✅ Version bumped to 0.5.1
- ✅ 3-tier alias system implemented (primary + medium + short)
- ✅ All documentation updated
- ✅ Pull request created and ready for merge
- ✅ 80+ tests passing
- ✅ Zero breaking changes

## Start Here

Begin with **Milestone 2, Task 1, Step 1** (M2.T1.S1) in the roadmap:
- File: `mcp_arangodb_async/__main__.py`
- Change: Update `server` command parser to add `--config-file` as primary
- Commit: `"feat(cli): add --config-file as primary with --config-path alias in server"`

The roadmap has everything you need. Follow it step by step.

