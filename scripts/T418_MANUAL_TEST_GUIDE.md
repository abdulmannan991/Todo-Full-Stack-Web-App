# T418: Conversation Persistence - Quick Test Guide

**Objective**: Verify conversation history survives page refresh and browser restart.

---

## Prerequisites

- Backend server running: http://localhost:8000
- Frontend server running: http://localhost:3000
- Valid user account and logged in
- Browser DevTools available (F12)

---

## Part A: Page Refresh Test (5 minutes)

### Steps

1. **Navigate to Assistant**
   - Open http://localhost:3000/assistant
   - Ensure you're logged in

2. **Send Initial Message**
   - Type: `"Add a task to test page refresh"`
   - Wait for assistant response
   - **Note the conversation_id**:
     - Open DevTools (F12) → Console
     - Run: `localStorage.getItem('flow_assistant_conversation_id')`
     - Write down the ID: ___________

3. **Refresh Page**
   - Press `F5` or click browser refresh button
   - Wait for page to reload

4. **Verify Persistence**
   - ✅ Previous messages still visible?
   - ✅ Conversation continues from same context?
   - ✅ conversation_id unchanged in localStorage?
   - ✅ Can send new messages?

5. **Test Context Maintenance**
   - Send: `"What task did I just create?"`
   - ✅ Assistant remembers the "test page refresh" task?

### Expected Result

All checkboxes above should be ✅. If any fail, note which step failed.

---

## Part B: Browser Restart Test (5 minutes)

### Steps

1. **Send Message**
   - Type: `"Add a task to test browser restart"`
   - Wait for assistant response
   - **Note the conversation_id** (same as Part A if continuing)

2. **Close Browser Completely**
   - Close ALL browser windows and tabs
   - Wait 5 seconds

3. **Reopen Browser**
   - Open browser
   - Navigate to http://localhost:3000/assistant
   - Log in if session expired

4. **Verify Persistence**
   - ✅ Previous conversation restored automatically?
   - ✅ All messages from before restart visible?
   - ✅ conversation_id matches the one from before restart?
   - ✅ Can continue conversation seamlessly?

5. **Test Context Maintenance**
   - Send: `"Show my tasks"`
   - ✅ Assistant lists tasks including "test browser restart"?

### Expected Result

All checkboxes above should be ✅. If any fail, note which step failed.

---

## Troubleshooting

### Messages Disappear After Refresh

**Check**:
- DevTools → Application → Local Storage → http://localhost:3000
- Verify `flow_assistant_conversation_id` exists
- If missing, conversation persistence is broken

**Fix**:
- Check frontend/app/assistant/page.tsx lines 36-56 (localStorage logic)
- Verify conversation_id is being saved after first message

### New Conversation Started After Restart

**Check**:
- localStorage cleared on browser close?
- Session expired (requires re-login)?
- conversation_id changed?

**Fix**:
- Ensure localStorage persists across sessions
- Check browser settings (don't clear on exit)
- Verify conversation loading logic in useEffect

### Context Lost (Assistant Doesn't Remember)

**Check**:
- Backend logs for conversation history loading
- GET `/api/conversations/{id}/messages` returns 200 OK?
- Messages exist in database?

**Fix**:
- Check backend/api/chat.py conversation history loading (line 325)
- Verify sliding window history (last 50 messages)
- Check database: `SELECT * FROM message WHERE conversation_id = ?`

---

## Quick Verification Commands

### Check localStorage (Browser Console)
```javascript
// Get conversation ID
localStorage.getItem('flow_assistant_conversation_id')

// Clear conversation (for testing)
localStorage.removeItem('flow_assistant_conversation_id')

// Check all localStorage
console.log(localStorage)
```

### Check Backend Logs
```bash
# Watch for conversation loading
tail -f backend_output.log | grep -E "(conversation|history|messages)"
```

### Check Database
```sql
-- Check conversation exists
SELECT * FROM conversation WHERE id = [your_conversation_id];

-- Check messages in conversation
SELECT id, role, content, created_at
FROM message
WHERE conversation_id = [your_conversation_id]
ORDER BY created_at DESC
LIMIT 10;
```

---

## Test Report Template

```
T418: Conversation Persistence Test
Date: ___________
Tester: ___________

Part A: Page Refresh
- [ ] PASS - Messages persist after F5
- [ ] PASS - Context maintained
- [ ] PASS - Can send new messages
- [ ] FAIL - [Describe issue]

Part B: Browser Restart
- [ ] PASS - Conversation restored
- [ ] PASS - Context maintained
- [ ] PASS - Can continue conversation
- [ ] FAIL - [Describe issue]

Notes:
[Any observations or issues]
```

---

## Success Criteria

**PASS**: Both Part A and Part B complete successfully with all checkboxes ✅

**FAIL**: Any checkbox fails in either part

---

## Estimated Time

- Part A: 5 minutes
- Part B: 5 minutes
- Total: 10 minutes
