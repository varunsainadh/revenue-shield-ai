const BASE_URL = '/api';

export async function fetchHealth() {
  const res = await fetch(`${BASE_URL}/health`);
  return res.json();
}

export async function fetchMetrics() {
  const res = await fetch(`${BASE_URL}/metrics`);
  return res.json();
}

export async function fetchAnalytics() {
  const res = await fetch(`${BASE_URL}/analytics`);
  return res.json();
}

export async function fetchCases(filters = {}) {
  const query = new URLSearchParams(filters).toString();
  const res = await fetch(`${BASE_URL}/cases?${query}`);
  return res.json();
}

export async function fetchCase(id) {
  const res = await fetch(`${BASE_URL}/cases/${id}`);
  return res.json();
}

export async function analyzeCase(id) {
  const res = await fetch(`${BASE_URL}/cases/${id}/analyze`, { method: 'POST' });
  return res.json();
}

export async function recoverCase(id) {
  const res = await fetch(`${BASE_URL}/cases/${id}/recover`, { method: 'POST' });
  return res.json();
}

export async function approveCase(id) {
  const res = await fetch(`${BASE_URL}/cases/${id}/approve`, { method: 'POST' });
  return res.json();
}

export async function rejectCase(id, reason) {
  const res = await fetch(`${BASE_URL}/cases/${id}/reject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reason })
  });
  return res.json();
}

export async function stopCase(id, reason) {
  const res = await fetch(`${BASE_URL}/cases/${id}/stop`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ reason })
  });
  return res.json();
}

export async function fetchManualReviews() {
  const res = await fetch(`${BASE_URL}/manual-review`);
  return res.json();
}

export async function fetchAuditLogs(filters = {}) {
  const query = new URLSearchParams(filters).toString();
  const res = await fetch(`${BASE_URL}/audit?${query}`);
  return res.json();
}

export async function fetchSettings() {
  const res = await fetch(`${BASE_URL}/settings`);
  return res.json();
}

export async function updateSettings(data) {
  const res = await fetch(`${BASE_URL}/settings`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return res.json();
}

export async function seedDemoData() {
  const res = await fetch(`${BASE_URL}/demo/seed`, { method: 'POST' });
  return res.json();
}

/* --- NEW API ENDPOINTS FOR PLATFORM UPGRADE --- */

export async function fetchChargebacks() {
  const res = await fetch(`${BASE_URL}/chargebacks`);
  return res.json();
}

export async function predictChargeback(data) {
  const res = await fetch(`${BASE_URL}/chargebacks/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return res.json();
}

export async function fetchFraudAlerts(status = null) {
  const url = status ? `${BASE_URL}/fraud/alerts?status=${status}` : `${BASE_URL}/fraud/alerts`;
  const res = await fetch(url);
  return res.json();
}

export async function resolveFraudAlert(id, status = 'RESOLVED', notes = '') {
  const res = await fetch(`${BASE_URL}/fraud/alerts/${id}/resolve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, resolution_notes: notes })
  });
  return res.json();
}

export async function askCopilot(query) {
  const res = await fetch(`${BASE_URL}/copilot/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
  return res.json();
}

export async function fetchRefunds() {
  const res = await fetch(`${BASE_URL}/refunds`);
  return res.json();
}

export async function processRefund(payment_id, amount, reason = '') {
  const res = await fetch(`${BASE_URL}/razorpay/refund`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ payment_id, amount, reason })
  });
  return res.json();
}
