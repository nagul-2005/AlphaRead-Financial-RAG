import React, { useState, useEffect } from 'react';

const VARIANTS = [
  { id: '01', ticker: 'MSFT', name: 'Microsoft Corp', year: 'FY2024', rev: '$245.1B', margin: '44.6%', item: 'Item 1A & Item 7', colorTint: 'contrast(1.05)' },
  { id: '02', ticker: 'NVDA', name: 'NVIDIA Corp', year: 'FY2024', rev: '$60.9B', margin: '54.1%', item: 'Item 1 & Item 7', colorTint: 'sepia(0.2) contrast(1.1)' },
  { id: '03', ticker: 'AAPL', name: 'Apple Inc', year: 'FY2024', rev: '$385.6B', margin: '30.7%', item: 'Item 1A & Item 8', colorTint: 'hue-rotate(15deg)' },
  { id: '04', ticker: 'TSLA', name: 'Tesla Inc', year: 'FY2024', rev: '$96.8B', margin: '18.2%', item: 'Item 7 & Item 8', colorTint: 'saturate(1.2)' },
  { id: '05', ticker: 'AMZN', name: 'Amazon.com Inc', year: 'FY2024', rev: '$574.8B', margin: '6.4%', item: 'Item 1 & Item 7', colorTint: 'contrast(1.1)' },
  { id: '06', ticker: 'GOOGL', name: 'Alphabet Inc', year: 'FY2024', rev: '$307.4B', margin: '27.4%', item: 'Item 1A & Item 7', colorTint: 'sepia(0.1)' }
];

