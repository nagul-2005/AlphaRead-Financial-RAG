import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import IngestionPanel from './components/IngestionPanel';
import ChatPanel from './components/ChatPanel';
import {
  fetchHealth,
  uploadPDFFile,
  ingestSECTicker,
  sendChatMessage,
  getIngestedDocuments,
  deleteSingleDocument,
  clearVectorDatabase
} from './api';

export default function App() {
  const [health, setHealth] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [messages, setMessages] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSendingChat, setIsSendingChat] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  // Initial load
  useEffect(() => {
    checkHealthStatus();
    loadDocumentsList();
  }, []);

  const checkHealthStatus = async () => {
    try {
      const data = await fetchHealth();
      setHealth(data);
    } catch (err) {
      console.warn("Backend health check warning:", err.message);
      setHealth(null);
    }
  };

  const loadDocumentsList = async () => {
    try {
      const data = await getIngestedDocuments();
      setDocuments(data.documents || []);
    } catch (err) {
      console.warn("Error fetching document list:", err.message);
    }
  };

  const clearMessagesAndBanners = () => {
    setStatusMessage(null);
    setErrorMessage(null);
  };

  // Upload PDF Handler
  const handleUploadPDF = async (file) => {
    clearMessagesAndBanners();
    setIsProcessing(true);
    setStatusMessage(`Ingesting PDF file '${file.name}' into vector store...`);

    try {
      const result = await uploadPDFFile(file);
      setStatusMessage(`Success! Ingested '${file.name}' (${result.chunks_created} chunks created).`);
      await loadDocumentsList();
    } catch (err) {
      setErrorMessage(err.message || "Failed to upload and ingest PDF.");
    } finally {
      setIsProcessing(false);
    }
  };

  // Ingest SEC 10-K Ticker Handler with Sections
  const handleIngestSEC = async (ticker, sections = ["Item 1A", "Item 7"]) => {
    clearMessagesAndBanners();
    setIsProcessing(true);
    setStatusMessage(`Fetching SEC 10-K sections (${sections.join(', ')}) for ticker '${ticker.toUpperCase()}'...`);

    try {
      const result = await ingestSECTicker(ticker, sections);
      setStatusMessage(
        `Successfully ingested ${ticker.toUpperCase()} 10-K (${result.sections_ingested} sections, ${result.chunks_created} chunks created).`
      );
      await loadDocumentsList();
    } catch (err) {
      setErrorMessage(err.message || `Failed to fetch 10-K for ${ticker}.`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Delete Single Document Handler
  const handleDeleteDocument = async (sourceName) => {
    clearMessagesAndBanners();
    try {
      await deleteSingleDocument(sourceName);
      setStatusMessage(`Deleted '${sourceName}' from vector memory.`);
      await loadDocumentsList();
    } catch (err) {
      setErrorMessage(err.message || `Failed to delete '${sourceName}'.`);
    }
  };

  // Send Chat Message Handler
  const handleSendMessage = async (userText) => {
    clearMessagesAndBanners();
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const userMsg = { sender: 'user', text: userText, timestamp };
    setMessages((prev) => [...prev, userMsg]);
    setIsSendingChat(true);

    try {
      const data = await sendChatMessage(userText);
      const aiMsg = {
        sender: 'ai',
        text: data.answer,
        citations: data.citations || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      const errorMsg = {
        sender: 'ai',
        text: `Error processing query: ${err.message || 'Server error'}. Make sure the backend server is running on port 8000.`,
        citations: [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsSendingChat(false);
    }
  };

  // Clear Database Index Handler
  const handleClearDatabase = async () => {
    if (!window.confirm("Are you sure you want to clear all vectors from the database index?")) return;
    clearMessagesAndBanners();
    try {
      await clearVectorDatabase();
      setDocuments([]);
      setMessages([]);
      setStatusMessage("Vector store cleared successfully.");
    } catch (err) {
      setErrorMessage("Failed to clear database index.");
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-50 font-sans overflow-hidden">
      
      {/* Header */}
      <Header
        health={health}
        onClearDatabase={handleClearDatabase}
        documentsCount={documents.length}
      />

      {/* Main 2-Column Dashboard Layout */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 p-6 overflow-hidden max-w-7xl mx-auto w-full">
        
        {/* Left Column: Data & SEC Ingestion (5 Cols = ~40% width) */}
        <div className="lg:col-span-5 h-full overflow-hidden">
          <IngestionPanel
            onUploadPDF={handleUploadPDF}
            onIngestSEC={handleIngestSEC}
            onDeleteDocument={handleDeleteDocument}
            documents={documents}
            isProcessing={isProcessing}
            statusMessage={statusMessage}
            errorMessage={errorMessage}
          />
        </div>

        {/* Right Column: Chat Interface (7 Cols = ~60% width) */}
        <div className="lg:col-span-7 h-full overflow-hidden">
          <ChatPanel
            messages={messages}
            onSendMessage={handleSendMessage}
            isSending={isSendingChat}
            documentsCount={documents.length}
          />
        </div>

      </main>

    </div>
  );
}
