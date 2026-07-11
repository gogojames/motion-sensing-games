<!--
╔══════════════════════════════════════════════════════════════════════════╗
║  SYNC IMPACT REPORT                                                    ║
║                                                                        ║
║  Version Change: (template) → 1.0.0                                   ║
║                                                                        ║
║  Modified Principles:                                                  ║
║    [PRINCIPLE_1_NAME] → I. Code Quality                                ║
║    [PRINCIPLE_2_NAME] → II. Testing Standards                          ║
║    [PRINCIPLE_3_NAME] → III. User Experience Consistency               ║
║    [PRINCIPLE_4_NAME] → IV. Performance Requirements                   ║
║    [PRINCIPLE_5_NAME] → omitted (4 principles specified by user)       ║
║                                                                        ║
║  Sections Renamed:                                                     ║
║    [SECTION_2_NAME] → Technical & Operational Standards                ║
║    [SECTION_3_NAME] → Development Workflow & Quality Gates             ║
║                                                                        ║
║  Added Sections:                                                       ║
║    (all sections filled from template placeholders)                    ║
║                                                                        ║
║  Removed Sections:                                                     ║
║    None                                                                ║
║                                                                        ║
║  Templates Requiring Updates:                                          ║
║    ✅ .specify/templates/plan-template.md — no changes needed          ║
║        (Constitution Check section is generic placeholder)             ║
║    ✅ .specify/templates/spec-template.md — no changes needed          ║
║    ✅ .specify/templates/tasks-template.md — no changes needed         ║
║    ✅ .specify/templates/commands/*.md — no outdated references        ║
║                                                                        ║
║  Follow-up TODOs: None                                                 ║
╚══════════════════════════════════════════════════════════════════════════╝
-->

# Motion-Sensing Games Constitution

## Core Principles

### I. Code Quality

Code quality is a first-class deliverable, not a secondary concern. Every
contribution MUST adhere to the following non-negotiable rules:

- **Static Analysis**: All code MUST pass the project's configured linter and
  type checker with zero errors before merge. No linter-disable comments
  unless accompanied by an inline justification comment.
- **Type Safety**: MUST use the strictest feasible type-checking settings.
  `any` types are forbidden unless explicitly reviewed and justified.
- **Architecture Discipline**: Dependencies MUST flow inward (domain
  layers must not depend on infrastructure layers). Circular dependencies
  are forbidden and MUST be caught by the project's dependency checker.
- **No Dead Code**: Unused exports, parameters, variables, and
  unreachable branches MUST be removed. Dead-code analysis tools MUST
  be run as part of the CI pipeline.
- **Reviewable Diffs**: Each commit or PR MUST present a coherent,
  reviewable change. Mixing refactoring with feature work is forbidden.
  Mechanical changes (renames, formatting) MUST be in isolated commits.
- **Complexity Budget**: Functions exceeding 60 lines or a cyclomatic
  complexity of 15 MUST be justified in the PR description or refactored.

*Rationale*: Motion-sensing applications involve real-time sensor fusion,
frame processing, and hardware interaction — where a single type error or
architectural violation can cause crashes, latency spikes, or incorrect
gesture recognition. Strict quality discipline prevents these at the
source.

---

### II. Testing Standards

All code MUST be verified through a defined test strategy before merge.
The test pyramid MUST guide investment: many fast unit tests, fewer
integration tests, minimal end-to-end tests.

- **Test Coverage Baseline**: New code MUST achieve >=80% line coverage.
  Critical paths (sensor pipelines, gesture classifiers, scoring logic)
  MUST achieve >=90% coverage.
- **TDD Encouraged**: Where feasible, tests MUST be written before
  implementation (Red-Green-Refactor). At minimum, tests MUST exist and
  pass before merge.
- **Test Independence**: Each test MUST be hermetic — no shared mutable
  state, no reliance on test execution order. Tests MUST be runnable in
  isolation and in parallel.
- **Test Types**:
  - *Unit tests*: Cover pure logic, data transformations, utility functions.
  - *Integration tests*: Cover storage, networking, hardware abstraction
    layer interactions. Use real or contract-verified test doubles.
  - *E2E tests (where applicable)*: Cover critical user journeys through
    the full stack.
- **Flakiness**: Any test that intermittently fails MUST be quarantined
  immediately. A flaky test is worse than no test — it destroys trust in
  the entire suite.
- **CI Gate**: The full test suite MUST pass on every PR before merge.
  Test execution MUST be part of the CI pipeline with a strict pass/fail
  gate.

*Rationale*: Motion-sensing games depend on precise timing and sensor
interpretation. Without rigorous testing, regressions in gesture detection,
frame timing, or sensor calibration go undetected until runtime, degrading
player experience.

---

### III. User Experience Consistency

Players interact with motion-sensing games through novel input modalities
(camera, accelerometer, gyroscope). Consistency in feedback, flow, and
visual language is essential for intuitive play.

- **Interaction Patterns**: Similar actions MUST produce consistent feedback
  across all game modes. A swipe, wave, or gesture that performs action X
  in one context MUST NOT perform a conflicting action in another.
- **Visual Language**: A shared design token system (colors, typography,
  spacing, animation curves) MUST be used across all screens and games.
  No ad-hoc styling.
- **Accessibility (a11y)**: All interactive elements MUST be operable via
  keyboard/alternative input where hardware permits. Visual feedback MUST
  not rely solely on color — use icons, text, or haptics as supplements.
- **Responsiveness**: UI MUST respond to user input within 100ms
  (perceptual instant). Motion-triggered actions MUST provide visual or
  haptic confirmation within 200ms of gesture completion.
- **Onboarding**: First-time users MUST be guided through the motion
  controls with clear, visual instructions before being dropped into
  gameplay. Calibration steps MUST be obvious and forgiving.
- **Error States**: Network drops, sensor failures, and gesture
  misreads MUST surface human-readable error messages with recovery
  paths. Silent failures are forbidden.
- **Platform Consistency**: On each target platform (web, mobile,
  desktop), UI MUST conform to platform conventions for navigation,
  scrolling, gestures, and system chrome.

*Rationale*: Motion controls are inherently unfamiliar compared to
keyboard/mouse/touch. Consistent UX reduces the learning curve,
prevents player frustration, and builds trust in the motion-sensing
system.

---

### IV. Performance Requirements

Motion-sensing games are real-time interactive systems. Performance is
not an optimization target — it is a correctness requirement.

- **Frame Budget**: All rendering and game logic MUST complete within
  the target frame budget (e.g., 16ms for 60fps, 33ms for 30fps).
  Exceeding the budget in the critical path constitutes a bug.
- **Sensor Latency**: Raw sensor data (camera frames, IMU reads) MUST be
  processed and made available to game logic within a bounded latency
  budget defined per-platform. Late sensor data MUST be dropped, not
  queued.
- **No Jank**: Garbage collection pauses, layout thrashing, and
  main-thread blocking MUST be profiled and eliminated. Allocation
  hot paths MUST be pre-allocated or object-pooled.
- **Performance Budgets**: Every feature MUST define and enforce
  performance budgets before implementation:
  - Memory: Maximum heap / GPU memory per scene
  - Startup: Time from launch to first interactive frame
  - Load: Time for asset / level transitions
  - Battery: Estimated drain rate (mobile targets)
- **Profile Before Optimize**: All performance optimizations MUST be
  guided by profiling data (not intuition). Each optimization MUST
  include before/after measurements in the PR.
- **CI Performance Gate**: Performance regression tests MUST run in CI
  for critical paths. A regression >5% on key metrics MUST block merge
  unless explicitly waived.
- **Target Platform Testing**: All performance assertions MUST be
  validated on the lowest-spec target device, not just the developer's
  machine.

*Rationale*: In motion-sensing games, latency is not a smoothness issue —
it is a correctness issue. A 50ms delay in gesture recognition can mean
the difference between a hit and a miss, breaking the core gameplay loop.
Performance IS functionality.

---

## Technical & Operational Standards

### Technology Stack Requirements

- **Primary Language**: TypeScript (strict mode) for all application
  logic. JavaScript is permitted only for legacy or build-tooling code.
- **Runtime**: Node.js LTS for server/backend; modern evergreen browser
  for web targets; platform-native runtimes for mobile.
- **Motion-Sensing APIs**: Web-based targets use the W3C Sensor API,
  MediaPipe, or TensorFlow.js for camera-based pose/gesture detection.
  Native targets use platform SDKs (ARKit, CameraX, etc.).
- **Rendering**: Canvas2D / WebGL / WebGPU for web targets; platform
  native rendering pipelines for mobile. No game engines that introduce
  opaque performance characteristics unless explicitly justified.
- **Storage**: Local-first with optional cloud sync. IndexedDB for web,
  SQLite or CoreData for native.
- **CI/CD**: GitHub Actions for all CI pipelines. Performance regression
  tests run on self-hosted or metal runners for consistent timing.

### Security Requirements

- All sensor data processing MUST happen on-device. No raw frame data
  transmitted to external services without explicit user consent.
- User accounts, if implemented, MUST use OAuth 2.0 / OpenID Connect.
- No hardcoded secrets, API keys, or tokens in source code.

### Documentation Requirements

- Every public API, module, and component MUST have a documented
  purpose, interface, and usage example.
- Performance characteristics (expected latency, memory footprint) MUST
  be documented alongside sensor-processing modules.
- Architectural Decision Records (ADRs) MUST accompany any
  significant technical choice.

---

## Development Workflow & Quality Gates

### Branch Strategy

- `main` — production-ready. MUST be green at all times.
- `feat/<###>-<short-desc>` — feature branches from `main`.
- `fix/<###>-<short-desc>` — bug-fix branches.
- No direct pushes to `main`. All changes arrive via PR.

### Code Review Process

- Every PR MUST receive at least one approval from a qualified reviewer.
- Reviewer MUST verify compliance with all four constitutional principles
  before approving.
- PRs with performance implications MUST include profiling evidence.
- PRs modifying sensor/gesture pipelines MUST include test results
  showing no regression.

### Quality Gates (Pre-Merge Checklist)

1. Linter + type checker → zero errors
2. Full test suite → all passing
3. Coverage check → meets baseline
4. Performance regression check (if applicable) → within budget
5. No `any` types, no `@ts-ignore`, no `FIXME` or `TODO` without
   linked issue
6. ADR filed (if architectural decision)

### Post-Merge

- Performance benchmarks automatically compared against `main` baseline.
- Regressions flagged as GitHub issues automatically.

---

## Governance

### Supremacy

This Constitution supersedes all informal practices, local preferences,
and ad-hoc conventions. Every contribution — code, docs, config,
infrastructure — MUST comply with its principles.

### Amendment Procedure

1. **Proposal**: Open a GitHub Discussion or Issue describing the
   proposed change and its rationale.
2. **Review**: At least two maintainers MUST review and approve.
3. **Documentation**: The amendment MUST be documented as a diff to this
   Constitution, with the version updated according to semantic rules.
4. **Migration**: Breaking amendments MUST include a migration plan
   and transition period before taking effect.

### Versioning Policy

- **MAJOR** (1.x.x → 2.0.0): Principle removal, redefinition, or
  backward-incompatible governance change.
- **MINOR** (x.1.x → x.2.0): New principle or materially expanded
  guidance.
- **PATCH** (x.x.1 → x.x.2): Clarifications, wording fixes,
  non-semantic refinements.

### Compliance Review

All PRs/reviews MUST verify compliance. A "Constitution Check" section
in every implementation plan gates Phase 0 research and is re-verified
after Phase 1 design. Violations MUST be documented with justification
in the Complexity Tracking section of the plan.

---

**Version**: 1.0.0 | **Ratified**: 2026-07-11 | **Last Amended**: 2026-07-11
