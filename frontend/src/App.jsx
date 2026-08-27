import React, { useState, useEffect } from 'react';
import ProgressSpine from './components/ProgressSpine';
import VerticalRail from './components/VerticalRail';
import Header from './components/Header';
import HeroCatalogue from './components/HeroCatalogue';
import ChatPanel from './components/ChatPanel';
import EditionsTable from './components/EditionsTable';
import MetricsGrid from './components/MetricsGrid';
import ProcessList from './components/ProcessList';
import FooterClose from './components/FooterClose';

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
  const [selectedVariantIndex, setSelectedVariantIndex] = useState(0);

  // Initial data load & health check
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
    setStatusMessage(`Ingesting PDF file '${file.name}' into vector memory...`);

    try {
      const result = await uploadPDFFile(file);
      setStatusMessage(`Success! Ingested '${file.name}' (${result.chunks_created || 1} chunks created).`);
      await loadDocumentsList();
    } catch (err) {
      setErrorMessage(err.message || "Failed to upload and ingest PDF.");
    } finally {
      setIsProcessing(false);
    }
  };

  // Ingest SEC 10-K Ticker Handler
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

  // Select Variant Handler
  const handleSelectVariant = (idx) => {
    setSelectedVariantIndex(idx);
    const tickers = ['MSFT', 'NVDA', 'AAPL', 'TSLA', 'AMZN', 'GOOGL'];
    const selectedTicker = tickers[idx];
    if (selectedTicker) {
      handleIngestSEC(selectedTicker, ["Item 1A", "Item 7"]);
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
        text: `Error processing query: ${err.message || 'Server error'}. Please ensure the backend is running.`,
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
    if (!window.confirm("Are you sure you want to clear all vector memory from the database?")) return;
    clearMessagesAndBanners();
    try {
      await clearVectorDatabase();
      setDocuments([]);
      setMessages([]);
      setStatusMessage("Vector store memory cleared successfully.");
    } catch (err) {
      setErrorMessage("Failed to clear vector database index.");
    }
  };

  return (
    <div className="relative min-h-screen bg-[#E8E6DF] text-[#151515] font-mono selection:bg-[#C4442C] selection:text-[#E8E6DF]">
      
      {/* 1. Fixed Progress Spine */}
      <ProgressSpine />

      {/* 2. Fixed Left Vertical Rail */}
      <VerticalRail />

      {/* 3. Main Content Offset by 34px Left Rail on Desktop */}
      <div className="md:pl-[34px] flex flex-col min-h-screen">
        
        {/* Header Navigation */}
        <Header
          health={health}
          onClearDatabase={handleClearDatabase}
          documentsCount={documents.length}
        />

        {/* Hero Catalogue Section */}
        <HeroCatalogue
          selectedVariantIndex={selectedVariantIndex}
          onSelectVariant={handleSelectVariant}
          onIngestSEC={handleIngestSEC}
        />

        {/* Section 01: Quantitative Query Terminal */}
        <ChatPanel
          messages={messages}
          onSendMessage={handleSendMessage}
          isSending={isSendingChat}
          documentsCount={documents.length}
        />

        {/* Section 02: SEC Editions Table & PDF Zone */}
        <EditionsTable
          onIngestSEC={handleIngestSEC}
          onUploadPDF={handleUploadPDF}
          documents={documents}
          onDeleteDocument={handleDeleteDocument}
          isProcessing={isProcessing}
          statusMessage={statusMessage}
          errorMessage={errorMessage}
        />

        {/* Section 03: Architecture Metrics Three-Cell Grid */}
        <MetricsGrid />

        {/* Section 04: Execution Pipeline Process List */}
        <ProcessList />

        {/* Section 05: System Close & Cropped Wordmark */}
        <FooterClose
          health={health}
          onClearDatabase={handleClearDatabase}
        />

      </div>

    </div>
  );
}
