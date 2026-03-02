# 📦 New Files & Architecture Overview

## Files Created

### Core Upgrade Modules (6 Phases)

| File | Phase | Purpose | Key Features |
|------|-------|---------|---|
| `decision_log.py` | 1 | Complete audit trail | Logs every decision to JSON |
| `preview_mode.py` | 2 | Safe preview workflow | Review before moving, queued decisions |
| `explanation_engine.py` | 3 | Decision explanations | Human-readable "why" for each decision |
| `confidence_scorer.py` | 4 | Confidence calculation | 0-100% scores, thresholds, signal combination |
| `cli_interface.py` | 5 | Interactive CLI | Full command interface for control |
| `safety_guardrails.py` | 6 | File protection | Blocks hidden, system, and critical files |

### Enhanced Main File

| File | Purpose | Changes |
|------|---------|---------|
| `realtime_organizer.py` | Main orchestrator | Integrated all 6 phases, added logging, safety checks |
| `realtime_organizer_upgraded.py` | Upgrade template | Full upgraded version (saved as reference) |
| `realtime_organizer_backup.py` | Backup | Original version (for rollback if needed) |

### Documentation

| File | Purpose |
|------|---------|
| `UPGRADE_GUIDE.md` | Comprehensive upgrade guide (70+ KB) |
| `CLI_REFERENCE.md` | Quick command reference |
| `ARCHITECTURE.md` | This file - architecture overview |

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     FILE ORGANIZER SYSTEM                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐     ┌──────────────┐      ┌──────────────┐   │
│  │   FILE INPUT     │────▶│   SAFETY     │─────▶│  PROCESS     │   │
│  │  (Watchdog)      │     │ GUARDRAILS   │      │   FILE       │   │
│  └──────────────────┘     │   (Phase 6)  │      └──────────────┘   │
│                           └──────────────┘            │             │
│                                                       ▼             │
│  ┌──────────────────┐     ┌──────────────┐      ┌──────────────┐   │
│  │  DECISION LOG    │◀────│ CONFIDENCE   │◀─────│  CLASSIFY    │   │
│  │   (Phase 1)      │     │  SCORING     │      │  & EXTRACT   │   │
│  │                  │     │  (Phase 4)   │      │  CONTENT     │   │
│  └──────────────────┘     └──────────────┘      └──────────────┘   │
│        │                         ▲                     │             │
│        │                         │                     ▼             │
│        │                   ┌──────────────┐      ┌──────────────┐   │
│        │                   │ EXPLANATION  │      │   SUBJECT    │   │
│        │                   │   ENGINE     │      │ CLASSIFIER   │   │
│        └──────────────────▶│  (Phase 3)   │◀─────│              │   │
│                            └──────────────┘      └──────────────┘   │
│                                  │                                   │
│        ┌─────────────────────────┴──────────────────────────┐       │
│        ▼                          ▼                          ▼       │
│  ┌──────────────┐        ┌──────────────┐        ┌──────────────┐  │
│  │  PREVIEW     │        │   EXECUTE    │        │   SEMANTIC   │  │
│  │    MODE      │        │    MOVE      │        │    MEMORY    │  │
│  │ (Phase 2)    │        │              │        │   INDEXING   │  │
│  └──────────────┘        └──────────────┘        └──────────────┘  │
│        │                        │                                    │
│        └────────────┬───────────┴──────────────────┬────────────┘  │
│                     ▼                              ▼                │
│            ┌──────────────┐            ┌──────────────┐            │
│            │  DECISION    │            │   CLI INTER  │            │
│            │  LOG JSON    │            │   FACE       │            │
│            │              │            │  (Phase 5)   │            │
│            └──────────────┘            └──────────────┘            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Phase 1: File Detection
```
Filesystem Event
    ↓
Watchdog detects file creation/modification
    ↓
Debounce check (avoid duplicate processing)
    ↓
Next Phase: Safety Check
```

