# Legacy Files

This directory contains archived files from the refactoring process. These files are preserved for reference but are no longer actively used.

## Contents

### Refactor Documentation
- `REFACTOR_PROGRESS.md` - Progress tracking during the refactor
- `FRONTEND_REFACTOR_GUIDE.md` - Step-by-step guide for frontend extraction
- `REFACTOR_COMPLETE.md` - Complete results and benefits report
- `REFACTOR_SUMMARY.md` - Final summary of the refactor

### Backup Files
- `scene.py.backup` - Original 2,025-line monolithic scene.py (before refactor)
- `index.html.backup` - Original 1,373-line HTML with inline JavaScript (before refactor)

### Legacy Implementations
- `artnet-bridge-js/` - JavaScript-based ArtNet bridge (superseded by Rust implementation)
- `standalone-js-simulator/` - JavaScript simulator (superseded by Python implementation)
- `test-files/` - Old test files
- `docs/` - Historical documentation

## Note

All files in this directory are excluded from Claude Code's context via `.claudeignore` to keep the working context clean and focused on active development.

For current documentation, see the main project README.
