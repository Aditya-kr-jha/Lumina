import { FileText, MessageSquare, Settings } from 'lucide-react';
import { useChat } from '../../context/ChatContext';
import { useDocuments } from '../../context/DocumentContext';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import { EXAMPLE_QUESTIONS } from '../../utils/constants';
import { formatFileSize } from '../../utils/formatters';

const ChatArea = ({ onShowDetails }) => {
  const { messages, sendMessage } = useChat();
  const { currentDocument } = useDocuments();
  
  const handleExampleClick = async (question) => {
    if (currentDocument) {
      await sendMessage(question, currentDocument.document_id);
    }
  };
  
  const renderEmptyState = () => {
    if (!currentDocument) {
      return (
        <div className="flex flex-col items-center justify-center h-full text-center px-4">
          <FileText className="text-gray-300 mb-4" size={64} />
          <h3 className="text-lg font-semibold text-gray-700 mb-2">
            Select a document from the sidebar
          </h3>
          <p className="text-gray-500">
            Upload a PDF to get started with AI-powered document analysis
          </p>
        </div>
      );
    }
    
    if (messages.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center h-full text-center px-4">
          <MessageSquare className="text-gray-300 mb-4" size={64} />
          <h3 className="text-lg font-semibold text-gray-700 mb-2">
            Ask anything about this document
          </h3>
          <p className="text-gray-500 mb-6">
            Try one of these example questions:
          </p>
          
          <div className="flex flex-wrap gap-2 justify-center max-w-2xl">
            {EXAMPLE_QUESTIONS.map((question, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(question)}
                className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 hover:border-primary-500 transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      );
    }
    
    return null;
  };
  
  return (
    <div className="flex flex-col h-full bg-white overflow-hidden">
      {/* Section 1: Header Bar (Top - Fixed) */}
      <div className="border-b border-gray-200 px-6 py-4 flex items-center justify-between bg-white">
        <div>
          <h2 className="text-lg font-medium text-gray-900">
            {currentDocument ? currentDocument.filename : 'Select a document'}
          </h2>
          {currentDocument && (
            <p className="text-sm text-gray-500">
              {currentDocument.pages} pages • {formatFileSize(currentDocument.file_size)}
            </p>
          )}
        </div>
        
        {currentDocument && (
          <button
            onClick={onShowDetails}
            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <Settings size={20} />
          </button>
        )}
      </div>
      
      {/* Section 2: Message Area (Middle - Scrollable) */}
      <div className="flex-1 overflow-y-auto bg-white">
        <div className="p-6">
          {messages.length > 0 ? <MessageList /> : renderEmptyState()}
        </div>
      </div>
      
      {/* Section 3: Input Area (Bottom - Fixed) */}
      <div className="border-t border-gray-200 p-4 bg-white">
        <MessageInput />
      </div>
    </div>
  );
};

export default ChatArea;
