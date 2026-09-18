'use client';

import React, { useState, useEffect, useRef, useMemo } from 'react';
import {
  GraduationCap,
  BookOpen,
  Bot,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  Send,
  ChevronLeft,
  ChevronRight,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  ExternalLink,
  ThumbsUp,
  Flag,
  Activity,
  Layers,
  X,
  FileText,
  ShieldCheck,
} from 'lucide-react';

// --- TYPES ---
interface SlideData {
  title: string;
  content: string;
  course?: string;
}

interface GoldenCase {
  id: string;
  layer: string;
  question_type: string;
  page_ref: string;
  context_snippet: string;
  student_question: string;
  expected_decision_flow?: string;
  expected_behavior?: string;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  type?: 'grounded' | 'fallback' | 'clarification' | 'validation_failed';
  text: string;
  pageRef?: string;
  citation?: string;
  quotedSnippet?: string;
  contextAttached?: string | null;
  timestamp: string;
}

const DEFAULT_SLIDES: Record<string, SlideData> = {
  'Trang 1': {
    title: 'Day 1 — LLM Foundation & AI Product Thinking',
    content:
      'Chào mừng các bạn đến với khoá học AI Product Hackathon.\nNội dung chính Day 1: Xây dựng nền tảng tư duy sản phẩm AI, hiểu giới hạn của mô hình ngôn ngữ lớn và phương pháp đo lường chất lượng giải pháp.\nLưu ý quy chế lớp học: Lộ trình từ CP1 đến CP6 kết thúc lúc 21:00. Mọi vấn đề xin lùi hạn, điểm danh cần liên hệ TA.',
    course: 'Khoá K4 — AI Thực Chiến',
  },
  'Trang 15': {
    title: 'Cài đặt môi trường & Thư viện SDK',
    content:
      "Hướng dẫn cài đặt môi trường lập trình Python cho AI.\nLỗi thường gặp khi thiếu thư viện: ModuleNotFoundError: No module named 'google.genai'.\nCách khắc phục chuẩn xác: Chạy lệnh 'pip install google-genai' trong terminal của môi trường ảo.",
    course: 'Khoá K4 — AI Thực Chiến',
  },
  'Trang 21': {
    title: 'Kiến trúc RNN so với Transformer',
    content:
      'RNN xử lý tuần tự từng từ một nên chậm và khó bắt phụ thuộc xa.\nTransformer sử dụng cơ chế Self-Attention cho phép xử lý toàn bộ các từ cùng một lúc (song song).',
    course: 'Khoá K4 — AI Thực Chiến',
  },
  'Trang 38': {
    title: 'Quy trình huấn luyện LLM: Pre-training vs SFT',
    content:
      'Giai đoạn 1: Pre-training là đọc cả thư viện hàng nghìn tỷ token để học ngữ pháp và tri thức tổng quát.\nGiai đoạn 2: SFT (Supervised Fine-Tuning) dạy mô hình học cách hội thoại và tuân thủ chỉ thị của con người.',
    course: 'Khoá K4 — AI Thực Chiến',
  },
};

