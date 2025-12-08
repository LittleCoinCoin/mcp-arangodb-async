# Augment Prompts for Multi-Tenancy

## 1. Refreshing the analysis given recent development

### 1.1 Original

We are looking into adding the capability to connect to multiple ArangoDB databases from a single MCP server instance. The readme `__reports__\multi_tenancy_analysis\prompts.md` is a perfect entry point to guide you through the relevant reports.

However, a dev sprint was done since these reports were generated and we must refresh the analysis given the recent changes. The purpose of the dev sprint was to enhance the MCP with search tools capabilities in order to give the possibility to LLM-based agents to better select the right tool for the job and reduce context window pollution. This work was performed between commits `df075dbd20a84aec3bd8f6662b45620944d863eb` (first of the dev sprint) and `8c9a26bc387f408f7fc8c09af6d0eb7c8ef76cf7` (last of the dev sprint).

**Your Task**:

1. Analyze the changes performed during the dev sprint by reviewing the commit history between the two commits above.
2. Produce updated architecture_design report accordingly

- We focus on that report for now; we will likely update the roadmap later given the changes.

**Constraints**:

- Follow the same format and structure as the previous reports.
- Leverage the cracking shells playbook for guidance on report writing `cracking-shells-playbook\instructions\reporting.instructions.md` and analysis (read & study before actuation) `cracking-shells-playbook\instructions\analytic-behavior.instructions.md`.
- Follow work ethics for rigorous analysis `cracking-shells-playbook\instructions\work-ethics.instructions.md`.

### 1.2 Augmented

#### Context

This project is an MCP (Model Context Protocol) server for ArangoDB. We are evaluating multi-tenancy capabilities to allow a single MCP server instance to connect to multiple ArangoDB databases. Previous analysis reports exist in `__reports__\multi_tenancy_analysis\` but are now outdated due to a recent development sprint.

#### Development Sprint Background

A development sprint was completed between commits:

- **Start**: `df075dbd20a84aec3bd8f6662b45620944d863eb` (first commit of sprint)
- **End**: `8c9a26bc387f408f7fc8c09af6d0eb7c8ef76cf7` (last commit of sprint)

**Sprint Objective**: Enhance the MCP server with search tool capabilities to:

- Enable LLM-based agents to better select appropriate tools for specific tasks
- Reduce context window pollution by improving tool discoverability and organization

#### Your Task

1. **Analyze Sprint Changes**:
   - Review the complete commit history between `df075dbd20a84aec3bd8f6662b45620944d863eb` and `8c9a26bc387f408f7fc8c09af6d0eb7c8ef76cf7` (inclusive)
   - Identify all architectural changes, new patterns, and design decisions introduced
   - Understand how search tool capabilities were implemented and their impact on the codebase structure

2. **Update Architecture Design Report**:
   - Locate the existing architecture design report in `__reports__\multi_tenancy_analysis\`
   - Produce an updated version that reflects the current state of the codebase after the sprint
   - Focus ONLY on updating the architecture design report (roadmap updates will be handled separately later)
   - Ensure the updated report accurately represents how the new search tool capabilities affect the multi-tenancy architecture considerations

#### Mandatory Constraints

1. **Format Consistency**: Maintain the exact same format, structure, and section organization as the existing architecture design report
2. **Playbook Compliance**: Before beginning your analysis, read and internalize these playbook documents:
   - `cracking-shells-playbook\instructions\analytic-behavior.instructions.md` - Study this for analytical methodology
   - `cracking-shells-playbook\instructions\reporting.instructions.md` - Follow this for report writing standards
   - `cracking-shells-playbook\instructions\work-ethics.instructions.md` - Adhere to these work ethics throughout
3. **Rigor**: Apply thorough, evidence-based analysis; avoid speculation about untested features
4. **DRY Principle**: Avoid redundancy in documentation; reference existing content where appropriate

#### Entry Point

Start by reviewing `__reports__\multi_tenancy_analysis\prompts.md` to understand the context and structure of previous analysis work.

#### Deliverable

An updated architecture design report that:

- Reflects the current codebase state post-sprint
- Incorporates the impact of new search tool capabilities on multi-tenancy design
- Maintains consistency with the original report format
- Provides actionable architectural insights for implementing multi-database support

## 2. Iterating on the architecture design report refresh

### 2.1 Original

The depth of your analysis is very commendable. But stakeholders are confused about the integration points and have some feedback that will likely require an iteration on the report:

**About Enhanced SessionContextManager (Section 2.2):**

- The stakeholders were confused for a considerable amount of time because the vocabulary used in the previous dev sprint was also "context." But in fact, the previous "context" was about workflow/tools context and the new "context" is about database context. We must make that clearer in the report and that will involve renaming classes or variables to differentiate `tools_workflow_context` (or something similar) and what will be introduced in this dev sprint `database_context` (or something similar).

**About the question Should tool discovery be database-specific or server-wide? (Section 6.5):**

- If the answer is "server-wide" then why are you suggesting to implement:

```
2. Create `session_context.py` with session management
   - Add database context management (from v1)
   - Add workflow context management (NEW in v2)
   - Add workflow stage management (NEW in v2)
   - Add tool usage tracking (NEW in v2)
