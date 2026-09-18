**Chạy VLearn RAG với OpenRouter**

Đã triển khai ingest PDF/Markdown, source store SQLite, chunking có offsets, OpenRouter embeddings, Qdrant, BM25 + RRF, reranking tùy chọn, ba decision gate, citation viewer, feedback và eval. Chạy các lệnh dưới đây từ thư mục gốc repository.

**1. Cài môi trường**

```bash
uv sync --python 3.12 --extra dev
```

Nếu không dùng `uv`, tạo virtualenv Python >=3.11 rồi cài `pip install -e '.[dev]'`. Các lệnh mẫu dùng `.venv/bin/` trên Linux/macOS; Windows dùng `.venv\Scripts\`.

**2. Cấu hình `.env`**

`.env.example` liệt kê toàn bộ tùy chọn. Dự án hiện đã có `.env`; thêm/sửa các dòng cần thiết, giữ các key cũ. Không commit `.env`.

```dotenv
OPENROUTER_API_KEY=<key-của-bạn>
OPENROUTER_EMBEDDING_MODEL=liquid/lfm-2.5-embedding-350m:free
OPENROUTER_CHAT_MODEL=google/gemini-2.5-flash
RAG_CHUNK_TOKENS=360
RAG_CHUNK_OVERLAP=40
```

Với Liquid, chương trình tự chọn tokenizer `LiquidAI/LFM2.5-Embedding-350M` và prefix `document: ` / `query: `. Chỉ tải tokenizer JSON, không tải model weights hay chạy remote model code. Tokenizer được cache trong `artifacts/tokenizers/`; hash được đưa vào snapshot để phát hiện thay đổi.

Model embedding này có giới hạn **512 token**, vector **1024 chiều** theo catalog. Chunk body tối đa 360 token; tiêu đề giới hạn riêng; trước khi gửi API chương trình kiểm tổng input, gồm prefix, title và special tokens. Không cắt ngầm câu hỏi hoặc tài liệu dài ở phía client.

**Điều kiện của model đã chọn:** OpenRouter công bố request và embedding thành công có thể được lưu và dùng huấn luyện Liquid. Data pack yêu cầu chỉ đưa phần tối thiểu vào công cụ AI ngoài. `prepare`, BM25 eval và xem nguồn chạy local; `index` gửi các chunk đủ điều kiện sang OpenRouter. Cân nhắc quy định pack trước khi chạy index corpus thật. [Thông tin model trên OpenRouter](https://openrouter.ai/liquid/lfm-2.5-embedding-350m:free).

Embedding và chat là hai model riêng. Model chat mặc định ở trên không phải model miễn phí; chỉ được gọi khi `ask`, eval e2e hoặc bật rerank. Có thể đổi `OPENROUTER_CHAT_MODEL` sang model hỗ trợ structured outputs trên OpenRouter.

Kiểm kết nối:

```bash
.venv/bin/vlearn doctor
.venv/bin/vlearn models
.venv/bin/vlearn smoke
```

`doctor` kiểm catalog và tokenizer, chỉ báo key có/không, không in key. `smoke` gửi hai câu tiếng Anh tự tạo để kiểm embedding; không dùng dữ liệu khóa học. `models` lấy catalog embedding hiện tại, không hardcode danh sách model.

Endpoint Liquid miễn phí chỉ khả dụng nếu data policy của tài khoản OpenRouter cho phép endpoint có thể dùng request để huấn luyện. Khi privacy settings chặn loại endpoint này, `smoke`/`index` trả thông báo cụ thể và không tự đổi model. Với dữ liệu khóa học, lựa chọn ưu tiên là giữ privacy settings hiện tại và dùng một embedding endpoint tương thích chính sách dữ liệu; chỉ bật tùy chọn training-data khi bạn đã quyết định việc đó phù hợp quy định của data pack.

**3. Parse và chunk tại máy**

```bash
mkdir -p artifacts
.venv/bin/vlearn prepare > artifacts/prepare.json
```

Đọc `snapshot_id` trong `artifacts/prepare.json`; có thể đặt biến dùng cho các lệnh tiếp theo:

```bash
rag_snapshot_id=$(.venv/bin/python -c 'import json; print(json.load(open("artifacts/prepare.json"))["snapshot_id"])')
```

Đầu ra:

```text
artifacts/
  sources.sqlite3
  sources/<sha256>.pdf|md
  tokenizers/
  snapshots/<snapshot_id>/
    manifest.jsonl
    source_units.jsonl
    chunks.jsonl
    parse_quality_report.json
