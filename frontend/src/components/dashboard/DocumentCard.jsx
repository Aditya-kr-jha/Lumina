import { CheckCircle, Loader2, AlertCircle, Trash2, FileText } from 'lucide-react';
import { DOCUMENT_STATUS } from '../../utils/constants';
import { formatFileSize, formatRelativeTime, truncateText } from '../../utils/formatters';

const DocumentCard = ({ document, isActive, onClick, onDelete }) => {
  const getStatusIcon = () => {
    switch (document.status) {
      case DOCUMENT_STATUS.READY:
        return <CheckCircle className="text-white" size={18} />;
      case DOCUMENT_STATUS.PROCESSING:
        return <Loader2 className="text-white animate-spin" size={18} />;
      case DOCUMENT_STATUS.ERROR:
        return <AlertCircle className="text-white" size={18} />;
      default:
        return <FileText className="text-white" size={18} />;
    }
  };

  const getStatusColor = () => {
    switch (document.status) {
      case DOCUMENT_STATUS.READY:
        return 'bg-green-500';
      case DOCUMENT_STATUS.PROCESSING:
        return 'bg-blue-500';
      case DOCUMENT_STATUS.ERROR:
        return 'bg-red-500';
      default:
        return 'bg-gray-400';
    }
  };
  
  const handleDelete = (e) => {
    e.stopPropagation();
    if (window.confirm(`Delete "${document.filename}"?`)) {
      onDelete(document.document_id);
    }
  };
  
  return (
    <div
      onClick={onClick}
      role="button"
      tabIndex={0}
      aria-label={`Document: ${document.filename}, Status: ${document.status}`}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
      className={`mb-2 p-3.5 bg-white border rounded-lg cursor-pointer transition-all duration-200 group focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-1 ${
        isActive 
          ? 'bg-purple-50 border-purple-400 shadow-md' 
          : 'border-gray-200 hover:bg-gray-50 hover:border-gray-300 hover:shadow-sm'
      }`}
    >
      <div className="flex items-start gap-3">
        {/* Status Icon Section */}
        <div className={`flex-shrink-0 w-9 h-9 rounded-lg ${getStatusColor()} flex items-center justify-center shadow-sm`}>
          {getStatusIcon()}
        </div>
        
        {/* Information Section */}
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-medium text-gray-900 truncate mb-1">
            {truncateText(document.filename, 30)}
          </h3>
          
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span>{formatFileSize(document.file_size)}</span>
            <span>•</span>
            <span>{formatRelativeTime(document.upload_time)}</span>
          </div>
          
          {document.pages && (
            <div className="mt-1 text-xs text-gray-500">
              {document.pages} pages
              {document.chunk_count && ` • ${document.chunk_count} chunks`}
            </div>
          )}
          
          {document.status === DOCUMENT_STATUS.PROCESSING && (
            <div className="mt-1 text-xs text-blue-600 font-medium">Processing...</div>
          )}
          
          {document.status === DOCUMENT_STATUS.ERROR && (
            <div className="mt-1 text-xs text-red-600 font-medium">Processing failed</div>
          )}
        </div>
        
        {/* Invisible flex spacer for future actions */}
        <div className="flex-shrink-0 w-6">
          <button
            onClick={handleDelete}
            className="opacity-0 group-hover:opacity-100 transition-opacity text-gray-400 hover:text-red-600 p-1"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentCard;
