const API_BASE = (
  process.env.NEXT_PUBLIC_API_URL || "/api/proxy"
).replace(/\/$/, "");

async function apiRequest(path, options = {}) {
  let res;

  try {
    res = await fetch(`${API_BASE}${path}`, options);
  } catch (err) {
    const wrapped = new Error(
      "Backend request failed. Check that the API server is running and reachable."
    );
    wrapped.cause = err;
    wrapped.isNetworkError = true;
    throw wrapped;
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    const message =
      err.detail || err.message || `Request failed (${res.status})`;
    const error = new Error(message);
    error.status = res.status;
    throw error;
  }

  return res;
}

/**
 * Upload a file and run the analysis pipeline.
 * @param {File} file
 * @returns {Promise<object>} Upload response with file_id
 */
export async function uploadFile(file) {
  const form = new FormData();
  form.append("file", file);

  const res = await apiRequest("/upload/", {
    method: "POST",
    body: form,
  });
  return res.json();
}

/**
 * Correct column mappings for a parsed file.
 * @param {string} fileId
 * @param {object} mappings
 * @returns {Promise<object>} Parse result
 */
export async function correctColumns(fileId, mappings) {
  const res = await apiRequest(`/parse/${fileId}/correct`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(mappings),
  });
  return res.json();
}

/**
 * Load persisted session payload (transactions, insights, dashboard summary).
 * @param {string} sessionId
 */
export async function fetchSession(sessionId) {
  const res = await apiRequest(`/session/${sessionId}`);
  return res.json();
}

/**
 * Fetch dashboard data for a file.
 * @param {string} fileId
 * @returns {Promise<object>}
 */
export async function fetchDashboard(fileId) {
  const res = await apiRequest(`/dashboard/${fileId}`);
  return res.json();
}

/**
 * Fetch categorized transactions with optional filters.
 * @param {string} fileId
 * @param {object} params - Query params (category, txn_type, sort_by, order, limit, offset)
 * @returns {Promise<object>}
 */
export async function fetchTransactions(fileId, params = {}) {
  const query = new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([_, v]) => v != null))
  ).toString();

  const res = await apiRequest(
    `/transactions/${fileId}${query ? `?${query}` : ""}`
  );
  return res.json();
}

/**
 * Fetch financial insights (profile + recommendations).
 * @param {string} fileId
 * @returns {Promise<object>}
 */
export async function fetchInsights(fileId) {
  const res = await apiRequest(`/insights/${fileId}`);
  return res.json();
}

/**
 * Download a PDF financial report.
 * @param {string} fileId
 */
export async function downloadReport(fileId) {
  const res = await apiRequest(`/report/${fileId}`);

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `finance_report_${fileId}.pdf`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
