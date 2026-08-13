const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "https://alpharead-backend.onrender.com";

export async function fetchHealth() {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) throw new Error("Backend server unreachable.");
  return res.json();
}

export async function uploadPDFFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to upload PDF document.");
  return data;
}

export async function ingestSECTicker(ticker, sections = ["Item 1A", "Item 7"]) {
  const res = await fetch(`${API_BASE_URL}/ingest-sec`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ticker, sections }),
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || `Failed to fetch 10-K report for ${ticker}`);
  return data;
}

export async function downloadSECDataset(tickers) {
  const res = await fetch(`${API_BASE_URL}/download-dataset`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tickers, auto_ingest: true }),
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to download dataset.");
  return data;
}

export async function sendChatMessage(message) {
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Failed to process chat query.");
  return data;
}

export async function getIngestedDocuments() {
  const res = await fetch(`${API_BASE_URL}/documents`);
  if (!res.ok) throw new Error("Failed to fetch ingested documents.");
  return res.json();
}

export async function deleteSingleDocument(sourceName) {
  const encodedSource = encodeURIComponent(sourceName);
  const res = await fetch(`${API_BASE_URL}/documents/${encodedSource}`, {
    method: "DELETE",
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || `Failed to delete document '${sourceName}'.`);
  return data;
}

export async function clearVectorDatabase() {
  const res = await fetch(`${API_BASE_URL}/clear`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to clear database.");
  return res.json();
}
