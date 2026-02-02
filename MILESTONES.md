# Project Milestones

## v0.1.0 – Stable Local Baseline (LOCKED)

### What works
- FastAPI app boots safely
- No hard dependency on DB / Redis
- /health endpoint available
- /ready endpoint available
- OpenAPI schema accessible

### Operations
- airdrop.ps1 controls lifecycle:
  - start
  - stop (PID-safe)
  - status
  - test (basic)

### Guarantees
- Server can be started/stopped repeatedly
- Health checks pass locally
- Failures do not crash startup

### Status
✅ Baseline locked  
🚀 Ready for test command upgrade
