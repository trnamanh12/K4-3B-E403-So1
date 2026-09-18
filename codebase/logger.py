import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

# Đảm bảo mã hóa UTF-8 an toàn trên Windows console
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Đường dẫn mặc định lưu trace log
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TRACE_LOG_PATH = PROJECT_ROOT / "eval" / "trace_log.json"

class TraceLogger:
    """
    Cơ chế Logging thô: Bắt buộc lưu vết vào file (ví dụ eval/trace_log.json)
    gồm 3 trường bắt buộc:
      1. timestamp (ISO-8601)
      2. raw_prompt (toàn bộ prompt gửi tới LLM)
      3. raw_response (nội dung text thô do LLM trả về)
    Kèm các trường siêu dữ liệu để ban giám khảo đối soát kỹ thuật.
    """
    def __init__(self, log_file_path: Optional[Path] = None):
        self.log_file_path = Path(log_file_path or DEFAULT_TRACE_LOG_PATH)
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        raw_prompt: str,
        raw_response: str,
        step_name: str = "LLM_CALL",
        model: str = "gemini-2.5-flash",
        latency_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        echo_terminal: bool = True
    ) -> Dict[str, Any]:
        """
        Ghi một bản ghi gọi AI vào trace log.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        
        record = {
            "timestamp": now_iso,
            "raw_prompt": raw_prompt,
            "raw_response": raw_response,
            "step_name": step_name,
            "model": model,
            "latency_ms": latency_ms,
            "metadata": metadata or {}
        }

        # Lưu dạng JSON Array hoặc append JSON lines
        # Để dễ đọc và giám khảo inspect, lưu dạng JSON list
        existing_records = []
        if self.log_file_path.exists():
            try:
                with open(self.log_file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        existing_records = json.loads(content)
                        if not isinstance(existing_records, list):
                            existing_records = [existing_records]
            except Exception:
                existing_records = []

        existing_records.append(record)

        with open(self.log_file_path, "w", encoding="utf-8") as f:
            json.dump(existing_records, f, ensure_ascii=False, indent=2)

        if echo_terminal:
            try:
                print(f"\n[TRACE_LOG] [{record['timestamp']}] Step: {step_name} | Model: {model} | Latency: {latency_ms}ms")
                print(f"--- RAW_PROMPT (Length: {len(raw_prompt)} chars) ---")
                prompt_preview = raw_prompt if len(raw_prompt) < 300 else raw_prompt[:300] + "... [TRUNCATED]"
                print(prompt_preview)
                print(f"--- RAW_RESPONSE (Length: {len(raw_response)} chars) ---")
                resp_preview = raw_response if len(raw_response) < 300 else raw_response[:300] + "... [TRUNCATED]"
                print(resp_preview)
                print("------------------------------------------------------------\n")
            except Exception:
                pass

        return record

# Singleton instance mặc định
logger = TraceLogger()
