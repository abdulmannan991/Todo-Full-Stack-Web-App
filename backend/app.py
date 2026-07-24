import sys
import traceback
from datetime import datetime

print(f"===== Application Startup at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} =====", flush=True)

try:
    from main import app
    print("[OK] Application loaded successfully!", flush=True)
except Exception as e:
    print(f"[ERROR] Failed to load application: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)
