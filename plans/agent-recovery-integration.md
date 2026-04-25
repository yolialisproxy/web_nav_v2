# my-agent Recovery System Unification Plan

**Goal**: Solve fragmentation of recovery mechanisms, achieve zero-config, fully automatic self-healing Agent runtime

**Date**: 2026-04-25
**Status**: Pending
**Author**: yoli

---

## Current State Analysis

### Existing Components Matrix

| Component | Path | Status | Role | Problem |
|---|---|---|---|---|
| agent-recovery v2.5 | ~/.hermes/skills/my-agent/agent-recovery/ | Lib ready, NOT integrated | In-process daemon, 5-level recovery, unified state | Not in Hermes main process |
| agent-runtime | ~/.hermes/skills/my-agent/agent-runtime/ | Running | Checkpointing, cron wakeup, state management | External cron dependency |
| agent-core | ~/.hermes/skills/my-agent/agent-core/ | Running | Anti-hallucination, verification | Contains deprecated scripts |
| agent-stability | ~/.hermes/skills/my-agent/agent-stability/ | Deprecated | Memory check, process monitor | Merged to v2.5 |

---

## Upgrade Principles

1. Zero user config - Works immediately upon Agent start
2. Single recovery mechanism - agent-recovery v2.5 as sole source
3. Backward compatible - Preserve checkpoint capability
4. Silent operation - No logs when healthy
5. Auto cleanup - Deprecated components auto-flagged

---

## Unified Architecture (v3.0)

Hermes Gateway Main Process (v3.0)
├── Main Thread: Task Execution Loop
│   └── Every 5-10s: Monitor.heartbeat()
│
├── Daemon Thread 1: Monitor._heartbeat_loop (every 30s)
├── Daemon Thread 2: Monitor._memory_loop (every 5s)
├── Daemon Thread 3: Monitor._watchdog_loop (every 10s)
│
└── RecoveryEngine: 5-level recovery (L0-L4)
    └── Single state file: ~/.hermes/state/agent_state.json

---

## Integration Steps

### Step 1: sitecustomize Hook

Create `~/.hermes/sitecustomize.py`:

```python
import os, sys
from pathlib import Path

# Auto-enable for Hermes
if 'hermes' in ' '.join(sys.argv) or os.environ.get('HERMES_AUTO_RECOVERY') == '1':
    try:
        lib = Path.home() / '.hermes' / 'skills' / 'my-agent' / 'agent-recovery' / 'library'
        sys.path.insert(0, str(lib))
        from monitor import enable_monitoring
        enable_monitoring()
    except:
        pass
```

### Step 2: Patch agent-runtime/__main__.py

Replace state_manager usage with StateManager from agent-recovery.
Remove heartbeat and install_cron commands.

### Step 3: Unified State

agent-runtime checkpoint fields → merged into agent_state.json checkpoint section.

### Step 4: Remove Cron

- Delete install_cron command
- Remove wakeup.sh reference
- Recovery all handled by daemon threads

---

## Health Check & Auto-Fix

### health_check.py

- Check library files exist
- Check psutil installed
- Check agent_state.json heartbeat freshness
- Check Hermes process has recovery enabled

Return codes: 0=OK, 2=issues found

### auto_fix.py

- Install missing psutil
- Create sitecustomize hook if missing
- Trigger recovery if heartbeat stale

---

## Cleanup Plan

DEPRECATED (delete after 14 days):
- my-agent/agent-stability/
- my-agent/agent-core/scripts/heartbeat.py
- my-agent/agent-core/scripts/mem_cleaner.py
- my-agent/agent-runtime/scripts/heartbeat.py
- my-agent/agent-runtime/scripts/state_manager.py
- my-agent/agent-recovery/scripts.deprecated.v2.4/

---

## Migration

From v2.4: Auto-migrate state files, backup & clear cron.
From v2.5: Just enable sitecustomize hook.
Fresh: Auto-enables.

---

## Success Criteria

- [ ] No hermes cron tasks
- [ ] Single state file: agent_state.json
- [ ] Auto-enable on Hermes start
- [ ] Logs < 5 lines daily when healthy
- [ ] L0 <100ms, L3 <2s
- [ ] Deprecated scripts removed

---

## Risks & Rollback

Risk: Hermes path varies → Use sitecustomize (global hook)
Risk: Custom cron tasks → Backup before removal

Rollback:
```bash
export HERMES_AUTO_RECOVERY=0
crontab ~/.hermes/backup/cron-before-v3
```

---

**End**: Final unification of my-agent recovery system.