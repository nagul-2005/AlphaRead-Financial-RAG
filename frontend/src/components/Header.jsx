import React from 'react';

export default function Header({ health, onClearDatabase, documentsCount }) {
  const isOnline = health && health.status === 'online';
  const groqReady = health && health.groq_configured;

  return (
    <header className="sticky top-0 bg-[#E8E6DF] border-b border-[#151515]/16 z-[800] px-4 md:px-8 py-3.5 flex flex-wrap items-center justify-between gap-4 font-mono text-[10px] uppercase tracking-[0.12em]">
      {/* Brand & Catalogue Spec */}
      <div className="flex items-center gap-3">
        <div className="w-2.5 h-2.5 bg-[#C4442C]" />
        <span className="font-display font-bold text-sm tracking-tighter text-[#151515]">
          ALPHAREAD <span className="text-outline">CATALOGUE</span>
        </span>
        <span className="hidden sm:inline border-l border-[#151515]/16 pl-3 text-[#75736C]">
          OBJECT NO. 2025-SEC-10K
        </span>
      </div>

      {/* Live System Indicators */}
      <div className="flex items-center gap-4 text-[#494844]">
        <div className="flex items-center gap-1.5">
          <span className={`w-1.5 h-1.5 ${isOnline ? 'bg-[#C4442C]' : 'bg-[#75736C]'}`} />
          <span>API STATUS: <strong className="text-[#151515]">{isOnline ? 'ONLINE (GROQ LLAMA-3)' : 'CONNECTING...'}</strong></span>
        </div>

        <div className="hidden lg:flex items-center gap-1.5 border-l border-[#151515]/16 pl-4">
          <span className="text-[#75736C]">INDEXED CHUNKS:</span>
          <span className="text-[#151515] font-bold">{documentsCount} DOCS</span>
        </div>

        {/* Paper Catalogue Clear Button */}
        <button
          onClick={onClearDatabase}
          className="border border-[#151515]/20 hover:border-[#C4442C] hover:text-[#C4442C] px-3 py-1 text-[9.5px] uppercase tracking-[0.14em] transition-colors"
          title="Purge vector store memory index"
        >
          [CLEAR VECTOR STORE]
        </button>
      </div>
    </header>
  );
}