### Phase 2-6: Processing Pipeline
```
File Path
    ↓
SAFETY GUARDRAILS (Phase 6)
├─ Is hidden? → SKIP
├─ Is system file? → SKIP
├─ Is build artifact? → SKIP
└─ Is critical project file? → SKIP
    ↓ (if safe)
CONTENT EXTRACTION
├─ Extract text/metadata
├─ Analyze structure
└─ Prepare for classification
    ↓
KEYWORD DETECTION
├─ Check filename
├─ Check path
└─ Check content for keywords
    ↓
CONFIDENCE SCORING (Phase 4)
├─ Keyword match score
├─ Weight by priority
└─ Start combining signals
    ↓
AI CLASSIFICATION
├─ Semantic embedding
├─ Category prediction
└─ Subject detection (if COLLEGE)
    ↓
CONFIDENCE COMBINATION
├─ Keyword score (35% weight)
├─ Semantic score (40% weight)
├─ Extension score (15% weight)
└─ Subject score (10% weight)
    ↓
EXPLANATION GENERATION (Phase 3)
├─ Which signals triggered decision
├─ Confidence level
└─ Final reasoning
    ↓
CONFIDENCE THRESHOLD CHECK
├─ >80%? → AUTO MOVE
├─ 60-80%? → NEEDS CONFIRMATION
├─ 40-60%? → SKIP (uncertain)
└─ <40%? → SKIP (very uncertain)
    ↓
DESTINATION DETERMINATION
├─ Handle versioning
├─ Check for duplicates (hash)
└─ Final path calculation
    ↓
PREVIEW MODE CHECK (Phase 2)
├─ If preview enabled → QUEUE for review
├─ If manual mode → ASK user
└─ If auto mode → PROCEED
    ↓
DECISION LOGGING (Phase 1)
├─ Log to decision_log.json
├─ Log to file_logs.csv
└─ Log to move_history.json
    ↓
EXECUTE MOVE
├─ Safe move with retry logic
├─ Handle lock conflicts
└─ Update move history
    ↓
SEMANTIC INDEXING
├─ Store in FAISS
├─ Link to category/subject
└─ Enable semantic search
    ↓
DONE
```

---

## Confidence Scoring Algorithm

```
Input: File with detection signals
    ↓
Extract Signals:
├─ Keywords found in filename/content
├─ Semantic similarity score from AI model
├─ File extension classification
└─ Subject classification (if applicable)
    ↓
Score Each Signal:
├─ Keyword: 0-1 based on count & priority
│   └─ 1 keyword: 0.45-0.95 (depends on priority)
│   └─ 2 keywords: 0.70-0.95
│   └─ 3+ keywords: 0.95-0.99
│
├─ Semantic: 0-1 from embedding model
│   └─ Direct output of cosine similarity
│   └─ Dampened by 5% for uncertainty
│
├─ Extension: 0.55-0.75
│   └─ 0.55 if no content analysis
│   └─ 0.75 if combined with semantic
│
└─ Subject: 0.80-0.99
    └─ Adds 10% boost to primary category
    └─ If 2+ subject keywords match
    ↓
Weight and Combine:
├─ Keyword score × 0.35
├─ Semantic score × 0.40
├─ Extension score × 0.15
├─ Subject score × 0.10
└─ Sum = Final Confidence (0-1)
    ↓
Determine Action:
├─ 0.95-1.00 (VERY HIGH 🟢)  → AUTO MOVE
├─ 0.85-0.94 (HIGH 🟢)        → AUTO MOVE + LOG
├─ 0.70-0.84 (MEDIUM 🟡)      → CONFIRM
├─ 0.50-0.69 (LOW 🟠)         → SKIP
└─ 0.00-0.49 (VERY LOW 🔴)    → SKIP
    ↓
Output: Decision with confidence score
```

---

## Decision Log Schema

```json
{
  "timestamp": "ISO 8601 timestamp",
  "file": "string - basename",
  "file_path": "string - full path",
  "file_size_bytes": "int",
  "action": "moved | skipped | duplicate | preview | error",
  "reason": "string - human-readable explanation",
  "category": "COLLEGE | PROGRAMMING | PROJECTS | CAREER | REFERENCE | null",
  "subject": "string or null",
  "destination": "string - final path or null",
  "confidence": "float 0-1 or null",
  "details": {
    "signals": ["array of explanation strings"],
    "confidence_action": "auto | confirm | skip | manual",
    "file_size": "int",
    "violations": ["array if safety check failed"],
    "error": "string if error occurred"
  }
}
```

---

## Safety Guardrails Rules

```python
Block if:
├─ Hidden file (starts with .)
│   ├─ .git, .github, .vscode, .idea, .env, .config, .cache, etc.
│   └─ Reason: Contains sensitive project metadata
│
├─ Critical project configuration
│   ├─ package.json, setup.py, pyproject.toml, Pipfile
│   ├─ pom.xml, build.gradle, docker-compose.yml, etc.
│   └─ Reason: Project depends on these files being in place
│
├─ Build/cache directories
│   ├─ node_modules, venv, .gradle, build, dist, target
│   ├─ .dart_tool, android, ios, windows, linux, macos, etc.
│   └─ Reason: Regenerable, automatically created
│
├─ System executables
│   ├─ .exe, .dll, .sys, .msi, .app, .dmg, .deb, .rpm, .apk
│   └─ Reason: System files, shouldn't be moved
│
└─ Package lock files
    ├─ package-lock.json, yarn.lock, poetry.lock, Gemfile.lock
    └─ Reason: Project dependencies, shouldn't be moved
```