export default function VLearnTutorPage() {
  const [slides, setSlides] = useState<Record<string, SlideData>>(DEFAULT_SLIDES);
  const [currentPage, setCurrentPage] = useState('Trang 1');
  const [zoomLevel, setZoomLevel] = useState(100);
  const [sourceAnchorPulse, setSourceAnchorPulse] = useState(false);
  const [anchorSnippet, setAnchorSnippet] = useState('');

  // Golden set modal state
  const [goldenCases, setGoldenCases] = useState<GoldenCase[]>([]);
  const [isGoldenModalOpen, setIsGoldenModalOpen] = useState(false);
  const [selectedLayerFilter, setSelectedLayerFilter] = useState('ALL');

  // Text selection & Attached context state
  const [activeSelection, setActiveSelection] = useState({
    text: '',
    page: '',
  });
  const [attachedContext, setAttachedContext] = useState<{ page: string; snippet: string } | null>(null);

  // Chatbot conversation state
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome-1',
      role: 'assistant',
      type: 'grounded',
      text: 'Chào bạn! Mình là Gia Sư AI VLearn. Mình giải đáp bài giảng dựa trên căn cứ thực tế từ các trang slide bài học. Bạn có thể bôi đen đoạn tài liệu bên trái hoặc chọn câu hỏi mẫu từ bộ Golden Set bên trên nhé!',
      pageRef: '',
      citation: '',
      quotedSnippet: '',
      timestamp: 'Vừa xong',
    },
  ]);
  const [studentInput, setStudentInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [inputPulse, setInputPulse] = useState(false);

  // Inspector state
  const [isInspectionOpen, setIsInspectionOpen] = useState(false);
  const [traceCount, setTraceCount] = useState(12);
  const [activeInspectionData, setActiveInspectionData] = useState({
    similarityScore: 0.95,
    intent: 'Sẵn sàng hỗ trợ (System Ready)',
    nliFaithfulness: 'Chờ truy vấn',
    decisionTrace: [
      { step: 'C_Quyet_dinh_1', output: { decision: 'READY', reason: 'Hệ thống sẵn sàng tiếp nhận câu hỏi của học viên.' } },
      { step: 'G_Quyet_dinh_2', output: { decision: 'READY', reason: 'Kho tri thức 58 slide và 648 transcript đã được nạp.' } },
    ],
  });

  // Toast message
  const [toast, setToast] = useState<{ message: string; type?: 'success' | 'info' } | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const showToast = (message: string, type: 'success' | 'info' = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  };

  useEffect(() => {
    fetch('/api/slides')
      .then((res) => res.json())
      .then((data) => {
        if (data && Object.keys(data).length > 0) {
          setSlides(data);
          if (!data[currentPage]) setCurrentPage(Object.keys(data)[0]);
        }
      })
      .catch(() => {});

    fetch('/api/golden_set')
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) setGoldenCases(data);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isGenerating]);

  // SỬA LỖI & HOÀN THIỆN: Nạp câu hỏi từ Golden Set vào ô nhập của học viên
  const applyGoldenCase = (c: GoldenCase, autoSend = false) => {
    if (!c) return;

    let targetPage = c.page_ref || 'Trang 1';
    if (targetPage.includes('và')) {
      targetPage = targetPage.split('và')[0].trim();
    }
    if (slides[targetPage]) {
      setCurrentPage(targetPage);
    }

    const snippet = c.context_snippet || (slides[targetPage] ? slides[targetPage].content : '');
    setAttachedContext({
      page: c.page_ref || targetPage,
      snippet,
    });

    setAnchorSnippet(snippet);
    setStudentInput(c.student_question);
    setIsGoldenModalOpen(false);

    setInputPulse(true);
    setTimeout(() => setInputPulse(false), 2000);

    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.focus();
        textareaRef.current.style.height = 'auto';
        textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
      }
    }, 100);

    showToast(`✨ Đã nạp thành công câu hỏi [${c.id}] vào ô nhập của học viên!`);

    if (autoSend) {
      setTimeout(() => {
        executeChat(c.student_question, snippet, c.page_ref || targetPage, c.id);
      }, 300);
    }
  };

  const handleCitationClick = (pageRef: string, snippet?: string) => {
    const cleanPage = pageRef.replace(/[\[\]↗]/g, '').trim();
    let target = cleanPage;
    if (target.toLowerCase().startsWith('trang')) {
      const num = target.replace(/\D/g, '');
      target = `Trang ${num}`;
    }
    if (slides[target]) setCurrentPage(target);

    if (snippet) setAnchorSnippet(snippet);
    setSourceAnchorPulse(true);
    setTimeout(() => setSourceAnchorPulse(false), 2500);

    showToast(`Đã neo đến nguồn tài liệu tại ${target}!`, 'info');
  };

  const executeChat = async (qText?: string, snippetText?: string, pageName?: string, turnId?: string) => {
    const question = (qText || studentInput).trim();
    if (!question || isGenerating) return;

    const currentSnippet = snippetText !== undefined ? snippetText : (attachedContext ? attachedContext.snippet : '');
    const currentPageRef = pageName || (attachedContext ? attachedContext.page : currentPage);

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      text: question,
      contextAttached: attachedContext ? `${attachedContext.page}` : null,
      timestamp: 'Bây giờ',
    };

    setMessages((prev) => [...prev, userMsg]);
    setStudentInput('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
    setIsGenerating(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          context_snippet: currentSnippet,
          page_ref: currentPageRef,
          turn_id: turnId || `WEB_TURN_${Date.now()}`,
        }),
      });

      const data = await res.json();
      setIsGenerating(false);

      let cardType: 'grounded' | 'fallback' | 'clarification' | 'validation_failed' = 'grounded';
      if (data.final_status === 'INSUFFICIENT_GROUNDING') {
        cardType = 'fallback';
      } else if (data.final_status === 'CLARIFICATION_OR_OUT_OF_SCOPE' || data.final_status === 'AMBIGUOUS' || data.final_status === 'OUT_OF_SCOPE') {
        cardType = 'clarification';
      } else if (data.final_status === 'VALIDATION_FAILED_HALLUCINATION') {
        cardType = 'validation_failed';
      }

      const aiMsg: ChatMessage = {
        id: `ai-${Date.now()}`,
        role: 'assistant',
        type: cardType,
        text: data.final_response || 'Không có phản hồi từ máy chủ.',
        pageRef: currentPageRef,
        citation: `[${currentPageRef} ↗]`,
        quotedSnippet: currentSnippet,
        timestamp: 'Vừa xong',
      };

      setMessages((prev) => [...prev, aiMsg]);
      setTraceCount((prev) => prev + 1);
    } catch (err) {
      setIsGenerating(false);
      setMessages((prev) => [
        ...prev,
        {
          id: `ai-err-${Date.now()}`,
          role: 'assistant',
          type: 'fallback',
          text: 'Lỗi kết nối máy chủ AI.',
          pageRef: currentPageRef,
          timestamp: 'Vừa xong',
        },
      ]);
    }
  };

  const currentSlideData = slides[currentPage] || {
    title: 'Trang tài liệu',
    content: 'Nội dung đang được nạp...',
    course: 'Khoá K4 — AI Thực Chiến',
  };

  const slideKeys = Object.keys(slides);
  const currentSlideIndex = slideKeys.indexOf(currentPage);

  return (
    <div className="h-screen flex flex-col bg-slate-100 text-slate-800 font-sans antialiased overflow-hidden">
      {/* Toast */}
      {toast && (
        <div className="fixed top-4 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-xl shadow-xl bg-emerald-600 text-white text-sm font-medium animate-bounce-subtle">
          <CheckCircle2 className="w-5 h-5" />
          <span>{toast.message}</span>
        </div>
      )}

      {/* Header */}
      <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between shadow-sm z-20 flex-shrink-0">
        <div className="flex items-center gap-4">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/20">
            <GraduationCap className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold text-slate-900">Gia Sư AI VLearn</h1>
              <span className="text-xs px-2 py-0.5 rounded-md font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                Trợ Lý Học Tập Có Căn Cứ
              </span>
            </div>
            <p className="text-xs text-slate-500">Khóa AI Thực Chiến K4 · Hệ thống RAG Kiểm chứng Citation thời gian thực</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Đang bảo vệ căn cứ (Grounded Mode)</span>
          </div>

          <button
            onClick={() => setIsGoldenModalOpen(true)}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-indigo-500 to-blue-600 text-white hover:from-indigo-600 hover:to-blue-700 shadow-sm transition-all"
          >
            <Layers className="w-4 h-4" />
            <span>Kho 20 câu Golden Set</span>
            <span className="bg-white/20 px-1.5 py-0.2 rounded-full text-[10px]">20</span>
          </button>

          <button
            onClick={() => setIsInspectionOpen(!isInspectionOpen)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-200"
          >
            <Activity className="w-4 h-4 text-blue-600" />
            <span>Trace Inspector</span>
            <span className="bg-slate-200 text-slate-800 px-1.5 py-0.2 rounded-full text-[10px] font-semibold">{traceCount}</span>
          </button>
        </div>
      </header>

      {/* Split-Screen Workspace: 6:4 Ratio */}
      <div className="flex-1 flex overflow-hidden">
        {/* 60% Left: Document Viewer */}
        <section className="w-3/5 border-r border-slate-200 flex flex-col bg-slate-100/70 relative">
          <div className="h-12 bg-white/90 backdrop-blur border-b border-slate-200 px-5 flex items-center justify-between z-10">
            <div className="flex items-center gap-1.5 text-xs text-slate-500 font-medium">
              <span className="text-slate-700 font-semibold">Khóa AI Thực Chiến</span>
              <span>&gt;</span>
              <span>Day 03</span>
              <span>&gt;</span>
              <span className="text-blue-600 flex items-center gap-1">
                <FileText className="w-3.5 h-3.5" />
                Slide_Agentic_RAG.pdf
              </span>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs">
                <button
                  onClick={() => currentSlideIndex > 0 && setCurrentPage(slideKeys[currentSlideIndex - 1])}
                  disabled={currentSlideIndex <= 0}
                  className="p-1 rounded hover:bg-white text-slate-600 disabled:opacity-30"
                >
                  <ChevronLeft className="w-3.5 h-3.5" />
                </button>
                <select
                  value={currentPage}
                  onChange={(e) => setCurrentPage(e.target.value)}
                  className="bg-transparent text-slate-800 font-medium px-2 py-0.5 outline-none text-xs cursor-pointer"
                >
                  {slideKeys.map((k) => (
                    <option key={k} value={k}>
                      {k} ({slides[k].title.substring(0, 24)}...)
                    </option>
                  ))}
                </select>
                <button
                  onClick={() => currentSlideIndex < slideKeys.length - 1 && setCurrentPage(slideKeys[currentSlideIndex + 1])}
                  disabled={currentSlideIndex >= slideKeys.length - 1}
                  className="p-1 rounded hover:bg-white text-slate-600 disabled:opacity-30"
                >
                  <ChevronRight className="w-3.5 h-3.5" />
                </button>
              </div>

              <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs">
                <button onClick={() => setZoomLevel((p) => Math.max(70, p - 10))} className="p-1 rounded hover:bg-white text-slate-600">
                  <ZoomOut className="w-3.5 h-3.5" />
                </button>
                <span className="px-1 font-mono text-[11px] text-slate-700">{zoomLevel}%</span>
                <button onClick={() => setZoomLevel((p) => Math.min(140, p + 10))} className="p-1 rounded hover:bg-white text-slate-600">
                  <ZoomIn className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>

          <div className="flex-1 overflow-auto p-8 flex justify-center items-start">
            <div
              style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: 'top center' }}
              className="w-full max-w-2xl bg-white rounded-2xl shadow-md border border-slate-200 p-8 min-h-[520px] flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-5">
                  <span className="text-xs font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2.5 py-1 rounded-md border border-blue-100">
                    {currentSlideData.course}
                  </span>
                  <span className="text-xs font-mono font-bold text-slate-600 bg-slate-100 px-2 py-0.5 rounded">{currentPage}</span>
                </div>

                <h2 className="text-2xl font-extrabold text-slate-900 mb-6">{currentSlideData.title}</h2>

                <div className="space-y-4 text-slate-700 text-sm leading-relaxed">
                  {currentSlideData.content.split('\n').map((line, idx) => {
                    const isAnchor = anchorSnippet && line.toLowerCase().includes(anchorSnippet.substring(0, 20).toLowerCase());
                    return (
                      <p
                        key={idx}
                        className={`p-1.5 rounded transition-all duration-700 ${
                          sourceAnchorPulse && isAnchor ? 'bg-emerald-100 text-emerald-950 ring-2 ring-emerald-500 font-medium' : ''
                        }`}
                      >
                        {line}
                      </p>
                    );
                  })}
                </div>

                <div className="mt-8 pt-4 border-t border-slate-100">
                  <div className="text-xs font-semibold text-slate-500 mb-2 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                    <span>Đoạn trích kỹ thuật trọng tâm:</span>
                  </div>
                  <div className="bg-amber-50/90 border-l-4 border-amber-400 p-4 rounded-r-xl">
                    <p className="text-xs text-amber-950 font-mono select-text">"{activeSelection.text}"</p>
                    <button
                      onClick={() => {
                        setAttachedContext({ page: currentPage, snippet: activeSelection.text });
                        showToast(`Đã đính kèm đoạn trích tại ${currentPage}!`);
                        textareaRef.current?.focus();
                      }}
                      className="mt-3 inline-flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-amber-500 to-amber-600 text-white text-xs font-bold rounded-lg shadow-sm hover:from-amber-600 hover:to-amber-700"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>+ Hỏi AI về đoạn này</span>
                    </button>
                  </div>
                </div>
              </div>

              <div className="mt-8 pt-4 border-t border-slate-100 flex justify-between text-xs text-slate-400">
                <span>VLearn AI Academic Platform © 2026</span>
                <span className="font-mono">Tài liệu bảo chứng căn cứ</span>
              </div>
            </div>
          </div>
        </section>

        {/* 40% Right: Chatbot */}
        <section className="w-2/5 flex flex-col bg-white">
          <div className="h-12 border-b border-slate-200 px-5 flex items-center justify-between bg-slate-50/80">
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></div>
              <span className="text-xs font-bold text-slate-800">Hội Thoại Gia Sư AI</span>
            </div>
            <span className="text-[11px] text-slate-500 font-medium">Gemini 2.5 Flash</span>
          </div>

          <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-slate-50/40">
            {messages.map((msg) => (
              <div key={msg.id} className="space-y-1">
                {msg.role === 'user' ? (
                  <div className="flex justify-end">
                    <div className="max-w-[85%] bg-blue-600 text-white rounded-2xl rounded-tr-xs px-4 py-3 shadow-sm text-sm">
                      {msg.contextAttached && (
                        <div className="text-[11px] font-mono text-blue-200 mb-1 flex items-center gap-1">
                          <FileText className="w-3 h-3" />
                          <span>Tham chiếu: {msg.contextAttached}</span>
                        </div>
                      )}
                      <p className="leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                    </div>
                  </div>
                ) : (
                  <div className="flex justify-start">
                    <div className="max-w-[92%] w-full">
                      {msg.type === 'grounded' && (
                        <div className="bg-white border border-emerald-200 rounded-2xl p-4 shadow-sm border-t-4 border-t-emerald-500">
                          <div className="flex items-center justify-between mb-2">
                            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200">
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                              ✓ Có căn cứ xác thực
                            </span>
                            <span className="text-[10px] text-slate-400">{msg.timestamp}</span>
                          </div>
                          <p className="text-sm text-slate-800 leading-relaxed inline">{msg.text} </p>
                          {msg.pageRef && (
                            <button
                              onClick={() => handleCitationClick(msg.pageRef!, msg.quotedSnippet)}
                              className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-bold text-emerald-700 bg-emerald-100 hover:bg-emerald-200 rounded-md border border-emerald-300 ml-1.5"
                            >
                              {msg.citation || `[${msg.pageRef} ↗]`}
                            </button>
                          )}
                          <div className="mt-3.5 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                            <span className="text-slate-400 text-[11px]">Đánh giá:</span>
                            <div className="flex items-center gap-2">
                              <button onClick={() => showToast('Cảm ơn bạn đã phản hồi! 👍')} className="flex items-center gap-1 px-2 py-1 rounded text-slate-600 hover:bg-emerald-50 border border-slate-200">
                                <ThumbsUp className="w-3 h-3 text-emerald-600" />
                                <span>Hữu ích 👍</span>
                              </button>
                              <button onClick={() => showToast('Đã gửi phản ánh tới giảng viên! ⚠️', 'info')} className="flex items-center gap-1 px-2 py-1 rounded text-slate-600 hover:bg-rose-50 border border-slate-200">
                                <Flag className="w-3 h-3 text-rose-500" />
                                <span>Báo lỗi nguồn ⚠️</span>
                              </button>
                            </div>
                          </div>
                        </div>
                      )}

                      {msg.type === 'fallback' && (
                        <div className="border border-amber-300 bg-amber-50/70 rounded-2xl p-4 shadow-sm border-t-4 border-t-amber-500">
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 border border-amber-300 mb-2">
                            <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                            ⚠️ Chưa đủ căn cứ trong bài học
                          </span>
                          <p className="text-sm text-amber-950 leading-relaxed mb-3">{msg.text}</p>
                          <div className="flex gap-2 pt-2 border-t border-amber-200/60 text-xs">
                            <a href="https://discord.com" target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 px-3 py-1.5 bg-indigo-600 text-white font-semibold rounded-lg">
                              Hỏi TA trên Discord #lab-support <ExternalLink className="w-3 h-3" />
                            </a>
                            <button onClick={() => setCurrentPage(currentPage === 'Trang 15' ? 'Trang 38' : 'Trang 15')} className="px-3 py-1.5 bg-white text-amber-900 font-semibold rounded-lg border border-amber-300">
                              Đổi đoạn tài liệu khác
                            </button>
                          </div>
                        </div>
                      )}

                      {msg.type === 'clarification' && (
                        <div className="border border-slate-300 bg-slate-50 rounded-2xl p-4 shadow-sm border-t-4 border-t-slate-400">
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-200 text-slate-800 border border-slate-300 mb-2">
                            <HelpCircle className="w-3.5 h-3.5 text-slate-600" />
                            ❓ Yêu cầu làm rõ ngữ cảnh
                          </span>
                          <p className="text-sm text-slate-800 leading-relaxed">{msg.text}</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Bottom Chat Input */}
          <div className="p-4 border-t border-slate-200 bg-white">
            {attachedContext && (
              <div className="mb-2.5 flex items-center justify-between bg-blue-50 border border-blue-200 px-3 py-1.5 rounded-lg text-xs">
                <div className="flex items-center gap-2 text-blue-900 truncate">
                  <FileText className="w-3.5 h-3.5 text-blue-600" />
                  <span className="font-semibold">[Đã chọn: Slide Day 3 - {attachedContext.page}]</span>
                  <span className="truncate italic text-blue-700/80 text-[11px]">"{attachedContext.snippet}"</span>
                </div>
                <button onClick={() => setAttachedContext(null)} className="p-1 text-blue-600 hover:text-blue-900">
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            )}

            <div className="relative">
              <textarea
                ref={textareaRef}
                value={studentInput}
                onChange={(e) => setStudentInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    executeChat();
                  }
                }}
                placeholder="Hỏi gia sư AI về nội dung bài giảng (hoặc chọn câu từ Golden Set)..."
                rows={1}
                className={`w-full pr-12 pl-3.5 py-2.5 bg-slate-50 text-slate-900 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all resize-none ${
                  inputPulse ? 'ring-4 ring-blue-500 border-blue-500 bg-blue-50/50' : ''
                }`}
              />
              <button
                onClick={() => executeChat()}
                disabled={!studentInput.trim() || isGenerating}
                className="absolute right-2 bottom-2 p-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-30 text-white rounded-lg transition-all"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </section>
      </div>

      {/* Golden Set Modal with 1-click Injection */}
      {isGoldenModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 p-4">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-4xl max-h-[85vh] flex flex-col overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <h3 className="text-base font-bold text-slate-900">Kho 20 Câu Hỏi Kiểm Thử Mẫu (Golden Set)</h3>
              <button onClick={() => setIsGoldenModalOpen(false)}>
                <X className="w-5 h-5 text-slate-400 hover:text-slate-700" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6 grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-50/60">
              {goldenCases.map((c) => (
                <div key={c.id} className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs flex flex-col justify-between">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="font-mono text-xs font-bold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">{c.id}</span>
                      <span className="text-[11px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded">{c.page_ref}</span>
                    </div>
                    <div className="text-sm font-semibold text-slate-900 mb-2">❓ "{c.student_question}"</div>
                    <div className="text-xs text-slate-600 bg-slate-50 p-2.5 rounded-lg border mb-3 italic">"{c.context_snippet}..."</div>
                  </div>
                  <div className="pt-3 border-t border-slate-100 flex gap-2">
                    <button
                      onClick={() => applyGoldenCase(c, false)}
                      className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold text-xs rounded-lg shadow-sm"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>✨ Nạp vào ô nhập học viên</span>
                    </button>
                    <button
                      onClick={() => applyGoldenCase(c, true)}
                      className="px-3 py-2 bg-emerald-600 text-white font-bold text-xs rounded-lg shadow-sm"
                    >
                      🚀 Gửi ngay
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
