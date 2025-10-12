import { useEffect, useState } from 'react';
import { Settings, Menu } from 'lucide-react';
import { useDocuments } from '../context/DocumentContext';
import Sidebar from '../components/dashboard/Sidebar';
import ChatArea from '../components/dashboard/ChatArea';
import Modal from '../components/common/Modal';
import { getDocumentById, getDocumentStats } from '../services/documentService';
import { formatFileSize, formatDateTime } from '../utils/formatters';
import Loader from '../components/common/Loader';

const Dashboard = () => {
  const { fetchDocuments, currentDocument } = useDocuments();
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [documentDetails, setDocumentDetails] = useState(null);
  const [documentStats, setDocumentStats] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);
  
  const handleShowDetails = async () => {
    if (!currentDocument) return;
    
    setShowDetailsModal(true);
    setLoadingDetails(true);
    
    try {
      const [details, stats] = await Promise.all([
        getDocumentById(currentDocument.document_id),
        getDocumentStats(currentDocument.document_id),
      ]);
      
      setDocumentDetails(details);
      setDocumentStats(stats);
    } catch (err) {
      console.error('Failed to fetch document details:', err);
    } finally {
      setLoadingDetails(false);
    }
  };
  
  return (
    <div className="flex h-screen overflow-hidden bg-gradient-to-b from-[#A020F0] via-[#6366F1] to-[#00D9FF]">
      {/* Hamburger Menu Button - Mobile Only */}
      <button
        onClick={() => setSidebarOpen(true)}
        className="fixed top-4 left-4 z-30 lg:hidden p-3 bg-white/90 backdrop-blur-sm rounded-xl shadow-lg hover:bg-white transition-all hover:scale-105"
        aria-label="Open menu"
      >
        <Menu size={24} className="text-gray-700" />
      </button>

      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <ChatArea onShowDetails={handleShowDetails} />
      </div>
      
      {/* Document Details Modal */}
      <Modal
        isOpen={showDetailsModal}
        onClose={() => setShowDetailsModal(false)}
        title="Document Details"
        size="md"
      >
        {loadingDetails ? (
          <Loader />
        ) : (
          <div className="space-y-4">
            {documentDetails && (
              <>
                <div>
                  <label className="text-sm font-medium text-gray-700">Filename</label>
                  <p className="text-gray-900 mt-1">{documentDetails.filename}</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">File Size</label>
                    <p className="text-gray-900 mt-1">{formatFileSize(documentDetails.file_size)}</p>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-700">Pages</label>
                    <p className="text-gray-900 mt-1">{documentDetails.pages}</p>
                  </div>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-gray-700">Upload Date</label>
                  <p className="text-gray-900 mt-1">{formatDateTime(documentDetails.upload_time)}</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Status</label>
                    <p className="text-gray-900 mt-1 capitalize">{documentDetails.status}</p>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-700">Chunks</label>
                    <p className="text-gray-900 mt-1">{documentDetails.chunk_count}</p>
                  </div>
                </div>
              </>
            )}
            
            {documentStats && (
              <>
                <div className="border-t pt-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Query Statistics</h3>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">Total Queries</label>
                      <p className="text-gray-900 mt-1">{documentStats.query_count}</p>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium text-gray-700">Sessions</label>
                      <p className="text-gray-900 mt-1">{documentStats.unique_sessions}</p>
                    </div>
                  </div>
                  
                  {documentStats.first_query && (
                    <div className="mt-4">
                      <label className="text-sm font-medium text-gray-700">First Query</label>
                      <p className="text-gray-900 mt-1">{formatDateTime(documentStats.first_query)}</p>
                    </div>
                  )}
                  
                  {documentStats.last_query && (
                    <div className="mt-4">
                      <label className="text-sm font-medium text-gray-700">Last Query</label>
                      <p className="text-gray-900 mt-1">{formatDateTime(documentStats.last_query)}</p>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Dashboard;
