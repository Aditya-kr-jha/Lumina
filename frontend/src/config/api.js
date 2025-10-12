// API Configuration
const BASE_URL = 'http://0.0.0.0:8000';
export const API_BASE_URL = `${BASE_URL}/api/v1`;

// API endpoints
export const API_ENDPOINTS = {
  // Auth endpoints (TOKEN is outside /api/v1)
  TOKEN: `${BASE_URL}/token`,
  REGISTER: '/user/register',
  
  // User endpoints
  USER_ME: '/user/me',
  USER_CHANGE_PASSWORD: '/user/me/change-password',
  USER_DELETE: '/user/me',
  
  // Document endpoints - MUST start with /
  DOCUMENTS: '/documents/',
  DOCUMENT_UPLOAD: '/documents/upload',
  BATCH_UPLOAD: '/documents/batch-upload',
  DOCUMENT_BY_ID: (id) => `/documents/${id}`,
  DOCUMENT_STATUS: (id) => `/documents/${id}/status`,
  
  // Chat endpoints
  CHAT_QUERY: '/chat/query',
  CHAT_SESSIONS: '/chat/sessions',
  CHAT_HISTORY: (sessionId) => `/chat/history/${sessionId}`,
  CHAT_SESSION_DELETE: (sessionId) => `/chat/session/${sessionId}`,
  CHAT_CLEAR_ALL: '/chat/sessions/clear-all',
  CHAT_STATS_QUERIES: '/chat/stats/queries',
  CHAT_STATS_DOCUMENT: (documentId) => `/chat/stats/document/${documentId}`,
};

export const getApiUrl = (endpoint) => {
  if (endpoint.startsWith('http://') || endpoint.startsWith('https://')) {
    return endpoint;
  }
  return `${API_BASE_URL}${endpoint}`;
};

export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
};