import sys
import os
import http.server
import socketserver
import json
import urllib.parse
from pathlib import Path

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Thêm codebase vào sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CODEBASE_DIR = PROJECT_ROOT / "codebase"
STATIC_DIR = CODEBASE_DIR / "static"
sys.path.append(str(CODEBASE_DIR))

import mimetypes
mimetypes.init()
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("application/javascript", ".jsx")
mimetypes.add_type("text/css", ".css")

from core_decision import VLearnTutorCore, parse_student_question_turn
from logger import logger
from rag_indexer import indexer

PORT = 8080

# Mẫu slide nền cho toàn bộ 20 Golden Cases và các trang quan trọng
SAMPLE_SLIDES = {
    "Trang 1": {
        "title": "Day 1 — LLM Foundation & AI Product Thinking",
        "content": "Chào mừng các bạn đến với khoá học AI Product Hackathon.\nNội dung chính Day 1: Xây dựng nền tảng tư duy sản phẩm AI, hiểu giới hạn của mô hình ngôn ngữ lớn và phương pháp đo lường chất lượng giải pháp.\nLưu ý quy chế lớp học: Lộ trình từ CP1 đến CP6 kết thúc lúc 21:00. Mọi vấn đề xin lùi hạn, điểm danh cần liên hệ TA.",
        "course": "K4P1"
    },
    "Trang 2": {
        "title": "Day 1 — Tổng quan kiến trúc & Chủ đề chính",
        "content": "Day 1 giới thiệu các chủ đề chính: Tổng quan LLM Foundation, cách hoạt động của Transformer, hệ sinh thái API của các nhà cung cấp lớn và thực hành gọi API.\nBảo mật hệ thống AI và phòng chống rủi ro rò rỉ dữ liệu qua Prompt Injection.",
        "course": "K4P1"
    },
    "Trang 5": {
        "title": "Thực hành gọi API đa nền tảng & Google AI Studio",
        "content": "Thực hành gọi API đa nền tảng: Học viên kết nối và sử dụng API từ 3 nhà cung cấp hàng đầu là OpenAI, Google Gemini và Anthropic.\nGoogle AI Studio cung cấp gói Gemini Free Tier với hạn mức khoảng 1.500 requests mỗi ngày, phục vụ tốt cho mục đích thực hành và kiểm thử đồ án.",
        "course": "K4P1"
    },
    "Trang 10": {
        "title": "Prompt Engineering Fundamentals",
        "content": "Trang 10: Giới thiệu kỹ thuật Zero-shot và Few-shot Prompting. Cách thiết kế System Prompt và tinh chỉnh chỉ thị để mô hình phản hồi nhất quán, tránh dài dòng.",
        "course": "K4P1"
    },
    "Trang 12": {
        "title": "AI Agent & Kiểm thử tự động với Python",
        "content": "Xây dựng AI Agent và kiểm thử tự động với thư viện Python. Thiết kế các tool call, routing quyết định và quy trình đánh giá chất lượng phản hồi.",
        "course": "K4P1"
    },
    "Trang 15": {
        "title": "Cài đặt môi trường & Thư viện SDK",
        "content": "Hướng dẫn cài đặt môi trường lập trình Python cho AI. Lỗi thường gặp khi thiếu thư viện: ModuleNotFoundError: No module named 'google.genai'. Cách khắc phục: chạy lệnh 'pip install google-genai'.",
        "course": "K4P1"
    },
    "Trang 21": {
        "title": "Kiến trúc RNN so với Transformer",
        "content": "RNN xử lý tuần tự từng từ một nên chậm và khó bắt phụ thuộc xa.\nTransformer sử dụng cơ chế Self-Attention cho phép xử lý toàn bộ các từ cùng một lúc (song song).",
        "course": "K4P1"
    },
    "Trang 22": {
        "title": "Cơ chế Self-Attention & Xử lý song song",
        "content": "Cơ chế Self-Attention tính toán ma trận tương quan giữa tất cả các token đồng thời, giúp mô hình nắm bắt ngữ cảnh toàn câu mà không cần duyệt từng từ một cách tuần tự.",
        "course": "K4P1"
    },
    "Trang 23": {
        "title": "Lab Task 2 — Gọi Gemini 2.5 Flash SDK",
        "content": "Task 2: Hoàn thành hàm call_gemini để gọi model Gemini 2.5 Flash sử dụng Google GenAI SDK mới nhất với gói thư viện google-genai.",
        "course": "K4P1"
    },
    "Trang 38": {
        "title": "Quy trình huấn luyện LLM: Pre-training vs SFT",
        "content": "Giai đoạn 1: Pre-training là đọc cả thư viện hàng nghìn tỷ token để học ngữ pháp và tri thức tổng quát.\nGiai đoạn 2: SFT (Supervised Fine-Tuning) dạy mô hình học cách hội thoại và tuân thủ chỉ thị của con người.",
        "course": "K4P1"
    },
    "Trang 39": {
        "title": "Kiến trúc RAG (Retrieval-Augmented Generation)",
        "content": "RAG (Retrieval-Augmented Generation) là kiến trúc kết hợp giữa truy xuất tài liệu từ kho dữ liệu bên ngoài và mô hình ngôn ngữ lớn để trả lời chính xác, giảm thiểu hallucination.",
        "course": "K4P1"
    },
    "Trang 61": {
        "title": "Tối ưu hoá Transformer: RoPE & GQA",
        "content": "Sự tiến hoá của kiến trúc Transformer hiện đại: áp dụng Rotary Position Embedding (RoPE) để mã hoá vị trí tương đối trong không gian quay vector, kết hợp Grouped-Query Attention (GQA) giúp giảm mạnh bộ nhớ KV cache khi suy luận.",
        "course": "K4P1"
    },
    "Trang 63": {
        "title": "Khái niệm Multimodal (Đa phương thức)",
        "content": "Multimodal (Đa phương thức): Mô hình hiện đại không chỉ xử lý văn bản mà còn có khả năng hiểu trực tiếp hình ảnh, biểu đồ PDF, âm thanh và video thay vì chỉ làm việc với chữ thuần tuý.",
        "course": "K4P1"
    },
    "Trang 68": {
        "title": "Chi phí Token & Bảng giá các dòng Model",
        "content": "Mỗi model LLM (GPT-4, Gemini, Claude, DeepSeek) có chi phí token và tốc độ xử lý khác nhau. Cần cân đối giữa chất lượng câu trả lời và chi phí API để tối ưu sản phẩm.",
        "course": "K4P1"
    },
    "Trang 76": {
        "title": "Sampling Parameters: Temperature & Top-P",
        "content": "Temperature điều chỉnh độ phẳng của phân phối xác suất softmax (làm câu trả lời sáng tạo hơn hoặc xác định hơn).\nTop-P (Nucleus Sampling) giới hạn tập hợp các token tích lũy có tổng xác suất đạt ngưỡng P trước khi lấy mẫu.\nTrong bài giảng, model được ví như một số tổng đài mà ứng dụng gọi tới để nhận phản hồi.",
        "course": "K4P1"
    }
}

