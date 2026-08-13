import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, Search, Layers, CheckCircle2, AlertCircle, Loader2, Trash2 } from 'lucide-react';

export default function IngestionPanel({
  onUploadPDF,
  onIngestSEC,
  onDeleteDocument,
  documents,
  isProcessing,
  statusMessage,
  errorMessage
}) {
  const [tickerInput, setTickerInput] = useState('');
  const [selectedSections, setSelectedSections] = useState(['Item 1A', 'Item 7']);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const quickTickers = ['AAPL', 'NVDA', 'MSFT', 'AMZN', 'GOOGL', 'TSLA'];

  const availableSections = [
    { id: 'Item 1A', label: 'Item 1A: Risk Factors' },
    { id: 'Item 7', label: 'Item 7: MD&A' },
    { id: 'Item 8', label: 'Item 8: Financial Statements' },
    { id: 'Item 1', label: 'Item 1: Business Overview' },
  ];

  const toggleSection = (secId) => {
    if (selectedSections.includes(secId)) {
      if (selectedSections.length === 1) return; // Maintain at least 1 section
      setSelectedSections(selectedSections.filter(s => s !== secId));
    } else {
      setSelectedSections([...selectedSections, secId]);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
        onUploadPDF(file);
      } else {
        alert('Please drop a valid PDF file.');
      }
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      onUploadPDF(e.target.files[0]);
    }
  };

  const handleSecSubmit = (e) => {
    e.preventDefault();
    if (!tickerInput.trim()) return;
    onIngestSEC(tickerInput.trim().toUpperCase(), selectedSections);
    setTickerInput('');
  };

  const handleQuickTicker = (ticker) => {
    onIngestSEC(ticker, selectedSections);
  };

  return (
    <div className="bg-white rounded-3xl p-6 shadow-soft border border-slate-100/80 flex flex-col h-full overflow-hidden space-y-6">
      
      {/* Panel Header */}
      <div>
        <div className="flex items-center space-x-2">
          <div className="w-7 h-7 rounded-xl bg-teal-100 text-teal-700 flex items-center justify-center font-bold text-xs">
            <Layers className="w-4 h-4" />
          </div>
          <h2 className="text-lg font-bold text-slate-800 tracking-tight">Data & SEC Ingestion</h2>
        </div>
        <p className="text-xs text-slate-500 mt-1 leading-relaxed">
          Upload PDF financial reports or automatically extract custom SEC 10-K sections into your RAG memory.
        </p>
      </div>

      {/* Dynamic Feedback Banner */}
      {statusMessage && (
        <div className="bg-emerald-50 border border-emerald-200/80 text-emerald-800 text-xs px-4 py-3 rounded-2xl flex items-center space-x-2.5 animate-fadeIn">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span className="font-medium">{statusMessage}</span>
        </div>
      )}

      {errorMessage && (
        <div className="bg-rose-50 border border-rose-200/80 text-rose-800 text-xs px-4 py-3 rounded-2xl flex items-center space-x-2.5 animate-fadeIn">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span className="font-medium">{errorMessage}</span>
        </div>
      )}

      <div className="flex-1 overflow-y-auto pr-1 space-y-6">

        {/* 1. PDF Drag & Drop Upload Zone */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider block">
            1. Upload Financial PDF
          </label>
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-3xl p-6 text-center cursor-pointer transition-all duration-200 flex flex-col items-center justify-center space-y-3 ${
              dragActive
                ? 'border-teal-500 bg-teal-50/60 scale-[1.01]'
                : 'border-slate-200 hover:border-teal-400 bg-slate-50/50 hover:bg-teal-50/30'
            }`}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              accept=".pdf"
              className="hidden"
            />
            <div className="w-12 h-12 rounded-2xl bg-white shadow-soft flex items-center justify-center text-teal-600 border border-slate-100">
              <UploadCloud className="w-6 h-6 stroke-[1.8]" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-700">
                Click or drag financial PDF here
              </p>
              <p className="text-xs text-slate-400 mt-0.5">
                Supports 10-K, 10-Q, Annual Reports, Earnings Transcripts
              </p>
            </div>
          </div>
        </div>

        {/* 2. SEC 10-K Ticker Lookup with Section Checkboxes */}
        <div className="space-y-3 pt-2 border-t border-slate-100">
          <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider block">
            2. Fetch SEC 10-K Report
          </label>
          
          <form onSubmit={handleSecSubmit} className="flex gap-2">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Stock Ticker (e.g. AAPL, NVDA)..."
                value={tickerInput}
                onChange={(e) => setTickerInput(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-teal-500/30 focus:border-teal-500 font-medium placeholder:text-slate-400 transition-all"
                disabled={isProcessing}
              />
            </div>
            <button
              type="submit"
              disabled={isProcessing || !tickerInput.trim()}
              className="bg-slate-800 hover:bg-slate-900 disabled:opacity-50 text-white font-medium text-xs px-5 py-2.5 rounded-full transition-all shadow-sm flex items-center space-x-1.5 shrink-0"
            >
              {isProcessing ? (
                <Loader2 className="w-4 h-4 animate-spin text-teal-300" />
              ) : (
                <span>Fetch 10-K</span>
              )}
            </button>
          </form>

          {/* SEC Section Selection Checkboxes */}
          <div className="space-y-1.5 bg-slate-50/80 p-3 rounded-2xl border border-slate-200/60">
            <span className="text-[11px] font-semibold text-slate-500 block mb-1">
              Select 10-K Sections to Extract:
            </span>
            <div className="grid grid-cols-2 gap-1.5">
              {availableSections.map((sec) => {
                const isChecked = selectedSections.includes(sec.id);
                return (
                  <label
                    key={sec.id}
                    className={`flex items-center space-x-2 text-xs p-2 rounded-xl border cursor-pointer transition-all font-medium ${
                      isChecked
                        ? 'bg-teal-50/80 border-teal-300 text-teal-900 font-semibold'
                        : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={() => toggleSection(sec.id)}
                      className="rounded text-teal-600 focus:ring-teal-500 h-3.5 w-3.5"
                    />
                    <span className="truncate">{sec.label}</span>
                  </label>
                );
              })}
            </div>
          </div>

          {/* Quick Ticker Chips */}
          <div className="flex flex-wrap items-center gap-1.5 pt-1">
            <span className="text-xs text-slate-400 font-medium mr-1">Popular:</span>
            {quickTickers.map((ticker) => (
              <button
                key={ticker}
                onClick={() => handleQuickTicker(ticker)}
                disabled={isProcessing}
                className="text-xs bg-slate-100 hover:bg-teal-100 hover:text-teal-800 text-slate-600 font-semibold px-2.5 py-1 rounded-full transition-all border border-slate-200/50"
              >
                {ticker}
              </button>
            ))}
          </div>
        </div>

        {/* 3. Ingested Documents Inventory with Single Delete */}
        <div className="space-y-3 pt-2 border-t border-slate-100">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
              Knowledge Base ({documents.length})
            </label>
            <span className="text-[11px] text-slate-400 font-medium">Vector Memory</span>
          </div>

          {documents.length === 0 ? (
            <div className="text-center py-8 bg-slate-50/50 rounded-2xl border border-dashed border-slate-200 text-slate-400">
              <FileText className="w-8 h-8 mx-auto stroke-1 text-slate-300 mb-1" />
              <p className="text-xs font-medium">No documents ingested yet</p>
              <p className="text-[11px] text-slate-400 mt-0.5">Upload a PDF or select an SEC ticker above</p>
            </div>
          ) : (
            <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
              {documents.map((doc, idx) => (
                <div
                  key={idx}
                  className="bg-white hover:bg-slate-50 p-3 rounded-2xl border border-slate-200/80 shadow-soft flex items-center justify-between transition-all group"
                >
                  <div className="flex items-center space-x-3 overflow-hidden">
                    <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${
                      doc.doc_type === 'SEC_10K'
                        ? 'bg-indigo-50 text-indigo-600 border border-indigo-100'
                        : 'bg-emerald-50 text-emerald-600 border border-emerald-100'
                    }`}>
                      <FileText className="w-4 h-4" />
                    </div>
                    <div className="truncate">
                      <p className="text-xs font-bold text-slate-800 truncate" title={doc.source}>
                        {doc.source}
                      </p>
                      <p className="text-[11px] text-slate-400">
                        {doc.doc_type} • {doc.chunks_count} Vector Chunks
                      </p>
                    </div>
                  </div>

                  {/* Single Delete Button */}
                  <button
                    onClick={() => onDeleteDocument(doc.source)}
                    title={`Delete '${doc.source}' from database`}
                    className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-all opacity-80 group-hover:opacity-100 shrink-0 ml-2"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
