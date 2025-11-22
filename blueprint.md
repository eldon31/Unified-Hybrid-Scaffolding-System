# 📘 Domain Blueprint & Context Richness Map

> This blueprint is derived from the Dependency Graph Construction (Phase 1) and Context Richness Analysis (Phase 2) of the Hybrid Scaffolding System [3]. It provides the LLM with a logical flow of understanding, ensuring it sees 'logical flow of understanding, not random files!' [12].

## 1. Architectural Layers (Centrality-Based Structure)

The structure is organized by dependency, where modules with high **In-Degree** (high centrality) form the core foundation and are extracted first [4, 7].

| Layer | Definition | Extraction Strategy [8] |
| :--- | :--- | :--- |
| **Layer 0: Core Modules (High Centrality)** | Entry points, main orchestration logic, and foundational interfaces [3]. | **FULL** extraction (Complete file) [8]. |
| **Layer 1: Domain Models/Logic** | Business rules, models, and entities [3]. | **SIGNATURE** extraction (Classes/functions only) [8]. |
| **Layer 2: Data Layer / Persistence** | Storage, persistence logic, and API contracts [3]. | **STRUCTURED** or **SIGNATURE** extraction [13]. |
| **Layer 3: Utilities & Helpers** | Low-centrality, low-complexity functions [3]. | **MINIMAL** extraction (Docstrings only) [8]. |

## 2. Core Entities and Critical Paths

This section summarizes components with the highest **Centrality** scores [4]. These files are considered **Essential for others** and are critical architectural pieces [4].

### 2.1 Foundational Systems (Focus Areas)

*   **[Repo Name: github/awesome-copilot]**: Identify core configuration and interface models here.
*   **[Repo Name: github/spec-kit]**: Identify the primary parser or execution entry points.
*   **[Repo Name: bmad-code-org/BMAD-METHOD]**: Identify the main processing loop or calculation engine.
*   **[Repo Name: Fission-AI/OpenSpec]**: Identify the key specification definition models.

## 3. Context Richness Map (Understanding Difficulty)

This map highlights files with high **Cyclomatic Complexity** [4], indicating **Understanding Difficulty** [4]. These complex sections will be extracted using the **SIGNATURE** strategy to maximize token efficiency while preserving structure [8, 13].

| Component/File Path | Complexity (CC) | Context Richness (#APIs, LOC) [4] | Required Explanation |
| :--- | :--- | :--- | :--- |
| `src/core/router.py` | [CC Score] | [API Count, LOC] | High (Due to branching logic and conditional statements). |
| `src/data/processor.ts` | [CC Score] | [API Count, LOC] | Medium (Complex data transformation logic). |

## 4. Data Structure Schemas

Explicitly defining data structures eliminates ambiguity, as **Pydantic models** serve as "executable documentation" [10, 11]. This ensures the LLM understands the expected types and constraints [10].

### 4.1 Domain Data Models
*   **User/Request Model:** See `./schemas/request_model.py` for Pydantic definition.
*   **Output Payload:** See `./schemas/response_schema.json` for JSON Schema definition.
