# 🎮 Synapse CLI Commands Quick Reference

## 🚀 Start Synapse

```bash
# Run with real-time monitoring
python realtime_organizer.py

# Start interactive CLI only
python realtime_organizer.py cli
```

---

## 🎛️ Mode Commands

```bash
synapse> auto
✓ Switched to AUTO mode - files will be moved silently

synapse> manual  
✓ Switched to MANUAL mode - all files require user confirmation

synapse> preview
✓ Switched to PREVIEW mode - decisions shown without moving files

synapse> status
📊 SYSTEM STATUS
════════════════════════════════════════════════════════════════
Operating Mode:     AUTO
Preview Mode:       DISABLED
Total Decisions:    42
  - Moved:         38
  - Skipped:       3
  - Duplicates:    1
════════════════════════════════════════════════════════════════
```

---

## 🔍 Query Commands

### Get Help
```bash
synapse> help
╔════════════════════════════════════════════════════════════════════╗
║                           AVAILABLE COMMANDS                       ║
[Shows all available commands with examples]
╚════════════════════════════════════════════════════════════════════╝
```

### Explain a File's Decision
```bash
synapse> explain CPU Scheduling.pdf
📋 Explanation(s) for: CPU Scheduling.pdf
════════════════════════════════════════════════════════════════════
📅 2026-03-02T10:15:23
   Action:      MOVED
   Category:    COLLEGE
   Subject:     Operating Systems
   Reason:      Semantic classifier predicted COLLEGE...
   Confidence:  92%
   Destination: D:/01_COLLEGE/Operating Systems/CPU Scheduling.pdf

synapse> explain "partial name"
# Finds all files containing "partial name" in decision log
```

### Search Decisions
```bash
synapse> search operating systems
🔍 Search Results: 3 match(es)
════════════════════════════════════════════════════════════════════
✓ [2026-03-02] CPU Scheduling.pdf             → Semantic classifier...
✓ [2026-03-02] Memory Management.pdf          → Subject classifier...
✗ [2026-03-01] abstract_os_paper.docx         → Skipped - insufficient keywords...

synapse> search "lab"
# Find all files with "lab" in filename or reason

synapse> search programming
# Find all PROGRAMMING category decisions
```

### View History
```bash
synapse> history
📜 Recent Decisions (last 10)
════════════════════════════════════════════════════════════════════
✓ 2026-03-02 | MOVED      | CPU Scheduling.pdf    | COLLEGE
✓ 2026-03-02 | MOVED      | Python Tutorial.pdf   | PROGRAMMING
⊙ 2026-03-01 | DUPLICATE  | resume_v1.pdf         | CAREER
✗ 2026-03-01 | SKIPPED    | config.json           | Reference
✓ 2026-03-01 | MOVED      | Flutter App.zip       | Projects

synapse> history 5
# Shows last 5 decisions

synapse> history 50
# Shows last 50 decisions
```

### View Summary
```bash
synapse> summary
════════════════════════════════════════════════════════════════════
📊 DECISION LOG SUMMARY
════════════════════════════════════════════════════════════════════
Files Moved:      38
Files Skipped:    3
Duplicates Found: 1
Processing Errors: 0
Total Entries:    42
Log File:         D:/AUTOMATION/decision_log.json
════════════════════════════════════════════════════════════════════

# Perfect for checking system health and statistics
```

---

## ⚙️ Configuration

### Show Config
```bash
synapse> config show
⚙️  Configuration:

Confidence Threshold (auto):     80%
Confidence Threshold (confirm):  60%
Confidence Threshold (reject):   40%
Semantic Model:                  all-mpnet-base-v2
Decision Log:                    D:/AUTOMATION/decision_log.json

# Shows all current settings
```

### Threshold Adjustment
```bash
synapse> config threshold
# (Feature for future: adjust thresholds interactively)
```

---

## 📈 Decision Log Files Created

### Main Decision Log
```
Location: D:/AUTOMATION/decision_log.json
Contains: Every decision by the system
Format:   JSON with timestamp, reason, confidence, etc.
```

### CSV Log (Legacy)
```
Location: D:/AUTOMATION/file_logs.csv
Contains: Simple CSV of moves for reporting
Format:   timestamp, category, extension, size, source
```

### Move History
```
Location: D:/AUTOMATION/move_history.json
Contains: File path transformations
Format:   JSON with [file_path, destination, timestamp, category, subject]
```

---

## 💡 Common Workflows

### Workflow 1: Initial Testing
```bash
python realtime_organizer.py cli
synapse> summary
# Check initial scan results

synapse> history 20
# See what was processed

synapse> explain "suspicious_file"
# Understand specific decisions

synapse> exit
```

### Workflow 2: Preview Before Automation
```bash
synapse> preview
# Enable preview mode
# Files are queued, not moved

synapse> status
# Check what's in preview queue

synapse> explain queued_file
# Check specific queued files

synapse> exit
# When satisfied, disable preview and enable auto
organizer> auto
```

### Workflow 3: Debug a Move
```bash
organizer> explain "the_file.pdf"
# Get full explanation

organizer> search "specific_keyword"
# Find related decisions

organizer> status
# Check overall system health

organizer> exit
```