---

## CLI Interface Commands

```
MODES:
  auto              Enable automatic mode
  manual            Require approval for all moves
  preview           Show decisions without moving
  status            Show current settings

QUERIES:
  explain <file>    Explain why file was handled
  search <pattern>  Search decision log
  history [n]       Show last n decisions
  summary           Show statistics

CONFIG:
  config show       Display settings
  help              Show help
  exit              Exit program
```

---

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| File detection | <50ms | Watchdog event |
| Safety check | <5ms | File path parsing |
| Content extraction | 500-2000ms | Depends on file size/type |
| Semantic embedding | 100-500ms | Model inference |
| Classification | 50-200ms | Category + subject |
| Confidence scoring | <5ms | Simple arithmetic |
| Move operation | 100-500ms | Filesystem I/O |
| Decision logging | <10ms | JSON write |
| Total per file | 1-3 seconds | Sequential processing |

---

## Integration Points

### With Existing System
- Uses existing `extract_content()` from `ai_content_engine`
- Uses existing `classify_document()` from `semantic_classifier`
- Uses existing `classify_subject()` from `subject_classifier`
- Uses existing `add_document_memory()` from `semantic_memory`
- Maintains backward compatibility with `move_history.json`

### New Integration Points
- Decision logging (new, separate)
- Preview mode (new, optional)
- Explanation engine (new, decorative)
- Confidence scoring (new, gating mechanism)
- CLI interface (new, optional)
- Safety guardrails (new, protective)

---

## File Structure

```
D:/AUTOMATION/
├── realtime_organizer.py              [Main file - UPGRADED]
├── realtime_organizer_backup.py       [Original backup]
├── realtime_organizer_upgraded.py     [Upgrade template]
│
├── PHASE IMPLEMENTATION FILES:
├── decision_log.py                    [Phase 1]
├── preview_mode.py                    [Phase 2]
├── explanation_engine.py              [Phase 3]
├── confidence_scorer.py                [Phase 4]
├── cli_interface.py                   [Phase 5]
├── safety_guardrails.py               [Phase 6]
│
├── EXISTING FILES:
├── ai_content_engine.py
├── semantic_classifier.py
├── subject_classifier.py
├── semantic_memory.py
├── project_health_engine.py
├── semantic_engine.py
├── analytics_dashboard.py
├── project_intelligence.py
├── suggestion_engine.py
├── test_classifier.py
│
├── DATA FILES:
├── decision_log.json                  [NEW - Decision audit trail]
├── file_logs.csv                      [Existing - CSV logs]
├── move_history.json                  [Existing - Move records]
├── jarvis_prompt_history.txt
├── semantic_memory.index
│
└── DOCUMENTATION:
    ├── UPGRADE_GUIDE.md               [Full upgrade documentation]
    ├── CLI_REFERENCE.md               [Command reference]
    └── ARCHITECTURE.md                [This file]
```

---

## Backward Compatibility

✓ All existing files unchanged (except realtime_organizer.py)
✓ All existing functions still work
✓ CSV logging still works (file_logs.csv)
✓ Move history still recorded (move_history.json)
✓ Semantic memory still indexed (semantic_memory.index)
✓ Can disable new features in code
✓ Can rollback to realtime_organizer_backup.py

---

## Future Enhancement Ideas

1. **Machine Learning Feedback**
   - Track user corrections
   - Retrain confidence model
   - Learn user preferences

2. **Advanced Reporting**
   - Dashboard of decision statistics
   - Charts of confidence distribution
   - Category accuracy metrics

3. **Bulk Operations**
   - Process entire directories
   - Batch approve/reject
   - Undo multiple moves

4. **Integration**
   - Slack notifications
   - Email reports
   - Cloud sync

5. **Advanced Confidence**
   - Per-category thresholds
   - Ensemble methods
   - Bayesian updates

---

## Troubleshooting Guide

### Import Errors
```
ModuleNotFoundError: No module named 'decision_log'
→ Check all new .py files are in D:/AUTOMATION/
```

### Decision Log Permission Errors
```
PermissionError: Cannot write decision_log.json
→ Check file permissions in D:/AUTOMATION/
```

### CLI Not Starting
```
CLI interface won't start
→ python realtime_organizer.py cli
→ Check python version (3.8+)
```

### Files Not Being Moved
```
Check with: organizer> status
→ May be in preview/manual mode
→ May have low confidence (<70%)
→ May be blocked by safety rules
```

---

**Architecture Version**: 1.0  
**Created**: 2026-03-02  
**Status**: Documented & Ready ✓
