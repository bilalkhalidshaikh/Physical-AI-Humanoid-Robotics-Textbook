# Feature Specification: Book Master Plan

**Feature Branch**: `001-book-master-plan`
**Created**: 2025-12-14
**Status**: Draft
**Input**: User description: "Create the Book Master Plan based on the constitution. Generate the 'docs' folder structure for Docusaurus. Create a 'docs/intro.md' landing page. Create subfolders for each of the 4 modules: docs/module-1-ros2, docs/module-2-digital-twin, docs/module-3-brain, docs/module-4-vla"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navigate Textbook Landing Page (Priority: P1)

A reader visits the Physical AI & Humanoid Robotics textbook website and sees a clear
introduction explaining what the book covers, its learning objectives, prerequisites, and
how to navigate the four core modules.

**Why this priority**: The landing page is the entry point for all readers. Without a clear
introduction, users cannot understand the scope of the textbook or navigate to relevant
content.

**Independent Test**: Can be fully tested by visiting the deployed site root URL and
verifying all introductory content is visible, readable, and contains navigation links to
all four modules.

**Acceptance Scenarios**:

1. **Given** a reader visits the textbook homepage, **When** the page loads, **Then** they
   see a welcome message, book overview, learning objectives, and prerequisite information.
2. **Given** a reader is on the landing page, **When** they look for module navigation,
   **Then** they see clearly labeled links to all four modules (ROS 2, Digital Twin, Brain,
   VLA).
3. **Given** a reader wants to understand the book structure, **When** they read the intro,
   **Then** they understand the relationship between the four modules and recommended
   learning path.

---

### User Story 2 - Access Module 1: Robotic Nervous System (ROS 2) (Priority: P2)

A reader wants to learn about ROS 2 as the communication backbone for humanoid robots.
They navigate to Module 1 and find an organized chapter structure covering nodes, topics,
services, and real-time control.

**Why this priority**: ROS 2 is the foundational middleware that all other modules build
upon. Understanding ROS 2 is prerequisite for Digital Twin and AI integration.

**Independent Test**: Can be tested by navigating to module-1-ros2 folder and verifying
the folder structure exists with placeholder index file.

**Acceptance Scenarios**:

1. **Given** a reader clicks on Module 1 from the landing page, **When** the module page
   loads, **Then** they see an overview of ROS 2 topics covered in this module.
2. **Given** the module folder exists, **When** content authors add chapters, **Then** the
   chapters appear in the correct navigation hierarchy.

---

### User Story 3 - Access Module 2: Digital Twin (Gazebo) (Priority: P2)

A reader wants to learn about creating digital twins of humanoid robots using Gazebo for
simulation and testing. They navigate to Module 2 and find content on URDF modeling,
physics simulation, and sensor plugins.

**Why this priority**: Digital Twin simulation is essential for safe robot development
before deploying to physical hardware, directly supporting the Physical-First principle.

**Independent Test**: Can be tested by navigating to module-2-digital-twin folder and
verifying the folder structure exists with placeholder index file.

**Acceptance Scenarios**:

1. **Given** a reader clicks on Module 2 from the landing page, **When** the module page
   loads, **Then** they see an overview of Digital Twin/Gazebo topics covered.
2. **Given** the module folder exists, **When** content authors add chapters, **Then** the
   chapters integrate properly with the Docusaurus navigation.

---

### User Story 4 - Access Module 3: AI-Robot Brain (Isaac Sim) (Priority: P2)

A reader wants to learn about training AI policies for robot intelligence using NVIDIA
Isaac Sim. They navigate to Module 3 and find content on reinforcement learning, domain
randomization, and sim-to-real transfer.

**Why this priority**: The AI-Robot Brain is the intelligence layer that enables autonomous
behavior, building on the ROS 2 and simulation foundations.

**Independent Test**: Can be tested by navigating to module-3-brain folder and verifying
the folder structure exists with placeholder index file.