```

in phase 1?

- Essentially the integration of database context management (which you are calling session management, correct?) with what developpers of the previous dev sprint called workflow context management is unclear at this point.

**About New MCP Tools Section (Section 2.9):**:

- These tools are not new, correct? They are the ones introduced in the previous dev sprint but what you mean by "new" is that you need to update them. Is that correct? The way you are talking about them currently makes it sound like you want to implement them but they are already in `mcp_arangodb_async\handlers.py`.

Overall, it seems you understood very well what the previous dev sprint was about. But the overwhelming length and details provided in the report are making it hard for stakeholders to understand the key integration points. Some of your statements seems slightly contradictory and stakeholders cannot be sure at this point that you are not going to wrongly integrate.

**Your Task**: Write a report dedicated to the integration of this new multi-tenancy feature with the previous dev sprint. Given that the multi-tenancy feature will:

1. introduce new tools

- so where do they fit in the new effort of agent-friendly tool discorvery workflow context switching and so on.
- be careful to not invent fantasy usage cases that would suddenly require adding many workflows of tool categories for the tool search

2. introduce multi-database support

- how can the tool usage and workflow context be sure to match the right database and not mess up the queries?
- how can we leverage the effort on tool search and workflow context from the previous dev sprint?

3. both points 1 and 2 might disturb the user-facing documentation `docs\user-guide\mcp-design-patterns.md`

**Constraints**:

- Leverage the cracking shells playbook for guidance on report writing `cracking-shells-playbook\instructions\reporting.instructions.md` and analysis (read & study before actuation) `cracking-shells-playbook\instructions\analytic-behavior.instructions.md`.
  - Your reports are very good but too long on average. Even for yourself, strive to extract the essence.
  - Stakeholders know that you can produce good code; the reports are there for the design of the architecture, not to write and review the code.
- Follow work ethics for rigorous analysis `cracking-shells-playbook\instructions\work-ethics.instructions.md`.

### 2.2 Augmented

#### Context

You previously created an updated architecture design report (v2) for multi-tenancy integration. Stakeholders have reviewed it and identified critical clarity issues around integration points with the v0.4.0 sprint (Design Patterns feature).

#### Stakeholder Feedback

##### Issue 1: Terminology Collision - "Context" Overload

**Problem**: The term "context" is used ambiguously for two distinct concepts:

- **Workflow/Tool Context** (v0.4.0 sprint): Which workflow stage is active? Which tools are loaded? What's the agent's current task?
- **Database Context** (multi-tenancy feature): Which database is the focus of operations?

**Required Action**: Establish clear, distinct terminology throughout the report. Suggested naming:

- `workflow_context` or `tool_discovery_context` for v0.4.0 design pattern state
- `database_context` or `focused_database` for multi-tenancy database selection

##### Issue 2: Contradictory Design - Tool Discovery Scope vs. Session Management

**Problem**: Section 6.5 concludes tool discovery should be "server-wide" (not database-specific), yet Phase 1 implementation proposes integrating database context management with workflow context management in a unified `session_context.py`. This appears contradictory.

**Required Clarification**:

- If tool discovery is server-wide, why does `session_context.py` need to manage both database context AND workflow context?
- What is the relationship between "session management" and "database context management"?
- How do these two context types interact without interfering with each other?

##### Issue 3: Misleading "New" Label for Existing Tools

**Problem**: Section 2.9 labels design pattern tools as "New MCP Tools" when they already exist in `mcp_arangodb_async/handlers.py` from the v0.4.0 sprint.

**Required Clarification**:

- Are these tools being created (new) or modified (updated)?
- If modified, what specific changes are needed for multi-tenancy compatibility?

##### Issue 4: Report Length Obscures Key Integration Points

**Problem**: The 1000+ line report contains excellent analysis but buries critical integration decisions. Stakeholders cannot quickly identify:

- Where exactly do the two features intersect?
- What are the 3-5 key integration risks?
- What design decisions must be made before implementation?

#### Your Task

Create a **focused integration analysis report** (target: 300-500 lines) that addresses stakeholder concerns. This is NOT a comprehensive architecture document—it's a targeted integration design.

##### Required Report Sections

###### 1. Terminology Clarification (50-75 lines)

- Define distinct terms for workflow context vs. database context
- Provide a comparison table showing the differences
- Propose specific variable/class naming conventions to eliminate ambiguity

###### 2. Integration Architecture (100-150 lines)

Answer these specific questions:

- **Q1**: How do workflow context (v0.4.0) and database context (multi-tenancy) coexist in the same session?
- **Q2**: When an agent switches workflow stages (e.g., "data_exploration" → "data_modification"), does this affect database context? Why or why not?
- **Q3**: When an agent switches focused databases, does this affect workflow context? Why or why not?
- **Q4**: Where is the single source of truth for each context type stored?
- **Q5**: How does `call_tool()` in `handlers.py` determine which database to use when both contexts are active?

###### 3. Multi-Tenancy Tools Integration (75-100 lines)

For the 6 new multi-tenancy tools (set_focused_database, list_databases, etc.):

- **Tool Discovery**: Which workflow category do they belong to? (e.g., "database_management", "configuration", etc.)
- **Workflow Impact**: Do they trigger workflow stage changes? If yes, which stages?
- **Existing Tools**: Do any existing design pattern tools in `handlers.py` need modification? List specific tools and required changes.
- **Fantasy Check**: Validate that proposed tool categories align with EXISTING workflow categories in the codebase—do NOT invent new categories unless absolutely necessary.

###### 4. Database Safety Mechanisms (50-75 lines)

- **Problem Statement**: How do we prevent an agent from executing a query intended for Database A against Database B when workflow context switches occur?
- **Proposed Solution**: Describe the mechanism (e.g., session-scoped database binding, per-tool database validation, etc.)
- **Failure Modes**: What happens if database context is not set when a database operation tool is called?

###### 5. Documentation Impact Analysis (25-50 lines)

Review `docs/user-guide/mcp-design-patterns.md`:

- **Section 1**: Which sections need updates to reflect multi-database scenarios?
- **Section 2**: Are new usage examples needed? If yes, provide 1-2 concrete example titles (not full examples).
- **Section 3**: Do existing workflow examples remain valid with multi-tenancy, or do they need database context annotations?

###### 6. Implementation Risks & Decisions (50-75 lines)

- List 3-5 key integration risks (e.g., "Workflow context reset might clear database context")
- For each risk, provide a mitigation strategy
- Identify any design decisions that must be made before coding begins

##### Constraints

1. **Brevity**: Target 300-500 lines total. Stakeholders need clarity, not comprehensiveness.
2. **Evidence-Based**: Reference actual code locations (file:line) from the current codebase—no speculation about untested features.
3. **Playbook Compliance**:
   - Study `cracking-shells-playbook/instructions/analytic-behavior.instructions.md` for analytical rigor
   - Study `cracking-shells-playbook/instructions/reporting.instructions.md` for concise reporting style
   - Follow `cracking-shells-playbook/instructions/work-ethics.instructions.md` for thoroughness
4. **No Code Samples**: Stakeholders trust your coding ability. Use pseudocode or descriptions instead of full code blocks.
5. **Actionable**: Every section should answer "What decision must be made?" or "What must be built?"

##### Deliverable

A new report file: `__reports__/multi_tenancy_analysis/02-integration_design.md`

This report should enable stakeholders to:

1. Understand exactly how workflow context and database context interact
2. Approve the integration architecture before implementation begins
3. Identify any blocking design decisions that need resolution

## 3. Iterating on the integration report

### 3.1 Original

This is very informative. Let's iterate on that. Here are the stakeholder feedback points:

- There are currently no tools in the new multi-tenancy feature which directly switch the Sessions you are mentioning, correct? So who/what is responsible for switching the sessions?

- The link session/active_workflow/focused_database is still confusing from a use case perspective. Typically, we can expect that building/creating documents/collections in one database will depend on the data from another (or multiple) databases. In that case how to do you see the tri-partite (session/active_workflow/focused_database) working together?
  - After working out these use cases, do you need to revise the proposed integration architecture?

- the existing `arango_switch_context` will need to be renamed to `arango_switch_workflow_context` to avoid ambiguity. Check other tool names as well.

- If we are different sessions, stakeholders already anticipate people will want to be able to work on different sessions in parallel.
  - How will you support that use case? which concurrency model is better to choose? Is the choice of the concurrency model influenced by the existing codebase? Influenced by something else in the current integration study context?

**Your Task**: Write a new version `__reports__/multi_tenancy_analysis/02-integration_design_v1.md` that addresses the stakeholder feedback points.

**Note**: You forgot the version suffix `_v0` in the file name `02-integration_design.md`. Add it.

### 3.2 Augmented

#### Context

You previously created an integration design report (`__reports__/multi_tenancy_analysis/02-integration_design.md`) analyzing how the v0.4.0 Design Patterns feature integrates with the proposed multi-tenancy feature. Stakeholders have reviewed it and identified critical gaps in the analysis that must be addressed before implementation can proceed.

#### Stakeholder Feedback - Critical Questions

##### Feedback 1: Session Management Responsibility

**Question**: The report mentions "sessions" as the isolation boundary for both workflow context and database context. However, there are currently no tools in the proposed multi-tenancy feature that directly create, switch, or manage these sessions.

**Required Analysis**:

- Who or what is responsible for creating sessions? (MCP protocol? Server initialization? Client requests?)
- Who or what is responsible for switching between sessions? (Agent tools? Client application? Server logic?)
- How does the MCP protocol's native session concept map to your proposed SessionState class?
- Provide evidence from the MCP specification or existing codebase showing how sessions are currently managed

##### Feedback 2: Cross-Database Workflow Use Cases

**Question**: The report states that `active_workflow` and `focused_database` are "orthogonal" (independent), but this doesn't align with real-world use cases. In practice, agents often need to:

- Read data from Database A (e.g., production analytics)
- Transform/analyze that data (workflow stage: data_exploration)
- Write results to Database B (e.g., reporting database)

**Required Analysis**:

- Provide 2-3 concrete use case scenarios showing how the tri-partite relationship (session/active_workflow/focused_database) works when an agent needs to access MULTIPLE databases within a SINGLE workflow stage
- For each use case, show the sequence of tool calls and state changes
- Does the current "one focused database per session" design support these use cases? If not, what architectural changes are needed?
- After analyzing these use cases, determine if the proposed integration architecture in Section 2 needs revision. If yes, provide the revised architecture.

##### Feedback 3: Tool Naming Audit for Ambiguity

**Action Required**: The existing tool `arango_switch_context` (from v0.4.0 Design Patterns feature) must be renamed to `arango_switch_workflow_context` to avoid ambiguity with database context switching.

**Required Analysis**:

- Audit ALL existing tool names in `mcp_arangodb_async/handlers.py` that contain the word "context", "switch", "set", "activate", or similar state-changing verbs
- For each tool, determine if the name is ambiguous when multi-tenancy is added
- Provide a renaming table with columns: [Current Name | Ambiguity Issue | Proposed New Name | Justification]
- Identify any tools where renaming would break backward compatibility with existing agent workflows

##### Feedback 4: Parallel Session Concurrency Model

**Question**: If different sessions can exist simultaneously (e.g., Session A working on Database X, Session B working on Database Y), stakeholders anticipate that agents will want to work on multiple sessions in parallel (concurrent operations).

**Required Analysis**:

- **Concurrency Support**: How will the proposed architecture support parallel session operations? (e.g., Can an agent execute a long-running query in Session A while simultaneously exploring schema in Session B?)
- **Concurrency Model Selection**: Which concurrency model is appropriate? Options include:
  - Thread-based concurrency (threading module)
  - Async/await concurrency (asyncio - already used in codebase)
  - Process-based concurrency (multiprocessing)
  - No concurrency (sequential only)
- **Existing Codebase Constraints**: Analyze `mcp_arangodb_async/entry.py` and `mcp_arangodb_async/handlers.py` to determine:
  - Is the codebase already async? (Check for `async def`, `await` keywords)
  - Are there any global state variables that would create race conditions in concurrent scenarios?
  - Does the ArangoDB client library (`python-arango`) support concurrent operations?
- **Integration Context Constraints**: Are there MCP protocol limitations on concurrent tool execution?
- **Recommendation**: Provide a specific concurrency model recommendation with justification based on the above analysis

#### Your Tasks

##### Task 1: File Versioning Correction

**Action**: Rename the existing report to include the `_v0` version suffix:

- **Current**: `__reports__/multi_tenancy_analysis/02-integration_design.md`
- **New**: `__reports__/multi_tenancy_analysis/02-integration_design_v0.md`

##### Task 2: Create Updated Integration Design Report

**Action**: Create a new version `__reports__/multi_tenancy_analysis/02-integration_design_v1.md` that:

1. **Addresses all 4 stakeholder feedback points** with evidence-based analysis
2. **Maintains the same report structure** as v0 (6 sections) but updates content based on feedback
3. **Adds new subsections** where needed to address feedback (e.g., "Cross-Database Workflow Scenarios" in Section 2, "Concurrency Model Analysis" in Section 6)
4. **Revises the integration architecture** (Section 2) if the cross-database use case analysis reveals design flaws
5. **Updates implementation risks** (Section 6) to include concurrency-related risks if parallel sessions are supported

##### Task 3: Update README

**Action**: Update `__reports__/multi_tenancy_analysis/README.md` to:

- Mark `02-integration_design_v0.md` as ARCHIVED
- Mark `02-integration_design_v1.md` as CURRENT
- Add a brief changelog entry explaining what changed from v0 to v1

#### Constraints

1. **Evidence-Based**: All claims must reference actual code (file:line), MCP specification sections, or ArangoDB client library documentation
2. **Brevity**: Target 400-600 lines (v0 was 525 lines, so similar length is acceptable)
3. **Playbook Compliance**: Follow the same analytical rigor standards from the playbook documents
4. **No Speculation**: If you cannot find evidence for a claim (e.g., MCP protocol concurrency support), explicitly state "Evidence not found - requires further investigation" and mark it as a blocking question
5. **Actionable**: Each feedback point must result in either:
   - A concrete architectural decision
   - A revised design
   - A blocking question that requires stakeholder input

#### Deliverables

1. Renamed file: `02-integration_design_v0.md`
2. New file: `02-integration_design_v1.md` (addresses all 4 feedback points)
3. Updated file: `README.md` (version tracking and changelog)

#### Success Criteria

Stakeholders should be able to:

1. Understand exactly how sessions are created and managed (Feedback 1)
2. Visualize how cross-database workflows operate with concrete examples (Feedback 2)
3. Approve the tool renaming plan (Feedback 3)
4. Approve the concurrency model selection (Feedback 4)
5. Proceed to implementation OR identify blocking questions that need resolution

## 4. Updating the roadmap

### 4.1 Original

Let's move on to updating the roadmap accordingly.

**Your task**: Write an updated version `__reports__\multi_tenancy_analysis\02-implementation_roadmap_v2.md`, adapting the content to the new `__reports__\multi_tenancy_analysis\01-architecture_design_v3.md`

**Constraints**:

- Follow the org's roadmap standards `cracking-shells-playbook\instructions\roadmap-generation.instructions.md`.
- Leverage the cracking shells playbook for guidance on report writing `cracking-shells-playbook\instructions\reporting.instructions.md` and analysis (read & study before actuation) `cracking-shells-playbook\instructions\analytic-behavior.instructions.md`.
  - Your reports are very good but too long on average. Even for yourself, strive to extract the essence.
  - Stakeholders know that you can produce good code; the reports are there for the design of the architecture, not to write and review the code.
- Follow work ethics for rigorous analysis `cracking-shells-playbook\instructions\work-ethics.instructions.md`.

### 4.2 Augmented

#### Context

We have completed the v3 architecture design document (`__reports__/multi_tenancy_analysis/01-architecture_design_v3.md`) which finalizes the multi-tenancy feature design for the v0.5.0 release. The existing implementation roadmap (`__reports__/multi_tenancy_analysis/02-implementation_roadmap_v1.md`) is now outdated and needs to be updated to reflect the v3 architecture decisions.

#### Your Task

Create an updated implementation roadmap: `__reports__/multi_tenancy_analysis/02-implementation_roadmap_v2.md`

The roadmap must:

1. **Align with v3 Architecture**: Reflect all decisions from `01-architecture_design_v3.md`, including:
   - Terminology changes (SessionState, active_workflow, tool_lifecycle_stage)
   - 3 tool renamings (arango_switch_workflow, arango_get_active_workflow, arango_list_workflows)
   - Per-tool database override for 35 data operation tools
   - 6 new multi-tenancy tools
   - CLI tool with 5 subcommands
   - 4-week timeline (5 phases)

2. **Follow Organizational Standards**: Study and apply `cracking-shells-playbook/instructions/roadmap-generation.instructions.md` for roadmap structure and format

3. **Be Concise and Actionable**:
   - Target 400-600 lines (extract the essence, avoid verbosity)
   - Focus on WHAT needs to be built and WHEN, not HOW to code it
   - Stakeholders trust your coding ability—the roadmap is for planning and tracking, not code review
   - Include only essential details: deliverables, dependencies, timeline, risks
   - Actionable content at the task level should reflect `cracking-shells-playbook\instructions\code-change-phases.instructions.md`

4. **Maintain Consistency**:
   - Use the same phase structure as v3 architecture (5 phases, 4 weeks)
   - Reference specific file paths and component names from v3 architecture
   - Ensure timeline and effort estimates match v3 architecture

#### Mandatory Playbook Compliance

Before writing, study these playbooks:

- `cracking-shells-playbook/instructions/roadmap-generation.instructions.md` - Roadmap structure and standards
- `cracking-shells-playbook/instructions/reporting.instructions.md` - Concise reporting style
- `cracking-shells-playbook/instructions/analytic-behavior.instructions.md` - Analytical rigor
- `cracking-shells-playbook/instructions/work-ethics.instructions.md` - Work ethics and thoroughness

#### Deliverable

A focused, actionable implementation roadmap (400-600 lines) that enables:

1. Development team to execute the 5 implementation phases
2. Stakeholders to track progress and identify blockers
3. Project managers to allocate resources and manage timeline

#### Success Criteria

- ✅ Aligns with all v3 architecture decisions
- ✅ Follows organizational roadmap standards
- ✅ Concise (400-600 lines, no code samples)
- ✅ Actionable (clear deliverables, dependencies, timeline)
- ✅ Trackable (milestones, success criteria, risks)

## 5. Iterating over the roadmap

### 5.1 Original

Stakeholder feedbacks and adjustments:

- As deferred feature, add the server-side multi threading within one session ID such that multiple queries can be run.
- Success gates for documentation should explicitely mention that:
  - documentation respects style guide
  - documentation integration analysis step to make sure the docs do not grow uncontrolled
- Be a bit more explicit about testing tasks:
  - mention the 90% coverage paths for all new features to make sure that the final 90% are reached directly
  - tests design should respect existing style
  - Make sure to instruct/identify to test ONLY what we implement in the milestone/task
  - Do not test things that are not the responsibility of this milestone/task. Do not test fantasy use cases.
- For each task, include:
  - strategic **context** section (1-4 bullet points)
    - this cites relevant design document sections
  - **rationale** section (1-2 sentences)

### 5.2 Augmented

#### Context

You previously created the v2 implementation roadmap (`__reports__/multi_tenancy_analysis/02-implementation_roadmap_v2.md`) for the multi-tenancy feature. Stakeholders have reviewed it and provided feedback requiring specific enhancements to task definitions, success criteria, and deferred features.

#### Your Task

Update the implementation roadmap to version v3: `__reports__/multi_tenancy_analysis/02-implementation_roadmap_v2.md` → `__reports__/multi_tenancy_analysis/02-implementation_roadmap_v3.md`

Apply the following stakeholder-requested changes:

#### Change 1: Add Deferred Feature

**Location**: Section "Deferred Features (v0.6.0+)"

**Action**: Add a new deferred feature:

- **Feature Name**: "Server-Side Multi-Threading Within Single Session"
- **Description**: Enable concurrent query execution within a single session ID (currently sequential)
- **Rationale**: Allows a single agent to execute multiple long-running queries in parallel without blocking
- **Technical Considerations**: Requires thread-safe session state management and ArangoDB connection pooling per session

#### Change 2: Enhance Documentation Success Gates

**Location**: All milestones with documentation deliverables (Milestones 2.1, 4.2, 5.1)

**Action**: For each documentation success gate, add two explicit requirements:

1. **Style Guide Compliance**: "Documentation follows the project style guide (tone, formatting, structure)"
2. **Integration Analysis**: "Documentation integration analysis completed to prevent uncontrolled growth (identify redundancies, consolidation opportunities, and ensure DRY principle)"

#### Change 3: Enhance Testing Task Specifications

**Location**: All tasks with testing deliverables (Tasks 1.1.1, 1.1.2, 1.1.3, 1.2.1, 1.2.2, 2.1.2, 3.1.1, 3.1.2, 3.1.3, 4.1.2, 4.2.1, 4.2.2, 5.1.1, 5.1.2)

**Action**: For each testing deliverable, add these explicit requirements:

1. **Coverage Target**: "Achieve 90% code coverage for all new code introduced in this task (not cumulative project coverage)"
2. **Style Compliance**: "Tests follow existing test style and conventions (naming, structure, assertions)"
3. **Scope Discipline**: "Test ONLY functionality implemented in this specific task/milestone—do not test upstream dependencies, downstream consumers, or speculative use cases outside this task's responsibility"

#### Change 4: Add Context and Rationale to Each Task

**Location**: All 23 tasks across all phases

**Action**: For each task, add two new subsections immediately after the task title:

##### **Context** (1-4 bullet points)

- Cite specific sections from `01-architecture_design_v3.md` that inform this task
- Reference relevant design decisions or architectural patterns
- Identify dependencies on previous tasks or external components
- Note any constraints or assumptions

##### **Rationale** (1-2 sentences)

- Explain WHY this task is necessary for the overall feature
- Describe the specific problem this task solves or value it provides

**Example Format**:

```
#### Task 1.1.1: SessionState Component

