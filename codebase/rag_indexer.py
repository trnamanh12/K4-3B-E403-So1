"""
Module RAG Indexer & Knowledge Retrieval Engine cho VLearn AI Tutor.
- Parse 58 trang slide PDF (Day 1 & Day 2) bằng pdftotext, làm sạch watermark.
- Parse 700 đoạn transcript bài giảng (transcript-01 -> 06) từ markdown.
- Lập chỉ mục với SQLite FTS5 (BM25 ranking) với bộ tokenizer unicode61 hỗ trợ tiếng Việt.
- Cung cấp API truy xuất tự động (Auto-retrieval) và cấp dữ liệu slide cho Web UI.
"""

import os
import re
import sqlite3
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SLIDES_DIR = PROJECT_ROOT / "data" / "vlearn-pack" / "slides"
TRANSCRIPT_DIR = PROJECT_ROOT / "data" / "vlearn-pack" / "transcript"
DB_PATH = PROJECT_ROOT / "codebase" / "data_index.db"

def clean_watermark_and_format(text: str) -> str:
    """
    Làm sạch các ký tự watermark dạng đơn lẻ trên từng dòng:
    A H K C N I I C A I T N O - H T A N O
    """
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Loại bỏ các ký tự watermark đứng 1 mình (chữ in hoa hoặc dấu gạch nối)
        if len(stripped) == 1 and (stripped.isupper() or stripped in ["-", "·", "•"]):
            # Giữ lại bullet point nếu có text sau đó, nhưng ở đây stripped chỉ có 1 ký tự
            continue
        cleaned_lines.append(line)
    
    # Gộp các dòng trống liên tiếp
    merged = "\n".join(cleaned_lines)
    merged = re.sub(r"\n{3,}", "\n\n", merged)
    return merged.strip()

def parse_pdf_slides(pdf_path: Path, day_label: str) -> List[Dict[str, Any]]:
    """
    Trích xuất từng trang slide từ PDF bằng pdftotext (có sẵn trên Linux/Ubuntu).
    """
    slides = []
    if not pdf_path.exists():
        return slides

    try:
        cmd = ["pdftotext", str(pdf_path), "-"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        raw_pages = res.stdout.split("\x0c")  # Form feed ký hiệu ngắt trang của pdftotext
    except Exception as e:
        print(f"[WARN] Không thể chạy pdftotext trên {pdf_path}: {e}")
        return slides

    page_num = 1
    for raw_page in raw_pages:
        page_text = raw_page.strip()
        if not page_text:
            continue
        
        cleaned = clean_watermark_and_format(page_text)
        if not cleaned:
            continue

        # Lấy dòng đầu tiên có nội dung làm title
        lines = [l.strip() for l in cleaned.split("\n") if l.strip()]
        title = lines[0] if lines else f"{day_label} - Trang {page_num}"
        if len(title) > 80:
            title = title[:80] + "..."

        slide_id = f"SLIDE_{day_label.replace(' ', '_').upper()}_P{page_num:02d}"
        page_tag = f"Trang {page_num} ({day_label})"

        slides.append({
            "id": slide_id,
            "source_type": "slide",
            "day_or_file": day_label,
            "page_or_tag": f"Trang {page_num}",
            "title": title,
            "content": cleaned,
            "citation_label": f"[{day_label} - Trang {page_num}]"
        })
        page_num += 1

    return slides

def parse_transcript_markdown(md_path: Path) -> List[Dict[str, Any]]:
    """
    Trích xuất các block [Txx-NNN] từ file transcript clean markdown.
    """
    chunks = []
    if not md_path.exists():
        return chunks

    content = md_path.read_text(encoding="utf-8")
    
    # Lấy tiêu đề tài liệu
    title_match = re.search(r"^#\s*(.+)", content, re.MULTILINE)
    doc_title = title_match.group(1).strip() if title_match else md_path.stem

    # Bóc tách các đoạn [Txx-NNN]
    pattern = r"\*\*\[(T\d+-\d+)\]\*\*\s*(.*?)(?=\n\n\*\*\[T\d+-\d+\]\*\*|\n## |\Z)"
    matches = re.findall(pattern, content, re.DOTALL)

    for tag, text in matches:
        cleaned_text = re.sub(r"\[Hoạt động lớp:.*?\]", "", text).strip()
        cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text).strip()
        if not cleaned_text or len(cleaned_text) < 15:
            continue

        chunk_id = f"TRANSCRIPT_{tag}"
        chunks.append({
            "id": chunk_id,
            "source_type": "transcript",
            "day_or_file": md_path.name,
            "page_or_tag": f"[{tag}]",
            "title": doc_title,
            "content": cleaned_text,
            "citation_label": f"[{tag}]"
        })

    return chunks

