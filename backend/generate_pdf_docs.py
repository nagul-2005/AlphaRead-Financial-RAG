import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

def create_project_pdf(output_filename="AlphaRead_Project_Documentation.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0f766e"), # Teal primary
        alignment=TA_LEFT,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569"),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=14,
        spaceAfter=8
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#0f766e"),
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        leftIndent=12,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"),
        borderColor=colors.HexColor("#e2e8f0"),
        borderWidth=0.5,
        borderPadding=4,
        spaceAfter=6
    )

    story = []

    # Title & Header
    story.append(Paragraph("AlphaRead — Project Technical Documentation", title_style))
    story.append(Paragraph("Full-Stack Financial GenAI RAG Application (FastAPI + React + Llama-3)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0d9488"), spaceAfter=12))

    # Executive Summary
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph(
        "<b>AlphaRead</b> is a production-grade, full-stack Retrieval-Augmented Generation (RAG) web application "
        "engineered for querying, analyzing, and citing financial statements, annual reports, and US SEC 10-K filings in real time. "
        "It combines a FastAPI Python backend with a humanized React frontend (Vite + Tailwind CSS v4), embedding financial documents "
        "via HuggingFace sentence transformers, storing dense vectors in memory, and invoking Groq's high-speed <b>Llama-3 LLM</b> "
        "to deliver fact-grounded analytical reports with interactive, verifiable Source Citations.",
        body_style
    ))

    # Live Cloud URLs Table
    story.append(Paragraph("2. Live Cloud Deployment Specifications", h1_style))
    url_data = [
        [Paragraph("<b>Component</b>", body_style), Paragraph("<b>Platform</b>", body_style), Paragraph("<b>Live Public URL</b>", body_style)],
        [Paragraph("Frontend Web UI", body_style), Paragraph("Vercel (Global Edge)", body_style), Paragraph("<u>https://alpha-read-financial.vercel.app</u>", body_style)],
        [Paragraph("Backend REST API", body_style), Paragraph("Render (Python 3)", body_style), Paragraph("<u>https://alpharead-backend.onrender.com</u>", body_style)],
        [Paragraph("GitHub Repository", body_style), Paragraph("GitHub (Public)", body_style), Paragraph("<u>https://github.com/nagul-2005/AlphaRead-Financial-RAG</u>", body_style)]
    ]
    t_urls = Table(url_data, colWidths=[120, 130, 280])
    t_urls.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#ccfbf1")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#0f766e")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_urls)
    story.append(Spacer(1, 10))

    # Key Features
    story.append(Paragraph("3. Core Application Features", h1_style))
    story.append(Paragraph("• <b>Dual Ingestion Pipeline:</b> Drag-and-drop PDF statement uploader alongside a 1-click SEC EDGAR 10-K ticker fetcher (AAPL, NVDA, MSFT, TSLA, AMZN, GOOGL, META, etc.).", bullet_style))
    story.append(Paragraph("• <b>Dynamic SEC Section Selection:</b> Allows users to customize 10-K section extraction prior to ingestion (Item 1 Business, Item 1A Risk Factors, Item 7 MD&A, Item 8 Financial Statements).", bullet_style))
    story.append(Paragraph("• <b>Granular Document Deletion:</b> Individual trash icon (DELETE /documents/src) enabling deletion of single document vectors without wiping the entire vector memory.", bullet_style))
    story.append(Paragraph("• <b>High-Speed Vector Engine:</b> FastEmbed ONNX runtime sentence embeddings (BAAI/bge-small-en-v1.5 / all-MiniLM-L6-v2) operating under 60MB RAM footprint for low-latency retrieval.", bullet_style))
    story.append(Paragraph("• <b>Llama-3 Generative Reasoning:</b> Sub-second Groq API integration (llama-3.3-70b-versatile) producing structured financial summaries with inline source attribution.", bullet_style))
    story.append(Paragraph("• <b>Interactive Source Citations:</b> Every AI response features a collapsible drawer showing exact document names, section/page numbers, relevance match scores (%), and verbatim text snippets.", bullet_style))
    story.append(Spacer(1, 10))

    # Architecture & Technology Stack Table
    story.append(Paragraph("4. Technical Stack & Architecture", h1_style))
    tech_data = [
        [Paragraph("<b>Layer</b>", body_style), Paragraph("<b>Technology</b>", body_style), Paragraph("<b>Description / Purpose</b>", body_style)],
        [Paragraph("Frontend UI", body_style), Paragraph("React 18, Vite, Tailwind v4", body_style), Paragraph("Humanized light-theme dashboard, responsive 2-column layout.", body_style)],
        [Paragraph("Backend Web Server", body_style), Paragraph("FastAPI, Uvicorn, Python 3.13", body_style), Paragraph("Asynchronous REST API with guaranteed CORS HTTP middleware.", body_style)],
        [Paragraph("Document Parsers", body_style), Paragraph("pypdf, pdfplumber, edgartools", body_style), Paragraph("Parses uploaded PDF text & SEC EDGAR 10-K sections.", body_style)],
        [Paragraph("Chunking & Embeddings", body_style), Paragraph("LangChain, FastEmbed ONNX", body_style), Paragraph("RecursiveCharacterSplitter (1000/200) + fast ONNX dense vectors.", body_style)],
        [Paragraph("Vector Store", body_style), Paragraph("ChromaDB / Local Vector Engine", body_style), Paragraph("Cosine similarity search with persistent disk storage.", body_style)],
        [Paragraph("LLM Integration", body_style), Paragraph("Groq API (Llama-3.3)", body_style), Paragraph("Generates natural language financial answers with citations.", body_style)]
    ]
    t_tech = Table(tech_data, colWidths=[110, 150, 270])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 10))

    # API Reference
    story.append(Paragraph("5. API Endpoints Reference", h1_style))
    api_data = [
        [Paragraph("<b>HTTP Method</b>", body_style), Paragraph("<b>Endpoint Path</b>", body_style), Paragraph("<b>Function & Return Payload</b>", body_style)],
        [Paragraph("GET", body_style), Paragraph("/health", body_style), Paragraph("Checks backend status & Groq API configuration state.", body_style)],
        [Paragraph("POST", body_style), Paragraph("/upload", body_style), Paragraph("Ingests PDF statement, returns pages & chunks created.", body_style)],
        [Paragraph("POST", body_style), Paragraph("/ingest-sec", body_style), Paragraph("Fetches ticker 10-K sections, returns vector chunk stats.", body_style)],
        [Paragraph("POST", body_style), Paragraph("/chat", body_style), Paragraph("Vectorizes query, retrieves top 3 chunks, returns answer & citations.", body_style)],
        [Paragraph("GET", body_style), Paragraph("/documents", body_style), Paragraph("Lists all ingested documents, doc_types, and vector counts.", body_style)],
        [Paragraph("DELETE", body_style), Paragraph("/documents/{src}", body_style), Paragraph("Deletes vector embeddings for a specific source document.", body_style)],
        [Paragraph("DELETE", body_style), Paragraph("/clear", body_style), Paragraph("Resets vector store index completely.", body_style)]
    ]
    t_api = Table(api_data, colWidths=[80, 140, 310])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f8fafc")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_api)

    doc.build(story)
    print(f"PDF successfully created: {output_filename}")

if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "AlphaRead_Project_Documentation.pdf")
    create_project_pdf(out_path)