**Context**:
- Architecture Design v3, Section 2.2: SessionState component specification
- Replaces global state variables (_active_context, _current_stage, _tool_usage_stats) with per-session isolation
- Foundation for all subsequent multi-tenancy features (database context, workflow state)

**Rationale**: SessionState provides the isolation boundary for multi-database workflows, ensuring that different agents (sessions) can work with different databases and workflow stages without interference.

**Goal**: Implement the SessionState class...
[rest of task definition continues]
```

#### Constraints

1. **Maintain Structure**: Keep the same 5-phase, 7-milestone, 23-task structure
2. **Preserve Timeline**: 4 weeks total (no changes to effort estimates)
3. **Consistency**: Ensure all 23 tasks receive Context and Rationale sections
4. **Brevity**: Target 500-700 lines (increased from v2's 473 lines due to added sections)
5. **Playbook Compliance**: Continue following roadmap generation standards

#### Deliverables

1. **New File**: `__reports__/multi_tenancy_analysis/02-implementation_roadmap_v3.md`
2. **Updated README**: Mark v3 as CURRENT, v2 as ARCHIVED, add changelog entry

#### Success Criteria

- ✅ All 4 stakeholder changes applied consistently across the document
- ✅ All 23 tasks have Context (1-4 bullets) and Rationale (1-2 sentences)
- ✅ Deferred features section includes server-side multi-threading
- ✅ Documentation success gates explicitly mention style guide compliance and integration analysis
- ✅ Testing specifications explicitly mention 90% coverage, style compliance, and scope discipline
- ✅ Document length: 500-700 lines
