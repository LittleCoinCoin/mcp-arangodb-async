# Augment Prompts for Multi-Tenancy Implementation

## 1. Milestone 1.1: Core Infrastructure - Implementation

### 1.1 Original

#### Milestone 1.1 - Foundation Core Components

**GitHub Milestone**: <https://github.com/LittleCoinCoin/mcp-arangodb-async/milestones/1>

You are implementing **Milestone 1.1: Foundation Core Components** for mcp-arangodb-async v0.5.0 multi-tenancy feature.

##### Three Tasks (In Order)

###### 1️⃣ Task 1.1.1: SessionState Component

**Issue**: <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/1>

###### 2️⃣ Task 1.1.2: MultiDatabaseConnectionManager Component

**Issue**: <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/2>

###### 3️⃣ Task 1.1.3: ConfigFileLoader Component

**Issue**: <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/3>

##### Constraints

- Analytic behavior (read & study before actuation) `cracking-shells-playbook/instructions/analytic-behavior.instructions.md`
- Leverage the relevant code change phases sections on depending on the nature of the task (tests definition & implementation, feature implementation & testing, documentation) `cracking-shells-playbook/instructions/code-change-phases.instructions.md`
- Apply expected work ethics `cracking-shells-playbook/instructions/work-ethics.instructions.md`
- Follow org's git standards `cracking-shells-playbook/instructions/git-workflow.md`
  - Related changes grouped in single commits, Logical sequence of commits.
- This is NOT a Cracking Shells project so not all standards apply --> PRIORITISE THE STYLE AND ORGANISATION OF THE EXISTING REPO.

##### For Each Task

1. Read the GitHub issue (link above)
2. Review Architecture Design v3 (Section 2.1-2.3): `__reports__/multi_tenancy_analysis/01-architecture_design_v3.md`
3. Implement, document, commit following relevant org's standards
4. Comment on GitHub issue for **small** summary after completion
5. Move task to next task

##### Success Criteria

✅ All 3 tasks completed with success gates met
✅ All unit tests pass (90% coverage minimum)
✅ No regressions in existing functionality
✅ Ready to proceed to Milestone 1.2

---
**Next**: Milestone 1.2 Foundation Integration

### 2.2 Augmented

None

## 2. Milestone 1.1: Core Infrastructure - Closure

### 2.1 Original

Great Work. Everything seems fine from the perspective of the stakeholders. Let's move toward closure of this milestone.

**Your Tasks**:

1. Push your changes to origin
2. PR to origin/feat/multi-arangodb-tenancy

- Include closing keywords for the relevant issues

3. Once finished, give me in this chat a user prompt I can use to transition smoothly to the development for milestone 1.2

**Constraints**:

- For consistency, stakeholders would like you to follow the git branching standards of roadmap-based feature implementation `cracking-shells-playbook\instructions\roadmap-generation.instructions.md` section `## Git Workflow`
  - In the current case, you can just go with a single milestone branch `milestone/1.1-core-infrastructure` and disregard the task branches.
  - And the current working branch `feat/multi-arangodb-tenancy` can reset to three commits ago
  - This will enable a clean PR for long-term traceability.
- Respect all other standards regarding analytic behavior and work ethics.

### 2.2 Augmented

Excellent work on Milestone 1.1! The implementation meets all stakeholder requirements. Now let's prepare for milestone closure with proper git workflow and create a clean PR for long-term traceability.

#### Your Tasks

##### 1. Restructure Git History Following Roadmap-Based Feature Standards

Following the git branching standards in `cracking-shells-playbook/instructions/roadmap-generation.instructions.md` section `## Git Workflow`:

**Current State:**

- Working branch: `feat/multi-arangodb-tenancy`
- Contains 3 commits for Milestone 1.1 tasks (commits: `2909aed`, `a962768`, `2b248c3`)

**Required Actions:**

1. Create a new milestone branch: `milestone/1.1-core-infrastructure` from the current `feat/multi-arangodb-tenancy` branch
2. Reset `feat/multi-arangodb-tenancy` to 3 commits ago (before the Milestone 1.1 work)
3. Verify that `milestone/1.1-core-infrastructure` contains all 3 Milestone 1.1 commits

**Note:** Disregard task-level branches for this milestone (no need for `task/1.1.1-session-state`, etc.)

##### 2. Push Changes to Remote

Push the new milestone branch to origin:

- `git push origin milestone/1.1-core-infrastructure`

##### 3. Create Pull Request

Create a PR from `milestone/1.1-core-infrastructure` to `feat/multi-arangodb-tenancy` with:

- **Title:** `feat: Milestone 1.1 - Foundation Core Components`
- **Description:** Include:
  - Summary of the 3 implemented components (SessionState, MultiDatabaseConnectionManager, ConfigFileLoader)
  - Test coverage metrics (all >90%, total 32 tests passing)
  - Closing keywords for issues: `Closes #1`, `Closes #2`, `Closes #3`
  - Link to milestone: <https://github.com/LittleCoinCoin/mcp-arangodb-async/milestones/1>
  - Confirmation that success criteria are met

##### 4. Provide Transition Prompt

Once the PR is created and you've confirmed all steps are complete, provide me with a ready-to-use prompt that I can copy-paste to smoothly transition to Milestone 1.2 development.

#### Constraints