```

File gốc được lưu bản có checksum để citation cũ không trỏ sang nội dung mới. SQLite là nguồn chuẩn; Qdrant chỉ index những chunk được phép dùng làm bằng chứng. Re-run với cùng input/config cho cùng snapshot và IDs.

Kết quả khảo sát/prepare hiện tại: **8 tài liệu, 58 trang, 700 đoạn transcript, 1.405 chunk, 1.238 chunk đủ điều kiện index**. Các con số chunk thay đổi khi model, tokenizer, mapping hoặc quy tắc review thay đổi.

**4. Rà soát chất lượng và quan hệ bài học**

Watermark chéo được bỏ khỏi text tìm kiếm; giữ raw text và bbox để đối chiếu. Số trang PDF và nhãn slide gốc lưu riêng. Các trang có hình lớn hoặc quá ít text bị loại khỏi evidence đến khi được review. 12 trang trong pack hiện tại bị đánh dấu có hình lớn; pipeline chưa tích hợp OCR/VLM tự động.

Transcript được tách theo ID, giữ heading, previous/next ID và marker `[không nghe rõ]`. Lời học viên/hoạt động lớp được nhận diện bằng dấu hiệu rõ ràng và loại khỏi evidence mặc định. Phân loại này là heuristic, vẫn cần audit các đoạn không ghi người nói.

Mặc định Day 1 gồm slide D1 và transcript 04; Day 2 gồm slide D2 và transcript 01, dựa trên định vị tin cậy cao trong README pack. Transcript 02/03/05/06 chưa tự đưa vào lesson-expanded retrieval; vẫn xem và chọn nguồn trực tiếp được. Để sửa mapping, sao chép `config/lesson_map.example.json`, chỉnh sau khi xác nhận rồi đặt `RAG_LESSON_MAP=<path>` và chạy lại prepare.

Review nguồn bằng JSON do người quản trị tạo, ví dụ **schema minh họa**:

```json
{
  "d2-slide-hackathon:p021": {
    "document_version": "<sha256 từ manifest>",
    "text": "<bản chép đã kiểm tra gồm cả sơ đồ nếu cần>",
    "evidence_eligible": true
  }
}
```

Đặt `RAG_REVIEW_FILE=<path>` rồi prepare lại. Text override phải được đối chiếu ảnh gốc; review cũ không dùng được nếu checksum tài liệu thay đổi. Trường `text` có thể bỏ nếu chỉ xác nhận text đã trích là đủ; hệ thống vẫn không suy ra nội dung của hình không được chép lại. Bbox cũ được bỏ khi thay text để tránh highlight sai tọa độ.

**5. Chạy baseline local trước khi embedding**

```bash
.venv/bin/vlearn search 'Temperature và top_p khác nhau thế nào?' \
  --snapshot "$rag_snapshot_id" --lesson day-1 --mode LESSON_EXPANDED --backend bm25

.venv/bin/python -m vlearn.evaluate retrieval \
  --snapshot "$rag_snapshot_id" --backend bm25
```

`eval/retrieval_cases.json` có 20 câu hỏi, 11 câu phát triển từ chatlog và ghi `source_turn_id`; nội dung đã điều chỉnh để kiểm nguồn đang có, không giữ nguyên số trang từ chatlog cũ. Đây là **dev set khởi đầu**, chưa phải held-out benchmark hoặc một tập gold đầy đủ mọi đoạn nguồn tương đương. Runner không đưa gold sources vào request retrieval.

Baseline BM25 đã đo: tìm được trang mục tiêu trong top 10 ở **19/20 case**, Recall@10 **0,95**, MRR@10 khoảng **0,768**. Chỉ số này chưa đánh giá embedding Liquid hoặc chất lượng câu trả lời LLM.

**6. Tạo vector index, đánh giá, rồi kích hoạt**

Sau khi đã có key và bảo đảm việc gửi corpus phù hợp quy định dữ liệu:

```bash
.venv/bin/vlearn index --snapshot "$rag_snapshot_id"

.venv/bin/python -m vlearn.evaluate retrieval \
  --snapshot "$rag_snapshot_id" --backend hybrid