# Tải trước toàn bộ Slide từ SQLite FTS5 (58 trang PDF) và hợp nhất với SAMPLE_SLIDES
def get_combined_slides():
    try:
        indexer.build_index()
        all_slides = indexer.get_all_slides_dict()
        # Ưu tiên các slide golden set mẫu để đảm bảo test trên UI chuẩn xác
        all_slides.update(SAMPLE_SLIDES)
        return all_slides
    except Exception as e:
        print(f"[WARN] Lỗi tải slide từ indexer: {e}")
        return SAMPLE_SLIDES

COMBINED_SLIDES = get_combined_slides()

# Shared core instance
global_tutor = VLearnTutorCore()

class VLearnApiHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/slides":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(COMBINED_SLIDES, ensure_ascii=False).encode("utf-8"))
            return

        elif path == "/api/search":
            query_params = urllib.parse.parse_qs(parsed_url.query)
            q = query_params.get("q", [""])[0].strip()
            source_type = query_params.get("type", [None])[0]
            top_k = int(query_params.get("top_k", ["5"])[0])
            
            results = indexer.search(q, top_k=top_k, source_type=source_type) if q else []
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(results, ensure_ascii=False).encode("utf-8"))
            return

        elif path == "/api/golden_set":
            golden_path = PROJECT_ROOT / "eval" / "golden_set.json"
            if golden_path.exists():
                with open(golden_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = []
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
            return

        elif path == "/api/traces":
            trace_path = PROJECT_ROOT / "eval" / "trace_log.json"
            if trace_path.exists():
                with open(trace_path, "r", encoding="utf-8") as f:
                    try:
                        traces = json.load(f)
                    except Exception:
                        traces = []
            else:
                traces = []
            # Trả về 30 lượt gọi gần nhất đảo ngược
            recent_traces = list(reversed(traces))[:30]
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "total_count": len(traces),
                "recent_traces": recent_traces
            }, ensure_ascii=False).encode("utf-8"))
            return

        # Phục vụ file tĩnh mặc định
        return super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(post_body)
            except Exception:
                data = {}

            question = data.get("question", "").strip()
            context_snippet = data.get("context_snippet", "").strip()
            page_ref = data.get("page_ref", "Trang 1").strip()
            turn_id = data.get("turn_id", "WEB_DEMO")
            session_id = data.get("session_id", "WEB_SESSION")

            try:
                result = global_tutor.execute_workflow(
                    student_question=question,
                    context_snippet=context_snippet,
                    page_ref=page_ref,
                    turn_id=turn_id,
                    session_id=session_id
                )
            except Exception as ex:
                import traceback
                traceback.print_exc()
                result = {
                    "turn_id": turn_id,
                    "session_id": session_id,
                    "student_question": question,
                    "context_snippet": context_snippet,
                    "page_ref": page_ref,
                    "final_status": "SERVER_ERROR",
                    "final_response": f"Lỗi xử lý từ máy chủ AI: {str(ex)}",
                    "citation": page_ref,
                    "pedagogic_move": "review_concept",
                    "decision_trace": []
                }

            # Lấy bản ghi trace log mới nhất để trả về cho UI inspect
            trace_path = PROJECT_ROOT / "eval" / "trace_log.json"
            latest_trace = None
            if trace_path.exists():
                try:
                    with open(trace_path, "r", encoding="utf-8") as f:
                        traces = json.load(f)
                        if traces:
                            latest_trace = traces[-1]
                except Exception:
                    pass

            result["latest_trace"] = latest_trace

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode("utf-8"))
            return

        self.send_error(404, "Endpoint not found")

def run_server():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), VLearnApiHandler) as httpd:
        print(f"🚀 VLearn Web Demo Server running at: http://localhost:{PORT}")
        print("Bấm Ctrl+C để dừng server.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nĐang dừng server...")

if __name__ == "__main__":
    run_server()
