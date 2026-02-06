# Project Milestones

## v0.2.0 - Test & Doctor Upgrade

### New Features
- irdrop.ps1 test runs full system check:
  - Health endpoint
  - Ready endpoint (DB/Redis status)
  - OpenAPI availability
- irdrop.ps1 doctor checks local environment:
  - Python & Uvicorn
  - Logs folder
  - PID file sanity

### Operations
- Start/Stop/Status now fully compatible with test/doctor
- System tests pass even if DB/Redis disabled
- Failures handled gracefully

### Status
- ✅ Server controllable via PowerShell
- ✅ Test command functional
- ✅ Doctor command functional
