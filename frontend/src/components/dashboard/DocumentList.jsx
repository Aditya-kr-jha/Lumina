import { useState } from 'react';
import { Search, FileX, AlertCircle } from 'lucide-react';
import { useDocuments } from '../../context/DocumentContext';
import { useChat } from '../../context/ChatContext';
import DocumentCard from './DocumentCard';
import { showToast } from '../common/Toast';
import Loader from '../common/Loader';
import { DOCUMENT_STATUS } from '../../utils/constants';

const DocumentList = ({ searchQuery = '' }) => {
  const { documents, currentDocument, selectDocument, deleteDocument, loading } = useDocuments();
  const { startNewChat } = useChat();
  
  const filteredDocuments = documents.filter((doc) =>
    doc.filename.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  const handleDocumentClick = (document) => {
    if (document.status !== DOCUMENT_STATUS.READY) {
      showToast('Document is still processing. Please wait.', 'warning');
      return;
    }
    
    selectDocument(document);
    startNewChat();
  };
  
  const handleDeleteDocument = async (documentId) => {
    const result = await deleteDocument(documentId);
    
    if (result.success) {
      showToast('Document deleted successfully', 'success');
    } else {
      showToast(result.error || 'Failed to delete document', 'error');
    }
  };
  
  // State 1: Loading
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-16">
        <Loader size="lg" color="primary" variant="spinner" />
        <p className="text-sm text-gray-500 mt-4">Loading documents...</p>
      </div>
    );
  }

  // State 2: Empty (no documents)
  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-4">
        <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mb-4 shadow-sm">
          <FileX className="text-gray-400" size={40} />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No documents yet</h3>
        <p className="text-sm text-gray-500 text-center max-w-xs">
          Upload a PDF document to get started with AI-powered analysis
        </p>
      </div>
    );
  }

  // State 3: Loaded (with documents)
  return (
    <div className="space-y-2">
      {filteredDocuments.length === 0 ? (
        // Empty search results
        <div className="flex flex-col items-center justify-center py-12 px-4">
          <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mb-3">
            <Search className="text-gray-400" size={20} />
          </div>
          <h3 className="text-base font-medium text-gray-900 mb-1">No documents found</h3>
          <p className="text-sm text-gray-500 text-center">
            Try adjusting your search terms
          </p>
        </div>
      ) : (
        filteredDocuments.map((doc) => (
          <DocumentCard
            key={doc.document_id}
            document={doc}
            isActive={currentDocument?.document_id === doc.document_id}
            onClick={() => handleDocumentClick(doc)}
            onDelete={handleDeleteDocument}
          />
        ))
      )}
    </div>
  );
};

export default DocumentList;
