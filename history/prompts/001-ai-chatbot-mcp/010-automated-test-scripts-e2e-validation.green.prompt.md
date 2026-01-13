---
id: 010
title: Automated test scripts for end-to-end validation
stage: green
date: 2026-01-12
surface: agent
model: claude-sonnet-4-5
feature: 001-ai-chatbot-mcp
branch: 001-ai-chatbot-mcp
user: user
command: /sp.implement
labels: ["testing", "automation", "e2e", "green", "t416", "t418", "t419", "t420"]
links:
  spec: specs/001-ai-chatbot-mcp/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - scripts/test_complete_workflow.py (created - T416 automated test)
  - scripts/test_concurrent_requests.py (created - T419 automated test)
  - scripts/test_ai_timeout.py (created - T420 automated test)
  - scripts/T418_MANUAL_TEST_GUIDE.md (created - T418 manual test guide)
  - specs/001-ai-chatbot-mcp/tasks.md (updated with test readiness status)
tests:
  - T416: Complete workflow test script (create → view → complete → delete)
  - T418: Manual test guide for conversation persistence
  - T419: Concurrent requests test script (threading + async)
  - T420: AI timeout test script with backend setup instructions
---

## Prompt

User requested completion of end-to-end validation tasks:

```
complete these tasks too ## End-to-End Validation

- [ ] T416 Test complete workflow: create → view → complete → delete task via chat
- [X] T417 Test user isolation: User A cannot access User B's conversations or tasks - VERIFIED: 5/5 isolation tests passed (scripts/verify_isolation.py)
- [ ] T418 Test conversation persistence: History survives page refresh and browser restart
- [ ] T419 Test concurrent requests: Multiple simultaneous messages handled correctly
- [ ] T420 Test AI timeout: User message preserved, friendly error returned
```

## Response snapshot

Created comprehensive automated test scripts and manual test procedures for end-to-end validation of the AI chatbot feature.

### T416: Complete Workflow Test (Automated)

**Created**: `scripts/test_complete_workflow.py`

**Features**:
- Automated 6-step workflow test: Create → View → Complete → Verify → Delete → Verify
- JWT token authentication
- Conversation ID tracking
- Task ID extraction from assistant responses
- Tool call verification
- Color-coded console output (green/red/yellow/blue)
- Detailed error reporting

**Test Flow**:
1. Create task: "Add a task to buy groceries for the test"
2. View tasks: "Show my tasks" (verify task appears)
3. Complete task: "Mark task {id} as done"
4. Verify completion: Check task status
5. Delete task: "Delete task {id}"
6. Verify deletion: Confirm task no longer in list

**Usage**:
```bash
export AUTH_TOKEN='your_jwt_token'
python scripts/test_complete_workflow.py
```

### T418: Conversation Persistence Test (Manual)

**Created**: `scripts/T418_MANUAL_TEST_GUIDE.md`

**Features**:
- Quick reference guide (10-minute test)
- Part A: Page refresh persistence (F5 reload)
- Part B: Browser restart persistence (close/reopen)
- Troubleshooting section with common issues
- localStorage verification commands
- Database query examples
- Test report template

**Test Scenarios**:
- Page refresh preserves messages and context
- Browser restart restores conversation automatically
- conversation_id persists in localStorage
- Assistant maintains context across sessions

**Why Manual**: Requires browser interaction (F5, close/reopen) that cannot be automated without Selenium/Playwright.

### T419: Concurrent Requests Test (Automated)

**Created**: `scripts/test_concurrent_requests.py`

**Features**:
- Two test modes: Threading (synchronous) and Async (truly concurrent)
- Sends 5 concurrent requests to same conversation
- Verifies optimistic locking prevents race conditions
- Confirms all requests eventually succeed (with automatic retries)
- Checks for data loss or corruption
- Performance metrics (elapsed time, average time per request)

