const API_URL = "http://localhost:8000";


// Get the JWT token saved after login
function getToken() {
  return localStorage.getItem("cyberpulse_token");
}


// Common headers for authenticated requests
function authHeaders() {
  const token = getToken();

  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}


// =========================
// REGISTER
// =========================

export async function registerUser(username, email, password) {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username,
      email,
      password,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Registration failed");
  }

  return data;
}


// =========================
// LOGIN
// =========================

export async function loginUser(username, password) {
  const formData = new URLSearchParams();

  formData.append("username", username);
  formData.append("password", password);

  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Login failed");
  }

  // Save JWT for future API requests
  localStorage.setItem("cyberpulse_token", data.access_token);

  return data;
}


// =========================
// LOGOUT
// =========================

export function logoutUser() {
  localStorage.removeItem("cyberpulse_token");
}


// =========================
// CHECK LOGIN
// =========================

export function isLoggedIn() {
  return Boolean(getToken());
}


// =========================
// POST SECURITY LOG
// =========================

export async function sendLog(logData) {
  const response = await fetch(`${API_URL}/logs`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(logData),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to send log");
  }

  return data;
}


// =========================
// GET ALERTS
// =========================

export async function getAlerts() {
  const response = await fetch(`${API_URL}/alerts`, {
    method: "GET",
    headers: authHeaders(),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to retrieve alerts");
  }

  return data;
}


// =========================
// PATCH ALERT STATUS
// =========================

export async function updateAlertStatus(alertId, status) {
  const response = await fetch(
    `${API_URL}/alerts/${alertId}?status=${encodeURIComponent(status)}`,
    {
      method: "PATCH",
      headers: authHeaders(),
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to update alert");
  }

  return data;
}