**Acceptance Scenarios**:

1. **Given** a reader clicks on Module 3 from the landing page, **When** the module page
   loads, **Then** they see an overview of Isaac Sim and AI training topics.
2. **Given** the module folder exists, **When** content authors add chapters, **Then** the
   chapters appear in correct order with proper navigation.

---

### User Story 5 - Access Module 4: Vision-Language-Action (VLA) (Priority: P2)

A reader wants to learn about multimodal AI systems that combine vision, language, and
action for intelligent robot behavior. They navigate to Module 4 and find content on
Whisper integration, LLM reasoning, and action generation.

**Why this priority**: VLA represents the cutting-edge of humanoid robot intelligence,
enabling natural human-robot interaction through language and vision.

**Independent Test**: Can be tested by navigating to module-4-vla folder and verifying
the folder structure exists with placeholder index file.

**Acceptance Scenarios**:

1. **Given** a reader clicks on Module 4 from the landing page, **When** the module page
   loads, **Then** they see an overview of VLA topics including speech and LLM integration.
2. **Given** the module folder exists, **When** content authors add chapters, **Then** the
   chapters integrate with the overall book navigation structure.

---

### Edge Cases

- What happens when a reader accesses a module that has no content yet?
  - Display a "Coming Soon" placeholder with expected topics and timeline.
- How does the system handle broken internal links between modules?
  - Docusaurus build process should fail on broken links, preventing deployment.
- What happens if a reader accesses the site before initial deployment?
  - GitHub Pages returns 404; DNS should only be configured after first deployment.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a `docs/intro.md` file that serves as the textbook
  landing page with book overview, learning objectives, and module navigation.
- **FR-002**: System MUST create `docs/module-1-ros2/` folder for ROS 2 content with an
  index file placeholder.
- **FR-003**: System MUST create `docs/module-2-digital-twin/` folder for Gazebo/Digital
  Twin content with an index file placeholder.
- **FR-004**: System MUST create `docs/module-3-brain/` folder for Isaac Sim/AI content
  with an index file placeholder.
- **FR-005**: System MUST create `docs/module-4-vla/` folder for Vision-Language-Action
  content with an index file placeholder.
- **FR-006**: Each module folder MUST contain a `_category_.json` file for Docusaurus
  sidebar configuration specifying module label and position.
- **FR-007**: The landing page MUST include links to all four modules that work when
  module content is added.
- **FR-008**: The folder structure MUST be compatible with Docusaurus 3.x conventions
  for automatic sidebar generation.
- **FR-009**: All markdown files MUST include proper frontmatter with title and sidebar
  position metadata.

### Key Entities

- **Module**: A major section of the textbook covering a specific robotics domain (ROS 2,
  Digital Twin, AI Brain, VLA). Contains multiple chapters organized by topic.
- **Chapter**: A single markdown file within a module covering a specific topic. Includes
  frontmatter, content sections, code examples, and exercises.
- **Landing Page**: The intro.md file serving as the book's homepage and navigation hub.

## Assumptions

- Docusaurus 3.x will be initialized in a separate setup task (not part of this spec).
- The docs folder follows Docusaurus conventions where `docs/intro.md` becomes the root
  documentation page.
- Module folders use `_category_.json` for sidebar grouping as per Docusaurus 3 standards.
- Content will be added incrementally after the folder structure is established.
- The project uses the default Docusaurus theme without custom modifications initially.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Readers can navigate from the landing page to any of the four modules in
  two clicks or fewer.
- **SC-002**: The folder structure supports adding new chapters without modifying
  configuration files (automatic sidebar generation).
- **SC-003**: 100% of internal links resolve correctly when the site is built (zero
  broken link errors in build output).
- **SC-004**: The landing page loads and displays all content within 3 seconds on
  standard broadband connection.
- **SC-005**: Content authors can add a new chapter by creating a single markdown file
  with proper frontmatter (no additional configuration required).
