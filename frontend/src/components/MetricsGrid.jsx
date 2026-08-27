import React from 'react';

export default function MetricsGrid() {
  return (
    <section className="bg-[#E8E6DF] border-b border-[#151515]/16 p-6 md:p-12">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Section Header Tag */}
        <div className="border-b border-[#151515]/16 pb-4 flex flex-wrap items-center justify-between gap-4 font-mono text-[10px] uppercase tracking-[0.14em]">
          <div className="flex items-center gap-2 text-[#C4442C]">
            <span className="w-2 h-2 bg-[#C4442C]" />
            <span>[SECTION 03 // ARCHITECTURE METRICS]</span>
          </div>
          <span className="text-[#75736C]">SYSTEM BENCHMARK DATA</span>
        </div>

        {/* Headline mixing SOLID and OUTLINED words */}
        <div className="space-y-2">
          <h2 className="font-display font-extrabold text-3xl md:text-5xl tracking-tighter text-[#151515]">
            HYBRID <span className="text-outline">RETRIEVAL</span> METRICS
          </h2>
          <p className="font-palatino text-[14px] text-[#494844] max-w-3xl leading-relaxed">
            Quantitative architecture specs driving AlphaRead's high-speed document indexing and inference engine.
          </p>
        </div>

        {/* Three-Cell Data Grid Separated by 1px Gaps over Hairline Background */}
        <div className="bg-[#151515]/16 p-[1px] grid grid-cols-1 md:grid-cols-3 gap-[1px] font-mono select-none">
          
          {/* Cell 1 */}
          <div className="bg-[#DEDBD2] p-8 space-y-4 flex flex-col justify-between hover:bg-[#E8E6DF] transition-colors">
            <div className="space-y-2">
              <span className="text-[9.5px] text-[#75736C] uppercase tracking-[0.14em]">
                01 // SUBWORD CHUNKING
              </span>
              <h3 className="font-display font-bold text-2xl text-[#151515] tracking-tight">
                256 TOKENS
              </h3>
            </div>
            <div className="border-t border-[#151515]/16 pt-4 space-y-1.5 text-[10px] text-[#494844]">
              <div className="flex justify-between">
                <span>TEXT PARSER:</span>
                <span className="font-bold text-[#151515]">PyMuPDF (C++)</span>
              </div>
              <div className="flex justify-between">
                <span>TOKEN BOUNDARY:</span>
                <span className="font-bold text-[#151515]">tiktoken (Rust BPE)</span>
              </div>
              <div className="flex justify-between">
                <span>CHUNK OVERLAP:</span>
                <span className="font-bold text-[#C4442C]">30 TOKENS</span>
              </div>
            </div>
          </div>

          {/* Cell 2 */}
          <div className="bg-[#DEDBD2] p-8 space-y-4 flex flex-col justify-between hover:bg-[#E8E6DF] transition-colors">
            <div className="space-y-2">
              <span className="text-[9.5px] text-[#75736C] uppercase tracking-[0.14em]">
                02 // ONNX VECTOR ENGINE
              </span>
              <h3 className="font-display font-bold text-2xl text-[#151515] tracking-tight">
                384 DIMS
              </h3>
            </div>
            <div className="border-t border-[#151515]/16 pt-4 space-y-1.5 text-[10px] text-[#494844]">
              <div className="flex justify-between">
                <span>DENSE MODEL:</span>
                <span className="font-bold text-[#151515]">bge-small-en-v1.5</span>
              </div>
              <div className="flex justify-between">
                <span>RUNNING RAM:</span>
                <span className="font-bold text-[#C4442C]">~38 MB RAM</span>
              </div>
              <div className="flex justify-between">
                <span>SEARCH ENGINE:</span>
                <span className="font-bold text-[#151515]">NumPy Matrix / ChromaDB</span>
              </div>
            </div>
          </div>

          {/* Cell 3 */}
          <div className="bg-[#DEDBD2] p-8 space-y-4 flex flex-col justify-between hover:bg-[#E8E6DF] transition-colors">
            <div className="space-y-2">
              <span className="text-[9.5px] text-[#75736C] uppercase tracking-[0.14em]">
                03 // LLM REASONING
              </span>
              <h3 className="font-display font-bold text-2xl text-[#151515] tracking-tight">
                GROQ LLAMA-3
              </h3>
            </div>
            <div className="border-t border-[#151515]/16 pt-4 space-y-1.5 text-[10px] text-[#494844]">
              <div className="flex justify-between">
                <span>PRIMARY MODEL:</span>
                <span className="font-bold text-[#151515]">openai/gpt-oss-120b</span>
              </div>
              <div className="flex justify-between">
                <span>RELEVANCE THRESHOLD:</span>
                <span className="font-bold text-[#C4442C]">0.35 SCORE</span>
              </div>
              <div className="flex justify-between">
                <span>RERANKING FUSION:</span>
                <span className="font-bold text-[#151515]">BM25 + Dense RRF</span>
              </div>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