- Follow analytic behavior: read and verify git state before making changes
- Apply work ethics: verify each step completes successfully before proceeding
- Follow git workflow standards from `cracking-shells-playbook/instructions/roadmap-generation.instructions.md` section `## Git Workflow`
- Ensure clean git history for long-term traceability
- Do NOT push or create PR without explicit confirmation that git restructuring is correct-

## 3. Milestone 1.2: Foundation Integration - Implementation

### 3.1 Original

#### Milestone 1.2 - Foundation Integration

**GitHub Milestone:** <https://github.com/LittleCoinCoin/mcp-arangodb-async/milestones/2>

You are implementing **Milestone 1.2: Foundation Integration** for mcp-arangodb-async v0.5.0 multi-tenancy feature.

##### Milestone Overview

Integrate the three foundation core components (SessionState, MultiDatabaseConnectionManager, ConfigFileLoader) into the MCP server entry point and implement database resolution logic.

##### Three Tasks (In Order)

###### 1️⃣ Task 1.2.1: Database Resolver

**Issue:** <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/4>

###### 2️⃣ Task 1.2.2: Session ID Extraction

**Issue:** <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/5>

###### 3️⃣ Task 1.2.3: Entry Point Integration

**Issue:** <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/6>

##### Constraints

- Analytic behavior (read & study before actuation) `cracking-shells-playbook/instructions/analytic-behavior.instructions.md`
- Leverage the relevant code change phases sections on depending on the nature of the task (tests definition & implementation, feature implementation & testing, documentation) `cracking-shells-playbook/instructions/code-change-phases.instructions.md`
- Apply expected work ethics `cracking-shells-playbook/instructions/work-ethics.instructions.md`
- Follow org's git standards `cracking-shells-playbook/instructions/git-workflow.md`
  - Related changes grouped in single commits, Logical sequence of commits.
  - follow branching standards `cracking-shells-playbook/instructions/roadmap-generation.instructions.md` section `## Git Workflow` (milestone branches from feature branch, task branches from milestone branches)
- This is NOT a Cracking Shells project so not all standards apply --> PRIORITISE THE STYLE AND ORGANISATION OF THE EXISTING REPO.

##### For Each Task

1. Read the GitHub issue
2. Review Architecture Design v3 (Section 2.4-2.6): `__reports__/multi_tenancy_analysis/01-architecture_design_v3.md`
3. Implement, document, commit following relevant org's standards
4. Comment on GitHub issue for **small** summary after completion
5. Move to next task

##### Success Criteria

✅ All 3 tasks completed with success gates met
✅ All unit tests pass (90% coverage minimum)
✅ No regressions in existing functionality
✅ Ready to proceed to Milestone 2.1: Tool Renaming

##### Next

Milestone 2.1: Tool Renaming (rename 3 design pattern tools to eliminate context ambiguity)

---

