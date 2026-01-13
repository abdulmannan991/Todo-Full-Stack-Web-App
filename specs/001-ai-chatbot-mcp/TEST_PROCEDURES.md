# End-to-End Test Procedures: AI-Powered Todo Chatbot

**Feature**: 001-ai-chatbot-mcp
**Date**: 2026-01-12
**Purpose**: Manual test procedures for T416-T420 validation

---

## Prerequisites

Before running these tests:

1. **Backend Server Running**: `uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload`
2. **Frontend Server Running**: `npm run dev` (Next.js on http://localhost:3000)
3. **Database Connected**: Neon PostgreSQL connection active
4. **User Account**: Valid test user account created and authenticated
5. **Browser**: Chrome/Firefox with DevTools available

---

## T416: Complete Workflow Test (Create → View → Complete → Delete)

**Objective**: Verify the entire task lifecycle works correctly through natural language chat.

### Test Steps

#### Step 1: Create Task
1. Navigate to http://localhost:3000/assistant
2. Ensure you're logged in (check for JWT token in localStorage: `auth_token`)
3. Send message: `"Add a task to buy groceries"`
4. **Expected Result**:
   - Assistant responds with confirmation (e.g., "Task 'Buy groceries' has been added.")
   - Tool call transparency shows `➕ Creating task`
   - Expandable details show task ID and arguments

#### Step 2: View Tasks
1. Send message: `"Show my tasks"` or `"List all my tasks"`
2. **Expected Result**:
   - Assistant lists all tasks including the newly created one
   - Tool call shows `📋 Listing tasks`
   - Task appears with correct title and status (pending)

#### Step 3: Complete Task
1. Send message: `"Mark task [ID] as done"` (use actual task ID from Step 2)
   - Alternative: `"Complete the groceries task"`
2. **Expected Result**:
   - Assistant confirms task completion
   - Tool call shows `✅ Completing task`
   - Task status updated to "completed"

#### Step 4: Verify Completion
1. Send message: `"Show my tasks"`
2. **Expected Result**:
   - Task appears with status "completed"
   - Or assistant indicates task is done

#### Step 5: Delete Task
1. Send message: `"Delete task [ID]"` (use actual task ID)
   - Alternative: `"Remove the groceries task"`
2. **Expected Result**:
   - Assistant confirms deletion
   - Tool call shows `🗑️ Deleting task`

#### Step 6: Verify Deletion
1. Send message: `"Show my tasks"`
2. **Expected Result**:
   - Deleted task no longer appears in the list
   - Or assistant indicates no tasks found

### Success Criteria
- ✅ All 6 steps complete without errors
- ✅ Each operation confirmed by assistant
- ✅ Tool calls visible and accurate
- ✅ Database reflects all changes (verify with direct query if needed)

### Failure Scenarios to Check
- ❌ Task not created (check backend logs for errors)
- ❌ Task not visible in list (check user_id filtering)
- ❌ Task not marked complete (check optimistic locking)
- ❌ Task not deleted (check user_id authorization)

---

## T418: Conversation Persistence Test

**Objective**: Verify conversation history survives page refresh and browser restart.

### Test Steps

#### Part A: Page Refresh Persistence

1. **Initial Setup**:
   - Navigate to http://localhost:3000/assistant
   - Ensure logged in
   - Send message: `"Add a task to test persistence"`
   - Wait for assistant response
   - Note the conversation_id in localStorage: `flow_assistant_conversation_id`

2. **Page Refresh**:
   - Press `F5` or click browser refresh button
   - Wait for page to reload

3. **Verification**:
   - **Expected Result**:
     - Previous messages still visible in chat interface
     - Conversation continues from same context
     - conversation_id unchanged in localStorage
     - Can send new messages and receive responses

4. **Context Verification**:
   - Send message: `"What task did I just create?"`
   - **Expected Result**:
     - Assistant remembers the "test persistence" task
     - Response references previous conversation

#### Part B: Browser Restart Persistence

1. **Initial Setup**:
   - Navigate to http://localhost:3000/assistant
   - Send message: `"Add a task to test browser restart"`
   - Wait for assistant response
   - Note the conversation_id in localStorage

2. **Browser Restart**:
   - Close browser completely (all windows/tabs)
   - Reopen browser
   - Navigate to http://localhost:3000/assistant
   - Log in if session expired

3. **Verification**:
   - **Expected Result**:
     - Previous conversation restored automatically
     - All messages from before restart visible
     - conversation_id matches the one from before restart
     - Can continue conversation seamlessly

4. **Context Verification**:
   - Send message: `"Show my tasks"`
   - **Expected Result**:
     - Assistant lists tasks including "test browser restart"
     - Conversation context maintained

### Success Criteria
- ✅ Page refresh preserves all messages
- ✅ Browser restart preserves conversation
- ✅ conversation_id persists in localStorage
- ✅ Assistant maintains context across sessions
- ✅ No duplicate messages after reload

### Failure Scenarios to Check
- ❌ Messages disappear after refresh (check localStorage)
- ❌ New conversation started after restart (check conversation loading logic)
- ❌ Context lost (check history loading in backend)
- ❌ Duplicate messages (check message deduplication)

---

## T419: Concurrent Requests Test

**Objective**: Verify multiple simultaneous messages are handled correctly with optimistic locking.

### Test Steps

#### Setup: Open Browser DevTools
1. Navigate to http://localhost:3000/assistant
2. Open DevTools (F12) → Console tab
3. Prepare to send multiple requests simultaneously

#### Test 1: Rapid Sequential Messages

1. **Send Messages Quickly**:
   - Type and send: `"Add task 1"`
   - Immediately type and send: `"Add task 2"`
   - Immediately type and send: `"Add task 3"`
   - (Send within 1-2 seconds of each other)

2. **Expected Result**:
   - All three messages appear in chat
   - All three assistant responses appear
   - All three tasks created successfully
   - No 409 conflict errors visible to user
   - Backend may retry on conflicts (check logs)

#### Test 2: Programmatic Concurrent Requests

1. **Run in DevTools Console**:
   ```javascript
   // Simulate concurrent requests
   const sendConcurrent = async () => {
     const promises = [
       fetch('http://localhost:8000/api/chat', {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json',
           'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
         },
         body: JSON.stringify({
           conversation_id: parseInt(localStorage.getItem('flow_assistant_conversation_id')),
           message: 'Add task concurrent 1'
         })
       }),
       fetch('http://localhost:8000/api/chat', {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json',
           'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
         },
         body: JSON.stringify({
           conversation_id: parseInt(localStorage.getItem('flow_assistant_conversation_id')),
           message: 'Add task concurrent 2'
         })
       }),
       fetch('http://localhost:8000/api/chat', {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json',
           'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
         },
         body: JSON.stringify({
           conversation_id: parseInt(localStorage.getItem('flow_assistant_conversation_id')),
           message: 'Add task concurrent 3'
         })
       })
     ];

     const results = await Promise.all(promises);
     console.log('All requests completed:', results.map(r => r.status));
   };

   sendConcurrent();
   ```

2. **Expected Result**:
   - All requests return 200 OK (after retries)
   - No 409 errors in final responses
   - Backend logs may show 409 conflicts with automatic retries
   - All tasks created successfully
   - Conversation version incremented correctly

#### Test 3: Check Backend Logs

1. **Review Server Logs**:
   - Look for `409 Conflict` responses
   - Verify retry logic triggered
   - Confirm optimistic locking working

2. **Expected Log Pattern**:
   ```
   INFO: POST /api/chat - 409 Conflict (version mismatch)
   INFO: Retrying request (attempt 1/3)
   INFO: POST /api/chat - 200 OK
   ```

### Success Criteria
- ✅ All concurrent requests eventually succeed
- ✅ No data loss or corruption
- ✅ Optimistic locking prevents race conditions
- ✅ Automatic retry handles conflicts gracefully
- ✅ User sees no errors (retries are transparent)

### Failure Scenarios to Check
- ❌ 409 errors shown to user (should be retried automatically)
- ❌ Messages lost or duplicated
- ❌ Conversation version not incremented
- ❌ Database deadlocks or timeouts

---

## T420: AI Timeout Test

**Objective**: Verify user message is preserved and friendly error returned when AI times out.

### Test Steps

#### Setup: Simulate Slow AI Response

**Option 1: Mock Slow Response (Recommended)**

1. **Temporarily Modify Backend** (backend/api/chat.py):
   ```python
   # Add before AI agent call (around line 150)
   import time
   time.sleep(6)  # Simulate 6-second delay (exceeds 5-second timeout)
   ```

2. **Restart Backend Server**

**Option 2: Network Throttling**

1. Open DevTools → Network tab
2. Set throttling to "Slow 3G"
3. This may cause timeout if AI service is slow

#### Test Execution

1. **Send Message**:
   - Navigate to http://localhost:3000/assistant
   - Send message: `"Add a task to test timeout"`
   - Wait for response

2. **Expected Result**:
   - Loading indicator shows for ~5 seconds
   - Error message appears: "The AI assistant is temporarily unavailable. Please try again in a moment."
   - Error displayed with blue styling (503 error type)
   - Helper text: "The assistant will be back shortly. You can try sending your message again."
   - User message is preserved in chat history

3. **Verify Message Preservation**:
   - Check chat interface: user message should still be visible
   - Backend should have saved user message to database
   - Conversation should be in valid state

4. **Retry After Timeout**:
   - Remove the `time.sleep(6)` line from backend
   - Restart backend server
   - Send message: `"Show my tasks"`
   - **Expected Result**:
     - Request succeeds normally
     - Assistant responds without timeout
     - Previous timeout didn't corrupt conversation

#### Test Database State

1. **Check Message Table**:
   ```sql
   SELECT * FROM message
   WHERE conversation_id = [your_conversation_id]
   ORDER BY created_at DESC
   LIMIT 5;
   ```

2. **Expected Result**:
   - User message "Add a task to test timeout" is saved
   - No assistant response for that message (timeout occurred)
   - Subsequent messages work normally

### Success Criteria
- ✅ Timeout occurs after 5 seconds
- ✅ Friendly error message displayed (503 style)
- ✅ User message preserved in chat and database
- ✅ Conversation remains in valid state
- ✅ Subsequent requests work normally
- ✅ No data corruption or orphaned records

### Failure Scenarios to Check
- ❌ Request hangs indefinitely (timeout not working)
- ❌ Generic error message (should be friendly 503 message)
- ❌ User message lost from chat
- ❌ Conversation corrupted (can't send new messages)
- ❌ Database transaction not rolled back properly

---

## Test Reporting Template

After completing each test, document results:

```markdown
## Test Results: [Test ID]

**Date**: YYYY-MM-DD
**Tester**: [Your Name]
**Environment**:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Database: Neon PostgreSQL

### Test Outcome
- [ ] PASS - All success criteria met
- [ ] FAIL - One or more criteria not met
- [ ] BLOCKED - Cannot complete test (explain why)

### Observations
[Describe what happened during the test]

### Issues Found
[List any bugs, unexpected behavior, or edge cases discovered]

### Screenshots/Logs
[Attach relevant screenshots or log excerpts]

### Recommendations
[Suggest fixes or improvements if test failed]
```

---

## Automated Test Script (Optional)

For T416, you can create an automated test script:

```python
# tests/e2e/test_complete_workflow.py
import requests
import time

BASE_URL = "http://localhost:8000"
TOKEN = "your_jwt_token_here"

def test_complete_workflow():
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    # Step 1: Create task
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"conversation_id": None, "message": "Add a task to buy groceries"},
        headers=headers
    )
    assert response.status_code == 200
    conversation_id = response.json()["conversation_id"]
    print(f"✓ Task created (conversation: {conversation_id})")

    # Step 2: List tasks
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={"conversation_id": conversation_id, "message": "Show my tasks"},
        headers=headers
    )
    assert response.status_code == 200
    assert "groceries" in response.json()["message"]["content"].lower()
    print("✓ Task listed")

    # Step 3: Complete task (extract task ID from response)
    # ... continue with remaining steps

    print("✅ Complete workflow test PASSED")

if __name__ == "__main__":
    test_complete_workflow()
```

---

## Notes

- **T417 (User Isolation)**: Already verified with `scripts/verify_isolation.py` - 5/5 tests passed
- **Browser Compatibility**: Test on Chrome, Firefox, and Safari
- **Mobile Testing**: Test on mobile devices for responsive behavior
- **Performance**: Monitor response times during tests
- **Error Logs**: Always check backend logs for detailed error information

---

## Quick Test Checklist

Use this for rapid validation:

- [ ] T416: Create → View → Complete → Delete workflow works
- [ ] T418: Page refresh preserves conversation
- [ ] T418: Browser restart preserves conversation
- [ ] T419: Concurrent requests handled correctly
- [ ] T420: AI timeout shows friendly error
- [ ] T420: User message preserved after timeout
- [ ] All error messages are user-friendly (T402-T404)
- [ ] Tool calls visible and accurate
- [ ] No console errors in browser DevTools
- [ ] Backend logs show no critical errors
