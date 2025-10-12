import { useEffect, useRef, useState } from 'react';
import { useChat } from '../../context/ChatContext';
import { useDocuments } from '../../context/DocumentContext';
import Message from './Message';
import Loader from '../common/Loader';
import { MessageSquare, Bot } from 'lucide-react';

const MessageList = () => {
  const { messages, loading, regenerateLastMessage } = useChat();
  const { currentDocument } = useDocuments();
  const messagesEndRef = useRef(null);
  const [isNearBottom, setIsNearBottom] = useState(true);
  const [showScrollButton, setShowScrollButton] = useState(false);
  const containerRef = useRef(null);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  const checkIfNearBottom = () => {
    if (!containerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const threshold = 100;
    const nearBottom = scrollHeight - scrollTop - clientHeight < threshold;
    setIsNearBottom(nearBottom);
    setShowScrollButton(!nearBottom && messages.length > 0);
  };
  
  useEffect(() => {
    if (isNearBottom || messages.length === 0) {
      scrollToBottom();
    }
  }, [messages, isNearBottom]);
  
  useEffect(() => {
    const container = containerRef.current;
    if (container) {
      container.addEventListener('scroll', checkIfNearBottom);
      return () => container.removeEventListener('scroll', checkIfNearBottom);
    }
  }, []);
  
  const handleRegenerate = async () => {
    if (currentDocument) {
      await regenerateLastMessage(currentDocument.document_id);
    }
  };
  
  // State 1: Empty (New Chat)
  if (messages.length === 0 && !loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center px-4">
        <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-purple-600 rounded-full flex items-center justify-center mb-6 shadow-lg">
          <MessageSquare className="text-white" size={36} />
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-3">
          Hi! Ask me anything about your document
        </h3>
        <p className="text-base text-gray-600 max-w-md mb-8">
          I can help you understand, summarize, and answer questions about your PDF documents.
        </p>
        
        {/* Example Questions */}
        <div className="w-full max-w-lg">
          <p className="text-sm font-medium text-gray-700 mb-4">Try asking:</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {[
              "What is this document about?",
              "Summarize the key points",
              "What are the main findings?",
              "Explain the methodology"
            ].map((question, index) => (
              <div
                key={index}
                className="px-4 py-3 bg-white border border-gray-200 rounded-lg text-sm text-gray-700 hover:border-purple-400 hover:shadow-sm transition-all cursor-pointer text-left"
              >
                {question}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }
  
  // State 2: Messages Loading (less common)
  if (messages.length === 0 && loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader size="lg" color="primary" />
      </div>
    );
  }
  
  // State 3: Messages Displayed
  return (
    <div ref={containerRef} className="h-full overflow-y-auto">
      <div className="space-y-6 p-6">
        {messages.map((message, index) => (
          <Message
            key={index}
            message={message}
            isLast={index === messages.length - 1 && message.role === 'assistant'}
            onRegenerate={handleRegenerate}
          />
        ))}
        
        {/* State 4: AI is Typing */}
        {loading && (
          <div className="flex gap-4 justify-start mb-6">
            <div className="flex-shrink-0 w-9 h-9 rounded-full bg-gradient-to-br from-purple-500 to-purple-600 flex items-center justify-center shadow-md">
              <Bot className="text-white" size={18} />
            </div>
            <div className="bg-gray-100 border border-gray-200 rounded-2xl rounded-tl-sm px-5 py-3">
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                </div>
                <span className="text-sm text-gray-600 ml-1">AI is thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Scroll to Bottom Button */}
      {showScrollButton && (
        <button
          onClick={scrollToBottom}
          className="fixed bottom-28 right-8 w-12 h-12 bg-purple-600 text-white rounded-full shadow-lg hover:bg-purple-700 hover:shadow-xl transition-all duration-200 flex items-center justify-center z-10"
          aria-label="Scroll to bottom"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </button>
      )}
    </div>
  );
};

export default MessageList;
