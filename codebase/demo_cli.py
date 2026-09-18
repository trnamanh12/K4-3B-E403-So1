import sys
import os
from pathlib import Path

# Add codebase to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root / "codebase"))

from core_decision import VLearnTutorCore

def print_separator(title=""):
    print("\n" + "=" * 70)
    if title:
        print(f"  📌 {title}")
        print("=" * 70)

def display_workflow_result(test_num, title, page_ref, snippet, question, result):
    print_separator(f"KỊCH BẢN {test_num}: {title}")
    print(f"📖 Trang tài liệu: {page_ref}")
    print(f"📑 Đoạn trích dẫn: \"{snippet}\"")
    print(f"❓ Câu hỏi học viên: \"{question}\"")
    print("-" * 70)
    print("🔄 QUÁ TRÌNH XỬ LÝ THEO WORKFLOW:")
    for step in result["decision_trace"]:
        step_name = step["step"]
        out = step["output"]
        if step_name == "C_Quyet_dinh_1":
            print(f"  👉 [Quyết định 1 - C] Kiểm tra ngữ cảnh: {out.get('decision')} | Lý do: {out.get('reason')}")
        elif step_name == "G_Quyet_dinh_2":
            print(f"  👉 [Quyết định 2 - G] Kiểm tra hỗ trợ nguồn: {out.get('decision')} | Lý do: {out.get('reason')}")
        elif step_name == "J_AI_Generation":
            print(f"  👉 [AI Generation - J] Sinh nháp câu trả lời: \"{out}\"")
        elif step_name == "K_AI_Validator_Quyet_dinh_3":
            print(f"  👉 [Validator - K] Đối soát 100% tài liệu: {out.get('decision')} (Hallucination: {out.get('has_hallucination')})")

    print("-" * 70)
    status_icon = "🟢" if result["final_status"] == "GROUNDED" else "🟡"
    print(f"🎯 KẾT QUẢ HIỂN THỊ TRÊN UI ({status_icon} {result['final_status']}):")
    print(f"💬 Phản hồi học viên: {result['final_response']}")
    if result.get("citation"):
        print(f"📎 Trích dẫn nguồn xác thực: [{result['citation']}]")

def main():
    tutor = VLearnTutorCore()

    # 4 Kịch bản đại diện cho 4 nhánh rẽ trong flowchart
    scenarios = [
        {
            "num": 1,
            "title": "Happy Path — Câu hỏi rõ ràng, có đầy đủ căn cứ tài liệu",
            "page": "Trang 21",
            "snippet": "RNN xử lý tuần tự từng từ một nên chậm và khó bắt phụ thuộc xa. Transformer sử dụng cơ chế Self-Attention cho phép xử lý toàn bộ các từ cùng một lúc (song song).",
            "question": "RNN và Transformer khác nhau ở điểm cốt lõi nào?"
        },
        {
            "num": 2,
            "title": "Mơ hồ — Học viên bôi đen text rác hoặc câu hỏi quá vắn tắt",
            "page": "Trang 2",
            "snippet": "asds",
            "question": "asds"
        },
        {
            "num": 3,
            "title": "Ngoài thẩm quyền — Học viên hỏi về quy chế, xin lùi hạn deadline",
            "page": "Trang 1",
            "snippet": "Lộ trình AI Product Hackathon kết thúc CP4 lúc 21:00.",
            "question": "Nhóm em đang fix bug chưa kịp nộp, AI cho nhóm em xin lùi deadline thêm 2 tiếng được không?"
        },
        {
            "num": 4,
            "title": "Thiếu nguồn — Tài liệu hiện tại không đề cập đến nội dung câu hỏi",
            "page": "Trang 10",
            "snippet": "Trang 10: Giới thiệu kỹ thuật Zero-shot và Few-shot Prompting.",
            "question": "Slide 9 của bài hôm trước nói về nội dung gì vậy bạn?"
        }
    ]

    for s in scenarios:
        res = tutor.execute_workflow(
            student_question=s["question"],
            context_snippet=s["snippet"],
            page_ref=s["page"],
            turn_id=f"DEMO_{s['num']}"
        )
        display_workflow_result(s["num"], s["title"], s["page"], s["snippet"], s["question"], res)

    print_separator("KIỂM TRA BẰNG CHỨNG GHI VẾT (TRACE LOG)")
    log_file = project_root / "eval" / "trace_log.json"
    import json
    if log_file.exists():
        logs = json.load(open(log_file, encoding="utf-8"))
        print(f"✅ File trace log: {log_file}")
        print(f"✅ Tổng số lượt gọi AI đã ghi nhận: {len(logs)} lượt")
        latest = logs[-1]
        print(f"🕒 Lượt gọi mới nhất: {latest['timestamp']} | Step: {latest['step_name']} | Model: {latest['model']}")
        print(f"   Raw prompt length: {len(latest['raw_prompt'])} ký tự | Raw response length: {len(latest['raw_response'])} ký tự")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
