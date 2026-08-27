import React from 'react';

const PROCESS_STEPS = [
  { step: '01', title: 'PDF & SEC 10-K INGESTION', desc: 'Direct C++ PyMuPDF page parsing and EDGAR API 10-K HTML tag sanitization.', metric: '< 15 MS PARSE TIME' },
  { step: '02', title: 'SUBWORD TOKEN CHUNKING', desc: 'Sliding window subword tokenization via tiktoken BPE with 256 token windows and 30 token overlaps.', metric: '256 TOKENS / CHUNK' },
  { step: '03', title: 'ONNX DENSE EMBEDDING GENERATION', desc: 'Lightweight FastEmbed BAAI/bge-small-en-v1.5 embedding generation with 384 dimensional vectors.', metric: '384 DIMENSIONS' },
  { step: '04', title: 'BM25 & DENSE RRF RECURSIVE SEARCH', desc: 'Hybrid rank fusion combining BM25 keyword match with vectorized dense cosine similarity.', metric: 'TOP-20 CANDIDATES' },
  { step: '05', title: 'LOGIT CALIBRATION & RELEVANCE FILTERING', desc: 'Offset logit score calibration with a strict 0.35 relevance threshold to eliminate false citations.', metric: 'THRESHOLD 0.35' },
  { step: '06', title: 'GROQ LLAMA-3 REASONING & CITATION ATTACHMENT', desc: 'Context-grounded narrative generation with inline [Source] tags and formatted bullet points.', metric: 'GROQ 70B LLAMA-3' }
];

export default function ProcessList() {
  return (
    <section className="bg-[#DEDBD2] border-b border-[#151515]/16 p-6 md:p-12">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Section Header Tag */}
        <div className="border-b border-[#151515]/16 pb-4 flex flex-wrap items-center justify-between gap-4 font-mono text-[10px] uppercase tracking-[0.14em]">
          <div className="flex items-center gap-2 text-[#C4442C]">
            <span className="w-2 h-2 bg-[#C4442C]" />
            <span>[SECTION 04 // PROCESS METHODOLOGY]</span>
          </div>
          <span className="text-[#75736C]">PIPELINE AUDIT TRAIL</span>
        </div>

        {/* Headline mixing SOLID and OUTLINED words */}
        <div className="space-y-2">
          <h2 className="font-display font-extrabold text-3xl md:text-5xl tracking-tighter text-[#151515]">
            EXECUTION <span className="text-outline">PIPELINE</span>
          </h2>
          <p className="font-palatino text-[14px] text-[#494844] max-w-3xl leading-relaxed">
            Sequential data transformation pipeline from document ingestion to grounded financial answer synthesis.
          </p>
        </div>

        {/* Hairline-Ruled Rows */}
        <div className="border-t border-[#151515]/20 divide-y divide-[#151515]/16 font-mono">
          {PROCESS_STEPS.map((step) => (
            <div 
              key={step.step} 
              className="py-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-[#E8E6DF]/60 px-4 transition-colors"
            >
              <div className="flex items-start md:items-center gap-4">
                <span className="text-[#C4442C] font-bold text-sm">
                  [{step.step}]
                </span>
                <div>
                  <h4 className="font-display font-bold text-base text-[#151515] tracking-tight">
                    {step.title}
                  </h4>
                  <p className="font-palatino text-[13.5px] text-[#494844] mt-0.5 max-w-2xl leading-relaxed">
                    {step.desc}
                  </p>
                </div>
              </div>

              <div className="text-right">
                <span className="bg-[#151515] text-[#E8E6DF] px-3 py-1 text-[9.5px] font-bold tracking-[0.12em] whitespace-nowrap">
                  {step.metric}
                </span>
              </div>
            </div>
          ))}
        </div>

      </div>
    </section>
  );
}
