# 🚀 QUICK START GUIDE - 5 Minutes to Go

**Goal**: Get your upgraded file organizer running in 5 minutes

---

## ⏱️ Step 1: Start the System (1 minute)

```bash
cd d:\AUTOMATION
python realtime_organizer.py
```

**What happens**:
- Initial scan of `D:/TEST_AI/input`
- Files analyzed and classified
- All decisions logged to `decision_log.json`
- Summary shown at end
- Press `Ctrl+C` to stop

```
🔍 Running initial scan...
════════════════════════════════════════════════════════════════
✓ CPU Scheduling.pdf → COLLEGE
✓ Python Tutorial.pdf → PROGRAMMING
⊙ resume_v1.pdf: Duplicate detected → skipped
🛡️  .gitignore: BLOCKED - Hidden file
════════════════════════════════════════════════════════════════
✓ Initial scan completed

📊 DECISION LOG SUMMARY
════════════════════════════════════════════════════════════════
Files Moved:      38
Files Skipped:    3
Duplicates Found: 1
Processing Errors: 0
Total Entries:    42
════════════════════════════════════════════════════════════════
```

---

## 📊 Step 2: Review Results in CLI (2 minutes)

```bash
python realtime_organizer.py cli
```

**Type these commands**:

```bash
organizer> help
# See all available commands

organizer> status
# Check current mode and settings

organizer> summary
# View statistics

organizer> history 10
# See last 10 decisions

organizer> explain "CPU Scheduling"
# Understand why that file was moved
```

**Expected output**:
```
organizer> summary
════════════════════════════════════════════════════════════════
📊 DECISION LOG SUMMARY
════════════════════════════════════════════════════════════════
Files Moved:      38
Files Skipped:    3
Duplicates Found: 1
Processing Errors: 0
Total Entries:    42
Log File:         D:/AUTOMATION/decision_log.json
════════════════════════════════════════════════════════════════

organizer> history 3
📜 Recent Decisions (last 3)
════════════════════════════════════════════════════════════════
✓ 2026-03-02 | MOVED      | CPU Scheduling.pdf    | COLLEGE
✓ 2026-03-02 | MOVED      | Python Tutorial.pdf   | PROGRAMMING
✗ 2026-03-01 | SKIPPED    | random_config.json    | Reference
```

---

## 🔍 Step 3: Understand System Decisions (1 minute)

```bash
organizer> explain CPU Scheduling
```

**Output**:
```
📋 Explanation(s) for: CPU Scheduling
════════════════════════════════════════════════════════════════
📅 2026-03-02T10:15:23
   Action:      MOVED
   Category:    COLLEGE
   Subject:     Operating Systems
   Reason:      Semantic classifier predicted COLLEGE and subject classifier selected: Operating Systems.
   Confidence:  92%
   Destination: D:/01_COLLEGE/Operating Systems/CPU Scheduling.pdf
```

**What this tells you**:
- File **was moved** ✓
- To **COLLEGE** category
- Detected **Operating Systems** subject
- **92% confidence** - very high!
- Reason: **Semantic model** + **subject detection**

---

## 👁️ Step 4: Test Preview Mode (1 minute)

```bash
organizer> preview
✓ Preview mode ENABLED - files will NOT be moved

organizer> exit
```

**What this does**:
- Next time you run the system, files will be analyzed but NOT moved
- Each file analyzed is queued for review
- You can then approve individually
- Perfect for testing before full automation

To use:
```bash
python realtime_organizer.py
# Files are analyzed and queued
# Check decision_log.json to see what would be moved
# When happy, switch back to auto mode
```

---

## ✅ Step 5: Enable Full Automation (0 minute)

Already enabled by default! The system is ready to:

```bash
python realtime_organizer.py
# Leave running to continuously process new files
# All decisions logged automatically
# High-confidence files move silently
# Low-confidence files are skipped
# Protected files never moved
```

---

## 🎯 3-Mode Cheat Sheet

### Auto Mode (Default - Silent)
```bash
python realtime_organizer.py cli
organizer> auto
organizer> exit
python realtime_organizer.py
# Files move automatically, logged to decision_log.json
```

### Manual Mode (Ask Permission)
```bash
python realtime_organizer.py cli
organizer> manual
organizer> exit
python realtime_organizer.py
# Each file requires Y/N approval before moving
```

### Preview Mode (No Moves)
```bash
python realtime_organizer.py cli
organizer> preview
organizer> exit
python realtime_organizer.py
# Files analyzed but NOT moved
# Review decisions before manually moving
```

---

## 📁 What's New (The 6 Phases)

| Phase | What's New | Example |
|-------|-----------|---------|
| 1️⃣ Logging | Every decision saved | See `decision_log.json` |
| 2️⃣ Preview | Review before moving | `organizer> preview` |
| 3️⃣ Explain | Understand decisions | `organizer> explain file` |
| 4️⃣ Confidence | Trust scores (0-100%) | "92% confidence" |
| 5️⃣ CLI | Interactive control | `organizer> help` |
| 6️⃣ Safety | Protected critical files | `.git`, `package.json`, etc. |

---

## 🎮 Essential CLI Commands

