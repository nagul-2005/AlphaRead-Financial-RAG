import React, { useState } from 'react';

export default function MessageBubble({ message }) {
  const isUser = message.sender === 'user';
  const [showCitations, setShowCitations] = useState(true);

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} my-4`}>
      <div className={`w-full max-w-4xl space-y-2 ${isUser ? 'items-end' : 'items-start'}`}>
        
        {/* Paper Header Strip */}
        <div className={`flex items-center gap-3 font-mono text-[9.5px] uppercase tracking-[0.14em] ${
          isUser ? 'justify-end text-[#C4442C]' : 'justify-start text-[#494844]'
        }`}>
          <span className={`w-1.5 h-1.5 ${isUser ? 'bg-[#C4442C]' : 'bg-[#151515]'}`} />
          <span>{isUser ? '[USER QUERY]' : '[ALPHAREAD INTELLIGENCE OUPUT]'}</span>
          <span className="text-[#75736C]">{message.timestamp || '00:00'}</span>
        </div>

        {/* Paper Message Container */}
        <div className={`p-5 font-mono text-[11px] leading-relaxed border transition-colors ${
          isUser
            ? 'bg-[#151515] text-[#E8E6DF] border-[#151515]'
            : 'bg-[#E8E6DF] text-[#151515] border-[#151515]/25'
        }`}>
          <div className="whitespace-pre-wrap tracking-[0.04em]">
            {message.text}
          </div>

          {/* Source Citations Section */}
          {!isUser && message.citations && message.citations.length > 0 && (
            <div className="mt-5 pt-4 border-t border-[#151515]/20 space-y-3">
              <button
                onClick={() => setShowCitations(!showCitations)}
                className="flex items-center justify-between w-full font-mono text-[9.5px] uppercase tracking-[0.14em] text-[#C4442C] bg-[#DEDBD2] hover:bg-[#151515] hover:text-[#E8E6DF] p-2.5 border border-[#151515]/20 transition-colors"
              >
                <span>[RAG SOURCE CITATIONS: {message.citations.length} CHUNKS]</span>
                <span>{showCitations ? '[- HIDE]' : '[+ EXPAND]'}</span>
              </button>

              {showCitations && (
                <div className="space-y-2.5">
                  {message.citations.map((citation, idx) => {
                    const score = citation.relevance_score;
                    const pct = typeof score === 'number' ? Math.round(score * 100) : 85;
                    return (
                      <div
                        key={idx}
                        className="bg-[#DEDBD2] border border-[#151515]/20 p-3 space-y-2 text-[10px] font-mono"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[#151515]/16 pb-2">
                          <span className="font-bold text-[#151515] uppercase tracking-[0.1em]" title={citation.document}>
                            [SRC {citation.source_id || idx + 1}] {citation.document}
                          </span>
                          <div className="flex items-center gap-3 text-[#75736C]">
                            <span>SEC/PAGE: {citation.section_or_page}</span>
                            <span className="bg-[#151515] text-[#E8E6DF] px-2 py-0.5 font-bold text-[9px]">
                              {pct}% MATCH
                            </span>
                          </div>
                        </div>

                        <p className="text-[10px] text-[#494844] italic bg-[#E8E6DF] p-2.5 border border-[#151515]/16 leading-relaxed">
                          "{citation.snippet}"
                        </p>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
