import api from './api';
import { API_ENDPOINTS } from '../config/api';
import { CHAT_CONFIG } from '../utils/constants';

/**
 * Send chat query
 * @param {object} queryData - { question, document_id, session_id, include_sources, top_k }
 * @returns {Promise<object>} Chat response
 */
export const sendChatQuery = async (queryData) => {
  const response = await api.post(API_ENDPOINTS.CHAT_QUERY, {
    question: queryData.question,
    document_id: queryData.document_id,
    session_id: queryData.session_id,
    include_sources: queryData.include_sources ?? true,
    top_k: queryData.top_k ?? CHAT_CONFIG.DEFAULT_TOP_K,
  });
  return response.data;
};

/**
 * Get all chat sessions
 * @returns {Promise<object>} Sessions list
 */
export const getChatSessions = async () => {
  const response = await api.get(API_ENDPOINTS.CHAT_SESSIONS);
  return response.data;
};

/**
 * Get chat history for session
 * @param {string} sessionId
 * @returns {Promise<object>} Chat history
 */
export const getChatHistory = async (sessionId) => {
  const response = await api.get(API_ENDPOINTS.CHAT_HISTORY(sessionId));
  return response.data;
};

/**
 * Delete chat session
 * @param {string} sessionId
 * @returns {Promise<object>} Delete response
 */
export const deleteChatSession = async (sessionId) => {
  const response = await api.delete(API_ENDPOINTS.CHAT_SESSION_DELETE(sessionId));
  return response.data;
};

/**
 * Clear all chat sessions
 * @returns {Promise<object>} Clear response
 */
export const clearAllSessions = async () => {
  const response = await api.delete(API_ENDPOINTS.CHAT_CLEAR_ALL);
  return response.data;
};

/**
 * Get user query statistics
 * @returns {Promise<object>} Query stats
 */
export const getQueryStats = async () => {
  const response = await api.get(API_ENDPOINTS.CHAT_STATS_QUERIES);
  return response.data;
};