```bash
# START INTERACTIVE MODE
python realtime_organizer.py cli

# INSIDE CLI:
organizer> help              Show all commands
organizer> status            Show current mode
organizer> summary           Show statistics
organizer> history 10        Last 10 decisions
organizer> explain filename  Why that file?
organizer> preview           Enable preview
organizer> auto              Auto mode
organizer> manual            Manual mode
organizer> exit              Quit
```

---

## 💾 Files Created

**Decision Log** (most important):
- Location: `D:/AUTOMATION/decision_log.json`
- Contains: Every file decision with reasoning
- Opens in: Any text editor or Excel

**System Status**:
- Location: CLI command `organizer> status`
- Shows: Current mode, total decisions, move counts

**History**:
- Command: `organizer> history 20`
- Shows: Last 20 decisions

---

## 🆘 Troubleshooting (30 seconds)

### System won't start
```bash
# Check Python version
python --version
# Should be 3.8+

# Check you're in right directory
cd d:\AUTOMATION

# Try explicit path
python .\realtime_organizer.py
```

### Files not being moved
```bash
python realtime_organizer.py cli
organizer> status
# If "manual" or "preview" mode: switch to auto
organizer> auto
organizer> exit
```

### Want to understand a decision
```bash
organizer> explain "filename"
# Shows exactly why it was handled that way
```

### Too many files being skipped
```bash
organizer> history 20
# Look at rejection reasons
organizer> explain "skipped_file"
# See if it's low confidence or safety block
```

---

## 📚 Full Docs (If You Answer Yes To Any)

**If you ask...** → **Read this**
- "What are all the new files?" → `ARCHITECTURE.md`
- "How does confidence scoring work?" → `UPGRADE_GUIDE.md` (Phase 4)
- "What's the full command list?" → `CLI_REFERENCE.md`
- "What was changed?" → `UPGRADE_SUMMARY.md`

---

## ⚡ Power User Tips

### Tip 1: Continuous Monitoring
```bash
# Leave this running in a terminal
python realtime_organizer.py

# Files from D:/TEST_AI/input will be continuously processed
# All decisions logged to decision_log.json
# Press Ctrl+C to stop
```

### Tip 2: Quick Health Check
```bash
python realtime_organizer.py cli
organizer> summary
# If most files >80% confidence, system is working well!
```

### Tip 3: Learn System Behavior
```bash
python realtime_organizer.py cli
organizer> preview
organizer> exit
# Run: python realtime_organizer.py
# Let it analyze files (don't move yet)
organizer> history 50
# Review what would have been moved
```

### Tip 4: Search for Issues
```bash
organizer> search "error"
# Find any problematic files

organizer> search "low confidence"
# Find uncertain classifications

organizer> search "operating systems"
# Find all COLLEGE/OS decisions
```

---

## 🎉 Success Indicators

After 5 minutes, you should see:

✅ System runs without errors
✅ Initial scan completes
✅ CLI responds to commands
✅ `decision_log.json` is created with entries
✅ `help` command shows all available commands
✅ `summary` shows statistics (moved/skipped counts)
✅ `explain` command works for files
✅ Hidden files are BLOCKED (safety working)
✅ Confidence scores shown (e.g., "92%")
✅ System in correct operating mode

---

## 🚀 What's Next?

### Immediate (Today)
1. Run initial scan: `python realtime_organizer.py`
2. Check results: `python realtime_organizer.py cli` → `status`
3. Verify working: Look at `decision_log.json`

### Short Term (This Week)
1. Leave monitoring active to process new files
2. Check `organizer> history` periodically
3. Use `organizer> explain` on any suspicious decisions
4. Read `UPGRADE_GUIDE.md` for deeper understanding

### Long Term (Ongoing)
1. Monitor system health: `organizer> summary`
2. Verify no false positives: Check safety blocks
3. Optimize thresholds if needed (in code)
4. Integrate with other tools (future enhancement)

---

## 📞 Need Help?

| Issue | Solution |
|-------|----------|
| Command doesn't work | `organizer> help` |
| File moved wrong place | `organizer> explain filename` |
| Too many rejections | `organizer> history` - check confidences |
| Want to understand decision | `organizer> explain filename` |
| Need detailed guide | Read `UPGRADE_GUIDE.md` |
| Commands reference | Read `CLI_REFERENCE.md` |
| System design | Read `ARCHITECTURE.md` |

---

## ⏱️ Time Check

```
Step 1: Start system    ✅ 1 min
Step 2: Review in CLI   ✅ 2 min
Step 3: Understand      ✅ 1 min
Step 4: Test preview    ✅ 1 min
Step 5: Enable auto     ✅ 0 min
────────────────────────────────
Total time:             ✅ 5 min
```

**You're done! System is ready to use.** 🎉

---

## 🎯 One-Minute Version

```bash
# 1. Run system
python realtime_organizer.py

# 2. Check status
python realtime_organizer.py cli
organizer> summary
organizer> exit

# 3. Done!
# Files are being processed and logged
```

**That's it!** System is now running with full transparency and control. 🚀

---

**Last Updated**: 2026-03-02  
**Time to Deploy**: 5 minutes  
**Complexity**: Very Simple ✅