class RAGIndexer:
    """
    Quản lý cơ sở dữ liệu SQLite FTS5 chứa toàn bộ Slides & Transcripts.
    """
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            # Bảng lưu trữ gốc
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_items (
                    id TEXT PRIMARY KEY,
                    source_type TEXT,
                    day_or_file TEXT,
                    page_or_tag TEXT,
                    title TEXT,
                    content TEXT,
                    citation_label TEXT
                )
            """)
            # Bảng FTS5 tìm kiếm toàn văn unicode61
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
                    id UNINDEXED,
                    source_type,
                    day_or_file,
                    page_or_tag,
                    title,
                    content,
                    tokenize = 'unicode61'
                )
            """)
            conn.commit()

    def build_index(self, force: bool = False) -> Dict[str, int]:
        """
        Quét dữ liệu từ thư mục slides và transcript, nạp vào SQLite FTS5.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM knowledge_items")
            count = cursor.fetchone()[0]
            if count > 0 and not force:
                return {"status": "ALREADY_BUILT", "total_docs": count}

            # Xoá bảng cũ nếu force
            conn.execute("DELETE FROM knowledge_items")
            conn.execute("DELETE FROM knowledge_fts")

            total_slides = 0
            total_transcripts = 0

            # 1. Parse Slides Day 1 & Day 2
            d1_slides = parse_pdf_slides(SLIDES_DIR / "d1-slide-hackathon.pdf", "Day 1")
            d2_slides = parse_pdf_slides(SLIDES_DIR / "d2-slide-hackathon.pdf", "Day 2")
            all_slides = d1_slides + d2_slides
            total_slides = len(all_slides)

            for s in all_slides:
                conn.execute("""
                    INSERT INTO knowledge_items (id, source_type, day_or_file, page_or_tag, title, content, citation_label)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (s["id"], s["source_type"], s["day_or_file"], s["page_or_tag"], s["title"], s["content"], s["citation_label"]))
                
                conn.execute("""
                    INSERT INTO knowledge_fts (id, source_type, day_or_file, page_or_tag, title, content)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (s["id"], s["source_type"], s["day_or_file"], s["page_or_tag"], s["title"], s["content"]))

            # 2. Parse 6 Transcripts
            for md_file in sorted(TRANSCRIPT_DIR.glob("transcript-*.md")):
                t_chunks = parse_transcript_markdown(md_file)
                total_transcripts += len(t_chunks)
                for c in t_chunks:
                    conn.execute("""
                        INSERT INTO knowledge_items (id, source_type, day_or_file, page_or_tag, title, content, citation_label)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (c["id"], c["source_type"], c["day_or_file"], c["page_or_tag"], c["title"], c["content"], c["citation_label"]))

                    conn.execute("""
                        INSERT INTO knowledge_fts (id, source_type, day_or_file, page_or_tag, title, content)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (c["id"], c["source_type"], c["day_or_file"], c["page_or_tag"], c["title"], c["content"]))

            conn.commit()
            return {
                "status": "BUILT_SUCCESS",
                "slides_count": total_slides,
                "transcripts_count": total_transcripts,
                "total_count": total_slides + total_transcripts
            }

    def search(self, query: str, top_k: int = 3, source_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Truy vấn kiến thức bằng BM25 xếp hạng độ liên quan từ SQLite FTS5.
        Tự động làm sạch ký tự lạ để tránh lỗi cú pháp FTS5.
        """
        # Trích xuất các từ đơn chữ và số
        raw_words = re.findall(r"\w+", query, re.UNICODE)
        # Loại bỏ các từ quá ngắn hoặc quá chung
        stop_words = {"là", "gì", "như", "thế", "nào", "hãy", "cho", "tôi", "biết", "ở", "đâu", "khi", "sao", "được", "có", "không", "các", "và", "của", "trong", "về"}
        search_words = [w for w in raw_words if w.lower() not in stop_words and len(w) > 1]

        if not search_words:
            # Fallback nếu câu quá ngắn
            search_words = [w for w in raw_words if len(w) > 1]
            if not search_words:
                return []

        fts_query = " OR ".join(f'"{w}"' for w in search_words)

        results = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                if source_type:
                    sql = """
                        SELECT k.id, k.source_type, k.day_or_file, k.page_or_tag, k.title, k.content, k.citation_label,
                               bm25(knowledge_fts) as rank
                        FROM knowledge_fts f
                        JOIN knowledge_items k ON f.id = k.id
                        WHERE knowledge_fts MATCH ? AND k.source_type = ?
                        ORDER BY rank
                        LIMIT ?
                    """
                    cursor.execute(sql, (fts_query, source_type, top_k))
                else:
                    sql = """
                        SELECT k.id, k.source_type, k.day_or_file, k.page_or_tag, k.title, k.content, k.citation_label,
                               bm25(knowledge_fts) as rank
                        FROM knowledge_fts f
                        JOIN knowledge_items k ON f.id = k.id
                        WHERE knowledge_fts MATCH ?
                        ORDER BY rank
                        LIMIT ?
                    """
                    cursor.execute(sql, (fts_query, top_k))

                for row in cursor.fetchall():
                    results.append({
                        "id": row["id"],
                        "source_type": row["source_type"],
                        "day_or_file": row["day_or_file"],
                        "page_or_tag": row["page_or_tag"],
                        "title": row["title"],
                        "content": row["content"],
                        "citation_label": row["citation_label"],
                        "score": round(float(row["rank"]), 4)
                    })
            except Exception as e:
                # Fallback LIKE query nếu FTS5 gặp ký tự ngoài ý muốn
                sql_fallback = """
                    SELECT id, source_type, day_or_file, page_or_tag, title, content, citation_label
                    FROM knowledge_items
                    WHERE content LIKE ?
                    LIMIT ?
                """
                like_term = f"%{search_words[0]}%"
                cursor.execute(sql_fallback, (like_term, top_k))
                for row in cursor.fetchall():
                    results.append({
                        "id": row["id"],
                        "source_type": row["source_type"],
                        "day_or_file": row["day_or_file"],
                        "page_or_tag": row["page_or_tag"],
                        "title": row["title"],
                        "content": row["content"],
                        "citation_label": row["citation_label"],
                        "score": 1.0
                    })

        return results

    def get_all_slides_dict(self) -> Dict[str, Dict[str, str]]:
        """
        Lấy toàn bộ slide đã parse dưới dạng dictionary tương thích với SAMPLE_SLIDES của web server.
        Key dạng 'Trang N' hoặc 'Trang N (Day 2)'
        """
        slides_dict = {}
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, day_or_file, page_or_tag, title, content
                FROM knowledge_items
                WHERE source_type = 'slide'
                ORDER BY day_or_file, id
            """)
            for row in cursor.fetchall():
                day = row["day_or_file"]
                p_tag = row["page_or_tag"]
                key = f"{p_tag}" if day == "Day 1" else f"{p_tag} ({day})"
                slides_dict[key] = {
                    "title": row["title"],
                    "content": row["content"],
                    "course": day.replace(" ", "")
                }
        return slides_dict

    def get_slide_content(self, page_str: str) -> Optional[Dict[str, Any]]:
        """
        Tìm slide cụ thể theo chuỗi trang, ví dụ 'Trang 5'
        """
        p_match = re.search(r"trang\s*(\d+)", page_str, re.IGNORECASE)
        if not p_match:
            return None
        page_target = f"Trang {int(p_match.group(1))}"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, day_or_file, page_or_tag, title, content, citation_label
                FROM knowledge_items
                WHERE source_type = 'slide' AND page_or_tag = ?
                LIMIT 1
            """, (page_target,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

# Singleton indexer instance
indexer = RAGIndexer()

if __name__ == "__main__":
    print("=== TIẾN HÀNH INDEX SLIDE & TRANSCRIPT VÀO SQLITE FTS5 ===")
    res = indexer.build_index(force=True)
    print("Kết quả lập chỉ mục:", res)

    print("\n--- TEST TRUY VẤN: 'Transformer hoạt động thế nào' ---")
    matches = indexer.search("Transformer hoạt động thế nào", top_k=2)
    for m in matches:
        print(f"[{m['source_type'].upper()}] {m['citation_label']} {m['title']}")
        print(f"Content snippet: {m['content'][:150]}...\n")

    print("--- TEST TRUY VẤN: 'Google AI Studio hạn mức bao nhiêu' ---")
    matches_api = indexer.search("Google AI Studio hạn mức bao nhiêu", top_k=1)
    for m in matches_api:
        print(f"[{m['source_type'].upper()}] {m['citation_label']} {m['title']}")
        print(f"Content snippet: {m['content'][:150]}...\n")
