# K4-3B-E403-So1

## 👥 Thành viên nhóm & Phân công vai trò

**Lớp:** 3B · **Phòng:** E403 · **Track:** A (VLearn Tutor)

| Họ và Tên | Mã Học Viên | Vai trò chính | Phần việc đảm nhiệm trong dự án |
|---|---|---|---|
| Trần Nam Anh | 2A202602901 | Trưởng nhóm / AI Engineer / Data |
| Hoàng Phong | 2A202602943 | Data Engineer | 
| Hoàng Anh Minh | 2A202602566 | UI / AI / Data  |
| Lê Trung Kiên | 2A202602748 | Back end  / AI / Data  |

**VLearn RAG**

Backend Python dùng OpenRouter embeddings (`liquid/lfm-2.5-embedding-350m:free`), Qdrant, BM25, citation theo nguồn và giao diện học viên.

- [Hướng dẫn cấu hình, ingest, retrieval, API và kiểm thử](RAG_SETUP.md)
- [Kế hoạch và thiết kế dữ liệu](RAG_DESIGN_PLAN.md)
- Cài đặt: `uv sync --python 3.12 --extra dev`
- Parse local: `.venv/bin/vlearn prepare`
- Mở giao diện: `.venv/bin/vlearn serve`

Thêm `OPENROUTER_API_KEY` vào `.env` để chạy embedding và trả lời bằng LLM. Dữ liệu khóa học và artifacts được giữ ngoài Git.
