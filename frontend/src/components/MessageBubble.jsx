import React, { useState } from 'react';
import { Bot, User, FileText, ChevronDown, ChevronUp, ExternalLink, Bookmark, Sparkles } from 'lucide-react';

export default function MessageBubble({ message }) {
  const isUser = message.sender === 'user';
  const [showCitations, setShowCitations] = useState(true);

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} my-3 group`}>
      <div className={`flex max-w-[85%] sm:max-w-[78%] space-x-3 ${isUser ? 'flex-row-reverse space-x-reverse' : 'flex-row'}`}>
        
        {/* Avatar */}
        <div className={`w-9 h-9 rounded-2xl flex items-center justify-center shrink-0 shadow-sm ${
          isUser 
            ? 'bg-slate-800 text-white' 
            : 'bg-gradient-to-br from-teal-500 to-emerald-500 text-white shadow-teal-500/20'
        }`}>
          {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5 stroke-[2.2]" />}
        </div>

        {/* Content Container */}
        <div className="flex flex-col space-y-2">
          
          {/* Main Bubble */}
          <div className={`px-5 py-4 rounded-3xl text-sm leading-relaxed ${
            isUser
              ? 'bg-slate-800 text-white font-medium rounded-tr-sm shadow-sm'
              : 'bg-white border border-slate-100 text-slate-800 rounded-tl-sm shadow-soft'
          }`}>
            
            {/* Sender Label */}
            <div className="flex items-center justify-between text-[11px] font-semibold mb-1.5 opacity-70">
              <span>{isUser ? 'You' : 'AlphaRead AI'}</span>
              <span>{message.timestamp || 'Just now'}</span>
            </div>

            {/* Message Body */}
            <div className="whitespace-pre-wrap font-normal text-grey-700 leading-relaxed">
              {message.text}
            </div>

            {/* Source Citations Section (For AI Messages) */}
            {!isUser && message.citations && message.citations.length > 0 && (
              <div className="mt-4 pt-3 border-t border-slate-100">
                <button
                  onClick={() => setShowCitations(!showCitations)}
                  className="flex items-center justify-between w-full text-xs font-bold text-slate-600 hover:text-teal-700 bg-slate-50/80 hover:bg-teal-50/50 px-3 py-2 rounded-xl transition-all border border-slate-200/60"
                >
                  <div className="flex items-center space-x-2">
                    <Bookmark className="w-3.5 h-3.5 text-teal-600" />
                    <span>Source Citations ({message.citations.length} RAG Chunks)</span>
                  </div>
                  {showCitations ? (
                    <ChevronUp className="w-3.5 h-3.5" />
                  ) : (
                    <ChevronDown className="w-3.5 h-3.5" />
                  )}
                </button>

                {/* Collapsible Citation Cards */}
                {showCitations && (
                  <div className="mt-3 space-y-2 animate-fadeIn">
                    {message.citations.map((citation, idx) => (
                      <div
                        key={idx}
                        className="bg-slate-50/90 border border-slate-200/80 rounded-2xl p-3 text-xs space-y-1.5 hover:border-teal-300 transition-all shadow-sm"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-1.5 text-teal-800 font-bold">
                            <FileText className="w-3.5 h-3.5 text-teal-600" />
                            <span className="truncate max-w-[200px]" title={citation.document}>
                              {citation.document}
                            </span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className="text-[10px] text-slate-500 font-medium">
                              Page/Sec: {citation.section_or_page}
                            </span>
                            {(() => {
                              const score = typeof citation.relevance_score === 'number' ? citation.relevance_score : 0.85;
                              const pct = Math.round(score * 100);
                              const badgeStyle = pct >= 70 
                                ? "bg-emerald-100 text-emerald-800 border-emerald-200" 
                                : pct >= 40 
                                  ? "bg-amber-100 text-amber-800 border-amber-200" 
                                  : "bg-slate-100 text-slate-700 border-slate-200";
                              return (
                                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${badgeStyle}`}>
                                  {pct}% Match
                                </span>
                              );
                            })()}
                          </div>
                        </div>

                        <p className="text-[11px] text-slate-600 italic bg-white p-2.5 rounded-xl border border-slate-200/50 leading-relaxed font-sans">
                          "{citation.snippet}"
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

          </div>

        </div>

      </div>
    </div>
  );
}
