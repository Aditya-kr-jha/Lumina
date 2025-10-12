import { createContext, useState, useContext, useCallback } from 'react';
import {
  getDocuments,
  uploadDocument,
  uploadMultipleDocuments,
  deleteDocument as deleteDocumentService,
  getDocumentStatus,
} from '../services/documentService';
import { DOCUMENT_STATUS, CHAT_CONFIG } from '../utils/constants';

const DocumentContext = createContext(null);

export const DocumentProvider = ({ children }) => {
  const [documents, setDocuments] = useState([]);
  const [currentDocument, setCurrentDocument] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState({});

  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getDocuments();
      setDocuments(data.documents || []);
    } catch (err) {
      console.error('Failed to fetch documents:', err);
      setError(err.response?.data?.detail || 'Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  }, []);

  const uploadSingleDocument = async (file) => {
    try {
      setError(null);
      
      const data = await uploadDocument(file, (progress) => {
        setUploadProgress((prev) => ({ ...prev, [file.name]: progress }));
      });

      // Add document to list
      setDocuments((prev) => [data, ...prev]);

      // Start polling for processing status
      if (data.status === DOCUMENT_STATUS.PROCESSING) {
        pollDocumentStatus(data.document_id);
      }

      // Clear upload progress
      setUploadProgress((prev) => {
        const newProgress = { ...prev };
        delete newProgress[file.name];
        return newProgress;
      });

      return { success: true, data };
    } catch (err) {
      console.error('Upload failed:', err);
      setError(err.response?.data?.detail || 'Upload failed');
      
      // Clear upload progress
      setUploadProgress((prev) => {
        const newProgress = { ...prev };
        delete newProgress[file.name];
        return newProgress;
      });
      
      return { success: false, error: err.response?.data?.detail || 'Upload failed' };
    }
  };

  const uploadMultiple = async (files) => {
    try {
      setError(null);
      
      const data = await uploadMultipleDocuments(files, (progress) => {
        setUploadProgress((prev) => ({ ...prev, batch: progress }));
      });

      // Add successful uploads to list
      if (data.results) {
        setDocuments((prev) => [...data.results, ...prev]);

        // Start polling for processing documents
        data.results.forEach((doc) => {
          if (doc.status === DOCUMENT_STATUS.PROCESSING) {
            pollDocumentStatus(doc.document_id);
          }
        });
      }

      // Clear upload progress
      setUploadProgress((prev) => {
        const newProgress = { ...prev };
        delete newProgress.batch;
        return newProgress;
      });

      return { success: true, data };
    } catch (err) {
      console.error('Batch upload failed:', err);
      setError(err.response?.data?.detail || 'Batch upload failed');
      
      setUploadProgress((prev) => {
        const newProgress = { ...prev };
        delete newProgress.batch;
        return newProgress;
      });
      
      return { success: false, error: err.response?.data?.detail || 'Batch upload failed' };
    }
  };

  const pollDocumentStatus = async (documentId) => {
    try {
      const data = await getDocumentStatus(documentId);

      // Update document in list
      setDocuments((prev) =>
        prev.map((doc) =>
          doc.document_id === documentId
            ? { ...doc, status: data.status, chunk_count: data.chunk_count }
            : doc
        )
      );

      // Continue polling if still processing
      if (data.status === DOCUMENT_STATUS.PROCESSING) {
        setTimeout(() => pollDocumentStatus(documentId), CHAT_CONFIG.POLLING_INTERVAL);
      }
    } catch (err) {
      console.error('Failed to poll document status:', err);
      // Mark as error
      setDocuments((prev) =>
        prev.map((doc) =>
          doc.document_id === documentId ? { ...doc, status: DOCUMENT_STATUS.ERROR } : doc
        )
      );
    }
  };

  const deleteDocument = async (documentId) => {
    try {
      setError(null);
      await deleteDocumentService(documentId);

      // Remove from list
      setDocuments((prev) => prev.filter((doc) => doc.document_id !== documentId));

      // Clear current document if it was deleted
      if (currentDocument?.document_id === documentId) {
        setCurrentDocument(null);
      }

      return { success: true };
    } catch (err) {
      console.error('Failed to delete document:', err);
      setError(err.response?.data?.detail || 'Failed to delete document');
      return { success: false, error: err.response?.data?.detail || 'Failed to delete document' };
    }
  };

  const selectDocument = (document) => {
    setCurrentDocument(document);
  };

  const value = {
    documents,
    currentDocument,
    loading,
    error,
    uploadProgress,
    fetchDocuments,
    uploadSingleDocument,
    uploadMultiple,
    deleteDocument,
    selectDocument,
    setCurrentDocument,
  };

  return <DocumentContext.Provider value={value}>{children}</DocumentContext.Provider>;
};

export const useDocuments = () => {
  const context = useContext(DocumentContext);
  if (!context) {
    throw new Error('useDocuments must be used within a DocumentProvider');
  }
  return context;
};

export default DocumentContext;
