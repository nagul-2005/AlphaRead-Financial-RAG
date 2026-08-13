import React from 'react';
import { TrendingUp, Database, Sparkles, RefreshCw, ShieldCheck } from 'lucide-react';

export default function Header({ health, onClearDatabase, documentsCount }) {
  return (
    <header className="bg-white border-b border-slate-100 px-6 py-4 flex items-center justify-between shadow-soft z-10 relative">
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-teal-500 to-emerald-400 flex items-center justify-center shadow-md shadow-teal-500/20 text-white font-bold text-xl">
          <TrendingUp className="w-5 h-5 stroke-[2.5]" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-bold text-slate-800 tracking-tight">AlphaRead</h1>
            <span className="px-2.5 py-0.5 text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/60 rounded-full">
              Financial GenAI RAG
            </span>
          </div>
          <p className="text-xs text-slate-500 font-medium">
            AI Document Intelligence for Financial Statements & SEC 10-K Reports
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        {/* Status indicator */}
        <div className="hidden sm:flex items-center space-x-2 bg-slate-50 px-3 py-1.5 rounded-full border border-slate-200/60 text-xs text-slate-600">
          <span className={`w-2 h-2 rounded-full ${health ? 'bg-emerald-500 animate-pulse-subtle' : 'bg-amber-400'}`}></span>
          <span className="font-medium">
            {health ? (health.groq_configured ? 'Llama-3 via Groq Ready' : 'Local Fallback RAG') : 'Connecting...'}
          </span>
        </div>

        {/* Ingested Documents Counter */}
        <div className="flex items-center space-x-1.5 bg-teal-50 text-teal-700 px-3 py-1.5 rounded-full text-xs font-semibold border border-teal-200/60">
          <Database className="w-3.5 h-3.5" />
          <span>{documentsCount} Sources Ingested</span>
        </div>

        {/* Clear Database Button */}
        <button
          onClick={onClearDatabase}
          title="Clear vector database index"
          className="flex items-center space-x-1.5 text-xs text-slate-500 hover:text-rose-600 hover:bg-rose-50 px-3 py-1.5 rounded-full transition-all duration-200 border border-slate-200/60 hover:border-rose-200 font-medium"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span className="hidden md:inline">Reset Vector Index</span>
        </button>
      </div>
    </header>
  );
}