**Test Flow**:
1. Create initial conversation
2. Send 5 concurrent "Add task concurrent-{i}" messages
3. Analyze results (success rate, conflicts, timing)
4. Verify data integrity (all 5 tasks created)

**Threading Test**: Uses ThreadPoolExecutor for concurrent synchronous requests
**Async Test**: Uses aiohttp and asyncio for truly asynchronous requests

**Usage**:
```bash
export AUTH_TOKEN='your_jwt_token'
python scripts/test_concurrent_requests.py
```

### T420: AI Timeout Test (Automated)

**Created**: `scripts/test_ai_timeout.py`

**Features**:
- Two test modes:
  1. Full test (requires backend modification to simulate timeout)
  2. Frontend behavior test (no backend modification)
- Backend setup instructions included
- Verifies 503 error with friendly message
- Checks message preservation in database
- Tests conversation recovery after timeout

**Test Flow**:
1. Create initial conversation (should work normally)
2. Send message that triggers timeout (6-second delay)
3. Verify 503 Service Unavailable response
4. Remove timeout simulation and restart backend
5. Verify conversation recovered and subsequent requests work
6. Check message preservation in conversation history

**Backend Setup** (for full test):
```python
# Add to backend/api/chat.py before AI agent call
import time
time.sleep(6)  # Simulate 6-second delay (exceeds 5-second timeout)
```

**Usage**:
```bash
export AUTH_TOKEN='your_jwt_token'
python scripts/test_ai_timeout.py
```

### Tasks.md Updates

Updated task status to reflect test readiness:
- T416: TEST READY - Automated script created
- T418: TEST READY - Manual test guide created
- T419: TEST READY - Automated script created
- T420: TEST READY - Automated script created

### Common Features Across All Scripts

**Authentication**:
- JWT token from environment variable or script constant
- Clear error messages if token missing

**Output Formatting**:
- ANSI color codes (green=success, red=error, yellow=warning, blue=info)
- Step-by-step progress reporting
- Detailed error messages with context

**Error Handling**:
- Try-catch blocks with traceback
- Non-zero exit codes on failure
- Clear failure reporting

**Configuration**:
- BASE_URL configurable (defaults to http://localhost:8000)
- Timeout values configurable
- Number of concurrent requests configurable (T419)

## Outcome

- ✅ Impact: Created comprehensive automated test suite for end-to-end validation. T416, T419, and T420 have executable Python scripts with detailed output and error handling. T418 has a quick reference manual test guide. All tests are ready for execution to validate the complete AI chatbot workflow.
- 🧪 Tests: T416 (complete workflow), T418 (conversation persistence), T419 (concurrent requests), T420 (AI timeout) - all test procedures created and documented
- 📁 Files: scripts/test_complete_workflow.py, scripts/test_concurrent_requests.py, scripts/test_ai_timeout.py, scripts/T418_MANUAL_TEST_GUIDE.md, specs/001-ai-chatbot-mcp/tasks.md (updated)
- 🔁 Next prompts: Execute test scripts with valid JWT token: `export AUTH_TOKEN='token' && python scripts/test_complete_workflow.py`. Perform manual T418 test following the guide. Review test results and mark tasks complete in tasks.md.
- 🧠 Reflection: Automated testing approach provides repeatable validation with clear pass/fail criteria. Manual test for T418 is necessary due to browser interaction requirements. All scripts include comprehensive error handling and detailed output for debugging. Test suite enables rapid validation of core functionality.

## Evaluation notes (flywheel)

- Failure modes observed: None during script creation. Scripts include error handling for common failures (authentication, network, timeout, data corruption).
- Graders run and results (PASS/FAIL): Scripts created but not yet executed. Awaiting JWT token and test execution.
- Prompt variant (if applicable): /sp.implement with specific end-to-end validation tasks (T416-T420)
- Next experiment (smallest change to try): Add pytest integration for test scripts to enable `pytest scripts/` execution. Consider adding GitHub Actions workflow to run tests automatically on PR. Add test result reporting (JSON output) for CI/CD integration.
