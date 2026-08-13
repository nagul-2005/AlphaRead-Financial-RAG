import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, Sparkles, MessageSquare, Loader2, Compass } from 'lucide-react';
import MessageBubble from './MessageBubble';

export default function ChatPanel({
  messages,
  onSendMessage,
  isSending,
  documentsCount
}) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const starterPrompts = [
    "Summarize key Management Discussion (MD&A) insights",
    "What are the top 3 Risk Factors mentioned in the 10-K?",
    "Highlight revenue growth drivers and quarterly performance",
    "Analyze debt obligations and liquidity risk factors"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isSending]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isSending) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handlePromptClick = (promptText) => {
    if (isSending) return;
    onSendMessage(promptText);
  };

  return (
    <div className="bg-white rounded-3xl shadow-soft border border-slate-100/80 flex flex-col h-full overflow-hidden relative">
      
      {/* Top Chat Header */}
      <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-white z-10 shrink-0">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center font-bold text-sm border border-teal-100">
            <MessageSquare className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-800 tracking-tight">Financial AI Assistant</h2>
            <p className="text-xs text-slate-400 font-medium">
              ChromaDB Context Retrieval • Llama-3 Reasoning
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-500 bg-slate-50 px-3 py-1.5 rounded-full border border-slate-200/60">
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span>{documentsCount > 0 ? `${documentsCount} Sources Ready` : 'Awaiting Data Ingestion'}</span>
        </div>
      </div>

      {/* Scrollable Message Thread */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto space-y-6 py-8">
            <div className="w-16 h-16 rounded-3xl bg-gradient-to-tr from-teal-500 to-emerald-400 flex items-center justify-center shadow-lg shadow-teal-500/20 text-white">
              <Bot className="w-8 h-8 stroke-[2]" />
            </div>
            
            <div>
              <h3 className="text-lg font-bold text-slate-800">Welcome to AlphaRead</h3>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                Upload financial PDFs or fetch stock ticker 10-K reports in the left panel, then ask any quantitative or analytical question below.
              </p>
            </div>

            {/* Starter Prompts */}
            <div className="w-full space-y-2 pt-2">
              <div className="flex items-center justify-center space-x-1.5 text-xs font-semibold text-slate-400">
                <Compass className="w-3.5 h-3.5" />
                <span>Recommended Financial Queries:</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left">
                {starterPrompts.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => handlePromptClick(prompt)}
                    className="p-3 bg-slate-50 hover:bg-teal-50/60 border border-slate-200/70 hover:border-teal-300 rounded-2xl text-xs font-medium text-slate-700 hover:text-teal-900 transition-all shadow-sm text-left flex items-start space-x-2"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-teal-600 shrink-0 mt-0.5" />
                    <span className="leading-snug">{prompt}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, index) => (
              <MessageBubble key={index} message={msg} />
            ))}
            
            {/* Thinking / Streaming Loading State */}
            {isSending && (
              <div className="flex items-center space-x-3 my-3">
                <div className="w-8 h-8 rounded-2xl bg-teal-50 text-teal-600 flex items-center justify-center border border-teal-100">
                  <Loader2 className="w-4 h-4 animate-spin" />
                </div>
                <div className="bg-slate-50 border border-slate-200/60 text-slate-600 text-xs px-4 py-3 rounded-2xl flex items-center space-x-2 font-medium">
                  <span className="animate-pulse">Retrieving top 3 ChromaDB chunks & synthesizing answer...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Fixed Bottom Input Area */}
      <div className="p-4 border-t border-slate-100 bg-white shrink-0">
        <form onSubmit={handleSubmit} className="relative flex items-center">
          <textarea
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your financial documents (Press Enter to send)..."
            className="w-full pl-4 pr-14 py-3.5 text-sm bg-slate-50 border border-slate-200 rounded-full focus:outline-none focus:ring-2 focus:ring-teal-500/30 focus:border-teal-500 font-medium placeholder:text-slate-400 transition-all resize-none max-h-32"
            disabled={isSending}
          />
          <button
            type="submit"
            disabled={isSending || !input.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 w-9 h-9 rounded-full bg-slate-800 hover:bg-slate-900 disabled:opacity-40 text-white flex items-center justify-center transition-all shadow-md shrink-0"
          >
            {isSending ? (
              <Loader2 className="w-4 h-4 animate-spin text-teal-300" />
            ) : (
              <Send className="w-4 h-4 stroke-[2.2]" />
            )}
          </button>
        </form>
        <p className="text-[10px] text-center text-slate-400 mt-2 font-medium">
          AlphaRead uses HuggingFace embeddings & ChromaDB vector store for accurate source citations.
        </p>
      </div>

    </div>
  );
}
