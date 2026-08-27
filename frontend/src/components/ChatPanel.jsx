import React, { useState, useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';

const SAMPLE_QUERIES = [
  "What is Microsoft annual revenue and Azure growth in Item 7?",
  "What are NVIDIA primary Risk Factors in Item 1A?",
  "Analyze Apple Services gross margin and R&D expenses.",
  "What are Tesla automotive gross margin trends and risk factors?"
];

export default function ChatPanel({ messages, onSendMessage, isSending, documentsCount }) {
  const [inputQuery, setInputQuery] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputQuery.trim() || isSending) return;
    onSendMessage(inputQuery.trim());
    setInputQuery('');
  };

  const handleSelectSample = (sample) => {
    if (isSending) return;
    onSendMessage(sample);
  };

  return (
    <section id="rag-terminal" className="bg-[#E8E6DF] border-b border-[#151515]/16 p-6 md:p-12">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Section Header Tag */}
        <div className="border-b border-[#151515]/16 pb-4 flex flex-wrap items-center justify-between gap-4 font-mono text-[10px] uppercase tracking-[0.14em]">
          <div className="flex items-center gap-2 text-[#C4442C]">
            <span className="w-2 h-2 bg-[#C4442C]" />
            <span>[SECTION 01 // QUANTITATIVE QUERY TERMINAL]</span>
          </div>
          <span className="text-[#75736C]">INDEXED VECTOR KNOWLEDGE: {documentsCount} DOCUMENTS</span>
        </div>

        {/* Headline mixing SOLID and OUTLINED words */}
        <div className="space-y-2">
          <h2 className="font-display font-extrabold text-3xl md:text-5xl tracking-tighter text-[#151515]">
            QUANTITATIVE <span className="text-outline">QUERY</span> ENGINE
          </h2>
          <p className="font-palatino text-[14px] text-[#494844] max-w-3xl leading-relaxed">
            Execute natural language financial analysis across ingested SEC 10-K filings and uploaded PDFs. Powered by hybrid BM25 + Dense RRF retrieval and Groq Llama-3 reasoning.
          </p>
        </div>

        {/* Sample Quick Query Chips */}
        <div className="space-y-2">
          <span className="text-[9px] font-mono uppercase tracking-[0.14em] text-[#75736C] block">
            [SELECT SAMPLE SEC 10-K QUERY]
          </span>
          <div className="flex flex-wrap gap-2">
            {SAMPLE_QUERIES.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleSelectSample(q)}
                disabled={isSending}
                className="bg-[#DEDBD2] hover:bg-[#151515] hover:text-[#E8E6DF] text-[#151515] border border-[#151515]/20 px-3 py-1.5 font-mono text-[9.5px] uppercase tracking-[0.1em] transition-colors text-left"
              >
                [{String(idx + 1).padStart(2, '0')}] {q}
              </button>
            ))}
          </div>
        </div>

        {/* Terminal Output Display Area */}
        <div className="bg-[#DEDBD2] border border-[#151515]/20 min-h-[380px] max-h-[550px] overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-64 flex flex-col items-center justify-center text-center space-y-3 text-[#75736C] font-mono">
              <div className="w-4 h-4 bg-[#C4442C]/40 animate-pulse" />
              <p className="text-[11px] uppercase tracking-[0.14em]">
                NO ACTIVE QUERIES IN CURRENT SESSION
              </p>
              <p className="text-[9.5px] text-[#494844] max-w-md">
                Select a sample query above or type a financial question into the prompt terminal below to begin analyzing SEC 10-K statements.
              </p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <MessageBubble key={index} message={msg} />
            ))
          )}

          {isSending && (
            <div className="bg-[#E8E6DF] border border-[#151515]/20 p-4 font-mono text-[10px] text-[#C4442C] flex items-center gap-3">
              <span className="w-2 h-2 bg-[#C4442C] animate-ping" />
              <span className="uppercase tracking-[0.14em]">
                EXECUTING HYBRID VECTOR RETRIEVAL & GROQ LLAMA-3 REASONING...
              </span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Prompt Input Terminal Bar */}
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Type your financial query (e.g. 'What is Microsoft revenue growth in Item 7?')..."
            disabled={isSending}
            className="flex-1 bg-[#E8E6DF] border border-[#151515]/30 focus:border-[#C4442C] px-4 py-3.5 font-palatino text-[14px] text-[#151515] placeholder-[#75736C] outline-none"
          />
          <button
            type="submit"
            disabled={isSending || !inputQuery.trim()}
            className="bg-[#151515] hover:bg-[#C4442C] text-[#E8E6DF] disabled:opacity-50 border border-[#151515] px-6 py-3.5 font-mono text-[10.5px] uppercase tracking-[0.14em] transition-colors whitespace-nowrap"
          >
            {isSending ? '[PROCESSING...]' : '[SUBMIT QUERY]'}
          </button>
        </form>

      </div>
    </section>
  );
}
