import React from 'react';

export default function FooterClose({ health, onClearDatabase }) {
  return (
    <footer className="relative bg-[#E8E6DF] border-t border-[#151515]/16 pt-16 pb-0 overflow-hidden font-mono select-none">
      <div className="max-w-7xl mx-auto px-6 md:px-12 space-y-12">
        
        {/* Top Header & Buttons */}
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8 border-b border-[#151515]/16 pb-12">
          
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-[10px] uppercase tracking-[0.14em] text-[#C4442C]">
              <span className="w-2 h-2 bg-[#C4442C]" />
              <span>[SECTION 05 // SYSTEM CLOSE]</span>
            </div>
            
            <h2 className="font-display font-extrabold text-4xl md:text-6xl tracking-tighter text-[#151515]">
              ALPHAREAD <span className="text-outline">FINANCIAL</span>
            </h2>
            
            <p className="font-palatino text-[14px] text-[#494844] max-w-xl leading-relaxed">
              AlphaRead Catalogue System v1.0 // Engineered for high-throughput SEC 10-K filing analysis, subword token chunking, and grounded financial RAG inference.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
              className="bg-[#151515] text-[#E8E6DF] hover:bg-[#C4442C] border border-[#151515] px-5 py-3 text-[10px] uppercase tracking-[0.14em] transition-colors"
            >
              [BACK TO TOP]
            </button>
            
            <button
              onClick={onClearDatabase}
              className="bg-[#E8E6DF] text-[#151515] hover:border-[#C4442C] hover:text-[#C4442C] border border-[#151515]/30 px-5 py-3 text-[10px] uppercase tracking-[0.14em] transition-colors"
            >
              [PURGE VECTOR MEMORY]
            </button>

            <a
              href="https://github.com/nagul-2005/AlphaRead-Financial-RAG"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-[#E8E6DF] text-[#151515] hover:border-[#C4442C] hover:text-[#C4442C] border border-[#151515]/30 px-5 py-3 text-[10px] uppercase tracking-[0.14em] transition-colors"
            >
              [GITHUB REPO]
            </a>
          </div>

        </div>

        {/* Footer Metadata Strip */}
        <div className="flex flex-wrap items-center justify-between gap-4 text-[9.5px] text-[#75736C] uppercase tracking-[0.14em] border-b border-[#151515]/16 pb-8">
          <div>
            <span>STATUS: </span>
            <span className="text-[#151515] font-bold">
              {health?.status === 'online' ? 'ONLINE (GROQ ENGINE ACTIVE)' : 'CONNECTED'}
            </span>
          </div>
          <div>
            <span>RAM FOOTPRINT: </span>
            <span className="text-[#C4442C] font-bold">~38 MB ONNX RUNTIME</span>
          </div>
          <div>
            <span>CATALOGUE SPEC: </span>
            <span className="text-[#151515] font-bold">2025-SEC-10K</span>
          </div>
        </div>

      </div>

      {/* Cropped Wordmark: Full width at clamp(70px,19vw,290px) translated down .17em so the bottom page edge crops it */}
      <div className="w-full text-center overflow-hidden leading-none select-none pointer-events-none pt-4">
        <div 
          className="font-display font-black text-[#151515] tracking-tighter w-full block uppercase"
          style={{
            fontSize: 'clamp(70px, 19vw, 290px)',
            transform: 'translateY(0.17em)',
            lineHeight: '0.8'
          }}
        >
          ALPHAREAD
        </div>
      </div>
    </footer>
  );
}