### Workflow 4: Monitor System Health
```bash
organizer> summary
# Check move/skip counts

organizer> status
# Check confidence average

organizer> history
# Recent activity

# Look for:
# - Too many skips → confidence threshold too high
# - Wrong categories → need to adjust rules
# - Blocked files → safety working correctly
```

---

## 🎯 Pro Tips

### Tip 1: Batch Process New Files
```bash
python realtime_organizer.py
# Leave running to continuously monitor D:/TEST_AI/input
# New files are processed automatically
# Press Ctrl+C to stop
```

### Tip 2: Learn System Behavior
```bash
organizer> preview
# Enable preview to see all decisions without moving

organizer> exit
# Let system analyze files in background
# Don't press Y/N yet

organizer> history 100
# Later, review what would have been moved
```

### Tip 3: Check Confidence Before Trusting
```bash
organizer> history
# Look at confidence % for recent moves
# If many <80%, system is uncertain about files
# Consider checking a few with: explain <file>
```

### Tip 4: Search for Patterns
```bash
organizer> search "assignment"
# Find all "assignment" related files
# See how they were categorized

organizer> search "error"
# Find any errors or problems

organizer> search "skipped"
# Find all skipped files and why
```

### Tip 5: Use Decision Log for Auditing
```bash
# Open in Excel/spreadsheet:
D:\AUTOMATION\decision_log.json

# Can create pivot tables:
# - By action type (moved, skipped)
# - By confidence score distribution
# - By category
# - By timestamp (when were most processed)
```

---

## ❌ Exit Commands

```bash
organizer> exit
👋 Goodbye!

organizer> quit
# Same as exit

organizer> q
# Quick exit

# Or press Ctrl+C
^C
👋 Interrupted
```

---

## 📊 Understanding Output Icons

| Icon | Meaning | Example |
|------|---------|---------|
| ✓ | Success / File moved | ✓ CPU Scheduling.pdf → COLLEGE |
| ✗ | Skipped / Failed | ✗ config.json - Low confidence |
| ⊙ | Duplicate detected | ⊙ resume_v1.pdf: Duplicate |
| 🔑 | Keyword detected | 🔑 Keyword detected: assignment |
| 👁️  | Preview mode active | 👁️  Added to preview queue |
| ⚙️  | Build file | ⚙️  Build system file detected |
| 🛡️  | Safety block | 🛡️  BLOCKED - Hidden file |
| 🟢 | Very high/high confidence | 🟢 Confidence 92% |
| 🟡 | Medium confidence | 🟡 Confidence 75% |
| 🟠 | Low confidence | 🟠 Confidence 55% |
| 🔴 | Very low confidence | 🔴 Confidence 35% |

---

## 🆘 If Something Goes Wrong

### System refuses to move files
```bash
organizer> status
# Check if in "preview" or "manual" mode
organizer> auto
# Switch to automatic mode
```

### Too many files being skipped
```bash
organizer> history 20
organizer> explain "first_skipped_file"
# Check confidence score and reason
# If <70% confidence, that's why it was skipped
```

### Wrong category assigned
```bash
organizer> explain "wrong_file"
# See what signals led to wrong decision
# Report in decision log for future improvement
```

### File wasn't moved but should have been
```bash
organizer> search "filename"
# Check if file is in decision log at all
# If not in log: file may not meet relevance criteria
# Check decision_log for details
```

---

## 📝 Example Session

```bash
$ python realtime_organizer.py cli

🚀 SMART AUTONOMOUS FILE ORGANIZER - Interactive CLI
════════════════════════════════════════════════════════════════════
Type 'help' for available commands
════════════════════════════════════════════════════════════════════

organizer> status
📊 SYSTEM STATUS
════════════════════════════════════════════════════════════════════
Operating Mode:     AUTO
Preview Mode:       DISABLED
Total Decisions:    42
  - Moved:         38
  - Skipped:       3
  - Duplicates:    1
════════════════════════════════════════════════════════════════════

organizer> history 3
📜 Recent Decisions (last 3)
════════════════════════════════════════════════════════════════════
✓ 2026-03-02 | MOVED      | CPU Scheduling.pdf      | COLLEGE
✓ 2026-03-02 | MOVED      | Python Tutorial.pdf     | PROGRAMMING
✗ 2026-03-01 | SKIPPED    | random_config.json      | Reference

organizer> explain CPU Scheduling.pdf
📋 Explanation(s) for: CPU Scheduling.pdf
════════════════════════════════════════════════════════════════════
📅 2026-03-02T10:15:23
   Action:      MOVED
   Category:    COLLEGE
   Subject:     Operating Systems
   Reason:      Semantic classifier predicted COLLEGE...
   Confidence:  92%
   Destination: D:/01_COLLEGE/Operating Systems

organizer> exit
👋 Goodbye!
```

---

**Quick Copy-Paste Commands:**

```bash
# Start CLI
python realtime_organizer.py cli

# Common first commands
organizer> help
organizer> status
organizer> summary
organizer> history 10

# Explore a file
organizer> explain filename.pdf

# Change mode
organizer> auto
organizer> preview
organizer> manual

# Exit
organizer> exit
```

---

**Last Updated**: 2026-03-02  
**Version**: Quick Reference v1
