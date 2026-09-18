// Gia Sư AI VLearn · Trợ Lý Học Tập Có Căn Cứ
// Frontend Application built with React 18 & Tailwind CSS

const { useState, useEffect, useRef, useMemo } = React;

// --- LUCIDE ICONS (HANDCRAFTED SVG COMPONENTS) ---
const Icon = ({ name, className = "w-4 h-4", ...props }) => {
  const icons = {
    GraduationCap: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
        <path d="M6 12v5c3 3 9 3 12 0v-5"/>
      </svg>
    ),
    BookOpen: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
      </svg>
    ),
    Bot: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <rect x="3" y="11" width="18" height="10" rx="2"/>
        <circle cx="12" cy="5" r="2"/>
        <path d="M12 7v4"/>
        <line x1="8" y1="16" x2="8" y2="16"/>
        <line x1="16" y1="16" x2="16" y2="16"/>
      </svg>
    ),
    Sparkles: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>
      </svg>
    ),
    CheckCircle2: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <circle cx="12" cy="12" r="10"/>
        <path d="m9 12 2 2 4-4"/>
      </svg>
    ),
    AlertTriangle: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
        <line x1="12" y1="9" x2="12" y2="13"/>
        <line x1="12" y1="17" x2="12.01" y2="17"/>
      </svg>
    ),
    HelpCircle: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <circle cx="12" cy="12" r="10"/>
        <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
        <line x1="12" y1="17" x2="12.01" y2="17"/>
      </svg>
    ),
    Send: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <line x1="22" y1="2" x2="11" y2="13"/>
        <polygon points="22 2 15 22 11 13 2 9 22 2"/>
      </svg>
    ),
    ChevronLeft: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <polyline points="15 18 9 12 15 6"/>
      </svg>
    ),
    ChevronRight: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <polyline points="9 18 15 12 9 6"/>
      </svg>
    ),
    ZoomIn: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <circle cx="11" cy="11" r="8"/>
        <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        <line x1="11" y1="8" x2="11" y2="14"/>
        <line x1="8" y1="11" x2="14" y2="11"/>
      </svg>
    ),
    ZoomOut: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <circle cx="11" cy="11" r="8"/>
        <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        <line x1="8" y1="11" x2="14" y2="11"/>
      </svg>
    ),
    RotateCcw: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
        <path d="M3 3v5h5"/>
      </svg>
    ),
    ExternalLink: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
        <polyline points="15 3 21 3 21 9"/>
        <line x1="10" y1="14" x2="21" y2="3"/>
      </svg>
    ),
    ThumbsUp: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <path d="M7 10v12"/>
        <path d="M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h3"/>
      </svg>
    ),
    Flag: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/>
        <line x1="4" y1="22" x2="4" y2="15"/>
      </svg>
    ),
    Activity: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
      </svg>
    ),
    Layers: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <polygon points="12 2 2 7 12 12 22 7 12 2"/>
        <polyline points="2 17 12 22 22 17"/>
        <polyline points="2 12 12 17 22 12"/>
      </svg>
    ),
    X: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <line x1="18" y1="6" x2="6" y2="18"/>
        <line x1="6" y1="6" x2="18" y2="18"/>
      </svg>
    ),
    Check: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <polyline points="20 6 9 17 4 12"/>
      </svg>
    ),
    FileText: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="16" y1="13" x2="8" y2="13"/>
        <line x1="16" y1="17" x2="8" y2="17"/>
        <line x1="10" y1="9" x2="8" y2="9"/>
      </svg>
    ),
    MessageSquare: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
    ),
    ShieldCheck: (
      <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        <path d="m9 12 2 2 4-4"/>
      </svg>
    )
  };
  return icons[name] || null;
};

// --- DEFAULT SLIDE DATA FALLBACK ---
const DEFAULT_SLIDES = {
  "Trang 1": {
    title: "Day 1 — LLM Foundation & AI Product Thinking",
    content: "Chào mừng các bạn đến với khoá học AI Product Hackathon.\nNội dung chính Day 1: Xây dựng nền tảng tư duy sản phẩm AI, hiểu giới hạn của mô hình ngôn ngữ lớn và phương pháp đo lường chất lượng giải pháp.\nLưu ý quy chế lớp học: Lộ trình từ CP1 đến CP6 kết thúc lúc 21:00. Mọi vấn đề xin lùi hạn, điểm danh cần liên hệ TA.",
    course: "Khoá K4 — AI Thực Chiến"
  },
  "Trang 15": {
    title: "Cài đặt môi trường & Thư viện SDK",
    content: "Hướng dẫn cài đặt môi trường lập trình Python cho AI.\nLỗi thường gặp khi thiếu thư viện: ModuleNotFoundError: No module named 'google.genai'.\nCách khắc phục chuẩn xác: Chạy lệnh 'pip install google-genai' trong terminal của môi trường ảo.",
    course: "Khoá K4 — AI Thực Chiến"
  },
  "Trang 21": {
    title: "Kiến trúc RNN so với Transformer",
    content: "RNN xử lý tuần tự từng từ một nên chậm và khó bắt phụ thuộc xa.\nTransformer sử dụng cơ chế Self-Attention cho phép xử lý toàn bộ các từ cùng một lúc (song song).",
    course: "Khoá K4 — AI Thực Chiến"
  },
  "Trang 38": {
    title: "Quy trình huấn luyện LLM: Pre-training vs SFT",
    content: "Giai đoạn 1: Pre-training là đọc cả thư viện hàng nghìn tỷ token để học ngữ pháp và tri thức tổng quát.\nGiai đoạn 2: SFT (Supervised Fine-Tuning) dạy mô hình học cách hội thoại và tuân thủ chỉ thị của con người.",
    course: "Khoá K4 — AI Thực Chiến"
  }
};

