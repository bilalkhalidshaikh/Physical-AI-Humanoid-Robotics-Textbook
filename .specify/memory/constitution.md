<!--
  === SYNC IMPACT REPORT ===
  Version change: 0.0.0 → 1.0.0 (MAJOR - initial constitution creation)

  Modified principles: N/A (initial creation)
  Added sections:
    - Core Principles (3 principles as specified by user)
    - Technology Stack (project-specific)
    - Module Architecture (4 modules)
    - Governance
  Removed sections: N/A (initial creation)

  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ (compatible - no changes needed)
    - .specify/templates/spec-template.md ✅ (compatible - no changes needed)
    - .specify/templates/tasks-template.md ✅ (compatible - no changes needed)

  Follow-up TODOs: None
-->

# Physical AI & Humanoid Robotics Textbook Constitution

## Core Principles

### I. Spec-Driven Development

All features, chapters, and components MUST begin with a formal specification before
implementation. This ensures traceability, clarity, and alignment across the documentation
and chatbot components.

**Non-negotiable rules:**
- Every chapter, module, or feature MUST have a corresponding spec.md before development
- Specifications MUST include acceptance criteria and success metrics
- Changes to existing content MUST first update the specification
- No code or content shall be merged without spec approval

**Rationale:** Spec-driven development ensures that the complex interplay between robotics
concepts, simulation environments, and AI systems is properly planned and documented before
implementation, reducing rework and maintaining consistency across the textbook.

### II. Physical-First Design

All explanations, examples, and implementations MUST prioritize physical world applicability
and real-robot behavior over pure simulation or theoretical constructs.

**Non-negotiable rules:**
- Examples MUST demonstrate real-world physical constraints (torque limits, sensor noise,
  latency)
- Simulation content MUST include reality gap considerations and sim-to-real transfer notes
- Code samples MUST be tested or validated against physical robot behaviors where applicable
- Safety considerations for physical robots MUST be explicitly documented

**Rationale:** A Physical AI textbook loses value if it only works in simulation. Readers
must understand how concepts translate to actual humanoid robots with real-world physics.

### III. Content Accuracy

All technical content MUST be factually accurate, up-to-date with current robotics research,
and properly cited. Misleading or outdated information is unacceptable.

**Non-negotiable rules:**
- Technical claims MUST be verifiable through documentation, papers, or reproducible code
- Version-specific information MUST clearly state the version (e.g., ROS 2 Humble, Isaac Sim
  2023.1)
- Deprecated APIs or methods MUST be marked and alternatives provided
- Mathematical formulations MUST be correct and consistent with standard robotics notation
- Code examples MUST be tested and working with specified versions

**Rationale:** Students and practitioners rely on this textbook for learning. Inaccurate
content can lead to safety issues in physical robot applications and erode trust in the
material.

## Technology Stack

The project employs the following technology stack. All implementations MUST use these
technologies unless explicitly justified and approved.

| Layer | Technology | Purpose |
|-------|------------|---------|
| Documentation | Docusaurus 3 | Static site generation for textbook |
| Hosting | GitHub Pages | Public deployment and versioning |
| Robotics Middleware | ROS 2 | Robot communication and control |
| Physics Simulation | Gazebo | Digital twin and simulation |
| AI/ML Platform | NVIDIA Isaac Sim | AI-robot brain training |
| Language Processing | Python | Primary implementation language |
| Voice/LLM | Whisper, LLMs | Vision-Language-Action models |

**Stack constraints:**
- Python version MUST be 3.10+ for ROS 2 compatibility
- ROS 2 distribution MUST be Humble or newer
- Isaac Sim content MUST specify compatible NVIDIA driver versions
- Docusaurus plugins MUST be compatible with version 3.x

## Module Architecture

The textbook is organized into four core modules. Each module MUST maintain clear boundaries
and well-defined interfaces.

### Module 1: Robotic Nervous System (ROS 2)

**Scope:** Robot communication, sensor integration, actuator control, and middleware patterns
using ROS 2.

**Key topics:**
- Node architecture and lifecycle management
- Topic/Service/Action communication patterns
- Sensor drivers and data processing
- Real-time control considerations

### Module 2: Digital Twin (Gazebo)

**Scope:** Physics simulation, environment modeling, and sensor simulation for testing and
validation.

**Key topics:**
- URDF/SDF robot modeling
- Physics engine configuration
- Sensor plugins and noise models
- World and environment design

### Module 3: AI-Robot Brain (Isaac Sim)

**Scope:** AI training environments, reinforcement learning, and neural network deployment
for robot intelligence.

**Key topics:**
- Domain randomization for sim-to-real
- Reinforcement learning pipelines
- Motion policy training
- Perception model training

### Module 4: Vision-Language-Action (VLA)

**Scope:** Multimodal AI systems combining vision, language understanding, and action
generation for intelligent robot behavior.

**Key topics:**
- Speech recognition integration (Whisper)
- Large Language Model reasoning
- Vision-language grounding
- Action generation from natural language commands

## Governance

### Amendment Procedure

1. Propose amendment via spec document in `specs/constitution-amendment/`
2. Obtain stakeholder review (minimum 1 reviewer)
3. Document rationale and impact analysis
4. Update constitution.md with new version
5. Propagate changes to dependent templates
6. Create PHR documenting the amendment

### Versioning Policy

The constitution follows semantic versioning:
- **MAJOR:** Backward-incompatible changes to core principles or governance
- **MINOR:** New principles, sections, or significant clarifications added
- **PATCH:** Typo fixes, minor wording improvements, non-semantic changes

### Compliance Review

- All PRs MUST be checked against constitution principles before merge
- Module content MUST align with specified technology stack
- Complexity additions MUST be justified against simplicity goals
- Annual review of constitution for relevance to current robotics landscape

### Development Guidance

For runtime development guidance and agent-specific instructions, refer to `CLAUDE.md` at
the repository root.

**Version**: 1.0.0 | **Ratified**: 2025-12-14 | **Last Amended**: 2025-12-14
