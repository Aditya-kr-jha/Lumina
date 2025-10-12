import api from './api';
import { API_ENDPOINTS } from '../config/api';

/**
 * Get all documents for current user
 * @returns {Promise<object>} Documents list
 */
export const getDocuments = async () => {
  const response = await api.get(API_ENDPOINTS.DOCUMENTS);
  return response.data;
};

/**
 * Get document by ID
 * @param {string} documentId
 * @returns {Promise<object>} Document data
 */
export const getDocumentById = async (documentId) => {
  const response = await api.get(API_ENDPOINTS.DOCUMENT_BY_ID(documentId));
  return response.data;
};

/**
 * Get document status
 * @param {string} documentId
 * @returns {Promise<object>} Status data
 */
export const getDocumentStatus = async (documentId) => {
  const response = await api.get(API_ENDPOINTS.DOCUMENT_STATUS(documentId));
  return response.data;
};

/**
 * Upload single document
 * @param {File} file
 * @param {function} onProgress - Progress callback
 * @returns {Promise<object>} Upload response
 */
export const uploadDocument = async (file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post(API_ENDPOINTS.DOCUMENT_UPLOAD, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(progress);
      }
    },
  });

  return response.data;
};

/**
 * Upload multiple documents
 * @param {File[]} files
 * @param {function} onProgress - Progress callback
 * @returns {Promise<object>} Upload response
 */
export const uploadMultipleDocuments = async (files, onProgress) => {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });

  const response = await api.post(API_ENDPOINTS.BATCH_UPLOAD, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(progress);
      }
    },
  });

  return response.data;
};

/**
 * Delete document
 * @param {string} documentId
 * @returns {Promise<object>} Delete response
 */
export const deleteDocument = async (documentId) => {
  const response = await api.delete(API_ENDPOINTS.DOCUMENT_BY_ID(documentId));
  return response.data;
};

/**
 * Get document statistics
 * @param {string} documentId
 * @returns {Promise<object>} Document stats
 */
export const getDocumentStats = async (documentId) => {
  const response = await api.get(API_ENDPOINTS.CHAT_STATS_DOCUMENT(documentId));
  return response.data;
};