export default function HeroCatalogue({ selectedVariantIndex, onSelectVariant, onIngestSEC }) {
  const [scrollTranslateX, setScrollTranslateX] = useState(0);
  const activeVariant = VARIANTS[selectedVariantIndex] || VARIANTS[0];

  useEffect(() => {
    const handleScroll = () => {
      const offset = window.scrollY * 0.35;
      setScrollTranslateX(offset);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <section className="relative min-h-[calc(100vh-50px)] bg-[#DEDBD2] border-b border-[#151515]/16 overflow-hidden flex flex-col justify-between p-6 md:p-12">
      
      {/* Ghosted Outline Numeral (Counter-travels horizontally on scroll) */}
      <div 
        className="absolute top-1/2 -translate-y-1/2 right-[5%] select-none pointer-events-none z-0 font-display font-bold text-outline-light transition-transform duration-75 ease-out"
        style={{
          fontSize: 'clamp(220px, 44vw, 660px)',
          lineHeight: '0.8',
          transform: `translateY(-50%) translateX(${scrollTranslateX * 0.25}px)`
        }}
        aria-hidden="true"
      >
        {activeVariant.id}
      </div>

      {/* Inspect Controls: Vertical stack of small square monospaced buttons pinned to right edge */}
      <div className="hidden lg:flex fixed right-6 top-1/2 -translate-y-1/2 flex-col gap-1.5 z-[700] select-none">
        <span className="text-[8.5px] font-mono text-[#75736C] uppercase tracking-[0.14em] mb-1 text-right">
          [VARIANTS]
        </span>
        {VARIANTS.map((v, idx) => {
          const isSelected = selectedVariantIndex === idx;
          return (
            <button
              key={v.id}
              onClick={() => onSelectVariant(idx)}
              aria-pressed={isSelected}
              className={`px-2.5 py-1.5 font-mono text-[10px] uppercase tracking-[0.12em] border transition-all text-left ${
                isSelected
                  ? 'bg-[#C4442C] text-[#E8E6DF] border-[#C4442C]'
                  : 'bg-[#E8E6DF] text-[#151515] border-[#151515]/20 hover:border-[#151515]'
              }`}
            >
              {v.id} {v.ticker}
            </button>
          );
        })}
      </div>

      {/* Main Hero Content Layout */}
      <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center max-w-7xl mx-auto w-full my-auto">
        
        {/* Left Copy Column: Max 44vw width on desktop */}
        <div className="lg:col-span-7 flex flex-col justify-center space-y-6 max-w-none lg:max-w-[44vw]">
          
          {/* Eyebrow */}
          <div className="inline-flex items-center gap-2 text-[10px] font-mono uppercase tracking-[0.14em] text-[#C4442C]">
            <span className="w-2 h-[2px] bg-[#C4442C]" />
            <span>CATALOGUE REF {activeVariant.id} // {activeVariant.ticker} 10-K</span>
          </div>

          {/* Headline mixing SOLID and OUTLINED words */}
          <h1 className="font-display font-extrabold tracking-tighter text-[#151515] leading-[0.92]" style={{ fontSize: 'clamp(38px, 6.4vw, 92px)' }}>
            FINANCIAL <br />
            <span className="text-outline">INTELLIGENCE</span> <br />
            OBJECT
          </h1>

          {/* Lede Paragraph */}
          <p className="font-mono text-[11px] text-[#494844] leading-relaxed tracking-[0.06em]">
            Production RAG architecture for SEC 10-K reports. Features subword token-aligned chunking (`256 tokens`), FastEmbed ONNX vector embeddings (`BAAI/bge-small-en-v1.5`), and Groq Llama-3 quantitative reasoning.
          </p>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-3 pt-2">
            <a
              href="#rag-terminal"
              className="bg-[#151515] text-[#E8E6DF] hover:bg-[#C4442C] hover:text-[#E8E6DF] border border-[#151515] px-5 py-3 font-mono text-[10.5px] uppercase tracking-[0.14em] transition-colors"
            >
              [EXECUTE QUERY TERMINAL]
            </a>
            <button
              onClick={() => onIngestSEC(activeVariant.ticker, ["Item 1A", "Item 7"])}
              className="bg-[#E8E6DF] text-[#151515] hover:border-[#C4442C] hover:text-[#C4442C] border border-[#151515]/30 px-5 py-3 font-mono text-[10.5px] uppercase tracking-[0.14em] transition-colors"
            >
              [INGEST {activeVariant.ticker} 10-K]
            </button>
          </div>
        </div>

        {/* Right Cut-Out Subject Card (Sized by Height) */}
        <div className="lg:col-span-5 flex justify-center lg:justify-end">
          <div 
            className="w-full max-w-sm bg-[#E8E6DF] border border-[#151515]/20 p-6 flex flex-col justify-between space-y-6 transition-all duration-300"
            style={{ filter: activeVariant.colorTint }}
          >
            {/* Header Badge */}
            <div className="flex items-center justify-between border-b border-[#151515]/16 pb-3">
              <span className="font-mono text-[9.5px] uppercase tracking-[0.14em] text-[#75736C]">
                SUBJECT NO. {activeVariant.id}
              </span>
              <span className="font-mono text-[10px] font-bold text-[#C4442C]">
                {activeVariant.ticker}
              </span>
            </div>

            {/* Entity Spec */}
            <div>
              <h3 className="font-display font-bold text-2xl text-[#151515] tracking-tight">
                {activeVariant.name}
              </h3>
              <p className="font-mono text-[10px] text-[#494844] tracking-[0.12em] uppercase mt-1">
                SEC 10-K FILING // FISCAL YEAR {activeVariant.year}
              </p>
            </div>

            {/* Metrics Breakdown Grid */}
            <div className="grid grid-cols-2 gap-4 border-t border-b border-[#151515]/16 py-4 font-mono">
              <div>
                <span className="text-[9px] text-[#75736C] uppercase tracking-[0.12em]">ANNUAL REVENUE</span>
                <p className="text-base font-bold text-[#151515] mt-0.5">{activeVariant.rev}</p>
              </div>
              <div>
                <span className="text-[9px] text-[#75736C] uppercase tracking-[0.12em]">OPERATING MARGIN</span>
                <p className="text-base font-bold text-[#C4442C] mt-0.5">{activeVariant.margin}</p>
              </div>
            </div>

            {/* Section Tag */}
            <div className="flex items-center justify-between text-[9.5px] font-mono text-[#494844]">
              <span>TARGET SECTIONS:</span>
              <span className="font-bold text-[#151515]">{activeVariant.item}</span>
            </div>

            {/* Direct Ingestion Quick Trigger */}
            <button
              onClick={() => onIngestSEC(activeVariant.ticker, ["Item 1A", "Item 7"])}
              className="w-full bg-[#151515] text-[#E8E6DF] hover:bg-[#C4442C] py-2.5 font-mono text-[10px] uppercase tracking-[0.14em] transition-colors"
            >
              [INSPECT & LOAD {activeVariant.ticker} DATA]
            </button>
          </div>
        </div>

      </div>

      {/* Mobile Inspection Variant Bar */}
      <div className="flex lg:hidden flex-wrap gap-2 justify-center py-4 border-t border-[#151515]/16 my-4 z-10">
        {VARIANTS.map((v, idx) => (
          <button
            key={v.id}
            onClick={() => onSelectVariant(idx)}
            className={`px-3 py-1 font-mono text-[10px] uppercase border ${
              selectedVariantIndex === idx
                ? 'bg-[#C4442C] text-[#E8E6DF] border-[#C4442C]'
                : 'bg-[#E8E6DF] text-[#151515] border-[#151515]/20'
            }`}
          >
            {v.id} {v.ticker}
          </button>
        ))}
      </div>

      {/* Bottom Rail */}
      <div className="relative z-10 border-t border-[#151515]/16 pt-4 flex flex-wrap items-center justify-between gap-4 font-mono text-[9.5px] uppercase tracking-[0.14em] text-[#494844]">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 bg-[#C4442C]" />
          <span>[SCROLL TO INSPECT STATEMENTS & QUERY TERMINAL]</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[#75736C]">CATALOGUE INDEX:</span>
          <span className="font-bold text-[#151515]">{activeVariant.id} / 06</span>
        </div>
      </div>

    </section>
  );
}