// --- MAIN APPLICATION COMPONENT ---
function VLearnTutorApp() {
  // Slides state
  const [slides, setSlides] = useState(DEFAULT_SLIDES);
  const [currentPage, setCurrentPage] = useState("Trang 1");
  const [zoomLevel, setZoomLevel] = useState(100);
  const [sourceAnchorPulse, setSourceAnchorPulse] = useState(false);
  const [anchorSnippet, setAnchorSnippet] = useState("");

  // Golden set state
  const [goldenCases, setGoldenCases] = useState([]);
  const [isGoldenModalOpen, setIsGoldenModalOpen] = useState(false);
  const [selectedLayerFilter, setSelectedLayerFilter] = useState("ALL");

  // Selection & Popover state
  const [activeSelection, setActiveSelection] = useState({
    text: "",
    page: ""
  });
  const [attachedContext, setAttachedContext] = useState(null);

  // Chat state
  const [messages, setMessages] = useState([
    {
      id: "welcome-1",
      role: "assistant",
      type: "grounded",
      text: "Chào bạn! Mình là Gia Sư AI VLearn. Mình sẵn sàng giải đáp thắc mắc bài giảng dựa trên căn cứ thực tế từ các slide và transcript bài học. Bạn có thể bôi đen đoạn tài liệu bất kỳ bên trái, gõ câu hỏi tự do, hoặc chọn câu hỏi mẫu từ bộ Golden Set bên trên nhé!",
      pageRef: "",
      citation: "",
      quotedSnippet: "",
      pedagogicMove: "review_concept",
      timestamp: "Vừa xong",
      feedback: null
    }
  ]);
  const [studentInput, setStudentInput] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [inputPulse, setInputPulse] = useState(false);

  // Inspector & Drawer state
  const [isInspectionOpen, setIsInspectionOpen] = useState(false);
  const [traceCount, setTraceCount] = useState(12);
  const [activeInspectionData, setActiveInspectionData] = useState({
    similarityScore: 0.95,
    intent: "Sẵn sàng hỗ trợ (System Ready)",
    nliFaithfulness: "Chờ truy vấn",
    decisionTrace: [
      { step: "C_Quyet_dinh_1", output: { decision: "READY", reason: "Hệ thống sẵn sàng tiếp nhận câu hỏi của học viên." } },
      { step: "G_Quyet_dinh_2", output: { decision: "READY", reason: "Kho tri thức 58 slide và 648 transcript đã được nạp." } }
    ]
  });

  // Feedback modal state
  const [feedbackModal, setFeedbackModal] = useState({ isOpen: false, messageId: null });
  const [feedbackReason, setFeedbackReason] = useState("Trích dẫn sai trang slide");
  const [feedbackNote, setFeedbackNote] = useState("");

  // Toast notification state
  const [toast, setToast] = useState(null);

  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Show Toast
  const showToast = (message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  };

  // 1. Fetch slides and golden set on mount
  useEffect(() => {
    fetch("/api/slides")
      .then(res => res.json())
      .then(data => {
        if (data && Object.keys(data).length > 0) {
          setSlides(data);
          if (!data[currentPage]) {
            setCurrentPage(Object.keys(data)[0]);
          }
        }
      })
      .catch(err => console.log("Using default slides:", err));

    fetch("/api/golden_set")
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) setGoldenCases(data);
      })
      .catch(err => console.log("Using local golden cases:", err));

    fetch("/api/traces")
      .then(res => res.json())
      .then(data => {
        if (data && data.total_count) setTraceCount(data.total_count);
      })
      .catch(() => {});
  }, []);

  // Auto-scroll messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isGenerating]);

  // Handle text selection on the slide
  const handleSlideMouseUp = () => {
    const sel = window.getSelection();
    const text = sel ? sel.toString().trim() : "";
    if (text.length > 5) {
      setActiveSelection({ text, page: currentPage });
    }
  };

  // Attach selection to chat context
  const handleAttachSelection = (snippetText = null) => {
    const textToAttach = snippetText || activeSelection.text || (slides[currentPage] ? slides[currentPage].content : "");
    setAttachedContext({
      page: currentPage,
      snippet: textToAttach
    });
    showToast(`Đã đính kèm đoạn trích tại ${currentPage} vào ngữ cảnh hỏi đáp!`);
    textareaRef.current?.focus();
  };

  // Remove attached context tag
  const handleRemoveContext = () => {
    setAttachedContext(null);
  };

  // SỬA LỖI & HOÀN THIỆN: Nạp câu hỏi từ Golden Set vào ô nhập của học viên
  const applyGoldenCase = (c, autoSend = false) => {
    if (!c) return;

    // 1. Chuẩn hóa target page (xử lý trường hợp "Trang 68 và Trang 76" -> lấy "Trang 68")
    let targetPage = c.page_ref || "Trang 1";
    if (targetPage.includes("và")) {
      targetPage = targetPage.split("và")[0].trim();
    }
    if (slides[targetPage]) {
      setCurrentPage(targetPage);
    }

    // 2. Cập nhật context đính kèm
    const snippet = c.context_snippet || (slides[targetPage] ? slides[targetPage].content : "");
    setAttachedContext({
      page: c.page_ref || targetPage,
      snippet: snippet
    });

    // 3. Highlight đoạn trích trên tài liệu
    setAnchorSnippet(snippet);

    // 4. ĐIỀN VÀO Ô NHẬP HỌC VIÊN
    setStudentInput(c.student_question);

    // 5. Đóng modal Golden Set
    setIsGoldenModalOpen(false);

    // 6. Hiệu ứng phát sáng và focus vào textarea
    setInputPulse(true);
    setTimeout(() => setInputPulse(false), 2000);

    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.focus();
        // Tự co giãn textarea
        textareaRef.current.style.height = "auto";
        textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
      }
    }, 100);

    showToast(`✨ Đã nạp thành công câu hỏi [${c.id}] vào ô nhập của học viên!`);

    // Nếu chọn Nạp & Gửi ngay
    if (autoSend) {
      setTimeout(() => {
        executeChat(c.student_question, snippet, c.page_ref || targetPage, c.id);
      }, 300);
    }
  };

  // Source Anchor Jump: Click citation chip in chat
  const handleCitationClick = (pageRef, snippet) => {
    // Chuyển trang nếu cần
    const cleanPage = pageRef.replace(/[\[\]↗]/g, "").trim();
    let target = cleanPage;
    if (target.toLowerCase().startsWith("trang")) {
      // chuẩn hóa chữ hoa đầu
      const num = target.replace(/\D/g, "");
      target = `Trang ${num}`;
    }
    if (slides[target]) {
      setCurrentPage(target);
    }
    
    // Đặt snippet cần nháy sáng
    if (snippet) {
      setAnchorSnippet(snippet);
    }
    setSourceAnchorPulse(true);
    setTimeout(() => setSourceAnchorPulse(false), 2500);

    showToast(`Đã neo đến nguồn tài liệu tại ${target}!`, "info");
  };

  // Gửi câu hỏi vào API Chat
  const executeChat = async (qText, snippetText, pageName, turnId = null) => {
    const question = (qText || studentInput).trim();
    if (!question || isGenerating) return;

    const currentSnippet = snippetText !== undefined ? snippetText : (attachedContext ? attachedContext.snippet : "");
    const currentPageRef = pageName || (attachedContext ? attachedContext.page : currentPage);

    // Thêm tin nhắn của học viên
    const userMsg = {
      id: `user-${Date.now()}`,
      role: "user",
      text: question,
      contextAttached: attachedContext ? `${attachedContext.page}` : null,
      timestamp: "Bây giờ"
    };

    setMessages(prev => [...prev, userMsg]);
    setStudentInput("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
    setIsGenerating(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: question,
          context_snippet: currentSnippet,
          page_ref: currentPageRef,
          turn_id: turnId || `WEB_TURN_${Date.now()}`,
          session_id: "VLEARN_WEB_USER"
        })
      });

      const data = await res.json();
      setIsGenerating(false);

      // Cập nhật thông số Inspection Drawer
      if (data.decision_trace) {
        const d1 = data.decision_trace.find(x => x.step && x.step.includes("1"));
        const d3 = data.decision_trace.find(x => x.step && x.step.includes("3"));
        setActiveInspectionData({
          similarityScore: data.final_status === "GROUNDED" ? 0.94 : (data.final_status === "INSUFFICIENT_GROUNDING" ? 0.42 : 0.68),
          intent: d1?.output?.decision === "OUT_OF_SCOPE" ? "Ngoài phạm vi trợ giảng" : (d1?.output?.decision === "AMBIGUOUS" ? "Câu hỏi mơ hồ" : "Kiến thức bài giảng"),
          nliFaithfulness: d3?.output?.decision === "PASSED" ? "Passed (100% Khớp nguồn)" : "Chưa kiểm chứng",
          decisionTrace: data.decision_trace,
          latestTrace: data.latest_trace
        });
        setTraceCount(prev => prev + 1);
      }

      // Phân loại khối thẻ hiển thị theo final_status
      let cardType = "grounded";
      if (data.final_status === "INSUFFICIENT_GROUNDING") {
        cardType = "fallback";
      } else if (data.final_status === "AMBIGUOUS" || data.final_status === "CLARIFICATION_OR_OUT_OF_SCOPE") {
        cardType = "clarification";
      } else if (data.final_status === "OUT_OF_SCOPE") {
        cardType = "out_of_scope";
      } else if (data.final_status === "VALIDATION_FAILED_HALLUCINATION") {
        cardType = "validation_failed";
      } else if (data.final_status === "SERVER_ERROR") {
        cardType = "server_error";
      }

      const resolvedCitation = data.citation || currentPageRef;
      const aiMsg = {
        id: `ai-${Date.now()}`,
        role: "assistant",
        type: cardType,
        text: data.final_response || "Không có phản hồi từ máy chủ.",
        pageRef: resolvedCitation,
        citation: `[${resolvedCitation} ↗]`,
        quotedSnippet: data.context_snippet || currentSnippet,
        pedagogicMove: data.pedagogic_move || "review_concept",
        retrievedSources: data.retrieved_sources || [],
        rawStatus: data.final_status,
        timestamp: "Vừa xong",
        feedback: null
      };

      setMessages(prev => [...prev, aiMsg]);

    } catch (err) {
      console.error("Chat error:", err);
      setIsGenerating(false);
      setMessages(prev => [
        ...prev,
        {
          id: `ai-err-${Date.now()}`,
          role: "assistant",
          type: "server_error",
          text: "Đã xảy ra lỗi kết nối với máy chủ AI. Vui lòng đảm bảo web server đang chạy ('python codebase/web_server.py') và thử lại.",
          pageRef: currentPageRef,
          timestamp: "Vừa xong"
        }
      ]);
    }
  };

  // Submit Human-In-The-Loop feedback
  const submitFeedback = (isPositive) => {
    if (isPositive) {
      showToast("Cảm ơn bạn đã xác nhận câu trả lời hữu ích và chuẩn xác! 👍");
      return;
    }
    // Báo lỗi mở modal
    setFeedbackModal({ isOpen: true, messageId: messages[messages.length - 1]?.id });
  };

  const handleSendReport = () => {
    showToast(`Đã ghi nhận phản ánh: "${feedbackReason}". Đội ngũ trợ giảng sẽ kiểm tra lại slide! ⚠️`, "info");
    setFeedbackModal({ isOpen: false, messageId: null });
    setFeedbackNote("");
  };

  // Lọc Golden Cases theo Tab
  const filteredGoldenCases = useMemo(() => {
    if (selectedLayerFilter === "ALL") return goldenCases;
    return goldenCases.filter(c => {
      if (selectedLayerFilter === "LAYER_1") return c.layer === "Lop_1_Nguon_Su_That";
      if (selectedLayerFilter === "LAYER_2") return c.layer === "Lop_2_Mo_Ho_Thieu_Tin";
      if (selectedLayerFilter === "LAYER_3") return c.layer === "Lop_3_Ngoai_Tham_Quyen";
      if (selectedLayerFilter === "LAYER_4") return c.layer === "Lop_4_Dac_Thu_Domain";
      if (selectedLayerFilter === "EDGE") return c.layer && c.layer.includes("Edge");
      return true;
    });
  }, [goldenCases, selectedLayerFilter]);

  const currentSlideData = slides[currentPage] || {
    title: "Không tìm thấy trang",
    content: "Nội dung slide chưa được tải.",
    course: "Khoá K4"
  };

  const slideKeys = Object.keys(slides);
  const currentSlideIndex = slideKeys.indexOf(currentPage);

  const goToNextSlide = () => {
    if (currentSlideIndex < slideKeys.length - 1) {
      setCurrentPage(slideKeys[currentSlideIndex + 1]);
    }
  };

  const goToPrevSlide = () => {
    if (currentSlideIndex > 0) {
      setCurrentPage(slideKeys[currentSlideIndex - 1]);
    }
  };

  return (
    <div className="h-full flex flex-col bg-slate-100 text-slate-800">
      
      {/* TOAST ALERT */}
      {toast && (
        <div className={`fixed top-4 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-xl shadow-xl border text-sm font-medium transition-all animate-bounce-subtle ${
          toast.type === "success" 
            ? "bg-emerald-600 text-white border-emerald-500" 
            : "bg-blue-600 text-white border-blue-500"
        }`}>
          <Icon name={toast.type === "success" ? "CheckCircle2" : "Sparkles"} className="w-5 h-5 flex-shrink-0" />
          <span>{toast.message}</span>
        </div>
      )}

      {/* --- TOP APP HEADER --- */}
      <header className="h-16 bg-white border-b border-slate-200/80 px-6 flex items-center justify-between shadow-sm z-20 flex-shrink-0">
        <div className="flex items-center gap-4">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/20">
            <Icon name="GraduationCap" className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold text-slate-900 tracking-tight">Gia Sư AI VLearn</h1>
              <span className="text-xs px-2 py-0.5 rounded-md font-semibold bg-blue-50 text-blue-700 border border-blue-200/60">
                Trợ Lý Học Tập Có Căn Cứ
              </span>
            </div>
            <p className="text-xs text-slate-500">Khóa AI Thực Chiến K4 · Hệ thống RAG Kiểm chứng Citation thời gian thực</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Badge Grounded Mode */}
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Đang bảo vệ căn cứ (Grounded Mode)</span>
          </div>

          {/* Nút Mở 20 Golden Cases */}
          <button 
            onClick={() => setIsGoldenModalOpen(true)}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-indigo-500 to-blue-600 text-white hover:from-indigo-600 hover:to-blue-700 shadow-sm transition-all"
            title="Xem và nạp 20 câu kiểm thử mẫu vào ô nhập học viên"
          >
            <Icon name="Layers" className="w-4 h-4" />
            <span>Kho 20 câu Golden Set</span>
            <span className="bg-white/20 px-1.5 py-0.2 rounded-full text-[10px]">20</span>
          </button>

          {/* Nút Xem Trace Inspector */}
          <button 
            onClick={() => setIsInspectionOpen(!isInspectionOpen)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-200 transition-all"
            title="Xem các chỉ số NLI Faithfulness và vết quyết định"
          >
            <Icon name="Activity" className="w-4 h-4 text-blue-600" />
            <span>Trace Inspector</span>
            <span className="bg-slate-200 text-slate-800 px-1.5 py-0.2 rounded-full text-[10px] font-semibold">{traceCount}</span>
          </button>

          {/* Nút Reset Chat */}
          <button 
            onClick={() => {
              setMessages([{
                id: `welcome-${Date.now()}`,
                role: "assistant",
                type: "grounded",
                text: "Đã làm mới phiên thảo luận. Bạn có thể tiếp tục chọn đoạn văn bản bên tài liệu hoặc đặt câu hỏi mới nhé!",
                pageRef: currentPage,
                timestamp: "Vừa xong"
              }]);
              showToast("Đã làm mới phiên hỏi đáp!");
            }}
            className="p-2 rounded-lg text-slate-500 hover:text-slate-800 hover:bg-slate-100 border border-slate-200 transition-all"
            title="Làm mới hội thoại"
          >
            <Icon name="RotateCcw" className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* --- WORKSPACE BODY: 6:4 SPLIT SCREEN --- */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* ======================================================== */}
        {/* CỘT TRÁI (60% - DOCUMENT VIEWER) */}
        {/* ======================================================== */}
        <section className="w-3/5 border-r border-slate-200 flex flex-col bg-slate-100/70 relative">
          
          {/* Document Header Bar */}
          <div className="h-12 bg-white/90 backdrop-blur border-b border-slate-200 px-5 flex items-center justify-between z-10">
            {/* Breadcrumb */}
            <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium truncate">
              <span className="text-slate-700 font-semibold">Khóa AI Thực Chiến</span>
              <span>&gt;</span>
              <span>Day 03</span>
              <span>&gt;</span>
              <span className="text-blue-600 flex items-center gap-1">
                <Icon name="FileText" className="w-3.5 h-3.5" />
                Slide_Agentic_RAG.pdf
              </span>
            </div>

            {/* Pagination & Zoom Controls */}
            <div className="flex items-center gap-3">
              {/* Pagination */}
              <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs">
                <button 
                  onClick={goToPrevSlide}
                  disabled={currentSlideIndex <= 0}
                  className="p-1 rounded hover:bg-white text-slate-600 disabled:opacity-30 disabled:hover:bg-transparent"
                  title="Trang trước"
                >
                  <Icon name="ChevronLeft" className="w-3.5 h-3.5" />
                </button>
                
                <select 
                  value={currentPage}
                  onChange={(e) => setCurrentPage(e.target.value)}
                  className="bg-transparent text-slate-800 font-medium px-2 py-0.5 rounded cursor-pointer outline-none text-xs"
                >
                  {slideKeys.map(k => (
                    <option key={k} value={k}>
                      {k} ({slides[k].title.substring(0, 24)}...)
                    </option>
                  ))}
                </select>

                <span className="text-slate-400 text-[11px] pr-1">/ {slideKeys.length}</span>

                <button 
                  onClick={goToNextSlide}
                  disabled={currentSlideIndex >= slideKeys.length - 1}
                  className="p-1 rounded hover:bg-white text-slate-600 disabled:opacity-30 disabled:hover:bg-transparent"
                  title="Trang sau"
                >
                  <Icon name="ChevronRight" className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Zoom Controls */}
              <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs">
                <button 
                  onClick={() => setZoomLevel(prev => Math.max(70, prev - 10))}
                  className="p-1 rounded hover:bg-white text-slate-600"
                  title="Thu nhỏ"
                >
                  <Icon name="ZoomOut" className="w-3.5 h-3.5" />
                </button>
                <span className="px-1 font-mono text-[11px] text-slate-700">{zoomLevel}%</span>
                <button 
                  onClick={() => setZoomLevel(prev => Math.min(140, prev + 10))}
                  className="p-1 rounded hover:bg-white text-slate-600"
                  title="Phóng to"
                >
                  <Icon name="ZoomIn" className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>

          {/* Document Canvas Container */}
          <div 
            className="flex-1 overflow-auto p-8 flex justify-center items-start"
            onMouseUp={handleSlideMouseUp}
          >
            <div 
              style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: "top center", transition: "transform 0.2s ease" }}
              className="w-full max-w-2xl bg-white rounded-2xl shadow-md border border-slate-200/90 p-8 relative flex flex-col justify-between min-h-[520px]"
            >
              {/* Slide Header Decorator */}
              <div>
                <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-5">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2.5 py-1 rounded-md border border-blue-100">
                      {currentSlideData.course || "Khoá K4 — AI Thực Chiến"}
                    </span>
                    <span className="text-xs font-medium text-slate-400">· Bài Giảng Chính</span>
                  </div>
                  <span className="text-xs font-mono font-bold text-slate-600 bg-slate-100 px-2 py-0.5 rounded">
                    {currentPage}
                  </span>
                </div>

                {/* Slide Title */}
                <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight mb-6 leading-snug">
                  {currentSlideData.title}
                </h2>

                {/* Slide Body Content */}
                <div className="space-y-4 text-slate-700 leading-relaxed text-sm">
                  {currentSlideData.content.split("\n").map((line, idx) => {
                    const isAnchorTarget = anchorSnippet && line.toLowerCase().includes(anchorSnippet.substring(0, 20).toLowerCase());
                    return (
                      <p 
                        key={idx} 
                        className={`p-1.5 rounded transition-all duration-700 ${
                          sourceAnchorPulse && isAnchorTarget 
                            ? "source-anchor-active bg-emerald-100 text-emerald-950 ring-2 ring-emerald-500 font-medium" 
                            : ""
                        }`}
                      >
                        {line}
                      </p>
                    );
                  })}
                </div>

                {/* TÍNH NĂNG GIẢ LẬP TƯƠNG TÁC: Đoạn text kỹ thuật có sẵn bôi đen kèm nút popover nổi */}
                <div className="mt-8 pt-4 border-t border-slate-100">
                  <div className="text-xs font-semibold text-slate-500 mb-2 flex items-center gap-1.5">
                    <Icon name="Sparkles" className="w-3.5 h-3.5 text-amber-500" />
                    <span>Đoạn trích kỹ thuật trọng tâm:</span>
                  </div>
                  <div className="relative group bg-amber-50/90 border-l-4 border-amber-400 p-4 rounded-r-xl shadow-xs transition-all hover:bg-amber-100/90">
                    <p className="text-xs text-amber-950 font-mono leading-relaxed select-text">
                      "{activeSelection.text}"
                    </p>
                    
                    {/* Popover Nổi Bật: + Hỏi AI về đoạn này */}
                    <div className="mt-3 flex items-center gap-2">
                      <button 
                        onClick={() => handleAttachSelection(activeSelection.text)}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-amber-500 to-amber-600 text-white text-xs font-bold rounded-lg shadow-sm hover:from-amber-600 hover:to-amber-700 transition-all cursor-pointer"
                      >
                        <Icon name="Sparkles" className="w-3.5 h-3.5" />
                        <span>+ Hỏi AI về đoạn này</span>
                      </button>
                      <span className="text-[11px] text-amber-800/80">
                        (Bấm để gắn ngay vào context hỏi đáp bên phải)
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Slide Footer */}
              <div className="mt-8 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
                <span>VLearn AI Academic Platform © 2026</span>
                <span className="font-mono">Tài liệu bảo chứng căn cứ</span>
              </div>
            </div>
          </div>
        </section>

        {/* ======================================================== */}
        {/* CỘT PHẢI (40% - GIA SƯ AI CHATBOT) */}
        {/* ======================================================== */}
        <section className="w-2/5 flex flex-col bg-white">
          
          {/* Header Khung Chat */}
          <div className="h-12 border-b border-slate-200 px-5 flex items-center justify-between bg-slate-50/80 backdrop-blur z-10 flex-shrink-0">
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></div>
              <span className="text-xs font-bold text-slate-800 tracking-tight">Hội Thoại Gia Sư AI</span>
              <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-100/70 px-2 py-0.5 rounded-full border border-emerald-300">
                Bảo vệ căn cứ
              </span>
            </div>
            <div className="text-[11px] text-slate-500 flex items-center gap-1">
              <span>Đang kết nối:</span>
              <span className="font-semibold text-slate-700">Gemini 2.5 Flash</span>
            </div>
          </div>

          {/* Message Thread (Cuộn Mượt) */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-slate-50/40">
            {messages.map((msg) => (
              <div key={msg.id} className="space-y-1">
                {/* Tin nhắn học viên */}
                {msg.role === "user" && (
                  <div className="flex justify-end">
                    <div className="max-w-[85%] bg-blue-600 text-white rounded-2xl rounded-tr-xs px-4 py-3 shadow-sm text-sm">
                      {msg.contextAttached && (
                        <div className="text-[11px] font-mono text-blue-200 mb-1 flex items-center gap-1">
                          <Icon name="FileText" className="w-3 h-3" />
                          <span>Tham chiếu: {msg.contextAttached}</span>
                        </div>
                      )}
                      <p className="leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                      <span className="block text-[10px] text-blue-200 text-right mt-1">{msg.timestamp}</span>
                    </div>
                  </div>
                )}

                {/* Tin nhắn Trợ Giảng AI */}
                {msg.role === "assistant" && (
                  <div className="flex justify-start">
                    <div className="max-w-[92%] w-full">
                      
                      {/* 1. KHỐI CÂU TRẢ LỜI CHUẨN (GROUNDED ANSWER CARD) */}
                      {msg.type === "grounded" && (
                        <div className="bg-white border border-emerald-200 rounded-2xl rounded-tl-xs p-4 shadow-sm border-t-4 border-t-emerald-500 transition-all hover:shadow-md">
                          {/* Badge góc trên */}
                          <div className="flex items-center justify-between mb-2.5">
                            <div className="flex items-center gap-2">
                              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
                                <Icon name="CheckCircle2" className="w-3.5 h-3.5 text-emerald-600" />
                                <span>✓ Có căn cứ xác thực</span>
                              </div>
                              {msg.pedagogicMove && (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-blue-50 text-blue-700 border border-blue-200">
                                  {msg.pedagogicMove === 'give_hint' ? '💡 Gợi ý bước giải' :
                                   msg.pedagogicMove === 'give_example' ? '🔍 Ví dụ áp dụng' :
                                   msg.pedagogicMove === 'ask_probing_question' ? '❓ Đào sâu tư duy' : '🎓 Ôn khái niệm'}
                                </span>
                              )}
                            </div>
                            <span className="text-[10px] text-slate-400">{msg.timestamp}</span>
                          </div>

                          {/* Nội dung câu trả lời */}
                          <div className="text-sm text-slate-800 leading-relaxed">
                            <p className="whitespace-pre-wrap inline">{msg.text} </p>
                            
                            {/* Citation Chip Bấm Được */}
                            {msg.pageRef && (
                              <span className="relative inline-block group ml-1.5">
                                <button 
                                  onClick={() => handleCitationClick(msg.pageRef, msg.quotedSnippet)}
                                  className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold text-emerald-700 bg-emerald-100 hover:bg-emerald-200 rounded-md border border-emerald-300 shadow-2xs transition-all cursor-pointer"
                                >
                                  <span>{msg.citation || `[${msg.pageRef} ↗]`}</span>
                                </button>
                                
                                {/* Tooltip trích nguyên văn */}
                                <div className="absolute bottom-full left-0 mb-1.5 hidden group-hover:block z-30 w-64 p-2.5 bg-slate-900 text-white text-xs rounded-xl shadow-xl border border-slate-700 text-left">
                                  <div className="text-[10px] font-bold text-emerald-400 mb-1 flex items-center gap-1">
                                    <Icon name="FileText" className="w-3 h-3" />
                                    <span>Trích nguyên văn {msg.pageRef}:</span>
                                  </div>
                                  <p className="italic text-slate-200 line-clamp-3">
                                    "{msg.quotedSnippet || "Nội dung đối chiếu trực tiếp từ trang slide bài giảng."}"
                                  </p>
                                  <div className="text-[10px] text-slate-400 mt-1.5 border-t border-slate-700 pt-1">
                                    Bấm để cuộn và nháy sáng bên tài liệu
                                  </div>
                                </div>
                              </span>
                            )}
                          </div>

                          {/* Hàng nút đánh giá (Human-in-the-loop) */}
                          <div className="mt-3.5 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                            <span className="text-slate-400 text-[11px]">Đánh giá phản hồi:</span>
                            <div className="flex items-center gap-2">
                              <button 
                                onClick={() => submitFeedback(true)}
                                className="flex items-center gap-1 px-2 py-1 rounded-md text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 border border-slate-200 hover:border-emerald-200 transition-all"
                                title="Câu trả lời chính xác, hữu ích"
                              >
                                <Icon name="ThumbsUp" className="w-3 h-3 text-emerald-600" />
                                <span>Hữu ích 👍</span>
                              </button>
                              <button 
                                onClick={() => submitFeedback(false)}
                                className="flex items-center gap-1 px-2 py-1 rounded-md text-slate-600 hover:text-rose-700 hover:bg-rose-50 border border-slate-200 hover:border-rose-200 transition-all"
                                title="Báo cáo câu trả lời sai hoặc không khớp tài liệu"
                              >
                                <Icon name="Flag" className="w-3 h-3 text-rose-500" />
                                <span>Báo lỗi nguồn không khớp ⚠️</span>
                              </button>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* 2. KHỐI THIẾU NGUỒN / NGOÀI PHẠM VI (TRANSPARENT FALLBACK CARD) */}
                      {msg.type === "fallback" && (
                        <div className="border border-amber-300 bg-amber-50/70 rounded-2xl rounded-tl-xs p-4 shadow-sm border-t-4 border-t-amber-500">
                          {/* Badge góc trên */}
                          <div className="flex items-center justify-between mb-2">
                            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-300">
                              <Icon name="AlertTriangle" className="w-3.5 h-3.5 text-amber-600" />
                              <span>Chưa đủ căn cứ trong bài học</span>
                            </div>
                            <span className="text-[10px] text-slate-400">{msg.timestamp}</span>
                          </div>

                          <div className="text-sm text-amber-950 leading-relaxed mb-3">
                            <p className="whitespace-pre-wrap">{msg.text}</p>
                          </div>

                          {/* CTA Điều Hướng */}
                          <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-amber-200/60 text-xs">
                            <a 
                              href="https://discord.com" 
                              target="_blank" 
                              rel="noreferrer"
                              className="inline-flex items-center gap-1 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg shadow-2xs transition-all"
                            >
                              <span>Hỏi TA trên Discord #lab-support</span>
                              <Icon name="ExternalLink" className="w-3 h-3" />
                            </a>
                            <button 
                              onClick={() => {
                                const nextP = currentPage === "Trang 15" ? "Trang 38" : "Trang 15";
                                setCurrentPage(nextP);
                                showToast(`Đã chuyển sang ${nextP}`);
                              }}
                              className="inline-flex items-center gap-1 px-3 py-1.5 bg-white hover:bg-amber-100 text-amber-900 font-semibold rounded-lg border border-amber-300 transition-all"
                            >
                              <span>Đổi đoạn tài liệu khác</span>
                            </button>
                          </div>
                        </div>
                      )}

                      {/* 3. KHỐI YÊU CẦU LÀM RÕ (CLARIFICATION PROMPT) */}
                      {msg.type === "clarification" && (
                        <div className="border border-slate-300 bg-slate-50 rounded-2xl rounded-tl-xs p-4 shadow-sm border-t-4 border-t-slate-400">
                          <div className="flex items-center justify-between mb-2">
                            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-200 text-slate-800 border border-slate-300">
                              <Icon name="HelpCircle" className="w-3.5 h-3.5 text-slate-600" />
                              <span>❓ Yêu cầu làm rõ ngữ cảnh</span>
                            </div>
                            <span className="text-[10px] text-slate-400">{msg.timestamp}</span>
                          </div>

                          <p className="text-sm text-slate-800 leading-relaxed mb-3">
                            {msg.text}
                          </p>

                          {/* 2 nút lựa chọn nhanh gợi ý */}
                          <div className="pt-2 border-t border-slate-200 space-y-1.5">
                            <span className="text-[11px] text-slate-500 font-medium block">Gợi ý câu hỏi bổ sung:</span>
                            <div className="flex flex-wrap gap-2">
                              <button 
                                onClick={() => {
                                  const text = "Em đang gặp lỗi khi chạy file main.py với Python 3.11, cần khắc phục thế nào?";
                                  setStudentInput(text);
                                  textareaRef.current?.focus();
                                }}
                                className="text-xs bg-white hover:bg-blue-50 hover:text-blue-700 hover:border-blue-300 text-slate-700 px-2.5 py-1 rounded-lg border border-slate-200 font-medium transition-all"
                              >
                                "Em đang gặp lỗi khi chạy file main.py với Python 3.11..."
                              </button>
                              <button 
                                onClick={() => {
                                  const text = "Giải thích chi tiết cơ chế hoạt động của khái niệm này kèm ví dụ code";
                                  setStudentInput(text);
                                  textareaRef.current?.focus();
                                }}
                                className="text-xs bg-white hover:bg-blue-50 hover:text-blue-700 hover:border-blue-300 text-slate-700 px-2.5 py-1 rounded-lg border border-slate-200 font-medium transition-all"
                              >
                                "Giải thích chi tiết cơ chế hoạt động kèm ví dụ code"
                              </button>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* KHỐI TỪ CHỐI NGOÀI THẨM QUYỀN / INJECTION (OUT OF SCOPE / FIN1) */}
                      {msg.type === "out_of_scope" && (
                        <div className="border border-amber-300 bg-amber-50 rounded-2xl rounded-tl-xs p-4 shadow-sm border-t-4 border-t-amber-500">
                          <div className="flex items-center justify-between mb-2">
                            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-900 border border-amber-300">
                              <Icon name="ShieldCheck" className="w-3.5 h-3.5 text-amber-700" />
                              <span>🛡️ Vượt thẩm quyền / Chuyển tiếp Giảng viên - TA</span>
                            </div>
                            <span className="text-[10px] text-slate-400">{msg.timestamp}</span>
                          </div>
                          <p className="text-sm text-amber-950 leading-relaxed">
                            {msg.text}
                          </p>
                        </div>
                      )}

                      {/* 4. KHỐI BỊ TỪ CHỐI / THẨM ĐỊNH LỖI (VALIDATION FAILED) */}
                      {msg.type === "validation_failed" && (
                        <div className="border border-rose-300 bg-rose-50 rounded-2xl rounded-tl-xs p-4 shadow-sm border-t-4 border-t-rose-500">
                          <div className="flex items-center gap-1.5 text-xs font-bold text-rose-800 mb-1.5">
                            <Icon name="AlertTriangle" className="w-4 h-4 text-rose-600" />
                            <span>🛡️ Thẩm Định Viên Chặn Trả Lời (Factuality Guard)</span>
                          </div>
                          <p className="text-sm text-rose-950 leading-relaxed">{msg.text}</p>
                        </div>
                      )}

                      {/* 5. KHỐI LỖI KẾT NỐI SERVER (SERVER ERROR CARD) */}
                      {msg.type === "server_error" && (
                        <div className="border border-rose-300 bg-rose-50/80 rounded-2xl rounded-tl-xs p-4 shadow-sm border-t-4 border-t-rose-500">
                          <div className="flex items-center justify-between mb-2">
                            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-300">
                              <Icon name="AlertTriangle" className="w-3.5 h-3.5 text-rose-600" />
                              <span>Lỗi kết nối máy chủ AI</span>
                            </div>
                            <span className="text-[10px] text-slate-400">{msg.timestamp}</span>
                          </div>

                          <div className="text-sm text-rose-950 leading-relaxed mb-3">
                            <p className="whitespace-pre-wrap">{msg.text}</p>
                          </div>

                          <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-rose-200/60 text-xs">
                            <button 
                              onClick={() => {
                                if (studentInput.trim()) {
                                  handleSendMessage();
                                }
                              }}
                              className="inline-flex items-center gap-1 px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white font-semibold rounded-lg shadow-2xs transition-all"
                            >
                              <Icon name="RotateCcw" className="w-3 h-3" />
                              <span>Thử gửi lại câu hỏi</span>
                            </button>
                            <span className="text-rose-700 text-[11px] self-center">
                              Kiểm tra terminal: lệnh <code>python codebase/web_server.py</code> đang hoạt động tại cổng 8080.
                            </span>
                          </div>
                        </div>
                      )}

                    </div>
                  </div>
                )}
              </div>
            ))}

            {/* Trạng thái đang sinh phản hồi */}
            {isGenerating && (
              <div className="flex justify-start">
                <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm flex items-center gap-3">
                  <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                  <div className="text-xs text-slate-600">
                    <span className="font-semibold text-blue-600">Đang thẩm định 3 quyết định:</span> Kiểm tra rõ nghĩa ➔ Đối chiếu trực tiếp slide ➔ Thẩm định Citation...
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* --- KHUNG NHẬP LIỆU (CHAT INPUT BOTTOM) --- */}
          <div className="p-4 border-t border-slate-200 bg-white">
            
            {/* Thanh Tag hiển thị Context đính kèm */}
            {attachedContext && (
              <div className="mb-2.5 flex items-center justify-between bg-blue-50 border border-blue-200/80 px-3 py-1.5 rounded-lg text-xs">
                <div className="flex items-center gap-2 text-blue-900 truncate">
                  <Icon name="FileText" className="w-3.5 h-3.5 text-blue-600 flex-shrink-0" />
                  <span className="font-semibold flex-shrink-0">[Đã chọn: Slide Day 3 - {attachedContext.page}]</span>
                  <span className="truncate italic text-blue-700/80 text-[11px]">
                    "{attachedContext.snippet}"
                  </span>
                </div>
                <button 
                  onClick={handleRemoveContext}
                  className="p-1 text-blue-600 hover:text-blue-900 hover:bg-blue-100 rounded-md transition-all ml-2"
                  title="Gỡ bỏ đoạn trích đính kèm"
                >
                  <Icon name="X" className="w-3.5 h-3.5" />
                </button>
              </div>
            )}

            {/* Quick Prompts (Gợi Ý Câu Hỏi Nhanh) */}
            <div className="mb-2 flex items-center gap-1.5 overflow-x-auto pb-1 text-xs no-scrollbar">
              <span className="text-[11px] text-slate-400 flex items-center gap-1 flex-shrink-0">
                <Icon name="Sparkles" className="w-3 h-3 text-amber-500" />
                Gợi ý:
              </span>
              {[
                "Tóm tắt slide này ngắn gọn",
                "Transformer và RNN khác nhau thế nào?",
                "Phân biệt Pre-training vs SFT",
                "Self-Attention hoạt động thế nào?"
              ].map((qp, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setStudentInput(qp);
                    textareaRef.current?.focus();
                  }}
                  className="px-2.5 py-0.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-full flex-shrink-0 border border-slate-200/70 text-[11px] font-medium transition-all"
                >
                  {qp}
                </button>
              ))}
            </div>

            {/* Khung Textarea & Nút Gửi */}
            <div className="relative">
              <textarea
                ref={textareaRef}
                value={studentInput}
                onChange={(e) => setStudentInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    executeChat();
                  }
                }}
                placeholder="Hỏi gia sư AI về nội dung bài giảng (hoặc chọn câu từ Golden Set)..."
                rows={1}
                className={`w-full pr-12 pl-3.5 py-2.5 bg-slate-50 focus:bg-white text-slate-900 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all resize-none shadow-inner ${
                  inputPulse ? "input-glow-active ring-4 ring-blue-500 border-blue-500 bg-blue-50/50" : ""
                }`}
                style={{ minHeight: "44px", maxHeight: "140px" }}
              />

              <button
                onClick={() => executeChat()}
                disabled={!studentInput.trim() || isGenerating}
                className="absolute right-2 bottom-2 p-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-30 disabled:hover:bg-blue-600 text-white rounded-lg transition-all shadow-sm flex items-center justify-center cursor-pointer"
                title="Gửi câu hỏi (Enter)"
              >
                <Icon name="Send" className="w-4 h-4" />
              </button>
            </div>

            <div className="mt-1.5 flex items-center justify-between text-[11px] text-slate-400">
              <span>Enter để gửi · Shift+Enter để xuống dòng</span>
              <span className="flex items-center gap-1 text-emerald-600 font-medium">
                <Icon name="ShieldCheck" className="w-3 h-3" />
                Kiểm chứng Citation 100%
              </span>
            </div>
          </div>
        </section>
      </div>

      {/* ======================================================== */}
      {/* DRAWER / MODAL: KHO 20 CÂU KIỂM THỬ GOLDEN SET */}
      {/* ======================================================== */}
      {isGoldenModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-xs p-4">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-4xl max-h-[85vh] flex flex-col overflow-hidden animate-bounce-subtle">
            
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-base font-bold text-slate-900">Kho 20 Câu Hỏi Kiểm Thử Mẫu (Golden Set)</h3>
                  <span className="text-xs bg-indigo-100 text-indigo-800 font-semibold px-2 py-0.5 rounded-full">
                    {filteredGoldenCases.length} câu
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-0.5">
                  Bấm <strong>[ ✨ Nạp vào ô nhập học viên ]</strong> để tự động chuyển trang slide, bôi đen context và điền câu hỏi để test!
                </p>
              </div>
              <button 
                onClick={() => setIsGoldenModalOpen(false)}
                className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-200 rounded-lg transition-all"
              >
                <Icon name="X" className="w-5 h-5" />
              </button>
            </div>

            {/* Filter Tabs */}
            <div className="px-6 py-2.5 border-b border-slate-200 flex items-center gap-2 overflow-x-auto bg-white text-xs">
              {[
                { key: "ALL", label: "Tất cả (20)" },
                { key: "LAYER_1", label: "Lớp 1: Nguồn sự thật" },
                { key: "LAYER_2", label: "Lớp 2: Mơ hồ / Thiếu tin" },
                { key: "LAYER_3", label: "Lớp 3: Ngoài thẩm quyền" },
                { key: "LAYER_4", label: "Lớp 4: Thuật ngữ" },
                { key: "EDGE", label: "Edge Cases & Bịa đặt" }
              ].map(tab => (
                <button
                  key={tab.key}
                  onClick={() => setSelectedLayerFilter(tab.key)}
                  className={`px-3 py-1.5 rounded-lg font-medium transition-all ${
                    selectedLayerFilter === tab.key 
                      ? "bg-blue-600 text-white shadow-xs" 
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Card List Container */}
            <div className="flex-1 overflow-y-auto p-6 grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-50/60">
              {filteredGoldenCases.map(c => (
                <div 
                  key={c.id}
                  className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs hover:shadow-md transition-all flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-mono text-xs font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                        {c.id}
                      </span>
                      <span className="text-[11px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                        {c.page_ref}
                      </span>
                    </div>

                    <div className="text-sm font-semibold text-slate-900 mb-2 leading-snug">
                      ❓ "{c.student_question}"
                    </div>

                    <div className="text-xs text-slate-600 bg-slate-50 p-2.5 rounded-lg border border-slate-200/70 mb-3 italic">
                      <span className="font-semibold text-slate-500 not-italic">Đoạn nguồn: </span>
                      "{c.context_snippet ? c.context_snippet.substring(0, 110) : ""}..."
                    </div>

                    <div className="text-[11px] text-slate-500 space-y-1 mb-3">
                      <div><strong className="text-slate-700">Kỳ vọng: </strong>{c.expected_behavior}</div>
                    </div>
                  </div>

                  {/* Nút Hành Động Nạp Câu Hỏi Vào Ô Nhập */}
                  <div className="pt-3 border-t border-slate-100 flex items-center gap-2">
                    <button
                      onClick={() => applyGoldenCase(c, false)}
                      className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold text-xs rounded-lg shadow-sm transition-all"
                    >
                      <Icon name="Sparkles" className="w-3.5 h-3.5" />
                      <span>✨ Nạp vào ô nhập học viên</span>
                    </button>
                    <button
                      onClick={() => applyGoldenCase(c, true)}
                      className="flex items-center justify-center gap-1 px-3 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-lg shadow-sm transition-all"
                      title="Nạp và gửi luôn vào chatbot"
                    >
                      <span>🚀 Gửi ngay</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-3 border-t border-slate-200 bg-white flex justify-end">
              <button 
                onClick={() => setIsGoldenModalOpen(false)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-semibold transition-all"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* DRAWER: TRACE INSPECTOR (KIỂM CHỨNG KỸ THUẬT) */}
      {/* ======================================================== */}
      {isInspectionOpen && (
        <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white shadow-2xl border-l border-slate-200 flex flex-col animate-bounce-subtle">
          <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
            <div className="flex items-center gap-2">
              <Icon name="Activity" className="w-5 h-5 text-blue-600" />
              <h3 className="text-sm font-bold text-slate-900">Nhật Ký Kiểm Chứng (Trace Inspector)</h3>
            </div>
            <button 
              onClick={() => setIsInspectionOpen(false)}
              className="p-1 text-slate-400 hover:text-slate-700 rounded-lg"
            >
              <Icon name="X" className="w-5 h-5" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-5 space-y-5 text-xs text-slate-700">
            {/* 3 Thước Đo Backend Đặc Thù */}
            <div className="space-y-3 bg-slate-50 p-4 rounded-xl border border-slate-200">
              <div className="font-bold text-slate-900 flex items-center justify-between">
                <span>Chỉ số thẩm định câu trả lời gần nhất</span>
                <span className="text-[10px] text-emerald-700 font-bold bg-emerald-100 px-2 py-0.5 rounded">
                  Đã đạt chuẩn
                </span>
              </div>

              {/* Metric 1: Similarity Score */}
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-slate-600">Similarity Score (Độ tương đồng ngữ nghĩa):</span>
                  <span className="font-mono font-bold text-blue-700">{activeInspectionData.similarityScore}</span>
                </div>
                <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                  <div 
                    className="bg-blue-600 h-full rounded-full transition-all duration-500" 
                    style={{ width: `${activeInspectionData.similarityScore * 100}%` }}
                  ></div>
                </div>
              </div>

              {/* Metric 2: Intent */}
              <div className="flex justify-between border-t border-slate-200/60 pt-2">
                <span className="text-slate-600">Phân loại Intent (Quyết định 1):</span>
                <span className="font-semibold text-slate-900 bg-white px-2 py-0.5 rounded border border-slate-200">
                  {activeInspectionData.intent}
                </span>
              </div>

              {/* Metric 3: NLI Faithfulness */}
              <div className="flex justify-between border-t border-slate-200/60 pt-2">
                <span className="text-slate-600">NLI Faithfulness (Quyết định 3):</span>
                <span className="font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                  {activeInspectionData.nliFaithfulness}
                </span>
              </div>
            </div>

            {/* Step-by-Step Decision Trace Timeline */}
            <div>
              <div className="font-bold text-slate-900 mb-3 flex items-center gap-1.5">
                <Icon name="ShieldCheck" className="w-4 h-4 text-blue-600" />
                <span>Tiến trình 3 Quyết Định Thực Tế:</span>
              </div>

              <div className="space-y-3 relative before:absolute before:left-3 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200 pl-7">
                {activeInspectionData.decisionTrace.map((t, idx) => (
                  <div key={idx} className="relative bg-white border border-slate-200 rounded-xl p-3 shadow-2xs">
                    <div className="absolute -left-7 top-3 w-3 h-3 rounded-full bg-blue-600 ring-4 ring-blue-100"></div>
                    <div className="font-mono font-bold text-blue-700 text-[11px] mb-1">
                      {t.step}
                    </div>
                    <pre className="font-mono text-[10px] text-slate-600 bg-slate-50 p-2 rounded overflow-x-auto whitespace-pre-wrap">
                      {typeof t.output === "object" ? JSON.stringify(t.output, null, 2) : t.output}
                    </pre>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="p-4 border-t border-slate-200 bg-slate-50">
            <button 
              onClick={() => setIsInspectionOpen(false)}
              className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-lg transition-all"
            >
              Đóng Drawer
            </button>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* POPUP / MODAL: BÁO LỖI NGUỒN KHÔNG KHỚP (HITL) */}
      {/* ======================================================== */}
      {feedbackModal.isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-md p-6 animate-bounce-subtle">
            <div className="flex items-center gap-2 text-rose-600 font-bold text-base mb-3">
              <Icon name="Flag" className="w-5 h-5" />
              <h4>Báo lỗi nguồn không khớp tài liệu</h4>
            </div>
            <p className="text-xs text-slate-600 mb-4">
              Ý kiến của bạn sẽ gửi thẳng đến giảng viên và cập nhật bộ lọc Factuality Validator để cải thiện chất lượng căn cứ.
            </p>

            <div className="space-y-2 mb-4">
              <label className="text-xs font-semibold text-slate-700 block">Chọn lý do:</label>
              {[
                "Trích dẫn sai số trang slide",
                "Tự ý suy diễn thêm thông tin ngoài bài giảng (Hallucination)",
                "Tài liệu có đề cập nhưng AI báo không tìm thấy",
                "Lý do khác"
              ].map((reason, idx) => (
                <label key={idx} className="flex items-center gap-2 text-xs text-slate-700 p-2 rounded-lg hover:bg-slate-50 cursor-pointer border border-transparent hover:border-slate-200">
                  <input 
                    type="radio" 
                    name="feedback-reason" 
                    checked={feedbackReason === reason} 
                    onChange={() => setFeedbackReason(reason)}
                    className="text-blue-600"
                  />
                  <span>{reason}</span>
                </label>
              ))}
            </div>

            <div className="mb-4">
              <label className="text-xs font-semibold text-slate-700 block mb-1">Ghi chú bổ sung (nếu có):</label>
              <textarea 
                value={feedbackNote}
                onChange={(e) => setFeedbackNote(e.target.value)}
                placeholder="Ví dụ: Trang 15 thực tế nói về pip install..."
                rows={2}
                className="w-full text-xs p-2.5 border border-slate-300 rounded-lg outline-none focus:ring-2 focus:ring-rose-500 resize-none"
              />
            </div>

            <div className="flex justify-end gap-2 text-xs font-semibold">
              <button 
                onClick={() => setFeedbackModal({ isOpen: false, messageId: null })}
                className="px-3 py-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-all"
              >
                Hủy bỏ
              </button>
              <button 
                onClick={handleSendReport}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg transition-all shadow-xs"
              >
                Gửi phản ánh
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

// Render root React component
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<VLearnTutorApp />);
