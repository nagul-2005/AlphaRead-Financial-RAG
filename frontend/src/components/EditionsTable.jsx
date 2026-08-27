import React, { useState } from 'react';

const EDITIONS = [
  { ticker: 'MSFT', company: 'Microsoft Corporation', year: 'FY2024', sections: 'Item 1A, Item 7' },
  { ticker: 'NVDA', company: 'NVIDIA Corporation', year: 'FY2024', sections: 'Item 1, Item 7' },
  { ticker: 'AAPL', company: 'Apple Inc', year: 'FY2024', sections: 'Item 1A, Item 8' },
  { ticker: 'TSLA', company: 'Tesla Inc', year: 'FY2024', sections: 'Item 7, Item 8' },
  { ticker: 'AMZN', company: 'Amazon.com Inc', year: 'FY2024', sections: 'Item 1, Item 7' },
  { ticker: 'GOOGL', company: 'Alphabet Inc', year: 'FY2024', sections: 'Item 1A, Item 7' }
];

export default function EditionsTable({ onIngestSEC, onUploadPDF, documents, onDeleteDocument, isProcessing, statusMessage, errorMessage }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedTicker, setSelectedTicker] = useState('MSFT');

  const handleFileDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
        onUploadPDF(file);
      }
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      onUploadPDF(e.target.files[0]);
    }
  };

  return (
    <section id="editions-catalogue" className="bg-[#DEDBD2] border-b border-[#151515]/16 p-6 md:p-12">
      <div className="max-w-7xl mx-auto space-y-10">
        
        {/* Section Header Tag */}
        <div className="border-b border-[#151515]/16 pb-4 flex flex-wrap items-center justify-between gap-4 font-mono text-[10px] uppercase tracking-[0.14em]">
          <div className="flex items-center gap-2 text-[#C4442C]">
            <span className="w-2 h-2 bg-[#C4442C]" />
            <span>[SECTION 02 // SEC EDITIONS & FILE INGESTION]</span>
          </div>
          <span className="text-[#75736C]">KNOWLEDGE SOURCE ENGINE</span>
        </div>

        {/* Headline mixing SOLID and OUTLINED words */}
        <div className="space-y-2">
          <h2 className="font-display font-extrabold text-3xl md:text-5xl tracking-tighter text-[#151515]">
            EDITIONS <span className="text-outline">CATALOGUE</span>
          </h2>
          <p className="font-mono text-[11px] text-[#494844] max-w-3xl leading-relaxed">
            Direct SEC EDGAR 10-K filing retrieval pipeline and multi-core PDF document parser. Ingest filings into ChromaDB with subword token-aligned chunking.
          </p>
        </div>

        {/* Status Banners */}
        {statusMessage && (
          <div className="bg-[#E8E6DF] border border-[#C4442C] p-3.5 font-mono text-[10.5px] text-[#C4442C] uppercase tracking-[0.12em] flex items-center gap-3">
            <span className="w-2 h-2 bg-[#C4442C] animate-ping" />
            <span>{statusMessage}</span>
          </div>
        )}

        {errorMessage && (
          <div className="bg-[#151515] text-[#E8E6DF] border border-[#C4442C] p-3.5 font-mono text-[10.5px] uppercase tracking-[0.12em]">
            [ERROR] {errorMessage}
          </div>
        )}

        {/* Editions Table */}
        <div className="bg-[#E8E6DF] border border-[#151515]/20 overflow-x-auto">
          <table className="w-full text-left font-mono border-collapse">
            <thead>
              <tr className="border-b border-[#151515]/20 bg-[#DEDBD2] text-[9.5px] uppercase tracking-[0.14em] text-[#75736C]">
                <th className="p-4 font-bold">TICKER</th>
                <th className="p-4 font-bold">ENTITY NAME</th>
                <th className="p-4 font-bold">FISCAL YEAR</th>
                <th className="p-4 font-bold">TARGET SECTIONS</th>
                <th className="p-4 font-bold">STATUS</th>
                <th className="p-4 font-bold text-right">ACTION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#151515]/16 text-[10.5px]">
              {EDITIONS.map((ed) => {
                const isIngested = documents.some(d => d.source.toUpperCase().includes(ed.ticker));
                return (
                  <tr key={ed.ticker} className="hover:bg-[#DEDBD2]/50 transition-colors">
                    <td className="p-4 font-display font-extrabold text-base text-[#151515]">
                      {ed.ticker}
                    </td>
                    <td className="p-4 text-[#494844] tracking-[0.06em]">
                      {ed.company}
                    </td>
                    <td className="p-4 text-[#75736C]">
                      {ed.year}
                    </td>
                    <td className="p-4 text-[#151515] font-bold">
                      {ed.sections}
                    </td>
                    <td className="p-4">
                      {isIngested ? (
                        <span className="text-[#C4442C] font-bold uppercase tracking-[0.12em]">
                          ● INGESTED
                        </span>
                      ) : (
                        <span className="text-[#75736C] uppercase tracking-[0.12em]">
                          ○ STANDBY
                        </span>
                      )}
                    </td>
                    <td className="p-4 text-right">
                      <button
                        onClick={() => onIngestSEC(ed.ticker, ed.sections.split(', '))}
                        disabled={isProcessing}
                        className="bg-[#151515] hover:bg-[#C4442C] text-[#E8E6DF] border border-[#151515] px-4 py-2 font-mono text-[9.5px] uppercase tracking-[0.14em] transition-colors whitespace-nowrap disabled:opacity-50"
                      >
                        [FETCH 10-K]
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Drag & Drop PDF Zone & Document Index Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 pt-4">
          
          {/* Drag & Drop PDF Dropzone */}
          <div className="lg:col-span-6">
            <div
              onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
              onDragLeave={() => setDragActive(false)}
              onDrop={handleFileDrop}
              className={`bg-[#E8E6DF] border-2 border-dashed p-8 text-center space-y-4 transition-colors relative cursor-pointer ${
                dragActive ? 'border-[#C4442C] bg-[#DEDBD2]' : 'border-[#151515]/30 hover:border-[#151515]'
              }`}
            >
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileSelect}
                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                disabled={isProcessing}
              />
              <div className="w-8 h-8 bg-[#C4442C] mx-auto flex items-center justify-center text-[#E8E6DF] font-bold font-mono text-xs">
                PDF
              </div>
              <div className="space-y-1 font-mono">
                <p className="text-[11px] font-bold uppercase tracking-[0.14em] text-[#151515]">
                  [DRAG & DROP FINANCIAL PDF REPORT HERE]
                </p>
                <p className="text-[9.5px] text-[#75736C] tracking-[0.1em]">
                  OR CLICK TO BROWSE LOCAL FILES (PARALLEL TOKEN CHUNKING)
                </p>
              </div>
            </div>
          </div>

          {/* Active Ingested Document Index */}
          <div className="lg:col-span-6 bg-[#E8E6DF] border border-[#151515]/20 p-6 space-y-4 font-mono">
            <div className="flex items-center justify-between border-b border-[#151515]/16 pb-3 text-[10px] uppercase tracking-[0.14em]">
              <span className="font-bold text-[#151515]">[INGESTED DOCUMENTS MEMORY]</span>
              <span className="text-[#C4442C]">{documents.length} FILES</span>
            </div>

            {documents.length === 0 ? (
              <p className="text-[10px] text-[#75736C] py-4 text-center">
                No custom documents ingested yet. Upload a PDF or fetch an SEC 10-K above.
              </p>
            ) : (
              <div className="max-h-48 overflow-y-auto space-y-2">
                {documents.map((doc, idx) => (
                  <div key={idx} className="bg-[#DEDBD2] p-3 border border-[#151515]/16 flex items-center justify-between gap-3 text-[10px]">
                    <div className="truncate">
                      <span className="font-bold text-[#151515]">{doc.source}</span>
                      <span className="text-[#75736C] text-[9px] block">CHUNKS: {doc.chunks_count || 1}</span>
                    </div>
                    <button
                      onClick={() => onDeleteDocument(doc.source)}
                      className="text-[#C4442C] hover:bg-[#C4442C] hover:text-[#E8E6DF] border border-[#C4442C] px-2 py-1 text-[9px] uppercase tracking-[0.12em] transition-colors"
                    >
                      [PURGE]
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>

      </div>
    </section>
  );
}