.venv/bin/vlearn activate --snapshot "$rag_snapshot_id"
.venv/bin/vlearn status
```

Index dùng batch 32 input/request, retry 429/5xx và cache embedding trong SQLite theo model/revision/prefix/input. Lỗi giữa chừng không kích hoạt snapshot dở dang; chạy lại lệnh index để tiếp tục từ cache. Free endpoint có quota request theo ngày; khi hết quota, chương trình giữ toàn bộ vector đã hoàn tất và báo nguyên nhân cụ thể. Không tự đổi sang model khác khi provider lỗi.

Qdrant được tạo theo snapshot, tự xác định vector dimension từ response rồi kiểm thống nhất cho mọi batch và query. Khi đổi embedding model hoặc dimension/prefix, chạy prepare để tạo snapshot mới, index và eval trước khi activate. Nếu provider đổi model sau cùng một alias, tăng `OPENROUTER_EMBEDDING_REVISION`.

**7. Chạy giao diện và API**

```bash
.venv/bin/vlearn serve
```

Mở **http://127.0.0.1:8000**. Chọn tài liệu → trang/đoạn → bôi đen nội dung → hỏi. Citation mở cả phần text được dẫn và PDF đúng trang nếu nguồn là slide. Feedback được lưu theo trace ID.

- `STRICT_SOURCE`: chỉ đoạn được chọn, hoặc cả source unit nếu không chọn offsets; không tự mở rộng sang nguồn khác.
- `LESSON_EXPANDED`: dense + BM25 trong cùng lesson/snapshot, gộp bằng RRF, giữ selection làm anchor. Đặt `RAG_RERANK=true` nếu muốn rerank bằng model chat và đo lại latency/chi phí.
- Mọi claim phải có evidence ID và quote exact; backend kiểm source/version/offset, rồi gọi semantic validator. Lỗi API trả `ERROR`/HTTP 503, không giả thành “tài liệu thiếu căn cứ”.

**Qdrant local chỉ cho một process truy cập thư mục cùng lúc:** dừng API trước khi chạy CLI index/dense search/hybrid eval, rồi khởi động lại. Backend API dùng một worker. Nếu cần API và ingest chạy đồng thời, dùng Qdrant server qua `QDRANT_URL` và `QDRANT_API_KEY`; không mở nhiều process vào cùng thư mục local.

`RAG_API_TOKEN` bật bearer authentication cho API và cookie HttpOnly sau khi đăng nhập UI. CLI mặc định bind loopback; yêu cầu có token khi bind địa chỉ khác. Đây là ứng dụng một data pack, chưa phải hệ thống phân quyền nhiều tenant.

Ví dụ API (thay snapshot và source ID theo corpus):

```json
POST /api/ask
{
  "question": "Temperature bằng 0 hoạt động như thế nào?",
  "snapshot_id": "<snapshot_id>",
  "mode": "STRICT_SOURCE",
  "lesson_id": "day-1",
  "selections": [{"unit_id": "T04-072"}]
}
```

Nếu dùng đoạn bôi đen, thêm `start`, `end` là offsets Unicode code point trên `text` trả từ `/api/sources/...`, không phải offsets trên PDF raw text. UI đã chuyển đổi từ UTF-16 của JavaScript. Client không được gửi text tự tạo thay thế nguồn backend.

Các endpoint: `/api/corpus`, `/api/documents/{snapshot}`, `/api/units/{snapshot}/{document}`, `/api/sources/{snapshot}/{unit}`, `/api/search`, `/api/ask`, `/api/feedback`. Swagger tại `/docs`.

**8. Kiểm thử và vận hành**

```bash
.venv/bin/pytest -q
.venv/bin/ruff check vlearn tests
.venv/bin/python -m vlearn.evaluate e2e --snapshot "$rag_snapshot_id"
```

Unit/integration tests dùng OpenRouter HTTP mock và Qdrant thật trên thư mục tạm; kiểm thứ tự response, prefix, cache, retry, giới hạn input, invalid vectors, idempotent ingest, thất bại index, scope leakage, citation giả, gate decisions, API auth và feedback. Test data pack tự skip khi private pack không có trên máy.

Eval e2e gọi OpenRouter thật, cần key, chat model và index cho mode mở rộng. Report đặt trong `artifacts/eval/`. Không diễn giải kết quả mock hoặc report `local_heuristic` cũ là kết quả LLM thật. Golden eval cũ giữ nguyên; runner mới độc lập vì mã `VLearnTutorCore` mà runner cũ import không có trong repo hiện tại.

Trace lưu snapshot/model/prompt version, source IDs, candidate ranks, quyết định từng gate, usage và latency; mặc định lưu hash câu hỏi thay vì raw question. Không log key, raw prompt hay toàn bộ câu trả lời. SQL có bảng `traces` và `feedback` để audit theo `trace_id`.

Rollback bằng `vlearn activate --snapshot <bản-cũ-đã-index>` và khôi phục embedding config tương ứng trước khi dense search. Xóa `artifacts/` xóa bản sao nguồn, vectors, cache và trace; chỉ thực hiện khi không cần citation cũ và theo quy định lưu dữ liệu của khóa học.

Giới hạn hiện tại: OCR/VLM và mapping transcript–slide cần review riêng; semantic validator vẫn có thể sai nên cần human audit; chưa chạy đánh giá embedding/LLM thật khi chưa cấu hình `OPENROUTER_API_KEY`.

Tham khảo API: [OpenRouter embedding catalog](https://openrouter.ai/docs/api/api-reference/embeddings/list-all-embeddings-models), [structured outputs](https://openrouter.ai/docs/guides/features/structured-outputs), [Liquid model card và prefix](https://huggingface.co/LiquidAI/LFM2.5-Embedding-350M).
