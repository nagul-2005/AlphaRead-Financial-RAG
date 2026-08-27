import React from 'react';

export default function VerticalRail() {
  return (
    <aside className="hidden md:flex fixed top-0 left-0 w-[34px] h-screen bg-[#E8E6DF] border-r border-[#151515]/16 z-[900] flex-col justify-between items-center py-6 select-none pointer-events-none">
      <div className="w-[1.5px] h-10 bg-[#C4442C]" />
      <span className="writing-mode-vertical text-[10px] font-mono tracking-[0.14em] uppercase text-[#494844] whitespace-nowrap">
        ALPHAREAD // FINANCIAL RAG KNOWLEDGE ENGINE // SEC 10-K CATALOGUE 2025
      </span>
      <span className="text-[9.5px] font-mono text-[#C4442C] tracking-[0.12em]">● 01</span>
    </aside>
  );
}
