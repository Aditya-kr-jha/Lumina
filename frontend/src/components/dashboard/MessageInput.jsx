import { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import { useChat } from '../../context/ChatContext';
import { useDocuments } from '../../context/DocumentContext';
import { validateQuestion } from '../../utils/validators';
import { showToast } from '../common/Toast';
import { VALIDATION_RULES } from '../../utils/constants';

const MessageInput = () => {
  const [question, setQuestion] = useState('');
  const textareaRef = useRef(null);
  
  const { sendMessage, loading } = useChat();
  const { currentDocument } = useDocuments();
  
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [question]);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!currentDocument) {
      showToast('Please select a document first', 'warning');
      return;
    }
    
    const error = validateQuestion(question);
    if (error) {
      showToast(error, 'error');
      return;
    }
    
    const result = await sendMessage(question, currentDocument.document_id);
    
    if (result.success) {
      setQuestion('');
    } else {
      showToast(result.error || 'Failed to send message', 'error');
    }
  };
  
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };
  
  const characterCount = question.length;
  const maxLength = VALIDATION_RULES.QUESTION.MAX_LENGTH;
  const isOverLimit = characterCount > maxLength;
  
  return (
    <form onSubmit={handleSubmit} className="px-4 sm:px-6 pb-6">
      {/* Container Wrapper with Pill Shape */}
      <div className="relative bg-white border-2 border-gray-300 rounded-full shadow-lg focus-within:border-purple-500 focus-within:ring-4 focus-within:ring-purple-100 transition-all duration-200">
        <textarea
          ref={textareaRef}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            currentDocument
              ? 'Ask a question about the document...'
              : 'Select a document to start chatting...'
          }
          disabled={!currentDocument || loading}
          rows={1}
          className="w-full pl-6 pr-16 py-4 bg-transparent border-0 rounded-full focus:outline-none resize-none max-h-32 disabled:bg-gray-100 disabled:cursor-not-allowed text-gray-900 placeholder-gray-500"
          style={{ minHeight: '48px' }}
        />
        
        {/* Character Count */}
        <div className="absolute right-14 bottom-2">
          <span
            className={`text-xs ${
              isOverLimit ? 'text-red-500' : 'text-gray-400'
            }`}
          >
            {characterCount}/{maxLength}
          </span>
        </div>
        
        {/* Send Button - Embedded on Right */}
        <button
          type="submit"
          disabled={!currentDocument || loading || !question.trim() || isOverLimit}
          className="absolute right-2 top-1/2 transform -translate-y-1/2 w-11 h-11 bg-purple-600 text-white rounded-full hover:bg-purple-700 active:bg-purple-800 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center shadow-md hover:shadow-lg disabled:shadow-none"
          aria-label="Send message"
        >
          <Send size={18} />
        </button>
      </div>
    </form>
  );
};

export default MessageInput;