**Status:** Ready to begin  
**Previous Milestone:** [1.1 - Foundation Core Components](https://github.com/LittleCoinCoin/mcp-arangodb-async/pulls/23) ✅
**Next Milestone:** [2.1 - Tool Renaming](https://github.com/LittleCoinCoin/mcp-arangodb-async/milestone/3)

### 3.2 Augmented

None

## 4. Milestone 1.2: Foundation Integration - Closure

### 4.1 Original (reusing `Augmented` from 2.2)

Excellent work on Milestone 1.2! The implementation meets all stakeholder requirements. Now let's prepare for milestone closure with proper git workflow and create a clean PR for long-term traceability.

#### Your Tasks

##### 1. Restructure Git History Following Roadmap-Based Feature Standards

Following the git branching standards in `cracking-shells-playbook/instructions/roadmap-generation.instructions.md` section `## Git Workflow`:

**Current State:**

- Working branch: `feat/multi-arangodb-tenancy`
- Contains 3 commits for Milestone 1.2 tasks (commits: `3da3d88`, `85700c3`, `9622aee`)

**Required Actions:**

1. Create a new milestone branch: `milestone/1.2-foundation-integration` from the current `feat/multi-arangodb-tenancy` branch
2. Reset `feat/multi-arangodb-tenancy` to 3 commits ago (before the Milestone 1.2 work)
3. Verify that `milestone/1.2-foundation-integration` contains all 3 Milestone 1.2 commits

**Note:** Disregard task-level branches for this milestone (no need for `task/1.2.1-database-resolver`, etc.)

##### 2. Push Changes to Remote

Push the new milestone branch to origin:

- `git push origin milestone/1.2-foundation-integration`

##### 3. Create Pull Request

Create a PR from `milestone/1.2-foundation-integration` to `feat/multi-arangodb-tenancy` with:

- **Title:** `feat: Milestone 1.2 - Foundation Integration`
- **Description:** Include:
  - Summary of the 3 implemented components (Database Resolver, Session ID Extraction, Entry Point Integration)
  - Test coverage metrics (all >90%, total 32 tests passing)
  - Closing keywords for issues: `Closes #4`, `Closes #5`, `Closes #6`

##### 4. Provide Transition Prompt

Once the PR is created and you've confirmed all steps are complete, provide me with a ready-to-use prompt that I can copy-paste to smoothly transition to Milestone 2.1 development `https://github.com/LittleCoinCoin/mcp-arangodb-async/milestone/3`.

#### Constraints

- Follow analytic behavior: read and verify git state before making changes
- Apply work ethics: verify each step completes successfully before proceeding
- Follow git workflow standards from `cracking-shells-playbook/instructions/roadmap-generation.instructions.md` section `## Git Workflow`
- Ensure clean git history for long-term traceability
- Do NOT push or create PR without explicit confirmation that git restructuring is correct-

### 4.2 Augmented

None

## 5. Milestone 2.1: Tool Renaming - Implementation

### 5.1 Original

We have successfully completed:

- **Milestone 1.1: Foundation Core Components** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/23>
- **Milestone 1.2: Foundation Integration** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/24>

This closes Phase 1: Foundation (1.1 + 1.2) on the roadmap `__reports__/multi_tenancy_analysis/02-implementation_roadmap_v3.md`.

**Next: Milestone 2.1 - Tool Renaming**

GitHub Milestone: <https://github.com/LittleCoinCoin/mcp-arangodb-async/milestones/3>

#### Milestone Overview

Rename symbols to eliminate context ambiguity.

#### Three Tasks (In Order)

##### 1️⃣ Task 2.1.1: Constant and Models

**Issue:** <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/7>

##### 2️⃣ Task 2.1.2: Handlers and Tests

**Issue:** <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/8>

##### 3️⃣ Task 2.1.3: Documentation

**Issue:** <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/9>

#### Constraints

- Prioritize existing repo style and organization
- Follow git workflow standards from `cracking-shells-playbook/instructions/roadmap-generation.instructions.md` section `## Git Workflow`
  - Branching policy follow milestones and tasks
  - conventional commits `cracking-shells-playbook/instructions/git-workflow.md`
- Analytic behavior (read & study before actuation) `cracking-shells-playbook/instructions/analytic-behavior.instructions.md`
- Work ethics (rigor and perseverance) `cracking-shells-playbook/instructions/work-ethics.instructions.md`
- Leverage relevant code change phases sections `cracking-shells-playbook/instructions/code-change-phases.instructions.md`

#### For Each Task

1. Read the GitHub issue
2. Review Architecture Design v3 (Section 2.8): `__reports__/multi_tenancy_analysis/01-architecture_design_v3.md` and section `## Phase 2: Tool Renaming (Week 2, Days 1-3)` from `__reports__/multi_tenancy_analysis/02-implementation_roadmap_v3.md`
3. Implement, document, commit following relevant org's standards
4. Comment on GitHub issue for small summary after completion
5. Update changelog `docs/developer-guide/changelog.md`
6. Move to next task

#### Success Criteria

✅ All 3 tasks completed with success gates met
✅ All unit tests pass (90% coverage minimum)

- No new tests required --> BUT no regressions
✅ Ready to proceed to Milestone 3.1: State Migration

#### Next

Milestone 3.1: State Migration <https://github.com/LittleCoinCoin/mcp-arangodb-async/milestone/4>

### 5.2 Augmented

None

## 6. Milestone 2.1: Tool Renaming - Closure

### 6.1 Original

Great Work. Everything seems fine from the perspective of the stakeholders. Let's move toward closure of this milestone.

**Your Tasks**:

1. Push your changes to origin
2. PR to origin/feat/multi-arangodb-tenancy

- Include closing keywords for the relevant issues (<https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword>)

3. Once finished, give me in this chat a user prompt I can use to transition smoothly to the development for milestone 3.1

**Constraints**:

- Respect all standards regarding analytic behavior and work ethics.

### 6.2 Augmented

Excellent work on Milestone 2.1 - Tool Renaming. All tasks are complete and tests are passing. Let's proceed with milestone closure.

**Your Tasks**:

1. **Push the branch to origin**
   - Push `milestone/2.1-tool-renaming` branch to remote repository

2. **Create Pull Request**
   - Target branch: `feat/multi-arangodb-tenancy` (base branch for multi-tenancy feature)
   - Source branch: `milestone/2.1-tool-renaming`
   - PR Title: Follow conventional format (e.g., "feat: rename workflow tools to eliminate context ambiguity")
   - PR Description: Include:
     - Summary of the 3 completed tasks (2.1.1, 2.1.2, 2.1.3)
     - Breaking changes notice (tool renamings)
     - Test results (121 tests passing)
     - Closing keywords for issues #7, #8, and #9 using GitHub syntax:
       - `Closes #7` (Task 2.1.1: Constants and Models)
       - `Closes #8` (Task 2.1.2: Handlers and Tests)
       - `Closes #9` (Task 2.1.3: Documentation)
     - Reference to Milestone: <https://github.com/LittleCoinCoin/mcp-arangodb-async/milestone/3>

3. **Provide transition prompt**
   - After PR is created, provide a ready-to-use user prompt that I can copy-paste to begin Milestone 3.1: State Migration
   - The prompt should reference:
     - Completion of Milestone 2.1
     - The merged PR (or ready-to-merge PR)
     - Milestone 3.1 GitHub link: <https://github.com/LittleCoinCoin/mcp-arangodb-async/milestone/4>
     - Issue #10: <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/10>
     - Relevant architecture sections from `__reports__/multi_tenancy_analysis/01-architecture_design_v3.md` and `__reports__/multi_tenancy_analysis/02-implementation_roadmap_v3.md`

**Constraints**:

- Follow analytic behavior: study & read before actuation on the codebase `cracking-shells-playbook/instructions/analytic-behavior.instructions.md`
- Follow work ethics (rigor and perseverance) `cracking-shells-playbook/instructions/work-ethics.instructions.md`
- Follow git workflow standards from `cracking-shells-playbook/instructions/git-workflow.md`
- Use conventional commit format for PR title
- Do NOT merge the PR - leave it for review

## 7. Milestone 3.1 State Migration: Tools - Implementation

### 7.1 Original

Generated from the end of `Milestone 2.1 implementation - Closure`

---

We have successfully completed:

- **Milestone 1.1: Foundation Core Components** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/23>
- **Milestone 1.2: Foundation Integration** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/24>
- **Milestone 2.1: Tool Renaming** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/25>

This closes Phase 1 (1.1 + 1.2) and Phase 2 (2.1) on the roadmap `__reports__/multi_tenancy_analysis/02-implementation_roadmap_v3.md`.

**Next: Milestone 3.1 - State Migration: Tools**

GitHub Milestone: <https://github.com/LittleCoinCoin/mcp-arangodb-async/milestone/4>

#### Milestone Overview

Migrate 6 design pattern tools + 1 helper from global variables to per-session state

#### Three Tasks (In Order)

##### 1️⃣ Task 3.1.1: Workflow Tool State Migration

**Issue:** <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/10>

##### 2️⃣ Task 3.1.2: Lifecycle Tool State Migration

**Issue:** <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/11>

##### 3️⃣ Task 3.1.3: Usage Stats State Migration

**Issue:** <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/12>

#### Constraints

- Prioritize existing repo style and organization
- Follow git workflow standards from `cracking-shells-playbook/instructions/roadmap-generation.instructions.md` section `## Git Workflow`
  - Branching policy follow milestones and tasks
  - conventional commits `cracking-shells-playbook/instructions/git-workflow.md`
- Analytic behavior (read & study before actuation) `cracking-shells-playbook/instructions/analytic-behavior.instructions.md`
- Work ethics (rigor and perseverance) `cracking-shells-playbook/instructions/work-ethics.instructions.md`
- Leverage relevant code change phases sections `cracking-shells-playbook/instructions/code-change-phases.instructions.md`

#### Architecture Reference

Review the following sections before implementation:

- `__reports__/multi_tenancy_analysis/02-implementation_roadmap_v3.md` Phase 3: State Migration
- `__reports__/multi_tenancy_analysis/01-architecture_design_v3.md`

#### For Each Task

1. Read the GitHub issue
2. Review Architecture Design v3 and Implementation Roadmap v3
3. Implement, document, commit following relevant org's standards

- These issues are migration-oriented --> You might not need to write tests OR you might need to write new tests and remove the deprecated tests

4. Comment on GitHub issue for small summary after completion
5. Update changelog `docs/developer-guide/changelog.md`
6. Move to next task

#### Success Criteria

✅ All tasks completed with success gates met
✅ All unit tests pass (90% coverage minimum)

- No new tests required --> BUT no regressions
✅ Ready to proceed to Milestone 3.2: Data Tool Migration

#### Next

Milestone 3.2: Data Tool Migration <https://github.com/LittleCoinCoin/mcp-arangodb-async/milestone/5>

### 7.2 Augmented

None

## 8. Milestone 3.1: State Migration - Closure

### 8.1 Original

Great Work. Everything seems fine from the perspective of the stakeholders. Let's move toward closure of this milestone.

**Your Tasks**:

1. Push your changes to origin
2. PR to origin/feat/multi-arangodb-tenancy

- Include closing keywords for the relevant issues

3. Once finished, give me in this chat a user prompt I can use to transition smoothly to the development for milestone 3.2

**Constraints**:

- Respect all standards regarding analytic behavior and work ethics.

### 8.2 Augmented

Excellent work on Milestone 3.1: State Migration - Tools. The implementation meets all stakeholder requirements. Let's proceed with the milestone closure process.

#### Your Tasks

##### 1. Push Changes to Remote Repository

Push the `milestone/3.1-state-migration-tools` branch to the remote repository (`origin`).

##### 2. Create Pull Request

Create a pull request from `milestone/3.1-state-migration-tools` to `feat/multi-arangodb-tenancy` with the following requirements:

**PR Title:**

```
Milestone 3.1 - State Migration: Tools
```

**PR Description Must Include:**

- Summary of the 3 completed tasks (3.1.1, 3.1.2, 3.1.3)
- List of migrated handlers (6 tools + 1 helper)
- Test results (number of tests passing, coverage maintained)
- Reference to Milestone 3.1: <https://github.com/LittleCoinCoin/mcp-arangodb-async/milestone/4>
- Closing keywords for the relevant issues:
  - `Closes #10` (Task 3.1.1: Workflow Tools Migration)
  - `Closes #11` (Task 3.1.2: Lifecycle Tools Migration)
  - `Closes #12` (Task 3.1.3: Usage Stats Migration)

**PR Checklist:**

- [ ] All unit tests pass (minimum 90% coverage maintained)
- [ ] No regressions introduced
- [ ] Changelog updated (`docs/developer-guide/changelog.md`)
- [ ] All 3 GitHub issues commented with completion summaries
- [ ] Follows conventional commit format
- [ ] Ready for review

##### 3. Provide Transition Prompt

After the PR is created and all tasks are complete, provide me with a ready-to-use prompt that I can copy-paste to smoothly transition to **Milestone 3.2: Data Tool Migration** (<https://github.com/LittleCoinCoin/mcp-arangodb-async/milestone/5>).

The transition prompt should:

- Reference the completed Milestone 3.1 PR
- Link to Milestone 3.2 and its associated GitHub issues
- Specify the same constraints and standards (git workflow, analytic behavior, work ethics, code change phases)
- Follow the same structured format as the original Milestone 3.1 prompt

#### Constraints

- Follow all organizational standards from `cracking-shells-playbook/instructions/`:
  - Analytic behavior (`analytic-behavior.instructions.md`)
  - Work ethics (`work-ethics.instructions.md`)
  - Git workflow (`git-workflow.md`)
  - Conventional commits format
- Verify all tests pass before pushing
- Ensure PR description is comprehensive and professional
- Do not proceed to Milestone 3.2 implementation yet—only provide the transition prompt

## 9. Milestone 3.2: Data Tool Migration - Implementation

### 9.1 Original

#### Milestone 3.2 State Migration: Cleanup

We have successfully completed:

- **Milestone 1.1: Foundation Core Components** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/23>
- **Milestone 1.2: Foundation Integration** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/24>
- **Milestone 2.1: Tool Renaming** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/25>
- **Milestone 3.1: State Migration - Tools** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/26>

This closes Phase 1 (1.1 + 1.2), Phase 2 (2.1), and Milestone 3.1 on the roadmap `__reports__/multi_tenancy_analysis/02-implementation_roadmap_v3.md`.

**Next: Milestone 3.2 - State Migration: Cleanup**

GitHub Milestone: <https://github.com/LittleCoinCoin/mcp-arangodb-async/milestone/5>

##### Milestone Overview

Remove global variables and verify concurrent session isolation

##### Two Tasks (In Order)

###### 1️⃣ Task 3.2.1: Global Variable Removal

**Issue:** <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/13>

###### 2️⃣ Task 3.2.2: Verification

**Issue:** <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/14>

##### Constraints

- Prioritize existing repo style and organization
- Follow git workflow standards from `cracking-shells-playbook/instructions/roadmap-generation.instructions.md` section `##### Git Workflow`
  - Branching policy follow milestones and tasks
  - conventional commits `cracking-shells-playbook/instructions/git-workflow.md`
- Analytic behavior (read & study before actuation) `cracking-shells-playbook/instructions/analytic-behavior.instructions.md`
- Work ethics (rigor and perseverance) `cracking-shells-playbook/instructions/work-ethics.instructions.md`
- Leverage relevant code change phases sections `cracking-shells-playbook/instructions/code-change-phases.instructions.md`

##### Architecture Reference

Review the following sections before implementation:

- `__reports__/multi_tenancy_analysis/02-implementation_roadmap_v3.md` Phase 3 (Milestone 3.2)
- `__reports__/multi_tenancy_analysis/01-architecture_design_v3.md` Section 2.8

##### For Each Task

1. Read the GitHub issue
2. Review Architecture Design v3 and Implementation Roadmap v3
3. Implement, document, commit following relevant org's standards

- Task 3.2.1: Remove deprecated code, update tests
- Task 3.2.2: Write/verify isolation tests

4. Comment on GitHub issue for small summary after completion
5. Update changelog `docs/developer-guide/changelog.md`
6. Move to next task

##### Success Criteria

✅ All tasks completed with success gates met
✅ All unit tests pass (90% coverage minimum)
✅ Global variables completely removed (grep returns 0 results)
✅ Concurrent session isolation verified
✅ Ready to proceed to Phase 4: Tool Implementation

##### Next

Phase 4: Tool Implementation (Milestone 4.1 + 4.2)

- Milestone 4.1: <https://github.com/LittleCoinCoin/mcp-arangodb-async/milestone/6>

## 10. Milestone 4.1: Tool Model Updates - Implementation

### 10.1 Original

#### Milestone 4.1 - Database Override: Tool Update (Models + Handlers)

We have successfully completed:

- **Milestone 1.1: Foundation Core Components** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/23>
- **Milestone 1.2: Foundation Integration** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/24>
- **Milestone 2.1: Tool Renaming** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/25>
- **Milestone 3.1: State Migration - Tools** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/27>
- **Milestone 3.2: State Migration - Cleanup** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/29>

This closes Phase 1 (1.1 + 1.2), Phase 2 (2.1), Phase 3 (3.1 + 3.2), and Milestone 3 on the roadmap `__reports__/multi_tenancy_analysis/02-implementation_roadmap_v3.md`.

**Next: Milestone 4.1 - Database Override: Tool Models**

GitHub Milestone: <https://github.com/LittleCoinCoin/mcp-arangodb-async/milestone/6>

##### Milestone Overview

Implement optional database parameter in tool models and handlers

##### Two Tasks (In Order)

###### 1️⃣ Task 4.1.1: Tool Models Update

**Issue:** <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/15>

###### 2️⃣ Task 4.1.2: Handler Updates

**Issue:** <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/16>

##### Constraints

- Prioritize existing repo style and organization
- Follow git workflow standards from `cracking-shells-playbook/instructions/roadmap-generation.instructions.md` section `##### Git Workflow`
  - Branching policy follow milestones and tasks
  - conventional commits `cracking-shells-playbook/instructions/git-workflow.md`
- Analytic behavior (read & study before actuation) `cracking-shells-playbook/instructions/analytic-behavior.instructions.md`
- Work ethics (rigor and perseverance) `cracking-shells-playbook/instructions/work-ethics.instructions.md`
- Leverage relevant code change phases sections `cracking-shells-playbook/instructions/code-change-phases.instructions.md`

##### Architecture Reference

Review the following sections before implementation:

- `__reports__/multi_tenancy_analysis/02-implementation_roadmap_v3.md` Phase 4 (Milestone 4.1)
- `__reports__/multi_tenancy_analysis/01-architecture_design_v3.md` Section 2.9

##### For Each Task

1. Read the GitHub issue
2. Review Architecture Design v3 and Implementation Roadmap v3
3. Implement, document, commit following relevant org's standards

- Task 4.1.1: Add `database: Optional[str]` to all 35 tool models
- Task 4.1.2: Update all 35 tool handlers to use database resolution

4. Comment on GitHub issue for small summary after completion
5. Update changelog `docs/developer-guide/changelog.md` and version number in `pyproject.toml`
6. Move to next task

##### Success Criteria

✅ All tasks completed with success gates met
✅ All unit tests pass (90% coverage minimum)
✅ All 35 tool models updated with `database: Optional[str] = Field(default=None, description="Database override")`
✅ All 35 tool handlers updated to use database resolution
✅ Ready to proceed to Milestone 4.2
✅ PR of milestone branch to `feat/multi-arangodb-tenancy` ready for review

##### Next

Milestone 4.2 (Multi-tenancy Tools): <https://github.com/LittleCoinCoin/mcp-arangodb-async/milestone/7>

### 10.2 Augmented

None

## 11. Milestone 4.2: Multi-tenancy Tools - Implementation

### 11.1 Original

#### Milestone 4.2 - Multi-tenancy Tools

We have successfully completed:

- **Milestone 1.1: Foundation Core Components** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/23>
- **Milestone 1.2: Foundation Integration** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/24>
- **Milestone 2.1: Tool Renaming** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/25>
- **Milestone 3.1: State Migration - Tools** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/27>
- **Milestone 3.2: State Migration - Cleanup** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/29>
- **Milestone 4.1: Database Override - Tool Models** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/30>

This closes Phase 1 (1.1 + 1.2), Phase 2 (2.1), Phase 3 (3.1 + 3.2), Phase 4.1 (4.1), and Milestone 4 on the roadmap `__reports__/multi_tenancy_analysis/02-implementation_roadmap_v3.md`.

**Next: Milestone 4.2 - Multi-tenancy Tools**

GitHub Milestone: <https://github.com/LittleCoinCoin/mcp-arangodb-async/milestone/7>

##### Milestone Overview

Implement 6 multi-tenancy MCP tools, CLI tool, and documentation.

##### Three Tasks (In Order)

###### 1️⃣ Task 4.2.1: MCP Tools Implementation

**Issue:** <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/17>

###### 2️⃣ Task 4.2.2: CLI Tool Implementation

**Issue:** <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/18>

###### 3️⃣ Task 4.2.3: Documentation

**Issue:** <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/19>

##### Constraints

- Prioritize existing repo style and organization
- Follow git workflow standards from `cracking-shells-playbook/instructions/roadmap-generation.instructions.md` section `##### Git Workflow`
  - Branching policy follow milestones and tasks
  - conventional commits `cracking-shells-playbook/instructions/git-workflow.md`
- Analytic behavior (read & study before actuation) `cracking-shells-playbook/instructions/analytic-behavior.instructions.md`
- Work ethics (rigor and perseverance) `cracking-shells-playbook/instructions/work-ethics.instructions.md`
- Leverage relevant code change phases sections `cracking-shells-playbook/instructions/code-change-phases.instructions.md`

##### Architecture Reference

Review the following sections before implementation:

- `__reports__/multi_tenancy_analysis/02-implementation_roadmap_v3.md` Phase 4 (Milestone 4.2)
- `__reports__/multi_tenancy_analysis/01-architecture_design_v3.md` Section 2.10

##### For Each Task

1. Read the GitHub issue
2. Review Architecture Design v3 and Implementation Roadmap v3
3. Implement, document, commit following relevant org's standards
   - Task 4.2.1: Implement 6 MCP tools
   - Task 4.2.2: Implement CLI tool
   - Task 4.2.3: Write documentation
4. Comment on GitHub issue for small summary after completion
5. Update changelog `docs/developer-guide/changelog.md` and version number in `pyproject.toml`
6. Move to next task

##### Success Criteria

✅ All tasks completed with success gates met
✅ All unit tests pass (90% coverage minimum)
✅ All 6 MCP tools implemented and passing tests
✅ CLI tool implemented and passing tests
✅ Documentation complete (README, CLI reference, user guide, database setup, database tools behavior, etc...)
✅ Documentation conforms to style guide and integrates seamlessly with existing documentation
✅ Documentation is educative with grounded examples from simple to advanced
✅ Ready to proceed to Phase 5: Verification & Release

##### Next

Phase 5: Verification & Release (Milestone 5.1) <https://github.com/LittleCoinCoin/mcp-arangodb-async/milestone/8>

## 12. Deciding whether to proceed to Phase 5: Verification & Release or add better setup CLIs

### 12.1 Original

We have successfully completed:

- **Milestone 1.1: Foundation Core Components** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/23>
- **Milestone 1.2: Foundation Integration** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/24>
- **Milestone 2.1: Tool Renaming** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/25>
- **Milestone 3.1: State Migration - Tools** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/27>
- **Milestone 3.2: State Migration - Cleanup** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/29>
- **Milestone 4.1: Database Override - Tool Models** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/30>
- **Milestone 4.2 (Task 4.2.1): Multi-tenancy Tools** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/31>
- **Milestone 4.2 (Task 4.2.2 + 4.2.3): Setup CLIs** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/32>

This closes Phase 1 (1.1 + 1.2), Phase 2 (2.1), Phase 3 (3.1 + 3.2), Phase 4.1 (4.1), and Milestone 4 on the roadmap `__reports__/multi_tenancy_analysis/02-implementation_roadmap_v3.md`.

We are facing the choice to move toward closure of the dev sprint with the next Milestone <https://github.com/LittleCoinCoin/mcp-arangodb-async/milestone/8>
However, stakeholders are hesitating because two non-negligeable features were  identified as missing from the initial scope. Read:
- https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/33
- https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/34

Probably, the most important one being #33.
Moreover, despite the suggestions in #33 and #34, actual decisions have not been made and lots remained to discussed to make them clean.

**Your tasks**: Evaluate the propositions in #33 and #34 and report back to the team.

**Constraints**:
- Follow analytic behavior: study & read before actuation on the codebase `cracking-shells-playbook/instructions/analytic-behavior.instructions.md`
- Follow work ethics (rigor and perseverance) `cracking-shells-playbook/instructions/work-ethics.instructions.md`
- Follow git workflow standards from `cracking-shells-playbook/instructions/git-workflow.md`
- Follow reporting standards from `cracking-shells-playbook/instructions/reporting.instructions.md`

### 12.3 Augmented

None

## 13. Going for issue #33: Admin Tools for Database & User Management

### 13.1 Original

Stakeholders have decided to indeed proceed with tackling #33 but your reduced scope is not acceptable for them. Anyway, they prefer to go through a proper `cracking-shells-playbook\instructions\code-change-phases.instructions.md` cycle for this tasks to take the time to properly engineer this CLI even if delays ensue. 
Moreover, for clarity, stakeholders prefer to insert an additional milestone 4.3 between 4.2 and 5.0 to contain this work.

**Your Task**: 
1. Leverage `cracking-shells-playbook\instructions\code-change-phases.instructions.md`  and `cracking-shells-playbook\instructions\roadmap-generation.instructions.md` to create a focused 1-milestone roadmap for this work. Tasks 4.3.1 will at least involve figuring out the scope of this feature as in Phase 1 of the code change phases.
2. Report back the roadmap to the stakeholders in `__reports__/multi_tenancy_analysis/04-admin_cli_roadmap_v0.md`

**Constraints**:
- Follow analytic behavior: study & read before actuation on the codebase `cracking-shells-playbook/instructions/analytic-behavior.instructions.md`
- Follow work ethics (rigor and perseverance) `cracking-shells-playbook/instructions/work-ethics.instructions.md`
- Follow reporting standards from `cracking-shells-playbook/instructions/reporting.instructions.md`

### 13.2 Augmented

None

## 14. Starting work on Milestone 4.3: Admin CLI

### 14.1 Original

We have successfully completed:

- **Milestone 1.1: Foundation Core Components** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/23>
- **Milestone 1.2: Foundation Integration** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/24>
- **Milestone 2.1: Tool Renaming** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/25>
- **Milestone 3.1: State Migration - Tools** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/27>
- **Milestone 3.2: State Migration - Cleanup** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/29>
- **Milestone 4.1: Database Override - Tool Models** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/30>
- **Milestone 4.2: Multi-tenancy Tools** <https://github.com/LittleCoinCoin/mcp-arangodb-async/pull/31>

This closes Phase 1 (1.1 + 1.2), Phase 2 (2.1), Phase 3 (3.1 + 3.2), Phase 4.1 (4.1), Phase 4.2 (4.2), and Milestone 4 on the roadmap `__reports__/multi_tenancy_analysis/02-implementation_roadmap_v3.md`.

**Next: Milestone 4.3 - Admin CLI**

GitHub Milestone: <https://github.com/LittleCoinCoin/mcp-arangodb-async/milestone/9>

#### Milestone Overview

Read the `__reports__/multi_tenancy_analysis/04-admin_cli_roadmap_v0.md` report.

This milestones contains one critical task (4.3.1) that I want to iterate on with you before implementation: issue <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/35> --> the **Scope Analysis & Design** task.

Although the issue and prior report `__reports__/multi_tenancy_analysis/04-admin_cli_roadmap_v0.md` contain a lot of information, I think we can do better. In particular, I am not satisfied with the logic of the proposed CLI. First, let's compare the proposed CLI with the existing `mcp-arangodb-async db` CLI:
1. Note the existing CLI is very short and sweet. 
2. it uses `db` as the main command for config file management
3. The proposed `admin` has a sub-command `database` and `user`. It's hard to know what the admin is for. 
   - The "admin" could be skipped entirely, no? why not using the argument `--env-password` like in the existing CLI and that will require the `root` password. Hence, it's implicit that you need to be an admin to perform these actions.
   - the original setup script `scripts\setup-arango.ps1` was creating a database and a user at the same time, no? But the proposed CLI separates the two. it makes sense, in particular with the grant/revoke commands. But shouldn't the `create` command have an option to create/assign a user at the same time?
   - we must have --dry-run option with clear line-by-line output of what will be created/modified/deleted.
4. Makes me think that we also need a `version` command to check the version of the CLI and the library it's based on.
   - This should rely on python lib reflection (`importlib.metadata.version`, or something like that, I forgot the exact name), not a separate versioning. It's bad practice to duplicate the version number and hardcode `__version__` in multiple places.

Anyway, there is a lot to consider

**Your Task**: 
1. Review the proposed CLI
2. Review the existing CLI
3. Analyze and suggest improvements in making the proposed CLI more ergonomic
4. Report back in `__reports__/multi_tenancy_analysis/cli_enhancements/`

**Constraints**:
- Follow analytic behavior: study & read before actuation on the codebase `cracking-shells-playbook/instructions/analytic-behavior.instructions.md`
- Follow work ethics (rigor and perseverance) `cracking-shells-playbook/instructions/work-ethics.instructions.md`
- Follow reporting standards from `cracking-shells-playbook/instructions/reporting.instructions.md`

### 14.2 Augmented

#### Context

We have successfully completed Milestones 1.1, 1.2, 2.1, 3.1, 3.2, 4.1, and 4.2 (PRs #23-31), closing Phases 1-4.2 on the roadmap `__reports__/multi_tenancy_analysis/02-implementation_roadmap_v3.md`.

**Next: Milestone 4.3 - Admin CLI**
- GitHub Milestone: <https://github.com/LittleCoinCoin/mcp-arangodb-async/milestone/9>
- Critical Task: Issue #35 (Scope Analysis & Design) - <https://github.com/LittleCoinCoin/mcp-arangodb-async/issues/35>

#### Problem Statement

The proposed CLI design in `__reports__/multi_tenancy_analysis/04-admin_cli_roadmap_v0.md` needs refinement. After reviewing the proposal against the existing `mcp-arangodb-async db` CLI, I've identified several ergonomic concerns that require deeper analysis before implementation.

#### Specific Concerns to Address

##### 1. Command Structure & Naming
- **Existing CLI**: Uses `db` as the main command for config file management (simple, clear)
- **Proposed CLI**: Uses `admin` with sub-commands `database` and `user`
- **Issue**: The `admin` prefix is ambiguous and adds unnecessary hierarchy
- **Question**: Can we eliminate the `admin` prefix and use `--env-password` (like existing CLI) to implicitly require root credentials for admin operations?

##### 2. Database & User Creation Workflow
- **Original behavior**: `scripts\setup-arango.ps1` created database and user atomically
- **Proposed CLI**: Separates database and user creation into distinct commands
- **Observation**: Separation makes sense for grant/revoke operations
- **Question**: Should the `create` command support an optional flag to create/assign a user simultaneously for common use cases?

##### 3. Missing Safety & Transparency Features
- **Required**: `--dry-run` option with clear, line-by-line output showing what will be created/modified/deleted
- **Rationale**: Critical for admin operations to prevent accidental changes

##### 4. Version Information
- **Required**: Add a `version` command to display CLI and library versions
- **Implementation constraint**: Use Python's `importlib.metadata.version()` (or equivalent reflection API) to retrieve version dynamically from package metadata
- **Anti-pattern to avoid**: Do NOT hardcode `__version__` variables or duplicate version strings across multiple files

#### Your Task

Conduct a comprehensive CLI design analysis and produce actionable recommendations:

1. **Review Existing Implementation**
   - Examine the current `mcp-arangodb-async db` CLI implementation
   - Document its command structure, arguments, and user experience patterns

2. **Review Proposed Design**
   - Analyze the proposed CLI in `__reports__/multi_tenancy_analysis/04-admin_cli_roadmap_v0.md`
   - Identify all commands, sub-commands, arguments, and workflows

3. **Comparative Analysis & Design Improvements**
   - Compare existing vs. proposed CLI structures
   - Address the 4 specific concerns listed above
   - Propose concrete improvements for:
     - Command hierarchy and naming conventions
     - Authentication/authorization patterns (explicit vs. implicit admin mode)
     - Atomic vs. granular operations (database+user creation)
     - Safety features (dry-run, confirmations, output clarity)
     - Version reporting mechanism
   - Consider additional ergonomic improvements not mentioned above

4. **Deliverable**
   - Create analysis report(s) in `__reports__/multi_tenancy_analysis/cli_enhancements/`
   - Include command structure diagrams, usage examples, and rationale for recommendations
   - Provide specific implementation guidance for the design decisions

#### Constraints

- **Analytic Behavior**: Study and read thoroughly before making any codebase changes (see `cracking-shells-playbook/instructions/analytic-behavior.instructions.md`)
- **Work Ethics**: Apply rigor and perseverance (see `cracking-shells-playbook/instructions/work-ethics.instructions.md`)
- **Reporting Standards**: Follow established reporting conventions (see `cracking-shells-playbook/instructions/reporting.instructions.md`)
- **Scope**: This is an analysis and design task only—no implementation yet (see Phase 1 in `cracking-shells-playbook/instructions/code-change-phases.instructions.md`)

#### Success Criteria

- Clear, well-justified CLI design that improves upon the initial proposal
- Addresses all 4 specific concerns with concrete solutions
- Maintains consistency with existing CLI patterns where appropriate
- Provides actionable specifications ready for implementation in subsequent milestones